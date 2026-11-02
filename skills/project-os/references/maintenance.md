# Maintain Project OS

Use this workflow for checks, repairs, upgrades, Program lifecycle and durable plan lifecycle. Ordinary bounded code changes follow repository instructions and do not need `$project-os`.

Resolve `scripts/project_os.py` relative to the installed skill. The exception is explicit candidate runtime testing while developing Project OS itself.

## Check

Run this in Terminal:

~~~shell
python3 /absolute/path/to/project-os/scripts/project_os.py check --target /path/to/repository
~~~

The command is read-only. Report each concrete error and the owning record. Do not turn a structural pass into a claim about application, artifact, deployment, production, manual or physical behavior.

## Start with a compact inspection

First identify readable project files, the selected helper and whether execution is available and permitted. Choose the applicable route before running any command:

| Available capability | Recovery route | Verification limit |
| --- | --- | --- |
| Selected helper can run and implements `brief` | Run `brief`, follow `read_next` and inspect original owners when needed | Report actual integrity, freshness and outcome readiness separately |
| Selected older helper can run but lacks `brief` | Keep that helper selected; use its supported `check` and `checkpoint --check` commands and read configured owners | Disclose unsupported checks; never silently substitute another helper |
| Execution is unavailable or forbidden, or the selected helper is missing | Read supplied SYSTEM and configured owners where accessible; describe recorded work provisionally | Integrity, checkpoint freshness and readiness checks remain unverified; preserve files and pending gates |

A real structural or stale-checkpoint failure is not an older-helper compatibility case. Inspect the actual error. If an older helper also lacks a required validation, finding, checkpoint or closure command, leave that operation incomplete and request a suitable selected helper. Do not test execution with a command the user has forbidden. If project material is missing or unreadable, request the specific files needed; an empty host workspace is not the supplied project.

With permitted helper execution, run `brief` before reading the relevant source records during repository recovery:

~~~shell
python3 /absolute/path/to/project-os/scripts/project_os.py brief --target /path/to/repository --json
~~~

The read-only report combines structural validation, checkpoint freshness, the active plan's readiness and pending gates, complete unresolved request objects and planned or blocked slices. Original request text, decisions and extension fields are preserved. Follow `read_next` for CONTEXT, STATE, the active Program contract when present and the active plan with its contract; `record_paths` separately names the original owners. Read Program authority, phases and cost boundaries even when no plan is active. Do not reread full registries or repeat successful standalone inspection checks just to recover facts already returned by `brief`. Read the original owner before editing it or when a needed field, history or error requires it. Verified and not-applicable gates are counted rather than copied, while resolved requests and historical plan bodies are omitted. Read the original contract for their proof and reasons. No unresolved item is truncated.

Exit zero means record integrity passed and the checkpoint is current; pending work can still make the active plan NOT_READY. There is no overall project-readiness claim. A failed structural check sets `records_available: false`; empty work arrays then mean unavailable data, not an empty backlog. A stale checkpoint fails inspection while retaining validated pending work. The report does not activate work, write a checkpoint or replace final `plan status --require-ready`. Without `--json`, it prints a text overview.

Without the required execution, do not change records, save a receipt or close a plan. Say which checks and required writeback were not performed and what capability or material would allow them. A stored PASS or CURRENT is historical file content, not a newly executed check. Do not synthesize a brief report or invent command output. If file operations are permitted, return an unchanged input or byte-preserving transport copy with factual hashes and the whole STATE receipt, labeling helper checks and Project OS export validation unperformed. This does not establish record integrity or freshness. If the host cannot create an actual downloadable file, state that limitation; do not claim the export protocol passed without its checks.

## Save findings and a current handoff

The connected WORKFLOW requires writeback even for a bounded repair without a plan and for supplied project copies in ChatGPT. First apply the capability route above; unavailable required execution leaves the input unchanged and writeback explicitly unperformed. With execution available and permitted, reproduce the defect and save observed commands/results in a repository evidence file, then use the finding helper with a temporary JSON input:

~~~json
{
  "title": "Describe the observed defect",
  "status": "confirmed",
  "impact": "Describe the affected behavior",
  "evidence": [".agents/evidence/reproduction.md"],
  "required_check": "Name the decisive remaining check"
}
~~~

