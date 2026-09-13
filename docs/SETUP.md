# Setup

## 1. Choose one installation route

### Plugin from the public GitHub marketplace

Use the plugin route when you want the complete versioned package and marketplace identity:

~~~bash
codex plugin marketplace add innrvoice/engineering-project-os --ref v1.0.0
codex plugin list --marketplace engineering-project-os --available --json
codex plugin add engineering-project-os@engineering-project-os
~~~

`marketplace add` registers a snapshot source; it does not install the plugin. Confirm that
`engineering-project-os` appears in the list, then install it with `plugin add`. Start a new Codex task
afterward.

### Standalone skill from GitHub

Send this prompt to Codex:

~~~text
$skill-installer Install project-os from https://github.com/innrvoice/engineering-project-os/tree/v1.0.0/skills/project-os
~~~

This installs only the skill for the current user. It does not install the plugin, add a marketplace,
or provide automatic updates. Use a new Codex task after installation.

### Manual skill copy from a checkout

For an offline or repository-scoped setup, clone or copy this repository, then copy the skill to one
of Codex's skill locations.

User-scoped installation:

~~~bash
mkdir -p ~/.agents/skills
cp -R /absolute/path/to/engineering-project-os/skills/project-os ~/.agents/skills/project-os
~~~

Repository-scoped installation:

~~~bash
mkdir -p /path/to/repository/.agents/skills
cp -R /absolute/path/to/engineering-project-os/skills/project-os /path/to/repository/.agents/skills/project-os
~~~

Do not copy over an existing `project-os` directory without reviewing the diff. Start a new Codex task
after copying.

## 2. Inspect the target repository

Start with one real repository. Before Project OS writes anything, ask it to inspect:

- Git state and existing repository instructions;
- project documentation and current sources of truth;
- CI, task runners, lockfiles, and tool configuration;
- existing `.agents`, continuity, plan, finding, evidence, and knowledge records;
- capability and ecosystem signals.

Detection proposes guidance only. It does not prove architecture, commands, ownership, product truth,
or release procedure.

## 3. Initialize or adopt

For a repository without an existing project control plane:

~~~text
$project-os Bootstrap this repository in Lite mode. Inspect it first, use a dry run, select only
applicable capability packs and overlays, preserve existing files, and do not change application code.
After I review the proposal, initialize the control plane and run the checker.
~~~

For a mature repository with existing records:

~~~text
$project-os Adopt this repository's existing engineering records. Inventory current paths and legacy
knowledge, propose mappings without overwriting anything, preserve project-specific authority, and run
the checker against the proposed manifest before writing it.
~~~

Lite mode is the default. Use Full mode only for an approved multi-phase audit, migration, release
program, or other initiative that needs a durable program and history.

The equivalent helper commands from this repository's checkout are:

~~~bash
python3 skills/project-os/scripts/project_os.py detect --target /path/to/repository
python3 skills/project-os/scripts/project_os.py init --target /path/to/repository --mode lite --packs auto --overlays auto --dry-run
python3 skills/project-os/scripts/project_os.py adopt --target /path/to/repository --dry-run --inventory
~~~

Apply the reviewed operation by repeating it without `--dry-run`.

`init` refuses any existing `.agents` tree. It also refuses an existing root `AGENTS.md` unless
`--allow-existing-agents` is supplied. That flag preserves the file and is accepted only after the
file already mentions both `.agents/CONTEXT.md` and `.agents/STATE.md`; it is not an overwrite escape
hatch. Use `adopt` when compatible state records already exist.

## 4. Review generated or mapped records

Confirm that:

- root `AGENTS.md` preserves and routes to the project's real authority;
- `.agents/SYSTEM.json` uses schema version 2 and maps every managed record correctly;
- `.agents/CONTEXT.md` contains only durable, verified facts and exact commands;
- `.agents/STATE.md` is a compact current checkpoint;
- selected packs match real service, web, mobile, data, or delivery boundaries;
- the `react-native-expo` overlay is selected only with the mobile pack and only for a matching repo;
- existing plans, findings, evidence, continuity, and knowledge remain authoritative where mapped;
- shared knowledge is sanitized and contains no credentials, personal data, private paths, or copied
  project history.

Project OS does not replace a project's product, API, architecture, security, legal, or release source
of truth. Record the actual authority hierarchy in the target repository.

## 5. Validate

Ask Codex:

~~~text
$project-os Check this repository's Project OS state and report errors without changing files.
~~~

Or run the checker directly:

~~~bash
python3 /absolute/path/to/engineering-project-os/skills/project-os/scripts/project_os.py check --target /path/to/repository
~~~

A successful structural check does not prove application behavior, deployment, artifact identity,
production state, or physical-device acceptance.

## 6. Share intentionally

Commit generated control-plane files only if the team wants the workflow in every clone. Keep personal
preferences in user-level Codex instructions and repository-specific truth in the repository where it
belongs.

The v1.0.0 installation commands are pinned to that tag and do not auto-update. Review later release
notes and select a newer tag explicitly when upgrading.

This GitHub distribution does not depend on a listing in the universal Plugins Directory, which is
outside the v1.0.0 release scope.
