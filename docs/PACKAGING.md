# GitHub release, packaging and optional directory submission

Project OS 2.0.1 is a Codex-only, skills-only package. `policy.products: [CODEX]` and disabled implicit
invocation remain part of the skill metadata. ChatGPT support is outside this release.

GitHub releases and Universal Plugin Directory submissions are independent distribution steps.
An identity review or directory rejection does not block releasing fixes on GitHub or installing the
standalone skill from a published tag. The ZIP builder only creates a local artifact; it never uploads
or submits anything.

## Build from the working tree

From the source checkout, run the full local suite and build to a new path outside the checkout:

~~~shell
python3 -B -m unittest discover -s tests -v
python3 -B scripts/package_plugin.py --output /tmp/engineering-project-os-2.0.1-plugin.zip
python3 -B scripts/package_plugin.py --check /tmp/engineering-project-os-2.0.1-plugin.zip
~~~

The output path must not exist. Use a different temporary directory for a subsequent build. The
builder reads the current files, including intentional uncommitted changes. Stable entry ordering,
timestamps and permissions make repeated builds reproducible in the same Python/zlib environment.
Record the reported SHA-256, entry count, compressed bytes and extracted bytes for the reviewed ZIP.

The allowlist includes the portable and Codex manifests, complete skills and assets, public docs,
README, license, security policy, changelog, contributing guide and this packaging tool. It excludes
the repository's root `.agents` control plane, Git metadata, tests and bytecode caches. Hidden
`.agents` paths under skill templates are required bootstrap assets and are included.

The check validates regular file entries, normalized unique paths, size limits, CRCs, manifest
version agreement and relative public-document links. The source suite also prepares every bundled
[reviewer fixture](../skills/project-os/evals/README.md) from an extracted ZIP and exercises fresh
bootstrap, check and idempotent upgrade there. No dependencies are installed.

## Release on GitHub

Use the GitHub release flow independently of the directory:

1. Finish local source and ZIP validation; review the complete diff. After staging, run
   `python3 -B scripts/check_public_tree.py` to exclude local working records from the Git source tree.
2. Verify the documented standalone skill installation route and release/version lockstep. If the
   release claims plugin-loader support, verify that route separately before making that claim.
3. Obtain explicit authorization for commit, push, tag and GitHub Release. Validate CI and the exact
   release candidate, then publish the versioned release. Do not rewrite an existing release tag.
4. Verify the tagged installation URL and hosted documentation, including the approved Privacy and
   Terms. A separate plugin ZIP attachment is optional; its presence does not imply directory approval.

The repo may retain packaging tools, reviewer fixtures and directory preparation documentation as
development material. Keep release notes focused on shipped behavior and explicitly separate any
unverified directory availability. The generated ZIP belongs outside the source checkout.

## Submit to the directory later

The following gates apply to the optional directory submission, not to the GitHub release:

1. Confirm the verified individual developer display name from OpenAI Platform and align both plugin
   manifests. An identity still in review is not verified publisher evidence.
2. Confirm the public listing and approved privacy/terms still match the package. Revalidate the ZIP
   after metadata or policy edits. If released files must change, use a subsequent release instead of
   replacing the previous tag or silently changing an already published artifact.
3. Test discovery and the reviewer prompts through a fresh Codex plugin-loader installation. Keep
   the installed stable skill separate from candidate development.
4. Obtain explicit authorization for portal upload and review submission. Run the portal scan on the
   exact ZIP, address ingestion or reviewer feedback, and rerun affected local checks after changes.
5. Record review approval and obtain authorization for final publication. Verify public-directory
   availability separately.

An older installed Plugin Creator validator may reject `policy.products`, `brandColorDark` or
`supportURL`. The current official [submission error reference](https://developers.openai.com/plugins/deploy/submission-errors)
documents those fields. Preserve supported metadata and distinguish local validator drift from the
portal's actual ingestion result. Local validation does not establish portal compatibility.

Use the official [submission guide](https://developers.openai.com/plugins/deploy/submission) and
[plugin guidelines](https://developers.openai.com/plugins/app-guidelines) for the external review.