~~~shell
python3 /absolute/path/to/project-os/scripts/project_os.py finding record --target /path/to/repository --input /private/tmp/finding.json --dry-run
python3 /absolute/path/to/project-os/scripts/project_os.py finding record --target /path/to/repository --input /private/tmp/finding.json
~~~

Search existing findings first. Use `--id <existing-id>` to update the same finding; verified or fixed_unverified input also needs resolution. The helper allocates the next stable ID, retains evidence SHA-256 values, preserves local fields on explicit updates and reuses an exact repeated input. It does not guess semantic equivalence or whether your status is justified. `check` verifies captured evidence hashes when present, while legacy findings remain compatible.

After the task, a pending knowledge review or an approved transfer, reconcile STATE against the real records. Create a UTF-8 draft outside record owners with Updated, Execution state, Active plan, Outcome, Verified, Remaining and Next action lines. Use the actual index state and the connected WORKFLOW example; keep the draft at most 78 lines. Then preview, save and verify:

~~~shell
python3 /absolute/path/to/project-os/scripts/project_os.py checkpoint --target /path/to/repository --draft /private/tmp/checkpoint.md --dry-run
python3 /absolute/path/to/project-os/scripts/project_os.py checkpoint --target /path/to/repository --draft /private/tmp/checkpoint.md
python3 /absolute/path/to/project-os/scripts/project_os.py checkpoint --target /path/to/repository --check --json
python3 /absolute/path/to/project-os/scripts/project_os.py check --target /path/to/repository
~~~

The helper writes only STATE and appends a receipt binding its body and current record owners, active plan/contract and active Program where applicable. Checkpoint does not complete or activate a plan. `checkpoint --check` is read-only and fails for missing, malformed or stale proof, including a later registry or active-contract change. General `check` still validates structure and preserves old records. CURRENT proves file identity and consistency, not the completeness or truth of your prose. A read-only fresh session reports stale/missing receipts without rewriting them; with write authority, reconcile and save before continuing.

## Repair

Inspect the repository and reproduce the checker error first. Preview the smallest change to its actual owner. Do not create duplicate state to silence an invariant. Preserve unrelated work, apply only a clean preview and run the checker again.

## Plans in Standard or Program

A plan owns one observable outcome that must survive checkpoints. It is independent of whether a Program is active.

Before opening, checkpointing, resuming or closing a plan:

1. Read AGENTS and `.agents/WORKFLOW.md` and choose the recovery capability route above. With permitted execution, run the selected helper's `brief --target <repository> --json` and follow `read_next` for CONTEXT, STATE, the active Program contract when present and the active plan with its contract. Use complete unresolved requests from a successful report; read original registries before editing them or when required details or errors demand it. Load only relevant packs and knowledge. Without required execution, keep the assessment read-only and checks unverified.
2. Compare the checkpoint with current files and Git HEAD/worktree status where available and permitted.
3. Revalidate evidence made stale by later code or external state.
4. Preview the intended record transition.

Keep exactly one active plan while execution is running. A plan file is not a transcript.

At checkpoint, capture and route material user additions, update only supported contract gates, rewrite `STATE.md` as a compact handoff and leave one exact next action. Report implementation, proof and target, obligations remaining for closure, owner decisions or authorization and following slices.

Never write `done` manually. Close through the guarded helper only with its required evidence and implemented or explicitly withdrawn scoped requests. Blocking preserves the exact unmet condition and resume point. Supersession names the replacement or next decision and does not rewrite the old plan.

`plan block` changes the active plan to `blocked`, execution to `idle` and the optional `active_plan` to null. Record the blocker and the first action available after it clears in the plan and STATE.

For `plan resume`, continue the active plan when one exists. To reactivate a blocked plan, accept `plan resume: <plan-id>` or select the only blocked plan when execution is idle. Ask for the ID when multiple blocked plans could match. Do not displace another active plan. Verify the recorded blocker is resolved from current evidence; if it is still unresolved, leave the plan blocked and report the exact missing condition. Preview `blocked` -> `active`, `idle` -> `running`, the optional `active_plan` pointer and the next action in STATE, then apply that transition. Preserve completed evidence and leave acceptance items incomplete until their checks actually pass. With `do not continue implementation`, stop after the authorized record transition; with `do not change files`, keep the entire assessment read-only.

