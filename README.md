<img src="assets/logo.svg" width="96" height="96" alt="Engineering Project OS logo">

# Engineering Project OS

[Install from the Universal Plugin Directory](https://chatgpt.com/plugins/plugins_6aa793523ba481918ea921c5438d98c9)

The current Universal Plugin Directory and source-tree version is 2.0.4.

The difficult part was rarely the first task. It was the fifth one.

I would reopen a repository, reconstruct what had already been decided, search for the command that had actually passed and try to remember which "done" item still needed a device, deployment or human check. The code was still there. The working state was not.

Chat history is a poor project database.

Engineering Project OS keeps that working state with the repository. It adds a small, visible control plane for durable context, current checkpoints, plans, findings, evidence and reusable failure knowledge. ChatGPT can help from a project description, selected files or a repository snapshot. Codex can work directly in an open repository workspace. Either way, a new chat can resume from verified repository state instead of treating an old conversation as current truth.

It is stack-agnostic. A TypeScript frontend, Python service, Clojure backend, native mobile app or mixed monorepo uses the same core system. Repository evidence selects only the capability guidance that fits its real boundaries.

## Start with these requests

These are the normal Project OS entry points.

**In ChatGPT, choose one of these starter requests:**

~~~text
@Engineering Project OS Help me choose the right Project OS setup for my project.
@Engineering Project OS Create a safe Project OS starter package for my project.
@Engineering Project OS Review my existing Project OS setup and tell me what to fix.
~~~

**In Codex, open the repository workspace, then type:**

~~~text
$project-os help
$project-os inspect
$project-os bootstrap
$project-os check
~~~

`@Engineering Project OS` explicitly selects the plugin or bundled skill in ChatGPT. `$project-os` selects the bundled skill in Codex. Neither form is a Terminal command, environment variable or permanent mode. The remaining text is an ordinary natural-language request. It can be short, detailed and written in any language.

In ChatGPT, setup advice can begin from a project description. A review of an existing setup needs its actual files, usually `AGENTS.md` and `.agents/`. A full repository ZIP is optional and useful only when the whole tree matters. Project OS does not pretend that an empty host workspace is the repository. In Codex, the selected workspace provides that context.

The exact Codex skill name is `project-os` with a hyphen. `$project os` is not the same invocation.

The examples above are recommended phrases, not a rigid command parser:

- `$project-os check` runs the same read-only workflow as a longer request to validate the current repository and report errors.
- `$project-os check only the plan registry` narrows that request.
- `$project-os проверь Project OS и ничего не меняй` expresses the same intent in Russian.
- An ambiguous request does not authorize a guess or a write. Codex explains the available requests or asks one focused question.
- An unrelated engineering request remains ordinary engineering work. The prefix is unnecessary and does not justify creating plans, findings or other Project OS records.

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

A **Program** is a temporary umbrella contract for one explicitly started multi-phase initiative. It is useful when several separate plans need one shared outcome, authority boundary, phase sequence, evidence policy, cost boundary and exit condition.

For example, fixing one pagination bug is ordinary Standard work. Even a long implementation can stay in Standard with one durable plan. Migrating authentication across an API, workers, web and mobile in separate rollout phases may justify a Program.

**Type this in Codex chat:**

~~~text
$project-os program start: migrate authentication across the API, workers, web and mobile without downtime
~~~

- Result: Codex inspects the repository and prepares the Program contract. It creates `.agents/PROGRAM.md` only when the initiative, outcome, authority, phases, evidence, cost boundary, exclusions and overall exit conditions are sufficiently defined.
- Files: `.agents/PROGRAM.md` and Program metadata in `.agents/SYSTEM.json` may change. No history archive, plan or application code is created automatically.
- Proof: the repository is in `program` mode and the Project OS checker passes.
- Skip it when: one plan can own the outcome or the work has no genuine multi-phase coordination boundary.

Closing a Program archives its exact contract under `.agents/history/programs/` with a SHA-256 digest recorded in the history index, then returns the repository to Standard. The checker can detect an uncoordinated archive edit, deletion or substitution. This is tamper-evident Git-tracked history, not technically immutable storage, a signature or a remote audit service.

## Install once, provide repository context in each new chat

Requirements:

- A supported ChatGPT or Codex surface with plugin access.
- A project description, relevant files or an optional repository snapshot for ChatGPT or a local checkout opened as the Codex workspace.
- Python 3.9 or newer on macOS or Linux when the deterministic helper runs locally.

### 1. Install from the Universal Plugin Directory

1. Open [Engineering Project OS](https://chatgpt.com/plugins/plugins_6aa793523ba481918ea921c5438d98c9).
2. Select the plus button or `Install`.
3. Start a new chat so the bundled skill becomes available.

In ChatGPT, type `@Engineering Project OS` to select the plugin. In Codex, type `$project-os` to select its bundled skill. Installation does not attach a repository or change repository files.

This is the primary installation route for ChatGPT and Codex.

### Alternative: install the standalone Codex skill

`$skill-installer` is a separate built-in Codex skill. Send this message in Codex, not Terminal.

**Type this in Codex chat:**

~~~text
$skill-installer Install project-os from https://github.com/innrvoice/engineering-project-os/tree/v2.0.4/skills/project-os
~~~

- Result: Codex installs the versioned standalone skill in the local Codex profile.
- Files: only the user-level skill installation changes; the open repository does not.
- Proof: start a new Codex task and confirm that `project-os` is available.
- Skip it when: this exact release is already installed.

This alternative is for Codex only. The URL is pinned to a versioned Git tag and does not follow `main` automatically.

### 2. Inspect and connect a repository

In ChatGPT, describe the project or attach the files relevant to the requested workflow. Setup advice and a starter package can begin from a description. Reviewing an existing setup requires its actual Project OS files. Attach a full repository archive only when the complete tree is needed. ChatGPT does not gain access to a live local checkout merely because the plugin is installed.

In Codex, open the target repository as the task workspace.

**Type this in ChatGPT:**

~~~text
@Engineering Project OS Help me choose the right Project OS setup for my project.
~~~

**Type this in Codex:**

~~~text
$project-os inspect
~~~

- Result: Project OS reads the supplied repository context, existing instructions, documentation and available engineering configuration. In Codex it can also inspect Git state and local task runners. It recommends bootstrap, an `AGENTS.md`-preserving bootstrap or adoption.
- Files: none change.
- Proof: the response identifies the setup path, justified packs and overlays and the files that would change.
- Skip it when: the repository already passes `$project-os check` at the installed version.

For a new control plane, review the inspection and continue with:

**In ChatGPT:**

~~~text
@Engineering Project OS Bootstrap Project OS in these files. Start with a safe dry run.
~~~

**In Codex:**

~~~text
$project-os bootstrap
~~~

Bootstrap creates Standard only. It preserves safe unrelated `.agents` namespaces such as `.agents/plugins` and refuses to overwrite existing project authority. In ChatGPT, any changed files remain chat artifacts until the user deliberately applies them to a repository. [Setup](docs/SETUP.md) covers clean repositories, an existing `AGENTS.md` and adoption of compatible existing records.

### 3. Work normally

After setup, start a fresh chat. In Codex, this lets the repository's `AGENTS.md` enter the instruction chain. Ordinary product and code work does not need an explicit Project OS mention.

**Type this in Codex chat:**

~~~text
Fix the pagination bug in the activity feed and run the focused tests.
~~~

Use `$project-os` again when the object of the request is Project OS itself: setup, validation, repair, upgrade, Program lifecycle, durable plan state, findings or failure knowledge.

## What is actually installed

The installed plugin contains a bundled skill with reasoning instructions, focused references, templates, capability guidance, seed knowledge and a deterministic Python helper. The standalone Codex installation contains the same skill. A connected repository contains visible files under `AGENTS.md` and `.agents/`.

Codex discovers applicable `AGENTS.md` files when a task starts. ChatGPT uses the project description and files provided in the chat. When Project OS records are present, those instructions route the agent to the specific `.agents` records needed for the current work. The entire directory is not inserted into every prompt.

There is no Project OS daemon, watcher, MCP server, hidden database, automatic upload, automatic Git operation or background cross-project synchronization. The helper runs only when explicitly invoked. It does not decide product truth or grant authority to change application code, install dependencies, commit, push, deploy or publish.

## Continue reading

- [Setup](docs/SETUP.md)
- [How it works](docs/HOW_IT_WORKS.md)
- [Usage](docs/USAGE.md)
- [Reference](docs/REFERENCE.md)
- [Directory and release packaging](docs/PACKAGING.md)
- [Changelog](CHANGELOG.md)
- [Contributing](CONTRIBUTING.md)
- [Security policy](SECURITY.md)
- [Privacy policy](docs/PRIVACY.md)
- [Terms of use](docs/TERMS.md)
- [Install from the Universal Plugin Directory](https://chatgpt.com/plugins/plugins_6aa793523ba481918ea921c5438d98c9)
- [Support](https://github.com/innrvoice/engineering-project-os/issues)
- [MIT License](LICENSE)
