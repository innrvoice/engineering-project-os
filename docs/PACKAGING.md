# GitHub distribution and release packaging

Project OS 2.2.4 corrects finding proof refresh and legacy ownership, retaining compact checkpoints and atomic completion. Completed final-commit Codex Review is a separate mandatory release gate. Schema remains 5. Fresh Codex and supplied-material ChatGPT execution must prove actual persistence and files-only recovery before the release ZIP is built. GitHub distribution is the primary release path; Directory submission remains a separate channel.

Retain the exact reviewed ZIP for the GitHub Release and verify its SHA-256 after download. Public documentation is part of that ZIP, so changing packaged copy before publication requires a new reproducible build and artifact checks. All selected skill files must match the behaviorally tested copy exactly. Preserve existing published artifacts unchanged.

Ordinary repairs must save actual findings and companion transfers must save their current checkpoint before returning project files. Verify the actual exported bytes by reconstructing the returned snapshot and running structural and checkpoint checks there. Passing runtime tests or a successful knowledge import does not establish that result. Preserve failed observations when revising and retesting the candidate.

The primary installation route registers the GitHub marketplace from `main` and installs `engineering-project-os@engineering-project-os` from its pinned `v2.2.4` source. The tagged standalone Codex skill is the secondary route. [Setup](SETUP.md) contains the exact Terminal commands and skill-installer request. GitHub installation applies to Codex; it does not publish or install the companion in ChatGPT Web.

## Verify before building the release package

Freeze the exact candidate skill files, install that frozen copy in isolated local sessions and run the ordinary finding, checkpoint and knowledge scenarios first. End the original sessions and repeat recovery in separate sessions that receive only the actual project files. Run the same exact candidate in the ChatGPT companion with supplied synthetic material before publication. Inspect actual findings, evidence hashes, current checkpoint receipts, material request routing and next actions. Preserve every initial failure and rerun affected cases after changes. An installed copy of an older release does not test candidate instructions.

Only after those behavioral checks pass, run the complete suite including extracted-package checks, then build the release ZIP to a new path outside the checkout:

~~~shell
python3 -B -m unittest discover -s tests -v
python3 -B scripts/package_plugin.py --output /private/tmp/engineering-project-os-2.2.4-plugin.zip
python3 -B scripts/package_plugin.py --check /private/tmp/engineering-project-os-2.2.4-plugin.zip
~~~

The output path must not exist. The builder reads the current working tree, including intentional uncommitted changes. Stable entry ordering, timestamps and permissions make repeated builds reproducible in the same Python and zlib environment. Record the SHA-256, entry count, compressed bytes and extracted bytes for the exact reviewed ZIP.

The package allowlist includes both manifests, the complete skill and its assets, public documentation, README, license, security policy, changelog, contributing guide and the packaging tool. It excludes the repository's local `.agents` control plane, Git metadata, tests and bytecode caches. Hidden `.agents` paths inside skill templates are public product assets and remain included.

The checker validates regular file entries, normalized unique paths, path traversal, symlinks, size limits, CRCs, manifest agreement, relative documentation links and Markdown layout. Public prose paragraphs and list items stay on one physical line so renderers cannot expose source wrapping as isolated words or conjunctions.

The package must not contain a release-managed failure knowledge database. Capability packs and overlays are product guidance. Project knowledge, the user's reusable knowledge registry and exported bundles exist only in connected repositories or user-selected artifact locations.

## Version and schema contract

Release version must be `2.2.4` in the helper, both plugin manifests, marketplace plugin-source ref, knowledge provenance, tests and active documentation. The marketplace catalog is read from `main` while its plugin source pins `v2.2.4`. `SCHEMA_VERSION` is `5`; plans use schema 2 and requests/contracts use schema 1. A dated legacy-channel status may name its own older version only inside an explicit Legacy Directory section.

The repository upgrade accepts schemas 2, 3 and 4, preserves existing legacy Program and knowledge migrations and adds the schema-5 continuity records in one transaction. It updates managed workflow, minimal AGENTS routing and plan-index metadata without rewriting Markdown plans, context, state, findings, evidence or application code. Historical dispositions remain legacy; uncontracted unfinished work requires review on resume. Test the exact transaction with dry-run, apply, `check`, `git diff --check` and path review.

## Selected metadata

Use these values in both manifests. They describe the current GitHub package independently of the legacy Directory listing:

