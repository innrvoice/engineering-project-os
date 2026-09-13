# Failure knowledge

Project OS deliberately separates incidents from reusable lessons.

Knowledge is stored in repository files. Nothing is uploaded or synchronized between projects in the
background. Promotion and synchronization happen only when explicitly requested.

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

Use the helper to import or update managed seed lessons without overwriting local edits. Resolve
`scripts/project_os.py` relative to the installed Project OS skill directory.

Run in Terminal with the installed helper path resolved:

```shell
python3 <project-os-skill-directory>/scripts/project_os.py sync-knowledge --target <repository> --dry-run
python3 <project-os-skill-directory>/scripts/project_os.py sync-knowledge --target <repository>
```

If an existing managed ID differs locally from the installed seed, the helper reports a conflict and
aborts before applying any changes. Resolve that conflict by reviewing scope and provenance, not by
selecting the newest text automatically. Project-specific knowledge is never replaced by this command.
