# Universal Plugin Directory and release packaging

Project OS 2.0.4 is the current source-tree and Universal Plugin Directory version for ChatGPT and Codex. The Universal Plugin Directory is the primary installation route. Product gating is omitted because the accepted skill policy contains only `allow_implicit_invocation`; implicit invocation lets the selected plugin expose the skill for a clear Project OS request. ChatGPT users can select `@Engineering Project OS` and Codex users can select `$project-os` explicitly.

GitHub releases and Universal Plugin Directory submissions are separate gates. By owner report, Directory version 2.0.4 is public and its skill works in ChatGPT Classic and Codex. Versions 2.0.2 and 2.0.3 were intermediate Directory-only releases and have no GitHub tags or GitHub Releases. The GitHub release line moves directly from `v2.0.1` to `v2.0.4`. The Directory does not expose the server-side package hash, so installed behavior does not prove that hash independently.

## Build from the working tree

From the source checkout, run the full local suite and build to a new path outside the checkout:

~~~shell
python3 -B -m unittest discover -s tests -v
python3 -B scripts/package_plugin.py --output /private/tmp/engineering-project-os-2.0.4-plugin.zip
python3 -B scripts/package_plugin.py --check /private/tmp/engineering-project-os-2.0.4-plugin.zip
~~~

The output path must not exist. Use a different temporary directory for a subsequent build. The builder reads the current files, including intentional uncommitted changes. Stable entry ordering, timestamps and permissions make repeated builds reproducible in the same Python/zlib environment. Record the reported SHA-256, entry count, compressed bytes and extracted bytes for the reviewed ZIP.

These commands verify packaging from the source tree. Do not submit a newly built 2.0.4 archive as a replacement for public Directory 2.0.4. Any replacement package requires a new patch version.

The allowlist includes the portable and Codex manifests, complete skills and assets, public docs, README, license, security policy, changelog, contributing guide and this packaging tool. It excludes the repository's root `.agents` control plane, Git metadata, tests and bytecode caches. Hidden `.agents` paths under skill templates are required bootstrap assets and are included.

The check validates regular file entries, normalized unique paths, size limits, CRCs, manifest version agreement, relative public-document links and Markdown layout. Public prose paragraphs and list items must each stay on one physical line so plugin renderers cannot expose source wrapping as stray fragments. The source suite also prepares every bundled [reviewer fixture](../skills/project-os/evals/README.md) from an extracted ZIP and exercises fresh bootstrap, check and idempotent upgrade there. No dependencies are installed.

## Complete the GitHub 2.0.4 release

Directory 2.0.4 publication does not create a Git tag or GitHub Release. Complete the remaining source release through these separate gates:

1. Finish local source and ZIP validation; review the complete diff. After staging, run `python3 -B scripts/check_public_tree.py` to exclude local working records from the Git source tree.
2. Obtain explicit authorization for a release branch, pull request, merge, tag and GitHub Release.
3. Wait for required checks, publish `v2.0.4` and verify that its changelog comparison starts at `v2.0.1`.
4. Verify the standalone Codex installation from the tagged URL in a fresh task.

The repo may retain packaging tools, reviewer fixtures and Directory preparation documentation as development material. Keep release notes focused on shipped behavior and explicitly separate Directory availability from GitHub publication. The generated ZIP belongs outside the source checkout.

## Prepare a future Directory version

Do not replace the contents of public 2.0.4 in place. Any package-content change after publication requires a new patch version. Keep the current published version available while its replacement is reviewed.

1. Bump the release version in the helper, manifests, marketplace metadata, bundled knowledge, tests and documentation.
2. Confirm the verified individual developer display name and align both plugin manifests.
3. Confirm the public listing, Directory link, Privacy Policy and Terms match the exact package. Revalidate the ZIP after every metadata or policy edit.
4. Upload the new ZIP through `Upload draft` and keep the published 2.0.4 available during review.
5. Walk through Plugin Info, Prompts, Skills and Submit. Verify images, capabilities, the three exact starter prompts, release notes and policy declarations before submission.
6. Record review approval separately from publication. Do not publish until the coordinated GitHub gate above is complete.

The skill metadata file `skills/project-os/agents/openai.yaml` uses only `policy.allow_implicit_invocation: true`. Do not add `policy.products`; the Directory validator accepts no other policy field in this file. Manifest fields such as `brandColorDark` and `supportURL` remain separate from skill policy. Local validation does not establish portal compatibility.

The three Directory starter prompts must match both manifests exactly:

1. `Help me choose the right Project OS setup for my project.`
2. `Create a safe Project OS starter package for my project.`
3. `Review my existing Project OS setup and tell me what to fix.`

Use the official [submission guide](https://developers.openai.com/plugins/deploy/submission) and [plugin guidelines](https://developers.openai.com/plugins/app-guidelines) for the external review.
