#!/usr/bin/env python3
"""Read-only, fail-closed Codex Review readiness for one exact PR head.

This repository guard never merges, resolves threads or publishes. A green CI
check is not a completed Codex review. Dispositions remain private local files.
Execute an independently trusted copy outside the candidate checkout with -I.
"""

import sys

# sys is built in. Refuse before this script imports any shadowable module.
# Python startup itself is safe only when the caller supplied -I already.
if __name__ == "__main__" and not sys.flags.isolated:
    print("NOT_READY: Run a trusted external guard with python3 -I -B; non-isolated execution is unsupported.",
          file=sys.stderr)
    raise SystemExit(1)

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import time
from pathlib import Path


BOT = "chatgpt-codex-connector[bot]"
BOT_GRAPHQL = "chatgpt-codex-connector"
SUMMARY_MARKER = "<!-- codex-pull-request-review-summary -->"
STATE_PATTERN = re.compile(r"<!-- codex-review-state:v1 (.*?) -->", re.DOTALL)
FINDING_MARKERS = {
    "<!-- codex-code-review-finding:v1 -->": "code_review",
    "<!-- codex-security-review-finding:v1 -->": "security_review",
}
# Keep this read-only input policy in sync with package_plugin.source_files.
# Never import or execute the target checkout's packaging code to inspect it.
PACKAGE_FILES = ("plugin.json", ".codex-plugin/plugin.json", "README.md", "LICENSE",
                 "SECURITY.md", "CHANGELOG.md", "CONTRIBUTING.md", "scripts/package_plugin.py",
                 "scripts/check_codex_review.py")
PACKAGE_TREES = ("skills", "assets", "docs")
QUERY = """query($owner:String!,$name:String!,$number:Int!) {
  repository(owner:$owner,name:$name) {
    nameWithOwner
    pullRequest(number:$number) {
      number url headRefOid state isDraft updatedAt reviewDecision
      comments { totalCount }
      reviews(first:100) {
        totalCount pageInfo { hasNextPage hasPreviousPage }
        nodes { id state submittedAt author { __typename login } commit { oid } }
      }
      reviewThreads(first:100) {
        totalCount pageInfo { hasNextPage hasPreviousPage }
        nodes {
          id isResolved
          comments(first:100) {
            totalCount pageInfo { hasNextPage hasPreviousPage }
            nodes { id url body updatedAt author { __typename login } commit { oid } replyTo { id } }
          }
        }
      }
    }
  }
}"""


class NotReady(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise NotReady(message)


def digest(data):
    return "sha256:" + hashlib.sha256(data).hexdigest()


def require_external_runner(target):
    runner = Path(__file__).resolve()
    require(runner != target and target not in runner.parents,
            "Guard must run from a trusted path outside --target; never execute the candidate checkout guard.")


def strict_json(data):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "Duplicate JSON key: " + key)
            result[key] = value
        return result
    return json.loads(data, object_pairs_hook=pairs)


def connection(value, label):
    require(isinstance(value, dict), label + ": missing connection")
    nodes, count, page = value.get("nodes"), value.get("totalCount"), value.get("pageInfo")
    require(isinstance(nodes, list) and type(count) is int and isinstance(page, dict),
            label + ": unknown pagination shape")
    require(page.get("hasNextPage") is False and page.get("hasPreviousPage") is False
            and count == len(nodes), label + ": incomplete pagination; collect every page before readiness")
    ids = [node.get("id") for node in nodes if isinstance(node, dict)]
    require(len(ids) == count and all(isinstance(item, str) and item for item in ids)
            and len(set(ids)) == count, label + ": missing or duplicate node IDs")
    return nodes


def graphql_bot(author):
    return (isinstance(author, dict) and author.get("__typename") == "Bot"
            and author.get("login") in (BOT_GRAPHQL, BOT))


