---
name: project-os
description: Bootstrap, inspect, validate, or maintain a repository-local engineering operating system using AGENTS.md and .agents state, plans, findings, evidence, and reusable failure knowledge. Use when a user asks to set up project instructions, make long-running work resumable, repair project workflow state, or capture a confirmed reusable engineering lesson. Do not trigger for ordinary coding that already has a healthy project workflow.
---

# Project OS

Create a small control plane around the repository without changing application behavior.

## Select the operation

- For first-time setup or adding Project OS to an existing repository, read
  [bootstrap.md](references/bootstrap.md).
- For a consistency check, plan lifecycle change, checkpoint, or repair, read
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

The helper entrypoint is `scripts/project_os.py`. Use `--dry-run` before initialization when the target
already contains project instructions or `.agents` state.
