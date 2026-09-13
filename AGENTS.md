# Project working agreement

## Authority and entry route

- Current user instructions take precedence over this repository workflow.
- `.agents/CONTEXT.md` records durable current facts, authority, architecture, and verified commands.
- `.agents/STATE.md` owns the current checkpoint and exact next action.
- `.agents/plans/index.json` owns execution state and plan statuses.
- `.agents/findings/findings.json` owns concrete project findings.
- `.agents/knowledge/` contains confirmed lessons, not product authority.
- Chat history, generated summaries, and archived evidence are context, not current verification.

Before non-trivial work, inspect Git HEAD and status, then read CONTEXT, STATE, the active plan if one
exists, applicable capability guidance, relevant knowledge entries, and the code and callers being changed.
Do not load complete history or unrelated evidence at startup.

Capability guidance lives under `.agents/packs/`. Read only selected packs and overlays relevant to
the requested change. Detected languages and frameworks are evidence, not behavioral profiles or
permission to infer commands.

Project OS is already connected to this repository. Ordinary engineering work follows this file and
the routed records without requiring `$project-os`. That prefix explicitly invokes the installed
Project OS skill for one message and is appropriate when the user wants to inspect, check, repair, or
upgrade the control plane, manage durable plans or checkpoints, or curate findings and knowledge. It is
not a shell command or a persistent mode.

## Project authority and self-hosting

- `VERSION` and `SCHEMA_VERSION` in `skills/project-os/scripts/project_os.py` own the candidate release
  and repository format. Package manifests, generated metadata, documentation, fixtures and bundled
  knowledge must remain in lockstep with them.
- `skills/project-os/SKILL.md` and its focused references own the skill workflow. `README.md` and
  `docs/` own the public explanation. Runtime behavior wins when prose and executable tests disagree;
  repair both in the same change.
- `tests/test_project_os.py` and `.github/workflows/ci.yml` own the deterministic release checks.
- The installed stable skill governs Project OS work. Candidate behavior is exercised with
  `skills/project-os/scripts/project_os.py` from this checkout. Never symlink or copy an unreleased
  checkout over the installed stable skill.
- Standalone installation from a versioned GitHub tag is the current public route. Repository plugin
  manifests are packaging surfaces, not evidence of public Codex marketplace availability.
- A commit, push, tag, GitHub Release, skill replacement or marketplace submission is a separate
  publication action and requires explicit owner authorization.

## Working method

1. Establish the concrete outcome, affected owners and callers, and the cheapest decisive check.
2. Distinguish current behavior, required behavior, stale documentation, and unresolved choices.
3. Make the smallest coherent change and preserve unrelated work.
4. Reproduce a defect before fixing when practical. Verify the observable outcome, not only an internal
   call or mock.
5. Update only the records whose durable truth changed, then leave an exact resumable checkpoint.

Ask a targeted question only when missing information would materially change behavior, security,
architecture, compatibility, data ownership, or public outcomes. Do not invent project commands or
requirements.

## Plans and state

- Simple bounded tasks do not require a plan.
- Multi-session work uses one active plan for one observable outcome.
- While `execution_state` is `running`, exactly one plan is `active`. If the optional `active_plan`
  field exists, it matches that record.
- `STATE` is a compact handoff, not a diary. Durable facts belong in `CONTEXT`; detailed results belong
  in linked evidence.
- A plan is not `done` until its stated acceptance evidence exists. Preserve missing manual, hosted,
  artifact, production, or physical checks as unverified.

## Findings and knowledge

- Keep candidate and project-specific incidents in the findings register.
- Add knowledge only after confirming a failure mechanism.
- Shared lessons must be sanitized, conditional on applicability, and explicit about version or
  platform boundaries.
- Never treat copied historical evidence as current proof.

## Scope and safety

- Do not refactor unrelated code or introduce speculative abstractions.
- Do not install dependencies, delete files, change branches, commit, push, deploy, or run destructive
  or expensive checks without the authorization required by the current user and repository.
- Keep credentials, tokens, private data, signed URLs, and production identifiers out of tracked agent
  records.
- Keep `.agents` material outside application runtime and distributed artifacts.

## Verification

Use the narrowest checks that provide meaningful confidence. Commands must come from verified project
configuration recorded in CONTEXT or current repository evidence. Keep static, unit, local integration,
hosted, artifact, production, owner-reported, and physical evidence distinct.

## Communication

Lead with the outcome. State what changed, what was verified, what remains unverified, and any exact
blocker. Label inference and uncertainty explicitly.
