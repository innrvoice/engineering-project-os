# Maintain Project OS

Use this workflow only when the repository control plane itself needs attention. Ordinary bounded code
changes should follow the repository's `AGENTS.md` and do not require `$project-os` or a plan.

Resolve `scripts/project_os.py` relative to the installed Project OS skill directory in every command
below. The repository does not need to contain a copy of the skill.

## Start or resume work

For non-trivial work that must survive multiple checkpoints:

1. Read `.agents/CONTEXT.md`, `.agents/STATE.md`, `.agents/plans/index.json`, the active plan, and only
   relevant capability and knowledge entries.
2. Compare the checkpoint with Git HEAD, status, and relevant current files.
3. Revalidate affected evidence when code or external state changed.
4. Continue the exact next action. Do not re-plan completed work.

Create a plan just in time for one observable outcome, normally small enough for one to three working
sessions. Set `execution_state` to `running` and keep exactly one plan with status `active`. The
`active_plan` field is optional; when present, it must match that derived plan. Simple bounded tasks
do not require a plan.

Opening a plan records durable execution state; it does not implement the work. Resume by reconciling
the recorded checkpoint with current Git and repository evidence before continuing.

## Checkpoint

At a meaningful checkpoint:

- Update the plan's acceptance items and evidence links.
- Update project findings only when their status or required check changed.
- Rewrite `.agents/STATE.md` so it contains current scope, verified progress, exact next action, and
  blockers. Do not append a diary.
- Keep durable facts in `CONTEXT`, not `STATE`.
- Run the checker.

## Complete, block, or supersede

- `done` requires the plan's stated evidence. A code edit or green unit test does not satisfy a manual,
  hosted, artifact, production, or physical gate.
- `blocked` preserves the exact unmet condition and every unfinished obligation.
- `superseded` identifies the replacement plan and explains why the old route no longer applies.
- When no plan remains active, set `execution_state` to `idle`. If `active_plan` is retained, set it
  to `null`.

## Repair inconsistent state

Run in Terminal with the installed helper path resolved:

```shell
python3 <project-os-skill-directory>/scripts/project_os.py check --target <repository>
```

Fix the source of truth named by each error. Do not make duplicate status tables to silence a check.
Preserve unrelated work and ask before destructive cleanup.

## Upgrade to the installed release

An upgrade is one direct sequence for every connected repository. There is no `upgrade` helper
subcommand and no separate compatibility route by previous release.

1. Inspect Git status, `.agents/SYSTEM.json`, the shared knowledge registry, and managed guidance.
2. Run synchronization as a dry run.
3. Review every proposed update and conflict. Continue only when the preview is clean.
4. Run the same synchronization without `--dry-run`.
5. Run the checker.

Run in Terminal with the installed helper path resolved:

```shell
python3 <project-os-skill-directory>/scripts/project_os.py sync-knowledge --target <repository> --dry-run
python3 <project-os-skill-directory>/scripts/project_os.py sync-knowledge --target <repository>
python3 <project-os-skill-directory>/scripts/project_os.py check --target <repository>
```

Synchronization updates only the Project OS version metadata, selected managed pack and overlay
guidance, and managed shared knowledge. It preserves locally divergent managed content by aborting
before applying any changes. It does not rewrite `AGENTS.md`, `CONTEXT.md`, `STATE.md`, plans, findings,
evidence, project-specific knowledge, or application code.

Do not edit version fields manually to silence the checker. A successful upgrade ends with the
repository version, shared knowledge version, and installed helper release aligned.
