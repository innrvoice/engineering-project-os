# Project working agreement

Current user instructions take precedence. Inspect Git HEAD and status before non-trivial work, read the relevant implementation and callers, preserve unrelated changes and verify the result.

## Authority

- `VERSION` and `SCHEMA_VERSION` in `skills/project-os/scripts/project_os.py` own release and format versions. Keep manifests, templates, knowledge provenance, tests and documentation in lockstep.
- `skills/project-os/SKILL.md` and its references own the skill workflow. `README.md` and `docs/` explain the public contract. Repair runtime and documentation together when they disagree.
- `tests/`, `scripts/` and `.github/workflows/ci.yml` define source and package checks.
- Use Python 3.9+ on macOS or Linux. The runtime has no third-party dependencies.

## Local working records

If present, read `.agents/CONTEXT.md`, `.agents/STATE.md` and the active plan routed by `.agents/plans/index.json`. Read only relevant capability guidance and knowledge. These records are local to this checkout and are not required to develop or test a fresh clone.

Keep this repository's plans, checkpoints, findings, evidence and knowledge out of Git. The sole public root `.agents` file is `.agents/plugins/marketplace.json`. Do not force-add local records. Bundled skill templates and synthetic test fixtures are public product files and remain tracked. Update local records only when their durable truth changes; state is a compact handoff, not a diary. Keep exactly one active plan while execution is running and preserve unverified acceptance gates.

## Development and verification

- Make the smallest coherent change. Reproduce defects where practical and test observable behavior.
- Preserve repository-owned data during bootstrap, upgrade, synchronization and Program transitions.
- Keep the installed stable skill separate from the candidate helper in this checkout.
- In Markdown, keep each prose paragraph and each list item on one physical line. Do not hard-wrap prose. Preserve separate lines only for structure such as headings, tables, code fences and intentional nested blocks.
- Use `python3 -B -m unittest discover -s tests -v` for the complete release checks.
- Before publication, run `python3 -B scripts/check_public_tree.py` against the staged file list and `git diff --cached --check`. Follow `CONTRIBUTING.md` and `docs/PACKAGING.md` for other checks.
- If local Project OS records exist, validate them with the candidate helper's `check --target .`.

## Publication and communication

Before any merge or publication, wait for completed Codex code and security reviews of the exact final source commit, address every remark and resolve its thread. CI success does not prove review completion. A new commit invalidates previous review evidence. Follow the trusted guard acquisition in `docs/PACKAGING.md`: verify an owner-trusted immutable guard commit and independent literal hash, retain its copy outside the candidate checkout and invoke it with an owner-trusted absolute Python path and `-I -B`, explicit trusted absolute `--git` and `--gh` paths and private comment/evidence-bound dispositions. The clean final PR checkout is data only; never execute its guard to establish its own readiness. Require READY immediately before merge and publication. Missing, running, stale or unresolved review blocks both actions. Keep an explicit review gate in the local release contract. Owner permission alone does not satisfy this gate.

Commit, push, tag, GitHub Release, installed-skill replacement and directory submission require owner authorization. A tagged standalone installation and public directory availability are separate outcomes. Never infer publication from passing local tests.

State what changed, what was verified and what remains unverified. Do not publish credentials, private data or internal working history in code, documentation, commit messages or release notes.

Read `.agents/WORKFLOW.md` before non-trivial work and after context compaction. It owns durable request intake and guarded plan completion; current user and repository instructions take precedence.

Read `.agents/WORKFLOW.md` for every engineering task, including bounded bug fixes. Record reproduced defects, save a current checkpoint and pass `checkpoint --check` before the final response. Current user and repository instructions take precedence.
