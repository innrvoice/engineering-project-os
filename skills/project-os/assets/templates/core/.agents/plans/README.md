# Implementation plans

`index.json` is the only plan status register. Simple bounded tasks do not need a plan. Create one just
in time when work must survive multiple checkpoints or has several evidence gates.

Status values are `planned`, `active`, `blocked`, `done`, and `superseded`.

While `execution_state` is `running`, exactly one plan must be active. `active_plan` is an optional
derived convenience field; when present, it must match that active record. When no work remains
active, use `idle` and no active record.

## Plan template

```markdown
# Plan NNN: One observable outcome

## Baseline and scope

- Source commit and relevant current state.
- Required outcome, boundaries, explicit exclusions, and applicable knowledge.

## Interfaces and compatibility

- Exact API, schema, configuration, data, or UI changes and affected consumers.
- Rollout, rollback, and backward-compatibility requirements, or `None`.

## Work and acceptance

- [ ] One verifiable task or acceptance criterion per item.

## Verification

- Required automated checks and environment.
- Required hosted, artifact, production, manual, or physical evidence, or why it does not apply.

## Evidence

- Links to sanitized results, limitations, rollback, and outstanding obligations.
```

Keep plans under 200 lines. Preserve unfinished obligations when blocking or superseding a plan. A code
change alone does not satisfy an evidence class named by the plan.
