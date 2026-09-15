# Reference

This is the technical contract for Project OS 2.1.1. Start with the [README](../README.md) if installation, plugin invocation or repository connection is still new.

## Interfaces

| Interface | Used for | Invocation |
| --- | --- | --- |
| Codex plugin or standalone skill | Repository-native workflows in the selected local workspace | `$project-os ...` in Codex chat |
| Repository records | Durable context, state, plans, findings, evidence and knowledge | `AGENTS.md` and `.agents/` files |
| Python helper | Deterministic setup, validation, upgrade, Program transitions and reusable knowledge operations | `project_os.py ...` in Terminal |
| ChatGPT companion | Explanations and workflows over project files or portable bundles supplied in the conversation | `@Engineering Project OS ...` with the needed material |

Engineering Project OS was built for Codex. `$project-os` selects the bundled skill for one Codex message while `@Engineering Project OS` selects the ChatGPT companion. Text after either selector is natural language, not a helper command line or rigid parser. This release enables implicit invocation so the selected plugin can expose the skill for a clear Project OS request.

Installation and repository access are separate. Codex can use only the local workspace selected for the task. ChatGPT can use only the project description, files and portable bundles available in the chat. Choosing a setup can begin from a description while reviewing an existing setup requires its actual Project OS files. Neither surface gains repository access from installation alone.

The ChatGPT Directory listing exposes three outcome-focused starter prompts:

| Starter prompt | Required initial context |
| --- | --- |
| `Tell me how Project OS helps Codex resume real engineering work across sessions.` | None |
| `Help me set up Project OS for this repository and start with a safe preview.` | Project description and any existing authority files |
| `Help me reuse verified failure knowledge from an earlier project in this one.` | An approved reusable bundle plus destination context; Codex can also use both repositories |

The helper lives at `scripts/project_os.py` inside the installed skill. Terminal examples use an absolute placeholder path so the target repository does not need its own helper copy.

## Project OS requests

| Shortcut | Required argument | Behavior |
| --- | --- | --- |
| `overview` | None | Read-only explanation of the developer audience, benefits, knowledge model and next useful workflow |
| `help` | None | Read-only menu of every shortcut and Terminal distinction |
| `inspect` | None | Read-only repository and control-plane inspection |
| `bootstrap` | None | Create Standard after a clean dry run |
| `adopt` | None | Map compatible existing records after a clean dry run |
| `check` | None | Read-only deterministic validation |
| `repair` | Error or scope if not already known | Repair only verified Project OS inconsistency |
| `upgrade` | None | Upgrade to the installed release with conflict checks |
| `program start: <initiative>` | Initiative | Start one complete multi-phase contract |
| `program status` | None | Read-only Program status |
| `program close completed` | None | Close after all exit evidence exists |
| `program close stopped: <reason>` | Reason | Stop and archive an incomplete Program |
| `plan open: <outcome>` | Outcome | Open one resumable execution package |
| `plan checkpoint` | None | Save a reconciled checkpoint |
| `plan resume[: <plan-id>]` | Plan ID when ambiguous | Continue active work or reactivate a blocked plan after its blocker resolves |
| `plan complete` | None | Complete only with required evidence |
| `plan block: <reason>` | Reason | Preserve a precise blocker and resume point |
| `plan supersede: <reason>` | Reason | Retire a plan whose route or outcome was replaced |
| `finding add: <observation>` | Observation | Record evidence without inventing a mechanism |
| `knowledge capture: <finding-id>` | Confirmed finding ID | Create project-specific failure knowledge |
| `knowledge list: project\|reusable` | Scope | List user-owned knowledge without writing |
| `knowledge prepare: <lesson-id\|all>` | Project lesson ID or `all` | Prepare a sanitized proposal outside the repository without writing |
| `knowledge approve: <proposal> <lesson-id\|all>` | Proposal and reviewed selection | Add only approved entries to the reusable library |
| `knowledge revise: <lesson-id>` | Reusable lesson ID | Prepare and apply a reviewed replacement revision |
| `knowledge retire: <lesson-id> because <reason>` | Lesson ID and reason | Retire an entry while preserving its lifecycle |
| `knowledge remove: <lesson-id>` | Lesson ID | Permanently remove a local entry after an explicit preview and confirmation |
| `knowledge export: <destination>` | New output path | Export approved entries and complete lifecycle chains to a deterministic bundle |
| `knowledge import: <repo-or-bundle>` | Source repository or bundle | Preview active entries applicable to the target plus lifecycle tombstones |
| `knowledge import all: <repo-or-bundle>` | Source repository or bundle | Explicitly preview every non-draft source entry |
| `knowledge propose-shared: <lesson-id>` | Project lesson ID | Deprecated read-only alias for `knowledge prepare` |

