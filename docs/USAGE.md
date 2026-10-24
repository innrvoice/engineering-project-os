# Usage

After [connecting a repository](SETUP.md#connect-a-repository), ask Codex for the engineering work you want. You do not need to manage findings, checkpoint commands or JSON yourself. Use `$project-os` when the request concerns Project OS itself or explicitly selects its knowledge workflow.

## Work on a normal engineering task

~~~text
Fix the crash when the input is missing and run the focused tests.
~~~

Codex investigates, reproduces the symptom where practical, makes the authorized correction and checks it. Its repository instructions require recording reproduced defects, including one you already named, while keeping hypotheses distinct from confirmed causes.

The saved finding, evidence and current checkpoint describe what changed, what was checked and what remains. A bounded repair can stay plan-free. Passing tests does not replace this handoff.

Decisions are needed for material ambiguity, scope changes or actions requiring permission. The agent must follow the workflow; Project OS does not independently discover every defect.

## Return to work in a new Codex task

Open the repository and ask:

~~~text
Continue the current work from the repository records. Verify what remains before changing code.
~~~

Codex reads the checkpoint, unresolved requests, active plan and acceptance conditions, then checks relevant findings and evidence. It verifies consistency and freshness before relying on the saved next action. This also applies after context compaction.

Codex verifies whether a recorded blocker is resolved and asks for a plan choice only when ambiguous. A new chat needs no resume command when the active plan already identifies the work.

Recovery uses saved files, not the entire previous conversation. Codex must reconcile stale records or explain discrepancies for a read-only request. The checkpoint should leave one concrete next action.

## Add a requirement during work

~~~text
Also handle reconnecting after the app has been offline. Keep the existing retry behavior.
~~~

Codex records a material instruction while handling your message, without waiting for a separate save command. A compatible addition joins the current outcome and its acceptance conditions. An independent outcome becomes a planned slice with a recorded order; only one plan runs at a time.

The saved request retains your wording, interpretation, destination and decision. Inclusion in a plan does not mean implementation; completion requires linked conditions and evidence.

If the addition conflicts with an earlier requirement, Codex preserves the conflict and asks for the needed decision while continuing independent authorized work. If you explicitly cancel or replace a requirement, it records that decision instead of silently dropping the request. These records are part of fresh-task recovery even when no plan is active.

## See what prevents closure

~~~text
$project-os Tell me what is complete, what remains and whether this outcome can be closed.
~~~

Codex checks conditions, evidence and unresolved requirements. Its report states what was implemented, what was verified and where, what prevents closure, which decisions are needed and the next action.

For example, local tests pass but a required remote migration is pending. The outcome remains NOT_READY and the plan stays open. Moving that migration into another slice cannot make the original result complete. A deliberately source-only outcome can close without deployment when that was the agreed scope.

The helper refuses closure for incomplete recorded requirements or proof. It cannot identify omitted prerequisites or validate evidence meaning. Structural PASS and checkpoint CURRENT do not prove production behavior, public availability or physical-device acceptance.

<a id="everyday-findings-and-reusable-lessons"></a>

## Transfer lessons directly to a new repository

Open the destination repository and send:

~~~text
$project-os Reuse the useful failure lessons from /path/to/earlier-repository here. Prepare only lessons that fit this project, keep the source unchanged and show me one batch to review.
~~~

Codex inspects the destination and reads the source without changing it. It prefers approved reusable lessons. If the source has only confirmed findings or project lessons, it prepares sanitized proposals outside both repositories instead of requiring you to organize an intermediate command sequence.

The agent checks mechanisms, prevention, verification and boundaries against the destination. Titles and tags find candidates; they do not establish applicability. It explains exclusions and removes private context.

The plan saves the request, selection and pending approval. Codex presents one batch with proposed additions, their purpose, skips and conflicts. Review it, then reply:

~~~text
Approved - apply the proposed additions.
~~~

You can approve a subset instead. Codex applies only the approved selection, validates the destination, checks repeated-import behavior and verifies source preservation. It records the approval and actual result, then closes the transfer through the guarded completion operation with a current checkpoint.

A connected destination and accessible source usually need this request and batch approval. Missing setup permission, unavailable source files or conflicts may require separate decisions. One batch review does not waive those boundaries. An unconnected destination gets a setup preview before connection.

Knowledge remains under your control. Transfer does not upload lessons to the Project OS author, create a shared database or enable background synchronization. Use [Reference](REFERENCE.md#user-owned-reusable-knowledge) for lifecycle and conflict rules.

## Transfer a portable bundle

When repositories are on different machines, ask Codex to prepare a portable bundle of approved reusable lessons. It previews the export location outside the source repository and produces a checked bundle after the required approval.

Supply the bundle and destination context to Codex or the ChatGPT companion. Ask which lessons fit, review the proposed batch and approve only those additions. The saved result should identify imported and skipped lessons, verification and the next action. A bundle does not carry permission to modify an unrelated project.

## Upgrade Project OS

Update the selected installation using [Setup](SETUP.md#upgrade-to-224), then ask `$project-os upgrade` in each connected repository. Codex identifies the installed helper, previews changes, handles any ownership review and applies only the reviewed operation after authorization.

The upgrade checks and saved checkpoint describe the actual result. Managed files, migration metadata and reviewed historical proof may change; application changes need their own authority. Conflicts stay pending. Do not simulate an upgrade by editing version or schema fields.

<a id="compact-request-table"></a>
<a id="open-and-checkpoint-a-long-task"></a>
<a id="run-a-program-for-a-multi-phase-initiative"></a>
<a id="advanced-record-a-particular-finding-and-prepare-a-lesson"></a>

## When you want more control

Ask for a durable plan when an outcome spans sessions or needs explicit acceptance conditions. Standard mode is complete for normal work. Program is optional coordination for an explicitly authorized multi-phase initiative, not a prerequisite for a long task.

The [request catalog](REFERENCE.md#project-os-requests), [plan rules](REFERENCE.md#contracts-intake-and-guarded-completion), [Program contract](REFERENCE.md#standard-and-program) and [helper syntax](REFERENCE.md#helper-summary) cover direct controls. They are available when useful, not steps you must memorize for every repair or transfer.

## ChatGPT companion boundaries

Select `@Engineering Project OS` for explanations, supplied project files and portable bundles. Reviewing an existing setup requires the relevant files. Changed copies remain chat artifacts until you deliberately apply them to the real checkout and validate in Codex.

## Safety rules

An explicit read-only request stays read-only. Project OS does not grant permission to install dependencies, delete data, commit, push, deploy, publish or contact external systems. Necessary decisions remain yours; recording and checking the already authorized work belongs to the agent.
