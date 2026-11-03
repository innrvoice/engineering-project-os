---
name: project-os
description: Use this when Codex engineering work must survive multiple sessions, preserve verified repository state or transfer reviewed failure lessons between the user's own projects. Explain, inspect, bootstrap, adopt, validate, upgrade or maintain the repository-local control plane. ChatGPT is a companion for explanations, supplied project files and portable knowledge bundles. Do not use for ordinary one-session coding, generic project management or automatic global knowledge sharing.
---

# Project OS

Engineering Project OS was built for Codex. Create and maintain a small repository control plane that lets Codex resume real engineering work from visible state without changing application behavior unless the user separately asks for application work. ChatGPT can use the same skill as a companion over project material supplied in the conversation.

## Invocation boundary

In Codex, `$project-os` explicitly selects the bundled skill. In ChatGPT, `@Engineering Project OS` explicitly selects the plugin or bundled skill. The request text is ordinary natural language in any language. It is not a shell command, environment variable, rigid command grammar or persistent mode.

Installing the plugin makes the skill available in Codex and exposes its companion workflow in ChatGPT. It does not modify a repository. Once Project OS is connected, ordinary Codex engineering requests follow applicable `AGENTS.md` instructions without requiring `$project-os`.

Use this skill only for Project OS requests. The host may expose it automatically when the installed plugin is selected or the request clearly matches, but do not apply it to unrelated coding work.

Before inspecting or changing a repository, identify the available project input. In Codex, use the repository workspace selected for the current task and accept an explicit path to another schema 5 repository as a read-only knowledge source. In ChatGPT, setup advice and a new starter package may begin from the user's project description, selected project files or an archive provided in the current chat. Ask only for the missing details required to choose a safe setup and mark conclusions that are not backed by files as unverified. Reviewing, validating, repairing, adopting or upgrading an existing Project OS setup requires the relevant repository files, normally `AGENTS.md` and `.agents/`; ask for them when they are missing. Knowledge import requires an approved reusable bundle plus the destination Project OS context. Knowledge export requires the source reusable registry. Never inspect an empty host workspace or claim that the plugin is unavailable. Installation alone does not attach or connect a repository on either surface.

## Recovery capabilities

Identify readable project files, the selected helper and permitted execution before choosing a recovery route. When helper execution is available and allowed, use the compact inspection below. If the selected older helper genuinely lacks `brief`, keep that helper selected, run its supported `check` and `checkpoint --check` commands and read the configured record owners. Disclose unsupported checks. If a required validation or writeback command is also unsupported, leave that operation incomplete and request a suitable selected helper. A failed integrity check is not an older-helper compatibility case; never silently substitute another helper.

For read-only Python checks, use `python3 -B` or `PYTHONDONTWRITEBYTECODE=1`, including inline helper imports. Compare each protected tree's complete path set and file hashes before and after execution; an added `__pycache__` is a mutation. Preserve existing caches and required input files rather than deleting or excluding them to hide a mismatch.

When execution is unavailable or forbidden, or the selected helper is missing, inspect only readable supplied files. Describe recorded work and permissions as file-derived observations; mark integrity, checkpoint freshness and readiness checks unverified. Do not invent a `brief` result, PASS, CURRENT or executed command. Preserve input bytes and pending gates; do not change records, create a receipt or close a plan through this fallback. Report that required writeback and export validation were not performed and name the specific missing capability or material. Ask only for what is needed to continue. Do not attempt a prohibited command to test availability. See [maintenance.md](references/maintenance.md) for the routes.

## Everyday knowledge requests

In a connected repository, ordinary development follows repository instructions that require Codex to record findings discovered during the task without a separate save request. Keep evidence, hypotheses and confirmed mechanisms distinct; prepare project lessons only after confirmation. This is agent-led work, not a background scan or a guarantee of exhaustive discovery.

When recording a material instruction, copy the complete relevant original user text verbatim into `source_text`, including conditions, exclusions and approval limits. Do not shorten, summarize, translate or replace wording with ellipses; put your interpretation in `interpretation`. For a message covering several outcomes, retain this outcome's complete block and every shared condition that applies to it without copying unrelated project material. Compare the saved text with the actual message before relying on it. On withdrawal, preserve the original `source_text` and quote the complete relevant cancellation wording verbatim in `decision` before explaining the disposition. The helper can validate record structure and hashes, but cannot establish fidelity to a conversation it cannot access.

When the required helper execution is available and permitted, use the connected WORKFLOW's required writeback before any engineering response or returned project snapshot, including bounded repairs and ChatGPT companion operations. A reproduced user-reported defect is a finding too. Save actual evidence with `finding record`, update the checkpoint through `checkpoint --draft` or guarded plan completion and pass `checkpoint --check`; plan completion writes its fresh idle receipt atomically. Successful application tests or knowledge import alone do not persist that handoff. On fresh recovery, verify the saved checkpoint against current files before using its next action. The read-only capability fallback above preserves files and reports missing writeback instead. See [maintenance.md](references/maintenance.md) for the deterministic commands.

