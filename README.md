# Engineering Project OS

The difficult part was rarely the first Codex task. It was the fifth one.

I would reopen a repository, reconstruct what was already decided, search for the command that had
actually passed and try to remember which "done" item still needed a device, deployment or human
check. The code was still there. The working state was not.

Chat history is a poor project database.

Engineering Project OS keeps that working state in the repository. It adds a small control plane for
durable context, the current checkpoint, plans, findings, evidence and reusable failure knowledge. A
new Codex task can resume from verified repository state instead of pretending that an old
conversation is current truth.

It is stack-agnostic. A TypeScript frontend, Python service, Clojure backend, native mobile app or
mixed monorepo uses the same core system. Repository evidence selects only the capability guidance
that fits its real boundaries.

## First: what `$project-os` means

`$project-os` explicitly selects the installed `project-os` skill inside Codex. The `$` is Codex
skill-invocation syntax. It is not a Terminal command, an environment variable or a permanent mode.
It applies to the request where you use it. Everything after the skill name is ordinary language and
can be written in any language.

**Type this in Codex chat:**

~~~text
$project-os Check this repository's Project OS state. Do not change files.
~~~

- Result: Codex loads the Project OS workflow for this request and runs a read-only consistency check.
- Files: none should change.
- Proof: the response ends with a checker result and any concrete errors.
- Skip it when: you are asking for ordinary product or code work and the repository setup is healthy.

Most work should look like this instead.

**Type this in Codex chat:**

~~~text
Fix the pagination bug in the activity feed and run the focused tests.
~~~

- Result: Codex follows the repository's `AGENTS.md` and works on the requested code normally.
- Files: only the application files and durable records justified by the task may change.
- Proof: review the diff and the focused verification reported by Codex.
- Skip it when: the task is about setting up, checking, repairing or deliberately maintaining Project
  OS itself.

## The four actions people tend to mix together

1. **Install the skill once.** This makes `$project-os` available to Codex. It changes no project.
2. **Connect each repository once.** Bootstrap a new control plane or adopt compatible records already
   there.
3. **Do ordinary engineering work in ordinary chat.** After setup, Codex reads `AGENTS.md` when a new
   task starts. You do not prefix every request with `$project-os`.
4. **Invoke `$project-os` for control-plane work.** Use it for bootstrap, adoption, consistency checks,
   repairs, durable plan transitions, findings, reusable knowledge and version upgrades.

Installing the skill is not integrating a repository. Integrating a repository is not opening a
plan. Opening a plan is not completing the work.

## What it adds to a repository

- A concise root `AGENTS.md` that routes Codex to current project records.
- `.agents/CONTEXT.md` for durable facts, authority, architecture and verified commands.
- `.agents/STATE.md` for the current checkpoint and exact next action.
- A canonical plan index plus just-in-time plans for work that must survive multiple sessions.
- Findings and sanitized evidence with explicit verification boundaries.
- Separate project-specific and portable failure knowledge.
- Capability packs for service, web, mobile, data and delivery boundaries.
- A React Native and Expo overlay that refines the mobile pack without changing the core model.
- A deterministic Python helper for detection, initialization, adoption, checking and managed
  knowledge synchronization.

Lite mode is enough for normal engineering work. Full mode adds a durable program and history boundary
for an explicitly approved multi-phase audit, migration or release program.

## Quick start

Requirements:

- A Codex client with standalone skill support.
- Python 3.9 or newer for the deterministic helper.
- A local checkout of the target repository.

### 1. Install the standalone skill

`$skill-installer` below selects Codex's built-in skill installer, just as `$project-os` will later
select Project OS.

**Type this in Codex chat:**

~~~text
$skill-installer Install project-os from https://github.com/innrvoice/engineering-project-os/tree/v1.0.1/skills/project-os
~~~

- Result: Codex installs the versioned `project-os` skill in the local Codex profile.
- Files: only the user-level Codex skill installation changes; the open repository does not.
- Proof: start a new Codex task and confirm that `project-os` appears in the available skills.
- Skip it when: this exact release is already installed. See [Setup](docs/SETUP.md) for the update
  workflow.

### 2. Inspect one target repository

Open the repository in a new Codex task. Start read-only so you can see whether it needs a clean
bootstrap, an `AGENTS.md`-preserving bootstrap or adoption.

**Type this in Codex chat:**

~~~text
$project-os Inspect this repository for Project OS setup. Do not change files. Decide whether it
needs a clean bootstrap, an AGENTS-preserving bootstrap or adoption. Recommend Lite or Full, the
applicable capability packs and overlays and the exact files you would create or map.
~~~

- Result: Codex inspects Git state, instructions, documentation, CI, task runners, lockfiles and tool
  configuration before recommending a setup path.
- Files: none should change.
- Proof: the response names one setup path, justified packs and overlays and a concrete file preview.
- Skip it when: the repository already has a healthy Project OS at the installed version and you only
  want to do ordinary work.

### 3. Apply the reviewed setup

Use the matching copy-paste prompt in [Setup](docs/SETUP.md). The setup guide covers all three cases
without overwriting existing project authority.

Then start one more fresh Codex task in the repository. Codex loads a newly created `AGENTS.md` when a
task starts, not retroactively into an already running task.

## What happens after setup

Codex automatically discovers the repository's `AGENTS.md` at task startup. That file tells it which
Project OS records to read for the current job. The whole `.agents` directory is not injected into
every prompt. Plans, capability packs, evidence and knowledge are loaded only when relevant.

There is no Project OS daemon, watcher, MCP server, hidden database, automatic upload or background
cross-project sync. The durable state is the repository files you can inspect and version. The helper
uses only the Python standard library and does not decide product truth or write plans for you.

[How it works](docs/HOW_IT_WORKS.md) explains the complete Codex lifecycle. [Usage](docs/USAGE.md)
contains copy-paste recipes for plans, checkpoints, findings, knowledge, repairs and upgrades.
[Reference](docs/REFERENCE.md) documents every record, mode, pack and helper command.

## Safety boundary

Project OS manages engineering control-plane files only. It does not grant authority to install
dependencies, modify application code, commit, push, deploy, publish or contact external systems.
Those actions still follow the user's request and the target repository's instructions.

Never place credentials, personal data, private paths, signed URLs, raw production logs or copied
project history in portable knowledge.

## Project information

- [Setup](docs/SETUP.md)
- [How it works](docs/HOW_IT_WORKS.md)
- [Usage](docs/USAGE.md)
- [Reference](docs/REFERENCE.md)
- [Changelog](CHANGELOG.md)
- [Contributing](CONTRIBUTING.md)
- [Security policy](SECURITY.md)
- [MIT License](LICENSE)
