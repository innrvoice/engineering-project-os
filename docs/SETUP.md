# Setup

Install Engineering Project OS, then ask Codex to connect the repository you want to work in. Installation makes the skill available; connection creates or adopts that repository's working records.

## Requirements

- A local repository opened in Codex.
- Python 3.9 or newer on macOS or Linux for the deterministic helper.
- For the GitHub alternative, a Codex CLI with plugin support.

Codex inspects existing instructions and configuration. You do not need to choose packs or edit JSON.

<a id="legacy-directory"></a>

## Install from the Plugin Directory

1. Open the [Engineering Project OS card in the Plugin Directory](https://chatgpt.com/plugins/plugins_6aa793523ba481918ea921c5438d98c9) and check that it shows 2.2.4.
2. Use the plus button to install, as described in [OpenAI's plugin guide](https://learn.chatgpt.com/docs/plugins).
3. Start a new Codex chat in your repository. Ask Codex to verify the selected Directory source and installed helper version 2.2.4, then [connect the repository](#connect-a-repository).

In ChatGPT, select `@Engineering Project OS` for the companion workflow over supplied files. Installation alone does not give ChatGPT access to your local checkout.

<a id="2-inspect-the-repository"></a>
<a id="3-preview-and-connect"></a>
<a id="4-validate-and-restart"></a>

## Connect a repository

Open the intended repository and send:

~~~text
$project-os Help me set up Project OS for this repository and start with a safe preview.
~~~

Codex inspects Git state, instructions and existing records. It chooses a fresh setup, preserves existing instructions or adopts compatible records. You do not select the internal operation yourself.

Before writing, Codex shows the proposed files and explains what it will preserve. Review that preview and approve the proposed connection. If the root, ownership or existing instructions are ambiguous, Codex asks for the decision it needs instead of replacing them.

The result is a connected repository in Standard mode, with context, working records and instruction routing. Setup preserves project authority and safe unrelated namespaces. It does not open a plan, start a Program or change application code. Adoption preserves compatible records and their ownership.

After setup, Codex checks and reports the changed files. Start a new chat to load the repository instructions. Then ask for normal engineering work without a Project OS prefix.

For a read-only assessment, ask `$project-os inspect`. Exact operations are in [Reference](REFERENCE.md#project-os-requests).

## Upgrade to 2.2.4

Update your installation first using the Directory host controls or the [GitHub](#github-marketplace-alternative) or [standalone](#standalone-codex-skill) route below. Then open the connected repository in a new Codex chat and send:

~~~text
$project-os upgrade
~~~

Codex previews the upgrade and applies the reviewed operation after authorization, then checks records and changed paths. Locally modified managed content requires an ownership decision before overwriting.

Updating the installed copy does not upgrade repository records by itself. The transaction can update managed instructions, routing and migration metadata. A reviewed proof migration can add helper-owned metadata or historical evidence archives while preserving original values and hashes. It does not authorize application changes or turn historical acceptance into newly verified behavior.

## Legacy finding proof ownership

Some repositories using 2.2.3 need an explicit review to distinguish earlier helper proofs from project-owned fields. Codex prepares that review and preserves the original data. If upgrade changes a file used as evidence, it also identifies the exact historical bytes that need archival consent. Missing proof or unclear ownership blocks the operation.

The [technical ownership contract](REFERENCE.md#legacy-finding-proof-ownership) describes `--finding-proof-review` and [historical snapshots](REFERENCE.md#historical-evidence-snapshots-during-upgrade). You do not need to assemble that JSON for the ordinary upgrade request.

## ChatGPT companion setup

Select `@Engineering Project OS` in ChatGPT. Explanations need no files; setup advice can start from a description. Inspecting or updating an existing setup requires its instructions and records. ChatGPT must ask for missing material.

Changed files remain supplied-copy artifacts until you deliberately apply them to the real repository and validate them in Codex. Use [Usage](USAGE.md#chatgpt-companion-boundaries) for that boundary.

<a id="1-install-in-codex-from-github"></a>

## GitHub marketplace alternative

Use the GitHub marketplace if you prefer that distribution route. Run these commands in Terminal:

~~~shell
codex plugin marketplace add innrvoice/engineering-project-os --ref main
codex plugin add engineering-project-os@engineering-project-os
~~~

The catalog comes from `main`; its plugin entry pins the source to `v2.2.4`. For an existing marketplace registration, refresh it in Terminal:

~~~shell
codex plugin marketplace upgrade engineering-project-os
codex plugin add engineering-project-os@engineering-project-os
~~~

Start a new Codex chat afterward. Codex must verify the selected installation and helper version before connecting or upgrading a repository. These commands do not install the ChatGPT Web companion.

## Standalone Codex skill

For a skill-only installation, send this message in Codex chat, not Terminal:

~~~text
$skill-installer Install project-os from https://github.com/innrvoice/engineering-project-os/tree/v2.2.4/skills/project-os
~~~

Start a new chat afterward. This pinned skill does not follow future releases or provide the ChatGPT companion. Continue with [connection](#connect-a-repository) or [repository upgrade](#upgrade-to-224).

## Resolve duplicate installations

To move from GitHub to Directory, install the Directory copy first. In a new chat, have Codex verify its source, path and helper version 2.2.4. Then disable the GitHub copy, leave one installation active and start a new chat. Preserve `AGENTS.md` and `.agents/`; connecting again is unnecessary. Run `$project-os upgrade` separately if the repository needs it.

For a standalone duplicate, confirm its path and removal permission first. After switching, verify the selected copy again.

<a id="setup-boundaries"></a>

Setup grants no permission to install dependencies, delete data, commit, push, deploy or publish. Continue with [Usage](USAGE.md); exact syntax and formats belong in [Reference](REFERENCE.md).
