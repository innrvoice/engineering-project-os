# Usage

Project OS uses the same workflow on two surfaces, but the repository arrives differently.

| Surface | Select Project OS | Repository context |
| --- | --- | --- |
| ChatGPT | `@Engineering Project OS` | Describe the project or attach the files needed for the requested workflow |
| Codex | `$project-os` | Open the local repository as the task workspace |

Installing the plugin does not attach a repository. In ChatGPT, setup advice and a starter package can begin from a project description. An existing setup review needs its actual files. Project OS asks for missing evidence and never inspects an empty host workspace as a fallback. Codex reads only the selected workspace and applicable repository instructions.

The detailed short request menu below uses Codex syntax. In ChatGPT, select `@Engineering Project OS` and write the same intent in ordinary language.

## Common requests on both surfaces

| Intent | ChatGPT | Codex |
| --- | --- | --- |
| Understand Project OS | `@Engineering Project OS What does Project OS do, how does it work and when should I use it?` | `$project-os overview` |
| Create starter package | `@Engineering Project OS Create a safe Project OS starter package for my project.` | `$project-os bootstrap` |
| Review existing setup | Attach `AGENTS.md` and `.agents/`, then send `@Engineering Project OS Review my existing Project OS setup and tell me what to fix.` | `$project-os check` |

ChatGPT returns analysis or changed file artifacts in the chat. Apply those artifacts to the real repository deliberately, then validate the resulting repository. Codex can preview and apply authorized changes directly in its selected workspace.

Most engineering work in a connected repository does not need `$project-os`.

Use ordinary chat for the product and its code. Invoke `$project-os` when the object you want to create, inspect or change is the repository's Project OS control plane.

## Understand Project OS before connecting a repository

**Type this in ChatGPT:**

~~~text
@Engineering Project OS What does Project OS do, how does it work and when should I use it?
~~~

**Type this in Codex chat:**

~~~text
$project-os overview
~~~

- Result: Project OS explains the developer audience, practical benefits, repository-local state, reusable failure knowledge and the next suitable workflow.
- Files: none change and no repository input is required.
- Proof: the response distinguishes project knowledge from reviewed shared knowledge and does not claim automatic cross-project learning.
- Skip it when: you already know whether you need a starter package, an existing-setup review or another Project OS operation.

## Ask for the Codex menu

**Type this in Codex chat:**

~~~text
$project-os help
~~~

- Result: Codex returns a concise, read-only menu of every supported short request, its purpose, required argument and one or two examples. It also separates Codex chat requests from Python helper commands that belong in Terminal.
- Files: none change.
- Proof: the response is explanatory only and contains no attempted mutation.
- Skip it when: you already know the request you need.

Help itself never inspects in order to mutate, never runs an applying helper command and never changes repository files.

## Short request menu

These are recommended natural-language shortcuts. They are not a strict command grammar.

| Short request | Purpose | Required text |
| --- | --- | --- |
| `$project-os overview` | Explain Project OS, its benefits and useful next steps | None |
| `$project-os help` | Show the read-only menu | None |
| `$project-os inspect` | Inspect repository and recommend setup or maintenance | None |
| `$project-os bootstrap` | Create a Standard control plane | None |
| `$project-os adopt` | Attach to compatible existing records | None |
| `$project-os check` | Validate Project OS without writes | None |
| `$project-os repair` | Repair verified Project OS errors | Error or scope when it is not already clear |
| `$project-os upgrade` | Upgrade to the installed release | None |
| `$project-os program start: <initiative>` | Start one temporary multi-phase Program | Initiative |
| `$project-os program status` | Report active Program state without writes | None |
| `$project-os program close completed` | Close a Program whose exit evidence is complete | None |
| `$project-os program close stopped: <reason>` | Stop and archive an incomplete Program | Reason |
| `$project-os plan open: <outcome>` | Open one resumable outcome plan | Outcome |
| `$project-os plan checkpoint` | Reconcile and save the active plan checkpoint | None |
| `$project-os plan resume[: <plan-id>]` | Continue active work or reactivate a resolved blocked plan | Plan ID when selection is ambiguous |
| `$project-os plan complete` | Complete the active plan when evidence permits | None |
| `$project-os plan block: <reason>` | Preserve a blocked plan and resume condition | Reason |
| `$project-os plan supersede: <reason>` | Retire a replaced plan | Reason |
| `$project-os finding add: <observation>` | Record a concrete finding without inventing cause | Observation |
| `$project-os knowledge capture: <finding-id>` | Convert a confirmed finding into project knowledge | Finding ID |
| `$project-os knowledge propose-shared: <lesson-id>` | Draft a sanitized portable lesson for review | Project lesson ID |

