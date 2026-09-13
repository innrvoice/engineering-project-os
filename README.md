# Engineering Project OS

Engineering Project OS is a stack-agnostic, repository-local operating system for resumable Codex
work. It keeps durable project facts, the current checkpoint, execution plans, findings, evidence,
and reusable failure knowledge separate so a new task can continue from repository state instead of
chat history.

It does not impose an application architecture, language, package manager, test framework, or release
process. Repository evidence selects capability guidance, while actual commands and sources of truth
must still be verified in the target project.

## What it provides

- Safe initialization for a new project and non-destructive adoption for an existing project system.
- Lite mode for normal engineering work and Full mode for approved multi-phase programs.
- Capability packs for service, web, mobile, data, and delivery boundaries.
- A React Native and Expo overlay that refines the mobile pack without making the system
  framework-specific.
- Separate project and shared failure knowledge, with conflict-aware synchronization.
- A deterministic Python checker for structure, invariants, paths, and knowledge integrity.

Languages and frameworks are toolchain signals, not behavioral profiles. A repository can select any
combination of capability packs that its real boundaries require.

## Requirements

- A Codex client that supports standalone skills or plugin marketplaces.
- Python 3.9 or newer to run the deterministic helper.
- A local checkout of the target repository for initialization, adoption, and checks.

The helper uses only the Python standard library.

## Install as a plugin

The plugin route installs the complete versioned package from this public GitHub repository:

~~~bash
codex plugin marketplace add innrvoice/engineering-project-os --ref v1.0.0
codex plugin add engineering-project-os@engineering-project-os
~~~

The first command registers the repository marketplace. The second installs the plugin exposed by
that marketplace. Start a new Codex task after installation so the bundled skill is discovered.

## Install only the standalone skill

Send this as a Codex prompt, not as a shell command:

~~~text
$skill-installer Install project-os from https://github.com/innrvoice/engineering-project-os/tree/v1.0.0/skills/project-os
~~~

This installs only the `project-os` skill for the current user. It does not register the plugin or its
marketplace. Use a new Codex task after installation.

## Bootstrap a repository

Open the target repository in a new Codex task and invoke:

~~~text
$project-os Bootstrap this repository in Lite mode. Inspect existing instructions, Git state,
documentation, CI, task runners, lockfiles, and tool configuration first. Detect applicable capability
packs and overlays, record only verified commands and authority, do not change application code, and
finish by running the Project OS checker.
~~~

For a repository that already has a compatible `.agents` control plane, ask Project OS to adopt the
existing layout instead of initializing over it. If the repository has only `AGENTS.md`, add and
review routing to `.agents/CONTEXT.md` and `.agents/STATE.md`, then initialize with
`--allow-existing-agents` so the file is preserved.

## Use the helper directly

From a clone of this repository:

~~~bash
python3 skills/project-os/scripts/project_os.py detect --target /path/to/repository
python3 skills/project-os/scripts/project_os.py init --target /path/to/repository --mode lite --packs auto --overlays auto --dry-run
python3 skills/project-os/scripts/project_os.py init --target /path/to/repository --mode lite --packs auto --overlays auto
python3 skills/project-os/scripts/project_os.py init --target /path/to/repository --mode lite --packs auto --overlays auto --allow-existing-agents
python3 skills/project-os/scripts/project_os.py adopt --target /path/to/repository --dry-run --inventory
python3 skills/project-os/scripts/project_os.py check --target /path/to/repository
python3 skills/project-os/scripts/project_os.py sync-knowledge --target /path/to/repository --dry-run
~~~

Initialization creates missing files only. Adoption maps compatible existing records and reports
conflicts instead of overwriting them. Run a dry run before changing a mature repository.

## Safety boundary

Project OS manages engineering control-plane files only. It does not authorize application changes,
package installation, commits, pushes, deployments, publication, or external communication. Those
actions still require the target repository's instructions and the user's request.

Never place credentials, personal data, private paths, signed URLs, raw production logs, or copied
project history in portable knowledge.

## Distribution scope

Version 1.0.0 is distributed from GitHub through the repository marketplace and as a standalone
skill. Listing in the universal Plugins Directory is outside this release's scope.

See [Setup](docs/SETUP.md) for installation and adoption, and [Usage](docs/USAGE.md) for the daily
workflow and record ownership model.

## Project information

- [Changelog](CHANGELOG.md)
- [Contributing](CONTRIBUTING.md)
- [Security policy](SECURITY.md)
- [MIT License](LICENSE)
