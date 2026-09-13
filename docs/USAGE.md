# Usage

Most engineering work in a connected repository does not need `$project-os`.

Use ordinary chat for the product and its code. Invoke `$project-os` when the thing you want to
create, check or change is the repository's Project OS control plane.

| Your intent | How to ask |
| --- | --- |
| Explain, debug, implement, test or review application work | Write a normal Codex message |
| Bootstrap, adopt, check, repair or upgrade Project OS | Start the message with `$project-os` |
| Make a long outcome resumable across tasks | Ask `$project-os` to open one plan |
| Record a checkpoint, finding or confirmed lesson | Use the matching `$project-os` recipe below |
| Run a deterministic operation manually or in CI | Run the Python helper in Terminal |

`$project-os` applies to the current message. It is not a mode you leave running.

## Do ordinary work

**Type this in Codex chat:**

~~~text
Find why the orders endpoint returns the same final item on two cursor pages. Fix the verified cause
without changing the response schema and run the focused tests.
~~~

- Result: Codex follows the repository's `AGENTS.md`, reads the relevant current records and works on
  the application normally.
- Files: code, tests and only those durable records whose truth changed may be updated.
- Proof: review the diff, the focused test result and every stated unverified boundary.
- Skip it when: the request is specifically about Project OS setup or state.

For a small task, stop there. Do not open a plan only to create paperwork.

## Open a durable plan

Use a plan when one observable outcome must survive several checkpoints, has several evidence gates or
cannot safely be reconstructed from one chat.

**Type this in Codex chat:**

~~~text
$project-os Open one plan to make password reset requests idempotent across API retries and worker
redelivery. Inspect current Git state and relevant callers first. Record the interfaces, compatibility
boundary, acceptance evidence and exact first action. Do not implement the application change yet.
~~~

- Result: Codex creates one outcome-focused plan, marks it active and rewrites the current checkpoint.
- Files: `.agents/plans/index.json`, one `.agents/plans/NNN-*.md` file and `.agents/STATE.md` may
  change.
- Proof: exactly one plan is active, execution state is `running`, acceptance items are observable and
  the checker passes.
- Skip it when: the task is bounded enough to complete and verify in the current working session.

A plan is not a transcript. It records the outcome, boundaries, interfaces, work, acceptance evidence
and unresolved obligations.

## Checkpoint active work

Checkpoint when another task must be able to continue without the current conversation.

**Type this in Codex chat:**

~~~text
$project-os Checkpoint the active plan. Reconcile it with the current Git diff and verification
results, update only acceptance items whose evidence exists and leave one exact next action. Keep
durable facts in CONTEXT and do not append a work diary.
~~~

- Result: Codex reconciles the active plan with current repository evidence and leaves a compact
  resumable state.
- Files: the active plan and `.agents/STATE.md` may change. Findings, evidence or `CONTEXT.md` change
  only when their owned truth changed.
- Proof: the next action is executable, completed items cite evidence and the checker passes.
- Skip it when: the task is complete and can be closed immediately or no durable plan is active.

## Resume from repository state

Start a new Codex task in the same repository, then ask Project OS to resume the active plan.

**Type this in Codex chat:**

~~~text
$project-os Resume the active plan from repository state. Compare the checkpoint with current HEAD,
Git status and relevant files, revalidate anything made stale by later changes and continue the exact
next action.
~~~

- Result: Codex treats current repository state as authority, checks whether the checkpoint is stale
  and continues the plan.
- Files: application files named by the plan and relevant Project OS records may change within the
  authority of the request.
- Proof: Codex states the reconciled baseline, work performed, verification and new next action.
- Skip it when: there is no active plan or you only need a read-only status summary.

For a read-only resume assessment, add `Do not change files or continue implementation.`

## Complete a plan

Completion requires the evidence named by the plan. A source change does not prove a deployment and a
green test does not prove a manual, hosted, artifact or physical gate.

**Type this in Codex chat:**

~~~text
$project-os Complete the active plan only if every acceptance item has its required evidence.
Reconcile the plan, evidence links and findings, set execution to idle and leave a compact final
checkpoint. Preserve every missing evidence class as an explicit open obligation.
~~~

- Result: Codex marks the plan `done` only when its acceptance contract is satisfied.
- Files: the active plan, plan index and `.agents/STATE.md` change. Linked findings or evidence may
  change when supported by new proof.
- Proof: no plan remains active, execution state is `idle`, evidence links resolve and the checker
  passes.
- Skip it when: any required gate is still missing. Block the plan instead of declaring it done.

## Block a plan

Blocking preserves work. It does not erase unfinished obligations.

**Type this in Codex chat:**

~~~text
$project-os Block the active plan on the missing staging credential. Preserve completed evidence,
record the exact unmet condition and the first action available after access is restored, then run the
checker.
~~~

- Result: Codex changes the plan status to `blocked` and records a precise blocker and resume point.
- Files: the plan, plan index and `.agents/STATE.md` change.
- Proof: no plan is marked active, the blocker is testable and completed work remains recorded.
- Skip it when: meaningful in-scope work can still continue without resolving the stated condition.

## Supersede a plan

Use supersession when the intended outcome or route has been replaced, not merely postponed.

**Type this in Codex chat:**

~~~text
$project-os Supersede the active plan because the repository now uses the replacement payments API.
Preserve unfinished obligations, identify the replacement plan or next decision and keep the old plan
as history rather than rewriting it.
~~~