def inspect_review(snapshot, repository, number, head):
    """Validate complete API data; this function performs no network or writes."""
    require(isinstance(snapshot, dict), "Missing API snapshot")
    graph = snapshot.get("graphql", {})
    require(isinstance(graph, dict) and not graph.get("errors"), "GraphQL errors or missing response")
    repo = graph.get("data", {}).get("repository")
    require(isinstance(repo, dict) and repo.get("nameWithOwner", "").casefold() == repository.casefold(),
            "Canonical API repository differs from --repo")
    canonical = repo["nameWithOwner"]
    pr = repo.get("pullRequest")
    require(isinstance(pr, dict) and pr.get("number") == number
            and pr.get("url") == "https://github.com/{}/pull/{}".format(canonical, number),
            "Canonical API pull request differs from --pr")
    require(pr.get("headRefOid") == head, "PR head changed or differs from --head; review the final SHA")
    require(pr.get("isDraft") is False and pr.get("state") in ("OPEN", "MERGED"),
            "PR is draft, closed without merge or has unknown state")
    require(pr.get("reviewDecision") in (None, "APPROVED"),
            "PR still requires approval or has requested changes")
    comments = snapshot.get("issue_comments")
    require(isinstance(comments, list) and pr.get("comments", {}).get("totalCount") == len(comments),
            "Issue comments: incomplete pagination")
    ids = [comment.get("id") for comment in comments if isinstance(comment, dict)]
    require(len(ids) == len(comments) and all(type(item) is int for item in ids)
            and len(set(ids)) == len(ids), "Issue comments: missing or duplicate IDs")
    summaries = [comment for comment in comments
                 if isinstance(comment.get("body"), str) and SUMMARY_MARKER in comment["body"]
                 and comment.get("user", {}).get("login") == BOT
                 and comment.get("user", {}).get("type") == "Bot"]
    require(summaries, "Missing trusted Codex bot summary; wait for the exact-head code and security reviews")
    require(all(isinstance(item.get("updated_at"), str) for item in summaries), "Unknown summary timestamp")
    summary = max(summaries, key=lambda item: (item["updated_at"], item["id"]))
    require(summary.get("html_url") == pr["url"] + "#issuecomment-" + str(summary["id"]),
            "Noncanonical Codex summary URL")
    markers = STATE_PATTERN.findall(summary["body"])
    require(len(markers) == 1, "Missing, duplicate or unknown Codex summary state marker")
    states = strict_json(markers[0])
    require(isinstance(states, dict), "Unknown Codex summary state")
    for kind in ("code_review", "security_review"):
        state = states.get(kind)
        require(isinstance(state, dict) and state.get("commit_sha") == head,
                kind + ": missing or wrong reviewed head; request review of the final SHA")
        require(state.get("status") == "completed", kind + ": not completed; wait for review")
        require(type(state.get("has_any_findings")) is bool
                and state.get("has_unresolved_findings") is False,
                kind + ": unknown or unresolved findings; triage and refresh the final-head review")
    for review in connection(pr.get("reviews"), "Reviews"):
        if graphql_bot(review.get("author")):
            require(review.get("state") in ("APPROVED", "COMMENTED", "DISMISSED", "CHANGES_REQUESTED"),
                    "Codex review is pending or has an unknown state")
            require(isinstance(review.get("submittedAt"), str), "Codex review lacks submission time")
            require(not (review.get("commit", {}).get("oid") == head
                         and review.get("state") == "CHANGES_REQUESTED"),
                    "Final-head Codex review still requests changes")
    findings = {}
    current_kinds = set()
    for thread in connection(pr.get("reviewThreads"), "Review threads"):
        require(thread.get("isResolved") is True, "Unresolved or unknown review thread: " + thread["id"])
        thread_comments = connection(thread.get("comments"), "Thread " + thread["id"])
        require(thread_comments, "Empty review thread cannot be verified")
        finding_ids = {comment["id"] for comment in thread_comments if graphql_bot(comment.get("author"))
                       and isinstance(comment.get("body"), str)
                       and any(marker in comment["body"] for marker in FINDING_MARKERS)}
        for comment in thread_comments:
            body = comment.get("body")
            require(isinstance(body, str), "Unknown review-comment body")
            if not graphql_bot(comment.get("author")):
                require(not any(marker in body for marker in FINDING_MARKERS),
                        "Finding marker has an untrusted or missing bot author")
                continue
            kinds = [kind for marker, kind in FINDING_MARKERS.items() if marker in body]
            if not kinds:
                # A plain reply to a known finding is discussion, not another finding.
                # Unknown finding markers and priority-bearing text still fail closed.
                require(not re.search(r"codex-[a-z-]*finding|\bP[0-3]\b", body)
                        and isinstance(comment.get("replyTo"), dict)
                        and comment["replyTo"].get("id") in finding_ids,
                        "Unclassified Codex review comment; inspect it and refresh supported review data")
                continue
            require(len(kinds) == 1, "Unclassified Codex review comment; inspect it and refresh supported review data")
            url = comment.get("url")
            require(isinstance(url, str) and re.fullmatch(
                re.escape(pr["url"]) + r"#discussion_r[0-9]+", url), "Noncanonical finding URL")
            require(url not in findings, "Duplicate finding URL")
            findings[url] = comment
            if comment.get("commit", {}).get("oid") == head:
                current_kinds.add(kinds[0])
    for kind in ("code_review", "security_review"):
        require(not states[kind]["has_any_findings"] or kind in current_kinds,
                kind + ": summary findings are absent from the complete thread data")
    return {"findings": findings, "summary_url": summary.get("html_url"), "states": states}


