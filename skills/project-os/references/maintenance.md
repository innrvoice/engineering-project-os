# Maintain Project OS

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

Run:

```bash
python3 scripts/project_os.py check --target <repository>
```

Fix the source of truth named by each error. Do not make duplicate status tables to silence a check.
Preserve unrelated work and ask before destructive cleanup.
