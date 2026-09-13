# Security Policy

## Supported version

Only the current release, Project OS 1.0.1, is supported. The installed skill and every connected
repository move to that version together.

## Report a vulnerability

Do not include exploit details, credentials, repository contents or other sensitive material in a
public issue.

Use GitHub's private vulnerability reporting for this repository when it is available. If that option
is unavailable, open a public issue containing no sensitive details and ask the maintainer for a
private reporting channel.

Include:

- the affected Project OS version;
- operating system and Python version;
- the exact command or Codex workflow boundary;
- expected and observed behavior;
- a minimal sanitized repository when possible.

## Runtime boundary

The v1.0.1 helper uses the Python standard library and initiates no network request. Its normal
operations read bundled assets and inspect or write only within the target repository selected by the
user. Installing or updating the skill from GitHub is a separate network operation performed by Codex
or Git.

Project OS contains no daemon, watcher, MCP server, lifecycle hook, hidden database or automatic
cross-project synchronization. The helper runs only when a person or Codex invokes it.

## File safety

Project OS is designed to fail closed on:

- absolute, escaping or otherwise unsafe managed paths;
- symlink replacement boundaries;
- malformed plan, finding or knowledge registries;
- incompatible record ownership during adoption;
- locally divergent managed guidance or knowledge;
- concurrent changes detected before an atomic replacement;
- credentials, private paths, personal data and other prohibited material in shared knowledge.

A dry run and human review are still required before initialization, adoption, repair or knowledge
synchronization in a mature repository.

## Authority boundary

`$project-os` selects a workflow. It does not grant new authority.

Project OS does not authorize dependency installation, application changes, file deletion, branch
changes, commits, pushes, deployments, publication or communication with external systems. Those
actions still require the current user's request and the target repository's instructions.

Repository records can also be stale or wrong. A passing Project OS checker proves structural
consistency, not application correctness, artifact identity, deployment state, production behavior or
manual and physical acceptance.

## Knowledge safety

Do not put credentials, tokens, personal data, private machine paths, private URLs, signed URLs, raw
production logs or copied project history in shared knowledge, fixtures or vulnerability examples.

Sanitization must preserve the engineering mechanism, applicability, trigger, prevention, decisive
verification and limits. If removing private context makes the lesson misleading, keep it in
project-specific knowledge instead.
