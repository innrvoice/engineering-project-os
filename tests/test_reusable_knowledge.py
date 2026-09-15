from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from test_project_os import PROJECT_OS, file_hashes, run_cli


def lesson(
    identifier: str,
    applies_to: list[str] | None = None,
    *,
    mechanism: str | None = None,
    status: str = "active",
) -> dict[str, object]:
    value: dict[str, object] = {
        "id": identifier,
        "title": f"Synthetic lesson {identifier}",
        "status": status,
        "applies_to": applies_to or ["engineering"],
        "trigger": "A synthetic operation crosses an ownership boundary.",
        "mechanism": mechanism or f"A stale result for {identifier} reaches a new owner.",
        "prevention": "Record the initiating owner and verify it before applying the result.",
        "verification": ["Delay the result, change the owner and confirm the result is rejected."],
        "boundaries": ["Use only where asynchronous ownership can change."],
        "source": {"kind": "user-reviewed", "created_with": PROJECT_OS.VERSION},
    }
    value["source"]["content_hash"] = PROJECT_OS.entry_content_hash(value)
    return value


def registry(entries: list[dict[str, object]]) -> dict[str, object]:
    return {"schema_version": 1, "entries": entries}


def bundle(entries: list[dict[str, object]]) -> dict[str, object]:
    return {
        "format": "project-os-reusable-knowledge",
        "schema_version": 1,
        "created_with": PROJECT_OS.VERSION,
        "entries": entries,
    }


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def rehash(entry: dict[str, object]) -> dict[str, object]:
    entry["source"]["content_hash"] = PROJECT_OS.entry_content_hash(entry)
    return entry


def first_json(text: str) -> dict[str, object]:
    value, _ = json.JSONDecoder().raw_decode(text.lstrip())
    if not isinstance(value, dict):
        raise AssertionError(f"Expected an object report, got {type(value).__name__}")
    return value


