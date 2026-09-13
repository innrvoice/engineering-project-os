# Setup

Project OS has two separate setup layers:

1. Install the reusable `project-os` skill for Codex.
2. Connect Project OS to each repository that should keep durable engineering state.

Installing the skill does not create `AGENTS.md` or `.agents`. Connecting one repository does not
change any other repository.

## Requirements

- A Codex client with standalone skill support.
- Python 3.9 or newer for the deterministic helper.
- A local checkout of every repository you want to connect.

The helper uses only the Python standard library.

## 1. Install the skill

### Recommended: standalone skill from GitHub

`$skill-installer` is Codex skill syntax. Send this message inside Codex, not in Terminal.

**Type this in Codex chat:**

~~~text
$skill-installer Install project-os from https://github.com/innrvoice/engineering-project-os/tree/v1.0.1/skills/project-os
~~~

- Result: Codex installs the complete versioned skill in the local Codex profile.
- Files: the user-level Codex skill directory changes; the open repository does not.
- Proof: start a new Codex task and confirm that `project-os` appears in the available skills.
- Skip it when: release 1.0.1 is already installed for this Codex profile.

The URL is pinned to a release tag. It does not follow the repository's `main` branch automatically.

### Updating an installed standalone skill

An installed skill is replaced as one directory. It is not merged file by file.

**Type this in Codex chat:**

~~~text
$skill-installer Update my installed project-os skill to the copy at
https://github.com/innrvoice/engineering-project-os/tree/v1.0.1/skills/project-os. Inspect the
existing installation, show the exact replacement path and replace that skill directory as one unit.
Do not change any repository.
~~~

- Result: Codex replaces the installed skill with release 1.0.1.
- Files: only the installed `project-os` skill directory changes.
- Proof: start a new Codex task so Codex rebuilds its skill list, then upgrade and check each connected
  repository as described below.
- Skip it when: the installed skill already comes from the v1.0.1 tag.

Updating the installed skill still does not update repositories. Repository upgrades are deliberate
and use the same workflow for every connected project.

## 2. Open the target repository in a new task

Codex loads available skills and repository instructions when a task starts. Open the target
repository as the task workspace after installation.

Do not copy `AGENTS.md`, `.agents/STATE.md`, plans, findings or project knowledge from another
repository. The reusable pieces are already inside the skill. Project-specific truth must come from
the target repository itself.

## 3. Inspect before changing files

This is the safe first prompt for every repository shape.

**Type this in Codex chat:**

~~~text
$project-os Inspect this repository for Project OS setup. Do not change files. Decide whether it
needs a clean bootstrap, an AGENTS-preserving bootstrap or adoption. Recommend Lite or Full, the
applicable capability packs and overlays and the exact files you would create or map.
~~~

- Result: Codex reads Git state, existing instructions, documentation, CI, task runners, lockfiles,
  tool configuration and existing engineering records.
- Files: none should change.
- Proof: the response names one setup path, the evidence for each selected pack or overlay and a dry
  run or mapping preview.
- Skip it when: the repository is already connected, passes the checker and only needs ordinary
  engineering work.

Detection is a recommendation, not project truth. It can find stack and capability signals, but it
cannot prove authority, architecture, ownership, exact commands or release procedure by filename
alone.

## 4. Apply exactly one setup path

### A. Clean bootstrap

Use this when the repository has neither a root `AGENTS.md` nor an existing `.agents` control plane.
Lite mode is the default for ordinary work.

**Type this in Codex chat:**

~~~text
$project-os Bootstrap this repository in Lite mode using the reviewed capability packs and overlays.
Preserve existing files, record only verified authority and commands and do not change application
code. Run a final initialization dry run, apply only if it matches the reviewed proposal and finish by
running the Project OS checker.
~~~

- Result: Codex runs detection and a dry run, creates the missing Project OS records, fills durable
  context only from verified repository evidence and checks the result.
- Files: a root `AGENTS.md` and the new `.agents` control plane may be created. Application files do
  not change.
- Proof: review the complete diff, confirm the selected packs and require `Project OS check: PASS`.
- Skip it when: root `AGENTS.md` or `.agents` already exists.

Use Full mode only for an approved multi-phase audit, migration, release program or another initiative
that genuinely needs a durable program contract and history boundary. Replace `Lite` with `Full` in
the prompt only after that decision is made.

### B. Preserve an existing `AGENTS.md`

Use this when the repository has root instructions but no `.agents` directory. Project OS must not
replace those instructions. First review the minimal routing addition.

**Type this in Codex chat:**

~~~text
$project-os Prepare an AGENTS-preserving Lite bootstrap for this repository. Do not change files.
Inspect the current AGENTS.md, propose only the routing needed for .agents/CONTEXT.md and
.agents/STATE.md, then show the complete initialization dry run with justified packs and overlays.
~~~

- Result: Codex proposes the smallest routing edit and previews the remaining control-plane files.
- Files: none should change.
- Proof: the preview preserves every existing instruction and names both required routes exactly.
- Skip it when: `.agents` already contains compatible project state; use adoption instead.