Text after a shortcut may add boundaries in any language.

**Type this in Codex chat:**

~~~text
$project-os check. Focus on archive hashes and do not change files.
~~~

That is still a check. If the intent is ambiguous, Codex shows relevant help or asks one focused question before any write. If the request is unrelated to Project OS, Codex treats it as ordinary work and does not manufacture control-plane records.

## Do ordinary work

**Type this in Codex chat:**

~~~text
Find why the orders endpoint repeats the final item on two cursor pages. Fix the verified cause without changing the response schema and run the focused tests.
~~~

- Result: Codex follows the repository's `AGENTS.md`, reads only relevant records and works on the application normally.
- Files: code, tests and only durable records whose truth changed may be updated.
- Proof: review the diff, focused checks and every stated unverified boundary.
- Skip it when: the request is specifically about Project OS setup or state.

A small task does not need a plan. A long task does not automatically need a Program.

## Inspect, bootstrap, adopt, check and repair

Use the shortest clear request. Add constraints only when they matter.

**Type this in Codex chat:**

~~~text
$project-os inspect
~~~

This is read-only and recommends a repository connection or maintenance path.

**Type this in Codex chat:**

~~~text
$project-os bootstrap
~~~

This creates Standard after inspection and a clean initialization dry run. It never creates `PROGRAM.md`.

**Type this in Codex chat:**

~~~text
$project-os adopt
~~~

This maps compatible existing owners after a clean adoption dry run. It never overwrites those owners.

**Type this in Codex chat:**

~~~text
$project-os check
~~~

This is always read-only.

**Type this in Codex chat:**

~~~text
$project-os repair: fix only the active_plan mismatch reported by the last check
~~~

A repair inspects current state, previews the exact Project OS changes, applies only when ownership is clear and finishes with the checker. It does not repair application code under the same request.

See [Setup](SETUP.md) for the three repository connection shapes.

## Open a durable plan

Use one plan when an observable outcome must survive several checkpoints or has evidence gates that cannot safely be reconstructed from one conversation.

**Type this in Codex chat:**

~~~text
$project-os plan open: make password reset idempotent across API retries and worker redelivery
~~~

- Result: Codex inspects current state, drafts one outcome-focused plan, previews the state transition, creates it only when its boundaries and acceptance evidence are clear and runs the checker.
- Files: `.agents/plans/index.json`, one plan file and `.agents/STATE.md` may change.
- Proof: exactly one plan is active, execution state is `running`, acceptance items are observable and the checker passes.
- Skip it when: the task can be completed and verified in the current working session.

Extra text can preserve a specific interface or prevent implementation in the same turn.

**Type this in Codex chat:**

~~~text
$project-os plan open: make password reset idempotent. Preserve the public API and only create the plan; do not implement it yet.
~~~

A plan is not a transcript. It owns one outcome, boundaries, interfaces, work, evidence and unresolved obligations.

## Checkpoint, resume and complete a plan

**Type this in Codex chat:**

~~~text
$project-os plan checkpoint
~~~

- Result: Codex reconciles the active plan with Git state and current evidence, updates only supported acceptance items and leaves one exact next action.
- Files: the active plan and `.agents/STATE.md` may change. Other records change only when their owned truth changed.
- Proof: completed items cite evidence, the next action is executable and the checker passes.
- Skip it when: no plan is active or the plan can be completed immediately.

