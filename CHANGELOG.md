# Changelog

All notable changes to Engineering Project OS are documented in this file.

The project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.5] - 2026-09-15

### Added

- Added a read-only `overview` route that explains what Project OS does, how it works and when a developer should use it without requiring repository files.
- Added a discovery golden set with direct, indirect, incomplete, negative and edge cases for ChatGPT and Codex activation checks.
- Added an explicit cross-project failure-knowledge lifecycle that keeps project evidence local, sanitizes reusable lessons and requires deliberate review before reuse.

### Changed

- Replaced the first Directory starter prompt with a product overview while retaining starter-package creation and existing-setup review as the other two entry points.
- Tightened plugin and skill metadata around resumable engineering work, repository continuity, evidence and reusable failure knowledge.
- Replaced the previous identity mark with a filled Resume symbol and refreshed the repository and social-preview artwork around the 2.0.5 positioning.
- Reworked the README and architectural explanation for developers so the audience, immediate benefits and compounding knowledge value are clear before setup details.
- Documented conservative implicit activation for clear Project OS continuity requests while excluding ordinary coding and generic project management.
- Kept technical setup, usage, reference and packaging guidance synchronized with the 2.0.5 behavior and release gates.

## [2.0.4] - 2026-09-14

### Changed

- Made the Universal Plugin Directory the primary installation route for ChatGPT and Codex, with the tagged standalone skill documented as a Codex-only alternative.
- Added the public Directory page to the README and setup guide, paired `@Engineering Project OS` and `$project-os` usage, update guidance and explicit repository-input boundaries.
- Reworked the README and architectural explanation around resumable engineering state while keeping setup, usage, reference, packaging, security and legal documents technical.
- Added ChatGPT and Codex capability metadata, reviewer guidance and starter prompts.
- Added a package gate that rejects hard-wrapped Markdown prose or list items and normalized public Markdown to one physical line per paragraph or item.
- Replaced file-upload instructions in the three ChatGPT starter buttons with outcome-focused setup, starter-package and review requests.
- Allowed ChatGPT setup advice and starter-package generation to begin from a project description or selected files while keeping existing-setup claims evidence-based.
- Documented full repository ZIP uploads as an optional deep-inspection input rather than the normal entry point.
- Included all changes from the Directory-only 2.0.2 and 2.0.3 versions in the GitHub 2.0.4 release line.

### Fixed

- Enabled implicit skill exposure when the plugin is selected so ChatGPT can invoke Project OS.
- Prevented the ChatGPT workflow from treating an empty host workspace as the supplied repository or falling back to a generic audit when repository files are missing.
- Kept `skills/project-os/agents/openai.yaml` within the accepted policy schema by using only `allow_implicit_invocation: true`.
- Increased all packaged SVG canvas dimensions to satisfy Directory validation.

## 2.0.3 - 2026-09-14 - Universal Plugin Directory only

### Changed

- Made the Universal Plugin Directory the primary installation route for ChatGPT and Codex, with the tagged standalone skill documented as a Codex-only alternative.
- Added the public Directory page to the README and setup guide, paired `@Engineering Project OS` and `$project-os` usage, update guidance and explicit repository-input boundaries.
- Reworked the README and architectural explanation around resumable engineering state while keeping setup, usage, reference, packaging, security and legal documents technical.
- Added ChatGPT and Codex capability metadata, reviewer guidance and starter prompts that ask for repository files when a ChatGPT conversation has none.
- Added a package gate that rejects hard-wrapped Markdown prose or list items and normalized public Markdown to one physical line per paragraph or item.

### Fixed

- Enabled implicit skill exposure when the plugin is selected so ChatGPT can invoke Project OS.
- Prevented the ChatGPT workflow from treating an empty host workspace as the supplied repository or falling back to a generic audit when repository files are missing.
- Kept `skills/project-os/agents/openai.yaml` within the accepted policy schema by using only `allow_implicit_invocation: true`.
- Increased all packaged SVG canvas dimensions to satisfy Directory validation.