Run the checker after every plan transition.

### Intake and contract ownership

Apply the managed WORKFLOW on ordinary engineering turns without requiring a Project OS prefix. Immediately save material corrections, clarifications and new instructions in the requests registry before long work or ending the response. Copy the complete relevant original wording verbatim into source_text, including conditions, exclusions and approval limits. Do not shorten, summarize, translate or replace wording with ellipses; write your interpretation separately in interpretation. For a message covering several outcomes, preserve this outcome's complete block and every shared condition that applies to it without copying unrelated project material. Compare saved source_text with the actual message before continuing. Route compatible same-outcome and prerequisite additions into the origin plan's contract; route independent outcomes into planned slices with their own contracts and explicit sequence. A conflict stays needs_clarification until the necessary decision arrives. Alternatives discussed during brainstorming are not automatically implementation instructions.

On explicit withdrawal, keep the original source_text unchanged and quote the complete relevant cancellation wording verbatim in decision before explaining the disposition. Do not replace the original request with the cancellation or retain only a translated summary. Apply the same original-wording rule to a knowledge approval, including its selection, conditions and exclusions. The helper validates stored records and proof, not whether an agent copied the original conversation accurately; a passing check or current receipt does not establish that fidelity.

The index owns status and contract_path. Plan Markdown describes implementation and decisions, not a second acceptance register. The adjacent JSON contract owns gates. Requests own intake and routing. STATE links the current checkpoint. Read the connected WORKFLOW canonical intake and proof examples and the plans README contract template. Use literal request keys origin_plan, target_plan, relation, source_text, recorded_on, status, gate_ids and decision. Validate and repair records immediately after intake, routing, withdrawal and revision before continuing application work. Increment contract revision on material outcome changes, record the reason and controlling request in Markdown and reassess evidence before attaching it to the new revision.

Before resuming any legacy_uncontracted plan, including an already active one, review a contract from current instructions and repository evidence, preview the attachment and remove its migration mark. An old closed disposition stays legacy_closed and is not newly verified. Preserve the old plan and its unverified obligations on supersession.

### Read status and complete

Run the read-only status helper before each final checkpoint, readiness claim, publication recommendation or release permission request:

~~~shell
python3 /absolute/path/to/project-os/scripts/project_os.py plan status --target /path/to/repository --require-ready --json
~~~

Use --id when no single active plan exists. Status reports READY or NOT_READY for the named outcome, gates, proof errors, scoped requests, blockers and following planned slices. --require-ready fails while any mandatory acceptance or request remains open. Lead with NOT_READY and the blockers before local successes; do not call the candidate verified or ask to publish it. Run required host scenarios on an exact isolated candidate before publication, preserving stable. A code-only scope cannot be used to imply release readiness. It cannot independently inspect production or judge the meaning of evidence.

Prepare a UTF-8 checkpoint draft in a temporary file outside repository record owners. Preserve relevant verified state and report the finished outcome, its evidence and remaining independent work. The draft must declare Execution state: idle and Active plan: none on separate lines and contain at most 78 lines, reserving two lines for the helper receipt within the 80-line STATE limit. Existing closure narratives remain supported; the helper does not invent missing narrative fields. Preview closure:

~~~shell
python3 /absolute/path/to/project-os/scripts/project_os.py plan complete --target /path/to/repository --id 001 --checkpoint /path/to/checkpoint.md --dry-run
~~~

Review the entire transition, completion receipt and checkpoint receipt, then apply the identical command without --dry-run. The helper guards the index, SYSTEM, STATE, plan, contract, request registry, checkpoint owner records and proof snapshots; it validates resulting state and written files before success. It updates only the index and STATE, writes a checkpoint receipt bound to the post-transition index and validates CURRENT inside the same transaction. Successors remain planned. A failed gate, stale proof, unresolved request, write failure, stale resulting checkpoint or concurrent input change prevents completion. Do not substitute a manual status edit or call a prerequisite independent to bypass closure.

Guarded plan completion already writes the now-idle checkpoint and its fresh receipt atomically; a second checkpoint save is unnecessary. Run the read-only `checkpoint --check` to verify the result. Preserve the complete STATE bytes, including the HTML receipt, when returning project files. A separate checkpoint write remains appropriate when later work changes the record owners or the handoff narrative.

