# Bootstrap a repository

Use this procedure for first-time setup or migration from an existing instruction system.

## Inspect first

1. Resolve the repository root and inspect Git status without modifying files.
2. Read every applicable existing `AGENTS.md` or `AGENTS.override.md` from the root to the working
   directory.
3. Inspect the real stack and commands from tracked configuration, lockfiles, CI, Makefiles, task
   runners, and existing documentation.
4. Identify authoritative product, architecture, API, security, and operational documents. Do not
   infer authority from a filename alone.

## Choose a mode

- `lite`: default. Creates routing, durable context, a compact checkpoint, just-in-time plans,
  findings, evidence, capability guidance, and project/shared knowledge.
- `full`: adds a program contract and history boundary for an approved multi-phase audit, migration,
  release program, or other long-running initiative.

Capability packs can be auto-detected or explicitly selected from `service`, `web`, `mobile`,
`data`, and `delivery`. Ecosystem overlays refine a matching pack; `react-native-expo` requires
`mobile`. Languages are toolchain signals only and never select behavioral profiles.

## Scaffold safely

Run detection and a dry run first:

```bash
python3 scripts/project_os.py detect --target <repository>
python3 scripts/project_os.py init --target <repository> --mode lite --packs auto --overlays auto --dry-run
```

Then initialize. The helper creates missing files only. It refuses an existing `.agents` tree; use
`adopt` for that case. If only root `AGENTS.md` exists, first add explicit routing to
`.agents/CONTEXT.md` and `.agents/STATE.md`, review that edit, then use
`--allow-existing-agents` to preserve the file while creating the remaining records.

After scaffolding:

1. Merge only the routing and lifecycle rules that fit the existing `AGENTS.md`.
2. Fill `.agents/CONTEXT.md` with verified authority, architecture, commands, and boundaries found in
   the repository.
3. Remove unjustified packs or overlays. Add nested `AGENTS.md` only where a subtree genuinely needs
   different rules or commands.
4. Keep `.agents/STATE.md` at `idle` until a concrete long-running package is opened.
5. Run `python3 scripts/project_os.py check --target <repository>`.

Do not copy another project's state, plan registry, findings, history, absolute paths, private
evidence, or product rules into the new repository.