The table shows the intent words used after `$project-os` in Codex. In ChatGPT, select `@Engineering Project OS` and express the same intent in ordinary language. `$project-os help` always returns this class of concise menu, with purpose, required arguments and one or two examples. It never writes files. See [Usage](USAGE.md) for complete examples.

## Standard and Program

| State | Use it for | Contents |
| --- | --- | --- |
| Standard | Every connected repository's normal operation | Routing, context, state, plans, findings, evidence, knowledge, packs and overlays |
| Program | One explicitly started multi-phase initiative | All Standard capabilities plus one active `PROGRAM.md` contract |

Bootstrap and adoption finish in Standard. A long task can remain in Standard with a plan. Program is not a larger installation profile and is not created automatically.

A Program is justified when multiple distinct phases or plans require one shared authority and exit contract. It is temporary:

`standard -> program -> standard`

### Program definition

The helper accepts a JSON definition whose top-level fields are:

| Field | Requirement |
| --- | --- |
| `initiative` | Non-empty Program name |
| `outcome` | One observable overall outcome |
| `authority` | Non-empty array of controlling sources or decisions |
| `phases` | At least two phase objects |
| `phases[].name` | Non-empty phase name |
| `phases[].outcome` | Observable phase outcome |
| `phases[].exit_conditions` | Non-empty array of phase exit conditions |
| `evidence_requirements` | Non-empty array of required evidence classes or checks |
| `cost_boundary` | Non-empty array of time, money, operational or scope limits |
| `exclusions` | Non-empty array of work outside the Program |
| `exit_conditions` | Non-empty array governing completion of the whole Program |

The helper rejects an incomplete definition. It generates a stable `program-YYYYMMDD-NNN` identifier and renders the active contract to `.agents/PROGRAM.md`. Starting a Program does not open a plan.

Closing requires no active plan. Use `completed` only after Program exit evidence has been evaluated by Codex and the user. The helper enforces structural lifecycle rules but cannot judge whether that evidence proves the outcome. `stopped` requires a reason and preserves unresolved obligations.

## Record ownership

| Path | Owns |
| --- | --- |
| `AGENTS.md` | Startup routing, authority, working method, safety and verification expectations |
| `.agents/SYSTEM.json` | Release, schema, state, active Program, mappings, selections and managed guidance baselines |
| `.agents/CONTEXT.md` | Durable verified facts, authority, architecture and exact commands |
| `.agents/STATE.md` | Current scope, verified progress, exact next action and blockers |
| `.agents/plans/index.json` | Canonical execution state and plan statuses |
| `.agents/plans/NNN-*.md` | One observable outcome, its work and acceptance evidence |
| `.agents/findings/findings.json` | Concrete defects, candidates and accepted risks |
| `.agents/evidence/` | Sanitized, dated evidence linked from plans or findings |
| `.agents/knowledge/project/` | Confirmed repository-specific lessons |
| `.agents/knowledge/reusable/failures.json` | Sanitized, reviewed and user-owned portable failure mechanisms |
| `.agents/packs/` | Managed capability and ecosystem guidance selected for the repository |
| `.agents/PROGRAM.md` | The one active multi-phase Program contract |
| `.agents/history/index.json` | Closed Program disposition, canonical closure date, archive path and SHA-256 digest |
| `.agents/history/programs/<id>/PROGRAM.md` | Exact closed Program contract bytes |

