# Maintain Project OS

Use this workflow for checks, repairs, upgrades, Program lifecycle and durable plan lifecycle. Ordinary bounded code changes follow repository instructions and do not need `$project-os`.

Resolve `scripts/project_os.py` relative to the installed skill. The exception is explicit candidate runtime testing while developing Project OS itself.

## Check

Run this in Terminal:

~~~shell
python3 /absolute/path/to/project-os/scripts/project_os.py check --target /path/to/repository
~~~

The command is read-only. Report each concrete error and the owning record. Do not turn a structural pass into a claim about application, artifact, deployment, production, manual or physical behavior.

## Repair

Inspect the repository and reproduce the checker error first. Preview the smallest change to its actual owner. Do not create duplicate state to silence an invariant. Preserve unrelated work, apply only a clean preview and run the checker again.

## Plans in Standard or Program

A plan owns one observable outcome that must survive checkpoints. It is independent of whether a Program is active.

Before opening, checkpointing, resuming or closing a plan:

1. Read `.agents/CONTEXT.md`, `.agents/STATE.md`, the plan index, the active plan if present and only relevant packs and knowledge.
2. Compare the checkpoint with Git HEAD, worktree status and current files.
3. Revalidate evidence made stale by later code or external state.
4. Preview the intended record transition.

Keep exactly one active plan while execution is running. A plan file is not a transcript.

At checkpoint, update only supported acceptance items, rewrite `STATE.md` as a compact handoff and leave one exact next action.

Mark a plan `done` only with its required evidence. Blocking preserves the exact unmet condition and resume point. Supersession names the replacement or next decision and does not rewrite the old plan.

`plan block` changes the active plan to `blocked`, execution to `idle` and the optional `active_plan` to null. Record the blocker and the first action available after it clears in the plan and STATE.

For `plan resume`, continue the active plan when one exists. To reactivate a blocked plan, accept `plan resume: <plan-id>` or select the only blocked plan when execution is idle. Ask for the ID when multiple blocked plans could match. Do not displace another active plan. Verify the recorded blocker is resolved from current evidence; if it is still unresolved, leave the plan blocked and report the exact missing condition. Preview `blocked` -> `active`, `idle` -> `running`, the optional `active_plan` pointer and the next action in STATE, then apply that transition. Preserve completed evidence and leave acceptance items incomplete until their checks actually pass. With `do not continue implementation`, stop after the authorized record transition; with `do not change files`, keep the entire assessment read-only.

Run the checker after every plan transition.

## Start a Program

Program is temporary and starts only from an explicit `program start: <initiative>` request. Do not start it because work is long or because several tasks exist.

Build a definition from verified repository authority. It must contain:

- non-empty `initiative` and observable `outcome`;
- non-empty `authority`;
- at least two phases, each with a name, outcome and non-empty exit conditions;
- non-empty `evidence_requirements`;
- non-empty `cost_boundary`;
- non-empty `exclusions`;
- non-empty overall `exit_conditions`.

If any material value cannot be verified or derived, ask for that decision and do not write.

Store the complete definition in a temporary JSON file outside the repository, then run:

~~~shell
python3 /absolute/path/to/project-os/scripts/project_os.py program start --target /path/to/repository --definition /path/to/program-definition.json --dry-run
~~~

Review the complete preview, then apply the identical command without `--dry-run`. The helper requires Standard, generates the Program ID, creates `.agents/PROGRAM.md`, records the active Program in `SYSTEM.json` and runs through the checker gate. Remove the temporary definition after use when the environment allows it.

Starting a Program does not open a plan or change application code.

## Program status

Run this in Terminal:

~~~shell
python3 /absolute/path/to/project-os/scripts/project_os.py program status --target /path/to/repository
~~~

This is read-only. Reconcile its output with current plans and evidence before reporting phase or exit status.

## Close a Program

Require no active plan. For `completed`, verify the overall exit conditions and required evidence. For `stopped`, require a reason and preserve unresolved obligations.

Preview one closure:

~~~shell
python3 /absolute/path/to/project-os/scripts/project_os.py program close --target /path/to/repository --disposition completed --dry-run
~~~

Or preview a stopped closure:

~~~shell
python3 /absolute/path/to/project-os/scripts/project_os.py program close --target /path/to/repository --disposition stopped --reason "Initiative stopped before completion" --dry-run
~~~

Apply only the same reviewed command without `--dry-run`. Closure copies the exact contract bytes to `.agents/history/programs/<program-id>/PROGRAM.md`, records disposition and SHA-256 in `.agents/history/index.json`, removes the active contract and returns to Standard. Conflicts abort before writes and caught write or validation failures roll back completed changes.

The checker verifies indexed paths and hashes. Describe this as tamper-evident history, not immutable storage, signing or prevention of a deliberate archive-plus-index rewrite.

## Upgrade

Use one helper command for every connected repository:

~~~shell
python3 /absolute/path/to/project-os/scripts/project_os.py upgrade --target /path/to/repository --dry-run
~~~

Inspect release, schema, managed baselines and Program state first. Review the complete file preview. Abort on managed conflict, unsafe ownership or stale state. Apply the same command without `--dry-run`; a successful apply ends with the checker.

If the repository release is newer than the helper, stop and use a matching or newer helper. Upgrade never downgrades repository state. Do not lower version fields manually to bypass this check.

Upgrade preserves `AGENTS.md`, context, state, plans, findings, evidence, project knowledge and application code except for an explicitly required lifecycle migration.

A schema 2 repository with a legacy Program contract needs explicit classification:

- Active: add `--legacy-program-state active`. Preserve the editable contract, enter Program, record its legacy origin and migration date and leave the unprovable start date null.
- Closed: add `--legacy-program-state closed --disposition completed --closed-on <YYYY-MM-DD>` or `--legacy-program-state closed --disposition stopped --closed-on <YYYY-MM-DD> --reason <reason>`. Archive the exact bytes and enter Standard.

Never infer this classification from the file alone. The closed date is the actual historical closure date, not the upgrade date. Derive it only from repository evidence. If the state or date cannot be established, stop for the user's decision.

`--closed-on` is valid only for a closed schema 2 migration. Do not pass it for an active legacy Program or a current-schema upgrade.

Do not edit version or schema fields manually. Do not reduce upgrade to `sync-knowledge`; schema, lifecycle, managed content and metadata are one transaction in this release.

## Self-hosting

When developing Project OS:

1. Let the installed stable skill govern the workflow and interpret chat requests.
2. Develop and test the candidate helper from the source checkout explicitly.
3. Do not replace the installed skill with a mutable candidate checkout.
4. After release, install the versioned tag and start a fresh task before installed-copy validation.

This separates the rules governing the work from the code currently being changed.
