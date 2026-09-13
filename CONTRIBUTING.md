# Contributing

Contributions that improve portability, deterministic validation, documentation, or safe adoption are
welcome.

## Development setup

1. Fork and clone the repository.
2. Use Python 3.9 or newer. Runtime dependencies are not required.
3. Create a focused branch and keep changes scoped to one observable outcome.
4. Run the checks below before opening a pull request.

~~~bash
python3 -B -m unittest discover -s tests -v
python3 -B -m compileall -q skills/project-os/scripts
python3 -B -m json.tool plugin.json >/dev/null
python3 -B -m json.tool .codex-plugin/plugin.json >/dev/null
python3 -B -m json.tool .agents/plugins/marketplace.json >/dev/null
~~~

## Contribution rules

- Preserve existing project files during initialization and adoption. Add an explicit migration only
  when a schema change requires it.
- Keep languages and frameworks as detection signals. Add capability guidance only when a boundary
  changes engineering or verification decisions.
- Keep reusable knowledge mechanism-focused and sanitized. Fixtures must contain no credentials,
  personal data, private paths, real user content, or copied proprietary project history.
- Add or update focused tests for behavioral changes, conflict cases, and path-safety boundaries.
- Avoid runtime dependencies unless the benefit and compatibility cost are demonstrated.
- Update public documentation when commands, records, supported Python versions, or installation
  behavior change.
- Keep `plugin.json`, `.codex-plugin/plugin.json`, the helper version, and release notes synchronized
  for a release.

## Pull requests

Describe the problem, the smallest implemented change, the checks run, and any unverified boundary.
Do not claim deployment, production behavior, or physical acceptance from source or unit-test evidence.

Report security issues through the process in [SECURITY.md](SECURITY.md), not in a public pull request.