## 2.0.2 - 2026-09-14 - Universal Plugin Directory only

### Changed

- Enabled the Project OS skill in both ChatGPT and Codex.
- Replaced Codex-only `$project-os` starter prompts with product-neutral prompts suitable for the shared Universal Plugin Directory listing.
- Updated plugin and skill metadata to explain explicit invocation in each product.

## [2.0.1] - 2026-09-14

### Fixed

- Anchored filesystem mutation and rollback to directory descriptors so parent symlink swaps cannot redirect writes; unsupported write environments now fail closed.
- Bound JSON parsing and concurrency hashes to the same byte snapshot across upgrade, sync and Program lifecycle operations.
- Rejected implicit release downgrades and guarded plan state throughout Program closure.
- Detected unprefixed PKCS#8 private-key markers in shared-knowledge sanitization.
- Handled non-object package.json values with a diagnostic instead of a traceback.
- Corrected the Expo bootstrap reviewer case and documented blocked-plan resumption.
- Corrected the copyright holder and author attribution to Pavel Bochkov Rastopchin.

### Changed

- Added public Privacy Policy, Terms and support metadata for the skills-only package.
- Aligned Codex-only metadata, listing assets and explicit invocation settings.
- Added reproducible ZIP packaging with complete public documentation, self-contained reviewer fixtures and extracted-artifact tests. Directory submission remains an independent distribution step.
- Kept this repository's working records local and added a publication check that preserves public plugin metadata, bundled templates and synthetic fixtures.

## [2.0.0] - 2026-09-13

### Changed

- Replaced installation profiles with one permanent Standard system and an explicit temporary Program lifecycle.
- Made short natural-language `$project-os` requests the primary Codex interface and added read-only help for discovering every supported request.
- Added deterministic Program start, status and close operations with complete contract validation.
- Added SHA-256 checked, tamper-evident archives for closed Program contracts.
- Added one conflict-checked helper upgrade operation with caught-failure rollback for release, schema, managed-content and lifecycle migrations.
- Advanced the repository manifest to schema 3 and aligned release surfaces on version 2.0.0.
- Documented safe self-hosting with a stable installed skill and candidate source helper.
- Added vector identity assets and aligned plugin and skill presentation metadata.
- Updated CI actions to current Node 24-based major releases.

## [1.0.1] - 2026-09-13

### Changed

- Clarified skill invocation, repository integration, everyday usage and release version alignment.
- Made the standalone GitHub skill the documented installation path.
- Aligned package metadata, generated repository metadata and bundled knowledge on one release version.
- Made repository and managed knowledge version mismatches fail the Project OS checker.
- Added lockstep release validation and documented the uniform managed-content upgrade workflow.

## [1.0.0] - 2026-09-13

### Added

- Stack-agnostic Project OS manifest with explicit record mappings.
- Non-destructive initialization and adoption of existing project systems.
- Service, web, mobile, data and delivery capability packs.
- React Native and Expo ecosystem overlay for the mobile pack.
- Deterministic detection, initialization, adoption, consistency checking and knowledge synchronization.
- Sanitized project and shared failure-knowledge lifecycle with conflict detection.
- Portable package manifests and repository-local packaging metadata.

[1.0.0]: https://github.com/innrvoice/engineering-project-os/releases/tag/v1.0.0
[1.0.1]: https://github.com/innrvoice/engineering-project-os/compare/v1.0.0...v1.0.1
[2.0.0]: https://github.com/innrvoice/engineering-project-os/compare/v1.0.1...v2.0.0
[2.0.1]: https://github.com/innrvoice/engineering-project-os/compare/v2.0.0...v2.0.1
[2.0.4]: https://github.com/innrvoice/engineering-project-os/compare/v2.0.1...v2.0.4
[2.0.5]: https://github.com/innrvoice/engineering-project-os/compare/v2.0.4...v2.0.5
