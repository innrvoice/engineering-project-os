# Setup

Engineering Project OS is a Codex developer tool distributed primarily through its GitHub marketplace. Installation makes the Project OS skill available, but it does not attach a repository or write Project OS records.

## Requirements

- A Codex CLI with plugin support for marketplace installation, or the built-in Codex skill installer for a standalone skill.
- A local repository opened as the Codex workspace.
- Python 3.9 or newer on macOS or Linux for deterministic helper operations.
- A clean understanding of any existing `AGENTS.md`, `.agents/` records and uncommitted work before setup.

## 1. Install in Codex from GitHub

Run these commands in Terminal:

~~~shell
codex plugin marketplace add innrvoice/engineering-project-os --ref main
codex plugin add engineering-project-os@engineering-project-os
~~~

The first command registers the repository marketplace from `main`. The catalog's plugin entry pins the installed source to `v2.2.4`. Open the target repository in Codex and start a new task so the installed skill is available. Confirm the selected helper's version is `2.2.4` before connecting or upgrading a repository:

~~~shell
python3 -B -c 'import runpy; print(runpy.run_path("/absolute/path/to/project-os/scripts/project_os.py")["VERSION"])'
~~~

Resolve this path from the installed skill selected by Codex. Do not guess a cache path or copy plugin files into the repository. Marketplace registration and plugin installation belong to the user profile while Project OS records belong to each connected repository. For a standalone skill, use the [secondary installation route](#standalone-codex-skill).

The official [plugin packaging guide](https://developers.openai.com/plugins/build/plugins#add-a-marketplace-from-the-cli) describes marketplace registration and local plugin sources for supported clients, including Codex CLI and Codex in the ChatGPT desktop app. The commands here use the CLI; desktop marketplace controls follow the host's current UI.

## 2. Inspect the repository

**Type this in Codex chat:**

~~~text
$project-os inspect
~~~

Inspection is read-only. Codex reads Git state, applicable instructions, existing Project OS records, documentation and available engineering configuration. It reports one recommended connection path and the files that path would affect.

The possible paths are:

- **Clean bootstrap:** no existing Project OS authority needs preservation.
- **`AGENTS.md`-preserving bootstrap:** a compatible root instruction file already exists and must remain authoritative.
- **Adoption:** compatible context, plans, findings, evidence or knowledge already exist and should be mapped instead of replaced.

Stop if the report cannot identify the repository root, finds ambiguous ownership or would overwrite project-owned authority.

## 3. Preview and connect

For a bootstrap, continue with:

~~~text
$project-os bootstrap
~~~

For compatible existing records, use:

~~~text
$project-os adopt
~~~

Codex inspects again, prepares the operation and runs the deterministic helper with `--dry-run`. Review the proposed files before authorizing the same operation without `--dry-run`.

Bootstrap creates Standard mode. It does not create a Program, active plan or application code. It preserves safe unrelated `.agents` namespaces such as `.agents/plugins` and refuses an unsafe overwrite.

Adoption maps compatible records to the Project OS ownership model. It does not silently treat arbitrary Markdown as current authority.

## 4. Validate and restart

After the reviewed operation is applied, run:

~~~text
$project-os check
~~~

A successful setup requires the helper check to pass and the Git diff to contain only the approved control-plane files. Start a new Codex task after `AGENTS.md` is created or changed so its instruction route enters the task startup chain.

Ordinary engineering work now uses ordinary requests. Use `$project-os` when the request concerns Project OS maintenance, durable plan state, findings, evidence, knowledge or Program lifecycle.

## Upgrade to 2.2.4

Project OS 2.2.4 retains SYSTEM schema 5, plans schema 2, JSON acceptance contracts and durable request intake. It corrects proof refresh and separates helper-owned finding proofs from project extensions while retaining checkpoint verification and atomic completion. Upgrading a legacy schema also delivers the schema-5 continuity records; upgrading an existing schema-5 repository keeps the schema and knowledge-transfer formats unchanged.

For an already registered GitHub marketplace, refresh its catalog and install the pinned plugin in Terminal:

~~~shell
codex plugin marketplace upgrade engineering-project-os
codex plugin add engineering-project-os@engineering-project-os
~~~

For a first GitHub installation, use the registration commands above. For a standalone installation, use the pinned skill-installer request below. Resolve duplicate installations and verify the selected helper version, then start a new Codex task in the repository and type:

~~~text
$project-os upgrade
~~~

Codex must use the installed 2.2.4 helper transaction:

~~~text
python3 /absolute/path/to/project-os/scripts/project_os.py upgrade --target /path/to/repository --dry-run
python3 /absolute/path/to/project-os/scripts/project_os.py upgrade --target /path/to/repository
python3 /absolute/path/to/project-os/scripts/project_os.py check --target /path/to/repository
git diff --check
~~~

Review the dry-run before applying it. After the check, inspect the exact changed paths. The reviewed transaction adds managed WORKFLOW, an empty requests registry, minimal AGENTS routing and plan-index migration metadata. Existing Markdown plans, context, state, evidence and application code remain unchanged. Findings retain their legacy fields; an explicitly reviewed proof adoption can add only the helper-owned namespace. Historical closed plans retain their dispositions without new proof. Before resuming a legacy unfinished plan, review its contract and remove its migration mark. Existing legacy knowledge migration rules remain applicable.

Updating the installed plugin or standalone skill alone does not upgrade a connected repository. Each repository keeps its recorded release until this explicit transaction succeeds.

## Legacy finding proof ownership

When the source repository records 2.2.3 and contains bare finding proof-like fields, Codex must prepare an explicit ownership review before upgrade. It preserves every project-owned field and adopts proven helper proofs without changing their original hashes. Ambiguous ownership stays pending; it is not resolved by deleting data or accepting changed evidence.

The [technical ownership migration contract](REFERENCE.md#legacy-finding-proof-ownership) describes `--finding-proof-review`, its exact registry hash, complete ID decisions and preview/apply commands. Earlier repositories preserve bare extension fields automatically. Updating the installed plugin does not perform this review or upgrade project records by itself.

## ChatGPT companion setup

ChatGPT is a companion for explanations, supplied project files and portable knowledge bundles. Where the companion is available in ChatGPT, start a new chat and select it with `@Engineering Project OS`. Codex marketplace commands install into Codex; they do not install a plugin in ChatGPT Web. See the [legacy Directory status](#legacy-directory) for that separate channel.

An overview needs no repository input:

~~~text
@Engineering Project OS Tell me how Project OS helps Codex resume real engineering work across sessions.
~~~

Setup advice can begin from a project description. Claims about an existing setup require the relevant files, usually `AGENTS.md`, `.agents/SYSTEM.json`, `.agents/CONTEXT.md`, `.agents/STATE.md` and the registries involved in the request. A complete repository archive is optional and appropriate only when the complete tree matters.

ChatGPT works against the supplied copies. It cannot connect to a live local checkout through installation alone. Any generated or changed files remain chat artifacts until the user deliberately applies them to the repository and validates the result in Codex.

## Standalone Codex skill

The secondary route installs only the standalone Codex skill. Send the following message in Codex chat, not Terminal:

~~~text
$skill-installer Install project-os from https://github.com/innrvoice/engineering-project-os/tree/v2.2.4/skills/project-os
~~~

Start a new Codex task after installation. This versioned URL does not follow `main` automatically. Verify the selected helper version before upgrading any repository.

## Resolve duplicate installations

Keep one intended Project OS installation active. Inspect the selected skill path and helper version before relying on `$project-os`; a GitHub plugin, an older Directory plugin and a standalone skill can otherwise compete. Disable an obsolete plugin through its host controls or remove an obsolete standalone skill only after confirming its path and obtaining any required authorization. Preserve repository-owned `AGENTS.md` and `.agents/` records. Start a new task and verify the selected version again.

## Legacy Directory

The existing [Universal Plugin Directory listing](https://chatgpt.com/plugins/plugins_6aa793523ba481918ea921c5438d98c9) remains on 2.2.2. On 2026-10-16, the maintainer reported that the Portal would not accept an updated skills-only submission for Engineering Project OS. This observation concerns this plugin's submission, so the GitHub release proceeds independently.

An existing Directory installation can retain its own companion access and older skill. Installing from GitHub does not upgrade that listing or prove that a new version is available in ChatGPT. Resolve any duplicate Codex installation before using the GitHub helper.

## Setup boundaries

- Installing the plugin is not connecting a repository.
- Connecting a repository is not opening a plan.
- Opening a plan is not starting a Program.
- A passing Project OS check proves structural consistency, not product acceptance.
- No setup path authorizes dependency installation, application edits, Git operations, deployment or publication.

Use [Usage](USAGE.md) for developer workflows, [Reference](REFERENCE.md) for exact syntax and [Packaging](PACKAGING.md) for maintainer release procedures.
