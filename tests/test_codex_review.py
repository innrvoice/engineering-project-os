"""Exercise final-head review readiness independently of CI and network timing."""

import copy
import importlib.util
import io
import json
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("check_codex_review", ROOT / "scripts/check_codex_review.py")
GUARD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GUARD)
REPOSITORY = "owner/project"
HEAD = "a" * 40
URL = "https://github.com/owner/project/pull/10"
FINDING_URL = URL + "#discussion_r123"
COMMENT_BODY = "P1: real defect\n<!-- codex-code-review-finding:v1 -->"


def connection(nodes):
    return {"nodes": nodes, "totalCount": len(nodes),
            "pageInfo": {"hasNextPage": False, "hasPreviousPage": False}}


def snapshot():
    states = {kind: {"commit_sha": HEAD, "status": "completed", "has_any_findings": False,
                     "has_unresolved_findings": False} for kind in ("code_review", "security_review")}
    return {"graphql": {"data": {"repository": {"nameWithOwner": REPOSITORY, "pullRequest": {
        "number": 10, "url": URL, "headRefOid": HEAD, "state": "OPEN", "isDraft": False,
        "updatedAt": "2026-10-16T10:00:00Z", "reviewDecision": None, "comments": {"totalCount": 1},
        "reviews": connection([]), "reviewThreads": connection([])}}}},
        "issue_comments": [{"id": 100, "updated_at": "2026-10-16T10:00:00Z", "html_url": URL + "#issuecomment-100",
            "user": {"login": GUARD.BOT, "type": "Bot"},
            "body": GUARD.SUMMARY_MARKER + "\n<!-- codex-review-state:v1 " + json.dumps(states) + " -->"}]}


def pr(value):
    return value["graphql"]["data"]["repository"]["pullRequest"]


def update_state(value, **changes):
    comment = value["issue_comments"][0]
    states = json.loads(GUARD.STATE_PATTERN.search(comment["body"]).group(1))
    kind = changes.pop("kind", "code_review")
    states[kind].update(changes)
    comment["body"] = GUARD.SUMMARY_MARKER + "\n<!-- codex-review-state:v1 " + json.dumps(states) + " -->"


def add_finding(value, head=HEAD, resolved=True):
    comment = {"id": "COMMENT", "url": FINDING_URL,
               "body": COMMENT_BODY,
               "author": {"__typename": "Bot", "login": GUARD.BOT_GRAPHQL}, "commit": {"oid": head},
               "updatedAt": "2026-10-16T10:00:00Z"}
    pr(value)["reviewThreads"] = connection([{"id": "THREAD", "isResolved": resolved,
                                              "comments": connection([comment])}])
    if head == HEAD:
        update_state(value, has_any_findings=True)
    return comment


class FakeLive:
    def __init__(self, value, on_refresh=None, source_after=None):
        self.value = value
        self.calls = 0
        self.source_calls = 0
        self.on_refresh = on_refresh
        self.source_after = source_after

    def source(self, target):
        self.source_calls += 1
        return self.source_after if self.source_after and self.source_calls > 1 else {"head": HEAD, "files": {"a": "b"}}

    def snapshot(self, repository, number):
        self.calls += 1
        if self.calls == 2 and self.on_refresh:
            self.on_refresh(self.value)
        return copy.deepcopy(self.value)


class CodexReviewTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.target = Path(self.temporary.name).resolve()
        self.proof = self.target / "proof.md"
        self.proof.write_text("Observed regression and verification.\n")
        self.dispositions = self.target / "private-dispositions.json"

    def dispositions_file(self, decision="fixed", **changes):
        row = {"comment_url": FINDING_URL, "decision": decision, "reason": "Verified the reported regression.",
               "comment_sha256": GUARD.digest(COMMENT_BODY.encode("utf-8")),
               "evidence": [{"path": "proof.md", "sha256": GUARD.digest(self.proof.read_bytes())}]}
        value = {"schema_version": 1, "repository": REPOSITORY, "pr": 10, "reviewed_head": HEAD, "findings": [row]}
        value.update(changes)
        self.dispositions.write_text(json.dumps(value))
        return value

    def inspect(self, value):
        return GUARD.inspect_review(value, REPOSITORY, 10, HEAD)

    def run_check(self, value, dispositions=None, **kwargs):
        return GUARD.check(REPOSITORY, 10, HEAD, self.target, dispositions, FakeLive(value, **kwargs))

    def test_completed_exact_head_without_findings_is_ready(self):
        self.assertEqual(self.run_check(snapshot())["readiness"], "READY")

    def test_green_ci_does_not_make_running_review_ready(self):
        value = snapshot()
        value["ci"] = {"conclusion": "success"}
        update_state(value, status="running", has_any_findings=None, has_unresolved_findings=None)
        with self.assertRaisesRegex(GUARD.NotReady, "not completed"):
            self.run_check(value)

    def test_both_reviews_must_be_completed_for_final_head(self):
        for kind in ("code_review", "security_review"):
            for change in [{"status": "running"}, {"status": "unknown"}, {"commit_sha": "b" * 40},
                           {"has_unresolved_findings": True}, {"has_unresolved_findings": None},
                           {"has_any_findings": None}]:
                with self.subTest(kind=kind, change=change):
                    value = snapshot()
                    update_state(value, kind=kind, **change)
                    with self.assertRaises(GUARD.NotReady):
                        self.inspect(value)

    def test_missing_untrusted_or_malformed_summary_is_not_ready(self):
        cases = []
        missing = snapshot(); missing["issue_comments"] = []; pr(missing)["comments"]["totalCount"] = 0
        cases.append(missing)
        for field, wrong in [("login", "lookalike-bot[bot]"), ("type", "User")]:
            value = snapshot(); value["issue_comments"][0]["user"][field] = wrong; cases.append(value)
        for body in [GUARD.SUMMARY_MARKER, GUARD.SUMMARY_MARKER + "\n<!-- codex-review-state:v2 {} -->"]:
            value = snapshot(); value["issue_comments"][0]["body"] = body; cases.append(value)
        duplicated = snapshot(); duplicated["issue_comments"][0]["body"] *= 2; cases.append(duplicated)
        for value in cases:
            with self.subTest(value=value):
                with self.assertRaises(GUARD.NotReady):
                    self.inspect(value)

    def test_newer_wrong_head_summary_cannot_be_hidden_by_old_completed_summary(self):
        value = snapshot()
        newer = copy.deepcopy(value["issue_comments"][0])
        newer.update(id=101, updated_at="2026-10-16T11:00:00Z", html_url=URL + "#issuecomment-101")
        newer["body"] = newer["body"].replace(HEAD, "b" * 40)
        value["issue_comments"].append(newer); pr(value)["comments"]["totalCount"] = 2
        with self.assertRaisesRegex(GUARD.NotReady, "wrong reviewed head"):
            self.inspect(value)

    def test_canonical_repository_pr_head_and_urls_are_checked(self):
        changes = [lambda v: v["graphql"]["data"]["repository"].update(nameWithOwner="other/project"),
                   lambda v: pr(v).update(number=11), lambda v: pr(v).update(url=URL.replace("/10", "/11")),
                   lambda v: pr(v).update(headRefOid="b" * 40), lambda v: pr(v).update(isDraft=True),
                   lambda v: pr(v).update(state="CLOSED"),
                   lambda v: v["issue_comments"][0].update(html_url=URL.replace("/10", "/11") + "#issuecomment-100")]
        for change in changes:
            value = snapshot(); change(value)
            with self.assertRaises(GUARD.NotReady):
                self.inspect(value)

    def test_unknown_or_incomplete_pagination_never_passes(self):
        for section in ("reviews", "reviewThreads"):
            for change in [{"totalCount": 1}, {"pageInfo": {"hasNextPage": True, "hasPreviousPage": False}},
                           {"pageInfo": {}}, {"nodes": [None]}]:
                value = snapshot(); pr(value)[section].update(change)
                with self.subTest(section=section, change=change):
                    with self.assertRaises(GUARD.NotReady):
                        self.inspect(value)
        value = snapshot(); pr(value)["comments"]["totalCount"] = 2
        with self.assertRaisesRegex(GUARD.NotReady, "incomplete pagination"):
            self.inspect(value)
        value = snapshot(); add_finding(value)
        pr(value)["reviewThreads"]["nodes"][0]["comments"]["pageInfo"]["hasNextPage"] = True
        with self.assertRaisesRegex(GUARD.NotReady, "incomplete pagination"):
            self.inspect(value)

    def test_unresolved_threads_block_even_without_bot_findings(self):
        value = snapshot(); comment = add_finding(value, resolved=False)
        comment["author"] = {"__typename": "User", "login": "reviewer"}
        comment["body"] = "Please address this."
        with self.assertRaisesRegex(GUARD.NotReady, "Unresolved"):
            self.inspect(value)

    def test_pending_or_changes_requested_bot_review_blocks(self):
        for state in ("PENDING", "CHANGES_REQUESTED", "UNKNOWN"):
            value = snapshot()
            pr(value)["reviews"] = connection([{"id": "REVIEW", "state": state,
                "submittedAt": "2026-10-16T10:00:00Z", "author": {"__typename": "Bot", "login": GUARD.BOT_GRAPHQL},
                "commit": {"oid": HEAD}}])
            with self.assertRaises(GUARD.NotReady):
                self.inspect(value)

    def test_findings_must_match_summary_and_trusted_bot(self):
        for change in ("missing", "untrusted", "unknown_marker", "noncanonical_url"):
            value = snapshot()
            comment = add_finding(value)
            if change == "missing": pr(value)["reviewThreads"] = connection([])
            elif change == "untrusted": comment["author"]["__typename"] = "User"
            elif change == "unknown_marker": comment["body"] = "<!-- codex-code-review-finding:v2 -->"
            else: comment["url"] = FINDING_URL.replace("/10", "/11")
            with self.subTest(change=change):
                with self.assertRaises(GUARD.NotReady):
                    self.inspect(value)

    def test_resolved_finding_requires_hash_bound_disposition(self):
        value = snapshot(); add_finding(value)
        with self.assertRaisesRegex(GUARD.NotReady, "Missing private"):
            self.run_check(value)
        self.dispositions_file()
        result = self.run_check(value, self.dispositions)
        self.assertEqual((result["readiness"], result["findings"]), ("READY", 1))

    def test_historical_findings_still_require_dispositions(self):
        value = snapshot(); add_finding(value, head="b" * 40)
        with self.assertRaisesRegex(GUARD.NotReady, "Missing private"):
            self.run_check(value)
        self.dispositions_file(decision="rejected")
        self.assertEqual(self.run_check(value, self.dispositions)["readiness"], "READY")

    def test_clean_rerun_on_same_head_keeps_historical_disposition_required(self):
        value = snapshot(); add_finding(value)
        update_state(value, has_any_findings=False)
        with self.assertRaisesRegex(GUARD.NotReady, "Missing private"):
            self.run_check(value)
        self.dispositions_file(decision="rejected")
        self.assertEqual(self.run_check(value, self.dispositions)["readiness"], "READY")
        pr(value)["reviewThreads"]["nodes"][0]["isResolved"] = False
        with self.assertRaisesRegex(GUARD.NotReady, "Unresolved"):
            self.run_check(value, self.dispositions)

    def test_plain_bot_followup_is_not_another_finding_but_unknown_findings_block(self):
        value = snapshot(); add_finding(value); self.dispositions_file()
        comments = pr(value)["reviewThreads"]["nodes"][0]["comments"]
        reply = {"id": "REPLY", "url": URL + "#discussion_r124", "body": "Verified the correction, thanks.",
                 "author": {"__typename": "Bot", "login": GUARD.BOT_GRAPHQL}, "replyTo": {"id": "COMMENT"}}
        comments["nodes"].append(reply); comments["totalCount"] = 2
        self.assertEqual(self.run_check(value, self.dispositions)["findings"], 1)
        for body in ("P1: another defect", "<!-- codex-code-review-finding:v2 -->"):
            reply["body"] = body
            with self.assertRaisesRegex(GUARD.NotReady, "Unclassified"):
                self.run_check(value, self.dispositions)

    def test_unknown_duplicate_or_unaccounted_disposition_urls_block(self):
        value = snapshot(); add_finding(value)
        for change in ("missing", "extra", "duplicate"):
            content = self.dispositions_file()
            if change == "missing": content["findings"] = []
            elif change == "extra": content["findings"][0]["comment_url"] = FINDING_URL + "9"
            else: content["findings"] *= 2
            self.dispositions.write_text(json.dumps(content))
            with self.assertRaisesRegex(GUARD.NotReady, "exactly one disposition"):
                self.run_check(value, self.dispositions)

    def test_self_declared_risk_empty_reason_or_missing_proof_is_rejected(self):
        value = snapshot(); add_finding(value)
        for field, wrong in [("decision", "owner_accepted_risk"), ("decision", "unknown"),
                             ("reason", " "), ("evidence", [])]:
            content = self.dispositions_file(); content["findings"][0][field] = wrong
            self.dispositions.write_text(json.dumps(content))
            with self.assertRaises(GUARD.NotReady):
                self.run_check(value, self.dispositions)

    def test_wrong_binding_and_changed_evidence_block(self):
        value = snapshot(); add_finding(value)
        for change in [{"reviewed_head": "b" * 40}, {"repository": "other/repo"}, {"pr": 11}, {"schema_version": True}]:
            self.dispositions_file(**change)
            with self.assertRaisesRegex(GUARD.NotReady, "do not bind"):
                self.run_check(value, self.dispositions)
        self.dispositions_file(); self.proof.write_text("Changed after disposition.\n")
        with self.assertRaisesRegex(GUARD.NotReady, "Changed or invalid"):
            self.run_check(value, self.dispositions)

    def test_edited_finding_body_cannot_reuse_old_disposition(self):
        value = snapshot(); comment = add_finding(value)
        self.dispositions_file()
        comment["body"] = comment["body"].replace("real defect", "different defect")
        with self.assertRaisesRegex(GUARD.NotReady, "Changed or unbound finding"):
            self.run_check(value, self.dispositions)

    def test_unsafe_or_symlink_evidence_paths_block(self):
        value = snapshot(); add_finding(value)
        link = self.target / "link"; link.symlink_to(self.proof)
        for relative in ("../proof.md", str(self.proof), "./proof.md", "link", "missing"):
            content = self.dispositions_file(); content["findings"][0]["evidence"][0]["path"] = relative
            self.dispositions.write_text(json.dumps(content))
            with self.assertRaises(GUARD.NotReady):
                self.run_check(value, self.dispositions)

    def test_concurrent_head_source_or_remote_change_blocks(self):
        for after in [{"head": "b" * 40, "files": {"a": "b"}}, {"head": HEAD, "files": {"a": "changed"}}]:
            with self.assertRaisesRegex(GUARD.NotReady, "Source HEAD or files changed"):
                self.run_check(snapshot(), source_after=after)
        with self.assertRaisesRegex(GUARD.NotReady, "GitHub review/head changed"):
            self.run_check(snapshot(), on_refresh=lambda value: pr(value).update(headRefOid="b" * 40))

    def test_concurrent_evidence_and_disposition_change_blocks(self):
        value = snapshot(); add_finding(value)
        for path in (self.proof, self.dispositions):
            self.dispositions_file()
            def mutate(unused):
                path.write_bytes(path.read_bytes() + b"\n")
            with self.assertRaisesRegex(GUARD.NotReady, "changed during validation"):
                self.run_check(value, self.dispositions, on_refresh=mutate)

    def test_duplicate_json_keys_fail_closed(self):
        with self.assertRaisesRegex(GUARD.NotReady, "Duplicate JSON key"):
            GUARD.strict_json('{"reviewed_head":"old","reviewed_head":"new"}')

    def test_live_wrapper_uses_canonical_host_and_actual_pagination(self):
        live = GUARD.Live(30)
        with mock.patch.object(live, "command", side_effect=["{}", "[[{\"id\":1}],[{\"id\":2}]]"]) as command:
            self.assertEqual([x["id"] for x in live.snapshot(REPOSITORY, 10)["issue_comments"]], [1, 2])
        for call in command.call_args_list:
            self.assertEqual(call.args[0][:4], ["gh", "api", "--hostname", "github.com"])
        self.assertIn("--paginate", command.call_args_list[1].args[0])
        self.assertIn("--slurp", command.call_args_list[1].args[0])

    def test_live_timeout_and_api_failure_return_nonzero_json(self):
        for failure in [subprocess.TimeoutExpired(["gh"], 1), OSError("gh missing")]:
            output = io.StringIO()
            with mock.patch.object(GUARD.subprocess, "run", side_effect=failure), redirect_stdout(output):
                code = GUARD.main(["--repo", REPOSITORY, "--pr", "10", "--head", HEAD, "--json"])
            self.assertEqual(code, 1)
            self.assertEqual(json.loads(output.getvalue())["readiness"], "NOT_READY")
        live = GUARD.Live(30)
        with mock.patch.object(GUARD.subprocess, "run", return_value=subprocess.CompletedProcess(["gh"], 1, "", "API denied")):
            with self.assertRaisesRegex(GUARD.NotReady, "Read-only command failed"):
                live.snapshot(REPOSITORY, 10)

    def test_plain_cli_error_is_actionable_and_never_ready(self):
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(GUARD.main(["--repo", REPOSITORY, "--pr", "10", "--head", "wrong"]), 1)
        self.assertTrue(output.getvalue().startswith("NOT_READY:"))

    def test_expired_deadline_never_starts_a_subprocess(self):
        live = GUARD.Live(30)
        live.deadline = 0
        with mock.patch.object(GUARD.subprocess, "run") as command:
            with self.assertRaisesRegex(GUARD.NotReady, "timed out"):
                live.snapshot(REPOSITORY, 10)
        command.assert_not_called()

    def test_local_checkout_must_match_reviewed_commit(self):
        live = FakeLive(snapshot())
        live.source = lambda target: {"head": "b" * 40, "files": {}}
        with self.assertRaisesRegex(GUARD.NotReady, "Local HEAD differs"):
            GUARD.check(REPOSITORY, 10, HEAD, self.target, None, live)
        self.assertEqual(live.calls, 0)

    def test_real_source_capture_rejects_dirty_and_untracked_changes(self):
        target = self.target / "git"
        target.mkdir()
        def git(*args):
            return subprocess.run(["git", "-C", str(target), *args], check=True, capture_output=True, text=True).stdout
        git("init", "-q")
        source = target / "source.py"; source.write_text("x = 1\n")
        ignore = target / ".gitignore"; ignore.write_text(".agents/\n")
        git("add", "source.py", ".gitignore")
        git("-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "Synthetic baseline")
        recorded = GUARD.Live(30).source(target)
        self.assertEqual(recorded["files"], {"source.py": {"sha256": GUARD.digest(source.read_bytes()), "mode": "100644"},
                                             ".gitignore": {"sha256": GUARD.digest(ignore.read_bytes()), "mode": "100644"}})
        private = target / ".agents"; private.mkdir(); (private / "dispositions.json").write_text("{}\n")
        self.assertEqual(GUARD.Live(30).source(target), recorded)
        source.write_text("x = 2\n")
        with self.assertRaisesRegex(GUARD.NotReady, "dirty"):
            GUARD.Live(30).source(target)
        source.write_text("x = 1\n"); (target / "untracked.py").write_text("x = 3\n")
        with self.assertRaisesRegex(GUARD.NotReady, "dirty"):
            GUARD.Live(30).source(target)

    def test_hidden_worktree_bytes_and_modes_must_equal_reviewed_git_blobs(self):
        for flag in ("--assume-unchanged", "--skip-worktree"):
            with self.subTest(flag=flag):
                target = self.target / flag.removeprefix("--")
                target.mkdir()
                def git(*args):
                    return subprocess.run(["git", "-C", str(target), *args], check=True, capture_output=True, text=True).stdout
                git("init", "-q")
                source = target / "source.py"; source.write_text("x = 1\n")
                git("add", "source.py")
                git("-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "Synthetic baseline")
                git("update-index", flag, "source.py"); source.write_text("x = 2\n")
                self.assertEqual(git("status", "--porcelain=v1"), "")
                with self.assertRaisesRegex(GUARD.NotReady, "bytes differ from reviewed HEAD"):
                    GUARD.Live(30).source(target)
                source.write_text("x = 1\n"); source.chmod(source.stat().st_mode | 0o100)
                self.assertEqual(git("status", "--porcelain=v1"), "")
                with self.assertRaisesRegex(GUARD.NotReady, "executable mode differs"):
                    GUARD.Live(30).source(target)

    def test_git_replacement_objects_cannot_substitute_unreviewed_source(self):
        target = self.target / "replaced"; target.mkdir()
        def git(*args, data=None):
            return subprocess.run(["git", "-C", str(target), *args], input=data,
                                  check=True, capture_output=True, text=True).stdout.strip()
        git("init", "-q")
        source = target / "source.py"; source.write_text("x = 1\n")
        git("add", "source.py")
        git("-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "Synthetic baseline")
        original = git("rev-parse", "HEAD:source.py")
        replacement = git("hash-object", "-w", "--stdin", data="x = 2\n")
        git("replace", original, replacement)
        git("update-index", "--assume-unchanged", "source.py"); source.write_text("x = 2\n")
        self.assertEqual(git("status", "--porcelain=v1"), "")
        with self.assertRaisesRegex(GUARD.NotReady, "bytes differ from reviewed HEAD"):
            GUARD.Live(30).source(target)


if __name__ == "__main__":
    unittest.main()
