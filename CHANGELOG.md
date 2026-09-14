# Changelog

All notable changes to Engineering Project OS are documented in this file.

The project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.1] - 2026-09-14

### Fixed

- Anchored filesystem mutation and rollback to directory descriptors so parent symlink swaps cannot
  redirect writes; unsupported write environments now fail closed.
- Bound JSON parsing and concurrency hashes to the same byte snapshot across upgrade, sync and
  Program lifecycle operations.
- Rejected implicit release downgrades and guarded plan state throughout Program closure.
- Detected unprefixed PKCS#8 private-key markers in shared-knowledge sanitization.
- Handled non-object package.json values with a diagnostic instead of a traceback.
- Corrected the Expo bootstrap reviewer case and documented blocked-plan resumption.
- Corrected the copyright holder and author attribution to Pavel Bochkov Rastopchin.

### Changed

- Added public Privacy Policy, Terms and support metadata for the skills-only package.
- Aligned Codex-only metadata, listing assets and explicit invocation settings.
- Added reproducible ZIP packaging with complete public documentation, self-contained reviewer
  fixtures and extracted-artifact tests. Directory submission remains an independent distribution step.
- Kept this repository's working records local and added a publication check that preserves public
  plugin metadata, bundled templates and synthetic fixtures.

## [2.0.0] - 2026-09-13

### Changed

- Replaced installation profiles with one permanent Standard system and an explicit temporary Program
  lifecycle.
- Made short natural-language `$project-os` requests the primary Codex interface and added read-only
  help for discovering every supported request.
- Added deterministic Program start, status and close operations with complete contract validation.
- Added SHA-256 checked, tamper-evident archives for closed Program contracts.
- Added one conflict-checked helper upgrade operation with caught-failure rollback for release,
  schema, managed-content and lifecycle migrations.
- Advanced the repository manifest to schema 3 and aligned release surfaces on version 2.0.0.
- Documented safe self-hosting with a stable installed skill and candidate source helper.
- Added vector identity assets and aligned plugin and skill presentation metadata.
- Updated CI actions to current Node 24-based major releases.

## [1.0.1] - 2026-09-13

### Changed

- Clarified skill invocation, repository integration, everyday usage and release version alignment.
- Made the standalone GitHub skill the documented installation path.
- Aligned package metadata, generated repository metadata and bundled knowledge on one release
  version.
- Made repository and managed knowledge version mismatches fail the Project OS checker.
- Added lockstep release validation and documented the uniform managed-content upgrade workflow.

## [1.0.0] - 2026-09-13

### Added

- Stack-agnostic Project OS manifest with explicit record mappings.
- Non-destructive initialization and adoption of existing project systems.
- Service, web, mobile, data and delivery capability packs.
- React Native and Expo ecosystem overlay for the mobile pack.
- Deterministic detection, initialization, adoption, consistency checking and knowledge
  synchronization.
- Sanitized project and shared failure-knowledge lifecycle with conflict detection.
- Portable package manifests and repository-local packaging metadata.

[1.0.0]: https://github.com/innrvoice/engineering-project-os/releases/tag/v1.0.0
[1.0.1]: https://github.com/innrvoice/engineering-project-os/compare/v1.0.0...v1.0.1
[2.0.0]: https://github.com/innrvoice/engineering-project-os/compare/v1.0.1...v2.0.0
[2.0.1]: https://github.com/innrvoice/engineering-project-os/compare/v2.0.0...v2.0.1