**Type this in Codex chat:**

~~~text
$project-os plan resume
~~~

- Result: Codex compares the checkpoint with current HEAD, worktree state and relevant files before continuing the exact next action. When idle, it can reactivate a selected blocked plan after verifying that the recorded blocker is resolved.
- Files: application files named by the plan and relevant Project OS records may change within the authority of the request.
- Proof: Codex reports the reconciled baseline, work performed, verification and next action.
- Skip it when: there is no active or blocked plan. Add `do not change files` for a read-only assessment. `Do not continue implementation` allows the requested record transition but stops before the next implementation step.

**Type this in Codex chat:**

~~~text
$project-os plan complete
~~~

- Result: Codex marks the plan `done` only when every acceptance item has its required evidence, then returns execution state to `idle`.
- Files: the plan, plan index and `.agents/STATE.md` change. Linked evidence or findings change only when supported by new proof.
- Proof: no plan remains active, evidence links resolve and the checker passes.
- Skip it when: any required gate is missing.

A source edit does not prove deployment. A unit test does not prove a hosted, artifact, production, manual or physical gate.

### Block or supersede

**Type this in Codex chat:**

~~~text
$project-os plan block: staging credentials are unavailable
~~~

This preserves completed evidence, the exact unmet condition and the first action available after the blocker clears. The plan becomes `blocked`, execution becomes `idle` and the optional `active_plan` pointer becomes null.

After the condition clears, type `$project-os plan resume: 001` with the intended plan ID. Codex verifies the condition, requires no other active plan, previews the transition back to `active` and `running`, updates STATE and runs the checker. If multiple blocked plans exist, bare `plan resume` requires a selection. An unresolved blocker leaves the plan blocked.

**Type this in Codex chat:**

~~~text
$project-os plan supersede: the repository now uses the replacement payments API
~~~

This preserves the old plan as history and identifies the replacement or next decision. Postponement alone is not supersession.

## Start a Program

Use a Program only when several plans or outcomes need one temporary multi-phase contract.

**Type this in Codex chat:**

~~~text
$project-os program start: migrate authentication across the API, workers, web and mobile without downtime
~~~

- Result: Codex inspects the repository, derives only verified contract fields and asks for any material missing decision. Once complete, it previews and starts the Program, then runs the checker.
- Files: `.agents/PROGRAM.md` and Program metadata in `.agents/SYSTEM.json` may change. Starting the first Program does not create an empty history archive, a plan or application code.
- Proof: the contract has explicit authority, at least two phases with exit conditions, evidence requirements, cost boundaries, exclusions and overall exit conditions; `SYSTEM.mode` is `program`; the checker passes.
- Skip it when: one plan can own the work or phases do not share a meaningful governing contract.

A concise request is enough to begin the workflow. It is not permission to invent missing authority, budget, evidence or exclusions.

### Program status

**Type this in Codex chat:**

~~~text
$project-os program status
~~~

- Result: Codex reports the active Program, current phase evidence, plan state and unresolved exit conditions.
- Files: none change.
- Proof: the report is derived from current repository records and Git state.
- Skip it when: no Program is active.

### Close a completed Program

**Type this in Codex chat:**

~~~text
$project-os program close completed
~~~

- Result: Codex verifies exit evidence and the absence of an active plan, previews closure, archives the exact contract with its SHA-256 digest and returns the repository to Standard.
- Files: active `PROGRAM.md` is removed, `.agents/SYSTEM.json` changes and a Program snapshot plus `.agents/history/index.json` are created or updated. The first close also creates `.agents/history/README.md`.
- Proof: `SYSTEM.mode` is `standard`, no active Program remains, the archived digest verifies and the checker passes.
- Skip it when: any exit condition lacks evidence or a plan remains active.

The helper can enforce the structural lifecycle and the absence of an active plan. It cannot decide whether repository or external evidence truly proves the Program outcome; Codex and the user make that judgment before the close command is applied.

### Stop a Program

**Type this in Codex chat:**