After reviewing that preview, apply it.

**Type this in Codex chat:**

~~~text
$project-os Apply the reviewed AGENTS-preserving Lite bootstrap. Preserve all existing AGENTS.md
instructions, add only the reviewed routes to .agents/CONTEXT.md and .agents/STATE.md, initialize with
the existing-AGENTS safety flag, do not change application code and run the checker.
~~~

- Result: Codex adds the reviewed routes, uses `--allow-existing-agents` and creates the missing
  Project OS records.
- Files: root `AGENTS.md` receives only the approved routing change and new `.agents` files are
  created. Application files do not change.
- Proof: the diff preserves the prior instructions, both routes are present and the checker passes.
- Skip it when: the routing preview has not been reviewed or the repository already has a compatible
  `.agents` control plane.

The helper accepts `--allow-existing-agents` only when `AGENTS.md` already mentions both required
paths. It is not a general overwrite flag.

### C. Adopt an existing control plane

Use this when compatible context, state, plans and findings already exist. Adoption maps those owners
instead of initializing over them.

**Type this in Codex chat:**

~~~text
$project-os Adopt this repository's existing engineering records. Inventory current paths and legacy
knowledge, preserve project-specific authority and existing records, report every conflict and show a
complete dry run without writing files.
~~~

- Result: Codex discovers compatible record owners, validates them and proposes a `SYSTEM.json`
  mapping plus managed packs and shared knowledge.
- Files: none should change during this preview.
- Proof: the report says the repository is safe to adopt, lists every planned create and lists no
  existing file as modified.
- Skip it when: required owners are missing or incompatible. Resolve the named structural problem
  instead of forcing adoption.

Apply only the reviewed adoption proposal.

**Type this in Codex chat:**

~~~text
$project-os Apply the adoption proposal exactly as reviewed. Preserve every mapped project-owned
record, create only the Project OS manifest and managed guidance or knowledge files from the preview,
then run the checker.
~~~

- Result: Codex attaches Project OS to the existing layout without rewriting mapped records.
- Files: `.agents/SYSTEM.json`, selected managed guidance and shared seed knowledge may be created.
  Existing context, state, plans, findings and evidence remain unchanged.
- Proof: compare the applied diff with the preview and require `Project OS check: PASS`.
- Skip it when: the dry run reported conflicts, incomplete knowledge coverage or unsafe paths.

## 5. Review repository truth

After bootstrap or adoption, confirm that:

- `AGENTS.md` preserves the project's actual authority and routes to current records.
- `.agents/CONTEXT.md` contains only durable, verified facts and exact commands.
- `.agents/STATE.md` is a compact checkpoint, not a task diary.
- `.agents/SYSTEM.json` selects only justified packs and overlays.
- plans, findings, evidence and project knowledge were not copied from another product.
- shared knowledge contains no credentials, personal data, private paths, signed URLs or private
  project history.

Project OS does not replace product, API, architecture, security, legal or release sources of truth.
Record the real authority hierarchy found in the repository.

## 6. Validate and restart

**Type this in Codex chat:**

~~~text
$project-os Check this repository's Project OS state and report errors without changing files.
~~~

- Result: Codex runs the deterministic checker against the repository control plane.
- Files: none should change.
- Proof: the helper prints `Project OS check: PASS`.
- Skip it when: never after setup. A first successful check is the setup exit gate.

Start a fresh Codex task in the connected repository. The new task will load the root `AGENTS.md` as
startup guidance. From that point, ordinary code requests do not need `$project-os`.

A structural pass proves the records are internally consistent. It does not prove application
behavior, deployment, artifact identity, production state or manual and physical acceptance.

## 7. Upgrade every connected repository the same way

First update the installed skill to v1.0.1 and start a new Codex task. Then open each connected
repository and use one upgrade prompt.

**Type this in Codex chat:**

~~~text
$project-os Upgrade this repository to the installed Project OS version. Inspect first,
preview all managed changes, preserve project-owned files, apply the update only when
the preview is clean, then run the Project OS checker.
~~~

- Result: the skill follows `inspect -> sync-knowledge --dry-run -> sync-knowledge -> check`. There is
  no separate Python `upgrade` command.
- Files: Project OS version metadata, managed capability guidance and managed shared knowledge may
  change. Project-owned context, state, plans, findings, evidence and application code are preserved.
- Proof: the final checker passes and `.agents/SYSTEM.json` plus shared knowledge report v1.0.1.
- Skip it when: the repository already passes the v1.0.1 checker.

The checker rejects a repository release version that differs from the installed helper. This is an
upgrade signal, not a reason to invent a repository-specific migration path. Resolve managed-content
conflicts first, then run the same upgrade workflow again.

## Next

- [How Project OS works inside Codex](HOW_IT_WORKS.md)
- [Daily usage and copy-paste recipes](USAGE.md)
- [Records, modes, packs and helper CLI reference](REFERENCE.md)
- [Security boundary](../SECURITY.md)
