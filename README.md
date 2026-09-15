<img src="assets/logo.svg" width="96" height="96" alt="Engineering Project OS logo">

# Engineering Project OS

[Install from the Universal Plugin Directory](https://chatgpt.com/plugins/plugins_6aa793523ba481918ea921c5438d98c9)

The source-tree release is 2.1.0. The Directory page shows the version currently available for installation.

Project OS is for developers who need AI-assisted engineering work to survive the next session.

It keeps context, decisions, plans, evidence and failure knowledge inside the repository, so ChatGPT and Codex can continue from verified state instead of starting over.

The difficult part was rarely the first task. It was the fifth one.

I would reopen a repository, reconstruct what had already been decided, search for the command that had actually passed and try to remember which "done" item still needed a device, deployment or human check. The code was still there. The working state was not.

Chat history is a poor project database.

Engineering Project OS adds a small, visible control plane to the repository. ChatGPT can help from a project description, selected files or a repository snapshot. Codex can work directly in an open repository workspace. Either way, a new chat can read current repository truth instead of treating an old conversation as current state.

## What you get

- Resume work from verified repository state instead of reconstructing context from old chats.
- Preserve decisions, checkpoints and evidence alongside the code.
- Preview Project OS changes before applying them.
- Keep long engineering work organized across sessions and agents.
- Turn confirmed failures into a knowledge library that belongs to you.
- Carry reviewed failure patterns into another project without copying its private history.

It is stack-agnostic. A TypeScript frontend, Python service, Clojure backend, native mobile app or mixed monorepo uses the same core system. Repository evidence selects only the capability guidance that fits its real boundaries.

## Knowledge that compounds

This part began with a fairly irritating thought. If I spent two months finding and fixing failures in one React Native project, why should a new React Native project make me pay for the same lessons again?

A failed approach should not disappear into a closed chat. Project OS records the finding, preserves the evidence and turns a confirmed mechanism into project knowledge with its trigger, prevention, decisive verification and applicability boundaries.

Project knowledge stays with its repository and may retain names, paths and local history. When a mechanism could help elsewhere, Project OS prepares a sanitized proposal. You review the batch, approve only the lessons that remain accurate without private context and keep those lessons in your own reusable library.

Codex can import that library directly from another repository. ChatGPT and cross-machine workflows can use a deterministic JSON bundle. The destination previews which lessons match its stack, shows what it would skip and changes nothing until you approve the import.

There is no failure database maintained by us, no lesson submission queue and no Project OS release between your old project and your new one. Nothing uploads, learns or synchronizes in the background. The knowledge is yours.

The first repository records the lesson. The next repository does not need to repeat the failure. That was the whole point.

## Start with these requests

The first request explains the product without requiring repository files. The second begins setup and the third moves reviewed knowledge from an earlier project.

**In ChatGPT, choose one of these starter requests:**

~~~text
@Engineering Project OS Tell me what Project OS does, how it works and when I should use it.
@Engineering Project OS Help me set up Project OS for this project and start with a safe preview.
@Engineering Project OS Help me reuse verified failure knowledge from an earlier project in this one.
~~~

**In Codex, open the repository workspace, then type:**

~~~text
$project-os overview
$project-os inspect
$project-os bootstrap
$project-os check
~~~

`@Engineering Project OS` explicitly selects the plugin or bundled skill in ChatGPT. `$project-os` selects the bundled skill in Codex. Neither form is a Terminal command, environment variable or permanent mode. The remaining text is an ordinary natural-language request. It can be short, detailed and written in any language.

The overview needs no project input. In ChatGPT, starter-package advice can begin from a project description. A review of an existing setup needs its actual files, usually `AGENTS.md` and `.agents/`. A full repository ZIP is optional and useful only when the whole tree matters. Project OS does not pretend that an empty host workspace is the repository. In Codex, the selected workspace provides that context.

The exact Codex skill name is `project-os` with a hyphen. `$project os` is not the same invocation.

The examples above are recommended phrases, not a rigid command parser:

- `$project-os overview` explains who Project OS is for, what it does and which workflow to choose without inspecting or changing a repository.
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
- managed capability packs and overlays plus user-owned project and reusable failure knowledge.

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
$skill-installer Install project-os from https://github.com/innrvoice/engineering-project-os/tree/v2.1.0/skills/project-os
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
@Engineering Project OS Help me set up Project OS for this project and start with a safe preview.
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

The installed plugin contains a bundled skill with reasoning instructions, focused references, templates, capability guidance and a deterministic Python helper. It does not contain a central failure database. The standalone Codex installation contains the same skill. A connected repository contains visible files under `AGENTS.md` and `.agents/`.

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
