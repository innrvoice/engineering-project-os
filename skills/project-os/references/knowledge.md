# Failure knowledge

Project OS separates project observations from reusable engineering lessons. Knowledge is stored in
repository files. Nothing uploads or synchronizes between projects in the background.

## Add a finding

For `finding add: <observation>`, inspect current evidence and search for an existing owner first.
Record a stable ID, status, impact, evidence, required next check and optional active plan. Keep
observations separate from inference and do not claim an unverified mechanism.

Preview the intended registry and evidence changes, preserve unrelated entries and run the checker
after writing.

## Capture project knowledge

For `knowledge capture: <finding-id>`, require a confirmed mechanism and decisive evidence.
Project-specific knowledge may retain repository, dependency and environment context.

Record applicability, trigger, mechanism, prevention, decisive verification and version or scope
boundaries. Link the source finding. Do not turn a candidate or hypothesis into a failure lesson.

## Propose shared knowledge

For `knowledge propose-shared: <lesson-id>`, remain read-only. Decide whether the mechanism is
portable. Remove project names, credentials, personal data, absolute machine paths, private URLs,
signed URLs, deployment identifiers and product history.

The helper rejects common detectable patterns and explicit sensitive field names. That screening is
not exhaustive, so human review remains mandatory before any lesson becomes shared knowledge.

If sanitization would make the lesson misleading, keep it project-specific. Otherwise present the
complete proposed entry for human review. Do not write or publish it merely because it was proposed.

## Synchronize managed knowledge

Use the helper only after an explicit bootstrap, adoption, synchronization or upgrade workflow.
Resolve it relative to the installed skill.

Run this in Terminal:

~~~shell
python3 /absolute/path/to/project-os/scripts/project_os.py sync-knowledge --target /path/to/repository --dry-run
~~~

If an existing managed ID or guidance file differs from its recorded baseline, report a conflict and
abort before applying any changes. The repository must already match the helper's Project OS release;
use the upgrade workflow for a version change. Resolve ownership and provenance rather than preferring
newer text.

Apply only a clean preview:

~~~shell
python3 /absolute/path/to/project-os/scripts/project_os.py sync-knowledge --target /path/to/repository
python3 /absolute/path/to/project-os/scripts/project_os.py check --target /path/to/repository
~~~

Project-specific knowledge is never replaced by synchronization. Shared knowledge travels to another
repository only through deliberate inclusion in a reviewed Project OS release and an explicit upgrade.
