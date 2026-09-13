# Security Policy

## Supported versions

| Version | Supported |
| --- | --- |
| 1.0.x | Yes |
| Earlier versions | No |

Security fixes are released on the latest supported version.

## Report a vulnerability

Do not include exploit details, credentials, repository contents, or other sensitive material in a
public issue.

Use GitHub's private vulnerability reporting for this repository when it is available. If that option
is unavailable, open a public issue containing no sensitive details and ask the maintainer for a
private reporting channel.

Include the affected version, operating system, Python version, reproduction boundary, expected
behavior, and observed behavior. Use a minimal sanitized repository when possible.

## Security boundary

The v1.0.0 helper uses the Python standard library and does not initiate network requests. Its normal
operations read bundled assets and inspect or write within the target repository selected by the user.
Installation from GitHub is handled separately by Codex or Git.

Project OS is designed to reject unsafe managed paths, symlink replacements, malformed registries,
unsanitized portable knowledge, and conflicting synchronization rather than silently overwriting
state. A dry run and review are still required before initialization, adoption, or knowledge sync in a
mature repository.

Project OS does not grant authority to install dependencies, modify application code, commit, push,
deploy, publish, or contact external systems.
