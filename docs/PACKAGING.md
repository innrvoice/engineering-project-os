# Universal Plugin Directory and release packaging

Project OS 2.1.0 is the current source-tree release candidate for ChatGPT and Codex. The Universal Plugin Directory is the primary installation route. Product gating is omitted because the accepted skill policy contains only `allow_implicit_invocation`; implicit invocation lets the selected plugin expose the skill for an explicit or clearly matching Project OS request. ChatGPT users can select `@Engineering Project OS` and Codex users can select `$project-os` explicitly.

GitHub releases and Universal Plugin Directory submissions are separate gates. At preparation time, by owner report, Directory version 2.0.5 is public and its skill works in ChatGPT Classic and Codex. Versions 2.0.2 and 2.0.3 were intermediate Directory-only releases and have no GitHub tags or GitHub Releases. The Directory does not expose the server-side package hash, so installed behavior does not prove that hash independently.

## Build from the working tree

From the source checkout, run the full local suite and build to a new path outside the checkout:

~~~shell
python3 -B -m unittest discover -s tests -v
python3 -B scripts/package_plugin.py --output /private/tmp/engineering-project-os-2.1.0-plugin.zip
python3 -B scripts/package_plugin.py --check /private/tmp/engineering-project-os-2.1.0-plugin.zip
~~~

The output path must not exist. Use a different temporary directory for a subsequent build. The builder reads the current files, including intentional uncommitted changes. Stable entry ordering, timestamps and permissions make repeated builds reproducible in the same Python/zlib environment. Record the reported SHA-256, entry count, compressed bytes and extracted bytes for the reviewed ZIP.

These commands verify packaging from the source tree. Do not replace the contents of a published Directory version in place. Any package-content change after publication requires a new patch version.

The allowlist includes the portable and Codex manifests, complete skills and assets, public docs, README, license, security policy, changelog, contributing guide and this packaging tool. It excludes the repository's root `.agents` control plane, Git metadata, tests and bytecode caches. Hidden `.agents` paths under skill templates are required bootstrap assets and are included.

The check validates regular file entries, normalized unique paths, size limits, CRCs, manifest version agreement, relative public-document links and Markdown layout. Public prose paragraphs and list items must each stay on one physical line so plugin renderers cannot expose source wrapping as stray fragments. The source suite also prepares every bundled [reviewer fixture](../skills/project-os/evals/README.md) from an extracted ZIP and exercises fresh bootstrap, check and idempotent upgrade there. No dependencies are installed.

The package must not contain release-managed failure-knowledge JSON. Capability packs and overlays remain product guidance in Markdown. User-owned project and reusable registries exist only inside connected repositories or user-created bundles.

## Coordinate the 2.1.0 release

Directory availability, the Git tag and the GitHub Release remain separate outcomes. Complete them through explicit gates:

1. Finish local source and ZIP validation, review the complete diff and run `python3 -B scripts/check_public_tree.py` against the staged file list before any commit.
2. Test the candidate in fresh ChatGPT and Codex conversations. Confirm that overview works without repository files and that repository operations request the input they actually need.
3. Obtain explicit authorization for a release branch, pull request, merge, tag and GitHub Release.
4. Wait for required checks, publish `v2.1.0` and verify the standalone Codex installation from the tagged URL in a fresh task.
5. Submit and publish Directory 2.1.0 only through the owner's separate Portal action and acceptance gate.

The repo may retain packaging tools, reviewer fixtures and Directory preparation documentation as development material. Keep release notes focused on shipped behavior and explicitly separate Directory availability from GitHub publication. The generated ZIP belongs outside the source checkout.

## Prepare Directory 2.1.0

Keep published Directory version 2.0.5 available while 2.1.0 is tested and reviewed.

1. Keep the release version synchronized in the helper, manifests, marketplace metadata, reusable knowledge migration fixtures, tests and documentation.
2. Confirm the verified individual developer display name and align both plugin manifests.
3. Confirm the public listing, Directory link, Privacy Policy and Terms match the exact package. Revalidate the ZIP after every metadata or policy edit.
4. Upload the new ZIP through `Upload draft` and keep published 2.0.5 available during review.
5. Walk through Plugin Info, Prompts, Skills and Submit. Verify images, capabilities, the three exact starter prompts, release notes and policy declarations before submission.
6. Record review approval separately from publication. Do not claim 2.1.0 is public before the owner publishes it and verifies a fresh installation.

The skill metadata file `skills/project-os/agents/openai.yaml` uses only `policy.allow_implicit_invocation: true`. Do not add `policy.products`; the Directory validator accepts no other policy field in this file. Its `short_description` must contain 25 to 64 characters and its `default_prompt` must mention `$project-os` explicitly. Do not add unsupported interface fields such as `brandColorDark` or `supportURL`; enter customer support information in the Portal listing and use supported `brandColor` or `logoDark` metadata when needed. Local validation does not establish portal compatibility.

Use these exact public metadata values:

- Name: `Engineering Project OS`
- Subtitle: `Resume work. Reuse lessons.`
- Skill short description: `Resume work and reuse failure knowledge`
- Description: `Use this when developers need durable repository state across ChatGPT and Codex sessions or want verified failure lessons to move safely between their own projects. It inspects, bootstraps, validates, repairs and upgrades Project OS records with previews before writes. Do not use it for ordinary one-session coding or as an automatic global knowledge service.`
- Capabilities: `Resume engineering work across sessions`; `Set up and validate repository state`; `Capture verified failure knowledge`; `Reuse user-owned lessons across projects`.

The three Directory starter prompts must match both manifests exactly:

1. `Tell me what Project OS does, how it works and when I should use it.`
2. `Help me set up Project OS for this project and start with a safe preview.`
3. `Help me reuse verified failure knowledge from an earlier project in this one.`

Replay the discovery golden set in `skills/project-os/evals/discovery.json` before submission. It covers direct requests, implicit continuity requests, incomplete requests, negative controls and edge cases. This skills-only plugin has no MCP tools and no plugin-owned UI, so tool metadata and UI screenshots do not apply.

The reviewer submission must include at least five positive cases and three negative cases. Cover overview without files, safe setup, batch knowledge preparation, direct repository import, bundle import, a privacy refusal, an ID conflict and an unrelated coding request that must not activate Project OS.

Use these release notes: `2.1.0 replaces release-managed shared failure knowledge with a user-owned reusable library. Developers can review, export and import verified lessons between their own projects with applicability previews, conflict checks and no automatic upload or global database. It also refreshes discovery metadata, documentation and the social preview.`

Use the official [metadata optimization guide](https://developers.openai.com/plugins/guides/optimize-metadata), [submission guide](https://developers.openai.com/plugins/deploy/submission) and [plugin guidelines](https://developers.openai.com/plugins/app-guidelines) for the external review.
