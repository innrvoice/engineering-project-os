# Failure knowledge

Project OS lets Codex record findings while working and carry useful lessons into another repository you own. You describe the outcome; Codex handles the records, preparation and checks. Findings, project evidence and reusable lessons stay in ordinary files under your control.

## Everyday use: Codex records findings as it works

Once a repository is connected, ask Codex to implement, investigate or verify work normally. Following the repository's instructions, Codex should record concrete defects, candidates and accepted risks it discovers during that work, with evidence and the next decisive check. You do not need to say `finding add` for each observation or prefix ordinary development with `$project-os`.

Codex updates existing findings instead of creating duplicates and keeps observations separate from hypotheses. A reproduced defect already named by the user is included, even in a bounded repair. Use the helper's finding record operation with observed evidence, then update the same ID after verification. When evidence confirms a failure mechanism, it can capture a project lesson with the trigger, cause, prevention, decisive verification and applicability boundaries. An unresolved candidate stays a finding rather than becoming advice for another project.

This is agent-led work during the task. Project OS has no background scanner, central failure database or automatic cross-repository synchronization. It does not guarantee exhaustive discovery. Human review and approval are required before a sanitized lesson becomes reusable or moves to another repository.

## Recipe: bring accumulated lessons into a new repository

Open the destination repository in Codex and send one request:

~~~text
$project-os Reuse the useful failure lessons from /path/to/earlier-repository in this repository. Set up Project OS here if needed, prepare anything that is missing and bring over only lessons that fit this project.
~~~

Codex handles the sequence rather than asking you to run each knowledge operation yourself:

1. Inspect the new project's stack and version boundaries. If it is not connected yet, preview the appropriate setup and continue the same transfer after setup is approved.
2. Read the source without changing it. Prefer its approved reusable library. If it only has project lessons or findings, inspect their evidence and prepare lessons only from confirmed mechanisms.
3. Read each candidate's trigger, mechanism, prevention, verification and boundaries before selecting it. A matching title or applies_to tag is only a filter. Exclude an entry whose body does not support its title, and compare the actual lesson bodies for duplicate mechanisms before proposing the batch. The helper's duplicate report covers its canonical content comparison; an empty report does not establish semantic independence. Prepare missing reusable entries outside both repositories, removing private context while preserving the useful mechanism. Leave unconfirmed, misleading, duplicate or inapplicable lessons out and explain why.
4. Before returning the batch review, open or reuse one small plan for this approval-dependent outcome, route the transfer request to its contract and retain the actual pending approval. Show one batch review of the proposed lesson changes: what fits, what is skipped, any conflicts and the exact destination changes. Complete preparation before asking for approval; the user need not provide a sequence of manual commands.
5. Record and route the approval to the same contract, apply only the approved selection and validate the destination. Save evidence for the actual imported and skipped IDs, idempotence and source preservation. Once its gates are verified, mark the routed requests implemented and close through plan complete, which writes the idle checkpoint and fresh receipt atomically. Pass checkpoint --check before returning the completed result; no second checkpoint save is required. Do not leave requests captured with a "completed" decision or claim no remaining work while their routing is unresolved. Preserve existing destination edits and keep the source unchanged. When returning project files, follow WORKFLOW's exact-byte export protocol and validate the reconstructed serialized snapshot before delivery.

The result is a local reusable library the next Codex task can read when relevant. The new project receives the applicable lessons rather than the old project's entire findings register, private history or unresolved hypotheses.

## Recipe: import an already prepared library

When both repositories are connected and the source lessons are already approved, the short request is enough:

~~~text
$project-os knowledge import: /path/to/earlier-repository
~~~

Codex previews the active lessons applicable to the destination's selected capabilities and ecosystem, includes required lifecycle records and explains skips. After approval, it applies the same reviewed import, runs `check` and verifies that a repeated preview has no pending writes. It does not import every lesson merely because the source path was supplied.

## Recipe: carry lessons to another machine

In the source repository, ask:

~~~text
$project-os Prepare the reusable failure lessons from this repository as a portable bundle for another project. Handle the preparation and show me the lessons to review before writing the bundle.
~~~

Codex prepares any missing reusable lessons for your review, applies only the approved selection and exports a JSON bundle outside the source repository. Supply that bundle in the destination Codex task and ask to reuse only lessons that fit the project. Codex previews and imports it through the same workflow. The ChatGPT companion can prepare and inspect supplied bundles and project files; it does not have access to a live local repository.

## Advanced use: individual operations

Use the following controls when you want to add a particular observation, inspect a stage or manage specific lessons. They are also the operations Codex uses to carry out the recipes above.

### How Codex completes the transfer

For already approved source entries, use the existing `knowledge import` helper and its applicability preview. Review platform and version boundaries as well as `applies_to` tags; tags alone do not prove that advice fits the destination. Preserve the lifecycle links required by the selected entries. For newly prepared lessons, apply the same applicability review and approve only the reviewed matching entries directly into the destination with `knowledge approve`; this avoids writing to the source. For a confirmed finding without an existing project lesson, first prepare the project-lesson content and its evidence links in the temporary preparation area, then sanitize the reusable proposal. Keep private evidence out of the destination reusable registry.

### Add a finding

For `finding add: <observation>`, inspect current evidence and search for an existing owner first. Record a stable ID, status, impact, evidence, required next check and optional active plan. Keep observations separate from inference and do not claim an unverified mechanism.

Preview the intended registry and evidence changes, preserve unrelated entries and run the checker after writing.

Use `finding record --target <repository> --input <temporary-json> --dry-run` followed by the same command without `--dry-run`; add `--id <existing-id>` for an update. The input contains title, status, impact, evidence paths and required_check; verified or fixed_unverified also needs resolution. Store actual evidence in the repository first. The helper allocates a stable ID, retains SHA-256 evidence hashes and guards the transaction. Follow the connected WORKFLOW to save and verify the current checkpoint afterward.