def evidence_file(target, relative):
    require(isinstance(relative, str) and relative and "\\" not in relative, "Invalid evidence path")
    path = Path(relative)
    require(not path.is_absolute() and ".." not in path.parts and path.as_posix() == relative,
            "Evidence path must be canonical and repository-relative")
    current = target
    for part in path.parts:
        current = current / part
        require(not current.is_symlink(), "Symlink evidence path is not allowed")
    require(current.is_file(), "Missing evidence file: " + relative)
    return current


def package_inputs(target):
    """Enumerate actual package inputs without trusting target code or Git ignores."""
    paths = set()
    for relative in PACKAGE_FILES:
        path = target / relative
        require(path.exists() or path.is_symlink(), "Missing required package file: " + relative)
        evidence_file(target, relative)
        require(stat.S_ISREG(path.lstat().st_mode), "Non-regular package input: " + relative)
        paths.add(relative)

    def visit(directory):
        with os.scandir(directory) as entries:
            children = sorted(entries, key=lambda entry: entry.name)
        for entry in children:
            path = Path(entry.path)
            relative = path.relative_to(target).as_posix()
            mode = entry.stat(follow_symlinks=False).st_mode
            require(not stat.S_ISLNK(mode), "Symlink package input is not allowed: " + relative)
            if stat.S_ISDIR(mode):
                # The packager also inspects excluded cache trees for symlinks.
                visit(path)
            elif "__pycache__" not in path.parts and path.suffix != ".pyc":
                require(stat.S_ISREG(mode), "Non-regular package input: " + relative)
                paths.add(relative)

    for relative in PACKAGE_TREES:
        directory = target / relative
        require(directory.exists() or directory.is_symlink(), "Missing required package tree: " + relative)
        require(stat.S_ISDIR(directory.lstat().st_mode), "Expected a real package directory: " + relative)
        visit(directory)
    return paths


def inspect_dispositions(path, target, repository, number, head, findings):
    """Return hashes for every local input that must remain unchanged."""
    if path is None:
        require(not findings, "Missing private --dispositions for reviewed findings")
        return {}
    require(not path.is_symlink() and path.is_file(), "Missing or symlink disposition file")
    data = path.read_bytes()
    value = strict_json(data)
    require(isinstance(value, dict) and type(value.get("schema_version")) is int and value.get("schema_version") == 1
            and value.get("repository") == repository and type(value.get("pr")) is int and value.get("pr") == number
            and value.get("reviewed_head") == head, "Dispositions do not bind this repository, PR and final reviewed head")
    rows = value.get("findings")
    require(isinstance(rows, list), "Dispositions findings must be a list")
    urls = [row.get("comment_url") for row in rows if isinstance(row, dict)]
    require(len(urls) == len(rows) and all(isinstance(url, str) for url in urls)
            and len(set(urls)) == len(urls) and set(urls) == set(findings),
            "Every reviewed finding needs exactly one disposition; unknown and duplicate URLs are rejected")
    inputs = {path.resolve(): digest(data)}
    for row in rows:
        require(row.get("comment_sha256") == digest(findings[row["comment_url"]]["body"].encode("utf-8")),
                "Changed or unbound finding comment; review its current text and update the disposition")
        require(row.get("decision") in ("fixed", "rejected"),
                "Only fixed/rejected dispositions are supported; owner_accepted_risk needs a separate explicit owner decision and review process")
        require(isinstance(row.get("reason"), str) and row["reason"].strip(), "Disposition reason is required")
        proofs = row.get("evidence")
        require(isinstance(proofs, list) and proofs, "Disposition needs hash-bound evidence")
        seen = set()
        for proof in proofs:
            require(isinstance(proof, dict) and set(proof) == {"path", "sha256"}, "Unknown evidence proof shape")
            relative = proof["path"]
            file_path = evidence_file(target, relative)
            require(relative not in seen, "Duplicate disposition evidence path")
            seen.add(relative)
            require(isinstance(proof["sha256"], str) and re.fullmatch(r"sha256:[0-9a-f]{64}", proof["sha256"])
                    and digest(file_path.read_bytes()) == proof["sha256"], "Changed or invalid disposition evidence: " + relative)
            inputs[file_path] = proof["sha256"]
    return inputs


