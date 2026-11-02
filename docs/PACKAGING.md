# Distribution and release packaging

This is the maintainer's route for checking and publishing Project OS 2.3.0 source. For installation, start with [Setup](SETUP.md). Directory is the primary installation channel; GitHub marketplace and a pinned standalone Codex skill remain alternatives. Source version, Directory publication and GitHub release availability each need their own evidence.

Project OS 2.3.0 adds the read-only `brief` recovery report, a separate recursive byte-snapshot utility and explicit current, older-helper and unavailable-execution routes. It retains finding-proof ownership, compact checkpoints and atomic completion. Schema remains 5. Local candidate preparation, actual host acceptance and completed final-commit Codex Review are distinct gates.

Required host validation includes isolated native Codex persistence and recovery and actual ChatGPT companion snapshot reconstruction, record hashes and checkpoint receipts. Strict isolation of ChatGPT Work context from account Memory has not been established. Keep account Memory settings unchanged and retain this limitation in the release evidence and notes. A fresh chat or a returned archive alone is not proof of Memory-isolated recovery.

Retain the exact reviewed ZIP for the GitHub Release and verify its SHA-256 after download. Public documentation is part of that ZIP, so changing packaged copy before publication requires a new reproducible build and artifact checks. All selected skill files must match the behaviorally tested copy exactly. Preserve existing published artifacts unchanged.

Existing published tags, ZIPs and assets retain their original bytes. A candidate archive prepares a new version; neither its version label nor passing local checks proves publication or authorizes replacement of a published artifact.

With required execution available and permitted, ordinary repairs must save actual findings and companion transfers must save their current checkpoint before returning project files. Verify actual exported bytes by reconstructing the returned snapshot and running structural and checkpoint checks there. Without required execution, preserve input and report checks and writeback unperformed; a permitted transport copy with factual hashes is not a validated Project OS export. Passing runtime tests or a successful knowledge import does not establish host acceptance. Preserve failed observations when revising and retesting the candidate.

