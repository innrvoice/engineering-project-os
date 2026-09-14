# Reference

This is the technical contract for Project OS 2.0.4. Start with the [README](../README.md) if installation, plugin invocation or repository connection is still new.

## Interfaces

| Interface | Used for | Invocation |
| --- | --- | --- |
| ChatGPT plugin | Setup advice from a project description and workflows over files supplied in the conversation | `@Engineering Project OS ...` with the needed project context |
| Codex plugin or standalone skill | Reasoned workflows in the selected local workspace | `$project-os ...` in Codex chat |
| Python helper | Deterministic detect, init, adopt, check, sync, upgrade and Program transitions | `project_os.py ...` in Terminal |
| Repository records | Durable context, state, plans, findings, evidence and knowledge | `AGENTS.md` and `.agents/` files |

`@Engineering Project OS` in ChatGPT and `$project-os` in Codex select the same bundled skill for one message. Text after the selector is natural language, not a helper command line or rigid parser. This release enables implicit invocation so the selected plugin can expose the skill for a clear Project OS request.

Installation and repository access are separate. ChatGPT can use only the project description and files available in the chat. Choosing a setup or creating a starter package can begin from a description. Reviewing an existing setup requires its actual Project OS files. Codex can use the local workspace selected for the task. Neither surface gains repository access from installation alone.

The ChatGPT Directory listing exposes three outcome-focused starter prompts:

| Starter prompt | Required initial context |
| --- | --- |
| `Help me choose the right Project OS setup for my project.` | Project description or relevant files |
| `Create a safe Project OS starter package for my project.` | Project description and any existing authority files |
| `Review my existing Project OS setup and tell me what to fix.` | Existing `AGENTS.md` and `.agents/` files or a relevant project bundle |

The helper lives at `scripts/project_os.py` inside the installed skill. Terminal examples use an absolute placeholder path so the target repository does not need its own helper copy.

## Project OS requests

| Shortcut | Required argument | Behavior |
| --- | --- | --- |
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
| `knowledge propose-shared: <lesson-id>` | Project lesson ID | Draft a sanitized portable lesson without writing |

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
| `.agents/SYSTEM.json` | Release, schema, state, active Program, mappings, selections and managed baselines |
| `.agents/CONTEXT.md` | Durable verified facts, authority, architecture and exact commands |
| `.agents/STATE.md` | Current scope, verified progress, exact next action and blockers |
| `.agents/plans/index.json` | Canonical execution state and plan statuses |
| `.agents/plans/NNN-*.md` | One observable outcome, its work and acceptance evidence |
| `.agents/findings/findings.json` | Concrete defects, candidates and accepted risks |
| `.agents/evidence/` | Sanitized, dated evidence linked from plans or findings |
| `.agents/knowledge/project/` | Confirmed repository-specific lessons |
| `.agents/knowledge/shared/failures.json` | Sanitized portable failure mechanisms |
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

Failure knowledge statuses are `active`, `retired` and `replaced`.

A status transition does not manufacture evidence. `done`, `verified` and completed Program closure require the evidence class named by the owning record.

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
| `sync-knowledge` | Unless `--dry-run` | Synchronize managed guidance and seed knowledge |
| `upgrade` | Unless `--dry-run` | Migrate to the installed release with caught-failure rollback |
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

### Synchronize managed guidance and knowledge

**Run this in Terminal:**

~~~bash
python3 /absolute/path/to/project-os/scripts/project_os.py sync-knowledge --target /path/to/repository --dry-run
~~~

A locally divergent managed file or knowledge entry is a conflict. Synchronization aborts before partial writes. The repository must already match the helper's Project OS release; synchronization does not perform an upgrade. Apply only a clean preview.

**Run this in Terminal:**

~~~bash
python3 /absolute/path/to/project-os/scripts/project_os.py sync-knowledge --target /path/to/repository
python3 /absolute/path/to/project-os/scripts/project_os.py check --target /path/to/repository
~~~

Project-owned context, state, plans, findings, evidence and project knowledge are never replaced by this command.

### Upgrade

**Run this in Terminal:**

~~~bash
python3 /absolute/path/to/project-os/scripts/project_os.py upgrade --target /path/to/repository --dry-run
~~~

For an ordinary connected repository, apply the same command without `--dry-run`. The upgrade combines schema migration, managed guidance, shared knowledge and `SYSTEM.json` changes in one conflict-checked transaction. A conflict aborts all writes. Caught write and final-validation failures roll back completed changes. Applying a clean upgrade finishes by running the checker.

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

For `sync-knowledge`, omitted selection flags use `SYSTEM.json`. Explicit selections must match it.

## Release and schema versions

Release and file-format versions are separate:

- Release 2.0.4 identifies the installed skill, helper, package metadata, connected `project_os_version` and managed knowledge provenance.
- `SYSTEM.schema_version` is 3.
- Knowledge registries retain their own `schema_version: 1`.
- The version in the external `$schema` URL inside `plugin.json` belongs to that external schema, not to the Project OS release.

The checker requires the repository release and shared knowledge version to match the installed helper. Do not edit version fields manually to silence it.

Upgrade rejects a repository release newer than the helper, including during a dry run. Use a matching or newer helper; implicit downgrade is unsupported. SemVer build metadata does not affect upgrade direction.

## Safety

- Managed paths remain repository-relative and free of symlink replacement boundaries.
- Multi-file operations use conflict and concurrency checks and fail closed.
- Writes require Python 3.9+ on a POSIX host with directory-descriptor operations, such as macOS or Linux. Unsupported write environments fail before mutation; there is no unsafe fallback.
- Create, replace, delete and rollback use opened directory descriptors and no-follow file opens. Detected parent replacement aborts the transaction; rollback uses the original directories.
- SYSTEM, knowledge and history JSON are parsed and hashed from the same bytes. Program closure also guards the plan registry through final validation, including closed legacy migration.
- An abrupt process termination or power loss can interrupt a multi-file operation. Run the checker afterward and repair from Git or another reviewed source if it reports partial state.
- Shared knowledge policy excludes credentials, personal data, private paths, private URLs, signed URLs and copied project history. The helper rejects common detectable patterns; human review is still required because a denylist cannot prove arbitrary text is sanitized.
- The helper initiates no network request and uses only the Python standard library.
- Project OS grants no authority for application changes, dependency installation, deletion, Git operations, deployment, publication or external communication.
- A passing checker proves Project OS structural consistency, not application or production behavior.

See [Security](../SECURITY.md) for the reporting policy.
