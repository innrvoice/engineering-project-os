# How Project OS works

Project OS combines one reusable Codex skill, one visible repository contract and ordinary files. The
skill knows how to create and maintain the system. The repository files keep the working truth after a
conversation ends.

## What `$project-os` means

`$project-os` explicitly selects the installed `project-os` skill for the current user message. The
`$` is Codex skill-invocation syntax. It is not shell syntax, an environment variable, a Python
command or a mode that stays enabled.

**Type this in Codex chat:**

~~~text
$project-os check
~~~

- Result: Codex loads the Project OS instructions needed for this request and runs a read-only check.
- Files: none change.
- Proof: the response reports `Project OS check: PASS` or concrete errors.
- Skip it when: you want ordinary product or code work.

The words after the skill name are normal language. Project OS publishes short requests because they
are easy to remember, not because it implements a command parser.

| Message | Interpretation |
| --- | --- |
| `$project-os check` | Validate the current control plane without writing |
| `$project-os check only plan state` | Run the same check with extra focus |
| `$project-os проверь систему и ничего не меняй` | Read-only check expressed in Russian |
| `$project-os program status` | Report Program and current Project OS state |
| `$project-os make this better` | Ambiguous: explain choices or ask before any write |
| `$project-os fix the null check in the handler` | Ordinary code task: do not create Project OS records merely because the prefix is present |

Case, punctuation and explanatory sentences may vary. A clear user constraint such as
`do not change files` always keeps the request read-only. A variant is accepted when its intent is
clear. An ambiguous mutation is not guessed.

`$project-os help` is also always read-only. It returns every supported short request with its
purpose, required argument and examples, then distinguishes those chat requests from Terminal helper
commands.

This release disables implicit skill invocation. Ordinary chat does not silently activate the skill.

## What Codex loads

Codex uses progressive disclosure for skills. At task startup it sees a compact list of available
skill names and descriptions. When `$project-os` is present, Codex loads the complete `SKILL.md` for
that message. The skill then routes to the focused bootstrap, maintenance or knowledge reference
needed for the operation.

The repository has a separate instruction lifecycle. Codex discovers applicable `AGENTS.md` files
when a task starts. A root file can define project authority, working method and routes to durable
Project OS records. Instructions closer to the working directory can refine broader ones.

| Situation | Initial route | What happens next |
| --- | --- | --- |
| Explicit Project OS request | `$project-os`, then the installed skill | Codex follows the requested control-plane workflow |
| Ordinary repository request | Applicable `AGENTS.md` files | Codex reads only the state, plan, packs and knowledge relevant to the work |
| Direct helper use | Python command in Terminal | The helper performs only its deterministic operation |

The `.agents` directory is not a hidden database and is not loaded all at once for every message. Its
files matter because `AGENTS.md` routes Codex to them and each file owns a specific kind of truth.

## Installation and repository connection are different

Installing the standalone skill makes a reusable workflow available in one Codex profile. It does not
touch the repository open in the app.

Connecting a repository is a separate request. `$project-os bootstrap` creates a new Standard
control plane. `$project-os adopt` maps compatible records already present. Both inspect first,
preview changes and use the helper for deterministic structure.

After a new `AGENTS.md` is created or changed, start a fresh Codex task in that repository. The
already running task is not proof that the new startup instruction route works.

Installing the skill is not connecting a repository. Connecting a repository is not opening a plan.
Opening a plan is not starting a Program.

## Standard and Program

### Standard

Standard is the normal, complete state of a connected repository. It includes routing, context,
checkpoint state, just-in-time plans, findings, evidence, knowledge, capability packs and overlays.

Bootstrap always creates Standard. Standard can support a long task and many sequential plans. A
repository does not need a Program merely because work spans several Codex tasks.

### Program

Program is a temporary coordination layer above plans. Use it when one initiative has multiple
distinct phases or outcomes that need one shared contract.

A useful distinction:

| Work | Use |
| --- | --- |
| Fix one API pagination failure | Standard, usually without a plan |
| Implement one resumable authentication change | Standard plus one plan |
| Migrate authentication across API, workers, web and mobile through separate rollout phases | Program plus separate plans as needed |
| Maintain a repository for years | Standard, not one permanent Program |

A Program contract owns:

- the initiative name and observable outcome;
- explicit authority;
- at least two phases, each with an outcome and exit conditions;
- evidence requirements;
- cost boundaries;
- exclusions;
- overall exit conditions.

Nothing creates `PROGRAM.md` during bootstrap, adoption or ordinary work.

**Type this in Codex chat:**

~~~text
$project-os program start: migrate authentication across the API, workers, web and mobile without downtime
~~~

Codex inspects repository truth and prepares a complete definition. If material fields cannot be
verified or derived, it asks for the missing decision and does not write. Once the definition is
complete, the helper dry-runs the transition, Codex reviews it, the helper creates
`.agents/PROGRAM.md`, `SYSTEM.mode` becomes `program` and the checker runs.

Starting a Program does not create or activate a plan. Plans remain outcome-sized execution packages
inside the wider initiative.

**Type this in Codex chat:**

~~~text
$project-os program status
~~~

This is read-only. It reports the Program contract, current phase, related plan state and unresolved
exit conditions from repository evidence.

A Program can close only when no plan is active.

**Type this in Codex chat:**

~~~text
$project-os program close completed
~~~