class ReusableKnowledgeCommandTest(unittest.TestCase):
    def init(self, root: Path, *, packs: str = "none", overlays: str = "none") -> Path:
        initialized = run_cli(
            "init", "--target", str(root), "--packs", packs, "--overlays", overlays
        )
        self.assertEqual(initialized.returncode, 0, initialized.stdout + initialized.stderr)
        return root / ".agents/knowledge/reusable/failures.json"

    def test_fresh_repository_starts_with_empty_user_owned_registry(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = self.init(root)
            self.assertEqual(json.loads(path.read_text()), {"schema_version": 1, "entries": []})
            system = json.loads((root / ".agents/SYSTEM.json").read_text())
            self.assertEqual(system["schema_version"], 4)
            self.assertEqual(system["paths"]["reusable_knowledge"], ".agents/knowledge/reusable/failures.json")
            self.assertNotIn("shared_knowledge", system["paths"])
            self.assertNotIn("managed_knowledge", system)

    def test_approve_requires_reviewed_ids_and_is_dry_run_safe(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = self.init(root)
            proposal = root / "proposal.json"
            proposed = lesson("USER-ASYNC-001")
            proposed.pop("status")
            proposed.pop("source")
            write_json(proposal, {
                "format": "project-os-knowledge-proposal",
                "schema_version": 1,
                "entries": [proposed],
            })
            before = file_hashes(root)
            preview = run_cli(
                "knowledge", "approve", "--target", str(root), "--proposal", str(proposal),
                "--ids", "USER-ASYNC-001", "--dry-run",
            )
            self.assertEqual(preview.returncode, 0, preview.stdout + preview.stderr)
            self.assertEqual(file_hashes(root), before)
            applied = run_cli(
                "knowledge", "approve", "--target", str(root), "--proposal", str(proposal),
                "--ids", "USER-ASYNC-001",
            )
            self.assertEqual(applied.returncode, 0, applied.stdout + applied.stderr)
            approved = json.loads(path.read_text())["entries"]
            self.assertEqual([entry["id"] for entry in approved], ["USER-ASYNC-001"])
            self.assertEqual(approved[0]["status"], "active")
            self.assertEqual(approved[0]["source"]["kind"], "user-reviewed")
            self.assertEqual(approved[0]["source"]["created_with"], PROJECT_OS.VERSION)
            self.assertEqual(approved[0]["source"]["content_hash"], PROJECT_OS.entry_content_hash(approved[0]))
            self.assertEqual(run_cli("check", "--target", str(root)).returncode, 0)

    def test_approve_rejects_private_material_without_writes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.init(root)
            proposal = root / "private-proposal.json"
            proposed = lesson("USER-PRIVATE-001", mechanism="Read /Users/example/private.txt with sk-proj-secret.")
            proposed.pop("status")
            proposed.pop("source")
            write_json(proposal, {
                "format": "project-os-knowledge-proposal",
                "schema_version": 1,
                "entries": [proposed],
            })
            before = file_hashes(root)
            refused = run_cli(
                "knowledge", "approve", "--target", str(root), "--proposal", str(proposal),
                "--all",
            )
            self.assertNotEqual(refused.returncode, 0)
            self.assertIn("private path", refused.stdout + refused.stderr)
            self.assertIn("credential-like token", refused.stdout + refused.stderr)
            self.assertEqual(file_hashes(root), before)

    def test_approve_rejects_public_urls_and_noncanonical_ids_or_tags(self) -> None:
        for name, proposed in (
            (
                "public-url",
                lesson(
                    "USER-URL-001",
                    mechanism="The details remain in https://github.com/example/project/issues/1.",
                ),
            ),
            (
                "scheme-less-url",
                lesson(
                    "USER-URL-002",
                    mechanism="The details remain in [the issue](github.com/private-org/secret-repo/issues/1).",
                ),
            ),
            ("id", lesson(" USER-ID-001")),
            ("id-whitespace", lesson("USER ID-001")),
            ("tag", lesson("USER-TAG-001", ["mobile,web"])),
            ("tag-whitespace", lesson("USER-TAG-002", ["react native"])),
        ):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                self.init(root)
                proposed.pop("status")
                proposed.pop("source")
                proposal = root / "proposal.json"
                write_json(proposal, {
                    "format": "project-os-knowledge-proposal",
                    "schema_version": 1,
                    "entries": [proposed],
                })
                before = file_hashes(root)
                refused = run_cli(
                    "knowledge", "approve", "--target", str(root),
                    "--proposal", str(proposal), "--all",
                )
                self.assertNotEqual(refused.returncode, 0)
                self.assertEqual(file_hashes(root), before)
                if name in {"public-url", "scheme-less-url"}:
                    self.assertIn("URL", refused.stdout + refused.stderr)

    def test_approve_draft_semantic_duplicate_remains_unapproved(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = self.init(root)
            draft = lesson("USER-DRAFT-001")
            active = json.loads(json.dumps(draft))
            active["id"] = "USER-ACTIVE-001"
            active["source"]["content_hash"] = PROJECT_OS.entry_content_hash(active)
            draft["status"] = "draft"
            draft["source"]["kind"] = "migration-review-required"
            draft["source"]["content_hash"] = PROJECT_OS.entry_content_hash(draft)
            write_json(path, registry([active, draft]))
            proposal_entry = json.loads(json.dumps(draft))
            proposal_entry.pop("status")
            proposal_entry.pop("source")
            proposal = root / "proposal.json"
            write_json(proposal, {
                "format": "project-os-knowledge-proposal",
                "schema_version": 1,
                "entries": [proposal_entry],
            })
            before = path.read_bytes()
            result = run_cli(
                "knowledge", "approve", "--target", str(root),
                "--proposal", str(proposal), "--all",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn(
                "USER-DRAFT-001:USER-ACTIVE-001",
                first_json(result.stdout)["duplicates"],
            )
            self.assertEqual(path.read_bytes(), before)

    def test_export_is_deterministic_exclusive_and_source_preserving(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            root = base / "repository"
            root.mkdir()
            path = self.init(root)
            entries = [lesson("USER-Z-001"), lesson("USER-A-001")]
            write_json(path, registry(entries))
            before_registry = path.read_bytes()
            first = base / "first.json"
            second = base / "second.json"
            preview = run_cli(
                "knowledge", "export", "--target", str(root), "--output", str(first),
                "--active-only", "--dry-run",
            )
            self.assertEqual(preview.returncode, 0, preview.stdout + preview.stderr)
            self.assertFalse(first.exists())
            exported = run_cli(
                "knowledge", "export", "--target", str(root), "--output", str(first),
                "--active-only",
            )
            self.assertEqual(exported.returncode, 0, exported.stdout + exported.stderr)
            repeated = run_cli(
                "knowledge", "export", "--target", str(root), "--output", str(second),
                "--active-only",
            )
            self.assertEqual(repeated.returncode, 0, repeated.stdout + repeated.stderr)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            self.assertEqual(path.read_bytes(), before_registry)
            value = json.loads(first.read_text())
            self.assertEqual(value["format"], "project-os-reusable-knowledge")
            self.assertEqual([entry["id"] for entry in value["entries"]], ["USER-A-001", "USER-Z-001"])
            digest = "sha256:" + hashlib.sha256(first.read_bytes()).hexdigest()
            self.assertIn(digest, exported.stdout)
            existing = run_cli(
                "knowledge", "export", "--target", str(root), "--output", str(first),
                "--active-only",
            )
            self.assertNotEqual(existing.returncode, 0)
            self.assertEqual(first.read_bytes(), second.read_bytes())

    def test_export_rejects_destinations_inside_the_source_repository(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            root = base / "repository"
            root.mkdir()
            path = self.init(root)
            write_json(path, registry([lesson("USER-EXPORT-001")]))

            reserved = root / ".agents/PROGRAM.md"
            self.assertFalse(reserved.exists())
            before = file_hashes(root)
            refused = run_cli(
                "knowledge", "export", "--target", str(root), "--output", str(reserved)
            )
            self.assertNotEqual(refused.returncode, 0)
            self.assertIn(
                "outside the target repository", refused.stdout + refused.stderr
            )
            self.assertFalse(reserved.exists())
            self.assertEqual(file_hashes(root), before)
            self.assertEqual(run_cli("check", "--target", str(root)).returncode, 0)

            export_zone = root / ".agents/export-zone"
            export_zone.mkdir()
            linked_parent = base / "linked-parent"
            linked_parent.symlink_to(root / ".agents", target_is_directory=True)
            resolved_output = linked_parent / "export-zone/bundle.json"
            before = file_hashes(root)
            refused_link = run_cli(
                "knowledge", "export", "--target", str(root),
                "--output", str(resolved_output),
            )
            self.assertNotEqual(refused_link.returncode, 0)
            self.assertIn(
                "outside the target repository", refused_link.stdout + refused_link.stderr
            )
            self.assertFalse(resolved_output.exists())
            self.assertEqual(file_hashes(root), before)

    def test_export_parent_swap_cannot_redirect_the_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            root = base / "repository"
            root.mkdir()
            path = self.init(root)
            write_json(path, registry([lesson("USER-EXPORT-001")]))
            before = file_hashes(root)
            parent = base / "exports"
            moved_parent = base / "exports-pinned"
            redirected_parent = base / "redirected"
            parent.mkdir()
            redirected_parent.mkdir()
            output = parent / "bundle.json"
            original_read_regular_at = PROJECT_OS.read_regular_at
            swapped = False

            def swap_parent_after_temp_read(directory_fd: int, name: str):
                nonlocal swapped
                value = original_read_regular_at(directory_fd, name)
                if name.startswith(".project-os-export-") and not swapped:
                    swapped = True
                    parent.rename(moved_parent)
                    parent.symlink_to(redirected_parent, target_is_directory=True)
                return value

            with mock.patch.object(
                PROJECT_OS, "read_regular_at", side_effect=swap_parent_after_temp_read
            ):
                with self.assertRaisesRegex(PROJECT_OS.ProjectOSError, "Directory changed"):
                    PROJECT_OS.knowledge_export(root, output, None, False, False)

            self.assertTrue(swapped)
            self.assertFalse((redirected_parent / "bundle.json").exists())
            self.assertFalse((moved_parent / "bundle.json").exists())
            self.assertEqual(list(moved_parent.glob(".project-os-export-*.tmp")), [])
            self.assertEqual(file_hashes(root), before)

    def test_export_fails_closed_when_the_validated_temp_is_swapped_before_link(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            root = base / "repository"
            root.mkdir()
            path = self.init(root)
            write_json(path, registry([lesson("USER-EXPORT-001")]))
            before = file_hashes(root)
            parent = base / "exports"
            parent.mkdir()
            output = parent / "bundle.json"
            concurrent = b"concurrent export bytes\n"
            original_read_regular_at = PROJECT_OS.read_regular_at
            swapped_names: list[str] = []

            def swap_after_temp_read(directory_fd: int, name: str):
                value = original_read_regular_at(directory_fd, name)
                if name.startswith(".project-os-export-") and not swapped_names:
                    os.unlink(name, dir_fd=directory_fd)
                    descriptor = os.open(
                        name,
                        os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                        0o600,
                        dir_fd=directory_fd,
                    )
                    with os.fdopen(descriptor, "wb") as handle:
                        handle.write(concurrent)
                    swapped_names.append(name)
                return value

            with mock.patch.object(
                PROJECT_OS, "read_regular_at", side_effect=swap_after_temp_read
            ):
                with self.assertRaisesRegex(
                    PROJECT_OS.ProjectOSError, "Published knowledge export changed"
                ):
                    PROJECT_OS.knowledge_export(root, output, None, False, False)

            self.assertEqual(output.read_bytes(), concurrent)
            self.assertEqual((parent / swapped_names[0]).read_bytes(), concurrent)
            self.assertEqual(file_hashes(root), before)

    def test_export_write_failure_preserves_a_concurrent_final_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            root = base / "repository"
            root.mkdir()
            path = self.init(root)
            write_json(path, registry([lesson("USER-EXPORT-001")]))
            before = file_hashes(root)
            parent = base / "exports"
            parent.mkdir()
            output = parent / "bundle.json"
            concurrent = b"concurrent user file\n"

            def fail_after_concurrent_write(_descriptor: int) -> None:
                output.write_bytes(concurrent)
                raise OSError("injected export write failure")

            with mock.patch.object(
                PROJECT_OS.os, "fsync", side_effect=fail_after_concurrent_write
            ):
                with self.assertRaisesRegex(PROJECT_OS.ProjectOSError, "export failed"):
                    PROJECT_OS.knowledge_export(root, output, None, False, False)

            self.assertEqual(output.read_bytes(), concurrent)
            self.assertEqual(list(parent.glob(".project-os-export-*.tmp")), [])
            self.assertEqual(file_hashes(root), before)

    def test_drafts_cannot_be_exported_or_imported_by_any_selector(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source = base / "source"
            target = base / "target"
            source.mkdir()
            target.mkdir()
            source_path = self.init(source)
            target_path = self.init(target)
            draft = lesson("USER-DRAFT-001", status="draft")
            draft["source"]["kind"] = "migration-review-required"
            draft["source"]["content_hash"] = PROJECT_OS.entry_content_hash(draft)
            write_json(source_path, registry([draft]))

            refused_output = base / "refused.json"
            refused_export = run_cli(
                "knowledge", "export", "--target", str(source),
                "--output", str(refused_output), "--ids", "USER-DRAFT-001",
            )
            self.assertNotEqual(refused_export.returncode, 0)
            self.assertFalse(refused_output.exists())
            filtered_output = base / "filtered.json"
            filtered_export = run_cli(
                "knowledge", "export", "--target", str(source),
                "--output", str(filtered_output),
            )
            self.assertEqual(filtered_export.returncode, 0, filtered_export.stdout + filtered_export.stderr)
            self.assertEqual(json.loads(filtered_output.read_text())["entries"], [])

            before_target = target_path.read_bytes()
            refused_import = run_cli(
                "knowledge", "import", "--target", str(target),
                "--source", str(source), "--ids", "USER-DRAFT-001",
            )
            self.assertNotEqual(refused_import.returncode, 0)
            self.assertEqual(target_path.read_bytes(), before_target)
            for selector in ([], ["--all"]):
                skipped = run_cli(
                    "knowledge", "import", "--target", str(target),
                    "--source", str(source), *selector,
                )
                self.assertEqual(skipped.returncode, 0, skipped.stdout + skipped.stderr)
                self.assertEqual(target_path.read_bytes(), before_target)

    def test_default_import_selects_applicable_and_reports_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = self.init(root, packs="mobile,delivery", overlays="react-native-expo")
            source = root / "source.json"
            entries = [
                lesson("USER-CORE-001", ["engineering"]),
                lesson("USER-MOBILE-001", ["mobile"]),
                lesson("USER-EXPO-001", ["react-native", "expo"]),
                lesson("USER-WEB-001", ["web", "mobile"]),
                lesson("USER-SERVICE-001", ["service"]),
                lesson("USER-DATA-001", ["data"]),
            ]
            write_json(source, bundle(entries))
            source_before = source.read_bytes()
            before = file_hashes(root)
            preview = run_cli(
                "knowledge", "import", "--target", str(root), "--source", str(source),
                "--dry-run",
            )
            self.assertEqual(preview.returncode, 0, preview.stdout + preview.stderr)
            report = first_json(preview.stdout)
            self.assertEqual(report["selected"], [
                "USER-CORE-001", "USER-EXPO-001", "USER-MOBILE-001", "USER-WEB-001"
            ])
            self.assertEqual(
                [item["id"] for item in report["skipped"]],
                ["USER-DATA-001", "USER-SERVICE-001"],
            )
            self.assertEqual(file_hashes(root), before)
            applied = run_cli(
                "knowledge", "import", "--target", str(root), "--source", str(source)
            )
            self.assertEqual(applied.returncode, 0, applied.stdout + applied.stderr)
            self.assertEqual(
                [entry["id"] for entry in json.loads(path.read_text())["entries"]],
                ["USER-CORE-001", "USER-EXPO-001", "USER-MOBILE-001", "USER-WEB-001"],
            )
            self.assertEqual(source.read_bytes(), source_before)
            second = run_cli(
                "knowledge", "import", "--target", str(root), "--source", str(source),
                "--dry-run",
            )
            self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
            second_report = first_json(second.stdout)
            self.assertEqual(second_report["additions"], [])
            self.assertEqual(second_report["updates"], [])
            self.assertEqual(run_cli("check", "--target", str(root)).returncode, 0)

    def test_explicit_all_import_includes_out_of_stack_lessons(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = self.init(root, packs="mobile", overlays="react-native-expo")
            source = root / "source.json"
            write_json(source, bundle([
                lesson("USER-MOBILE-001", ["mobile"]),
                lesson("USER-SERVICE-001", ["service"]),
            ]))
            applied = run_cli(
                "knowledge", "import", "--target", str(root), "--source", str(source), "--all"
            )
            self.assertEqual(applied.returncode, 0, applied.stdout + applied.stderr)
            self.assertEqual(
                [entry["id"] for entry in json.loads(path.read_text())["entries"]],
                ["USER-MOBILE-001", "USER-SERVICE-001"],
            )

    def test_import_deduplicates_semantics_and_blocks_id_conflicts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = self.init(root)
            existing = lesson("USER-ORIGINAL-001")
            write_json(path, registry([existing]))
            duplicate = json.loads(json.dumps(existing))
            duplicate["id"] = "USER-DUPLICATE-999"
            duplicate["source"]["content_hash"] = PROJECT_OS.entry_content_hash(duplicate)
            duplicate_source = root / "duplicate.json"
            write_json(duplicate_source, bundle([duplicate]))
            path.write_text(PROJECT_OS.canonical_json(registry([existing])), encoding="utf-8")
            before = file_hashes(root)
            deduplicated = run_cli(
                "knowledge", "import", "--target", str(root), "--source", str(duplicate_source), "--all"
            )
            self.assertEqual(deduplicated.returncode, 0, deduplicated.stdout + deduplicated.stderr)
            self.assertTrue(
                any(item.startswith("USER-DUPLICATE-999:") for item in first_json(deduplicated.stdout)["duplicates"])
            )
            self.assertEqual(path.read_text(), PROJECT_OS.canonical_json(registry([existing])))

            conflict = lesson("USER-ORIGINAL-001", mechanism="Different reviewed content uses the same ID.")
            conflict_source = root / "conflict.json"
            write_json(conflict_source, bundle([conflict]))
            before_conflict = file_hashes(root)
            refused = run_cli(
                "knowledge", "import", "--target", str(root), "--source", str(conflict_source), "--all"
            )
            self.assertNotEqual(refused.returncode, 0)
            self.assertIn("USER-ORIGINAL-001", refused.stdout + refused.stderr)
            self.assertEqual(file_hashes(root), before_conflict)
            self.assertEqual(duplicate_source.read_bytes(), json.dumps(bundle([duplicate]), indent=2, ensure_ascii=False).encode() + b"\n")
            self.assertNotEqual(before, {})

    def test_import_accepts_source_repository_without_modifying_it(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source_root = base / "source"
            target_root = base / "target"
            source_root.mkdir()
            target_root.mkdir()
            source_path = self.init(source_root)
            self.init(target_root)
            write_json(source_path, registry([lesson("USER-DIRECT-001")]))
            source_before = file_hashes(source_root)
            imported = run_cli(
                "knowledge", "import", "--target", str(target_root), "--source", str(source_root)
            )
            self.assertEqual(imported.returncode, 0, imported.stdout + imported.stderr)
            self.assertEqual(file_hashes(source_root), source_before)
            target_entries = json.loads((
                target_root / ".agents/knowledge/reusable/failures.json"
            ).read_text())["entries"]
            self.assertEqual([entry["id"] for entry in target_entries], ["USER-DIRECT-001"])

    def test_import_rejects_private_content_and_symlink_sources(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.init(root)
            source = root / "private.json"
            write_json(source, bundle([
                lesson("USER-PRIVATE-001", mechanism="Read /Users/example/private.txt before retrying.")
            ]))
            before = file_hashes(root)
            refused = run_cli(
                "knowledge", "import", "--target", str(root), "--source", str(source), "--all"
            )
            self.assertNotEqual(refused.returncode, 0)
            self.assertEqual(file_hashes(root), before)

            actual = root / "actual.json"
            write_json(actual, bundle([lesson("USER-SAFE-001")]))
            linked = root / "linked.json"
            linked.symlink_to(actual.name)
            before_link = file_hashes(root)
            symlinked = run_cli(
                "knowledge", "import", "--target", str(root), "--source", str(linked), "--all"
            )
            self.assertNotEqual(symlinked.returncode, 0)
            self.assertEqual(file_hashes(root), before_link)

    def test_import_rejects_public_urls_and_noncanonical_tags(self) -> None:
        for name, entry in (
            (
                "public-url",
                lesson(
                    "USER-URL-001",
                    mechanism="The public report is https://github.com/example/project/issues/1.",
                ),
            ),
            (
                "scheme-less-url",
                lesson(
                    "USER-URL-002",
                    mechanism="The report is github.com/private-org/secret-repo/issues/1.",
                ),
            ),
            ("tag", lesson("USER-TAG-001", [" mobile"])),
        ):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                self.init(root)
                entry["source"]["content_hash"] = PROJECT_OS.entry_content_hash(entry)
                source = root / "source.json"
                write_json(source, bundle([entry]))
                before = file_hashes(root)
                refused = run_cli(
                    "knowledge", "import", "--target", str(root),
                    "--source", str(source), "--all",
                )
                self.assertNotEqual(refused.returncode, 0)
                self.assertEqual(file_hashes(root), before)
                if name in {"public-url", "scheme-less-url"}:
                    self.assertIn("URL", refused.stdout + refused.stderr)

    def test_export_rejects_scheme_less_and_markdown_link_urls(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = self.init(root)
            entry = lesson(
                "USER-URL-001",
                mechanism="Review [the issue](github.com/private-org/secret-repo/issues/1).",
            )
            write_json(path, registry([entry]))
            output = root / "export.json"
            refused = run_cli(
                "knowledge", "export", "--target", str(root), "--output", str(output)
            )
            self.assertNotEqual(refused.returncode, 0)
            self.assertIn("URL", refused.stdout + refused.stderr)
            self.assertFalse(output.exists())

    def test_import_rejects_invalid_bundle_shape_and_stale_hash(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.init(root)
            for name, value in (
                ("extra-field", {**bundle([lesson("USER-INVALID-001")]), "repository": "private"}),
                ("stale-hash", bundle([lesson("USER-INVALID-002")])),
            ):
                with self.subTest(name=name):
                    if name == "stale-hash":
                        value["entries"][0]["mechanism"] = "Changed after the recorded hash."
                    source = root / f"{name}.json"
                    write_json(source, value)
                    before = file_hashes(root)
                    refused = run_cli(
                        "knowledge", "import", "--target", str(root), "--source", str(source), "--all"
                    )
                    self.assertNotEqual(refused.returncode, 0)
                    self.assertEqual(file_hashes(root), before)

    def test_import_rolls_back_when_final_validation_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = self.init(root)
            source = root / "source.json"
            write_json(source, bundle([lesson("USER-ROLLBACK-001")]))
            before = path.read_bytes()
            with mock.patch.object(
                PROJECT_OS,
                "require_passing_check",
                side_effect=PROJECT_OS.ProjectOSError("injected validation failure"),
            ):
                with self.assertRaisesRegex(PROJECT_OS.ProjectOSError, "rolled back"):
                    PROJECT_OS.knowledge_import(root, source, None, True, False)
            self.assertEqual(path.read_bytes(), before)

    def test_import_rolls_back_when_source_changes_after_target_write(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            root = base / "repository"
            root.mkdir()
            path = self.init(root)
            source = base / "source.json"
            write_json(source, bundle([lesson("USER-SOURCE-RACE-001")]))
            before = file_hashes(root)
            original_check = PROJECT_OS.require_passing_check
            changed_created_with = PROJECT_OS.VERSION + "+concurrent"

            def mutate_source_after_check(*arguments: object) -> None:
                original_check(*arguments)
                changed = json.loads(source.read_text())
                changed["created_with"] = changed_created_with
                write_json(source, changed)

            with mock.patch.object(
                PROJECT_OS, "require_passing_check", side_effect=mutate_source_after_check
            ):
                with self.assertRaisesRegex(PROJECT_OS.ProjectOSError, "rolled back"):
                    PROJECT_OS.knowledge_import(root, source, None, True, False)

            self.assertEqual(file_hashes(root), before)
            self.assertEqual(json.loads(source.read_text())["created_with"], changed_created_with)

    def test_sync_transaction_rolls_back_create_replace_and_delete_on_base_exceptions(self) -> None:
        for exception in (
            KeyboardInterrupt("injected interrupt"),
            SystemExit("injected exit"),
            RuntimeError("injected unexpected failure"),
        ):
            with self.subTest(exception=type(exception).__name__), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary).resolve()
                created = root / "created.txt"
                replaced = root / "replaced.txt"
                deleted = root / "deleted.txt"
                replaced.write_bytes(b"original replacement\n")
                deleted.write_bytes(b"original deletion\n")
                before = file_hashes(root)
                replaced_digest = hashlib.sha256(replaced.read_bytes()).hexdigest()
                deleted_digest = hashlib.sha256(deleted.read_bytes()).hexdigest()

                def fail_after_write() -> None:
                    raise exception

                expected = type(exception) if isinstance(
                    exception, (KeyboardInterrupt, SystemExit)
                ) else PROJECT_OS.ProjectOSError
                with self.assertRaises(expected):
                    PROJECT_OS.execute_sync_transaction(
                        root,
                        [(created, "new file\n")],
                        [(replaced, "replacement\n", replaced_digest)],
                        [(deleted, deleted_digest)],
                        after_write=fail_after_write,
                    )
                self.assertEqual(file_hashes(root), before)
                self.assertFalse(created.exists())

    def test_atomic_write_refuses_a_swapped_temporary_entry(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "record.json"
            original = b'{"value":"original"}\n'
            target.write_bytes(original)
            expected = hashlib.sha256(original).hexdigest()
            original_read_regular_at = PROJECT_OS.read_regular_at
            swapped_names: list[str] = []

            def swap_temporary(directory_fd: int, name: str):
                if ".project-os-write." in name and not swapped_names:
                    os.unlink(name, dir_fd=directory_fd)
                    descriptor = os.open(
                        name,
                        os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                        0o600,
                        dir_fd=directory_fd,
                    )
                    with os.fdopen(descriptor, "wb") as handle:
                        handle.write(b"concurrent replacement\n")
                    swapped_names.append(name)
                return original_read_regular_at(directory_fd, name)

            directory_fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY)
            try:
                with mock.patch.object(
                    PROJECT_OS, "read_regular_at", side_effect=swap_temporary
                ):
                    with self.assertRaisesRegex(
                        PROJECT_OS.ProjectOSError, "Temporary replacement changed"
                    ):
                        PROJECT_OS.atomic_write_bytes(
                            directory_fd,
                            target.name,
                            b'{"value":"candidate"}\n',
                            expected,
                        )
            finally:
                os.close(directory_fd)

            self.assertEqual(target.read_bytes(), original)
            self.assertEqual(len(swapped_names), 1)
            self.assertEqual((root / swapped_names[0]).read_bytes(), b"concurrent replacement\n")

    def test_atomic_write_restores_original_after_a_publish_boundary_temp_swap(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "record.json"
            original = b'{"value":"original"}\n'
            concurrent = b"concurrent replacement\n"
            target.write_bytes(original)
            expected = hashlib.sha256(original).hexdigest()
            original_link_at = PROJECT_OS.link_at
            swapped = False

            def swap_at_publish(
                directory_fd: int, source: str, destination: str
            ) -> None:
                nonlocal swapped
                if ".project-os-write." in source and not swapped:
                    swapped = True
                    os.unlink(source, dir_fd=directory_fd)
                    descriptor = os.open(
                        source,
                        os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                        0o600,
                        dir_fd=directory_fd,
                    )
                    with os.fdopen(descriptor, "wb") as handle:
                        handle.write(concurrent)
                original_link_at(directory_fd, source, destination)

            directory_fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY)
            try:
                with mock.patch.object(PROJECT_OS, "link_at", side_effect=swap_at_publish):
                    with self.assertRaisesRegex(
                        PROJECT_OS.ProjectOSError, "changed at publication"
                    ):
                        PROJECT_OS.atomic_write_bytes(
                            directory_fd,
                            target.name,
                            b'{"value":"candidate"}\n',
                            expected,
                        )
            finally:
                os.close(directory_fd)

            self.assertTrue(swapped)
            self.assertEqual(target.read_bytes(), original)
            conflicts = list(root.glob(".record.json.project-os-conflict.*"))
            self.assertEqual(len(conflicts), 1)
            self.assertEqual(conflicts[0].read_bytes(), concurrent)
            self.assertEqual(list(root.glob(".record.json.project-os-backup.*")), [])

    def test_atomic_write_never_overwrites_a_target_swapped_at_publication(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "record.json"
            original = b'{"value":"original"}\n'
            concurrent = b"foreign concurrent target\n"
            target.write_bytes(original)
            expected = hashlib.sha256(original).hexdigest()
            original_replace_at = PROJECT_OS.replace_at
            swapped = False

            def swap_target_before_move(
                directory_fd: int, source: str, destination: str
            ) -> None:
                nonlocal swapped
                if ".project-os-displaced." in destination and not swapped:
                    swapped = True
                    os.unlink(source, dir_fd=directory_fd)
                    descriptor = os.open(
                        source,
                        os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                        0o600,
                        dir_fd=directory_fd,
                    )
                    with os.fdopen(descriptor, "wb") as handle:
                        handle.write(concurrent)
                original_replace_at(directory_fd, source, destination)

            directory_fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY)
            try:
                with mock.patch.object(
                    PROJECT_OS, "replace_at", side_effect=swap_target_before_move
                ):
                    with self.assertRaisesRegex(
                        PROJECT_OS.ProjectOSError, "Target changed at publication"
                    ):
                        PROJECT_OS.atomic_write_bytes(
                            directory_fd,
                            target.name,
                            b'{"value":"candidate"}\n',
                            expected,
                        )
            finally:
                os.close(directory_fd)

            self.assertTrue(swapped)
            self.assertEqual(target.read_bytes(), original)
            displaced = list(root.glob(".record.json.project-os-displaced.*"))
            self.assertEqual(len(displaced), 1)
            self.assertEqual(displaced[0].read_bytes(), concurrent)
            self.assertEqual(list(root.glob(".record.json.project-os-backup.*")), [])

    def test_sync_transaction_restores_after_replace_succeeds_then_interrupts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            target = root / "record.json"
            original = b'{"value":"original"}\r\n'
            target.write_bytes(original)
            target.chmod(0o640)
            expected = hashlib.sha256(original).hexdigest()
            before = file_hashes(root)
            original_mode = target.stat().st_mode & 0o777
            original_replace_at = PROJECT_OS.replace_at
            interrupted = False

            def replace_then_interrupt(
                directory_fd: int, source: str, destination: str
            ) -> None:
                nonlocal interrupted
                original_replace_at(directory_fd, source, destination)
                if ".project-os-displaced." in destination and not interrupted:
                    interrupted = True
                    raise KeyboardInterrupt("injected after successful replace")

            with mock.patch.object(
                PROJECT_OS, "replace_at", side_effect=replace_then_interrupt
            ):
                with self.assertRaises(KeyboardInterrupt):
                    PROJECT_OS.execute_sync_transaction(
                        root,
                        [],
                        [(target, '{"value":"candidate"}\n', expected)],
                    )

            self.assertTrue(interrupted)
            self.assertEqual(file_hashes(root), before)
            self.assertEqual(target.read_bytes(), original)
            self.assertEqual(target.stat().st_mode & 0o777, original_mode)
            self.assertEqual(list(root.glob(".record.json.project-os-*")), [])

    def test_remove_rejects_both_sides_of_a_replacement_chain(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = self.init(root)
            write_json(path, registry([lesson("USER-OLD-001")]))
            proposal_entry = lesson("USER-NEW-001")
            proposal_entry.pop("status")
            proposal_entry.pop("source")
            proposal = root / "proposal.json"
            write_json(proposal, {
                "format": "project-os-knowledge-proposal",
                "schema_version": 1,
                "entries": [proposal_entry],
            })
            revised = run_cli(
                "knowledge", "revise", "--target", str(root),
                "--id", "USER-OLD-001", "--proposal", str(proposal),
            )
            self.assertEqual(revised.returncode, 0, revised.stdout + revised.stderr)
            before = path.read_bytes()
            for entry_id in ("USER-OLD-001", "USER-NEW-001"):
                refused = run_cli(
                    "knowledge", "remove", "--target", str(root),
                    "--id", entry_id, "--confirm", entry_id,
                )
                self.assertNotEqual(refused.returncode, 0)
                self.assertIn("lifecycle-linked", refused.stdout + refused.stderr)
                self.assertEqual(path.read_bytes(), before)

    def test_retire_and_confirmed_remove_have_preview_boundaries(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = self.init(root)
            write_json(path, registry([lesson("USER-LIFECYCLE-001")]))
            before = file_hashes(root)
            preview = run_cli(
                "knowledge", "retire", "--target", str(root), "--id", "USER-LIFECYCLE-001",
                "--reason", "A safer mechanism replaced it.", "--dry-run",
            )
            self.assertEqual(preview.returncode, 0, preview.stdout + preview.stderr)
            self.assertEqual(file_hashes(root), before)
            retired = run_cli(
                "knowledge", "retire", "--target", str(root), "--id", "USER-LIFECYCLE-001",
                "--reason", "A safer mechanism replaced it.",
            )
            self.assertEqual(retired.returncode, 0, retired.stdout + retired.stderr)
            entry = json.loads(path.read_text())["entries"][0]
            self.assertEqual(entry["status"], "retired")
            self.assertEqual(entry["reason"], "A safer mechanism replaced it.")

            before_remove = file_hashes(root)
            refused = run_cli(
                "knowledge", "remove", "--target", str(root), "--id", "USER-LIFECYCLE-001",
                "--confirm", "WRONG-ID",
            )
            self.assertNotEqual(refused.returncode, 0)
            self.assertEqual(file_hashes(root), before_remove)
            removed = run_cli(
                "knowledge", "remove", "--target", str(root), "--id", "USER-LIFECYCLE-001",
                "--confirm", "USER-LIFECYCLE-001",
            )
            self.assertEqual(removed.returncode, 0, removed.stdout + removed.stderr)
            self.assertEqual(json.loads(path.read_text())["entries"], [])

    def test_retirement_bundle_updates_only_the_exact_predecessor(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source = base / "source"
            target = base / "target"
            divergent = base / "divergent"
            source.mkdir()
            target.mkdir()
            divergent.mkdir()
            source_path = self.init(source)
            target_path = self.init(target)
            divergent_path = self.init(divergent)
            original = lesson("USER-LIFECYCLE-001")
            for path in (source_path, target_path, divergent_path):
                write_json(path, registry([json.loads(json.dumps(original))]))
            retired = run_cli(
                "knowledge", "retire", "--target", str(source), "--id", "USER-LIFECYCLE-001",
                "--reason", "The lesson was superseded by a safer mechanism.",
            )
            self.assertEqual(retired.returncode, 0, retired.stdout + retired.stderr)
            retired_entry = json.loads(source_path.read_text())["entries"][0]
            self.assertEqual(retired_entry["previous_content_hash"], original["source"]["content_hash"])
            exported_path = base / "lifecycle.json"
            exported = run_cli(
                "knowledge", "export", "--target", str(source), "--output", str(exported_path)
            )
            self.assertEqual(exported.returncode, 0, exported.stdout + exported.stderr)

            imported = run_cli(
                "knowledge", "import", "--target", str(target), "--source", str(exported_path)
            )
            self.assertEqual(imported.returncode, 0, imported.stdout + imported.stderr)
            self.assertEqual(json.loads(target_path.read_text())["entries"][0]["status"], "retired")

            changed = json.loads(divergent_path.read_text())
            changed["entries"][0]["mechanism"] = "The target changed the lesson after import."
            changed["entries"][0]["source"]["content_hash"] = PROJECT_OS.entry_content_hash(
                changed["entries"][0]
            )
            write_json(divergent_path, changed)
            before = file_hashes(divergent)
            refused = run_cli(
                "knowledge", "import", "--target", str(divergent), "--source", str(exported_path)
            )
            self.assertNotEqual(refused.returncode, 0)
            self.assertIn("USER-LIFECYCLE-001", refused.stdout + refused.stderr)
            self.assertEqual(file_hashes(divergent), before)

    def test_retirement_and_replacement_tombstone_branches_conflict(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            target = base / "target"
            target.mkdir()
            target_path = self.init(target)
            original = lesson("USER-BRANCH-OLD-001")
            write_json(target_path, registry([original]))
            retired = run_cli(
                "knowledge", "retire", "--target", str(target),
                "--id", original["id"], "--reason", "This branch retired the lesson.",
            )
            self.assertEqual(retired.returncode, 0, retired.stdout + retired.stderr)
            retired_entry = json.loads(target_path.read_text())["entries"][0]

            replacement = json.loads(json.dumps(retired_entry))
            replacement["status"] = "replaced"
            replacement["reason"] = "Another branch replaced the retired lesson."
            replacement["previous_content_hash"] = retired_entry["source"]["content_hash"]
            replacement["replaced_by"] = "USER-BRANCH-NEW-001"
            replacement["source"]["content_hash"] = PROJECT_OS.entry_content_hash(
                replacement
            )
            successor = lesson("USER-BRANCH-NEW-001")
            successor["replaces"] = replacement["id"]
            successor["source"]["content_hash"] = PROJECT_OS.entry_content_hash(
                successor
            )
            incoming = base / "replacement-branch.json"
            write_json(incoming, bundle([replacement, successor]))

            before = file_hashes(target)
            refused = run_cli(
                "knowledge", "import", "--target", str(target),
                "--source", str(incoming), "--all",
            )
            self.assertNotEqual(refused.returncode, 0)
            report = first_json(refused.stdout)
            self.assertEqual(report["conflicts"], [original["id"]])
            self.assertEqual(file_hashes(target), before)

    def test_absent_predecessor_tombstone_blocks_stale_active_resurrection(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source = base / "source"
            target = base / "target"
            source.mkdir()
            target.mkdir()
            source_path = self.init(source, packs="service")
            target_path = self.init(target)
            original = lesson("USER-RETIRED-001", ["service"])
            write_json(source_path, registry([original]))
            retired = run_cli(
                "knowledge", "retire", "--target", str(source),
                "--id", "USER-RETIRED-001", "--reason", "The mechanism is obsolete.",
            )
            self.assertEqual(retired.returncode, 0, retired.stdout + retired.stderr)
            tombstone_bundle = base / "tombstone.json"
            exported = run_cli(
                "knowledge", "export", "--target", str(source),
                "--output", str(tombstone_bundle),
            )
            self.assertEqual(exported.returncode, 0, exported.stdout + exported.stderr)

            imported = run_cli(
                "knowledge", "import", "--target", str(target),
                "--source", str(tombstone_bundle),
            )
            self.assertEqual(imported.returncode, 0, imported.stdout + imported.stderr)
            retained = json.loads(target_path.read_text())["entries"]
            self.assertEqual(len(retained), 1)
            self.assertEqual(retained[0]["status"], "retired")

            stale_bundle = base / "stale.json"
            write_json(stale_bundle, bundle([original]))
            before = target_path.read_bytes()
            stale = run_cli(
                "knowledge", "import", "--target", str(target),
                "--source", str(stale_bundle), "--all",
            )
            self.assertNotEqual(stale.returncode, 0)
            self.assertIn("USER-RETIRED-001", stale.stdout + stale.stderr)
            self.assertEqual(target_path.read_bytes(), before)

    def test_default_import_closes_cross_stack_replacement_chain(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source = base / "source"
            target = base / "target"
            divergent = base / "divergent"
            source.mkdir()
            target.mkdir()
            divergent.mkdir()
            source_path = self.init(source, packs="service")
            target_path = self.init(target)
            divergent_path = self.init(divergent)
            original = lesson("USER-SERVICE-OLD-001", ["service"])
            for path in (source_path, target_path, divergent_path):
                write_json(path, registry([json.loads(json.dumps(original))]))
            proposal_entry = lesson("USER-SERVICE-NEW-001", ["service"])
            proposal_entry.pop("status")
            proposal_entry.pop("source")
            proposal = base / "proposal.json"
            write_json(proposal, {
                "format": "project-os-knowledge-proposal",
                "schema_version": 1,
                "entries": [proposal_entry],
            })
            revised = run_cli(
                "knowledge", "revise", "--target", str(source),
                "--id", original["id"], "--proposal", str(proposal),
            )
            self.assertEqual(revised.returncode, 0, revised.stdout + revised.stderr)
            output = base / "replacement.json"
            exported = run_cli(
                "knowledge", "export", "--target", str(source), "--output", str(output)
            )
            self.assertEqual(exported.returncode, 0, exported.stdout + exported.stderr)

            exact_before = target_path.read_bytes()
            incomplete = run_cli(
                "knowledge", "import", "--target", str(target), "--source", str(output),
                "--ids", "USER-SERVICE-OLD-001",
            )
            self.assertNotEqual(incomplete.returncode, 0)
            self.assertIn("incomplete lifecycle chain", incomplete.stdout + incomplete.stderr)
            self.assertEqual(target_path.read_bytes(), exact_before)

            imported = run_cli(
                "knowledge", "import", "--target", str(target), "--source", str(output)
            )
            self.assertEqual(imported.returncode, 0, imported.stdout + imported.stderr)
            report = first_json(imported.stdout)
            self.assertEqual(report["conflicts"], [])
            self.assertEqual(
                report["lifecycle_selected"],
                [
                    {"id": "USER-SERVICE-NEW-001", "reason": "replaced_by of USER-SERVICE-OLD-001"},
                    {"id": "USER-SERVICE-OLD-001", "reason": "lifecycle tombstone"},
                ],
            )
            target_entries = json.loads(target_path.read_text())["entries"]
            self.assertEqual({entry["id"] for entry in target_entries}, {
                "USER-SERVICE-OLD-001", "USER-SERVICE-NEW-001",
            })

            divergent_value = json.loads(divergent_path.read_text())
            divergent_value["entries"][0]["mechanism"] = "Locally changed target mechanism."
            divergent_value["entries"][0]["source"]["content_hash"] = (
                PROJECT_OS.entry_content_hash(divergent_value["entries"][0])
            )
            write_json(divergent_path, divergent_value)
            before = divergent_path.read_bytes()
            refused = run_cli(
                "knowledge", "import", "--target", str(divergent), "--source", str(output)
            )
            self.assertNotEqual(refused.returncode, 0)
            self.assertEqual(divergent_path.read_bytes(), before)

    def test_strict_lifecycle_hashes_reciprocity_and_export_chain(self) -> None:
        invalid_hash = lesson("USER-HASH-001")
        invalid_hash["source"]["content_hash"] = "sha256:abc"
        with self.assertRaisesRegex(PROJECT_OS.ProjectOSError, "64 hex digits"):
            PROJECT_OS.validate_reusable_value(registry([invalid_hash]), "test registry")

        invalid_active = lesson("USER-ACTIVE-001")
        invalid_active["reason"] = "Active entries cannot carry tombstone state."
        invalid_active["source"]["content_hash"] = PROJECT_OS.entry_content_hash(invalid_active)
        with self.assertRaisesRegex(PROJECT_OS.ProjectOSError, "invalid lifecycle fields"):
            PROJECT_OS.validate_reusable_value(registry([invalid_active]), "test registry")

        predecessor = lesson("USER-OLD-001")
        predecessor_hash = predecessor["source"]["content_hash"]
        predecessor["status"] = "replaced"
        predecessor["replaced_by"] = "USER-NEW-001"
        predecessor["reason"] = "A safer revision replaced it."
        predecessor["previous_content_hash"] = predecessor_hash
        predecessor["source"]["content_hash"] = PROJECT_OS.entry_content_hash(predecessor)
        nonreciprocal = lesson("USER-NEW-001")
        with self.assertRaisesRegex(PROJECT_OS.ProjectOSError, "not reciprocal"):
            PROJECT_OS.validate_reusable_value(
                registry([predecessor, nonreciprocal]), "test registry"
            )

        dangling = lesson("USER-DANGLING-001")
        dangling["replaces"] = "USER-MISSING-001"
        dangling["source"]["content_hash"] = PROJECT_OS.entry_content_hash(dangling)
        with self.assertRaisesRegex(PROJECT_OS.ProjectOSError, "dangling"):
            PROJECT_OS.validate_reusable_value(registry([dangling]), "test registry")

        successor = lesson("USER-NEW-001")
        successor["replaces"] = "USER-OLD-001"
        successor["source"]["content_hash"] = PROJECT_OS.entry_content_hash(successor)
        PROJECT_OS.validate_reusable_value(
            registry([predecessor, successor]), "test registry"
        )
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            root = base / "repository"
            root.mkdir()
            path = self.init(root)
            write_json(path, registry([predecessor, successor]))
            incomplete = base / "incomplete.json"
            refused = run_cli(
                "knowledge", "export", "--target", str(root),
                "--output", str(incomplete), "--ids", "USER-NEW-001",
            )
            self.assertNotEqual(refused.returncode, 0)
            self.assertIn("incomplete lifecycle chain", refused.stdout + refused.stderr)
            self.assertFalse(incomplete.exists())
            active_only = base / "active-only.json"
            refused_active = run_cli(
                "knowledge", "export", "--target", str(root),
                "--output", str(active_only), "--active-only",
            )
            self.assertNotEqual(refused_active.returncode, 0)
            self.assertFalse(active_only.exists())
            complete = base / "complete.json"
            exported = run_cli(
                "knowledge", "export", "--target", str(root),
                "--output", str(complete),
            )
            self.assertEqual(exported.returncode, 0, exported.stdout + exported.stderr)
            self.assertEqual(len(json.loads(complete.read_text())["entries"]), 2)

    def test_replacement_cycle_fails_check_import_and_export_without_writes(self) -> None:
        entries = [lesson(f"USER-CYCLE-{index:03d}") for index in range(1, 4)]
        for index, entry in enumerate(entries):
            entry["status"] = "replaced"
            entry["replaces"] = entries[(index - 1) % len(entries)]["id"]
            entry["replaced_by"] = entries[(index + 1) % len(entries)]["id"]
            entry["reason"] = "Synthetic invalid replacement cycle."
            entry["previous_content_hash"] = "sha256:" + "0" * 64
            entry["source"]["content_hash"] = PROJECT_OS.entry_content_hash(entry)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = self.init(root)
            source = root / "cycle-source.json"
            write_json(source, bundle(entries))
            before = path.read_bytes()
            refused_import = run_cli(
                "knowledge", "import", "--target", str(root),
                "--source", str(source), "--all",
            )
            self.assertNotEqual(refused_import.returncode, 0)
            self.assertIn("replacement cycle", refused_import.stdout + refused_import.stderr)
            self.assertEqual(path.read_bytes(), before)

            write_json(path, registry(entries))
            self.assertNotEqual(run_cli("check", "--target", str(root)).returncode, 0)
            output = root / "cycle-export.json"
            refused_export = run_cli(
                "knowledge", "export", "--target", str(root), "--output", str(output)
            )
            self.assertNotEqual(refused_export.returncode, 0)
            self.assertIn("replacement cycle", refused_export.stdout + refused_export.stderr)
            self.assertFalse(output.exists())


class SchemaThreeKnowledgeMigrationTest(unittest.TestCase):
    DISTRIBUTION = [
        ("core", 7, ["engineering"]),
        ("data", 12, ["data"]),
        ("delivery", 3, ["delivery"]),
        ("mobile", 14, ["mobile"]),
        ("overlay/react-native-expo", 23, ["mobile", "react-native", "expo"]),
        ("service", 13, ["service"]),
        ("web", 8, ["web", "mobile"]),
    ]

    def make_schema_three(self, root: Path, count: int, *, with_vnf_coverage: bool) -> dict[str, bytes]:
        vibeloop_shape = count == 55 and not with_vnf_coverage
        packs = "mobile,delivery" if vibeloop_shape else "service,mobile,data,delivery"
        initialized = run_cli(
            "init", "--target", str(root), "--packs", packs,
            "--overlays", "react-native-expo",
        )
        self.assertEqual(initialized.returncode, 0, initialized.stdout + initialized.stderr)
        reusable_path = root / ".agents/knowledge/reusable/failures.json"
        reusable_path.unlink()
        reusable_path.parent.rmdir()

        entries: list[dict[str, object]] = []
        serial = 0
        distribution = (
            [item for item in self.DISTRIBUTION if item[0] not in {"data", "service"}]
            if vibeloop_shape else self.DISTRIBUTION
        )
        for pack, amount, applies_to in distribution:
            for _ in range(amount):
                serial += 1
                if serial > count:
                    break
                value = lesson(f"LEGACY-{serial:03d}", applies_to)
                value["source"] = {
                    "kind": "project-os-pack",
                    "pack": pack,
                    "project_os_version": "2.0.5",
                    "references": [],
                }
                value["source"]["content_hash"] = PROJECT_OS.entry_content_hash(value)
                entries.append(value)
            if serial >= count:
                break
        shared_path = root / ".agents/knowledge/shared/failures.json"
        write_json(shared_path, {
            "schema_version": 1,
            "knowledge_version": "2.0.5",
            "packs": ["core", *packs.split(",")],
            "overlays": ["react-native-expo"],
            "entries": entries,
        })

        system_path = root / ".agents/SYSTEM.json"
        system = json.loads(system_path.read_text())
        system["schema_version"] = 3
        system["project_os_version"] = "2.0.5"
        system["managed_knowledge"] = {
            entry["id"]: entry["source"]["content_hash"] for entry in entries
        }
        system["paths"].pop("reusable_knowledge")
        system["paths"]["shared_knowledge"] = ".agents/knowledge/shared/failures.json"

        protected: dict[str, bytes] = {}
        if with_vnf_coverage:
            legacy = root / ".agents/knowledge/legacy/lessons.md"
            lines = ["# Legacy lessons", ""]
            for index in range(1, 83):
                lines.extend([
                    f"## OLD-{index:03d}: Synthetic legacy lesson {index}",
                    "",
                    "- Applicability: synthetic migration coverage.",
                    "- Prevention: preserve explicit user ownership.",
                    "",
                ])
            legacy.parent.mkdir(parents=True, exist_ok=True)
            legacy.write_text("\n".join(lines), encoding="utf-8")
            inventory = PROJECT_OS.scan_markdown_lessons(
                root, [".agents/knowledge/legacy"]
            )
            coverage_entries = []
            for index, item in enumerate(inventory):
                mapped = dict(item)
                if index < len(entries):
                    mapped.update({
                        "canonical_id": entries[index]["id"],
                        "disposition": "promoted",
                        "target": entries[index]["source"]["pack"],
                    })
                else:
                    mapped.update({"disposition": "retained_private", "target": "project"})
                coverage_entries.append(mapped)
            coverage_path = root / ".agents/adoption/knowledge-map.json"
            write_json(coverage_path, {
                "schema_version": 1,
                "source_count": 82,
                "mapped_source_count": 82,
                "sources": [{
                    "path": ".agents/knowledge/legacy/lessons.md",
                    "sha256": PROJECT_OS.file_sha256(legacy),
                }],
                "entries": coverage_entries,
            })
            system["paths"]["legacy_knowledge"] = [".agents/knowledge/legacy"]
            system["paths"]["knowledge_coverage"] = ".agents/adoption/knowledge-map.json"
            protected = {
                ".agents/knowledge/legacy/lessons.md": legacy.read_bytes(),
                ".agents/adoption/knowledge-map.json": coverage_path.read_bytes(),
            }
        else:
            system["paths"]["legacy_knowledge"] = []
            system["paths"]["knowledge_coverage"] = None
        write_json(system_path, system)
        return protected

    def test_vnf_shape_preserves_80_promoted_lessons_and_two_private_sources(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            protected = self.make_schema_three(root, 80, with_vnf_coverage=True)
            before = file_hashes(root)
            preview = run_cli("upgrade", "--target", str(root), "--dry-run")
            self.assertEqual(preview.returncode, 0, preview.stdout + preview.stderr)
            self.assertEqual(file_hashes(root), before)
            upgraded = run_cli("upgrade", "--target", str(root))
            self.assertEqual(upgraded.returncode, 0, upgraded.stdout + upgraded.stderr)
            self.assertFalse((root / ".agents/knowledge/shared/failures.json").exists())
            entries = json.loads((
                root / ".agents/knowledge/reusable/failures.json"
            ).read_text())["entries"]
            self.assertEqual(len(entries), 80)
            self.assertTrue(all(entry["status"] == "active" for entry in entries))
            self.assertTrue(all(entry["source"]["kind"] == "user-reviewed" for entry in entries))
            for relative, content in protected.items():
                self.assertEqual((root / relative).read_bytes(), content)
            coverage = json.loads((root / ".agents/adoption/knowledge-map.json").read_text())
            self.assertEqual(
                sum(entry["disposition"] == "retained_private" for entry in coverage["entries"]),
                2,
            )
            self.assertEqual(run_cli("check", "--target", str(root)).returncode, 0)

    def test_promoted_schema_three_lessons_preserve_lifecycle_status_and_links(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_schema_three(root, 80, with_vnf_coverage=True)
            shared_path = root / ".agents/knowledge/shared/failures.json"
            shared = json.loads(shared_path.read_text())
            retired = shared["entries"][0]
            retired_previous = retired["source"]["content_hash"]
            retired["status"] = "retired"
            retired["reason"] = "The original mechanism no longer applies."
            retired["previous_content_hash"] = retired_previous
            retired["source"]["content_hash"] = PROJECT_OS.entry_content_hash(retired)
            retired_migrated_previous = PROJECT_OS.migrated_predecessor_hash(
                retired, retired["source"]["pack"]
            )
            self.assertIsNotNone(retired_migrated_previous)

            predecessor = shared["entries"][1]
            successor = shared["entries"][2]
            predecessor_previous = predecessor["source"]["content_hash"]
            predecessor["status"] = "replaced"
            predecessor["reason"] = "A more precise lesson replaced it."
            predecessor["previous_content_hash"] = predecessor_previous
            predecessor["replaced_by"] = successor["id"]
            predecessor["source"]["content_hash"] = PROJECT_OS.entry_content_hash(predecessor)
            replaced_migrated_previous = PROJECT_OS.migrated_predecessor_hash(
                predecessor, predecessor["source"]["pack"]
            )
            self.assertIsNotNone(replaced_migrated_previous)
            successor["replaces"] = predecessor["id"]
            successor["source"]["content_hash"] = PROJECT_OS.entry_content_hash(successor)
            write_json(shared_path, shared)

            upgraded = run_cli("upgrade", "--target", str(root))
            self.assertEqual(upgraded.returncode, 0, upgraded.stdout + upgraded.stderr)
            migrated = {
                entry["id"]: entry
                for entry in json.loads((
                    root / ".agents/knowledge/reusable/failures.json"
                ).read_text())["entries"]
            }
            self.assertEqual(migrated[retired["id"]]["status"], "retired")
            self.assertEqual(migrated[retired["id"]]["reason"], retired["reason"])
            self.assertEqual(
                migrated[retired["id"]]["previous_content_hash"],
                retired_migrated_previous,
            )
            self.assertNotEqual(retired_migrated_previous, retired_previous)
            self.assertEqual(migrated[predecessor["id"]]["status"], "replaced")
            self.assertEqual(
                migrated[predecessor["id"]]["replaced_by"], successor["id"]
            )
            self.assertEqual(
                migrated[predecessor["id"]]["previous_content_hash"],
                replaced_migrated_previous,
            )
            self.assertNotEqual(replaced_migrated_previous, predecessor_previous)
            self.assertEqual(migrated[successor["id"]]["status"], "active")
            self.assertEqual(
                migrated[successor["id"]]["replaces"], predecessor["id"]
            )
            self.assertEqual(run_cli("check", "--target", str(root)).returncode, 0)

    def test_migrated_retirement_applies_to_equivalent_migrated_predecessor(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source = base / "source"
            target = base / "target"
            source.mkdir()
            target.mkdir()
            self.make_schema_three(source, 1, with_vnf_coverage=True)
            self.make_schema_three(target, 1, with_vnf_coverage=True)
            shared_path = source / ".agents/knowledge/shared/failures.json"
            shared = json.loads(shared_path.read_text())
            tombstone = shared["entries"][0]
            tombstone["previous_content_hash"] = tombstone["source"]["content_hash"]
            tombstone["status"] = "retired"
            tombstone["reason"] = "The original mechanism is obsolete."
            tombstone["source"]["content_hash"] = PROJECT_OS.entry_content_hash(tombstone)
            write_json(shared_path, shared)

            self.assertEqual(run_cli("upgrade", "--target", str(source)).returncode, 0)
            self.assertEqual(run_cli("upgrade", "--target", str(target)).returncode, 0)
            source_entry = json.loads((
                source / ".agents/knowledge/reusable/failures.json"
            ).read_text())["entries"][0]
            target_path = target / ".agents/knowledge/reusable/failures.json"
            target_entry = json.loads(target_path.read_text())["entries"][0]
            self.assertEqual(
                source_entry["previous_content_hash"],
                target_entry["source"]["content_hash"],
            )
            output = base / "retired.json"
            exported = run_cli(
                "knowledge", "export", "--target", str(source),
                "--output", str(output), "--ids", source_entry["id"],
            )
            self.assertEqual(exported.returncode, 0, exported.stdout + exported.stderr)
            imported = run_cli(
                "knowledge", "import", "--target", str(target),
                "--source", str(output), "--ids", source_entry["id"],
            )
            self.assertEqual(imported.returncode, 0, imported.stdout + imported.stderr)
            self.assertEqual(first_json(imported.stdout)["conflicts"], [])
            self.assertEqual(json.loads(target_path.read_text())["entries"][0]["status"], "retired")

    def test_unprovable_legacy_tombstone_requires_review_without_writes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_schema_three(root, 1, with_vnf_coverage=True)
            shared_path = root / ".agents/knowledge/shared/failures.json"
            shared = json.loads(shared_path.read_text())
            tombstone = shared["entries"][0]
            tombstone["status"] = "retired"
            tombstone["reason"] = "The predecessor hash cannot be proven."
            tombstone["previous_content_hash"] = "sha256:" + "0" * 64
            tombstone["source"]["content_hash"] = PROJECT_OS.entry_content_hash(tombstone)
            write_json(shared_path, shared)
            before = file_hashes(root)
            refused = run_cli("upgrade", "--target", str(root))
            self.assertNotEqual(refused.returncode, 0)
            output = refused.stdout + refused.stderr
            self.assertIn("requires explicit review", output)
            self.assertIn(tombstone["id"], output)
            self.assertIn("reason", output)
            self.assertIn("previous_content_hash", output)
            self.assertIn("status", output)
            self.assertEqual(file_hashes(root), before)

    def test_modified_unmapped_retirement_requires_review_without_writes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_schema_three(root, 1, with_vnf_coverage=False)
            shared_path = root / ".agents/knowledge/shared/failures.json"
            shared = json.loads(shared_path.read_text())
            retired = shared["entries"][0]
            retired["previous_content_hash"] = retired["source"]["content_hash"]
            retired["status"] = "retired"
            retired["reason"] = "A local review retired this lesson."
            retired["source"]["content_hash"] = PROJECT_OS.entry_content_hash(retired)
            write_json(shared_path, shared)

            before = file_hashes(root)
            refused = run_cli("upgrade", "--target", str(root))
            self.assertNotEqual(refused.returncode, 0)
            output = refused.stdout + refused.stderr
            self.assertIn(f"{retired['id']}:", output)
            self.assertIn("previous_content_hash", output)
            self.assertIn("reason", output)
            self.assertIn("status", output)
            self.assertIn("requires explicit review", output)
            self.assertEqual(file_hashes(root), before)
            preserved = json.loads(shared_path.read_text())["entries"][0]
            self.assertEqual(preserved["status"], "retired")
            self.assertEqual(preserved["reason"], retired["reason"])

    def test_unmapped_replacement_requires_review_without_writes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_schema_three(root, 1, with_vnf_coverage=False)
            shared_path = root / ".agents/knowledge/shared/failures.json"
            shared = json.loads(shared_path.read_text())
            predecessor = lesson("LEGACY-UNKNOWN-OLD-001")
            successor = lesson("LEGACY-UNKNOWN-NEW-001")
            for entry in (predecessor, successor):
                entry["source"] = {
                    "kind": "incident-derived",
                    "pack": "core",
                    "project_os_version": "2.0.5",
                    "references": [],
                }
                entry["source"]["content_hash"] = PROJECT_OS.entry_content_hash(entry)
            predecessor["previous_content_hash"] = predecessor["source"]["content_hash"]
            predecessor["status"] = "replaced"
            predecessor["reason"] = "A local review replaced this lesson."
            predecessor["replaced_by"] = successor["id"]
            predecessor["source"]["content_hash"] = PROJECT_OS.entry_content_hash(
                predecessor
            )
            successor["replaces"] = predecessor["id"]
            successor["source"]["content_hash"] = PROJECT_OS.entry_content_hash(successor)
            shared["entries"].extend([predecessor, successor])
            write_json(shared_path, shared)

            before = file_hashes(root)
            refused = run_cli("upgrade", "--target", str(root))
            self.assertNotEqual(refused.returncode, 0)
            output = refused.stdout + refused.stderr
            self.assertIn(f"{predecessor['id']}:", output)
            self.assertIn("replaced_by", output)
            self.assertIn(f"{successor['id']}:", output)
            self.assertIn("replaces", output)
            self.assertIn("requires explicit review", output)
            self.assertEqual(file_hashes(root), before)
            preserved = {
                entry["id"]: entry
                for entry in json.loads(shared_path.read_text())["entries"]
            }
            self.assertEqual(
                preserved[predecessor["id"]]["replaced_by"], successor["id"]
            )
            self.assertEqual(
                preserved[successor["id"]]["replaces"], predecessor["id"]
            )

    def test_schema_three_draft_refuses_unsupported_user_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_schema_three(root, 1, with_vnf_coverage=False)
            shared_path = root / ".agents/knowledge/shared/failures.json"
            shared = json.loads(shared_path.read_text())
            entry = shared["entries"][0]
            entry["status"] = "archived"
            entry["mechanism"] = "The user changed this lesson locally."
            entry["review_note"] = "Preserve this human review."
            entry["source"]["references"] = ["Local incident record 17"]
            entry["source"]["content_hash"] = PROJECT_OS.entry_content_hash(entry)
            write_json(shared_path, shared)

            before = file_hashes(root)
            refused = run_cli("upgrade", "--target", str(root))
            self.assertNotEqual(refused.returncode, 0)
            output = refused.stdout + refused.stderr
            self.assertIn(f"{entry['id']}:", output)
            self.assertIn("review_note", output)
            self.assertIn("source.references", output)
            self.assertIn("status", output)
            self.assertIn("supported schema-4 lesson fields", output)
            self.assertEqual(file_hashes(root), before)

    def test_promoted_active_refuses_unsupported_user_fields_without_writes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_schema_three(root, 1, with_vnf_coverage=True)
            shared_path = root / ".agents/knowledge/shared/failures.json"
            shared = json.loads(shared_path.read_text())
            entry = shared["entries"][0]
            entry["review_note"] = "Preserve this promoted user note."
            entry["source"]["review_owner"] = "repository owner"
            entry["source"]["content_hash"] = PROJECT_OS.entry_content_hash(entry)
            write_json(shared_path, shared)

            before = file_hashes(root)
            refused = run_cli("upgrade", "--target", str(root))
            self.assertNotEqual(refused.returncode, 0)
            output = refused.stdout + refused.stderr
            self.assertIn(f"{entry['id']}:", output)
            self.assertIn("review_note", output)
            self.assertIn("source.review_owner", output)
            self.assertIn("requires explicit review", output)
            self.assertEqual(file_hashes(root), before)
            preserved = json.loads(shared_path.read_text())["entries"][0]
            self.assertEqual(preserved["review_note"], entry["review_note"])
            self.assertEqual(
                preserved["source"]["review_owner"], entry["source"]["review_owner"]
            )

    def test_promoted_modified_entry_refuses_local_source_references_without_writes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_schema_three(root, 1, with_vnf_coverage=True)
            shared_path = root / ".agents/knowledge/shared/failures.json"
            shared = json.loads(shared_path.read_text())
            entry = shared["entries"][0]
            entry["mechanism"] = "The repository owner refined this promoted lesson."
            entry["source"]["references"] = ["Local incident record 17"]
            entry["source"]["content_hash"] = PROJECT_OS.entry_content_hash(entry)
            write_json(shared_path, shared)

            before = file_hashes(root)
            original_shared = shared_path.read_bytes()
            refused = run_cli("upgrade", "--target", str(root))
            self.assertNotEqual(refused.returncode, 0)
            output = refused.stdout + refused.stderr
            self.assertIn(f"{entry['id']}:", output)
            self.assertIn("source.references", output)
            self.assertIn("requires explicit review", output)
            self.assertEqual(file_hashes(root), before)
            self.assertEqual(shared_path.read_bytes(), original_shared)

    def test_legacy_registry_refuses_unknown_top_level_fields_without_writes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_schema_three(root, 1, with_vnf_coverage=False)
            shared_path = root / ".agents/knowledge/shared/failures.json"
            shared = json.loads(shared_path.read_text())
            shared["review_notes"] = "Preserve this registry-level user note."
            write_json(shared_path, shared)

            before = file_hashes(root)
            original_shared = shared_path.read_bytes()
            refused = run_cli("upgrade", "--target", str(root))
            self.assertNotEqual(refused.returncode, 0)
            output = refused.stdout + refused.stderr
            self.assertIn("requires explicit review", output)
            self.assertIn("review_notes", output)
            self.assertEqual(file_hashes(root), before)
            self.assertEqual(shared_path.read_bytes(), original_shared)

    def test_legacy_registry_refuses_invalid_schema_or_version_without_writes(self) -> None:
        for field, value, expected in (
            ("schema_version", 2, "schema_version must be 1"),
            ("knowledge_version", "9.9.9", "must match SYSTEM project_os_version"),
        ):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                self.make_schema_three(root, 1, with_vnf_coverage=False)
                shared_path = root / ".agents/knowledge/shared/failures.json"
                shared = json.loads(shared_path.read_text())
                shared[field] = value
                write_json(shared_path, shared)

                before = file_hashes(root)
                refused = run_cli("upgrade", "--target", str(root))
                self.assertNotEqual(refused.returncode, 0)
                self.assertIn(expected, refused.stdout + refused.stderr)
                self.assertEqual(file_hashes(root), before)

    def test_legacy_registry_refuses_noncanonical_pack_metadata_without_writes(self) -> None:
        for field, value in (
            ("packs", ["core", "service", "mobile", "data", "delivery", "private-custom"]),
            ("overlays", {"note": "preserve this value"}),
        ):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                self.make_schema_three(root, 1, with_vnf_coverage=False)
                shared_path = root / ".agents/knowledge/shared/failures.json"
                shared = json.loads(shared_path.read_text())
                shared[field] = value
                write_json(shared_path, shared)

                before = file_hashes(root)
                original_shared = shared_path.read_bytes()
                refused = run_cli("upgrade", "--target", str(root))
                self.assertNotEqual(refused.returncode, 0)
                output = refused.stdout + refused.stderr
                self.assertIn("requires explicit review", output)
                self.assertIn(field, output)
                self.assertEqual(file_hashes(root), before)
                self.assertEqual(shared_path.read_bytes(), original_shared)

    def test_migrated_replacement_applies_to_equivalent_migrated_predecessor(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source = base / "source"
            target = base / "target"
            source.mkdir()
            target.mkdir()
            self.make_schema_three(source, 2, with_vnf_coverage=True)
            self.make_schema_three(target, 1, with_vnf_coverage=True)
            shared_path = source / ".agents/knowledge/shared/failures.json"
            shared = json.loads(shared_path.read_text())
            predecessor, successor = shared["entries"]
            predecessor["previous_content_hash"] = predecessor["source"]["content_hash"]
            predecessor["status"] = "replaced"
            predecessor["reason"] = "A more precise lesson replaced it."
            predecessor["replaced_by"] = successor["id"]
            predecessor["source"]["content_hash"] = PROJECT_OS.entry_content_hash(predecessor)
            successor["replaces"] = predecessor["id"]
            successor["source"]["content_hash"] = PROJECT_OS.entry_content_hash(successor)
            write_json(shared_path, shared)

            self.assertEqual(run_cli("upgrade", "--target", str(source)).returncode, 0)
            self.assertEqual(run_cli("upgrade", "--target", str(target)).returncode, 0)
            source_entries = json.loads((
                source / ".agents/knowledge/reusable/failures.json"
            ).read_text())["entries"]
            source_by_id = {entry["id"]: entry for entry in source_entries}
            target_path = target / ".agents/knowledge/reusable/failures.json"
            target_entry = json.loads(target_path.read_text())["entries"][0]
            migrated_predecessor = source_by_id[predecessor["id"]]
            self.assertEqual(
                migrated_predecessor["previous_content_hash"],
                target_entry["source"]["content_hash"],
            )
            output = base / "replaced.json"
            exported = run_cli(
                "knowledge", "export", "--target", str(source), "--output", str(output)
            )
            self.assertEqual(exported.returncode, 0, exported.stdout + exported.stderr)
            imported = run_cli(
                "knowledge", "import", "--target", str(target), "--source", str(output)
            )
            self.assertEqual(imported.returncode, 0, imported.stdout + imported.stderr)
            self.assertEqual(first_json(imported.stdout)["conflicts"], [])
            target_by_id = {
                entry["id"]: entry for entry in json.loads(target_path.read_text())["entries"]
            }
            self.assertEqual(target_by_id[predecessor["id"]]["status"], "replaced")
            self.assertEqual(target_by_id[successor["id"]]["replaces"], predecessor["id"])

    def test_vibeloop_shape_removes_55_exact_managed_seeds(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_schema_three(root, 55, with_vnf_coverage=False)
            upgraded = run_cli("upgrade", "--target", str(root))
            self.assertEqual(upgraded.returncode, 0, upgraded.stdout + upgraded.stderr)
            reusable = json.loads((
                root / ".agents/knowledge/reusable/failures.json"
            ).read_text())
            self.assertEqual(reusable, {"schema_version": 1, "entries": []})
            system = json.loads((root / ".agents/SYSTEM.json").read_text())
            self.assertEqual(system["schema_version"], 4)
            self.assertNotIn("managed_knowledge", system)
            self.assertNotIn("shared_knowledge", system["paths"])
            self.assertEqual(run_cli("check", "--target", str(root)).returncode, 0)

    def test_modified_or_unknown_schema_three_entry_migrates_as_draft(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_schema_three(root, 3, with_vnf_coverage=False)
            shared_path = root / ".agents/knowledge/shared/failures.json"
            shared = json.loads(shared_path.read_text())
            shared["entries"][0]["mechanism"] = "The user changed this legacy lesson locally."
            shared["entries"][0]["source"]["content_hash"] = PROJECT_OS.entry_content_hash(
                shared["entries"][0]
            )
            unknown = lesson("LEGACY-UNKNOWN-001", ["engineering"])
            unknown["source"] = {
                "kind": "incident-derived",
                "pack": "core",
                "project_os_version": "2.0.5",
                "references": [],
            }
            unknown["source"]["content_hash"] = PROJECT_OS.entry_content_hash(unknown)
            shared["entries"].append(unknown)
            write_json(shared_path, shared)
            upgraded = run_cli("upgrade", "--target", str(root))
            self.assertEqual(upgraded.returncode, 0, upgraded.stdout + upgraded.stderr)
            migrated = json.loads((
                root / ".agents/knowledge/reusable/failures.json"
            ).read_text())["entries"]
            self.assertEqual({entry["id"] for entry in migrated}, {"LEGACY-001", "LEGACY-UNKNOWN-001"})
            self.assertTrue(all(entry["status"] == "draft" for entry in migrated))
            self.assertTrue(all(entry["source"]["kind"] == "migration-review-required" for entry in migrated))

    def test_vnf_bundle_import_into_vibeloop_selects_55_and_skips_25(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source = base / "vnf"
            target = base / "vibeloop"
            source.mkdir()
            target.mkdir()
            self.make_schema_three(source, 80, with_vnf_coverage=True)
            self.make_schema_three(target, 55, with_vnf_coverage=False)
            self.assertEqual(run_cli("upgrade", "--target", str(source)).returncode, 0)
            self.assertEqual(run_cli("upgrade", "--target", str(target)).returncode, 0)
            output = base / "vnf-reusable.json"
            exported = run_cli(
                "knowledge", "export", "--target", str(source), "--output", str(output),
                "--active-only",
            )
            self.assertEqual(exported.returncode, 0, exported.stdout + exported.stderr)
            source_before = file_hashes(source)
            preview = run_cli(
                "knowledge", "import", "--target", str(target), "--source", str(output),
                "--dry-run",
            )
            self.assertEqual(preview.returncode, 0, preview.stdout + preview.stderr)
            report = first_json(preview.stdout)
            self.assertEqual(len(report["selected"]), 55)
            self.assertEqual(len(report["skipped"]), 25)
            applied = run_cli(
                "knowledge", "import", "--target", str(target), "--source", str(output)
            )
            self.assertEqual(applied.returncode, 0, applied.stdout + applied.stderr)
            target_entries = json.loads((
                target / ".agents/knowledge/reusable/failures.json"
            ).read_text())["entries"]
            self.assertEqual(len(target_entries), 55)
            self.assertEqual(file_hashes(source), source_before)
            repeated = run_cli(
                "knowledge", "import", "--target", str(target), "--source", str(source),
                "--dry-run",
            )
            self.assertEqual(repeated.returncode, 0, repeated.stdout + repeated.stderr)
            repeated_report = first_json(repeated.stdout)
            self.assertEqual(repeated_report["additions"], [])
            self.assertEqual(repeated_report["updates"], [])


if __name__ == "__main__":
    unittest.main()
