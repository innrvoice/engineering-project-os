<img src="assets/logo.svg" width="96" height="96" alt="Engineering Project OS logo">

# Engineering Project OS

The difficult part was rarely the first Codex task. It was the fifth one.

I would reopen a repository, reconstruct what had already been decided, search for the command that
had actually passed and try to remember which "done" item still needed a device, deployment or human
check. The code was still there. The working state was not.

Chat history is a poor project database.

Engineering Project OS keeps that working state in the repository. It adds a small, visible control
plane for durable context, current checkpoints, plans, findings, evidence and reusable failure
knowledge. A new Codex task can resume from verified repository state instead of treating an old
conversation as current truth.

It is stack-agnostic. A TypeScript frontend, Python service, Clojure backend, native mobile app or
mixed monorepo uses the same core system. Repository evidence selects only the capability guidance
that fits its real boundaries.

## Start with these requests

These are the normal Project OS entry points.

**Type this in Codex chat:**

~~~text
$project-os help
$project-os inspect
$project-os bootstrap
$project-os check
~~~

`$project-os` explicitly selects the installed `project-os` skill for one message. It is Codex skill
syntax, not a Terminal command, environment variable or permanent mode. The text after it is an
ordinary natural-language request. It can be short, detailed and written in any language.

The exact skill name is `project-os` with a hyphen. `$project os` is not the same invocation.

The examples above are recommended phrases, not a rigid command parser:

- `$project-os check` runs the same read-only workflow as a longer request to validate the current
  repository and report errors.
- `$project-os check only the plan registry` narrows that request.
- `$project-os проверь Project OS и ничего не меняй` expresses the same intent in Russian.
- An ambiguous request does not authorize a guess or a write. Codex explains the available requests
  or asks one focused question.
- An unrelated engineering request remains ordinary engineering work. The prefix is unnecessary and
  does not justify creating plans, findings or other Project OS records.

Every Project OS request that can change files follows the same safety sequence:

`inspect -> preview or helper dry-run -> apply only a clean result -> check`

## Standard is the system. Program is temporary.

Every connected repository starts in **Standard**. Standard is the complete everyday system:

- repository routing through `AGENTS.md`;
- durable context and the current checkpoint;
- just-in-time plans for work that must survive more than one task;
- findings, evidence and project-specific knowledge;
- managed capability packs, overlays and sanitized shared failure knowledge.

Bootstrap always creates Standard. It never creates `PROGRAM.md`.

A **Program** is a temporary umbrella contract for one explicitly started multi-phase initiative. It
is useful when several separate plans need one shared outcome, authority boundary, phase sequence,
evidence policy, cost boundary and exit condition.

For example, fixing one pagination bug is ordinary Standard work. Even a long implementation can stay
in Standard with one durable plan. Migrating authentication across an API, workers, web and mobile in
separate rollout phases may justify a Program.

**Type this in Codex chat:**

~~~text
$project-os program start: migrate authentication across the API, workers, web and mobile without downtime
~~~

- Result: Codex inspects the repository and prepares the Program contract. It creates
  `.agents/PROGRAM.md` only when the initiative, outcome, authority, phases, evidence, cost
  boundary, exclusions and overall exit conditions are sufficiently defined.
- Files: `.agents/PROGRAM.md` and Program metadata in `.agents/SYSTEM.json` may change. No history
  archive, plan or application code is created automatically.
- Proof: the repository is in `program` mode and the Project OS checker passes.
- Skip it when: one plan can own the outcome or the work has no genuine multi-phase coordination
  boundary.

Closing a Program archives its exact contract under `.agents/history/programs/` with a SHA-256 digest
recorded in the history index, then returns the repository to Standard. The checker can detect an
uncoordinated archive edit, deletion or substitution. This is tamper-evident Git-tracked history, not
technically immutable storage, a signature or a remote audit service.

## Install once, connect each repository once

Requirements:

- A Codex client with standalone skill support.
- Python 3.9 or newer for the deterministic helper.
- A local checkout of the target repository.

### 1. Install the standalone skill

`$skill-installer` is a separate built-in Codex skill. Send this message in Codex, not Terminal.

**Type this in Codex chat:**

~~~text
$skill-installer Install project-os from https://github.com/innrvoice/engineering-project-os/tree/v2.0.0/skills/project-os
~~~

- Result: Codex installs the versioned standalone skill in the local Codex profile.
- Files: only the user-level skill installation changes; the open repository does not.
- Proof: start a new Codex task and confirm that `project-os` is available.
- Skip it when: this exact release is already installed.

The documented installation route is the standalone skill from the versioned GitHub tag.

### 2. Inspect and connect a repository

Open the target repository in a new Codex task.

**Type this in Codex chat:**

~~~text
$project-os inspect
~~~

- Result: Codex reads existing instructions, Git state, documentation, CI, task runners, lockfiles and
  tool configuration. It recommends bootstrap, an `AGENTS.md`-preserving bootstrap or adoption.
- Files: none change.
- Proof: the response identifies the setup path, justified packs and overlays and the files that would
  change.
- Skip it when: the repository already passes `$project-os check` at the installed version.

For a new control plane, review the inspection and continue with:

**Type this in Codex chat:**

~~~text
$project-os bootstrap
~~~

Bootstrap creates Standard only. It preserves safe unrelated `.agents` namespaces such as
`.agents/plugins`, and it refuses to overwrite existing project authority. [Setup](docs/SETUP.md)
covers clean repositories, an existing `AGENTS.md` and adoption of compatible existing records.

### 3. Work normally

After setup, start a fresh Codex task so the repository's `AGENTS.md` enters the instruction chain.
Ordinary product and code work does not need `$project-os`.

**Type this in Codex chat:**

~~~text
Fix the pagination bug in the activity feed and run the focused tests.
~~~

Use `$project-os` again when the object of the request is Project OS itself: setup, validation,
repair, upgrade, Program lifecycle, durable plan state, findings or failure knowledge.

## What is actually installed

The installed skill contains reasoning instructions, focused references, templates, capability
guidance, seed knowledge and a deterministic Python helper. A connected repository contains visible
files under `AGENTS.md` and `.agents/`.

Codex discovers applicable `AGENTS.md` files when a task starts. Those instructions route it to the
specific `.agents` records needed for the current work. The entire directory is not inserted into
every prompt.

There is no Project OS daemon, watcher, MCP server, hidden database, automatic upload, automatic Git
operation or background cross-project synchronization. The helper runs only when explicitly invoked.
It does not decide product truth or grant authority to change application code, install dependencies,
commit, push, deploy or publish.

## Continue reading

- [Setup](docs/SETUP.md)
- [How it works](docs/HOW_IT_WORKS.md)
- [Usage](docs/USAGE.md)
- [Reference](docs/REFERENCE.md)
- [Changelog](CHANGELOG.md)
- [Contributing](CONTRIBUTING.md)
- [Security policy](SECURITY.md)
- [MIT License](LICENSE)
