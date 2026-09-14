---
name: project-os
description: Inspect, bootstrap, adopt, validate, upgrade or maintain a repository-local engineering operating system using AGENTS.md and .agents state, Programs, plans, findings, evidence and reusable failure knowledge. Use when the user explicitly wants to set up or operate that control plane. Do not use for ordinary coding in a repository with a healthy workflow.
---

# Project OS

Create and maintain a small repository control plane without changing application behavior unless the user separately asks for application work.

## Invocation boundary

In ChatGPT, `@Engineering Project OS` explicitly selects the plugin or bundled skill. In Codex, `$project-os` explicitly selects the bundled skill. The request text is ordinary natural language in any language. It is not a shell command, environment variable, rigid command grammar or persistent mode.

Installing the plugin makes the skill available to ChatGPT and Codex. It does not modify a repository. Once Project OS is connected, ordinary engineering requests follow applicable `AGENTS.md` instructions without requiring `$project-os`.

Use this skill only for Project OS requests. ChatGPT may expose it automatically when the installed plugin is selected or the request clearly matches, but do not apply it to unrelated coding work.

Before inspecting or changing a repository, identify the available project input. In ChatGPT, setup advice and a new starter package may begin from the user's project description, selected project files or an archive provided in the current chat. Ask only for the missing details required to choose a safe setup and mark conclusions that are not backed by files as unverified. Reviewing, validating, repairing, adopting or upgrading an existing Project OS setup requires the relevant repository files, normally `AGENTS.md` and `.agents/`; ask for them when they are missing. Never inspect an empty host workspace or claim that the plugin is unavailable. In Codex, use the repository workspace selected for the current task. Installation alone does not attach or connect a repository on either surface.

## Interpret short requests

Treat the following as canonical, memorable prompts rather than parser tokens:

- `help`: read-only menu. No argument.
- `inspect`: read-only repository and setup inspection. No argument.
- `bootstrap`: create Standard. No argument.
- `adopt`: map compatible existing records. No argument.
- `check`: read-only deterministic validation. No argument.
- `repair`: repair verified Project OS errors. Require an error or scope if it is not already clear.
- `upgrade`: upgrade to the installed release. No argument.
- `program start: <initiative>`: require the initiative.
- `program status`: read-only status. No argument.
- `program close completed`: require complete exit evidence.
- `program close stopped: <reason>`: require a reason.
- `plan open: <outcome>`: require one observable outcome.
- `plan checkpoint`, `plan complete`: require an active plan.
- `plan resume[: <plan-id>]`: continue the active plan or reactivate a selected blocked plan after verifying its blocker is resolved. Require a plan ID when the selection is ambiguous.
- `plan block: <reason>`, `plan supersede: <reason>`: require a reason.
- `finding add: <observation>`: require a concrete observation.
- `knowledge capture: <finding-id>`: require a confirmed finding.
- `knowledge propose-shared: <lesson-id>`: require a project lesson and remain read-only.

Additional text, synonyms, punctuation and another language may refine the same intent. Prefer the clear intended operation over exact wording. A user constraint such as `do not change files` always keeps the request read-only.

For `help`, never write files or run an applying helper operation. Return a concise menu of every supported short request above, its purpose, required argument and one or two examples. Explicitly separate requests typed in Codex chat from Python helper commands run in Terminal.

If a request is ambiguous, show the relevant part of help or ask one focused question before any write. If the requested work is unrelated to Project OS, handle it as ordinary repository work and do not create control-plane records merely because the user included the prefix.

## Standard and Program

Standard is the complete default system. Bootstrap always creates Standard and never creates `PROGRAM.md`.

Program is a temporary umbrella contract for one explicitly started multi-phase initiative. A long task or durable plan alone does not justify Program. Start one only through a clear `program start: <initiative>` request and only after initiative, overall outcome, authority, at least two phases with phase outcomes and exit conditions, evidence requirements, cost boundaries, exclusions and overall exit conditions are complete.

Starting Program does not open a plan. Closing requires no active plan. A completed close requires exit evidence. A stopped close requires a reason. Close archives the exact contract and returns the repository to Standard.

Program archives are SHA-256 checked and tamper-evident, not technically immutable, signed or remotely protected.

When upgrading a closed legacy Program, require its actual closure date in canonical `YYYY-MM-DD` form from repository evidence. Never substitute the upgrade date.

## Route to focused instructions

- For `inspect`, `bootstrap` or `adopt`, read [bootstrap.md](references/bootstrap.md).
- For `check`, `repair`, `upgrade`, Program lifecycle or plan lifecycle, read [maintenance.md](references/maintenance.md).
- For findings or failure knowledge, read [knowledge.md](references/knowledge.md).
- `help` is fully specified above and does not require loading every reference.

## Mutation protocol

For every operation that may change Project OS files:

1. Inspect the target repository, Git status, applicable instructions and current record owners.
2. Prepare the intended change and use the matching helper `--dry-run` when available.
3. Review the complete preview. Stop on ambiguity, unsafe ownership, stale state or conflict.
4. Apply only the same clean operation.
5. Run the deterministic checker and report changed files and remaining unverified boundaries.

For reasoned plan, finding or knowledge edits without a dedicated helper subcommand, produce the equivalent read-only preview before writing and run the checker afterward.

## Shared constraints

- Existing user and repository instructions take precedence.
- Never overwrite `AGENTS.md`, context, state, a Program, plan, finding, evidence or knowledge blindly.
- Keep application code, production configuration, credentials, personal data and runtime artifacts outside Project OS operations unless the user's request independently authorizes them.
- Record only verified repository facts. Mark unresolved claims as unverified.
- Keep project incidents separate from portable lessons. Promote only confirmed, sanitized mechanisms.
- Do not imply a daemon, watcher, hook, MCP server, hidden database, automatic upload or automatic cross-repository synchronization.
- Project OS does not grant authority to install dependencies, delete files, commit, push, deploy, publish or contact external systems.

The helper entrypoint is `scripts/project_os.py` relative to the installed skill directory. Resolve that path from the installed skill, not from the target repository, except when explicitly testing the candidate helper while developing Project OS itself.
