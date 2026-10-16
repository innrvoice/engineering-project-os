# Durable engineering workflow

Current user and repository instructions take precedence. This managed file supplies the Project OS workflow; project facts, permissions and commands belong to repository-owned records.

## Required writeback for every engineering task

A bounded task can stay plan-free; it still needs durable findings and a current checkpoint. When you reproduce or discover a concrete defect, save the observation and actual command/result in a repository evidence file and record the finding before the final response. A bug already named by the user is included. Fixing it and passing tests does not remove the need to record it. Search the existing findings first, reuse the stable ID and update its status after verification. Do not create findings for ordinary successful edits or turn an untested hypothesis into a confirmed mechanism.

Use the selected helper's `finding record --target <repository> --input <temporary-json> --dry-run`, review it and apply the same command without `--dry-run`. Input has title, status, impact, a nonempty evidence array of real repository-relative files and required_check. New helper proof belongs only to the versioned project_os_finding_proof namespace; bare legacy extension fields remain project-owned. Implicit repeated capture requires unchanged input and proof. Do not use an explicit ID merely to bypass an unexpected evidence change: review that change first. Follow the maintenance ownership review when upgrading earlier unnamespaced captures; preserve old values and hashes. For fixed_unverified or verified include resolution; use verified only for the evidence classes actually checked. Add `--id <existing-id>` when updating. The helper retains evidence hashes and prevents silent changes; write the JSON yourself from observed facts rather than asking the user to operate the register.

Before ending an engineering response, after any knowledge approval/import and before exporting project files for another session, reconcile requests, findings and actual results, then save STATE through `checkpoint --target <repository> --draft <temporary-markdown> --dry-run` and the same applying command, or through guarded plan complete when closing that outcome. Plan completion writes and validates its own current checkpoint receipt atomically; no second save is required. Do this while waiting for approval as well: save the proposed selection, exclusions and exact pending decision before asking. After an approved transfer, save the imported IDs, skipped IDs, checks, source-preservation result and exact next action. An unchanged initialization checkpoint is not a completed handoff.

The checkpoint draft contains one nonempty line each for Updated, Execution state, Active plan, Outcome, Verified, Remaining and Next action. Execution state and Active plan must match the index; a checkpoint does not close or activate plans. Example for a completed bounded task, using the actual date and results:

```text
# Current checkpoint

Updated: YYYY-MM-DD.
Execution state: idle.
Active plan: none.
Outcome: Describe the completed bounded result and relevant finding IDs.
Verified: Name the observed checks and evidence files.
Remaining: State unresolved obligations or none for this bounded outcome.
Next action: Name the first concrete remaining action or await the next request.
```

Replace the date placeholder, preview the write and apply only the reviewed command. Do not copy or edit the helper receipt. Run `checkpoint --target <repository> --check --json` and ordinary `check` afterward. A missing or stale checkpoint receipt blocks a completed-handoff claim even when structural check passes. On recovery, run both checks before trusting STATE; read the current record owners to explain differences. With write permission, reconcile a stale checkpoint before continuing; a read-only recovery reports the discrepancy without changing files. The receipt verifies the captured files, not the semantic truth or completeness of your report.

Before returning a project archive or snapshot, reread every actual source file with fresh read_bytes after all writes and checks. Preserve complete STATE bytes including its HTML receipt, hash those exact bytes and serialize one snapshot file. Never assemble returned files from draft variables, cached strings, narrated command results or rendered Markdown. Reconstruct that exact serialized snapshot in a new temporary directory, verify every path/hash, run check and checkpoint --check on the reconstructed copy and compare the original source hashes again after export. Return only the validated snapshot file. Missing or altered exported bytes mean NOT_READY even if the source checkpoint was CURRENT. Fresh-session acceptance must inspect the actual returned file, not a separately narrated manifest or command report.

## Intake and recovery

Read CONTEXT, STATE, the plan registry, unresolved requests and the active plan with its JSON contract before non-trivial work or after context compaction. Validate existing records with the selected helper check before trusting them; report and repair structural errors from their original owner before relying on recovery. When idle, inspect unresolved requests and planned slices. Load only relevant evidence and capability guidance.

