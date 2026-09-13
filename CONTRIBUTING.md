# Contributing

Contributions are welcome when they improve portability, deterministic validation, documentation or
safe repository adoption without turning Project OS into an application framework.

## Development setup

1. Fork and clone the repository.
2. Use Python 3.9 or newer. Runtime dependencies are not required.
3. Create a focused branch for one observable outcome.
4. Preserve unrelated working-tree changes.
5. Run the complete checks before opening a pull request.

**Run this in Terminal from the repository root:**

~~~bash
python3 -B -m unittest discover -s tests -v
python3 -B -m compileall -q skills/project-os/scripts
python3 -B -m json.tool plugin.json >/dev/null
python3 -B -m json.tool .codex-plugin/plugin.json >/dev/null
python3 -B -m json.tool .agents/plugins/marketplace.json >/dev/null
git diff --check
~~~

- Result: unit behavior, Python syntax, JSON manifests and patch whitespace are checked.
- Files: tracked source files should not change. `compileall` may create ignored Python cache files.
- Proof: every command exits zero and the working-tree diff contains only the intended change.
- Skip it when: none before a pull request. During development, run the narrowest relevant subset
  first and the full set before handoff.

## Implementation rules

- Preserve existing project files during initialization, adoption, repair and synchronization.
- Keep application code outside Project OS operations unless a separate user request authorizes the
  application change.
- Keep languages and frameworks as detection signals. Add capability guidance only when a boundary
  changes engineering or verification decisions.
- Avoid runtime dependencies unless the benefit, security boundary and Python compatibility cost are
  demonstrated.
- Reject unsafe paths, ambiguous ownership and locally divergent managed content instead of guessing.
- Use atomic writes and preserve rollback behavior for multi-file operations.
- Add focused tests for success, dry run, conflict, concurrency and path-safety behavior affected by
  the change.

## Knowledge rules

- Keep findings, project knowledge and shared knowledge separate.
- Add knowledge only after the failure mechanism is confirmed.
- Shared fixtures and seed entries must contain no credentials, personal data, private paths, real
  user content, private endpoints or copied proprietary history.
- Preserve applicability, trigger, mechanism, prevention, decisive verification and scope boundaries
  when sanitizing a lesson.
- Do not overwrite a conflicting shared entry because one copy has a newer date.

## Documentation rules

- Explain whether a command belongs in Codex chat or Terminal immediately before its code block.
- For a workflow recipe, state the result, files that may change, proof of success and when the recipe
  is unnecessary.
- Use `$project-os` only for explicit skill invocation. Do not format it as a shell command.
- Show ordinary application prompts without `$project-os` so the control-plane boundary remains clear.
- Keep setup, mental model, daily recipes and technical reference in their dedicated documents rather
  than copying the same procedure into every page.
- Update public documentation when commands, record ownership, supported Python versions, safety
  boundaries or installation behavior change.
- Keep examples stack-agnostic and free of private project material.

## Release version lockstep

`VERSION` in `skills/project-os/scripts/project_os.py` is the Project OS release source. A release
change must update every active release surface in one pull request:

- portable and Codex package manifests;
- repository-local packaging metadata, including its source ref;
- pinned standalone installation URLs;
- generated `SYSTEM.project_os_version`;
- shared `knowledge_version`;
- every bundled knowledge entry's `source.project_os_version` and content hash;
- CI assertions, test fixtures and release notes.

Do not change `SYSTEM.schema_version` unless the manifest format changes. Do not mechanically change
the version in `plugin.json`'s external `$schema` URL; that version belongs to the Agent Plugins
schema.

The lockstep test must pass before release. Do not add compatibility branches, special per-project
upgrade paths or silent version coercion.

## Pull requests

Describe:

- the concrete problem;
- the smallest implemented change;
- the checks run and their results;
- any evidence class or external boundary that remains unverified.

Do not claim deployment, production behavior or physical acceptance from source inspection or unit
tests.

Report security issues through [SECURITY.md](SECURITY.md), not in a public pull request.