### Capture project knowledge

For `knowledge capture: <finding-id>`, require a confirmed mechanism and decisive evidence. Project knowledge may retain repository names, dependencies, local paths and environment details because it does not leave the source repository automatically.

Record applicability, trigger, mechanism, prevention, decisive verification and version or scope boundaries. Link the source finding. Do not turn a candidate or hypothesis into a failure lesson.

### Prepare and approve reusable knowledge

For `knowledge prepare: <lesson-id|all>`, remain read-only. Build a proposal outside the repository from one confirmed project lesson or every confirmed project lesson requested by the user. Remove project names, credentials, personal data, absolute machine paths, every URL, deployment identifiers, evidence paths and copied product history.

Preserve enough detail to keep the trigger, mechanism, prevention, verification and boundaries accurate. Use trimmed canonical IDs and applicability tags without whitespace, commas or control characters. If sanitization would make a lesson misleading, leave it project-specific and explain why.

Show every proposed entry in one batch review. Do not approve, write, export or publish anything during preparation. The helper rejects detected URL forms plus common detectable private patterns and sensitive field names. Screening still cannot identify every project name or contextual disclosure, so human review remains mandatory.

After the user selects entries from the proposal, preview the deterministic approval command:

~~~shell
python3 /absolute/path/to/project-os/scripts/project_os.py knowledge approve --target /path/to/repository --proposal /path/to/proposal.json --ids FAIL-001,FAIL-002 --dry-run
~~~

Use `--all` only when the user approved the complete proposal. Apply the identical reviewed command without `--dry-run`, then run `check`. Approved entries belong to the user and live in `.agents/knowledge/reusable/failures.json`.

`knowledge propose-shared: <lesson-id>` is a deprecated read-only alias for `knowledge prepare: <lesson-id>` in release 2.1.0. Never interpret it as permission to publish a lesson or submit it to Project OS authors.

### List, revise, retire and remove

Use `knowledge list: project|reusable` for a read-only inventory. A reusable lesson can be revised only through a reviewed proposal so target-local changes are never overwritten silently.

`knowledge revise: <lesson-id>` prepares a replacement revision, previews its exact lifecycle links and applies only after review. `knowledge retire: <lesson-id> because <reason>` preserves the lesson and its reason with status `retired`. `knowledge remove: <lesson-id>` is destructive and requires a separate preview plus exact ID confirmation. It refuses to remove either side of a replacement chain. Local removal does not recall copies already imported elsewhere.

Run the matching helper operation with `--dry-run`, review it, apply the same operation and finish with `check`.

### Export reusable knowledge

Export only reviewed reusable knowledge. By default the bundle includes every non-draft entry: active lessons plus retired and replaced tombstones needed to propagate lifecycle changes. A direct repository transfer and a portable bundle carry the same entry format. Neither includes source repository identity or project evidence.

Preview a complete reusable export:

~~~shell
python3 /absolute/path/to/project-os/scripts/project_os.py knowledge export --target /path/to/source-repository --output /path/to/failure-knowledge.json --dry-run
~~~

Use `--ids FAIL-001,FAIL-002` for a selected set. Every export must include each linked predecessor and replacement record needed for a complete lifecycle chain. `--active-only` omits tombstones and works only when the selected active lessons have no lifecycle dependencies. Apply the identical command without `--dry-run`. The helper creates a deterministic `project-os-reusable-knowledge` JSON bundle at a new path that resolves outside the source repository and reports its SHA-256. It refuses to overwrite an existing output file.

In ChatGPT, the user downloads the returned bundle artifact and later uploads it to the destination conversation. In Codex, the destination workflow can read either that bundle or the source repository directly.

### Import into another project

Import is always explicit and never mutates the source. First ensure the destination repository is connected to the current Project OS schema, then preview the source:

~~~shell
python3 /absolute/path/to/project-os/scripts/project_os.py knowledge import --target /path/to/destination --source /path/to/source-repository --dry-run
~~~

The source may also be a canonical JSON bundle. By default the helper selects active lessons whose `applies_to` values match `engineering`, a selected capability pack or a selected ecosystem overlay in the destination. It also considers retired and replaced tombstones regardless of their applicability tags, then recursively includes every linked entry needed to keep each selected replacement chain complete. The preview lists selected and skipped entries with reasons. Use `--ids FAIL-001,FAIL-002` for an exact reviewed set; it fails if a required lifecycle link is omitted. Use `--all` to consider every non-draft entry explicitly.

Apply only the same reviewed command without `--dry-run`, then run `check` and repeat the import dry run. The repeated preview must report no pending writes. Record the approval in requests, reconcile the checkpoint with actual imported/skipped IDs, source preservation and the exact next action, save it through `checkpoint --draft` and run `checkpoint --check` before returning files or a final response. Use the actual index execution/active state; writing a checkpoint does not close a plan. Import rejects detected URL forms in reusable content before changing the target, but human review remains mandatory for contextual disclosures the scanner cannot recognize.

Import is conflict-safe:

- The same ID and content hash is already present and is skipped.
- The same content under another ID is deduplicated and reported.
- The same ID with different content is a conflict and causes no writes.
- A retired or replaced tombstone updates an existing target predecessor only when `previous_content_hash` matches. If the predecessor is absent, the tombstone is retained so an older active bundle cannot resurrect it later.
- A target-local revision is never overwritten silently.

### Deprecated synchronization command

Since 2.1.0, `sync-knowledge` is read-only. It explains that Project OS has no centrally managed knowledge source and directs the user to `knowledge import --source`. It does not write. Use `upgrade` to update product guidance, packs and overlays.