Apply the required writeback above on both Codex and the ChatGPT companion's supplied project copies. Material follow-ups and approval decisions must be captured in the request registry; a successful helper operation alone is not a durable record of the user's instruction. Complete the writeback before returning an updated project archive or snapshot.

Capture a material user correction, clarification or new instruction in the requests registry while handling that message, before long-running work or ending the response. Do not wait for a compaction warning or a separate instruction to save it. Use the exact JSON keys below, never aliases such as origin, target, relationship or source_formulation. Preserve the source text and the decision. Keep credentials and private data out of records. Discussion of alternatives alone is not an implementation instruction; preserve a consequential ambiguity as needs_clarification.

Integrate compatible additions to the same outcome into the active contract. Route independent outcomes to a planned slice with its own contract and explicit sequence. Preserve conflicts as needs_clarification, ask the necessary question and continue authorized independent work. Capturing and incorporating an authorized clarification requires no separate approval. External actions retain their existing authorization requirements.

Captured means saved. Integrated means routed. Implemented requires verified gates and evidence. Withdrawal requires the user's explicit cancellation or replacement, recorded in decision. Never silently discard, complete or defer an actionable requirement.

Route every accepted material follow-up to a real contract before reporting it complete. If no active plan exists, open a small plan for that outcome with its actual acceptance gates; do not leave a completed instruction as captured with null plan and empty gate_ids. An approval-dependent knowledge transfer spans messages: open its plan and route the transfer request before the batch review, preserve pending approval there, then route the approval to the same outcome. After verifying the selected transfer, mark the routed requests implemented with their gate evidence and close through plan complete, which atomically writes the resulting idle checkpoint and fresh receipt. A decision string saying "completed" does not change a captured request's state. A bounded repair without a material follow-up can remain plan-free.

## Canonical intake and proof

The registry has schema_version: 1, next_id and requests. Append to requests, preserve existing entries and increment next_id. A request ID is R- plus at least three digits. recorded_on is the actual date in YYYY-MM-DD form. Here is one routed addition; use real plan and gate IDs:

```json
{
  "id": "R-001",
  "recorded_on": "2026-10-01",
  "source_text": "Also reject None with ValueError.",
  "interpretation": "Include explicit None rejection in the current input outcome.",
  "origin_plan": "001",
  "target_plan": "001",
  "relation": "same_outcome",
  "status": "integrated",
  "gate_ids": ["normalization"],
  "decision": "Compatible addition integrated into plan 001; verification is pending."
}
```

Allowed request statuses are captured, needs_clarification, integrated, implemented and withdrawn. Allowed relations are same_outcome, prerequisite and independent. During unresolved intake, origin_plan and target_plan may be null and gate_ids may be empty. Same-outcome and prerequisite requests must stay in origin_plan. For an explicit cancellation, update the original request to withdrawn and record the user's cancellation in decision. Do not delete it or treat the cancellation as another missing task. Revise the contract and rerun affected checks for restored behavior.

Gate statuses are pending, verified and not_applicable. Never use satisfied, done or passed. A pending gate has evidence: [] and a non-empty next_action. A verified gate needs a real repository evidence file and proof with these exact keys:

```json
{
  "path": ".agents/evidence/input-check.md",
  "sha256": "sha256:<actual 64-digit file digest>",
  "checked_on": "2026-10-01",
  "target": "local",
  "revision": 2
}
```

Compute sha256 from the actual file after writing the observed command, result and target. target must equal the gate target and revision must equal the contract revision. Reassess every retained proof on revision changes; a command/result object alone is not proof. Read the plans README when creating or changing a contract.

Immediately after saving intake, routing, withdrawal or a contract revision, run the selected helper check --target <repository>. Repair schema errors before long application work or ending the response. Resolve the helper from the selected installed skill, or the explicitly selected candidate during isolated evaluation; never guess a stale path. A failed check must be reported and cannot be treated as a successful checkpoint.