def tool_stat(path):
    info = path.stat()
    require(stat.S_ISREG(info.st_mode) and os.access(path, os.X_OK), "Expected a regular executable tool: " + str(path))
    return {"device": info.st_dev, "inode": info.st_ino, "mode": info.st_mode,
            "size": info.st_size, "mtime_ns": info.st_mtime_ns, "ctime_ns": info.st_ctime_ns}


class Live:
    def __init__(self, timeout, target, git, gh):
        self.deadline = time.monotonic() + timeout
        self.target = target.resolve()
        self.tools = {}
        self.tool_proofs = {}
        # Bind both before executing either: a rejected gh must not run a git canary.
        for name, configured in (("git", git), ("gh", gh)):
            require(isinstance(configured, (str, Path)) and bool(str(configured)),
                    "Explicit --" + name + " absolute trusted executable path is required")
            candidate = Path(configured)
            require(candidate.is_absolute(), "--" + name + " must be an absolute trusted executable path")
            lexical = Path(os.path.abspath(str(candidate)))
            resolved = lexical.resolve(strict=True)
            for path in (lexical, resolved):
                require(path != self.target and self.target not in path.parents,
                        "Executable " + name + " must be outside --target: " + str(path))
            self.tools[name] = str(resolved)
            before = tool_stat(resolved)
            proof = dict(before, path=str(resolved), sha256=digest(resolved.read_bytes()))
            require(tool_stat(resolved) == before, "Executable changed during binding: " + name)
            self.tool_proofs[name] = proof
        directories = list(dict.fromkeys(str(Path(path).parent) for path in self.tools.values()))
        self.environment = dict(os.environ, PATH=os.pathsep.join(directories + ["/usr/bin", "/bin"]))

    def verify_tools(self, full=True):
        for name, path in self.tools.items():
            expected = self.tool_proofs[name]
            require(Path(path).resolve(strict=True) == Path(path), "Executable path changed during validation: " + name)
            actual = tool_stat(Path(path))
            require(actual == {key: expected[key] for key in actual}, "Executable identity changed during validation: " + name)
            if full:
                require(digest(Path(path).read_bytes()) == expected["sha256"], "Executable bytes changed during validation: " + name)
                require(tool_stat(Path(path)) == actual, "Executable changed during validation: " + name)
        return self.tool_proofs

    def command(self, argv, binary=False):
        remaining = self.deadline - time.monotonic()
        require(remaining > 0, "Read-only review check timed out; retry without merging")
        self.verify_tools(full=False)
        require(argv and argv[0] in self.tools.values(), "Only bound absolute executables may run")
        try:
            result = subprocess.run(argv, capture_output=True, text=not binary, timeout=remaining, env=self.environment)
        except subprocess.TimeoutExpired as error:
            raise NotReady("Read-only review check timed out; retry without merging") from error
        stderr = result.stderr.decode("utf-8", errors="replace") if isinstance(result.stderr, bytes) else result.stderr
        require(result.returncode == 0, "Read-only command failed: " + " ".join(argv[:4]) + "; " + stderr.strip())
        return result.stdout

    def snapshot(self, repository, number):
        self.verify_tools()
        owner, name = repository.split("/")
        graph = strict_json(self.command([self.tools["gh"], "api", "--hostname", "github.com", "graphql", "-f", "query=" + QUERY,
                                         "-F", "owner=" + owner, "-F", "name=" + name, "-F", "number=" + str(number)]))
        pages = strict_json(self.command([self.tools["gh"], "api", "--hostname", "github.com", "--paginate", "--slurp",
                                         "repos/{}/issues/{}/comments?per_page=100".format(repository, number)]))
        require(isinstance(pages, list) and all(isinstance(page, list) for page in pages), "Unknown issue-comment pagination response")
        self.verify_tools()
        return {"graphql": graph, "issue_comments": [comment for page in pages for comment in page]}

    def source(self, target):
        target = target.resolve()
        require(target == self.target, "Live source target differs from bound tool target")
        require_external_runner(target)
        self.verify_tools()
        git = [self.tools["git"], "--no-optional-locks", "--no-replace-objects", "-C", str(target)]
        top = Path(self.command(git + ["rev-parse", "--show-toplevel"]).strip()).resolve()
        require(top == target, "--target must be the checkout root")
        head = self.command(git + ["rev-parse", "HEAD"]).strip()
        status = self.command(git + ["status", "--porcelain=v1", "--untracked-files=normal"])
        require(not status, "Source checkout is dirty; commit the final source before requesting final-head readiness")
        entries = self.command(git + ["ls-tree", "-r", "--full-tree", "-z", "HEAD"]).split("\0")
        hashes = {}
        for entry in entries:
            if entry:
                metadata, relative = entry.split("\t", 1)
                mode, kind, oid = metadata.split()
                require(kind == "blob" and mode in ("100644", "100755"), "Unsupported source tree entry: " + relative)
                path = evidence_file(target, relative)
                data = path.read_bytes()
                committed = self.command(git + ["cat-file", "blob", oid], binary=True)
                require(data == committed, "Source bytes differ from reviewed HEAD: " + relative)
                require(bool(path.stat().st_mode & stat.S_IXUSR) == (mode == "100755"),
                        "Source executable mode differs from reviewed HEAD: " + relative)
                hashes[relative] = {"sha256": digest(data), "mode": mode}
        packaged = package_inputs(target)
        unreviewed = sorted(packaged - set(hashes))
        require(not unreviewed, "Unreviewed package input is absent from reviewed HEAD: " + ", ".join(unreviewed))
        self.verify_tools()
        return {"head": head, "files": hashes, "package_files": sorted(packaged)}