`.agents/history/` is optional until the first Program closes or compatible indexed history is adopted. Starting the first Program creates no empty history directory or index. History is valid while the repository is in Standard or Program. Archived records are never current authority.

## Archive integrity boundary

On Program close, the helper copies the exact active contract bytes and records their SHA-256 digest. The checker requires every indexed archive to exist, match its digest and have a canonical closure date. Stopped entries also require a non-empty reason. An uncoordinated edit, deletion or substitution fails the check.

This is tamper-evident, not technically immutable. It is not signed, it does not prevent a deliberate rewrite of both archive and index and it does not replace Git access controls or review.

An archive mismatch requires an authority decision. Do not automatically rehash changed content to make the checker pass.

## Plan and finding invariants

Plan statuses are `planned`, `active`, `blocked`, `done` and `superseded`.

When `execution_state` is `running`, exactly one plan is `active`. If `active_plan` is present, it names that plan. When no plan is active, execution state is `idle` and `active_plan`, when present, is `null`.

Finding statuses are `candidate`, `confirmed`, `fixed_unverified`, `verified`, `accepted_risk`, `deferred`, `rejected` and `merged`.

Reusable failure knowledge statuses are `active`, `draft`, `retired` and `replaced`.

A status transition does not manufacture evidence. `done`, `verified` and completed Program closure require the evidence class named by the owning record.

## User-owned reusable knowledge

Project knowledge and reusable knowledge have different privacy boundaries. Project knowledge may retain repository-specific evidence and context. Reusable knowledge contains only lessons explicitly prepared, reviewed and approved by the user for transfer.

Project OS ships no central failure database and no release-managed seed entries. A new repository starts with an empty reusable registry. Users can move their own lessons directly between repositories or through a portable bundle without submitting them to the publisher or waiting for a Project OS release.

The reusable registry has this top-level shape:

~~~json
{
  "schema_version": 1,
  "entries": []
}
~~~

Each entry requires `id`, `title`, `status`, `applies_to`, `trigger`, `mechanism`, `prevention`, `verification`, `boundaries` and `source`. `applies_to`, `verification` and `boundaries` are arrays. `status` is `active`, `draft`, `retired` or `replaced`. Lifecycle entries may also use `replaces`, `replaced_by`, `reason` and `previous_content_hash`. Canonical IDs and applicability tags are trimmed and cannot contain whitespace, commas or control characters.

For active, retired and replaced entries, `source.kind` is `user-reviewed`. A schema migration may preserve an unresolved local entry as `draft` with `source.kind: migration-review-required`. Every source also records `created_with` and a canonical `sha256:` content hash. Migrated entries may retain a non-private `origin_pack` for coverage verification, but applicability is determined only by `applies_to`.

A prepared approval or revision proposal has `format: project-os-knowledge-proposal`, `schema_version: 1` and a non-empty `entries` array. Every proposal entry contains exactly `id`, `title`, `applies_to`, `trigger`, `mechanism`, `prevention`, `verification` and `boundaries`. It contains no status, provenance or content hash; the helper adds reviewed provenance and the canonical hash during approval. Proposal and import validation rejects detected URL forms in reusable content, while human review remains responsible for contextual disclosures the scanner cannot recognize.

The portable bundle has this top-level shape:

~~~json
{
  "format": "project-os-reusable-knowledge",
  "schema_version": 1,
  "created_with": "2.1.1",
  "entries": []
}
~~~

Bundle JSON uses deterministic ordering and formatting. The helper reports the bundle SHA-256 separately. It does not add a timestamp or source repository identity. A default export includes active entries plus retired and replaced tombstones. Drafts never leave the repository. A selected export fails if `--ids` omits a linked predecessor or replacement record required for a complete lifecycle chain. `--active-only` omits tombstones but still fails when an included active lesson depends on an omitted lifecycle record.

