# Failure knowledge

Project OS deliberately separates incidents from reusable lessons.

## Project findings

`.agents/findings/findings.json` records concrete project problems and candidates. A finding keeps a
stable ID, status, impact, evidence, required next check, and optional active plan. Candidates and
hypotheses stay here.

## Project failure knowledge

`.agents/knowledge/project/failures.json` records confirmed mechanisms that remain specific to the
repository, stack versions, infrastructure, or product contract.

## Shared failure knowledge

`.agents/knowledge/shared/failures.json` contains sanitized lessons that can travel between projects.
Each entry needs:

- a stable ID and active/retired/replaced status;
- applicability and trigger;
- the observed mechanism;
- prevention and decisive verification;
- version, platform, or scope boundaries;
- a non-sensitive source and date.

Promote a lesson only after the failure is confirmed. Remove project names, user data, credentials,
absolute machine paths, private URLs, deployment identifiers, and claims that depend on unverified
infrastructure. Generalize the mechanism, not the story.

Use the helper to import missing seed lessons without overwriting local edits:

```bash
python3 scripts/project_os.py sync-knowledge --target <repository> --dry-run
python3 scripts/project_os.py sync-knowledge --target <repository>
```

If an existing ID differs from the seed, the helper reports a conflict and leaves the project entry
unchanged. Resolve that conflict by reviewing scope and provenance, not by selecting the newest text
automatically.