Use `completed` only when the Program's exit evidence exists. Use
`$project-os program close stopped: <reason>` when the initiative is deliberately discontinued.

Closing preserves the exact Program contract under
`.agents/history/programs/<program-id>/PROGRAM.md`, records its disposition and SHA-256 digest in
`.agents/history/index.json`, removes the active `.agents/PROGRAM.md` and returns
`SYSTEM.mode` to `standard`. The first closure also creates `.agents/history/README.md`.

Whether evidence actually proves the Program outcome is a user and Codex judgment. The helper checks
the structural lifecycle and refuses closure while a plan is active; it cannot verify the meaning of
product, deployment or external evidence.

## What the records own

- `AGENTS.md` owns startup routing, authority and working rules.
- `.agents/SYSTEM.json` owns release, schema, mode, active Program identity, path mappings, selected
  capabilities and managed baselines.
- `.agents/CONTEXT.md` owns durable verified facts and exact commands.
- `.agents/STATE.md` owns the current checkpoint and exact next action.
- `.agents/plans/` owns resumable outcome packages and execution status.
- `.agents/findings/` owns concrete defects, candidates and accepted risks.
- `.agents/evidence/` stores sanitized proof referenced by an owning record.
- `.agents/knowledge/project/` owns confirmed repository-specific lessons.
- `.agents/knowledge/shared/` owns sanitized portable failure mechanisms.
- `.agents/packs/` contains managed capability and ecosystem guidance.
- `.agents/PROGRAM.md` exists only while one Program is active.
- `.agents/history/` contains the Program history index and closed snapshots when they exist.

Do not duplicate one status in several files. `STATE.md` is a handoff, not a diary.
`CONTEXT.md` is not an active task list.

## What the helper does

The helper provides deterministic operations:

- `detect` inspects stack and capability signals.
- `init` creates a Standard control plane.
- `adopt` validates and maps compatible existing owners.
- `check` validates paths, registries, state invariants, archive hashes, managed baselines and
  version alignment.
- `sync-knowledge` synchronizes managed guidance and seed lessons without overwriting conflicts.
- `upgrade` conflict-checks and migrates supported repository state to the installed release, rolling
  back completed changes when a caught write or final-validation failure occurs.
- `program start`, `program status` and `program close` manage the Program lifecycle.

The helper does not infer product requirements, invent authority, write a real implementation plan,
confirm a finding or turn a source check into production evidence. Codex and the user make those
judgments from current evidence.

### The mutation sequence

A clear mutating short request causes Codex to:

1. Inspect Git state, applicable instructions and the current Project OS records.
2. Prepare the intended operation and run the helper with `--dry-run` when available.
3. Review every proposed write and stop on ambiguity, stale state or conflict.
4. Apply the same clean operation.
5. Run `check` and report the diff and remaining unverified boundaries.

For plan, finding or knowledge edits that are reasoned record updates rather than a dedicated helper
subcommand, Codex still prepares and validates the intended record change before writing, then runs the
checker.

## What tamper-evident history means

The Program archive is ordinary repository content. On close, the helper copies the exact
`PROGRAM.md` bytes and records their SHA-256 digest. The checker recomputes that digest and requires
every indexed archive path to exist.

This catches an uncoordinated edit, deletion or substitution. It does not make a file technically
immutable, prevent a person from rewriting both the file and its index, provide a cryptographic
signature or replace Git hosting controls. Git remains the review and distribution mechanism.

History is available to Standard and Program states. It is created when the first Program closes or
when compatible indexed history is adopted. Starting the first Program creates no empty history
scaffold. Archived snapshots never become current authority.

## What is not running in the background

Project OS has no:

- daemon or watcher;
- MCP server or remote service;
- lifecycle hook;
- hidden database;
- automatic upload;
- automatic Git operation;
- automatic cross-project synchronization.

No repository learns from another repository by itself. A portable failure lesson moves only after
deliberate sanitization, inclusion in a reviewed Project OS release and an explicit repository
upgrade. Local additions and conflicts remain visible for review.

## Versions and upgrades

The installed helper defines the Project OS release version. Release 2.0.0 uses
`SYSTEM.schema_version: 3` and `SYSTEM.mode: standard|program`. Knowledge registries have their own
schema version.

Updating the skill does not update repositories. `$project-os upgrade` inspects the old state,
previews every managed file change, preserves project-owned records, aborts on managed conflicts,
applies only a clean preview with caught-failure rollback and runs the checker.

When developing Project OS itself, the installed stable skill governs the workflow while the candidate
helper is developed and tested from the source checkout. Do not replace the installed skill with a
mutable candidate. Install only a published versioned tag, then start a fresh Codex task.

## Authority and safety

Project OS narrows where engineering state lives. It does not broaden what Codex may do. Application
edits, dependency installation, deletion, Git operations, deployment, publication and external
communication still require user authority and must follow repository instructions.

A passing Project OS checker proves structural consistency. It does not prove application correctness,
artifact identity, deployment state, production behavior or manual and physical acceptance.

For Codex behavior outside this project, see OpenAI's documentation for
[skills](https://learn.chatgpt.com/docs/build-skills) and
[`AGENTS.md`](https://learn.chatgpt.com/docs/agent-configuration/agents-md).

## Next

- [Install or connect a repository](SETUP.md)
- [Use Project OS day to day](USAGE.md)
- [Read the technical reference](REFERENCE.md)