Default import selects active entries whose `applies_to` intersects the destination tags and considers retired or replaced tombstones regardless of applicability, then recursively includes every linked entry needed to keep each selected replacement chain complete. Every destination has `engineering`; selected pack names add `service`, `web`, `mobile`, `data` or `delivery`; the `react-native-expo` overlay adds `react-native-expo`, `react-native` and `expo`. The preview reports selected and skipped entries with reasons. `--ids` chooses an exact set and fails if it omits a required lifecycle link. `--all` explicitly bypasses applicability filtering.

Import is idempotent and conflict-safe. The same ID and content hash is skipped. Identical content under another ID is deduplicated. The same ID with different content blocks all writes. A retired or replaced tombstone updates an existing predecessor only when its `previous_content_hash` matches the target predecessor's content hash. If that predecessor is absent, the tombstone is retained so an older active bundle cannot resurrect it later. Target-local revisions are never overwritten silently.

## Capability packs and overlays

Core Project OS owns lifecycle and state. Packs add guidance only where a boundary changes implementation or verification decisions.

| Pack | Boundary |
| --- | --- |
| `service` | APIs, workers, queues, authentication, integrations and distributed outcomes |
| `web` | Browser UI, routing, accessibility, responsive behavior and browser-owned state |
| `mobile` | Application lifecycle, permissions, native handoffs, persistence and device evidence |
| `data` | Schemas, migrations, transactions, storage, deletion and restore |
| `delivery` | Builds, artifacts, deployment, runtime compatibility and release gates |

The `react-native-expo` overlay refines the `mobile` pack when exact repository signals exist. It does not replace pinned dependencies, platform behavior, official documentation or runtime evidence.

Languages and frameworks are detection signals, not behavioral profiles. Any justified pack combination is valid. Concrete dependency and configuration signals may recommend capabilities in any ecosystem: for example, recognized Clojure HTTP and database libraries can select `service` and `data`, while a bare Clojure manifest selects neither pack merely because the language is present.

## Helper summary

| Command | Writes | Purpose |
| --- | --- | --- |
| `detect` | No | Inspect toolchain and capability signals |
| `init` | Unless `--dry-run` | Create Standard |
| `adopt` | Unless `--dry-run` | Attach to compatible existing owners |
| `check` | No | Validate structure, lifecycle, archive hashes and release alignment |
| `sync-knowledge` | No | Explain the migration from deprecated synchronization language to explicit user-owned import |
| `upgrade` | Unless `--dry-run` | Migrate to the installed release with caught-failure rollback |
| `knowledge list` | No | List project knowledge, reusable knowledge or both |
| `knowledge approve` | Unless `--dry-run` | Add reviewed proposal entries to the reusable registry |
| `knowledge export` | Unless `--dry-run` | Create a deterministic portable bundle |
| `knowledge import` | Unless `--dry-run` | Import reviewed entries from a repository or bundle |
| `knowledge revise` | Unless `--dry-run` | Replace one entry through a reviewed proposal |
| `knowledge retire` | Unless `--dry-run` | Retire one entry with a reason |
| `knowledge remove` | Unless `--dry-run` | Permanently remove one local entry after exact confirmation |
| `program start` | Unless `--dry-run` | Validate a definition and start one Program |
| `program status` | No | Report active Program state |
| `program close` | Unless `--dry-run` | Close and archive one Program |

Every command requires `--target`. Prefer an absolute repository path in automation. `.` is convenient only when Terminal is already at the intended repository root.

### Detect

**Run this in Terminal:**

~~~bash
python3 /absolute/path/to/project-os/scripts/project_os.py detect --target /path/to/repository
~~~

Detection reports toolchain signals plus recommended packs and overlays. It changes no files and never proves commands, authority, architecture or product requirements.

### Initialize Standard

Preview first.

**Run this in Terminal:**