### Return exact project files

After all writes and checks, collect each exported file with a fresh `read_bytes()` from its actual path. Preserve the whole STATE file, including its HTML receipt; compute each exported content hash from those exact bytes. Do not rebuild a snapshot from checkpoint drafts, cached variables, response prose or rendered Markdown. Serialize one snapshot file, reconstruct that exact serialized file into a new temporary directory and run both `check` and `checkpoint --check` there. Verify every reconstructed path and hash and compare the source hashes again after export to detect concurrent changes. Return only that validated snapshot file. A source CURRENT result does not override missing or altered bytes in the returned file set: report NOT_READY and repair the export before delivery. Read-only recovery must inspect the actual supplied files and preserve them.

Build the inventory from the actual authorized source tree, not a staging subset. Include every promised project, hidden owner, full STATE receipt and nested proposal or report, including files prepared outside a project directory. A manifest can accurately describe an incomplete staging copy, so compare the source path set as well as hashes. Do not retroactively repair a historical snapshot after its omission is discovered; retain that first observation separately from a corrected current artifact.

When execution of this bundled utility is permitted, preview and apply a byte snapshot with explicit required paths:

~~~shell
python3 /absolute/path/to/project-os/scripts/snapshot.py create --root /path/to/actual-source-tree --output /path/outside/source-tree/snapshot.zip --require campaign-output/proposals/ownership.json --dry-run
python3 /absolute/path/to/project-os/scripts/snapshot.py create --root /path/to/actual-source-tree --output /path/outside/source-tree/snapshot.zip --require campaign-output/proposals/ownership.json
python3 /absolute/path/to/project-os/scripts/snapshot.py check --root /path/to/actual-source-tree --archive /path/outside/source-tree/snapshot.zip --require campaign-output/proposals/ownership.json
~~~

Repeat --require for all promised files or nonempty directories. The output must be new and outside the source tree. The utility recursively includes every regular file without implicit exclusions, preserves existing MANIFEST.json/AUDIT.json and reserves PROJECT-OS-SNAPSHOT.json for its own inventory. Missing required paths, symlinks, special files, unsafe paths, a reserved-name collision or detected source drift refuse the snapshot. It verifies the actual serialized ZIP against the original inventory and never runs project helpers, application code or tests. A successful transport-byte result does not establish record integrity, freshness or readiness: reconstruct that ZIP and run only the project checks actually permitted. An execution prohibition remains controlling; if the utility is unavailable or forbidden, report that limit and use only permitted file tools with equivalent inventory checks.

Dry-run includes the full path/size/hash inventory and creates no output. Save large JSON outside the source tree. File bytes and directory paths are preserved; original permissions, ownership, timestamps and extended attributes are not. A failed create after exclusive output creation may leave an unverified file. Do not deliver it as a successful snapshot or delete a pathname whose ownership may have changed; inspect the error and use the read-only check against the actual source. The utility deliberately does not unlink a potentially replaced published pathname during failure cleanup.

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

Inspect release, schema, managed guidance baselines, user-owned knowledge and Program state first. Review the complete file preview. Abort on managed conflict, unsafe ownership or stale state. Apply the same command without `--dry-run`; a successful apply ends with the checker.

If the repository release is newer than the helper, stop and use a matching or newer helper. Upgrade never downgrades repository state. Do not lower version fields manually to bypass this check.

For a source repository recorded as 2.2.3, bare finding evidence_sha256 or capture_input_sha256 fields are ambiguous. Read the real configured registry and capture history, prepare one review file inside the target with schema_version1, exact registry_sha256 and an ownership map of every ambiguous ID to project_owned or helper_2_2_3. Ask only if ownership cannot be established from the supplied evidence. Pass --finding-proof-review <absolute-inside-target-file> to both preview and apply. Proven helper hashes are copied unchanged into project_os_finding_proof; changed evidence, stale or incomplete reviews and namespace collisions refuse writes. Preserve raw legacy values, custom paths and the complete review. Earlier source releases preserve these fields as project data automatically; never infer helper ownership merely from a matching shape.