## Outcomes and contracts

Define one observable outcome and every prerequisite needed for it, including effective schema, migrations, configuration, delivery and verification in the named target when applicable. A code-only outcome is valid only when it matches the actual instruction and is stated explicitly. Do not move a required prerequisite to an independent slice to make the original plan appear complete.

The plan registry owns status. The plan Markdown owns implementation narrative and decisions. Its JSON contract owns acceptance gates and evidence. The requests registry owns intake and routing. STATE is a compact checkpoint with references, not another task register.

Before resuming a legacy_uncontracted plan, prepare its contract from current instructions and repository truth, preview the change and remove the legacy mark only after validation. Retain historical legacy_closed dispositions without claiming new acceptance.

On material outcome changes, increment contract revision and record the reason and controlling request in the plan narrative. Reassess all evidence before attaching it to the new revision. Also revalidate evidence made stale by code or external changes. Missing access, permission or proof is pending, never not_applicable. Not_applicable requires a scope-grounded reason.

## Pull request and release review

When Codex Review is configured or required, give its completion a separate acceptance gate when opening a plan for PR delivery or release. Name the repository, PR and exact final source commit in its target once known. CI, source tests and local agent reviews do not satisfy it. Read the actual code/security review activity and every remark through the configured integration; missing access, running or unknown status, an older reviewed commit or an unresolved remark is NOT_READY and blocks merge and publication.

A delivery-readiness assessment of an active plan also needs the required checkpoint writeback when local record writes are allowed: save and verify a checkpoint naming the expected commit, unfinished review and exact next action before returning NOT_READY. Do not defer that save because source files stayed unchanged or external actions are forbidden. An explicit read-only or no-file-change request stays read-only; report a stale or missing checkpoint without changing it.

Record the final reviewed commit, completed review status and evidence-backed disposition of every remark. Resolve review threads after verification; simply hiding a thread is not proof of a fix. A later source commit invalidates the old review evidence: revise the target/contract, repeat affected checks and wait for the matching review. Pass the repository's applicable live review guard immediately before merge and publication. Keep the plan open while this prerequisite is pending. Owner authorization does not prove review completion or silently waive a known blocker.

## Checkpoints and closure

When a durable plan owns the outcome, run plan status --target <repository> --require-ready --json at each meaningful checkpoint and before a final result, readiness claim, publication recommendation or request for release authorization. Lead the report with READY or NOT_READY and name the outcome. If the command fails, any gate is pending or proof is missing, say the result is not ready and list the blocking obligations before local successes. Keep the plan open. Do not describe it as a verified candidate, ready to release or complete. Do not recommend publishing it to obtain missing acceptance. For bounded plan-free work, use the required finding/checkpoint writeback and checkpoint freshness guard; do not create a plan solely to obtain a status command.

Reconcile requirements, contracts, findings and evidence. Report what was implemented, what was verified and where, what remains for closure, what needs an owner decision or authorization and which additions belong to the current or a following slice. Leave one exact next action.

Use plan status to expose open gates and requirements. Close only through plan complete with a reviewed checkpoint draft and dry run. A passing structural check does not prove hosted, artifact, production, manual, owner-reported or physical acceptance. The helper validates recorded proof; the agent must judge whether it demonstrates the outcome.

After closure, independent planned slices remain planned. Do not automatically activate the next slice or grant new authority. For a correction to an already closed outcome, preserve historical proof and open a new corrective slice rather than rewriting its completion receipt.

## Boundaries

Project OS has no background access to chat, automatic cross-repository synchronization or independent production verification. Persistence depends on the agent recording incoming instructions. Keep exact candidate package and fresh host behavior checks separate; never replace an installed stable skill with a mutable candidate. Validate new behavior against an exact isolated candidate before publication. A ZIP or source test cannot replace missing host acceptance. Explicitly bounded source preparation can be ready only for that named scope; never expand that readiness into feature or release readiness. Project OS cannot intercept chat or independently verify the meaning of evidence; the agent must follow this workflow.