~~~bash
python3 /absolute/path/to/project-os/scripts/project_os.py init --target /path/to/repository --packs auto --overlays auto --dry-run
~~~

Apply only the identical reviewed operation without `--dry-run`.

**Run this in Terminal:**

~~~bash
python3 /absolute/path/to/project-os/scripts/project_os.py init --target /path/to/repository --packs auto --overlays auto
~~~

`init` always creates Standard and never creates `PROGRAM.md`. It refuses an existing Project OS owner, but preserves non-conflicting unrelated content such as `.agents/plugins`.

For an existing root `AGENTS.md`, first add and review the minimum routes to `.agents/CONTEXT.md` and `.agents/STATE.md`, then preview with the narrow preservation flag.

**Run this in Terminal:**

~~~bash
python3 /absolute/path/to/project-os/scripts/project_os.py init --target /path/to/repository --packs auto --overlays auto --allow-existing-agents --dry-run
~~~

Apply the same command without `--dry-run`. The flag never permits overwriting instructions.

### Adopt

Include `--inventory` when older Markdown lessons need explicit coverage.

**Run this in Terminal:**

~~~bash
python3 /absolute/path/to/project-os/scripts/project_os.py adopt --target /path/to/repository --inventory --dry-run
~~~

Apply only when the output reports `safe_to_adopt: true`, the mapping is correct and no project-owned destination is listed for modification.

**Run this in Terminal:**

~~~bash
python3 /absolute/path/to/project-os/scripts/project_os.py adopt --target /path/to/repository --inventory
~~~

Adoption fails closed on ambiguous owners, unsafe paths, incomplete legacy knowledge coverage and occupied managed destinations.

### Check

**Run this in Terminal:**

~~~bash
python3 /absolute/path/to/project-os/scripts/project_os.py check --target /path/to/repository
~~~

The command is read-only. Success prints `Project OS check: PASS` and exits zero. Use `--config /path/to/proposed-SYSTEM.json` to validate an adoption manifest before installing it.

### List knowledge

**Run this in Terminal:**

~~~bash
python3 /absolute/path/to/project-os/scripts/project_os.py knowledge list --target /path/to/repository --scope reusable
~~~

`--scope` accepts `project`, `reusable` or `all`. Listing is read-only.

### Approve a prepared proposal

The semantic `knowledge prepare` workflow creates and reviews the proposal outside the helper. The helper validates the selected proposal entries and writes only the approved set.

~~~bash
python3 /absolute/path/to/project-os/scripts/project_os.py knowledge approve --target /path/to/repository --proposal /path/to/proposal.json --ids FAIL-001,FAIL-002 --dry-run
~~~

Use `--all` instead of `--ids` only when the user reviewed and approved every proposal entry. Apply the identical operation without `--dry-run`, then run `check`.

### Export reusable knowledge

Preview a selected export:

~~~bash
python3 /absolute/path/to/project-os/scripts/project_os.py knowledge export --target /path/to/source-repository --output /path/to/failure-knowledge.json --dry-run
~~~

With no selector the helper exports every non-draft entry: active lessons plus retired and replaced tombstones. Use `--ids FAIL-001,FAIL-002` for an exact set. Every export must contain each linked predecessor and replacement record required for a complete lifecycle chain. `--active-only` excludes tombstones and is valid only when the selected active lessons have no lifecycle dependencies. The flags can be combined. Apply the same operation without `--dry-run`. The output must resolve outside the source repository and its path must not already exist. The source repository does not change and the helper reports the deterministic bundle SHA-256.

### Import reusable knowledge

The source can be a connected Project OS repository or a canonical portable bundle:

~~~bash
python3 /absolute/path/to/project-os/scripts/project_os.py knowledge import --target /path/to/destination --source /path/to/source-repository --dry-run
~~~

With no selection flag, import previews active entries applicable to the destination plus retired and replaced tombstones regardless of applicability. Use `--ids FAIL-001,FAIL-002` for an exact reviewed set or `--all` to explicitly consider every non-draft source entry. Apply only the same clean command without `--dry-run`, run `check`, then repeat the import dry run to prove idempotency. The source is always read-only.

