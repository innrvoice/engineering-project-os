# Setup

Project OS has two separate setup layers:

1. Install the plugin from the Universal Plugin Directory or use the standalone Codex alternative.
2. Provide the repository context and connect Project OS to it.

Installation does not create `AGENTS.md` or `.agents`. Connecting one repository does not change another repository.

## Requirements

- A supported ChatGPT or Codex surface with plugin access.
- A project description, relevant files or an optional repository snapshot for ChatGPT or a local checkout opened as the Codex workspace.
- Python 3.9 or newer on macOS or Linux when the deterministic helper runs locally. Unsupported write environments fail before mutation.

The helper uses only the Python standard library.

## 1. Install from the Universal Plugin Directory

1. Open [Engineering Project OS](https://chatgpt.com/plugins/plugins_6aa793523ba481918ea921c5438d98c9).
2. Select the plus button or `Install`.
3. Start a new chat so ChatGPT or Codex loads the bundled skill.

In ChatGPT, use `@Engineering Project OS` to select the plugin or bundled skill. In Codex, use `$project-os` to select the bundled skill. The remaining text is ordinary natural language.

The Directory is the primary installation route. Installing the plugin does not attach a repository, upload files or change an open checkout.

To update the Directory plugin, install the new published version when it appears, then start a new chat. Reinstall if the host still exposes an older version. Updating the plugin does not upgrade Project OS records inside a repository.

### Alternative: standalone Codex skill

`$skill-installer` is Codex skill syntax. Send this message inside Codex, not in Terminal.

**Type this in Codex chat:**

~~~text
$skill-installer Install project-os from https://github.com/innrvoice/engineering-project-os/tree/v2.0.5/skills/project-os
~~~

- Result: Codex installs the complete versioned skill in the local profile.
- Files: the user-level skill directory changes; the open repository does not.
- Proof: start a new Codex task and confirm that `project-os` is available.
- Skip it when: release 2.0.5 is already installed in this profile.

The URL is pinned to a release tag and does not follow `main` automatically. This route installs the skill in Codex only. It does not install the plugin in ChatGPT.

### Update the standalone Codex skill

An installed skill is replaced as one directory. It is not merged file by file.

**Type this in Codex chat:**

~~~text
$skill-installer Update my installed project-os skill from https://github.com/innrvoice/engineering-project-os/tree/v2.0.5/skills/project-os and replace only that installed skill; do not change any repository.
~~~

- Result: Codex replaces the installed `project-os` directory with release 2.0.5.
- Files: only the user-level skill installation changes.
- Proof: start a new Codex task so Codex rebuilds its available-skill list.
- Skip it when: the installed skill already comes from the same tag.

Updating the standalone skill does not update connected repositories. Upgrade each repository explicitly after starting a fresh task with the new skill.

## 2. Provide repository context in a new chat

### ChatGPT

Describe the project or attach the files relevant to the requested workflow. Choosing a setup or creating a starter package can begin from a project description. Reviewing, validating, repairing, adopting or upgrading an existing setup requires its actual Project OS files, normally `AGENTS.md` and `.agents/`. A full repository archive is optional and useful when the complete tree affects the recommendation. ChatGPT works only with information supplied in the chat; installing the plugin does not grant access to a live local checkout.

**Choose a starter request in ChatGPT:**

~~~text
@Engineering Project OS What does Project OS do, how does it work and when should I use it?
@Engineering Project OS Create a safe Project OS starter package for my project.
@Engineering Project OS Review my existing Project OS setup and tell me what to fix.
~~~

### Codex

Use the target repository as the Codex task workspace. Codex loads available skills and applicable `AGENTS.md` files when a task starts.

Do not copy `AGENTS.md`, state, plans, findings, evidence or project knowledge from another repository. The reusable system is already inside the skill. Project truth must come from the target repository.

## 3. Inspect before changing files

**Type this in Codex:**

~~~text
$project-os inspect
~~~

- Result: Codex reads Git state, applicable instructions, documentation, CI, task runners, lockfiles, tool configuration and existing engineering records. It recommends one connection path and only evidence-backed packs or overlays.
- Files: none change.
- Proof: the response names clean bootstrap, an `AGENTS.md`-preserving bootstrap or adoption and previews the affected files.
- Skip it when: the repository is already connected and currently passes `$project-os check`.

You may add ordinary language without memorizing an exact sentence.

**Type this in ChatGPT after attaching the relevant files:**

~~~text
@Engineering Project OS Inspect these files. Pay particular attention to the monorepo instructions and do not change files.
~~~

**Type this in Codex:**

~~~text
$project-os inspect. Pay particular attention to the monorepo instructions and do not change files.
~~~

This narrows the same read-only operation. Short requests are recommended prompts, not a parser.

## 4. Choose one connection path

Bootstrap always creates the Standard system. A Program is never created during repository setup.

### A. Clean bootstrap

Use this when there is no Project OS control plane. A safe unrelated namespace such as `.agents/plugins` may already exist; initialization preserves it.

**Type this in Codex chat:**

~~~text
$project-os bootstrap
~~~

- Result: Codex inspects again, runs detection, previews `init --dry-run`, reviews every proposed create, applies only a clean preview and runs the checker.
- Files: root `AGENTS.md` and Project OS records under `.agents` may be created. Safe unrelated `.agents` content is preserved. Application code does not change.
- Proof: review the complete diff, confirm the selected packs and require `Project OS check: PASS`.
- Skip it when: a compatible Project OS control plane already exists; use adoption instead.

To constrain the operation, extend the same short request.

**Type this in Codex chat:**

~~~text
$project-os bootstrap. Select only packs justified by tracked configuration, preserve .agents/plugins and do not change application code.
~~~

The extra sentence refines the natural-language request. It does not select a different bootstrap mode; Standard is the only bootstrap result.

### B. Preserve an existing `AGENTS.md`

Use this when root instructions already exist but Project OS does not. The existing file remains project-owned.

**Type this in Codex chat:**

~~~text
$project-os bootstrap. Preserve every existing AGENTS.md instruction and add only the minimum reviewed routes to .agents/CONTEXT.md and .agents/STATE.md.
~~~

- Result: Codex inspects the current instructions, previews the minimal routing edit, adds it only after the proposal is safe, runs `init --allow-existing-agents --dry-run`, applies the matching initialization and checks the result.
- Files: existing `AGENTS.md` receives only the required reviewed routes. Missing Project OS records are created. Application code does not change.
- Proof: the prior instructions remain intact, both routes are present and the checker passes.
- Skip it when: the repository already has compatible context, state, plans and findings; use adoption.

The helper accepts `--allow-existing-agents` only when both routes already exist. It is a narrow preservation gate, not an overwrite flag.

### C. Adopt compatible existing records

Use adoption when the repository already has compatible owners for context, state, plans and findings. Adoption maps those records rather than initializing over them.

**Type this in Codex chat:**

~~~text
$project-os adopt
~~~

- Result: Codex inventories existing owners and legacy knowledge, runs an adoption dry-run and presents its mappings and conflicts. It applies only a reviewed result with `safe_to_adopt: true`, then runs the checker.
- Files: the Project OS manifest, managed guidance and shared seed knowledge may be created. Mapped project-owned records remain byte-for-byte unchanged.
- Proof: the applied mapping matches the preview, no existing owner was overwritten and the checker passes.
- Skip it when: required owners are missing, ambiguous or incompatible. Repair the named structural problem rather than forcing adoption.

A pre-existing `PROGRAM.md` is not enough to infer whether a Program is active. Adoption fails closed in this case. Resolve the lifecycle explicitly instead of forcing an adoption.

## 5. Review repository truth

After bootstrap or adoption, confirm that:

- `AGENTS.md` preserves actual authority and routes to the current records.
- `.agents/CONTEXT.md` contains verified durable facts and exact commands.
- `.agents/STATE.md` is a compact checkpoint, not a task diary.
- `.agents/SYSTEM.json` reports schema 3, Standard mode and only justified packs and overlays.
- plans, findings, evidence and project knowledge were not copied from another product.
- shared knowledge contains no credentials, personal data, private paths, signed URLs or private project history. The helper rejects common detectable patterns, but this is not exhaustive; human review is mandatory.

Project OS does not replace product, API, architecture, security, legal or release sources of truth.

## 6. Validate and restart

**Type this in Codex chat:**

~~~text
$project-os check
~~~

- Result: Codex runs the deterministic checker without changing files.
- Files: none change.
- Proof: the helper prints `Project OS check: PASS`.
- Skip it when: never after setup. This is the setup exit gate.

Start a fresh ChatGPT chat with the current repository files or a fresh Codex task in the connected repository. In Codex, the new task loads the new or updated `AGENTS.md` into its instruction chain. Ordinary code work now uses those instructions without `$project-os`.

A passing checker proves structural consistency. It does not prove application behavior, artifact identity, deployment, production state or manual and physical acceptance.

## 7. Upgrade a connected repository

First update the Directory plugin or standalone Codex skill and start a new chat or task. Then provide or open each connected repository.

**Type this in Codex chat:**

~~~text
$project-os upgrade
~~~

- Result: Codex inspects the current schema and Program state, runs the helper upgrade as a dry run, reviews every managed change, applies only a clean transaction and runs the checker.
- Files: Project OS version and schema metadata, managed guidance, managed shared knowledge and any explicitly required lifecycle migration may change. Project-owned context, state, plans, findings, evidence and application code are preserved.
- Proof: the final checker passes, the repository reports release 2.0.5 and a repeated dry run has no pending changes.
- Skip it when: the repository already passes the installed 2.0.5 checker.

A schema 2 repository with the former basic setup upgrades directly to Standard. If a legacy `PROGRAM.md` exists, Codex must determine whether it is active or already closed from repository evidence. It does not guess. A closed contract is archived with an explicit `completed` or `stopped` disposition and its verified actual closure date; an active contract remains active in Program mode. If repository evidence does not establish the closure date, Codex stops for that decision instead of using the migration date.

Managed-content conflicts abort the transaction without partial changes. Resolve the ownership conflict, then run the same `$project-os upgrade` request again.

## Program is a later, explicit decision

Connecting a repository does not start a Program. Start one only for a real multi-phase initiative.

**Type this in Codex chat:**

~~~text
$project-os program start: migrate authentication across the API, workers, web and mobile without downtime
~~~

Codex creates `.agents/PROGRAM.md` only after the contract is complete enough to validate. See [Usage](USAGE.md) for start, status and close examples.

## Developing Project OS itself

The repository can use its own control plane, but the stable installed skill and the candidate source have different jobs:

1. Use the installed stable skill to govern the work and interpret `$project-os` requests.
2. Develop and test the candidate helper from this checkout.
3. Do not replace the installed skill with the mutable checkout.
4. Validate candidate fixtures and candidate repository state with the source helper explicitly.
5. After a versioned release is published, install that tag and start a fresh task before validating through the installed copy.

This prevents an unfinished candidate from silently redefining the workflow that governs its own development.

## Next

- [How Project OS works in ChatGPT and Codex](HOW_IT_WORKS.md)
- [Daily usage and short requests](USAGE.md)
- [Records, Program lifecycle, packs and helper CLI](REFERENCE.md)
- [Security boundary](../SECURITY.md)
