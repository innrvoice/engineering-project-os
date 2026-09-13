# Technical reference

This page is the compact contract for Project OS 1.0.1. Start with [README](../README.md) if
`$project-os`, installation and repository connection are still new concepts.

## Public interfaces

Project OS exposes three interfaces:

| Interface | Used for | Invocation |
| --- | --- | --- |
| Codex skill | Reasoned bootstrap, maintenance and knowledge workflows | `$project-os` in Codex chat |
| Python helper | Deterministic detect, init, adopt, check and sync operations | `project_os.py` in Terminal |
| Repository records | Durable context, state, plans, findings, evidence and knowledge | Files under `AGENTS.md` and `.agents/` |

`$project-os` is an explicit skill mention for one user message. It is not a shell command and it does
not put Codex into a permanent mode. This release sets implicit invocation to false.

The Python helper lives inside the installed skill at `scripts/project_os.py`. Paths in the examples
below are placeholders for that installed skill path or a checkout of this repository.

## Modes

| Mode | Use it for | Adds |
| --- | --- | --- |
| Lite | Default engineering work | Routing, context, checkpoint, just-in-time plans, findings, evidence, packs and knowledge |
| Full | An approved multi-phase audit, migration, release program or similar initiative | Everything in Lite plus `PROGRAM.md` and an immutable history boundary |

Full mode is not a more powerful default. Choose it only when the program contract and history have a
real owner and exit condition.

## Capability packs and overlays

Core Project OS owns state, plans, findings, evidence and knowledge lifecycle. Packs add guidance only
for boundaries that change implementation or verification decisions.

| Pack | Boundary |
| --- | --- |
| `service` | APIs, workers, queues, authentication, external integrations and distributed outcomes |
| `web` | Browser UI, routing, accessibility, responsive behavior and browser-owned state |
| `mobile` | Application lifecycle, permissions, native handoffs, persistence and device evidence |
| `data` | Schemas, migrations, transactions, storage, deletion and restore |
| `delivery` | Builds, artifacts, deployment, runtime compatibility and release gates |

The `react-native-expo` overlay refines the `mobile` pack for matching repositories. It requires the
mobile pack. An overlay never replaces pinned dependencies, platform behavior, official documentation
or current runtime evidence.

Languages and frameworks are detection signals, not behavioral profiles. A repository can select any
combination of packs justified by its actual boundaries.

## Record ownership

| Path | Owns |
| --- | --- |
| `AGENTS.md` | Startup routing, authority, working method, safety and verification expectations |
| `.agents/SYSTEM.json` | Project OS release, schema, mode, installation type, mappings, selections and managed baselines |
| `.agents/CONTEXT.md` | Durable verified facts, authority, architecture and exact commands |
| `.agents/STATE.md` | Current scope, verified progress, exact next action and blockers |
| `.agents/plans/index.json` | Canonical execution state and plan statuses |
| `.agents/plans/NNN-*.md` | One observable outcome, its work and acceptance evidence |
| `.agents/findings/findings.json` | Concrete defects, candidates and accepted risks |
| `.agents/evidence/` | Sanitized, dated evidence linked from plans or findings |
| `.agents/knowledge/project/` | Confirmed lessons that remain repository or environment specific |
| `.agents/knowledge/shared/failures.json` | Sanitized failure mechanisms that can be reused |
| `.agents/packs/` | Managed capability and ecosystem guidance selected for this repository |
| `.agents/PROGRAM.md` | Approved Full-mode multi-phase contract |
| `.agents/history/` | Full-mode immutable snapshots, never current authority |

Do not duplicate one status across several records. `STATE.md` is a handoff, not a diary. `CONTEXT.md`
is not an active task list. Evidence is linked from the record whose claim it supports.

## State invariants

Plan statuses are:

- `planned`
- `active`
- `blocked`
- `done`
- `superseded`

When `execution_state` is `running`, exactly one plan is `active`. If `active_plan` is present, it must
name that plan. When no plan is active, execution state is `idle` and `active_plan`, when present, is
`null`.

Finding statuses are:

- `candidate`
- `confirmed`
- `fixed_unverified`
- `verified`
- `accepted_risk`
- `deferred`
- `rejected`
- `merged`

Failure knowledge statuses are `active`, `retired` and `replaced`.

A status transition does not manufacture evidence. In particular, `done` and `verified` require the
evidence class named by the owning record.

## Helper command summary