~~~text
$project-os program close stopped: the migration was replaced by the vendor-managed rollout
~~~

- Result: Codex preserves the stated reason and unresolved obligations, archives the exact contract with disposition `stopped` and returns to Standard.
- Files and proof: the same lifecycle records change and the same archive hash is checked as for a completed close.
- Skip it when: the Program met its exit contract; use `completed` instead.

The archive is tamper-evident, not technically immutable. The checker catches uncoordinated archive changes but cannot prevent a deliberate rewrite of both content and index. Treat an archive hash mismatch as an integrity event. Determine which content is authoritative before repairing anything; never silence it by automatically recording the changed bytes.

## Record a finding and failure knowledge

**Type this in Codex chat:**

~~~text
$project-os finding add: password reset produced two emails for one accepted request
~~~

- Result: Codex records the observation, evidence, impact and decisive next check without claiming an unverified root cause.
- Files: `.agents/findings/findings.json` and sanitized linked evidence may change.
- Proof: the finding has a stable ID and distinguishes observation from inference.
- Skip it when: the note is temporary debugging output or already has an owner.

After the mechanism is confirmed:

**Type this in Codex chat:**

~~~text
$project-os knowledge capture: FIND-012
~~~

- Result: Codex creates a project-specific lesson with applicability, trigger, mechanism, prevention, decisive verification and boundaries.
- Files: `.agents/knowledge/project/failures.json` may change.
- Proof: the lesson links decisive evidence and contains no unverified mechanism.
- Skip it when: the finding is still a hypothesis.

Review portability separately.

**Type this in Codex chat:**

~~~text
$project-os knowledge propose-shared: FAIL-PROJECT-012
~~~

- Result: Codex proposes a sanitized portable entry or explains why the lesson must remain local.
- Files: none change during the proposal.
- Proof: project names, credentials, personal data, private paths, private URLs and product history are absent while the mechanism and limits remain intact.
- Skip it when: the lesson depends on a repository-specific contract.

Shared knowledge never travels to another repository automatically. The complete reuse path is:

1. Record the observed failure as a finding with evidence and a decisive next check.
2. Confirm the mechanism, then capture a project lesson.
3. Propose a sanitized portable lesson without writing or publishing it.
4. Review the proposal for privacy, portability, accuracy and useful scope boundaries.
5. Include an approved lesson in a reviewed Project OS release.
6. Install that release and run an explicit upgrade in another connected repository or synchronize managed knowledge when the repository already matches the release.

The receiving repository gets the reusable mechanism, prevention, verification and boundaries. It does not get the source project's name, credentials, private paths, private URLs, deployment identifiers or copied history.

## Upgrade

Update the Directory plugin or standalone Codex skill, start a fresh chat or task and provide the current repository context again.

**Type this in Codex chat:**

~~~text
$project-os upgrade
~~~

- Result: Codex inspects release, schema and Program state, previews every managed file change, applies only a conflict-free result with caught-failure rollback and runs the checker.
- Files: version and schema metadata, managed guidance, managed shared knowledge and an explicitly required lifecycle migration may change. Project-owned state and application code remain intact.
- Proof: the checker passes at release 2.0.5 and a repeated dry run reports no pending changes.
- Skip it when: the installed checker already passes and the repository is current.

A legacy Program whose state cannot be proved is a decision boundary, not something Codex guesses. For a closed legacy Program, Codex also requires the actual closure date in `YYYY-MM-DD` form and derives it only from repository evidence.

## Terminal commands are different

The short requests above belong in Codex chat. The deterministic helper belongs in Terminal.

**Run this in Terminal:**

~~~bash
python3 /absolute/path/to/project-os/scripts/project_os.py check --target /path/to/repository
~~~

- Result: Python runs exactly the helper check. It does not invoke the Codex skill or interpret natural language.
- Files: none change.
- Proof: the process exits zero and prints `Project OS check: PASS`.
- Skip it when: you want Codex to inspect context, choose a workflow or explain the result.

See [Reference](REFERENCE.md) for every helper command and flag.