- Name: `Engineering Project OS`
- Descriptor: `Built for Codex.`
- Subtitle: `Developer workflows for Codex`
- Category: `Developer Tools`
- Skill short description: `Resume Codex work and reuse failure knowledge`
- Plugin description: `Keep long-running Codex work resumable and reuse verified failure knowledge safely between your own projects. ChatGPT is a companion for supplied files and portable bundles.`
- Long description: `Developer tooling for Codex to resume repository work across sessions and persist plans, findings, evidence and checkpoints. Use this when work must survive context compaction or reviewed failure lessons need to move into another repository you own. Project OS inspects, bootstraps, validates, repairs and upgrades visible repository records with previews before writes. ChatGPT is a companion for explanation, supplied project files and portable knowledge bundles. Do not use it for ordinary one-session coding or as an automatic global knowledge service.`
- Capabilities: `Resume Codex work across sessions`; `Keep plans, decisions and evidence with the repository`; `Capture verified failure knowledge`; `Reuse reviewed lessons across your own projects`.
- Support URL: `https://github.com/innrvoice/engineering-project-os/issues`.

The official [listing metadata reference](https://developers.openai.com/plugins/deploy/submission#listing-metadata) defines the presentation fields and lists `Developer Tools` as a supported category title.

Keep `codex` before `chatgpt` in discovery keywords. The skill metadata file `skills/project-os/agents/openai.yaml` may contain only `policy.allow_implicit_invocation: true` under `policy`. Its `short_description` must contain 25 to 64 characters and its `default_prompt` must mention `$project-os` explicitly.

Declare `supportURL` as `https://github.com/innrvoice/engineering-project-os/issues` under `extensions.com.openai.interface` in root `plugin.json` and under `interface` in `.codex-plugin/plugin.json`. Source metadata validation and visible support-link rendering are separate checks.

The three companion starter prompts must match both manifests exactly:

1. `Tell me how Project OS helps Codex resume real engineering work across sessions.`
2. `Help me set up Project OS for this repository and start with a safe preview.`
3. `Help me reuse verified failure knowledge from an earlier project in this one.`

The social preview is versionless. It uses the eyebrow `BUILT FOR CODEX`, the title `Engineering Project OS`, the tagline `Resume work with durable state and reusable failure knowledge` and the existing `CONTEXT`, `PLANS`, `EVIDENCE`, `KNOWLEDGE` labels.

## Continuity and host checks

Replay the multi-message cases in `skills/project-os/evals/continuity.json` and the ordinary repair and transfer cases in `evals/persistence.json` using a frozen exact candidate skill installation. Verify actual record files and plan status after each message. End the initial session, start a fresh session with only the repository files and verify recovery, routing and the exact next action. Repeat relevant checks through the extracted release package after packaging. A passing deterministic fixture test is not a host workflow pass. Keep inaccessible Codex or ChatGPT acceptance pending with the exact required action.

## Required pre-publication acceptance guard

Run the fresh-host persistence and files-only recovery scenarios against a frozen local skill copy before building the release ZIP. Package consistency alone reports NOT_EVALUATED and never proves release readiness. Before recommending publication or asking for release authorization, run the read-only guard against the exact tested ZIP and the connected repository that owns its acceptance:

~~~shell
python3 -B scripts/package_plugin.py --check /private/tmp/engineering-project-os-2.2.4-plugin.zip --acceptance-target /path/to/repository --plan-id <release-acceptance-plan-id>
~~~

This guard rejects a ZIP differing from the candidate checkout and fails with NOT_READY when the selected plan has invalid records, stale proof, open requirements or pending acceptance. A successful result includes the exact ZIP SHA-256 and the named recorded outcome. It checks recorded proof consistency, not the semantic truth of evidence. The agent must verify that this is the release-preparation outcome and that it covers actual fresh Codex and ChatGPT behavior, not a narrower source-only plan. Acceptance files remain private and are never packaged.

If candidate host access is unavailable, report NOT_READY with the exact blocker and keep the plan open. Do not recommend publishing to unlock testing. Changed candidate bytes require rebuilding and repeating affected acceptance. Owner-directed publication with a known blocker does not verify it or close the preparation plan.

## Discovery checks

Replay `skills/project-os/evals/discovery.json` in a fresh Codex task. The set covers direct Codex overview and setup, indirect continuity loss, cross-project failure knowledge, one-session negative control, explicit ChatGPT use with supplied files, missing ChatGPT files and rejection of automatic global sharing.

The listing copy leads with Codex developer workflows, then states when to use the plugin and its boundaries. Discovery checks adapt the direct, indirect and negative prompt categories in the official [metadata optimization guide](https://developers.openai.com/plugins/guides/optimize-metadata). Change one metadata field at a time during later tuning and keep experiment notes only in ignored local `.agents` records.

Test all three public starter prompts in a fresh ChatGPT chat. The overview must describe Project OS as built for Codex and ChatGPT as the companion. Existing-repository requests without supplied files must ask for them rather than inspecting an empty host workspace.

## Required final-commit Codex Review

CI completion and Codex Review completion are separate prerequisites. Before merge or publication, verify both Codex code and security review have completed for the exact final source commit and every remark has a recorded disposition. Missing, running, unknown or wrong-commit review is NOT_READY. A later source commit invalidates the previous review. Local reviews and passing tests do not replace the configured GitHub review.

Run the read-only repository guard against a clean checkout of the reviewed PR head:

~~~shell
python3 -B scripts/check_codex_review.py --repo innrvoice/engineering-project-os --pr <number> --head <full-final-commit-sha> --target /path/to/clean/reviewed-checkout --dispositions /path/to/private/dispositions.json --json
~~~

The guard requires the canonical bot's completed final-head code/security status, no unresolved findings or review threads and a disposition for every marked bot finding across the PR history. With no findings, the disposition file is optional. It fails closed on missing API access, timeout, incomplete pagination, changed source, changed proof or concurrent review state. It does not merge, resolve threads or publish. Run it immediately before merge and again before publication using the retained reviewed checkout; verify the squash-merged tree matches that reviewed source.

Dispositions stay private and bind the repository, PR, reviewed head, exact comment body and local verification evidence. Each finding uses its real comment URL, `decision: fixed` or `decision: rejected`, a reason, `comment_sha256: sha256:<actual-comment-body-digest>` and `evidence: [{path: <repository-relative-proof>, sha256: sha256:<actual-file-digest>}]`. The top-level fields are `schema_version: 1`, `repository`, `pr`, `reviewed_head` and `findings`. An accepted-risk declaration or a resolved thread alone is insufficient. Refresh review after fixes, address every remark and preserve the actual guard result as the separate acceptance evidence.

## Release sequence

1. Finish runtime/source checks and review the complete diff. Freeze exact candidate skill files for isolated installation; keep existing published artifacts unchanged.
2. Run ordinary repair/discovery, knowledge review/approval, discovery and continuity scenarios in fresh Codex and ChatGPT sessions. Inspect actual findings, requests and current checkpoints; repeat recovery in separate sessions from files alone.
3. After all mandatory behavioral acceptance passes, run the full suite including extracted-package checks, build the release ZIP, verify reproducibility and compare every packaged file to the tested candidate.
4. Run `python3 -B scripts/check_public_tree.py` against the staged file list and run `git diff --cached --check` before any release commit. Test the three starter prompts and supplied-material companion boundaries.
5. After the candidate changes and available checks are concrete and reviewable, obtain scoped owner authorization for commit, push and a source pull request. Report every pending acceptance gate. Creating the PR enables review and does not authorize merge or publication; do not require an already completed PR review before creating that PR.
6. Complete the authorized source pull request and wait separately for CI and completed Codex code/security reviews of the final commit. Record every finding disposition, resolve its thread and pass the final-head guard above. A new source commit requires a matching new review and affected acceptance checks.
7. With all mandatory host results and final-commit review recorded, pass the pre-publication acceptance guard against the exact final ZIP. Only then recommend publication or request scoped owner authorization for merge, tag and GitHub Release. After authorization, merge and verify the merged tree, create tag `v2.2.4` on the accepted commit and attach the exact reviewed ZIP to the GitHub Release.
8. Verify the remote tag, Release metadata and downloaded asset SHA-256. Test the documented GitHub marketplace and tagged standalone routes in isolated profiles, then inspect the selected installation in a fresh Codex task. Check the installed version, exact skill bytes, bootstrap or upgrade, actual finding/checkpoint persistence and files-only recovery.
9. Report GitHub source, Release, artifact and installation results with their evidence. Report the legacy Directory status separately; a GitHub release does not require a new Portal submission or establish ChatGPT availability.

Do not replace package contents under an existing version. Any content change after publication requires another version.

## Release notes

Use these release notes after the release gates pass:

`2.2.4 rejects implicit refresh of changed finding proof, separates helper-owned proof data from legacy project fields and adds reviewed proof migration. Final-commit Codex Review and disposition of every remark are mandatory before merge or publication, independently of CI. GitHub marketplace installation remains primary with a tagged standalone skill alternative. Existing checkpoints, Standard, Program and schema compatibility remain supported.`

## Legacy Directory

The existing [Universal Plugin Directory listing](https://chatgpt.com/plugins/plugins_6aa793523ba481918ea921c5438d98c9) remains on 2.2.2. On 2026-10-16, the maintainer reported that the Portal would not accept an updated skills-only submission for Engineering Project OS. This observation concerns this plugin's submission and does not change the GitHub release gates.

If a future owner-authorized submission is accepted, follow the then-current official [submission guide](https://developers.openai.com/plugins/deploy/submission) and [plugin guidelines](https://developers.openai.com/plugins/plugin-guidelines). Verify the Portal form, images, capabilities, prompts, policies and exact package version. Declare the GitHub Issues support URL in both manifests, then verify actual Portal ingestion and public display separately. Record review approval, publication and fresh-host availability as distinct results. Preserve the existing published Directory artifact; GitHub release documentation does not replace it.