| Command | Writes | Purpose |
| --- | --- | --- |
| `detect` | No | Inspect toolchain and capability signals |
| `init` | Yes, unless `--dry-run` | Create a new Lite or Full control plane |
| `adopt` | Yes, unless `--dry-run` | Map and attach to compatible existing records |
| `check` | No | Validate structure, mappings, registries, paths, managed baselines and release alignment |
| `sync-knowledge` | Yes, unless `--dry-run` | Synchronize selected managed guidance and seed knowledge without overwriting conflicts |

Every command requires `--target`. Use an absolute repository path in automation. `.` is convenient
only when Terminal is already at the intended repository root.

### Detect

**Run this in Terminal:**

~~~bash
python3 /absolute/path/to/project-os/scripts/project_os.py detect --target /path/to/repository
~~~

- Result: the helper reports detected toolchain signals plus recommended packs and overlays.
- Files: none change.
- Proof: review the structured output and confirm each recommendation against repository evidence.
- Skip it when: a recent reviewed detection already exists and relevant tool configuration has not
  changed.

Detection never proves commands, authority, architecture or product requirements.

### Initialize a clean repository

Preview first.

**Run this in Terminal:**

~~~bash
python3 /absolute/path/to/project-os/scripts/project_os.py init --target /path/to/repository --mode lite --packs auto --overlays auto --dry-run
~~~

- Result: the command lists the proposed Lite-mode files and automatic selections without writing.
- Files: none change.
- Proof: review every proposed create and confirm the pack and overlay selections.
- Skip it when: `AGENTS.md` or `.agents` already exists.

Apply the exact reviewed selection by removing only `--dry-run`.

**Run this in Terminal:**

~~~bash
python3 /absolute/path/to/project-os/scripts/project_os.py init --target /path/to/repository --mode lite --packs auto --overlays auto
~~~

- Result: the helper creates the missing Lite-mode records.
- Files: root `AGENTS.md` and `.agents` are created. Application files do not change.
- Proof: compare the applied files with the dry run, fill repository-specific truth and run `check`.
- Skip it when: the preview was not reviewed or repository state changed after the preview.

`init` refuses any existing `.agents` tree. It also refuses an existing root `AGENTS.md` unless the
file already routes to `.agents/CONTEXT.md` and `.agents/STATE.md` and the explicit preservation flag
is supplied.

### Initialize while preserving `AGENTS.md`

Review and add the two required routes before running this command.

**Run this in Terminal:**

~~~bash
python3 /absolute/path/to/project-os/scripts/project_os.py init --target /path/to/repository --mode lite --packs auto --overlays auto --allow-existing-agents --dry-run
~~~

- Result: the helper validates that existing root instructions route to both required records, then
  previews creation of the remaining control plane.
- Files: none change.
- Proof: review every proposed create and confirm that `AGENTS.md` is preserved.
- Skip it when: `.agents` already exists or either required route is absent.

`--allow-existing-agents` is a narrow preservation gate, not permission to overwrite instructions.

Apply the same reviewed command without `--dry-run`.

**Run this in Terminal:**

~~~bash
python3 /absolute/path/to/project-os/scripts/project_os.py init --target /path/to/repository --mode lite --packs auto --overlays auto --allow-existing-agents
~~~

- Result: the helper preserves the routed root instructions and creates the remaining control plane.
- Files: `AGENTS.md` is unchanged and missing `.agents` records are created.
- Proof: the output says `existing AGENTS.md preserved`, then `check` passes.
- Skip it when: the preview was not reviewed or repository state changed after the preview.

### Adopt compatible existing records

Include `--inventory` when the repository contains older Markdown lessons that need explicit coverage.

**Run this in Terminal:**

~~~bash
python3 /absolute/path/to/project-os/scripts/project_os.py adopt --target /path/to/repository --dry-run --inventory
~~~

- Result: the helper discovers candidate record owners, validates them and reports mappings,
  conflicts, planned creates and legacy knowledge inventory.
- Files: none change.
- Proof: require `safe_to_adopt: true` and no existing files listed as modified.
- Skip it when: the repository has no compatible context, state, plan or finding owners.

Adoption fails closed on ambiguous owners, missing required routing, unsafe paths, incomplete legacy
knowledge coverage and occupied managed destinations.

Apply the reviewed adoption without `--dry-run`.

**Run this in Terminal:**

~~~bash
python3 /absolute/path/to/project-os/scripts/project_os.py adopt --target /path/to/repository --inventory
~~~

