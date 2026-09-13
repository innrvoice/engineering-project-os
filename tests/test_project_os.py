from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "skills" / "project-os" / "scripts" / "project_os.py"
FIXTURES = ROOT / "tests" / "fixtures"

SPEC = importlib.util.spec_from_file_location("project_os", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
PROJECT_OS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PROJECT_OS)


def run_cli(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-B", str(SCRIPT), *arguments],
        check=False,
        capture_output=True,
        text=True,
    )


def copy_fixture(name: str, parent: Path) -> Path:
    target = parent / name
    shutil.copytree(FIXTURES / name, target)
    return target


def file_hashes(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file() and not path.is_symlink()
    }


class KnowledgeAssetTest(unittest.TestCase):
    def test_all_public_knowledge_is_complete_unique_hashed_and_sanitized(self) -> None:
        knowledge_root = ROOT / "skills" / "project-os" / "assets" / "knowledge"
        entries: list[dict[str, object]] = []
        for path in sorted(knowledge_root.rglob("*.json")):
            value = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(value["schema_version"], 1, path)
            entries.extend(value["entries"])

        self.assertEqual(len(entries), 80)
        self.assertEqual(len({entry["id"] for entry in entries}), 80)
        required = {
            "id",
            "title",
            "status",
            "applies_to",
            "trigger",
            "mechanism",
            "prevention",
            "verification",
            "boundaries",
            "source",
        }
        denylist = re.compile(
            r"\b(?:VNF|Vibes?|A059|Astra|Discuss|Feel)\b|"
            r"owner-(?:accepted|reported|provided)|Package\s+\d+|"
            r"record_vibe_views|publish-(?:vibe|entity)|MOB-NATIVE-020|"
            r"\.\./\.\./audit/evidence|/Users/|/home/|C:\\Users\\",
            re.IGNORECASE,
        )
        for entry in entries:
            self.assertTrue(required.issubset(entry), entry.get("id"))
            for key in required.difference({"source"}):
                self.assertTrue(entry[key], f"{entry['id']}:{key}")
            source = entry["source"]
            self.assertIn(source["kind"], {"project-os-pack", "incident-derived"})
            if not source["references"]:
                self.assertEqual(source["kind"], "incident-derived", entry["id"])
            for reference in source["references"]:
                self.assertTrue(reference.startswith("https://"), reference)
            self.assertEqual(source["content_hash"], PROJECT_OS.entry_content_hash(entry))
            self.assertIsNone(denylist.search(json.dumps(entry, ensure_ascii=False)), entry["id"])

    def test_manifest_and_runtime_versions_match(self) -> None:
        portable = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
        compatibility = json.loads(
            (ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        self.assertEqual(portable["version"], "1.0.0")
        self.assertEqual(compatibility["version"], "1.0.0")
        self.assertEqual(PROJECT_OS.VERSION, "1.0.0")
        self.assertEqual(portable["name"], compatibility["name"])


class DetectionTest(unittest.TestCase):
    def test_languages_are_signals_not_behavioral_profiles(self) -> None:
        detected = run_cli("detect", "--target", str(FIXTURES / "language-only"))
        self.assertEqual(detected.returncode, 0, detected.stderr)
        value = json.loads(detected.stdout)
        self.assertEqual(value["toolchain_signals"], ["python", "clojure"])
        self.assertEqual(value["recommended_packs"], [])
        self.assertEqual(value["recommended_overlays"], [])

    def test_react_dom_repository_selects_web(self) -> None:
        detected = run_cli("detect", "--target", str(FIXTURES / "react-web"))
        self.assertEqual(detected.returncode, 0, detected.stderr)
        value = json.loads(detected.stdout)
        self.assertEqual(value["recommended_packs"], ["web"])

    def test_mature_expo_repository_detects_capabilities_without_web_false_positive(self) -> None:
        detected = run_cli("detect", "--target", str(FIXTURES / "mature-mobile"))
        self.assertEqual(detected.returncode, 0, detected.stderr)
        value = json.loads(detected.stdout)
        self.assertEqual(
            value["recommended_packs"], ["service", "mobile", "data", "delivery"]
        )
        self.assertEqual(value["recommended_overlays"], ["react-native-expo"])

    def test_bare_react_native_with_expo_package_does_not_select_expo_overlay(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            (target / "package.json").write_text(
                json.dumps(
                    {
                        "dependencies": {
                            "react-native": "0.86.0",
                            "@expo/vector-icons": "15.0.0",
                        }
                    }
                ),
                encoding="utf-8",
            )
            detected = run_cli("detect", "--target", str(target))
            self.assertEqual(detected.returncode, 0, detected.stderr)
            value = json.loads(detected.stdout)
            self.assertEqual(value["recommended_packs"], ["mobile"])
            self.assertEqual(value["recommended_overlays"], [])


class InitializationTest(unittest.TestCase):
    def test_dry_run_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "empty"
            target.mkdir()
            result = run_cli("init", "--target", str(target), "--dry-run")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(list(target.iterdir()), [])

    def test_lite_init_and_check_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "empty"
            target.mkdir()
            initialized = run_cli(
                "init", "--target", str(target), "--packs", "none", "--overlays", "none"
            )
            self.assertEqual(initialized.returncode, 0, initialized.stderr)
            self.assertTrue((target / ".agents" / "SYSTEM.json").is_file())
            checked = run_cli("check", "--target", str(target))
            self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
            knowledge = json.loads(
                (target / ".agents" / "knowledge" / "shared" / "failures.json").read_text()
            )
            self.assertEqual(len(knowledge["entries"]), 7)

    def test_full_init_requires_and_creates_program_and_history(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "full"
            target.mkdir()
            initialized = run_cli(
                "init",
                "--target",
                str(target),
                "--mode",
                "full",
                "--packs",
                "service,data",
                "--overlays",
                "none",
            )
            self.assertEqual(initialized.returncode, 0, initialized.stderr)
            self.assertTrue((target / ".agents" / "PROGRAM.md").is_file())
            self.assertTrue((target / ".agents" / "history" / "README.md").is_file())
            self.assertEqual(run_cli("check", "--target", str(target)).returncode, 0)

    def test_init_refuses_existing_instructions_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            agents = target / "AGENTS.md"
            agents.write_text("# Existing\n", encoding="utf-8")
            before = file_hashes(target)
            result = run_cli("init", "--target", str(target))
            self.assertEqual(result.returncode, 2)
            self.assertIn("use adopt", result.stderr)
            self.assertEqual(file_hashes(target), before)

    def test_init_can_preserve_pre_routed_agents_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            agents = target / "AGENTS.md"
            original = (
                "# Existing\n\nRead `.agents/CONTEXT.md` and `.agents/STATE.md` first.\n"
            )
            agents.write_text(original, encoding="utf-8")
            result = run_cli(
                "init",
                "--target",
                str(target),
                "--packs",
                "none",
                "--overlays",
                "none",
                "--allow-existing-agents",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(agents.read_text(encoding="utf-8"), original)
            self.assertEqual(run_cli("check", "--target", str(target)).returncode, 0)

    def test_overlay_requires_mobile_pack(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = run_cli(
                "init",
                "--target",
                temporary,
                "--packs",
                "none",
                "--overlays",
                "react-native-expo",
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("requires packs: mobile", result.stderr)

    def test_operation_rollback_removes_earlier_created_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            blocking_parent = root / "blocking-parent"
            blocking_parent.write_text("not a directory", encoding="utf-8")
            operations = [
                ("create", root / "first.txt", "first\n"),
                ("create", blocking_parent / "second.txt", "second\n"),
            ]
            with self.assertRaises(PROJECT_OS.ProjectOSError):
                PROJECT_OS.execute_operations(root, operations, dry_run=False)
            self.assertFalse((root / "first.txt").exists())

    def test_symlink_escape_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as temporary, tempfile.TemporaryDirectory() as outside:
            root = Path(temporary).resolve()
            (root / "link").symlink_to(Path(outside), target_is_directory=True)
            with self.assertRaises(PROJECT_OS.ProjectOSError):
                PROJECT_OS.execute_operations(
                    root,
                    [("create", root / "link" / "escaped.txt", "no\n")],
                    dry_run=False,
                )
            self.assertFalse((Path(outside) / "escaped.txt").exists())


class AdoptionTest(unittest.TestCase):
    def test_dry_run_is_read_only_and_reports_complete_mapping(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = copy_fixture("mature-mobile", Path(temporary))
            before = file_hashes(target)
            adopted = run_cli("adopt", "--target", str(target), "--dry-run", "--inventory")
            self.assertEqual(adopted.returncode, 0, adopted.stdout + adopted.stderr)
            report = json.loads(adopted.stdout.split("\ndry-run:", 1)[0])
            self.assertTrue(report["safe_to_adopt"])
            self.assertEqual(report["legacy_knowledge_count"], 1)
            self.assertEqual(report["existing_files_modified"], [])
            self.assertEqual(file_hashes(target), before)

    def test_adopt_preserves_existing_records_and_passes_check(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = copy_fixture("mature-mobile", Path(temporary))
            before = file_hashes(target)
            adopted = run_cli("adopt", "--target", str(target))
            self.assertEqual(adopted.returncode, 0, adopted.stdout + adopted.stderr)
            after = file_hashes(target)
            for relative, digest in before.items():
                self.assertEqual(after[relative], digest, relative)
            system = json.loads((target / ".agents" / "SYSTEM.json").read_text())
            self.assertEqual(system["packs"], ["service", "mobile", "data", "delivery"])
            self.assertEqual(system["overlays"], ["react-native-expo"])
            knowledge = json.loads(
                (target / ".agents" / "knowledge" / "shared" / "failures.json").read_text()
            )
            self.assertEqual(len(knowledge["entries"]), 80)
            checked = run_cli("check", "--target", str(target))
            self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)

    def test_missing_or_drifted_coverage_blocks_before_system_write(self) -> None:
        for mode in ("missing", "drifted"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as temporary:
                target = copy_fixture("mature-mobile", Path(temporary))
                coverage = target / ".agents" / "adoption" / "knowledge-map.json"
                if mode == "missing":
                    coverage.unlink()
                else:
                    lesson = target / ".agents" / "knowledge" / "legacy" / "lessons.md"
                    lesson.write_text(lesson.read_text() + "\nChanged.\n", encoding="utf-8")
                result = run_cli("adopt", "--target", str(target))
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertFalse((target / ".agents" / "SYSTEM.json").exists())

    def test_malformed_registry_and_ambiguous_owner_block_adoption(self) -> None:
        for mode in ("malformed", "ambiguous"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as temporary:
                target = copy_fixture("mature-mobile", Path(temporary))
                if mode == "malformed":
                    (target / ".agents" / "plans" / "index.json").write_text(
                        "{broken\n", encoding="utf-8"
                    )
                else:
                    other = target / "docs" / "plans"
                    other.mkdir(parents=True)
                    (other / "index.json").write_text(
                        json.dumps({"version": 1, "execution_state": "idle", "plans": []}),
                        encoding="utf-8",
                    )
                result = run_cli("adopt", "--target", str(target))
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertFalse((target / ".agents" / "SYSTEM.json").exists())

    def test_empty_secondary_evidence_directory_is_not_an_ambiguity(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = copy_fixture("mature-mobile", Path(temporary))
            (target / "docs" / "audit" / "evidence").mkdir(parents=True)
            result = run_cli("adopt", "--target", str(target), "--dry-run")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_adoption_rechecks_preserved_sources_immediately_before_writing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = copy_fixture("mature-mobile", Path(temporary))
            original_discover = PROJECT_OS.discover_adoption

            def discover_then_mutate(
                root: Path, include_inventory: bool = False
            ) -> dict[str, object]:
                report = original_discover(root, include_inventory=include_inventory)
                (target / ".agents" / "plans" / "index.json").write_text(
                    "{changed after discovery\n", encoding="utf-8"
                )
                return report

            with mock.patch.object(
                PROJECT_OS, "discover_adoption", side_effect=discover_then_mutate
            ), mock.patch("builtins.print"):
                with self.assertRaisesRegex(
                    PROJECT_OS.ProjectOSError, "Adoption sources changed after discovery"
                ):
                    PROJECT_OS.adopt_project(target, dry_run=False, include_inventory=False)

            self.assertFalse((target / ".agents" / "SYSTEM.json").exists())
            self.assertFalse((target / ".agents" / "packs").exists())
            self.assertFalse(
                (target / ".agents" / "knowledge" / "shared" / "failures.json").exists()
            )


class ValidationAndSyncTest(unittest.TestCase):
    def init(self, target: Path, packs: str = "none", overlays: str = "none", mode: str = "lite") -> None:
        result = run_cli(
            "init",
            "--target",
            str(target),
            "--mode",
            mode,
            "--packs",
            packs,
            "--overlays",
            overlays,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_active_plan_is_derived_and_optional_but_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            self.init(target)
            plan_path = target / ".agents" / "plans" / "001.md"
            plan_path.write_text("# Plan\n", encoding="utf-8")
            index_path = target / ".agents" / "plans" / "index.json"
            index = json.loads(index_path.read_text())
            index["execution_state"] = "running"
            index["plans"] = [
                {"id": "001", "status": "active", "path": ".agents/plans/001.md", "outcome": "x"}
            ]
            index_path.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
            self.assertEqual(run_cli("check", "--target", str(target)).returncode, 0)
            index["active_plan"] = "999"
            index_path.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
            failed = run_cli("check", "--target", str(target))
            self.assertEqual(failed.returncode, 1)
            self.assertIn("active_plan must match", failed.stdout)

    def test_unmanaged_dev_token_passes_but_reserved_token_in_pack_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            self.init(target, packs="web")
            history = target / ".agents" / "history"
            history.mkdir()
            (history / "debug.md").write_text("Flag: __DEV__.\n", encoding="utf-8")
            self.assertEqual(run_cli("check", "--target", str(target)).returncode, 0)
            pack = target / ".agents" / "packs" / "web.md"
            pack.write_text(pack.read_text() + "\n__PROJECT_NAME__\n", encoding="utf-8")
            failed = run_cli("check", "--target", str(target))
            self.assertEqual(failed.returncode, 1)
            self.assertIn("unresolved template tokens", failed.stdout)

    def test_shared_private_material_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            self.init(target)
            path = target / ".agents" / "knowledge" / "shared" / "failures.json"
            value = json.loads(path.read_text())
            value["entries"][0]["mechanism"] += " /Users/example/private.txt sk-proj-secret"
            path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
            failed = run_cli("check", "--target", str(target))
            self.assertEqual(failed.returncode, 1)
            self.assertIn("private path", failed.stdout)
            self.assertIn("credential-like token", failed.stdout)

    def test_check_rejects_symlinked_mutable_and_managed_paths(self) -> None:
        for kind in ("shared knowledge", "managed guidance"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as temporary:
                target = Path(temporary)
                self.init(target, packs="web")
                if kind == "shared knowledge":
                    path = target / ".agents" / "knowledge" / "shared" / "failures.json"
                else:
                    path = target / ".agents" / "packs" / "web.md"
                actual = path.with_name("actual-" + path.name)
                path.rename(actual)
                path.symlink_to(actual.name)

                checked = run_cli("check", "--target", str(target))
                self.assertEqual(checked.returncode, 1, checked.stdout + checked.stderr)
                self.assertIn("must not use symlink components", checked.stdout)

    def test_decoded_windows_private_path_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            self.init(target)
            path = target / ".agents" / "knowledge" / "shared" / "failures.json"
            value = json.loads(path.read_text())
            value["entries"][0]["mechanism"] = "C:\\Users\\alice\\private.txt"
            value["entries"][0]["source"]["content_hash"] = PROJECT_OS.entry_content_hash(
                value["entries"][0]
            )
            path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
            failed = run_cli("check", "--target", str(target))
            self.assertEqual(failed.returncode, 1, failed.stdout + failed.stderr)
            self.assertIn("private path", failed.stdout)

    def test_sync_conflict_is_unsuccessful_and_byte_preserving(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            self.init(target)
            path = target / ".agents" / "knowledge" / "shared" / "failures.json"
            value = json.loads(path.read_text())
            value["entries"][0]["title"] = "Local edit"
            path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
            before = path.read_bytes()
            synced = run_cli("sync-knowledge", "--target", str(target))
            self.assertEqual(synced.returncode, 1, synced.stdout + synced.stderr)
            self.assertIn("sync aborted", synced.stdout)
            self.assertEqual(path.read_bytes(), before)

    def test_rehashed_local_edit_still_conflicts_with_installed_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            self.init(target)
            path = target / ".agents" / "knowledge" / "shared" / "failures.json"
            value = json.loads(path.read_text())
            value["entries"][0]["title"] = "Local edit with a recomputed hash"
            value["entries"][0]["source"]["content_hash"] = PROJECT_OS.entry_content_hash(
                value["entries"][0]
            )
            path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
            before = file_hashes(target)
            synced = run_cli("sync-knowledge", "--target", str(target))
            self.assertEqual(synced.returncode, 1, synced.stdout + synced.stderr)
            self.assertIn("differs locally", synced.stdout)
            self.assertEqual(file_hashes(target), before)

    def test_clean_installed_baseline_can_receive_an_upstream_entry_update(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            PROJECT_OS.init_project(target, "lite", "none", "none", False)
            current = PROJECT_OS.composed_knowledge([], [])
            desired_entries = json.loads(json.dumps(current["entries"]))
            desired_entries[0]["title"] = "Upstream revised title"
            desired_entries[0]["source"]["content_hash"] = PROJECT_OS.entry_content_hash(
                desired_entries[0]
            )
            with mock.patch.object(PROJECT_OS, "seed_documents", return_value=desired_entries):
                result = PROJECT_OS.sync_knowledge(target, "selected", "selected", False)
                self.assertEqual(result, 0)
            updated = json.loads(
                (target / ".agents" / "knowledge" / "shared" / "failures.json").read_text()
            )
            self.assertEqual(updated["entries"][0]["title"], "Upstream revised title")

    def test_malformed_membership_values_fail_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            self.init(target)
            system_path = target / ".agents" / "SYSTEM.json"
            system = json.loads(system_path.read_text())
            system["mode"] = []
            system_path.write_text(json.dumps(system, indent=2) + "\n", encoding="utf-8")
            failed = run_cli("check", "--target", str(target))
            self.assertEqual(failed.returncode, 1, failed.stdout + failed.stderr)
            self.assertNotIn("Traceback", failed.stderr)

    def test_sync_requires_exact_system_selection_and_schema_v2(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            self.init(target, packs="service,mobile")
            before = file_hashes(target)
            subset = run_cli(
                "sync-knowledge",
                "--target",
                str(target),
                "--packs",
                "mobile",
                "--overlays",
                "none",
            )
            self.assertEqual(subset.returncode, 2)
            self.assertEqual(file_hashes(target), before)

            system_path = target / ".agents" / "SYSTEM.json"
            system = json.loads(system_path.read_text())
            system["schema_version"] = 1
            system_path.write_text(json.dumps(system, indent=2) + "\n", encoding="utf-8")
            before_old = file_hashes(target)
            old = run_cli("sync-knowledge", "--target", str(target))
            self.assertEqual(old.returncode, 2)
            self.assertIn("migrate older state explicitly", old.stderr)
            self.assertEqual(file_hashes(target), before_old)

    def test_sync_preserves_file_mode(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            self.init(target, packs="mobile", overlays="react-native-expo")
            path = target / ".agents" / "knowledge" / "shared" / "failures.json"
            path.chmod(0o644)
            synced = run_cli("sync-knowledge", "--target", str(target))
            self.assertEqual(synced.returncode, 0, synced.stdout + synced.stderr)
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o644)

    def test_directory_cannot_masquerade_as_existing_guidance(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            self.init(target, packs="web")
            pack = target / ".agents" / "packs" / "web.md"
            pack.unlink()
            pack.mkdir()
            knowledge = target / ".agents" / "knowledge" / "shared" / "failures.json"
            before = knowledge.read_bytes()
            synced = run_cli("sync-knowledge", "--target", str(target))
            self.assertEqual(synced.returncode, 2)
            self.assertEqual(knowledge.read_bytes(), before)

    def test_external_config_tokens_canonical_order_and_full_history_are_checked(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "project"
            target.mkdir()
            self.init(target, packs="service,mobile", mode="full")
            system_path = target / ".agents" / "SYSTEM.json"
            system = json.loads(system_path.read_text())

            alternate = root / "alternate.json"
            tokenized = dict(system)
            tokenized["note"] = "__PROJECT_NAME__"
            alternate.write_text(json.dumps(tokenized, indent=2) + "\n", encoding="utf-8")
            token_check = run_cli(
                "check", "--target", str(target), "--config", str(alternate)
            )
            self.assertEqual(token_check.returncode, 1)
            self.assertIn("unresolved template tokens", token_check.stdout)

            system["packs"] = ["mobile", "service"]
            system["pack_paths"] = [
                ".agents/packs/mobile.md",
                ".agents/packs/service.md",
            ]
            system_path.write_text(json.dumps(system, indent=2) + "\n", encoding="utf-8")
            order_check = run_cli("check", "--target", str(target))
            self.assertEqual(order_check.returncode, 1)
            self.assertIn("canonical order", order_check.stdout)

            system["packs"] = ["service", "mobile"]
            system["pack_paths"] = [
                ".agents/packs/service.md",
                ".agents/packs/mobile.md",
            ]
            system["paths"]["history"] = None
            system_path.write_text(json.dumps(system, indent=2) + "\n", encoding="utf-8")
            history_check = run_cli("check", "--target", str(target))
            self.assertEqual(history_check.returncode, 1)
            self.assertIn("paths.history is required", history_check.stdout)


if __name__ == "__main__":
    unittest.main()