def check(repository, number, head, target, dispositions, live):
    live.verify_tools()
    before = live.source(target)
    require(before["head"] == head, "Local HEAD differs from --head; review the exact final source commit")
    snapshot = live.snapshot(repository, number)
    result = inspect_review(snapshot, repository, number, head)
    inputs = inspect_dispositions(dispositions, target, repository, number, head, result["findings"])
    refreshed = live.snapshot(repository, number)
    require(refreshed == snapshot, "GitHub review/head changed during validation; rerun on the final state")
    require(live.source(target) == before, "Source HEAD or files changed during validation; rerun the exact final source")
    for path, expected in inputs.items():
        try:
            relative = path.relative_to(target).as_posix()
        except ValueError:
            relative = None
        if relative is not None:
            evidence_file(target, relative)
        require(path.is_file() and not path.is_symlink() and digest(path.read_bytes()) == expected,
                "Disposition or evidence changed during validation; review the new bytes")
    tools = live.verify_tools()
    return {"readiness": "READY", "repository": repository, "pr": number, "reviewed_head": head,
            "code_review": "completed", "security_review": "completed", "findings": len(result["findings"]),
            "unresolved_threads": 0, "summary_url": result["summary_url"],
            "tools": tools,
            "scope": "Recorded exact-head Codex reviews, resolved threads and hash-bound dispositions; CI and semantic evidence assessment remain separate."}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, help="canonical GitHub owner/repository")
    parser.add_argument("--pr", required=True, type=int)
    parser.add_argument("--head", required=True, help="exact lowercase 40-digit commit SHA")
    parser.add_argument("--target", type=Path, default=Path.cwd())
    parser.add_argument("--git", type=Path, required=True, help="required owner-trusted absolute git executable")
    parser.add_argument("--gh", type=Path, required=True, help="required owner-trusted absolute gh executable")
    parser.add_argument("--dispositions", type=Path, help="private JSON; never commit the working review register")
    parser.add_argument("--timeout-seconds", type=float, default=30)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        require(re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", args.repo) and args.pr > 0
                and re.fullmatch(r"[0-9a-f]{40}", args.head), "Invalid repository, PR or exact head")
        require(0 < args.timeout_seconds <= 300, "--timeout-seconds must be in (0, 300]")
        target = args.target.resolve()
        require_external_runner(target)
        result = check(args.repo, args.pr, args.head, target, args.dispositions,
                       Live(args.timeout_seconds, target, args.git, args.gh))
        code = 0
    except (NotReady, OSError, ValueError, TypeError, KeyError, AttributeError) as error:
        result = {"readiness": "NOT_READY", "repository": args.repo, "pr": args.pr,
                  "reviewed_head": args.head, "blocker": str(error)}
        code = 1
    print(json.dumps(result, sort_keys=True) if args.json else result["readiness"] + ": " +
          (result["blocker"] if "blocker" in result else result["scope"]))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