- Result: the helper rechecks its adoption preconditions and attaches Project OS to the mapped owners.
- Files: only the reviewed manifest, managed guidance and shared knowledge files are created.
- Proof: existing records are unchanged and `check` passes.
- Skip it when: the preview reported an error or repository state changed after the preview.

### Check

**Run this in Terminal:**

~~~bash
python3 /absolute/path/to/project-os/scripts/project_os.py check --target /path/to/repository
~~~

- Result: the helper validates the active repository control plane without changing it.
- Files: none change.
- Proof: successful output is exactly headed by `Project OS check: PASS` and the process exits zero.
- Skip it when: do not skip after Project OS changes. It is optional after application-only work that
  leaves all control-plane records untouched.

Use `--config /path/to/proposed-SYSTEM.json` to validate an adoption manifest before placing it at
`.agents/SYSTEM.json`.

### Synchronize managed guidance and knowledge

Always preview.

**Run this in Terminal:**

~~~bash
python3 /absolute/path/to/project-os/scripts/project_os.py sync-knowledge --target /path/to/repository --dry-run
~~~

- Result: the helper previews the installed release's managed guidance and shared seed knowledge.
- Files: none change.
- Proof: the output reports additions and updates with no guidance or knowledge conflicts.
- Skip it when: the connected repository already matches the installed release and its selected
  managed content.

Apply and validate only after reviewing the clean preview.

**Run this in Terminal:**

~~~bash
python3 /absolute/path/to/project-os/scripts/project_os.py sync-knowledge --target /path/to/repository
python3 /absolute/path/to/project-os/scripts/project_os.py check --target /path/to/repository
~~~

- Result: the helper applies the reviewed managed update and immediately validates the repository.
- Files: managed pack or overlay files, shared knowledge and managed metadata in `SYSTEM.json` may
  change. Project-owned records remain untouched.
- Proof: the final command prints `Project OS check: PASS`.
- Skip it when: the preview reported any conflict or repository state changed after the preview.

An existing managed file is updated only when it still matches its recorded baseline. A locally
divergent managed file or entry produces a conflict and aborts synchronization before partial writes.
Entries outside the selected upstream set are retained when their structure and provenance are valid.

## Selection values

For `init`:

- `--packs auto` uses detected recommendations.
- `--packs none` selects no capability packs.
- `--packs service,web` selects an explicit comma-separated set.
- `--overlays auto` uses detected recommendations compatible with selected packs.
- `--overlays none` selects no overlays.
- `--overlays react-native-expo` selects the current explicit overlay and requires `mobile`.

For `sync-knowledge`, omitted selection flags use the selections already stored in `SYSTEM.json`.
Explicit sync selections must exactly match that manifest.

## Release version and schema version

Project OS release version and file-format schema version are different values:

- Release `1.0.1` identifies the installed skill, helper, package metadata, connected
  `project_os_version` and managed knowledge provenance.
- `SYSTEM.schema_version` remains `2` until the manifest format itself changes.
- Knowledge registries currently use their own `schema_version: 1`.
- The version in the external `$schema` URL inside `plugin.json` belongs to the Agent Plugins schema,
  not to the Project OS release.

The helper's release constant is authoritative for generated and checked Project OS versions. The
checker rejects a connected repository whose `project_os_version` or managed `knowledge_version` does
not match it.

## Managed and project-owned content

Project OS records hashes for managed pack guidance and managed seed knowledge. This lets the helper
update an unchanged baseline and refuse a locally divergent one.

These records remain project-owned and are never replaced by synchronization:

- `AGENTS.md`
- `CONTEXT.md`
- `STATE.md`
- plans and plan index
- findings
- evidence
- project knowledge
- Full-mode program and history

Resolve a managed conflict by deciding whether the local content belongs in project-owned guidance,
should be contributed upstream or should be deliberately restored to the release baseline. Do not
choose text merely because it has a newer date.

## Evidence classes

Project OS keeps source, static, unit, local integration, hosted, artifact, production,
owner-reported, manual and physical evidence distinct. A passing checker proves Project OS structural
consistency only.

## Safety constraints

- Managed paths must remain safe, repository-relative and free of symlink replacement boundaries.
- Writes use conflict and concurrency checks and fail closed where ownership is unclear.
- Shared knowledge must not contain credentials, personal data, private machine paths, private URLs,
  signed URLs or copied project history.
- The helper initiates no network request and uses only the Python standard library.
- Project OS grants no authority for application changes, dependency installation, deletion, Git
  operations, deployment, publication or external communication.

See [Security](../SECURITY.md) for reporting and supported-version policy.