### Revise, retire or remove

Revision consumes a reviewed one-entry proposal:

~~~bash
python3 /absolute/path/to/project-os/scripts/project_os.py knowledge revise --target /path/to/repository --id FAIL-001 --proposal /path/to/revision.json --dry-run
~~~

The proposal must use a new stable ID. Apply marks the old active entry `replaced`, links both entries and stores the predecessor hash needed for safe lifecycle import.

Retirement preserves the entry and its reason:

~~~bash
python3 /absolute/path/to/project-os/scripts/project_os.py knowledge retire --target /path/to/repository --id FAIL-001 --reason "Superseded by the supported platform API" --dry-run
~~~

Permanent local removal requires the same exact ID twice:

~~~bash
python3 /absolute/path/to/project-os/scripts/project_os.py knowledge remove --target /path/to/repository --id FAIL-001 --confirm FAIL-001 --dry-run
~~~

Each operation must be reviewed in dry-run form, applied unchanged and followed by `check`. Removal refuses any lesson that participates in a replacement chain because deleting either side would leave a dangling lifecycle link. Removing an unlinked local entry does not recall copies already imported into another repository.

### Deprecated synchronization command

**Run this in Terminal:**

~~~bash
python3 /absolute/path/to/project-os/scripts/project_os.py sync-knowledge --target /path/to/repository
~~~

This compatibility command is read-only. It explains that there is no centrally managed failure knowledge source and directs the user to `knowledge import --source`. Use `upgrade` to update Project OS product guidance, packs, overlays, schema and metadata.

### Upgrade

**Run this in Terminal:**

~~~bash
python3 /absolute/path/to/project-os/scripts/project_os.py upgrade --target /path/to/repository --dry-run
~~~

For an ordinary connected repository, apply the same command without `--dry-run`. The upgrade combines schema migration, managed guidance, user-owned knowledge classification and `SYSTEM.json` changes in one conflict-checked transaction. A conflict aborts all writes. Caught write and final-validation failures roll back completed changes. Applying a clean upgrade finishes by running the checker.

The schema 3 to 4 migration removes unchanged release-managed seed entries. Entries proven as user-owned through adoption coverage become reusable lessons. Private entries remain project-local. Compatible unknown or locally modified former shared entries become `draft` with `source.kind: migration-review-required`. If classifying any retained local entry would discard lifecycle metadata or unsupported user fields, upgrade refuses the entire transaction and reports the affected lesson and fields. Drafts require explicit preparation and approval before export.

A schema 2 repository with a legacy `PROGRAM.md` requires explicit classification.

**Run this in Terminal for an active legacy Program:**

~~~bash
python3 /absolute/path/to/project-os/scripts/project_os.py upgrade --target /path/to/repository --legacy-program-state active --dry-run
~~~

The applying form preserves the active editable contract, records its legacy origin and migration date, leaves the unprovable Program start date null and enters Program mode.

**Run this in Terminal for a closed legacy Program:**

~~~bash
python3 /absolute/path/to/project-os/scripts/project_os.py upgrade --target /path/to/repository --legacy-program-state closed --disposition stopped --closed-on 2026-09-07 --reason "Initiative ended before this migration" --dry-run
~~~

Use `--disposition completed` only when completion evidence exists. `stopped` requires `--reason`. Every closed legacy migration requires `--closed-on YYYY-MM-DD`. This is the actual historical closure date, not the upgrade date. Codex derives it only from repository evidence and stops if it cannot be established. A closed migration archives the exact legacy Program bytes. Remove only `--dry-run` after reviewing the complete preview.

`--closed-on` is valid only with `--legacy-program-state closed`. Current-schema upgrades and active legacy migrations reject it.

The Codex shortcut `$project-os upgrade` inspects repository evidence and selects these flags. If legacy state cannot be determined, it stops for a decision.

