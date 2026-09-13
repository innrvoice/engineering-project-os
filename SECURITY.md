# Security Policy

## Supported version

Only Project OS 2.0.0 is supported by this source tree. Install the release first, then upgrade each
connected repository explicitly. Updating the installed skill does not update repositories by itself.

## Report a vulnerability

Do not include exploit details, credentials, repository contents or other sensitive material in a
public issue.

Use GitHub private vulnerability reporting when it is available. If it is unavailable, open a public
issue containing no sensitive details and ask the maintainer for a private reporting channel.

Include:

- affected Project OS version;
- operating system and Python version;
- exact helper command or Codex workflow boundary;
- expected and observed behavior;
- a minimal sanitized repository when possible.

## Runtime boundary

The 2.0.0 helper uses the Python standard library and initiates no network request. It reads bundled
assets and the target repository selected by the user. Commands with an explicit `--config` or
`--definition` may also read that user-selected file outside the target. Mutating operations write
only inside the target repository. Installing or updating the standalone skill from GitHub is a
separate network operation.

Project OS contains no daemon, watcher, MCP server, lifecycle hook, hidden database or automatic
cross-project synchronization. The helper runs only when a person or Codex invokes it.

## File safety

Project OS is designed to fail closed on:

- absolute, escaping or unsafe managed paths;
- symlink replacement boundaries;
- malformed Program, plan, finding, history or knowledge records;
- incompatible ownership during adoption;
- locally divergent managed guidance or knowledge;
- incomplete or ambiguous legacy Program migration;
- concurrent changes before an atomic replacement;
- common detectable credential, private-path and private-URL patterns in shared knowledge.

A mutating Codex request must inspect, preview or dry-run, apply only a clean result and finish with
the checker. Direct helper users must review `--dry-run` output before init, adopt, upgrade, Program
start, Program close or synchronization.

## Program archive boundary

Closing a Program stores the exact contract bytes and records a SHA-256 digest in the history index.
The checker detects missing archives, invalid closure metadata and content that no longer matches its
recorded digest.

This archive is tamper-evident, not technically immutable. It is not signed and does not prevent a
person with write access from deliberately changing both archive and index. Git review, repository
access control and backups remain separate security boundaries.

Treat a hash mismatch as an integrity event. Compare trusted Git history and repository evidence
before restoring either side. Never accept changed bytes merely by updating their recorded digest.

## Authority boundary

`$project-os` selects a skill workflow for one message. It does not grant new authority.

Project OS does not authorize dependency installation, application changes, deletion, branch changes,
commits, pushes, deployment, publication or communication with external systems. Those actions still
require the user's request and applicable repository instructions.

A passing checker proves structural consistency, not application correctness, artifact identity,
deployment state, production behavior or manual and physical acceptance.

## Knowledge safety

Do not put credentials, tokens, personal data, private machine paths, private URLs, signed URLs, raw
production logs or copied project history in shared knowledge, fixtures or vulnerability examples.

The helper rejects a bounded set of recognizable sensitive patterns. Pattern matching cannot prove
that arbitrary text is sanitized, so human review remains mandatory before a lesson is shared or
published.

Sanitization preserves the mechanism, applicability, trigger, prevention, decisive verification and
limits. If removing private context makes a lesson misleading, keep it in project-specific knowledge.
