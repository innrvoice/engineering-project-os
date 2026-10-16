"""Exercise final-head review readiness independently of CI and network timing."""

import copy
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("check_codex_review", ROOT / "scripts/check_codex_review.py")
GUARD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GUARD)
PACKAGE_SPEC = importlib.util.spec_from_file_location("trusted_test_packager", ROOT / "scripts/package_plugin.py")
PACKAGER = importlib.util.module_from_spec(PACKAGE_SPEC)
PACKAGE_SPEC.loader.exec_module(PACKAGER)
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

    def verify_tools(self, full=True):
        return {}

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
        self.external = tempfile.TemporaryDirectory()
        self.addCleanup(self.external.cleanup)
        self.gh = Path(self.external.name).resolve() / "gh"
        self.gh.write_text("#!/bin/sh\nexit 0\n")
        self.gh.chmod(0o700)
        self.git = Path(shutil.which("git")).resolve()

    def live(self, target=None):
        return GUARD.Live(30, target or self.target, git=self.git, gh=self.gh)

    def package_layout(self, target):
        for relative in PACKAGER.FILES:
            path = target / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("raise AssertionError('target code must not execute')\n")
        for relative in PACKAGER.TREES:
            directory = target / relative
            directory.mkdir(exist_ok=True)
            (directory / "tracked.txt").write_text("Reviewed package bytes.\n")

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
        live = self.live()
        with mock.patch.object(live, "command", side_effect=["{}", "[[{\"id\":1}],[{\"id\":2}]]"]) as command:
            self.assertEqual([x["id"] for x in live.snapshot(REPOSITORY, 10)["issue_comments"]], [1, 2])
        for call in command.call_args_list:
            self.assertEqual(call.args[0][:4], [str(self.gh), "api", "--hostname", "github.com"])
        self.assertIn("--paginate", command.call_args_list[1].args[0])
        self.assertIn("--slurp", command.call_args_list[1].args[0])

    def test_live_timeout_and_api_failure_return_nonzero_json(self):
        for failure in [subprocess.TimeoutExpired(["gh"], 1), OSError("gh missing")]:
            output = io.StringIO()
            with mock.patch.object(GUARD.subprocess, "run", side_effect=failure), redirect_stdout(output):
                code = GUARD.main(["--repo", REPOSITORY, "--pr", "10", "--head", HEAD,
                                   "--target", str(self.target), "--git", str(self.git), "--gh", str(self.gh), "--json"])
            self.assertEqual(code, 1)
            self.assertEqual(json.loads(output.getvalue())["readiness"], "NOT_READY")
        live = self.live()
        with mock.patch.object(GUARD.subprocess, "run", return_value=subprocess.CompletedProcess(["gh"], 1, "", "API denied")):
            with self.assertRaisesRegex(GUARD.NotReady, "Read-only command failed"):
                live.snapshot(REPOSITORY, 10)

    def test_plain_cli_error_is_actionable_and_never_ready(self):
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(GUARD.main(["--repo", REPOSITORY, "--pr", "10", "--head", "wrong",
                                        "--git", str(self.git), "--gh", str(self.gh)]), 1)
        self.assertTrue(output.getvalue().startswith("NOT_READY:"))

    def test_expired_deadline_never_starts_a_subprocess(self):
        live = self.live()
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
        self.package_layout(target)
        git("add", ".")
        git("-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "Complete package baseline")
        recorded = self.live(target).source(target)
        self.assertEqual(recorded["files"], {relative: {"sha256": GUARD.digest((target / relative).read_bytes()), "mode": "100644"}
                                           for relative in git("ls-files").splitlines()})
        private = target / ".agents"; private.mkdir(); (private / "dispositions.json").write_text("{}\n")
        self.assertEqual(self.live(target).source(target), recorded)
        source.write_text("x = 2\n")
        with self.assertRaisesRegex(GUARD.NotReady, "dirty"):
            self.live(target).source(target)
        source.write_text("x = 1\n"); (target / "untracked.py").write_text("x = 3\n")
        with self.assertRaisesRegex(GUARD.NotReady, "dirty"):
            self.live(target).source(target)

    def packaged_checkout(self, name):
        target = self.target / name
        target.mkdir()
        self.package_layout(target)
        (target / ".gitignore").write_text(".DS_Store\n__pycache__/\n*.pyc\n.agents/\n")
        def git(*args):
            return subprocess.run(["git", "-C", str(target), *args], check=True,
                                  capture_output=True, text=True).stdout.strip()
        git("init", "-q")
        git("add", ".")
        git("-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "Reviewed package baseline")
        return target, git

    def completed_live(self, head, on_refresh=None, target=None):
        value = snapshot()
        pr(value)["headRefOid"] = head
        for kind in ("code_review", "security_review"):
            update_state(value, kind=kind, commit_sha=head)
        bound_target = target or self.target
        bound_git, bound_gh = self.git, self.gh
        class ReviewedLive(GUARD.Live):
            def __init__(self):
                super().__init__(30, bound_target, git=bound_git, gh=bound_gh)
                self.snapshots = 0
            def snapshot(self, repository, number):
                self.snapshots += 1
                if self.snapshots == 2 and on_refresh:
                    on_refresh()
                return copy.deepcopy(value)
        return ReviewedLive()

    def test_package_input_policy_matches_actual_packager_and_keeps_exclusions(self):
        self.assertEqual(GUARD.PACKAGE_FILES, PACKAGER.FILES)
        self.assertEqual(GUARD.PACKAGE_TREES, PACKAGER.TREES)
        target, git = self.packaged_checkout("package-policy")
        before = self.live(target).source(target)
        (target / ".agents").mkdir()
        (target / ".agents/private.json").write_text("Private working records.\n")
        (target / "skills/__pycache__").mkdir()
        (target / "skills/__pycache__/module.pyc").write_bytes(b"Ignored cache")
        (target / "docs/cache.pyc").write_bytes(b"Ignored bytecode")
        expected = {path.relative_to(target).as_posix() for path in PACKAGER.source_files(target)}
        self.assertEqual(GUARD.package_inputs(target), expected)
        self.assertEqual(git("status", "--porcelain=v1"), "")
        self.assertEqual(self.live(target).source(target), before)
        result = GUARD.check(REPOSITORY, 10, before["head"], target, None, self.completed_live(before["head"], target=target))
        self.assertEqual(result["readiness"], "READY")

    def test_ignored_regular_inputs_in_each_packaged_tree_block_ready(self):
        for tree in PACKAGER.TREES:
            with self.subTest(tree=tree):
                target, git = self.packaged_checkout("ignored-" + tree)
                head = git("rev-parse", "HEAD")
                hidden = target / tree / ".DS_Store"
                hidden.write_bytes(b"Unreviewed package bytes")
                self.assertEqual(git("status", "--porcelain=v1"), "")
                self.assertIn(hidden, PACKAGER.source_files(target))
                self.assertIn(hidden.relative_to(target).as_posix(), GUARD.package_inputs(target))
                with self.assertRaisesRegex(GUARD.NotReady, "Unreviewed package input.*" + tree):
                    GUARD.check(REPOSITORY, 10, head, target, None, self.completed_live(head, target=target))

    def test_ignored_fixed_package_input_must_also_exist_in_reviewed_head(self):
        target, git = self.packaged_checkout("ignored-fixed")
        (target / ".git/info/exclude").write_text("/README.md\n")
        git("rm", "--cached", "README.md")
        git("-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "No reviewed README")
        self.assertEqual(git("status", "--porcelain=v1"), "")
        self.assertIn(target / "README.md", PACKAGER.source_files(target))
        with self.assertRaisesRegex(GUARD.NotReady, "Unreviewed package input.*README.md"):
            self.live(target).source(target)

    def test_ignored_package_symlinks_and_nonregular_entries_are_rejected(self):
        for kind in ("symlink", "fifo", "cache-symlink"):
            with self.subTest(kind=kind):
                target, git = self.packaged_checkout("unsafe-" + kind)
                hidden = target / "assets/.DS_Store"
                if kind == "fifo":
                    os.mkfifo(hidden)
                else:
                    if kind == "cache-symlink":
                        hidden = target / "skills/__pycache__/module.pyc"
                        hidden.parent.mkdir()
                    hidden.symlink_to(target / "README.md")
                self.assertEqual(git("status", "--porcelain=v1"), "")
                with self.assertRaises(ValueError):
                    PACKAGER.source_files(target)
                with self.assertRaisesRegex(GUARD.NotReady, "package input"):
                    self.live(target).source(target)

    def test_concurrent_ignored_package_input_addition_blocks_final_check(self):
        target, git = self.packaged_checkout("concurrent-ignored")
        head = git("rev-parse", "HEAD")
        def add_ignored():
            (target / "assets/.DS_Store").write_bytes(b"Appeared during remote review collection")
        live = self.completed_live(head, on_refresh=add_ignored, target=target)
        with self.assertRaisesRegex(GUARD.NotReady, "Unreviewed package input.*assets/.DS_Store"):
            GUARD.check(REPOSITORY, 10, head, target, None, live)
        self.assertEqual(live.snapshots, 2)
        self.assertEqual(git("status", "--porcelain=v1"), "")

    def test_hidden_worktree_bytes_and_modes_must_equal_reviewed_git_blobs(self):
        for flag in ("--assume-unchanged", "--skip-worktree"):
            with self.subTest(flag=flag):
                target = self.target / flag.removeprefix("--")
                target.mkdir()
                def git(*args):
                    return subprocess.run(["git", "-C", str(target), *args], check=True, capture_output=True, text=True).stdout
                self.package_layout(target)
                git("init", "-q")
                source = target / "source.py"; source.write_text("x = 1\n")
                git("add", ".")
                git("-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "Synthetic baseline")
                git("update-index", flag, "source.py"); source.write_text("x = 2\n")
                self.assertEqual(git("status", "--porcelain=v1"), "")
                with self.assertRaisesRegex(GUARD.NotReady, "bytes differ from reviewed HEAD"):
                    self.live(target).source(target)
                source.write_text("x = 1\n"); source.chmod(source.stat().st_mode | 0o100)
                self.assertEqual(git("status", "--porcelain=v1"), "")
                with self.assertRaisesRegex(GUARD.NotReady, "executable mode differs"):
                    self.live(target).source(target)

    def test_git_replacement_objects_cannot_substitute_unreviewed_source(self):
        target = self.target / "replaced"; target.mkdir()
        def git(*args, data=None):
            return subprocess.run(["git", "-C", str(target), *args], input=data,
                                  check=True, capture_output=True, text=True).stdout.strip()
        self.package_layout(target)
        git("init", "-q")
        source = target / "source.py"; source.write_text("x = 1\n")
        git("add", ".")
        git("-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "Synthetic baseline")
        original = git("rev-parse", "HEAD:source.py")
        replacement = git("hash-object", "-w", "--stdin", data="x = 2\n")
        git("replace", original, replacement)
        git("update-index", "--assume-unchanged", "source.py"); source.write_text("x = 2\n")
        self.assertEqual(git("status", "--porcelain=v1"), "")
        with self.assertRaisesRegex(GUARD.NotReady, "bytes differ from reviewed HEAD"):
            self.live(target).source(target)

    def test_cli_refuses_nonisolated_launch_before_shadowable_imports(self):
        for module in ("hashlib", "json"):
            with self.subTest(module=module):
                target = self.target / ("nonisolated-" + module)
                directory = target / "scripts"
                directory.mkdir(parents=True)
                runner = directory / "check_codex_review.py"
                runner.write_bytes((ROOT / "scripts/check_codex_review.py").read_bytes())
                marker = self.target / (module + "-unsafe-import.txt")
                (directory / (module + ".py")).write_text(
                    "with open(" + repr(str(marker)) + ", 'w') as stream:\n"
                    "    stream.write('PR-controlled module executed')\n"
                    "raise RuntimeError('harmless import canary')\n")
                environment = {key: value for key, value in os.environ.items()
                               if key not in ("PYTHONPATH", "PYTHONHOME", "PYTHONUSERBASE")}
                result = subprocess.run([sys.executable, "-B", str(runner), "--repo", REPOSITORY,
                                         "--pr", "10", "--head", HEAD, "--target", str(target), "--git", str(self.git), "--gh", str(self.gh), "--json"],
                                        cwd=target, env=environment, capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(marker.exists(), result.stderr)
                self.assertIn("NOT_READY", result.stdout + result.stderr)
                self.assertIn("-I", result.stdout + result.stderr)

    def test_isolated_external_cli_ignores_pr_modules_cwd_and_pythonpath(self):
        target, git = self.packaged_checkout("shadowed-pr")
        marker = self.target / "isolated-import-canary.txt"
        canary = ("with open(" + repr(str(marker)) + ", 'w') as stream:\n"
                  "    stream.write('PR-controlled code executed')\n"
                  "raise RuntimeError('harmless import canary')\n")
        # Even the PR's guard itself is data, never the runner being executed.
        (target / "scripts/check_codex_review.py").write_text(canary)
        for directory in (target, target / "scripts"):
            for module in ("hashlib", "json", "re", "pathlib", "sitecustomize", "usercustomize"):
                (directory / (module + ".py")).write_text(canary)
        git("add", ".")
        git("-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "Untrusted PR canaries")
        trusted = self.target / "trusted-runner"
        trusted.mkdir()
        runner = trusted / "check_codex_review.py"
        runner.write_bytes((ROOT / "scripts/check_codex_review.py").read_bytes())
        runner.chmod(0o444)
        environment = dict(os.environ)
        environment["PYTHONPATH"] = os.pathsep.join((str(target / "scripts"), str(target)))
        environment["PYTHONUSERBASE"] = str(target)
        before = {path.relative_to(target).as_posix(): path.read_bytes()
                  for path in target.rglob("*") if path.is_file() and ".git" not in path.parts}
        # A canonical, mismatched head reaches real source validation but no network.
        result = subprocess.run([sys.executable, "-I", "-B", str(runner), "--repo", REPOSITORY,
                                 "--pr", "10", "--head", HEAD, "--target", str(target), "--git", str(self.git), "--gh", str(self.gh), "--json"],
                                cwd=target / "scripts", env=environment, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1, result.stderr)
        value = json.loads(result.stdout)
        self.assertEqual(value["readiness"], "NOT_READY")
        self.assertIn("Local HEAD differs", value["blocker"])
        self.assertFalse(marker.exists(), result.stderr)
        self.assertEqual(before, {path.relative_to(target).as_posix(): path.read_bytes()
                                 for path in target.rglob("*") if path.is_file() and ".git" not in path.parts})

    def test_isolated_cli_rejects_a_runner_inside_the_target_checkout(self):
        target = self.target / "in-checkout-runner"
        directory = target / "scripts"
        directory.mkdir(parents=True)
        runner = directory / "check_codex_review.py"
        runner.write_bytes((ROOT / "scripts/check_codex_review.py").read_bytes())
        alias = self.target / "apparently-external-guard.py"
        alias.symlink_to(runner)
        for path in (runner, alias):
            with self.subTest(runner=path):
                result = subprocess.run([sys.executable, "-I", "-B", str(path), "--repo", REPOSITORY,
                                         "--pr", "10", "--head", HEAD, "--target", str(target), "--git", str(self.git), "--gh", str(self.gh), "--json"],
                                        cwd=target, capture_output=True, text=True)
                self.assertEqual(result.returncode, 1, result.stderr)
                value = json.loads(result.stdout)
                self.assertEqual(value["readiness"], "NOT_READY")
                self.assertRegex(value["blocker"], "outside|trusted external")

    def test_direct_source_capture_refuses_an_in_target_runner_before_commands(self):
        target = self.target / "direct-target"
        target.mkdir()
        live = self.live(target)
        with mock.patch.object(GUARD, "__file__", str(target / "scripts/check_codex_review.py")), \
                mock.patch.object(live, "command") as command:
            with self.assertRaisesRegex(GUARD.NotReady, "outside|trusted external"):
                live.source(target)
        command.assert_not_called()


    def test_every_required_package_file_and_tree_must_survive_committed_deletion(self):
        for index, relative in enumerate(PACKAGER.FILES + PACKAGER.TREES):
            with self.subTest(required=relative):
                target, git = self.packaged_checkout("missing-" + str(index))
                path = target / relative
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
                git("add", "-A")
                git("-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "Committed required input deletion")
                self.assertEqual(git("status", "--porcelain=v1"), "")
                with self.assertRaises((ValueError, FileNotFoundError)):
                    PACKAGER.source_files(target)
                live = self.completed_live(git("rev-parse", "HEAD"), target=target)
                with self.assertRaisesRegex(GUARD.NotReady, "Missing required package"):
                    GUARD.check(REPOSITORY, 10, git("rev-parse", "HEAD"), target, None, live)
                self.assertEqual(live.snapshots, 0)

    def test_candidate_tool_paths_and_aliases_reject_before_either_command(self):
        target = self.target / "tool-candidate"
        (target / "bin").mkdir(parents=True)
        marker = self.target / "tool-executed.txt"
        for name in ("git", "gh"):
            canary = target / "bin" / name
            canary.write_text("#!/bin/sh\nprintf touched > '" + str(marker) + "'\nexit 17\n")
            canary.chmod(0o700)
        for name in ("git", "gh"):
            for route in ("direct", "file-alias", "parent-alias", "path", "dot-path"):
                with self.subTest(tool=name, route=route):
                    selected = target / "bin" / name
                    explicit = {"git": self.git, "gh": self.gh}
                    environment = {}
                    if route == "file-alias":
                        selected = Path(self.external.name) / (name + "-alias")
                        selected.symlink_to(target / "bin" / name)
                    elif route == "parent-alias":
                        alias = Path(self.external.name) / (name + "-directory")
                        alias.symlink_to(target / "bin", target_is_directory=True)
                        selected = alias / name
                    elif route in ("path", "dot-path"):
                        explicit[name] = None
                        environment["PATH"] = ("." if route == "dot-path" else str(target / "bin"))
                    if route not in ("path", "dot-path"):
                        explicit[name] = selected
                    previous = Path.cwd()
                    try:
                        os.chdir(target / "bin")
                        with mock.patch.dict(os.environ, environment), mock.patch.object(GUARD.subprocess, "run") as command:
                            message = "Explicit --" + name if route in ("path", "dot-path") else "outside --target"
                            with self.assertRaisesRegex(GUARD.NotReady, message):
                                GUARD.Live(30, target, **explicit)
                            command.assert_not_called()
                    finally:
                        os.chdir(previous)
                    self.assertFalse(marker.exists())

    def test_tool_preflight_rejects_missing_relative_nonexecutable_and_directory(self):
        target = self.target / "tool-validation"; target.mkdir()
        nonexecutable = Path(self.external.name) / "nonexecutable"
        nonexecutable.write_text("plain data")
        for invalid in (Path("relative-git"), Path(self.external.name) / "missing", nonexecutable, Path(self.external.name)):
            with self.subTest(path=invalid), mock.patch.object(GUARD.subprocess, "run") as command:
                with self.assertRaises((GUARD.NotReady, OSError)):
                    GUARD.Live(30, target, git=invalid, gh=self.gh)
                command.assert_not_called()

    def test_cli_requires_both_explicit_tools_even_with_external_path_canaries(self):
        target = self.target / "omitted-tool-target"; target.mkdir()
        external = Path(self.external.name)
        marker = self.target / "external-path-canary.txt"
        for name in ("git", "gh"):
            path = external / ("poison-" + name)
            path.write_text("#!/bin/sh\nprintf touched > '" + str(marker) + "'\nexit 17\n")
            path.chmod(0o700)
        poison = external / "poison-tools"; poison.mkdir()
        for name in ("git", "gh"):
            (poison / name).symlink_to(external / ("poison-" + name))
        runner = external / "trusted-guard.py"
        runner.write_bytes((ROOT / "scripts/check_codex_review.py").read_bytes())
        for flags, missing in (([], ("--git", "--gh")), (["--git", str(self.git)], ("--gh",)),
                               (["--gh", str(self.gh)], ("--git",))):
            with self.subTest(missing=missing):
                result = subprocess.run([sys.executable, "-I", "-B", str(runner), "--repo", REPOSITORY,
                                         "--pr", "10", "--head", HEAD, "--target", str(target), *flags],
                                        cwd=target, env={**os.environ, "PATH": str(poison)},
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn("required", result.stderr)
                for argument in missing:
                    self.assertIn(argument, result.stderr)
                self.assertFalse(marker.exists())

    def test_live_api_requires_explicit_tools_before_any_subprocess(self):
        for configured in ({"git": None, "gh": self.gh}, {"git": self.git, "gh": None}):
            with self.subTest(configured=configured), mock.patch.object(GUARD.subprocess, "run") as command:
                with self.assertRaisesRegex(GUARD.NotReady, "Explicit --"):
                    GUARD.Live(30, self.target, **configured)
                command.assert_not_called()
        with mock.patch.object(GUARD.subprocess, "run") as command:
            with self.assertRaises(TypeError):
                GUARD.Live(30, self.target)
            command.assert_not_called()

    def test_bound_absolute_tools_ignore_later_path_poisoning_and_record_proof(self):
        target, git = self.packaged_checkout("bound-tools")
        live = self.live(target)
        canary = target / "git"
        marker = self.target / "late-path-executed.txt"
        canary.write_text("#!/bin/sh\nprintf touched > '" + str(marker) + "'\nexit 17\n")
        canary.chmod(0o700)
        git("add", "git")
        git("-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "Candidate tool remains data")
        with mock.patch.dict(os.environ, {"PATH": str(target)}):
            captured = live.source(target)
        self.assertEqual(captured["head"], git("rev-parse", "HEAD"))
        self.assertFalse(marker.exists())
        proofs = live.verify_tools()
        self.assertEqual(proofs["git"]["path"], str(self.git))
        self.assertEqual(proofs["gh"]["sha256"], GUARD.digest(self.gh.read_bytes()))
        self.assertNotIn(str(target), live.environment["PATH"].split(os.pathsep))
        self.assertNotIn(".", live.environment["PATH"].split(os.pathsep))
        with mock.patch.object(GUARD.subprocess, "run") as command:
            with self.assertRaisesRegex(GUARD.NotReady, "Only bound absolute"):
                live.command(["git", "status"])
            command.assert_not_called()

    def test_tool_changes_after_last_source_command_block_ready(self):
        for mutation in ("bytes", "mode", "replacement", "candidate-alias"):
            with self.subTest(mutation=mutation):
                target, git = self.packaged_checkout("late-tool-" + mutation)
                live = self.completed_live(git("rev-parse", "HEAD"), target=target)
                original_source = live.source
                calls = []
                def change_after_final_source(path):
                    result = original_source(path)
                    calls.append(path)
                    if len(calls) == 2:
                        if mutation == "bytes":
                            previous = self.gh.stat()
                            self.gh.write_text("#!/bin/sh\nexit 1\n")
                            os.utime(self.gh, ns=(previous.st_atime_ns, previous.st_mtime_ns))
                        elif mutation == "mode":
                            self.gh.chmod(0o500)
                        elif mutation == "replacement":
                            old = self.gh.read_bytes()
                            self.gh.unlink()
                            self.gh.write_bytes(old)
                            self.gh.chmod(0o700)
                        else:
                            moved = target / "moved-gh"
                            self.gh.rename(moved)
                            self.gh.symlink_to(moved)
                    return result
                with mock.patch.object(live, "source", side_effect=change_after_final_source):
                    with self.assertRaisesRegex(GUARD.NotReady, "Executable.*changed"):
                        GUARD.check(REPOSITORY, 10, git("rev-parse", "HEAD"), target, None, live)
                self.assertEqual(len(calls), 2)
                if self.gh.is_symlink():
                    self.gh.unlink()
                    self.gh.write_text("#!/bin/sh\nexit 0\n")
                self.gh.chmod(0o700)
                self.gh.write_text("#!/bin/sh\nexit 0\n")


if __name__ == "__main__":
    unittest.main()