- Result: Codex marks the old plan `superseded` and records why it no longer governs the work.
- Files: the old plan, plan index and `.agents/STATE.md` change. A replacement plan is created only if
  the prompt or current decision requires one.
- Proof: the superseded plan names its replacement or next decision and the checker passes.
- Skip it when: the same plan remains valid and is only waiting on a blocker.

## Record a finding

Findings are concrete repository problems, candidates and accepted risks. Hypotheses stay findings
until evidence confirms a mechanism.

**Type this in Codex chat:**

~~~text
$project-os Record the observed duplicate password-reset email as a project finding. Use the current
logs and reproduction as evidence, distinguish observation from inference, assign a stable ID and
state the decisive next check. Do not claim a root cause that is not verified.
~~~

- Result: Codex creates or updates one finding with status, impact, evidence and a required check.
- Files: `.agents/findings/findings.json` and sanitized linked evidence may change. The active plan
  changes only when the finding affects it.
- Proof: the finding has a stable ID, evidence references and a check that can confirm or reject it.
- Skip it when: the note is merely temporary debugging output or the issue is already represented by
  an existing finding.

## Turn a confirmed failure into knowledge

Project knowledge may retain repository, dependency and environment context. It still requires a
confirmed mechanism.

**Type this in Codex chat:**

~~~text
$project-os Convert finding FIND-012 into a confirmed project failure lesson. Preserve the mechanism,
trigger, prevention, decisive verification and version boundaries. Link the evidence and do not add
unverified conclusions.
~~~

- Result: Codex converts confirmed evidence into a reusable lesson for this repository.
- Files: `.agents/knowledge/project/failures.json` changes. The source finding may be linked or updated.
- Proof: the lesson states when it applies, how the failure happens and which check decisively catches
  it.
- Skip it when: the mechanism remains a hypothesis or the finding contains no decisive evidence.

Review portability separately before adding anything to shared knowledge.

**Type this in Codex chat:**

~~~text
$project-os Review the confirmed project lesson for shared use. If the mechanism is genuinely
portable, propose a sanitized shared entry that removes project names, private paths, credentials,
user data, private URLs and product history. Do not write or publish it until I review the proposal.
~~~

- Result: Codex proposes a mechanism-focused shared lesson or explains why it should remain local.
- Files: none should change during the proposal.
- Proof: the proposed lesson retains applicability, trigger, prevention, decisive verification and
  limits without retaining private project context.
- Skip it when: the lesson depends on this repository's product contract or environment.

After review, ask `$project-os` to add the exact approved entry. Shared knowledge does not travel to
other repositories automatically. To distribute it, add the sanitized lesson to a reviewed Project OS
release, then run the normal repository upgrade workflow where it applies.

## Check consistency

Run the checker after structural, mapping, plan-registry, finding-registry, managed-guidance or
knowledge changes.

**Type this in Codex chat:**

~~~text
$project-os Check this repository's Project OS state and report errors without changing files.
~~~

- Result: Codex runs the deterministic checker against the current control plane.
- Files: none should change.
- Proof: the helper prints `Project OS check: PASS` or returns concrete errors to repair.
- Skip it when: do not skip it after a Project OS state change. It is unnecessary after ordinary code
  work that did not alter Project OS records.

## Repair inconsistent state

Check first. Repair only the named source of truth instead of creating duplicate state to silence an
error.

**Type this in Codex chat:**

~~~text
$project-os Repair only the Project OS consistency errors from the last check. Inspect current Git
state, preserve project-owned content and unrelated work, preview every managed-file change and run
the checker again after applying the reviewed repair.
~~~

- Result: Codex fixes the smallest verified control-plane inconsistency and rechecks it.
- Files: only records or managed files named by the errors may change.
- Proof: compare the preview with the diff and require a final checker pass.
- Skip it when: no check has identified an error or the proposed repair would erase project-owned
  truth.

## Upgrade a connected repository

Update the installed skill first and start a new Codex task. Then use the same prompt in every
connected repository.

**Type this in Codex chat:**

~~~text
$project-os Upgrade this repository to the installed Project OS version. Inspect first,
preview all managed changes, preserve project-owned files, apply the update only when
the preview is clean, then run the Project OS checker.
~~~

- Result: the skill runs `inspect -> sync-knowledge --dry-run -> sync-knowledge -> check`. There is no
  separate Python `upgrade` command.
- Files: release metadata, managed packs or overlays and managed shared knowledge may change.
  Project-owned context, state, plans, findings, evidence and application code are preserved.
- Proof: the checker passes and the repository release matches the installed helper.
- Skip it when: the repository already passes with the installed release.

If the preview reports locally divergent managed guidance or a shared-entry conflict, no update should
be applied. Review ownership and provenance, resolve the conflict deliberately and run the same
workflow again.

## Evidence still has boundaries

Keep these claims separate:

- source inspection;
- static or unit verification;
- local integration behavior;
- a built artifact;
- hosted or deployed behavior;
- production availability;
- owner-reported or manual acceptance;
- physical-device acceptance.

Project OS records the evidence you have. It must not promote one class into another.

For direct helper commands, record schemas, modes, packs and status invariants, see
[Reference](REFERENCE.md). For first-time setup, see [Setup](SETUP.md).
