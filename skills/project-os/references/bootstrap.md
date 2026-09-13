# Connect a repository

Use this procedure when Project OS has not yet been connected to the target repository. Installing the
skill and connecting a repository are separate operations.

Resolve `scripts/project_os.py` relative to the installed Project OS skill directory in every command
below. Do not assume the target repository contains the helper.

## Inspect first

1. Resolve the repository root and inspect Git status without modifying files.
2. Read every applicable existing `AGENTS.md` or `AGENTS.override.md` from the root to the working
   directory.
3. Inspect the real stack and commands from tracked configuration, lockfiles, CI, Makefiles, task
   runners, and existing documentation.
4. Identify authoritative product, architecture, API, security, and operational documents. Do not
   infer authority from a filename alone.

If the user asked only for an inspection, stop after reporting the recommended setup, mode, packs,
overlays, files, and exact next command. Do not initialize or adopt anything.

## Choose a mode

- `lite`: default. Creates routing, durable context, a compact checkpoint, just-in-time plans,
  findings, evidence, capability guidance, and project/shared knowledge.
- `full`: adds a program contract and history boundary for an approved multi-phase audit, migration,
  release program, or other long-running initiative.

Capability packs can be auto-detected or explicitly selected from `service`, `web`, `mobile`,
`data`, and `delivery`. Ecosystem overlays refine a matching pack; `react-native-expo` requires
`mobile`. Languages are toolchain signals only and never select behavioral profiles.

## Choose the repository path

### Clean repository

Use `init` when neither `.agents` nor a root `AGENTS.md` exists.

Run in Terminal with the installed helper path resolved:

```shell
python3 <project-os-skill-directory>/scripts/project_os.py detect --target <repository>
python3 <project-os-skill-directory>/scripts/project_os.py init --target <repository> --mode lite --packs auto --overlays auto --dry-run
python3 <project-os-skill-directory>/scripts/project_os.py init --target <repository> --mode lite --packs auto --overlays auto
```

Change `--mode lite` to `--mode full` only when Full mode was selected deliberately. Review the dry-run
output before applying the identical command without `--dry-run`.

### Existing root AGENTS.md only

Preserve the file. Add the smallest explicit routing needed for Codex to read `.agents/CONTEXT.md` and
`.agents/STATE.md`, review that edit, then run `init` with `--allow-existing-agents`. The helper refuses
this flag until both routes are present.

Run in Terminal with the installed helper path resolved:

```shell
python3 <project-os-skill-directory>/scripts/project_os.py init --target <repository> --mode lite --packs auto --overlays auto --allow-existing-agents --dry-run
python3 <project-os-skill-directory>/scripts/project_os.py init --target <repository> --mode lite --packs auto --overlays auto --allow-existing-agents
```

Do not replace the existing `AGENTS.md` with the bundled template. Merge only compatible routing and
lifecycle rules.

### Existing compatible control plane

Use `adopt` when the repository already has compatible `.agents` owners for context, state, plans, and
findings. Adoption discovers the existing owners and adds managed Project OS metadata, guidance, and
shared knowledge without rewriting those owners.

Run in Terminal with the installed helper path resolved:

```shell
python3 <project-os-skill-directory>/scripts/project_os.py adopt --target <repository> --inventory --dry-run
python3 <project-os-skill-directory>/scripts/project_os.py adopt --target <repository> --inventory
```

Apply only when the dry run reports `safe_to_adopt: true`, the mapping is correct, and planned creates
contain no project-owned destination. If existing state is incomplete or incompatible, report the exact
missing owner or conflict instead of initializing over it.

## Finish the connection

After scaffolding:

1. Merge only the routing and lifecycle rules that fit the existing `AGENTS.md`.
2. Fill `.agents/CONTEXT.md` with verified authority, architecture, commands, and boundaries found in
   the repository.
3. Remove unjustified packs or overlays. Add nested `AGENTS.md` only where a subtree genuinely needs
   different rules or commands.
4. Keep `.agents/STATE.md` at `idle` until a concrete long-running package is opened.
5. Run the checker with the installed helper:

   ```shell
   python3 <project-os-skill-directory>/scripts/project_os.py check --target <repository>
   ```

6. Report the created or adopted files, checker result, and anything still unverified.
7. Recommend opening a new Codex task in the target repository so its new or updated `AGENTS.md` is
   loaded as startup instruction context.

Do not copy another project's state, plan registry, findings, history, absolute paths, private
evidence, or product rules into the new repository.
