# Project OS records

This directory stores repository-local working state for resumable engineering tasks. `AGENTS.md`
routes Codex to the relevant records; it does not load every file for every request.

- `SYSTEM.json`: schema, Project OS release, mode, path mappings, capability packs, overlays, and
  managed-file baselines.
- `CONTEXT.md`: durable project facts and verified commands.
- `STATE.md`: current checkpoint and next action.
- `plans/`: canonical execution registry and one-outcome plans.
- `findings/`: concrete project defects and candidates.
- `evidence/`: sanitized linked verification.
- `knowledge/project/`: confirmed project-specific lessons.
- `knowledge/shared/`: sanitized portable lessons.
- `packs/`: capability guidance selected from repository evidence. Language detection alone does not
  select behavior.

Do not put credentials, personal data, generated task diaries, or application runtime assets here.
History and broad program files are optional Full-mode additions.

Installing the Project OS skill, connecting this repository, and opening a plan are separate actions.
Ordinary engineering requests do not require `$project-os`; that prefix explicitly selects the skill
for one message about the control plane. There is no background service or automatic cross-repository
synchronization. Files change only through an explicit edit or helper run.