If a valid helper proof references a file the prospective upgrade rewrites or deletes, preserve its historical bytes through the same reviewed transaction. Extend the review with snapshot_evidence mapping each affected finding ID to the exact original path and its recorded sha256 digest. Include every affected unarchived proof path and no unaffected paths; preview reports the required map. For an already namespaced proof, ownership is empty. Read and verify the actual bytes and complete preview before applying the same command. Do not refresh the old hash to match new managed content, classify genuine helper proof as project-owned or lower a version to bypass migration.

For example, replace both digest placeholders with the exact registry and recorded evidence hashes; include other affected paths and ownership decisions when the preview requires them:

```json
{
  "schema_version": 1,
  "registry_sha256": "sha256:<exact-registry-digest>",
  "ownership": {"F-001": "helper_2_2_3"},
  "snapshot_evidence": {"F-001": {"AGENTS.md": "sha256:<recorded-evidence-digest>"}}
}
```

Upgrade writes content-addressed files below the configured evidence directory's finding-proof-snapshots/ and adds evidence_snapshots inside the owned proof namespace. Each mapping records the original path's snapshot file, source_release, registry_sha256 and review_sha256; original evidence paths, capture digest, evidence digests and raw legacy values remain unchanged. The checker validates these historical bytes against the original digest, not the rewritten current file. These archives are tamper-evident, not immutable or current acceptance proof. Ordinary unsnapshotted evidence remains sensitive to current-file changes. Existing exact archives are reused, changed or unsafe destinations refuse writes and repeated upgrades do not snapshot archived proof again. An explicitly reviewed finding --id update captures current evidence as a new proof and preserves raw legacy values and existing archive files. After upgrade, save a current checkpoint and report which evidence is historical and what remains unverified about the new files.

Upgrade preserves existing instructions and project content. Schema 5 adds managed WORKFLOW, an empty requests registry, minimal AGENTS routing and plan-index format metadata in the same transaction. Historical closed dispositions are registered as legacy_closed; unfinished plans without contracts become legacy_uncontracted and must be reviewed on resume. It does not reconstruct chat history or invent proof. Markdown plans, context, state, evidence and application code remain unchanged apart from an explicitly required legacy lifecycle or knowledge migration. Findings retain all raw fields; only explicitly reviewed helper proof adoption adds its versioned namespace. The schema 3 to 4 migration removes release-managed seed entries, promotes user-owned lessons proven by adoption coverage and keeps compatible unresolved local entries as drafts that require review. It aborts without writes if classifying any retained local entry would discard lifecycle metadata or unsupported user fields.

A schema 2 repository with a legacy Program contract needs explicit classification:

- Active: add `--legacy-program-state active`. Preserve the editable contract, enter Program, record its legacy origin and migration date and leave the unprovable start date null.
- Closed: add `--legacy-program-state closed --disposition completed --closed-on <YYYY-MM-DD>` or `--legacy-program-state closed --disposition stopped --closed-on <YYYY-MM-DD> --reason <reason>`. Archive the exact bytes and enter Standard.

Never infer this classification from the file alone. The closed date is the actual historical closure date, not the upgrade date. Derive it only from repository evidence. If the state or date cannot be established, stop for the user's decision.

`--closed-on` is valid only for a closed schema 2 migration. Do not pass it for an active legacy Program or a current-schema upgrade.

Do not edit version or schema fields manually. Since 2.1.0, `sync-knowledge` is a read-only deprecation route and cannot replace upgrade. Schema, lifecycle, managed guidance, user-owned knowledge migration and metadata remain one transaction.

For pull request delivery or release with Codex Review configured or required, keep a separate contract gate targeting the repository, PR and exact final source commit. Wait for completed code/security reviews, inspect every remark and retain evidence-backed dispositions before merge or publication. CI success and local reviews are separate checks. A later source commit invalidates the review evidence and requires a new matching review; missing, running or unresolved review means NOT_READY. Use the repository live guard when available and preserve its exact final-head result.

## Self-hosting

When developing Project OS:

1. Let the installed stable skill govern the workflow and interpret chat requests.
2. Develop and test the candidate helper from the source checkout explicitly.
3. Do not replace the installed skill with a mutable candidate checkout.
4. After release, install the versioned tag and start a fresh task before installed-copy validation.

This separates the rules governing the work from the code currently being changed.
