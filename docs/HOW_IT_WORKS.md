# How Project OS works

Project OS is deliberately less magical than it may look from the prompt.

It combines one reusable Codex skill, one visible repository contract and a set of ordinary files.
The skill knows how to create and maintain the system. The repository files keep the truth after the
current conversation ends.

## What `$project-os` does

`$project-os` explicitly selects the installed `project-os` skill for the current user message. The
`$` is Codex skill-invocation syntax. It is not shell syntax, an environment variable or a command
language.

**Type this in Codex chat:**

~~~text
$project-os Check this repository's Project OS state. Do not change files.
~~~

- Result: Codex loads the full Project OS instructions and the reference needed for this request, then
  uses the bundled checker.
- Files: none should change.
- Proof: the response reports the checker result and concrete errors, if any.
- Skip it when: you want ordinary application work and the repository control plane is healthy.

The words after `$project-os` are a normal prompt. They can be short or detailed and can use any
language Codex understands.

This Project OS release disables implicit invocation. A request that happens to resemble Project OS
work does not silently activate the skill. Use `$project-os` when you want the workflow.

## What Codex loads

Codex uses progressive disclosure for skills. At task startup it sees a compact list of available
skill names and descriptions. When `$project-os` is present, it loads the complete `SKILL.md` for
that request. Project OS then directs it to the focused bootstrap, maintenance or knowledge reference
needed for the operation.

The repository has a different lifecycle. Codex discovers applicable `AGENTS.md` files when a task or
session starts. A root `AGENTS.md` can define the project's authority, working method and routes to
durable Project OS records. Instructions closer to the working directory can refine broader ones.

That produces two distinct paths:

| Situation | What Codex starts from | What happens next |
| --- | --- | --- |
| Explicit Project OS request | `$project-os`, then the installed skill | Codex follows the requested control-plane workflow |
| Ordinary repository request | Applicable `AGENTS.md` instructions | Codex reads only the state, plan, packs and knowledge relevant to the task |

The `.agents` directory is not a special hidden database and it is not loaded in full for every
message. Its files matter because `AGENTS.md` routes Codex to them and assigns each one a clear kind of
truth.

## Installation and repository connection are different

Installing the skill makes a reusable workflow available in the local Codex profile. It does not
touch the repository open in the app.

Connecting a repository is a separate `$project-os` request. Bootstrap creates a new control plane.
Adoption maps compatible records already present. Both operations inspect first and use the bundled
helper for deterministic structure.

After a new `AGENTS.md` is created or changed, start a fresh Codex task in that repository. Codex reads
the applicable instruction chain at task startup, so the already running task should not be treated
as proof that the new startup route works.

Installing the skill is not integrating a repository. Integrating a repository is not opening a
plan. Opening a plan is not completing the work.

## Ordinary chat after setup

You do not keep Project OS "turned on". Once the repository is connected, ask for normal engineering
work normally.

**Type this in Codex chat:**

~~~text
Trace why password reset sometimes reports success before the email job is accepted. Fix the verified
cause and run the focused service tests.
~~~

- Result: Codex follows `AGENTS.md`, checks current repository state and works on the requested code.
- Files: application code, tests and only those Project OS records whose durable truth changes may be
  updated.
- Proof: review the code diff, focused checks and any explicit unverified boundary.
- Skip it when: you intend to operate on Project OS itself, in which case invoke `$project-os`.

Use `$project-os` again when the object of the request is the control plane:

- bootstrap or adoption;
- consistency checking or repair;
- opening, checkpointing, blocking, completing or superseding a durable plan;
- registering a finding or promoting a confirmed failure lesson;
- synchronizing managed guidance and shared knowledge;
- upgrading the repository to the installed Project OS release.

A long product task can begin with `$project-os Open one plan for ...` when it must survive several
checkpoints. A bounded task should stay plan-free.

## The three layers

### 1. The installed skill

The skill contains workflow instructions, focused references, templates, capability guidance, seed
knowledge and the Python helper. It is reusable across repositories.

The skill does not contain the target project's product truth. It must inspect the repository before
recording authority, commands, architecture or acceptance requirements.

### 2. `AGENTS.md`

`AGENTS.md` is the repository entry route Codex understands automatically. It tells a new task where
current facts live, which checks are legitimate and which safety or authority rules apply.

Current user instructions still take precedence. Project OS does not turn `AGENTS.md` into a new
permission system.

### 3. `.agents`

The `.agents` tree holds visible, reviewable state:

- `SYSTEM.json` records the release, schema, mode, managed baselines and path mappings.
- `CONTEXT.md` records durable verified facts and commands.
- `STATE.md` records the current checkpoint and exact next action.
- `plans/` owns execution status and multi-session outcomes.
- `findings/` owns concrete defects, candidates and accepted risks.
- `evidence/` stores sanitized evidence linked from plans or findings.
- `knowledge/project/` keeps confirmed repository-specific lessons.
- `knowledge/shared/` keeps sanitized portable mechanisms.
- `packs/` contains selected capability and ecosystem guidance.
- Full mode also adds `PROGRAM.md` and `history/`.

These files can be inspected in a diff, reviewed by a team and committed when the team wants the same
workflow in every clone.

## What the Python helper does

The helper provides five deterministic operations:

- `detect` inspects stack and capability signals.
- `init` creates missing control-plane files for a new setup.
- `adopt` discovers and validates compatible existing owners.
- `check` validates paths, registries, invariants, managed baselines and version alignment.
- `sync-knowledge` synchronizes selected managed guidance and shared seed knowledge without
  overwriting local conflicts.

The helper does not reason about product requirements, write a real implementation plan, decide that
a finding is confirmed or turn a test result into production proof. Codex and the user make those
judgments from repository evidence.

It is also not a background process. It runs only when Codex or a person invokes it.

## What is not running in the background

Project OS has no:

- daemon or watcher;
- MCP server or remote service;
- lifecycle hook;
- hidden database;
- automatic upload;
- automatic Git operation;
- automatic cross-project synchronization.

No repository learns from another repository by itself. A shared failure lesson travels only when it
has been deliberately sanitized, included in a Project OS release and synchronized into a connected
repository. Local additions and conflicts are preserved for review.

## Versions and upgrades

The installed helper defines the Project OS release version. The same release is written to
`SYSTEM.project_os_version`, shared `knowledge_version`, bundled knowledge provenance and package
metadata. `schema_version` is a separate file-format version and does not change just because the
release version changes.

The checker requires the connected repository to match the installed helper. Updating the skill does
not silently update repository files. Run the explicit upgrade workflow in each repository. It
previews managed changes, refuses locally divergent managed content, applies a clean synchronization
and checks the result.

There is no Python `upgrade` subcommand. The skill coordinates the existing deterministic steps:

`inspect -> sync-knowledge --dry-run -> sync-knowledge -> check`

## Authority and safety

Project OS narrows where engineering state lives. It does not broaden what Codex is allowed to do.
Application edits, dependencies, deletion, Git operations, deployments, publication and external
communication still require authority from the current user and repository instructions.

Repository state is not automatically correct just because it is durable. Current code and current
external evidence can supersede an old checkpoint. Project OS makes that discrepancy visible; it does
not remove the need to verify it.

For Codex behavior outside this repository, see OpenAI's documentation for
[skills](https://learn.chatgpt.com/docs/build-skills.md) and
[`AGENTS.md`](https://learn.chatgpt.com/docs/agent-configuration/agents-md.md).

## Next

- [Install or connect a repository](SETUP.md)
- [Use Project OS day to day](USAGE.md)
- [Read the technical reference](REFERENCE.md)