For a validated Project OS snapshot, freshly reread on-disk bytes after all writes and checks. Preserve complete STATE including its HTML receipt, compute each file hash from those exact bytes and reconstruct the exact serialized snapshot into a new temporary directory. Run check and checkpoint --check on that reconstructed copy and compare original source hashes again after export. Never assemble returned files from drafts, cached variables or rendered Markdown. An exported-file mismatch is NOT_READY even when the source check reported CURRENT; deliver only the validated snapshot file when claiming this protocol passed. The connected WORKFLOW and maintenance reference give the full export protocol.

When execution of the bundled snapshot utility is permitted, use scripts/snapshot.py against the actual authorized source tree, with --require for every promised proposal, report or directory. Its recursive source inventory detects nested files omitted by a hand-written copier; a manifest of an already incomplete staging copy cannot. Keep the output outside that tree and reconstruct the actual archive. This utility checks byte preservation only and never runs project helpers or overrides their execution prohibitions. See the [snapshot recipe](references/maintenance.md#return-exact-project-files).

If execution or artifact creation is unavailable, do not claim a validated export or invent a download link. When file operations are permitted, the host may return the unchanged input or a byte-preserving transport copy with factual hashes. Preserve the whole STATE receipt and clearly label helper checks and Project OS export validation unperformed. Such a copy does not establish record integrity or checkpoint freshness. A text report or proposed command does not prove that a file was created or a check ran.

When the user asks to reuse accumulated lessons in another repository, treat that as an outcome to carry through, not a request for a manual command catalog. Read [knowledge.md](references/knowledge.md), inspect the destination and the read-only source, handle any required setup and preparation, select lessons that fit the destination and show one batch review of lesson changes. This approval-dependent outcome needs a small plan: route its request and later approval to the same contract, then verify gates and mark the requests implemented before guarded completion. Captured requests are unresolved even if their decision text says completed. After approval, finish the reviewed transfer and validate the result. If the source has only confirmed findings or project lessons, prepare sanitized proposals outside both repositories and approve matching entries directly into the destination; do not modify the source merely to complete a transfer. Keep approval and applicability boundaries explicit.

## Interpret short requests

Treat the following as canonical, memorable prompts rather than parser tokens:

- `overview`: read-only product explanation. No argument or repository input.
- `help`: read-only menu. No argument.
- `inspect`: read-only repository and setup inspection. No argument.
- `bootstrap`: create Standard. No argument.
- `adopt`: map compatible existing records. No argument.
- `check`: read-only deterministic validation. No argument.
- `brief`: read-only compact record integrity, checkpoint and unresolved-work report. No argument.
- `repair`: repair verified Project OS errors. Require an error or scope if it is not already clear.
- `upgrade`: upgrade to the installed release. No argument.
- `program start: <initiative>`: require the initiative.
- `program status`: read-only status. No argument.
- `program close completed`: require complete exit evidence.
- `program close stopped: <reason>`: require a reason.
- `plan open: <outcome>`: require one observable outcome.
- `plan checkpoint`, `plan complete`: require an active plan. Completion uses the guarded helper and atomically writes a current idle checkpoint receipt.
- `plan status[: <plan-id>]`: read-only gate and request report; require an ID when no single active plan exists.
- `plan resume[: <plan-id>]`: continue the active plan or reactivate a selected blocked plan after verifying its blocker is resolved. Require a plan ID when the selection is ambiguous.
- `plan block: <reason>`, `plan supersede: <reason>`: require a reason.
- `finding add: <observation>`: require a concrete observation.
- `knowledge capture: <finding-id>`: require a confirmed finding.
- `knowledge list: project|reusable`: list the selected user-owned knowledge without writing.
- `knowledge prepare: <lesson-id|all>`: prepare a sanitized proposal outside the repository and remain read-only.
- `knowledge approve: <proposal> <lesson-id|all>`: write only the reviewed proposal entries selected by the user.
- `knowledge revise: <lesson-id>`: prepare a reviewed replacement revision rather than silently overwriting an entry.
- `knowledge retire: <lesson-id> because <reason>`: retire a reusable lesson while preserving its lifecycle.
- `knowledge remove: <lesson-id>`: require a separate destructive preview and explicit confirmation, then refuse removal when the lesson belongs to a replacement chain.
- `knowledge export: <destination>`: export approved reusable lessons and complete lifecycle chains to a deterministic portable bundle.
- `knowledge import: <repo-or-bundle>`: preview active lessons applicable to the target plus lifecycle tombstones, then include every linked entry needed to keep selected replacement chains complete.
- `knowledge import all: <repo-or-bundle>`: explicitly preview every non-draft lesson and lifecycle tombstone before importing.
- `knowledge propose-shared: <lesson-id>`: deprecated read-only alias for `knowledge prepare` during the 2.1.0 transition.

Additional text, synonyms, punctuation and another language may refine the same intent. Prefer the clear intended operation over exact wording. A user constraint such as `do not change files` always keeps the request read-only.

For `overview`, never inspect a repository, ask for files or write anything. Explain that Engineering Project OS was built for Codex and is for developers whose AI-assisted engineering work spans sessions. Lead with the practical benefits: resume from verified repository state, preserve decisions and evidence, preview control-plane changes and turn confirmed failures into user-owned reusable knowledge. Explain that project knowledge stays local while a sanitized lesson moves directly from one user-controlled repository to another or through a portable bundle, always after human review and an explicit import. Do not imply a central database, publication requirement, hidden service or automatic learning. End with the next useful Codex workflow, then mention the ChatGPT companion for supplied files and portable bundles.

For `help`, never write files or run an applying helper operation. Return a concise menu of every supported short request above, its purpose, required argument and one or two examples. Explicitly separate requests typed in Codex chat from Python helper commands run in Terminal.

For `brief`, a fresh session, resumed repository work or recovery after compaction, first choose the applicable recovery capability route above. With permitted helper execution, read AGENTS and WORKFLOW, resolve the selected helper and run `brief --target <repository> --json` before opening full plan or request registries. Follow `read_next` for CONTEXT, STATE, the active Program contract when present and the active plan with its contract. Program authority, phases and cost boundaries still apply when no plan is active. When inspection passes, use the complete unresolved request objects and execution summary directly; do not reload historical registries or repeat standalone inspection checks merely to obtain the same facts. Use `record_paths` to inspect originals before editing them or when history, omitted detail, a missing field or a reported error requires it. A failed integrity check or unavailable records requires inspection of the reported errors; empty arrays then do not prove there is no unfinished work. A passing inspection can still contain a NOT_READY active plan and unresolved requests. The report does not replace the WORKFLOW, checkpoint writeback or final plan status gate. It does not authorize activating planned work. See [maintenance.md](references/maintenance.md).

If a request is ambiguous, show the relevant part of help or ask one focused question before any write. If the requested work is unrelated to Project OS, handle it as ordinary repository work and do not create control-plane records merely because the user included the prefix.

## Standard and Program

Standard is the complete default system. Bootstrap always creates Standard and never creates `PROGRAM.md`.

Program is a temporary umbrella contract for one explicitly started multi-phase initiative. A long task or durable plan alone does not justify Program. Start one only through a clear `program start: <initiative>` request and only after initiative, overall outcome, authority, at least two phases with phase outcomes and exit conditions, evidence requirements, cost boundaries, exclusions and overall exit conditions are complete.

Starting Program does not open a plan. Closing requires no active plan. A completed close requires exit evidence. A stopped close requires a reason. Close archives the exact contract and returns the repository to Standard.

Program archives are SHA-256 checked and tamper-evident, not technically immutable, signed or remotely protected.

When upgrading a closed legacy Program, require its actual closure date in canonical `YYYY-MM-DD` form from repository evidence. Never substitute the upgrade date.

## Route to focused instructions

- For `inspect`, `bootstrap` or `adopt`, read [bootstrap.md](references/bootstrap.md).
- For `check`, `repair`, `upgrade`, Program lifecycle, request intake or plan lifecycle, read [maintenance.md](references/maintenance.md).
- For findings or failure knowledge, read [knowledge.md](references/knowledge.md).
- `overview` and `help` are fully specified above and do not require loading every reference.

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
- Follow the connected repository WORKFLOW for immediate durable user-request intake, canonical JSON, validation after each intake or cancellation, contract revisions and compaction recovery. Authorized clarifications require no separate permission to record or integrate.
- Before final checkpoints, readiness claims or publication recommendations for a named durable plan, run plan status --require-ready. Lead with NOT_READY when required acceptance is open; never present source checks or a ZIP as a verified release candidate. Bounded plan-free engineering still requires finding/checkpoint writeback and checkpoint --check.
- When Codex Review is configured or required, preserve a separate exact-final-commit review gate. Wait for completed code/security reviews and disposition of every remark before merge or publication; green CI is separate. A new source commit invalidates the old review evidence. A blocked delivery-readiness assessment still needs the connected WORKFLOW's checkpoint writeback when local record writes are allowed; forbidding external actions alone does not forbid that save. Explicit read-only or no-file-change requests remain read-only. Follow the repository review guard.
- Record only verified repository facts. Mark unresolved claims as unverified.
- Keep project incidents separate from portable lessons. Approve only confirmed, sanitized mechanisms and never require a Project OS release to transfer user knowledge.
- Do not imply a daemon, watcher, hook, MCP server, hidden database, automatic upload or automatic cross-repository synchronization.
- Project OS does not grant authority to install dependencies, delete files, commit, push, deploy, publish or contact external systems.

The helper entrypoint is `scripts/project_os.py` relative to the installed skill directory. Resolve that path from the installed skill, not from the target repository, except when explicitly testing the candidate helper while developing Project OS itself.
