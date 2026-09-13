# Usage

## Record ownership

- `AGENTS.md`: concise routing, authority, safety, working method, and verification expectations.
- `.agents/SYSTEM.json`: schema version, Project OS version, mode, record mappings, capability packs,
  overlays, and validation limits.
- `.agents/CONTEXT.md`: durable current project facts, authority, architecture, and verified commands.
- `.agents/STATE.md`: current scope, progress, exact next action, and blockers.
- `.agents/plans/index.json`: canonical execution status register.
- `.agents/plans/NNN-*.md`: one observable outcome and its acceptance evidence.
- `.agents/findings/findings.json`: concrete project defects, candidates, and accepted risks.
- `.agents/evidence/`: sanitized evidence linked from plans or findings.
- `.agents/knowledge/project/`: confirmed lessons that still depend on this project or environment.
- `.agents/knowledge/shared/failures.json`: sanitized portable failure mechanisms.
- `.agents/packs/`: selected capability guidance and ecosystem overlays.
- `.agents/PROGRAM.md`: optional approved multi-phase program in Full mode.
- `.agents/history/`: optional immutable snapshots, never a startup reading list.

Do not duplicate the same status across `STATE`, a plan, findings, and reports. Each record owns one
kind of truth and links to the others.

## Capability guidance

Project OS core owns resumable state, plans, findings, evidence, and knowledge lifecycle. Select only
the packs justified by the repository's real boundaries:

- `service`: APIs, workers, queues, authentication, external integrations, and distributed outcomes.
- `web`: browser UI, routing, accessibility, responsive behavior, and browser-owned state.
- `mobile`: lifecycle, permissions, native handoffs, persistence, and device evidence.
- `data`: schemas, migrations, transactions, storage, deletion, and restore.
- `delivery`: builds, artifacts, deployment, runtime compatibility, and release gates.

The `react-native-expo` overlay refines the mobile pack for matching repositories. An overlay never
replaces pinned project dependencies, platform behavior, official documentation, or runtime evidence.

## Start a normal task

For a bounded task, work directly from the repository contract. Update `CONTEXT` only when a durable
fact changes. Do not create a plan merely to record activity.

For work that must survive multiple checkpoints, ask:

~~~text
$project-os Open one implementation package for this outcome. Preserve the current Git state, define
the affected interfaces and evidence gates, and make the exact next action resumable.
~~~

## Resume work

~~~text
$project-os Resume the active package from repository state. Revalidate anything affected by current
Git changes and continue the exact next action.
~~~

Repository state outranks chat history. Recheck volatile external facts before relying on an older
checkpoint.

## Check consistency

~~~text
$project-os Check this repository's Project OS state and report errors without changing files.
~~~

Or run:

~~~bash
python3 /path/to/project-os/scripts/project_os.py check --target .
~~~

Run the checker after every structural, mapping, plan-registry, finding-registry, or knowledge change.

## Record a failure

First record a concrete finding with evidence. After the mechanism is confirmed, ask:

~~~text
$project-os Convert this confirmed failure into a project lesson. Propose a sanitized shared lesson
only if the mechanism is genuinely portable, and do not overwrite or publish conflicts.
~~~

Project lessons can retain repository-specific context. Shared lessons must remove private paths,
identifiers, credentials, user data, endpoints, signed URLs, and product-specific history while
preserving the mechanism, detection signals, prevention, decisive check, and limits.

## Synchronize bundled knowledge

Preview synchronization before writing:

~~~bash
python3 /path/to/project-os/scripts/project_os.py sync-knowledge --target . --dry-run
~~~

Apply it only after reviewing the selected packs, overlays, and conflicts:

~~~bash
python3 /path/to/project-os/scripts/project_os.py sync-knowledge --target .
python3 /path/to/project-os/scripts/project_os.py check --target .
~~~

Synchronization adds compatible guidance and lessons. It does not silently replace diverged project
knowledge.

## Complete work

Update acceptance and evidence, mark the plan `done`, set execution to `idle`, and rewrite `STATE` to
a compact checkpoint. Missing hosted, artifact, production, manual, owner-reported, or physical
evidence remains explicitly unverified.

Source inspection, a passing test, a built artifact, a deployment, public availability, and human
acceptance are separate evidence classes. Claim only the class actually established.

## Direct helper reference

~~~bash
python3 /path/to/project-os/scripts/project_os.py detect --target .
python3 /path/to/project-os/scripts/project_os.py init --target . --mode lite --packs auto --overlays auto --dry-run
python3 /path/to/project-os/scripts/project_os.py init --target . --mode lite --packs auto --overlays auto --allow-existing-agents --dry-run
python3 /path/to/project-os/scripts/project_os.py adopt --target . --dry-run --inventory
python3 /path/to/project-os/scripts/project_os.py check --target .
python3 /path/to/project-os/scripts/project_os.py sync-knowledge --target . --dry-run
~~~

Use `--packs none` or an explicit comma-separated list when automatic recommendations are not correct.
Use `--overlays none` or an explicit comma-separated list for ecosystem overlays. The
`react-native-expo` overlay requires the mobile pack.
