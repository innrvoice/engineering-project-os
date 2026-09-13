---
name: project-os
description: Inspect, bootstrap, adopt, validate, upgrade, or maintain a repository-local engineering operating system using AGENTS.md and .agents state, plans, findings, evidence, and reusable failure knowledge. Use when a user asks to set up project instructions, make long-running work resumable, repair workflow state, or capture a confirmed reusable engineering lesson. Do not use for ordinary coding that already has a healthy project workflow.
---

# Project OS

Create and maintain a small control plane around the repository without changing application behavior.

## Invocation boundary

`$project-os` explicitly selects this skill for the current user message. The text after the skill name
is an ordinary natural-language request and can be written in any language. It is not a shell command,
an environment variable, a command language, or a persistent mode.

Installing the skill only makes it available to Codex. It does not modify a repository. Once Project OS
has been added to a repository, ordinary engineering requests should use the applicable `AGENTS.md`
instructions and repository records without requiring `$project-os` again.

Codex discovers applicable `AGENTS.md` files as repository instructions when a task starts. Those files
route it to the relevant `.agents` records; do not treat the whole directory as eager prompt context.

Use this skill when the requested object is the repository control plane itself: setup, adoption,
validation, repair, upgrade, durable plan or checkpoint state, findings, evidence, or failure knowledge.
For a bounded code or product change that needs none of those operations, follow the repository's
existing instructions and do not create Project OS records merely because this skill was invoked.

## Select the operation

- For first-time setup or adding Project OS to an existing repository, read
  [bootstrap.md](references/bootstrap.md).
- For a consistency check, plan lifecycle change, checkpoint, repair, or version upgrade, read
  [maintenance.md](references/maintenance.md).
- For recording, promoting, importing, or synchronizing a failure lesson, read
  [knowledge.md](references/knowledge.md).

## Shared constraints

- Inspect the target repository, Git status, existing `AGENTS.md`, project documentation, and actual
  tool configuration before writing.
- Existing user and repository instructions take precedence over this skill.
- Never overwrite an existing `AGENTS.md`, project state, finding, plan, or knowledge entry blindly.
- Keep application code, production configuration, credentials, personal data, and runtime artifacts
  outside this workflow unless the user's task independently requires changing them.
- Use Lite mode unless the user requests a structured audit/program or the work clearly needs a durable
  multi-phase register.
- Record only verified repository facts. Mark unresolved facts as unverified instead of inventing
  commands, architecture, ownership, or product requirements.
- Keep concrete project incidents separate from portable lessons. Promote only confirmed and sanitized
  failure mechanisms.
- Run the deterministic checker after creating or changing Project OS records.
- Do not imply that Project OS runs a daemon, watcher, hook, MCP server, hidden database, automatic
  upload, or automatic cross-repository synchronization. Durable state is stored in repository files;
  the helper changes them only when it is explicitly run.

The helper entrypoint is `scripts/project_os.py` relative to this skill directory. Resolve that path
from the installed skill, not from the target repository. Use `--dry-run` before initialization,
adoption, or synchronization. There is no `upgrade` subcommand; use the synchronization sequence in
[maintenance.md](references/maintenance.md).