### Start a Program

Codex normally prepares the definition file from verified repository evidence. Direct helper use requires a JSON file matching the Program definition table above.

**Run this in Terminal:**

~~~bash
python3 /absolute/path/to/project-os/scripts/project_os.py program start --target /path/to/repository --definition /path/to/program-definition.json --dry-run
~~~

Apply the same reviewed command without `--dry-run`. The helper requires Standard mode, no active Program and a complete definition. It creates no plan and no empty history scaffold. History appears when the first Program is archived.

### Program status

**Run this in Terminal:**

~~~bash
python3 /absolute/path/to/project-os/scripts/project_os.py program status --target /path/to/repository
~~~

This command is read-only.

### Close a Program

Preview a completed closure.

**Run this in Terminal:**

~~~bash
python3 /absolute/path/to/project-os/scripts/project_os.py program close --target /path/to/repository --disposition completed --dry-run
~~~

Preview a stopped closure with its required reason.

**Run this in Terminal:**

~~~bash
python3 /absolute/path/to/project-os/scripts/project_os.py program close --target /path/to/repository --disposition stopped --reason "Initiative replaced by another approach" --dry-run
~~~

Closure fails while any plan is active. Apply only the reviewed command without `--dry-run`. The helper archives exact bytes, creates the history README on first closure, updates the history index and returns the repository to Standard as one transaction. It does not semantically validate completion evidence.

## Selection values

For `init`:

- `--packs auto` uses detected recommendations.
- `--packs none` selects no capability packs.
- `--packs service,web` selects an explicit comma-separated set.
- `--overlays auto` uses recommendations compatible with selected packs.
- `--overlays none` selects no overlays.
- `--overlays react-native-expo` requires `mobile`.

Knowledge import derives default applicability from the destination's selections in `SYSTEM.json`. Product guidance changes only through `upgrade`.

## Release and schema versions

Release and file-format versions are separate:

- Release 2.1.1 identifies the installed skill, helper, package metadata and connected `project_os_version`.
- `SYSTEM.schema_version` is 4.
- Knowledge registries retain their own `schema_version: 1`.
- Portable bundles use `format: project-os-reusable-knowledge` and `schema_version: 1`.
- The version in the external `$schema` URL inside `plugin.json` belongs to that external schema, not to the Project OS release.

The checker requires the repository release to match the installed helper and validates reusable entry content hashes independently of the release. Do not edit version or schema fields manually to silence it.

Upgrade rejects a repository release newer than the helper, including during a dry run. Use a matching or newer helper; implicit downgrade is unsupported. SemVer build metadata does not affect upgrade direction.

## Safety

- Managed paths remain repository-relative and free of symlink replacement boundaries.
- Multi-file operations use conflict and concurrency checks and fail closed.
- Writes require Python 3.9+ on a POSIX host with directory-descriptor operations, such as macOS or Linux. Unsupported write environments fail before mutation; there is no unsafe fallback.
- Create, replace, delete and rollback use opened directory descriptors and no-follow file opens. Detected parent replacement aborts the transaction; rollback uses the original directories.
- SYSTEM, knowledge and history JSON are parsed and hashed from the same bytes. Program closure also guards the plan registry through final validation, including closed legacy migration.
- An abrupt process termination or power loss can interrupt a multi-file operation. Run the checker afterward and repair from Git or another reviewed source if it reports partial state.
- Reusable knowledge policy excludes credentials, personal data, private paths, every URL, evidence paths, deployment identifiers and copied project history. The helper rejects detected URL forms plus common detectable sensitive patterns. Human review is still required because automated screening cannot recognize every project name or contextual disclosure.
- The helper initiates no network request and uses only the Python standard library.
- Project OS grants no authority for application changes, dependency installation, deletion, Git operations, deployment, publication or external communication.
- A passing checker proves Project OS structural consistency, not application or production behavior.

See [Security](../SECURITY.md) for the reporting policy.