Check intake against the actual original messages, not a semantically similar summary: source_text retains complete relevant wording and conditions, interpretation is separate and withdrawal preserves the exact cancellation. For snapshots, compare the original source inventory with the serialized archive and require promised nested proposal paths. The bundled snapshot utility proves byte preservation only; it never runs mixed-project checks or overrides execution prohibitions. See [complete byte snapshots](REFERENCE.md#complete-byte-snapshots).

The [Directory listing](https://chatgpt.com/plugins/plugins_6aa793523ba481918ea921c5438d98c9) is the first installation choice. The GitHub alternative registers the marketplace from `main`; this candidate's entry targets `v2.3.0`. Verify the version actually resolved by the published catalog or Directory. [Setup](SETUP.md) contains both alternatives, including the standalone skill-installer request. GitHub installation applies to Codex; it does not publish or install the companion in ChatGPT Web.

## Prepare a candidate and verify it before release

Finish source, skill and documentation changes, then freeze the exact candidate files. A clearly unaccepted inspection/test ZIP may be built before final host acceptance so those exact bytes can be tested. Run the ordinary finding, checkpoint and knowledge scenarios in isolated Codex sessions and the same candidate in actual ChatGPT with supplied synthetic material. End the original sessions and repeat recovery in separate sessions that receive only actual saved files. Inspect findings, evidence hashes, current checkpoint receipts, request routing and next actions. Preserve initial failures and rerun affected cases after changes. An installed older release does not test candidate instructions.

Run the complete local suite including extracted-package checks and build the candidate ZIP to a new path outside the checkout:

~~~shell
python3 -B -m unittest discover -s tests -v
python3 -B scripts/package_plugin.py --output /private/tmp/engineering-project-os-2.3.0-plugin.zip
python3 -B scripts/package_plugin.py --check /private/tmp/engineering-project-os-2.3.0-plugin.zip
~~~

The output path must not exist. The builder reads the current working tree, including intentional uncommitted changes. Stable entry ordering, timestamps and permissions make repeated builds reproducible in the same Python and zlib environment. Record the SHA-256, entry count, compressed bytes and extracted bytes for the exact reviewed ZIP.

Package consistency reports NOT_EVALUATED for release acceptance. Test the inspected candidate bytes on the required hosts, then endorse that same unchanged ZIP only after host acceptance and the final review guards pass. A rebuild must be byte-identical or receive affected revalidation. The locally prepared candidate is ready for the named tests, not for publication.

The package allowlist includes both manifests, the complete skill and its assets, public documentation, README, license, security policy, changelog, contributing guide and the packaging tool. It excludes the repository's local `.agents` control plane, Git metadata, tests and bytecode caches. Hidden `.agents` paths inside skill templates are public product assets and remain included.

The checker validates regular file entries, normalized unique paths, path traversal, symlinks, size limits, CRCs, manifest agreement, relative documentation links and Markdown layout. Public prose paragraphs and list items stay on one physical line so renderers cannot expose source wrapping as isolated words or conjunctions.

The package must not contain a release-managed failure knowledge database. Capability packs and overlays are product guidance. Project knowledge, the user's reusable knowledge registry and exported bundles exist only in connected repositories or user-selected artifact locations.

## Version and schema contract

Release version must be `2.3.0` in the helper, both plugin manifests, marketplace plugin-source ref, newly generated knowledge provenance, tests and active documentation. The marketplace catalog is read from `main` while this candidate's plugin source pins `v2.3.0`. `SCHEMA_VERSION` is `5`; plans use schema 2, requests/contracts use schema 1 and the separate brief report uses schema 1. Preserve older release descriptions as history in the changelog and existing user-owned provenance during supported migrations.

The repository upgrade accepts schemas 2, 3 and 4, preserves existing legacy Program and knowledge migrations and adds the schema-5 continuity records in one transaction. It updates managed workflow, minimal AGENTS routing and plan-index metadata while preserving project-owned data and application code. Reviewed finding-proof migrations can add proof metadata to the registry and preserve evidence for rewritten managed files in historical snapshots; this is not a promise that every record stays byte-identical. Historical dispositions remain legacy; uncontracted unfinished work requires review on resume. Follow the [proof ownership and snapshot review](REFERENCE.md#legacy-finding-proof-ownership), then test the exact transaction with dry-run, apply, `check`, `git diff --check` and path review.

## Selected metadata

Use these values in both manifests. The Directory package and GitHub release target the same 2.3.0 metadata; source validation and the host's visible presentation remain separate checks:

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

Replay the multi-message cases in `skills/project-os/evals/continuity.json` and the setup, scope and knowledge cases in `skills/project-os/evals/prompts.json` and `skills/project-os/evals/submission.json` using a frozen exact candidate skill installation. Also run an ordinary bounded repair in a connected synthetic project and inspect its genuine finding, verification evidence and current checkpoint. Verify record files and plan status after each message. End the initial session, start a fresh session with only the repository files and verify recovery, routing and the exact next action. Repeat relevant checks through the extracted release package after packaging. A passing deterministic fixture test is not a host workflow pass. Keep inaccessible Codex or ChatGPT acceptance pending with the exact required action.

Prepare one counted final host runbook after freezing the skill and docs, rather than requesting a separate preliminary owner upload for each branch. Preserve separate messages or sessions where acceptance requires them. Include current-helper brief, selected older-helper compatibility, execution prohibited by the user and genuinely unavailable execution as distinct cases; reuse the existing missing-material case. If a required host is inaccessible, report its actual blocker instead of treating a local simulation or an execution prohibition as that host result.

## Required pre-publication acceptance guard

Run fresh-host persistence and files-only recovery against the exact frozen skill bytes from the inspected candidate ZIP. Package consistency alone reports NOT_EVALUATED and never proves release readiness. Before recommending publication or asking for release authorization, run the read-only guard against the exact tested ZIP and the connected repository that owns its acceptance:

~~~shell
python3 -B scripts/package_plugin.py --check /private/tmp/engineering-project-os-2.3.0-plugin.zip --acceptance-target /path/to/repository --plan-id <release-acceptance-plan-id>
~~~

This guard rejects a ZIP differing from the candidate checkout and fails with NOT_READY when the selected plan has invalid records, stale proof, open requirements or pending acceptance. A successful result includes the exact ZIP SHA-256 and the named recorded outcome. It checks recorded proof consistency, not the semantic truth of evidence. The agent must verify that this is the release-preparation outcome and that it covers actual fresh Codex and ChatGPT behavior, not a narrower source-only plan. Acceptance files remain private and are never packaged.

If candidate host access is unavailable, report NOT_READY with the exact blocker and keep the plan open. Do not recommend publishing to unlock testing. Changed candidate bytes require rebuilding and repeating affected acceptance. Owner-directed publication with a known blocker does not verify it or close the preparation plan.

## Discovery checks

Replay `skills/project-os/evals/discovery.json` in a fresh Codex task. The set covers direct Codex overview and setup, indirect continuity loss, cross-project failure knowledge, one-session negative control, explicit ChatGPT use with supplied files, missing ChatGPT files and rejection of automatic global sharing.

The listing copy leads with Codex developer workflows, then states when to use the plugin and its boundaries. Discovery checks adapt the direct, indirect and negative prompt categories in the official [metadata optimization guide](https://developers.openai.com/plugins/guides/optimize-metadata). Change one metadata field at a time during later tuning and keep experiment notes only in ignored local `.agents` records.

Test all three public starter prompts in a fresh ChatGPT chat. The overview must describe Project OS as built for Codex and ChatGPT as the companion. Existing-repository requests without supplied files must ask for them rather than inspecting an empty host workspace.

## Required final-commit Codex Review

CI completion and Codex Review completion are separate prerequisites. Before merge or publication, verify both Codex code and security review have completed for the exact final source commit and every remark has a recorded disposition. Missing, running, unknown or wrong-commit review is NOT_READY. A later source commit invalidates the previous review. Local reviews and passing tests do not replace the configured GitHub review.

Run an independently trusted copy of the read-only guard outside the candidate checkout with Python isolated mode (`-I`). The PR checkout is data only: never execute its guard, packaging code or helper to establish review readiness. Choose the guard's immutable source commit and literal SHA-256 through an owner-approved trusted channel, independently of the candidate PR; a hash supplied by that PR is not a trust anchor. A previously reviewed guard can verify a newer candidate. If no trusted guard is available, stop with NOT_READY and obtain or independently review one before proceeding.

Use owner-trusted absolute paths for Python, Git and `gh` and a locally prepared checkout whose Git metadata, configuration and execution environment are trusted. Replace every placeholder below with the reviewed values; this recipe restricts bootstrap command lookup, extracts bytes from the separately trusted source, verifies them before execution and retains the external copy for the final checks:

~~~shell
(
set -eu
PATH='/usr/bin:/bin'
export PATH
trusted_python='/absolute/path/to/trusted/python3'
trusted_git='/absolute/path/to/trusted/git'
trusted_gh='/absolute/path/to/trusted/gh'
trusted_source='/path/to/owner-trusted/source-repository'
trusted_commit='<owner-trusted-immutable-commit-sha>'
trusted_sha256='<independently-trusted-64-digit-guard-sha256>'
guard_dir=$(mktemp -d "${TMPDIR:-/tmp}/project-os-review-guard.XXXXXXXX")
"$trusted_git" --no-replace-objects -C "$trusted_source" show "${trusted_commit}:scripts/check_codex_review.py" > "$guard_dir/check_codex_review.py"
"$trusted_python" -I -B - "$guard_dir/check_codex_review.py" "$trusted_sha256" <<'PY'
import hashlib
import pathlib
import sys

actual = hashlib.sha256(pathlib.Path(sys.argv[1]).read_bytes()).hexdigest()
if actual != sys.argv[2]:
    raise SystemExit('NOT_READY: trusted guard SHA-256 mismatch')
PY
chmod 400 "$guard_dir/check_codex_review.py"
chmod 500 "$guard_dir"
printf 'Retain trusted guard: %s\n' "$guard_dir/check_codex_review.py"
"$trusted_python" -I -B "$guard_dir/check_codex_review.py" --git "$trusted_git" --gh "$trusted_gh" --repo innrvoice/engineering-project-os --pr <number> --head <full-final-commit-sha> --target /path/to/clean/reviewed-checkout --dispositions /path/to/private/dispositions.json --json
)
~~~

The external directory must be outside `--target` and protected from untrusted writers. Read-only permissions prevent accidental edits; they do not establish provenance or protect against the file owner replacing it. Recheck the independently trusted hash before every invocation, retain the path and verified hash with the result and never refresh the guard from candidate bytes. The guard rejects non-isolated CLI launches before its own ordinary imports and rejects a runner whose resolved path is inside `--target`, including symlink aliases. These checks do not make an untrusted script trustworthy or prevent Python startup hooks that ran before an unsafe non-isolated launch. Programmatic imports are for trusted callers such as the unit suite, not candidate-provided launchers.

Before any subprocess, the guard requires explicit owner-trusted absolute `--git` and `--gh` paths, then binds both to resolved executable files outside `--target`; candidate paths and aliases into the checkout are rejected. Omitting either argument fails before any tool executes. The CLI and programmatic Live interface never select tools from inherited `PATH`. Commands use only the bound absolute paths and a child `PATH` containing their trusted directories plus `/usr/bin` and `/bin`. The result records tool byte hashes, identity and modes; changes during the operation block READY, including changes after the last source command. Absolute paths outside the checkout do not establish trust by themselves: the owner must select trusted tools and protect them from untrusted writers.

The guard requires the canonical bot's completed final-head code/security status, no unresolved findings or review threads and a disposition for every marked bot finding across the PR history. With no findings, the disposition file is optional. It fails closed on missing API access, timeout, incomplete pagination, changed source, changed proof or concurrent review state. It does not merge, resolve threads or publish. Run it immediately before merge and again before publication using the retained reviewed checkout; verify the squash-merged tree matches that reviewed source.

Every required package file and directory tree must exist and every actual package input must belong to the reviewed HEAD, including files hidden by Git ignore rules. The guard independently inventories the package's fixed files and directory trees before and after review validation, rejects missing or unreviewed inputs, symlinks and included non-regular entries and preserves the packager's regular cache exclusions. Ignored private working records outside package inputs remain allowed.

Dispositions stay private and bind the repository, PR, reviewed head, exact comment body and local verification evidence. Each finding uses its real comment URL, `decision: fixed` or `decision: rejected`, a reason, `comment_sha256: sha256:<actual-comment-body-digest>` and `evidence: [{path: <repository-relative-proof>, sha256: sha256:<actual-file-digest>}]`. The top-level fields are `schema_version: 1`, `repository`, `pr`, `reviewed_head` and `findings`. An accepted-risk declaration or a resolved thread alone is insufficient. Refresh review after fixes, address every remark and preserve the actual guard result as the separate acceptance evidence.

## Release sequence

1. Finish runtime, source and documentation changes and review the complete diff. Freeze exact candidate skill files; keep existing installed stable and published artifacts unchanged.
2. Run the full local suite including extracted-package checks, build an inspection/test candidate ZIP and verify reproducibility, privacy and every packaged byte. Keep host and release acceptance pending.
3. Use the exact inspected candidate for ordinary repair, knowledge review/approval, discovery and continuity scenarios in fresh Codex and ChatGPT sessions. Inspect actual findings, requests and current checkpoints; repeat recovery in separate sessions from files alone. Consolidate remaining owner steps into one counted runbook and repeat only checks affected by real changes or defects.
4. Run `python3 -B scripts/check_public_tree.py` against the staged file list and run `git diff --cached --check` before any release commit. Test the three starter prompts and supplied-material companion boundaries.
5. After the candidate changes and available checks are concrete and reviewable, obtain scoped owner authorization for commit, push and a source pull request. Report every pending acceptance gate. Creating the PR enables review and does not authorize merge or publication; do not require an already completed PR review before creating that PR.
6. Complete the authorized source pull request and wait separately for CI and completed Codex code/security reviews of the final commit. Record every finding disposition, resolve its thread and pass the final-head guard above. A new source commit requires a matching new review and affected acceptance checks.
7. With all mandatory host results and final-commit review recorded, revalidate the exact unchanged ZIP and pass the pre-publication acceptance guard. Only then recommend publication or request scoped owner authorization for merge, tag and GitHub Release. After authorization, merge and verify the merged tree, create tag `v2.3.0` on the accepted commit and attach the exact reviewed ZIP to the GitHub Release.
8. Verify the remote tag, Release metadata and downloaded asset SHA-256. Test the documented GitHub marketplace and tagged standalone routes in isolated profiles, then inspect the selected installation in a fresh Codex task. Check the installed version, exact skill bytes, bootstrap or upgrade, actual finding/checkpoint persistence and files-only recovery.
9. Report GitHub source, Release, artifact and installation results with their evidence. Report Directory status separately; a GitHub release does not establish Directory publication or ChatGPT availability. Follow the Directory checks below for an owner-authorized submission.

Do not replace package contents under an existing version. Any content change after publication requires another version.

## Release notes

The source behavior is summarized below. Actual release notes must state the verified host, artifact and publication scope rather than claiming a planned acceptance result:

`2.3.0 adds a compact read-only brief for session recovery, retaining complete unresolved requests and distinguishing record integrity from outcome readiness. Recovery guidance covers current helpers, selected older helpers and unavailable or forbidden execution without invented verification. Existing finding proofs, checkpoints, Standard, Program and schema compatibility remain supported. Final host acceptance and exact-final-commit Code/Security reviews remain distinct prerequisites for publication.`

<a id="legacy-directory"></a>

## Directory publication

Directory is the primary installation channel. Check the actual offered version and selected files through the [listing](https://chatgpt.com/plugins/plugins_6aa793523ba481918ea921c5438d98c9); neither this source version nor a GitHub release proves Directory availability. Earlier publication and submission observations remain history in the changelog.

For a future owner-authorized submission, follow the then-current official [submission guide](https://developers.openai.com/plugins/deploy/submission) and [plugin guidelines](https://developers.openai.com/plugins/plugin-guidelines). Verify the Portal form, images, capabilities, prompts, policies and exact package version. Declare the GitHub Issues support URL in both manifests, then verify actual Portal ingestion and public display separately. Record review approval, publication and fresh-host availability as distinct results. Preserve the existing published Directory artifact; repository documentation does not replace it.
