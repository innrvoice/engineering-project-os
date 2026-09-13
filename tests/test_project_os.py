from __future__ import annotations

import hashlib
import importlib.util
import json
import os
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


def write_program_definition(root: Path) -> Path:
    path = root / "program-definition.json"
    path.write_text(
        json.dumps(
            {
                "initiative": "Ship a safe platform migration",
                "outcome": "Move all supported consumers without behavior drift.",
                "authority": ["The repository contract", "Current user instructions"],
                "phases": [
                    {
                        "name": "Inventory",
                        "outcome": "Establish the migration baseline.",
                        "exit_conditions": ["Every consumer is classified."],
                    },
                    {
                        "name": "Migration",
                        "outcome": "Apply and verify the migration.",
                        "exit_conditions": ["Every supported consumer passes its checks."],
                    },
                ],
                "exit_conditions": ["All phases satisfy their exit conditions."],
                "evidence_requirements": ["Focused checks are recorded."],
                "cost_boundary": ["Do not redesign application behavior."],
                "exclusions": ["Production deployment is excluded."],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return path


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
            r"\b(?:internal-product-name|private-device-alias|private-person-name|private-feature-name)\b|"
            r"owner-(?:accepted|reported|provided)|Package\s+\d+|"
            r"record_private_entity|publish-private-entity|PROJECT-INCIDENT-\d+|"
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

    def test_release_version_is_in_lockstep(self) -> None:
        portable = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
        compatibility = json.loads(
            (ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        marketplace = json.loads(
            (ROOT / ".agents" / "plugins" / "marketplace.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(PROJECT_OS.VERSION, "2.0.0")
        self.assertEqual(PROJECT_OS.SCHEMA_VERSION, 3)
        self.assertEqual(portable["version"], PROJECT_OS.VERSION)
        self.assertEqual(compatibility["version"], PROJECT_OS.VERSION)
        self.assertEqual(portable["name"], compatibility["name"])
        portable_interface = portable["extensions"]["com.openai"]["interface"]
        self.assertEqual(
            portable_interface["defaultPrompt"],
            compatibility["interface"]["defaultPrompt"],
        )
        for key in ("brandColor", "composerIcon", "logo"):
            self.assertEqual(
                portable_interface[key], compatibility["interface"][key], key
            )
        self.assertEqual(portable_interface["brandColor"], "#B7F34A")
        for key in ("composerIcon", "logo"):
            asset = ROOT / portable_interface[key].removeprefix("./")
            self.assertTrue(asset.is_file(), asset)
        self.assertEqual(
            (ROOT / "assets" / "icon.svg").read_bytes(),
            (ROOT / "skills" / "project-os" / "assets" / "icon-small.svg").read_bytes(),
        )
        self.assertEqual(
            (ROOT / "assets" / "logo.svg").read_bytes(),
            (ROOT / "skills" / "project-os" / "assets" / "icon-large.svg").read_bytes(),
        )
        skill_interface = (
            ROOT / "skills" / "project-os" / "agents" / "openai.yaml"
        ).read_text(encoding="utf-8")
        self.assertIn('icon_small: "./assets/icon-small.svg"', skill_interface)
        self.assertIn('icon_large: "./assets/icon-large.svg"', skill_interface)
        self.assertIn('brand_color: "#B7F34A"', skill_interface)
        self.assertTrue(
            all(len(prompt) <= 128 for prompt in portable_interface["defaultPrompt"])
        )
        self.assertTrue(
            all(
                prompt.startswith("$project-os ")
                for prompt in portable_interface["defaultPrompt"]
            )
        )
        self.assertEqual(
            marketplace["plugins"][0]["source"]["ref"],
            f"v{PROJECT_OS.VERSION}",
        )
        self.assertEqual(
            portable["$schema"],
            "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
        )

        knowledge_root = ROOT / "skills" / "project-os" / "assets" / "knowledge"
        for path in sorted(knowledge_root.rglob("*.json")):
            value = json.loads(path.read_text(encoding="utf-8"))
            for entry in value["entries"]:
                self.assertEqual(
                    entry["source"]["project_os_version"], PROJECT_OS.VERSION, path
                )

        active_release_versions: set[str] = set()
        markdown_paths = [
            ROOT / "README.md",
            ROOT / "SECURITY.md",
            *(ROOT / "docs").glob("*.md"),
        ]
        for path in markdown_paths:
            active_release_versions.update(
                re.findall(
                    r"\bv?(\d+\.\d+\.\d+)\b", path.read_text(encoding="utf-8")
                )
            )
        self.assertEqual(active_release_versions, {PROJECT_OS.VERSION})


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

    def test_clojure_backend_dependencies_select_service_and_data(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            (target / "deps.edn").write_text(
                "{:deps {metosin/reitit {:mvn/version \"0.8.0\"}\n"
                "        http-kit/http-kit {:mvn/version \"2.8.0\"}\n"
                "        com.github.seancorfield/next.jdbc {:mvn/version \"1.3.0\"}}}\n",
                encoding="utf-8",
            )
            detected = run_cli("detect", "--target", str(target))
            self.assertEqual(detected.returncode, 0, detected.stderr)
            value = json.loads(detected.stdout)
            self.assertEqual(value["toolchain_signals"], ["clojure"])
            self.assertEqual(value["recommended_packs"], ["service", "data"])

    def test_bare_clojure_manifest_selects_no_capability_pack(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            (target / "deps.edn").write_text(
                "{:deps {org.clojure/clojure {:mvn/version \"1.12.0\"}}}\n",
                encoding="utf-8",
            )
            detected = run_cli("detect", "--target", str(target))
            self.assertEqual(detected.returncode, 0, detected.stderr)
            value = json.loads(detected.stdout)
            self.assertEqual(value["recommended_packs"], [])

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

    def test_standard_init_and_check_pass(self) -> None:
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
            system = json.loads((target / ".agents" / "SYSTEM.json").read_text())
            knowledge = json.loads(
                (target / ".agents" / "knowledge" / "shared" / "failures.json").read_text()
            )
            self.assertEqual(system["project_os_version"], PROJECT_OS.VERSION)
            self.assertEqual(system["schema_version"], 3)
            self.assertEqual(system["mode"], "standard")
            self.assertIsNone(system["active_program"])
            self.assertFalse((target / ".agents" / "PROGRAM.md").exists())
            self.assertFalse((target / ".agents" / "history").exists())
            self.assertEqual(knowledge["knowledge_version"], PROJECT_OS.VERSION)
            self.assertEqual(len(knowledge["entries"]), 7)

    def test_init_preserves_unrelated_agents_namespace(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "standard"
            target.mkdir()
            plugin = target / ".agents" / "plugins" / "marketplace.json"
            plugin.parent.mkdir(parents=True)
            plugin.write_text('{"plugins": []}\n', encoding="utf-8")
            original = plugin.read_bytes()
            initialized = run_cli(
                "init",
                "--target",
                str(target),
                "--packs",
                "service,data",
                "--overlays",
                "none",
            )
            self.assertEqual(initialized.returncode, 0, initialized.stderr)
            self.assertEqual(plugin.read_bytes(), original)
            self.assertFalse((target / ".agents" / "PROGRAM.md").exists())
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

    def test_sync_transaction_rolls_back_create_when_fsync_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            destination = root / "created" / "record.json"
            with mock.patch.object(PROJECT_OS.os, "fsync", side_effect=OSError("disk failure")):
                with self.assertRaisesRegex(PROJECT_OS.ProjectOSError, "rolled back"):
                    PROJECT_OS.execute_sync_transaction(
                        root, [(destination, '{"ok": true}\n')], []
                    )
            self.assertFalse(destination.exists())
            self.assertFalse(destination.parent.exists())

    def test_sync_transaction_rollback_preserves_exact_crlf_bytes_and_mode(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            destination = root / "record.txt"
            original = b"first\r\nsecond\r\n"
            destination.write_bytes(original)
            destination.chmod(0o640)
            digest = hashlib.sha256(original).hexdigest()

            def fail_validation() -> None:
                raise PROJECT_OS.ProjectOSError("injected validation failure")

            with self.assertRaisesRegex(PROJECT_OS.ProjectOSError, "rolled back"):
                PROJECT_OS.execute_sync_transaction(
                    root,
                    [],
                    [(destination, "replacement\n", digest)],
                    after_write=fail_validation,
                )
            self.assertEqual(destination.read_bytes(), original)
            self.assertEqual(stat.S_IMODE(destination.stat().st_mode), 0o640)

    def test_sync_rollback_preserves_concurrently_recreated_deleted_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            destination = root / "record.txt"
            original = b"original\n"
            concurrent = b"concurrent replacement\n"
            destination.write_bytes(original)

            def recreate_and_fail() -> None:
                destination.write_bytes(concurrent)
                raise PROJECT_OS.ProjectOSError("injected validation failure")

            with self.assertRaisesRegex(PROJECT_OS.ProjectOSError, "rollback incomplete"):
                PROJECT_OS.execute_sync_transaction(
                    root,
                    [],
                    [],
                    [(destination, hashlib.sha256(original).hexdigest())],
                    after_write=recreate_and_fail,
                )
            self.assertEqual(destination.read_bytes(), concurrent)
            tombstones = list(root.glob(".record.txt.project-os-delete.*"))
            self.assertEqual(len(tombstones), 1)
            self.assertEqual(tombstones[0].read_bytes(), original)

    def test_sync_rollback_preserves_concurrently_replaced_created_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            destination = root / "record.txt"
            concurrent = b"concurrent replacement\n"

            def replace_and_fail() -> None:
                destination.unlink()
                destination.write_bytes(concurrent)
                raise PROJECT_OS.ProjectOSError("injected validation failure")

            with self.assertRaisesRegex(PROJECT_OS.ProjectOSError, "rollback incomplete"):
                PROJECT_OS.execute_sync_transaction(
                    root,
                    [(destination, "created\n")],
                    [],
                    after_write=replace_and_fail,
                )
            self.assertEqual(destination.read_bytes(), concurrent)

    def test_operation_rollback_preserves_concurrently_replaced_created_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            destination = root / "first.txt"
            original_create_parent = PROJECT_OS.create_parent_directories
            calls = 0

            def replace_before_second_create(
                operation_root: Path, parent: Path, created: list[Path]
            ) -> None:
                nonlocal calls
                calls += 1
                if calls == 2:
                    destination.unlink()
                    destination.write_bytes(b"concurrent replacement\n")
                    raise PROJECT_OS.ProjectOSError("injected operation failure")
                original_create_parent(operation_root, parent, created)

            with mock.patch.object(
                PROJECT_OS,
                "create_parent_directories",
                side_effect=replace_before_second_create,
            ):
                with self.assertRaisesRegex(
                    PROJECT_OS.ProjectOSError, "rollback incomplete"
                ):
                    PROJECT_OS.execute_operations(
                        root,
                        [
                            ("create", destination, "created\n"),
                            ("create", root / "second" / "record.txt", "second\n"),
                        ],
                        dry_run=False,
                    )
            self.assertEqual(destination.read_bytes(), b"concurrent replacement\n")

    def test_operation_create_writes_exact_utf8_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            destination = root / "record.txt"
            PROJECT_OS.execute_operations(
                root, [("create", destination, "first\nsecond\n")], dry_run=False
            )
            self.assertEqual(destination.read_bytes(), b"first\nsecond\n")

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

    def test_adoption_rechecks_indexed_archive_bytes_before_writing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = copy_fixture("mature-mobile", Path(temporary))
            history = target / ".agents" / "history"
            history.mkdir()
            archive = history / "snapshot.md"
            archive.write_bytes(b"trusted snapshot\r\n")
            (history / "index.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "entries": [
                            {
                                "id": "snapshot-001",
                                "kind": "snapshot",
                                "path": ".agents/history/snapshot.md",
                                "sha256": "sha256:"
                                + hashlib.sha256(archive.read_bytes()).hexdigest(),
                            }
                        ],
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            original_discover = PROJECT_OS.discover_adoption

            def discover_then_mutate(
                root: Path, include_inventory: bool = False
            ) -> dict[str, object]:
                report = original_discover(root, include_inventory=include_inventory)
                archive.write_bytes(b"changed snapshot\n")
                return report

            with mock.patch.object(
                PROJECT_OS, "discover_adoption", side_effect=discover_then_mutate
            ), mock.patch("builtins.print"):
                with self.assertRaisesRegex(
                    PROJECT_OS.ProjectOSError, "Adoption sources changed after discovery"
                ):
                    PROJECT_OS.adopt_project(target, dry_run=False, include_inventory=False)
            self.assertFalse((target / ".agents" / "SYSTEM.json").exists())

    def test_adoption_reruns_transitive_plan_and_evidence_validation(self) -> None:
        for relative in (
            ".agents/plans/001-active.md",
            ".agents/audit/evidence/FIX-001.md",
        ):
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as temporary:
                target = copy_fixture("mature-mobile", Path(temporary))
                original_discover = PROJECT_OS.discover_adoption

                def discover_then_delete(
                    root: Path, include_inventory: bool = False
                ) -> dict[str, object]:
                    report = original_discover(root, include_inventory=include_inventory)
                    changed = target / relative
                    if changed.exists():
                        changed.unlink()
                    return report

                with mock.patch.object(
                    PROJECT_OS, "discover_adoption", side_effect=discover_then_delete
                ), mock.patch("builtins.print"):
                    with self.assertRaisesRegex(
                        PROJECT_OS.ProjectOSError,
                        "Adoption sources changed after discovery",
                    ):
                        PROJECT_OS.adopt_project(
                            target, dry_run=False, include_inventory=False
                        )
                self.assertFalse((target / ".agents" / "SYSTEM.json").exists())

    def test_adoption_rejects_managed_destination_appearing_after_discovery(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = copy_fixture("mature-mobile", Path(temporary))
            original_discover = PROJECT_OS.discover_adoption

            def discover_then_create(
                root: Path, include_inventory: bool = False
            ) -> dict[str, object]:
                report = original_discover(root, include_inventory=include_inventory)
                destination = target / ".agents" / "packs" / "README.md"
                destination.parent.mkdir(parents=True)
                destination.write_text("appeared\n", encoding="utf-8")
                return report

            with mock.patch.object(
                PROJECT_OS, "discover_adoption", side_effect=discover_then_create
            ), mock.patch("builtins.print"):
                with self.assertRaisesRegex(PROJECT_OS.ProjectOSError, "Refusing to overwrite"):
                    PROJECT_OS.adopt_project(target, dry_run=False, include_inventory=False)
            self.assertFalse((target / ".agents" / "SYSTEM.json").exists())


class ValidationAndSyncTest(unittest.TestCase):
    def init(self, target: Path, packs: str = "none", overlays: str = "none") -> None:
        result = run_cli(
            "init",
            "--target",
            str(target),
            "--packs",
            packs,
            "--overlays",
            overlays,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def mark_project_as_outdated(self, target: Path) -> None:
        knowledge_path = target / ".agents" / "knowledge" / "shared" / "failures.json"
        knowledge = json.loads(knowledge_path.read_text(encoding="utf-8"))
        knowledge["knowledge_version"] = "0.0.0"
        managed_knowledge: dict[str, str] = {}
        for entry in knowledge["entries"]:
            entry["source"]["project_os_version"] = "0.0.0"
            entry["source"]["content_hash"] = PROJECT_OS.entry_content_hash(entry)
            managed_knowledge[entry["id"]] = entry["source"]["content_hash"]
        knowledge_path.write_text(
            json.dumps(knowledge, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        system_path = target / ".agents" / "SYSTEM.json"
        system = json.loads(system_path.read_text(encoding="utf-8"))
        system["project_os_version"] = "0.0.0"
        system["managed_knowledge"] = dict(sorted(managed_knowledge.items()))
        system_path.write_text(
            json.dumps(system, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    def test_check_rejects_project_version_mismatch_with_upgrade_guidance(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            self.init(target)
            system_path = target / ".agents" / "SYSTEM.json"
            system = json.loads(system_path.read_text(encoding="utf-8"))
            system["project_os_version"] = "0.0.0"
            system_path.write_text(
                json.dumps(system, indent=2) + "\n", encoding="utf-8"
            )

            checked = run_cli("check", "--target", str(target))
            self.assertEqual(checked.returncode, 1, checked.stdout + checked.stderr)
            self.assertIn("SYSTEM project_os_version must match", checked.stdout)
            self.assertIn("upgrade workflow", checked.stdout)

    def test_check_rejects_shared_knowledge_version_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            self.init(target)
            knowledge_path = (
                target / ".agents" / "knowledge" / "shared" / "failures.json"
            )
            knowledge = json.loads(knowledge_path.read_text(encoding="utf-8"))
            knowledge["knowledge_version"] = "0.0.0"
            knowledge_path.write_text(
                json.dumps(knowledge, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            checked = run_cli("check", "--target", str(target))
            self.assertEqual(checked.returncode, 1, checked.stdout + checked.stderr)
            self.assertIn(
                "shared knowledge_version must match SYSTEM project_os_version",
                checked.stdout,
            )

    def test_upgrade_dry_run_is_byte_preserving(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            self.init(target, packs="mobile", overlays="react-native-expo")
            self.mark_project_as_outdated(target)
            before = file_hashes(target)

            upgraded = run_cli("upgrade", "--target", str(target), "--dry-run")
            self.assertEqual(upgraded.returncode, 0, upgraded.stdout + upgraded.stderr)
            self.assertIn("dry-run: no files written", upgraded.stdout)
            self.assertEqual(file_hashes(target), before)

    def test_upgrade_apply_updates_versions_and_passes_check(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            self.init(target, packs="mobile", overlays="react-native-expo")
            self.mark_project_as_outdated(target)

            upgraded = run_cli("upgrade", "--target", str(target))
            self.assertEqual(upgraded.returncode, 0, upgraded.stdout + upgraded.stderr)
            system = json.loads((target / ".agents" / "SYSTEM.json").read_text())
            knowledge = json.loads(
                (
                    target / ".agents" / "knowledge" / "shared" / "failures.json"
                ).read_text()
            )
            self.assertEqual(system["project_os_version"], PROJECT_OS.VERSION)
            self.assertEqual(knowledge["knowledge_version"], PROJECT_OS.VERSION)
            self.assertTrue(
                all(
                    entry["source"]["project_os_version"] == PROJECT_OS.VERSION
                    for entry in knowledge["entries"]
                )
            )
            checked = run_cli("check", "--target", str(target))
            self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)

    def test_upgrade_conflict_aborts_without_writing_any_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            self.init(target, packs="mobile", overlays="react-native-expo")
            self.mark_project_as_outdated(target)
            knowledge_path = (
                target / ".agents" / "knowledge" / "shared" / "failures.json"
            )
            knowledge = json.loads(knowledge_path.read_text(encoding="utf-8"))
            knowledge["entries"][0]["title"] = "Local edit"
            knowledge["entries"][0]["source"][
                "content_hash"
            ] = PROJECT_OS.entry_content_hash(knowledge["entries"][0])
            knowledge_path.write_text(
                json.dumps(knowledge, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            before = file_hashes(target)

            upgraded = run_cli("upgrade", "--target", str(target))
            self.assertEqual(upgraded.returncode, 2, upgraded.stdout + upgraded.stderr)
            self.assertIn("Upgrade conflicts", upgraded.stderr)
            self.assertEqual(file_hashes(target), before)

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
            PROJECT_OS.init_project(target, "none", "none", False)
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

    def test_malformed_history_and_active_program_membership_values_do_not_crash(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            self.init(target)
            definition = write_program_definition(target)
            self.assertEqual(
                run_cli(
                    "program",
                    "start",
                    "--target",
                    str(target),
                    "--definition",
                    str(definition),
                ).returncode,
                0,
            )
            system_path = target / ".agents" / "SYSTEM.json"
            system = json.loads(system_path.read_text())
            system["active_program"]["origin"] = []
            system_path.write_text(json.dumps(system, indent=2) + "\n", encoding="utf-8")
            active_check = run_cli("check", "--target", str(target))
            self.assertEqual(active_check.returncode, 1)
            self.assertNotIn("Traceback", active_check.stderr)

        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            self.init(target)
            history = target / ".agents" / "history"
            history.mkdir()
            archive = history / "snapshot.md"
            archive.write_text("snapshot\n", encoding="utf-8")
            index_path = history / "index.json"
            index_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "entries": [
                            {
                                "id": "snapshot-001",
                                "kind": [],
                                "path": ".agents/history/snapshot.md",
                                "sha256": "sha256:"
                                + hashlib.sha256(archive.read_bytes()).hexdigest(),
                                "disposition": [],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            system_path = target / ".agents" / "SYSTEM.json"
            system = json.loads(system_path.read_text())
            system["paths"]["history"] = ".agents/history"
            system["paths"]["history_index"] = ".agents/history/index.json"
            system_path.write_text(json.dumps(system, indent=2) + "\n", encoding="utf-8")
            history_check = run_cli("check", "--target", str(target))
            self.assertEqual(history_check.returncode, 1)
            self.assertNotIn("Traceback", history_check.stderr)

    def test_invalid_utf8_system_reports_clean_error(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            self.init(target)
            (target / ".agents" / "SYSTEM.json").write_bytes(b"\xff\xfe")
            checked = run_cli("check", "--target", str(target))
            self.assertEqual(checked.returncode, 1)
            self.assertIn("not valid UTF-8", checked.stdout)
            self.assertNotIn("Traceback", checked.stderr)

    def test_system_directory_reports_clean_read_error(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            self.init(target)
            system_path = target / ".agents" / "SYSTEM.json"
            system_path.unlink()
            system_path.mkdir()
            checked = run_cli("check", "--target", str(target))
            self.assertEqual(checked.returncode, 1)
            self.assertIn("Could not read JSON file", checked.stdout)
            self.assertNotIn("Traceback", checked.stderr)

    def test_owner_collisions_and_aliases_block_check_and_sync_without_writes(self) -> None:
        for shared_path in (
            ".agents/CONTEXT.md",
            ".agents/./CONTEXT.md",
            ".agents/context.md",
        ):
            with self.subTest(shared_path=shared_path), tempfile.TemporaryDirectory() as temporary:
                target = Path(temporary)
                self.init(target)
                context = target / ".agents" / "CONTEXT.md"
                original_context = context.read_bytes()
                system_path = target / ".agents" / "SYSTEM.json"
                system = json.loads(system_path.read_text())
                system["paths"]["shared_knowledge"] = shared_path
                system_path.write_text(json.dumps(system, indent=2) + "\n", encoding="utf-8")
                before = file_hashes(target)

                checked = run_cli("check", "--target", str(target))
                self.assertEqual(checked.returncode, 1, checked.stdout + checked.stderr)
                self.assertIn("owner collision", checked.stdout)
                synced = run_cli("sync-knowledge", "--target", str(target))
                self.assertEqual(synced.returncode, 2, synced.stdout + synced.stderr)
                self.assertEqual(file_hashes(target), before)
                self.assertEqual(context.read_bytes(), original_context)

    def test_history_index_must_be_inside_history_owner(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            self.init(target)
            history = target / ".agents" / "history"
            history.mkdir()
            outside_index = target / ".agents" / "history-index.json"
            outside_index.write_text(
                json.dumps({"schema_version": 1, "entries": []}) + "\n",
                encoding="utf-8",
            )
            system_path = target / ".agents" / "SYSTEM.json"
            system = json.loads(system_path.read_text())
            system["paths"]["history"] = ".agents/history"
            system["paths"]["history_index"] = ".agents/history-index.json"
            system_path.write_text(json.dumps(system, indent=2) + "\n", encoding="utf-8")
            checked = run_cli("check", "--target", str(target))
            self.assertEqual(checked.returncode, 1)
            self.assertIn("history_index must be inside", checked.stdout)

    def test_hardlinked_file_owners_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            self.init(target)
            context = target / ".agents" / "CONTEXT.md"
            shared = target / ".agents" / "knowledge" / "shared" / "failures.json"
            shared.unlink()
            os.link(context, shared)
            checked = run_cli("check", "--target", str(target))
            self.assertEqual(checked.returncode, 1)
            self.assertIn("same existing file", checked.stdout)

    def test_sync_rejects_outdated_release_and_does_not_advance_version(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            self.init(target)
            self.mark_project_as_outdated(target)
            before = file_hashes(target)
            synced = run_cli("sync-knowledge", "--target", str(target))
            self.assertEqual(synced.returncode, 2, synced.stdout + synced.stderr)
            self.assertIn("run upgrade before sync", synced.stderr)
            self.assertEqual(file_hashes(target), before)

    def test_sync_dry_run_previews_every_file_it_would_update(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            self.init(target)
            self.mark_project_as_outdated(target)
            system_path = target / ".agents" / "SYSTEM.json"
            system = json.loads(system_path.read_text())
            system["project_os_version"] = PROJECT_OS.VERSION
            system_path.write_text(json.dumps(system, indent=2) + "\n", encoding="utf-8")

            preview = run_cli(
                "sync-knowledge", "--target", str(target), "--dry-run"
            )
            self.assertEqual(preview.returncode, 0, preview.stdout + preview.stderr)
            mutations = [
                line
                for line in preview.stdout.splitlines()
                if line.startswith(("create: ", "update: ", "delete: "))
            ]
            self.assertEqual(
                mutations,
                [
                    "update: .agents/knowledge/shared/failures.json",
                    "update: .agents/SYSTEM.json",
                ],
            )

    def test_common_private_material_patterns_and_sensitive_keys_are_rejected(self) -> None:
        variants = (
            "gho_abcdefghijklmnopqrstuvwxyz",
            "ghu_abcdefghijklmnopqrstuvwxyz",
            "ghs_abcdefghijklmnopqrstuvwxyz",
            "ghr_abcdefghijklmnopqrstuvwxyz",
            "AIzaabcdefghijklmnopqrstuvwxyz123456",
            "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.payload.signature",
            "C:\\Users\\alice\\private.txt",
            "https://service.internal/path",
            "https://example.com/file?X-Goog-Signature=secret",
        )
        for value in variants:
            with self.subTest(value=value), tempfile.TemporaryDirectory() as temporary:
                target = Path(temporary)
                self.init(target)
                path = target / ".agents" / "knowledge" / "shared" / "failures.json"
                knowledge = json.loads(path.read_text())
                knowledge["entries"][0]["mechanism"] = value
                knowledge["entries"][0]["source"][
                    "content_hash"
                ] = PROJECT_OS.entry_content_hash(knowledge["entries"][0])
                path.write_text(
                    json.dumps(knowledge, indent=2) + "\n", encoding="utf-8"
                )
                self.assertEqual(run_cli("check", "--target", str(target)).returncode, 1)

        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            self.init(target)
            path = target / ".agents" / "knowledge" / "shared" / "failures.json"
            knowledge = json.loads(path.read_text())
            knowledge["entries"][0]["client_secret"] = "redacted"
            knowledge["entries"][0]["source"][
                "content_hash"
            ] = PROJECT_OS.entry_content_hash(knowledge["entries"][0])
            path.write_text(json.dumps(knowledge, indent=2) + "\n", encoding="utf-8")
            checked = run_cli("check", "--target", str(target))
            self.assertEqual(checked.returncode, 1)
            self.assertIn("sensitive field name", checked.stdout)

    def test_unreviewed_managed_shared_entry_blocks_sync_and_upgrade(self) -> None:
        for command, expected_code in (("sync-knowledge", 1), ("upgrade", 2)):
            with self.subTest(command=command), tempfile.TemporaryDirectory() as temporary:
                target = Path(temporary)
                self.init(target)
                path = target / ".agents" / "knowledge" / "shared" / "failures.json"
                knowledge = json.loads(path.read_text())
                entry = {
                    "id": "LOCAL-UNREVIEWED-001",
                    "title": "Unreviewed portable entry",
                    "status": "active",
                    "applies_to": ["core"],
                    "trigger": "A local entry was inserted.",
                    "mechanism": "The entry bypassed release review.",
                    "prevention": "Require a recorded managed baseline.",
                    "verification": ["The operation aborts."],
                    "boundaries": ["Shared knowledge only."],
                    "source": {
                        "kind": "incident-derived",
                        "pack": "core",
                        "project_os_version": PROJECT_OS.VERSION,
                        "references": [],
                    },
                }
                entry["source"]["content_hash"] = PROJECT_OS.entry_content_hash(entry)
                knowledge["entries"].append(entry)
                path.write_text(
                    json.dumps(knowledge, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8",
                )
                before = file_hashes(target)
                result = run_cli(command, "--target", str(target))
                self.assertEqual(result.returncode, expected_code, result.stdout + result.stderr)
                self.assertEqual(file_hashes(target), before)

    def test_sync_requires_exact_system_selection_and_schema_v3(self) -> None:
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

    def test_external_config_tokens_and_canonical_order_are_checked(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "project"
            target.mkdir()
            self.init(target, packs="service,mobile")
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


class ProgramLifecycleTest(unittest.TestCase):
    def init(self, target: Path) -> None:
        result = run_cli(
            "init",
            "--target",
            str(target),
            "--packs",
            "none",
            "--overlays",
            "none",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_program_start_dry_run_is_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            self.init(target)
            definition = write_program_definition(target)
            before = file_hashes(target)

            result = run_cli(
                "program",
                "start",
                "--target",
                str(target),
                "--definition",
                str(definition),
                "--dry-run",
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("dry-run: no files written", result.stdout)
            self.assertEqual(file_hashes(target), before)
            self.assertFalse((target / ".agents" / "PROGRAM.md").exists())

    def test_program_start_rejects_an_incomplete_definition_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            self.init(target)
            definition = write_program_definition(target)
            value = json.loads(definition.read_text())
            value.pop("exit_conditions")
            definition.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
            before = file_hashes(target)

            result = run_cli(
                "program",
                "start",
                "--target",
                str(target),
                "--definition",
                str(definition),
            )

            self.assertEqual(result.returncode, 2)
            self.assertIn("exit_conditions", result.stderr)
            self.assertEqual(file_hashes(target), before)
            self.assertFalse((target / ".agents" / "PROGRAM.md").exists())

    def test_program_start_rejects_multiline_identity_in_dry_run_and_apply(self) -> None:
        for field in ("initiative", "phase-name"):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as temporary:
                target = Path(temporary)
                self.init(target)
                definition = write_program_definition(target)
                value = json.loads(definition.read_text())
                if field == "initiative":
                    value["initiative"] = "Valid title\nStatus: completed."
                else:
                    value["phases"][0]["name"] = "Inventory\nStatus: completed."
                definition.write_text(
                    json.dumps(value, indent=2) + "\n", encoding="utf-8"
                )
                before = file_hashes(target)
                for extra in (("--dry-run",), ()):
                    result = run_cli(
                        "program",
                        "start",
                        "--target",
                        str(target),
                        "--definition",
                        str(definition),
                        *extra,
                    )
                    self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                    self.assertIn("single line", result.stderr)
                    self.assertEqual(file_hashes(target), before)

    def test_program_start_status_and_close_preserve_plan_state(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            self.init(target)
            definition = write_program_definition(target)
            plans_path = target / ".agents" / "plans" / "index.json"
            plans_before = plans_path.read_bytes()

            started = run_cli(
                "program",
                "start",
                "--target",
                str(target),
                "--definition",
                str(definition),
            )
            self.assertEqual(started.returncode, 0, started.stdout + started.stderr)
            self.assertEqual(plans_path.read_bytes(), plans_before)
            self.assertFalse((target / ".agents" / "history").exists())
            system = json.loads((target / ".agents" / "SYSTEM.json").read_text())
            self.assertEqual(system["mode"], "program")
            self.assertEqual(system["active_program"]["origin"], "created")
            program_path = target / ".agents" / "PROGRAM.md"
            program_path.write_bytes(program_path.read_bytes().replace(b"\n", b"\r\n"))
            original_program = program_path.read_bytes()
            program_text = original_program.decode("utf-8")
            for heading in (
                "## Outcome",
                "## Authority",
                "## Phases",
                "## Exit conditions",
                "## Evidence requirements",
                "## Cost boundary",
                "## Exclusions",
            ):
                self.assertIn(heading, program_text)

            status = run_cli("program", "status", "--target", str(target))
            self.assertEqual(status.returncode, 0, status.stdout + status.stderr)
            self.assertIn('"mode": "program"', status.stdout)

            before_close = file_hashes(target)
            preview = run_cli(
                "program",
                "close",
                "--target",
                str(target),
                "--disposition",
                "completed",
                "--dry-run",
            )
            self.assertEqual(preview.returncode, 0, preview.stdout + preview.stderr)
            self.assertEqual(file_hashes(target), before_close)

            closed = run_cli(
                "program",
                "close",
                "--target",
                str(target),
                "--disposition",
                "completed",
            )
            self.assertEqual(closed.returncode, 0, closed.stdout + closed.stderr)
            self.assertFalse(program_path.exists())
            system = json.loads((target / ".agents" / "SYSTEM.json").read_text())
            self.assertEqual(system["mode"], "standard")
            self.assertIsNone(system["active_program"])
            index = json.loads(
                (target / ".agents" / "history" / "index.json").read_text()
            )
            self.assertEqual(len(index["entries"]), 1)
            entry = index["entries"][0]
            archive = target / entry["path"]
            self.assertEqual(archive.read_bytes(), original_program)
            self.assertEqual(
                entry["sha256"], "sha256:" + hashlib.sha256(original_program).hexdigest()
            )
            self.assertEqual(run_cli("check", "--target", str(target)).returncode, 0)

    def test_program_close_requires_no_active_plan_and_stopped_reason(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            self.init(target)
            definition = write_program_definition(target)
            self.assertEqual(
                run_cli(
                    "program",
                    "start",
                    "--target",
                    str(target),
                    "--definition",
                    str(definition),
                ).returncode,
                0,
            )
            missing_reason = run_cli(
                "program",
                "close",
                "--target",
                str(target),
                "--disposition",
                "stopped",
            )
            self.assertEqual(missing_reason.returncode, 2)
            self.assertIn("requires --reason", missing_reason.stderr)

            plan = target / ".agents" / "plans" / "001.md"
            plan.write_text("# Active plan\n", encoding="utf-8")
            index_path = target / ".agents" / "plans" / "index.json"
            index = json.loads(index_path.read_text())
            index["execution_state"] = "running"
            index["plans"] = [
                {
                    "id": "001",
                    "status": "active",
                    "path": ".agents/plans/001.md",
                    "outcome": "Finish active work.",
                }
            ]
            index_path.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
            blocked = run_cli(
                "program",
                "close",
                "--target",
                str(target),
                "--disposition",
                "stopped",
                "--reason",
                "Owner stopped the initiative.",
            )
            self.assertEqual(blocked.returncode, 2)
            self.assertIn("Close the active plan", blocked.stderr)

    def test_created_program_contract_tampering_blocks_check_and_close(self) -> None:
        for mutation, expected_error in (
            ("metadata", "metadata does not match SYSTEM"),
            ("empty-section", "section must be non-empty"),
            ("missing-phase", "at least two phases"),
        ):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temporary:
                target = Path(temporary)
                self.init(target)
                definition = write_program_definition(target)
                self.assertEqual(
                    run_cli(
                        "program",
                        "start",
                        "--target",
                        str(target),
                        "--definition",
                        str(definition),
                    ).returncode,
                    0,
                )
                program = target / ".agents" / "PROGRAM.md"
                text = program.read_text(encoding="utf-8")
                if mutation == "metadata":
                    text = re.sub(
                        r"Program ID: program-\d{8}-\d{3,}\.",
                        "Program ID: program-20000101-999.",
                        text,
                    )
                elif mutation == "empty-section":
                    text = text.replace(
                        "## Outcome\n\nMove all supported consumers without behavior drift.",
                        "## Outcome\n",
                    )
                else:
                    text = re.sub(
                        r"\n### 2\. Migration.*?(?=\n## Exit conditions)",
                        "",
                        text,
                        flags=re.DOTALL,
                    )
                program.write_text(text, encoding="utf-8")

                checked = run_cli("check", "--target", str(target))
                self.assertEqual(checked.returncode, 1, checked.stdout + checked.stderr)
                self.assertIn(expected_error, checked.stdout)
                closed = run_cli(
                    "program",
                    "close",
                    "--target",
                    str(target),
                    "--disposition",
                    "completed",
                )
                self.assertEqual(closed.returncode, 2, closed.stdout + closed.stderr)
                self.assertTrue(program.is_file())

    def test_program_path_collision_cannot_delete_another_owner(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            self.init(target)
            definition = write_program_definition(target)
            self.assertEqual(
                run_cli(
                    "program",
                    "start",
                    "--target",
                    str(target),
                    "--definition",
                    str(definition),
                ).returncode,
                0,
            )
            context = target / ".agents" / "CONTEXT.md"
            context_before = context.read_bytes()
            system_path = target / ".agents" / "SYSTEM.json"
            system = json.loads(system_path.read_text())
            system["paths"]["program"] = ".agents/CONTEXT.md"
            system_path.write_text(json.dumps(system, indent=2) + "\n", encoding="utf-8")

            checked = run_cli("check", "--target", str(target))
            self.assertEqual(checked.returncode, 1)
            self.assertIn("paths.program", checked.stdout)
            closed = run_cli(
                "program",
                "close",
                "--target",
                str(target),
                "--disposition",
                "completed",
            )
            self.assertEqual(closed.returncode, 2)
            self.assertEqual(context.read_bytes(), context_before)
            self.assertTrue((target / ".agents" / "PROGRAM.md").is_file())

    def test_checker_detects_archive_tampering(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            self.init(target)
            definition = write_program_definition(target)
            self.assertEqual(
                run_cli(
                    "program",
                    "start",
                    "--target",
                    str(target),
                    "--definition",
                    str(definition),
                ).returncode,
                0,
            )
            self.assertEqual(
                run_cli(
                    "program",
                    "close",
                    "--target",
                    str(target),
                    "--disposition",
                    "completed",
                ).returncode,
                0,
            )
            index = json.loads(
                (target / ".agents" / "history" / "index.json").read_text()
            )
            archive = target / index["entries"][0]["path"]
            archive.write_text(archive.read_text() + "\nChanged.\n", encoding="utf-8")
            checked = run_cli("check", "--target", str(target))
            self.assertEqual(checked.returncode, 1)
            self.assertIn("history snapshot hash mismatch", checked.stdout)

    def test_checker_requires_a_reason_for_stopped_program_history(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            self.init(target)
            definition = write_program_definition(target)
            self.assertEqual(
                run_cli(
                    "program",
                    "start",
                    "--target",
                    str(target),
                    "--definition",
                    str(definition),
                ).returncode,
                0,
            )
            self.assertEqual(
                run_cli(
                    "program",
                    "close",
                    "--target",
                    str(target),
                    "--disposition",
                    "stopped",
                    "--reason",
                    "The owner ended the initiative.",
                ).returncode,
                0,
            )
            index_path = target / ".agents" / "history" / "index.json"
            index = json.loads(index_path.read_text())
            index["entries"][0].pop("reason")
            index_path.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
            checked = run_cli("check", "--target", str(target))
            self.assertEqual(checked.returncode, 1)
            self.assertIn("requires a non-empty reason", checked.stdout)


class UpgradeTest(unittest.TestCase):
    def init(self, target: Path) -> None:
        result = run_cli(
            "init",
            "--target",
            str(target),
            "--packs",
            "mobile",
            "--overlays",
            "none",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def make_schema2(self, target: Path, mode: str = "lite") -> None:
        knowledge_path = target / ".agents" / "knowledge" / "shared" / "failures.json"
        knowledge = json.loads(knowledge_path.read_text())
        knowledge["knowledge_version"] = "1.0.1"
        managed: dict[str, str] = {}
        for entry in knowledge["entries"]:
            entry["source"]["project_os_version"] = "1.0.1"
            entry["source"]["content_hash"] = PROJECT_OS.entry_content_hash(entry)
            managed[entry["id"]] = entry["source"]["content_hash"]
        knowledge_path.write_text(
            json.dumps(knowledge, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        system_path = target / ".agents" / "SYSTEM.json"
        system = json.loads(system_path.read_text())
        system["schema_version"] = 2
        system["project_os_version"] = "1.0.1"
        system["mode"] = mode
        system.pop("active_program", None)
        system["managed_knowledge"] = dict(sorted(managed.items()))
        system["paths"].pop("history_index", None)
        system_path.write_text(json.dumps(system, indent=2) + "\n", encoding="utf-8")

    def test_schema2_standard_upgrade_dry_run_then_apply(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            self.init(target)
            self.make_schema2(target)
            before = file_hashes(target)
            preview = run_cli("upgrade", "--target", str(target), "--dry-run")
            self.assertEqual(preview.returncode, 0, preview.stdout + preview.stderr)
            self.assertEqual(file_hashes(target), before)
            applied = run_cli("upgrade", "--target", str(target))
            self.assertEqual(applied.returncode, 0, applied.stdout + applied.stderr)
            system = json.loads((target / ".agents" / "SYSTEM.json").read_text())
            self.assertEqual(system["schema_version"], 3)
            self.assertEqual(system["mode"], "standard")
            self.assertEqual(system["project_os_version"], "2.0.0")
            self.assertEqual(run_cli("check", "--target", str(target)).returncode, 0)

    def test_current_upgrade_is_byte_preserving_even_with_an_old_generated_date(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            self.init(target)
            system_path = target / ".agents" / "SYSTEM.json"
            system = json.loads(system_path.read_text())
            system["generated_on"] = "2000-01-01"
            system_path.write_text(json.dumps(system, indent=2) + "\n", encoding="utf-8")
            before = file_hashes(target)

            preview = run_cli("upgrade", "--target", str(target), "--dry-run")
            self.assertEqual(preview.returncode, 0, preview.stdout + preview.stderr)
            self.assertEqual(file_hashes(target), before)
            applied = run_cli("upgrade", "--target", str(target))
            self.assertEqual(applied.returncode, 0, applied.stdout + applied.stderr)
            self.assertEqual(file_hashes(target), before)

    def test_closed_schema2_program_requires_classification_and_archives_exact_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            self.init(target)
            definition = write_program_definition(target)
            self.assertEqual(
                run_cli(
                    "program",
                    "start",
                    "--target",
                    str(target),
                    "--definition",
                    str(definition),
                ).returncode,
                0,
            )
            program = target / ".agents" / "PROGRAM.md"
            original = program.read_bytes()
            (target / ".agents" / "history").mkdir()
            self.make_schema2(target, mode="full")
            before = file_hashes(target)
            ambiguous = run_cli("upgrade", "--target", str(target))
            self.assertEqual(ambiguous.returncode, 2)
            self.assertIn("requires --legacy-program-state", ambiguous.stderr)
            self.assertEqual(file_hashes(target), before)

            missing_date = run_cli(
                "upgrade",
                "--target",
                str(target),
                "--legacy-program-state",
                "closed",
                "--disposition",
                "stopped",
                "--reason",
                "The legacy audit was already closed.",
            )
            self.assertEqual(missing_date.returncode, 2)
            self.assertIn("requires a YYYY-MM-DD date", missing_date.stderr)
            self.assertEqual(file_hashes(target), before)

            preview = run_cli(
                "upgrade",
                "--target",
                str(target),
                "--legacy-program-state",
                "closed",
                "--disposition",
                "stopped",
                "--closed-on",
                "2026-09-07",
                "--reason",
                "The legacy audit was already closed.",
                "--dry-run",
            )
            self.assertEqual(preview.returncode, 0, preview.stdout + preview.stderr)
            self.assertEqual(file_hashes(target), before)
            applied = run_cli(
                "upgrade",
                "--target",
                str(target),
                "--legacy-program-state",
                "closed",
                "--disposition",
                "stopped",
                "--closed-on",
                "2026-09-07",
                "--reason",
                "The legacy audit was already closed.",
            )
            self.assertEqual(applied.returncode, 0, applied.stdout + applied.stderr)
            self.assertFalse(program.exists())
            system = json.loads((target / ".agents" / "SYSTEM.json").read_text())
            self.assertEqual(system["mode"], "standard")
            history = json.loads(
                (target / ".agents" / "history" / "index.json").read_text()
            )
            entry = history["entries"][0]
            self.assertEqual(entry["disposition"], "stopped")
            self.assertEqual(entry["closed_on"], "2026-09-07")
            self.assertEqual((target / entry["path"]).read_bytes(), original)

    def test_active_schema2_program_is_preserved_with_explicit_classification(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            self.init(target)
            definition = write_program_definition(target)
            self.assertEqual(
                run_cli(
                    "program",
                    "start",
                    "--target",
                    str(target),
                    "--definition",
                    str(definition),
                ).returncode,
                0,
            )
            program = target / ".agents" / "PROGRAM.md"
            original = program.read_bytes()
            (target / ".agents" / "history").mkdir()
            self.make_schema2(target, mode="full")
            applied = run_cli(
                "upgrade",
                "--target",
                str(target),
                "--legacy-program-state",
                "active",
            )
            self.assertEqual(applied.returncode, 0, applied.stdout + applied.stderr)
            self.assertEqual(program.read_bytes(), original)
            system = json.loads((target / ".agents" / "SYSTEM.json").read_text())
            self.assertEqual(system["mode"], "program")
            self.assertEqual(system["active_program"]["origin"], "legacy-migration")
            self.assertIsNone(system["active_program"]["started_on"])
            self.assertRegex(system["active_program"]["migrated_on"], r"^\d{4}-\d{2}-\d{2}$")
            self.assertEqual(run_cli("check", "--target", str(target)).returncode, 0)

    def test_active_schema2_migration_does_not_invent_start_date_from_generated_on(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            self.init(target)
            definition = write_program_definition(target)
            self.assertEqual(
                run_cli(
                    "program",
                    "start",
                    "--target",
                    str(target),
                    "--definition",
                    str(definition),
                ).returncode,
                0,
            )
            (target / ".agents" / "history").mkdir()
            self.make_schema2(target, mode="full")
            system_path = target / ".agents" / "SYSTEM.json"
            system = json.loads(system_path.read_text())
            system["generated_on"] = {"not": "a Program start date"}
            system_path.write_text(json.dumps(system, indent=2) + "\n", encoding="utf-8")

            applied = run_cli(
                "upgrade",
                "--target",
                str(target),
                "--legacy-program-state",
                "active",
            )
            self.assertEqual(applied.returncode, 0, applied.stdout + applied.stderr)
            upgraded = json.loads(system_path.read_text())
            self.assertIsNone(upgraded["active_program"]["started_on"])
            self.assertEqual(run_cli("check", "--target", str(target)).returncode, 0)

    def test_upgrade_rolls_back_when_final_checker_rejects_project_owned_state(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            self.init(target)
            self.make_schema2(target)
            agents = target / "AGENTS.md"
            agents.write_text("# Broken routing\n", encoding="utf-8")
            before = file_hashes(target)

            result = run_cli("upgrade", "--target", str(target))
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("produced invalid Project OS state", result.stderr)
            self.assertEqual(file_hashes(target), before)

    def test_upgrade_malformed_schema_and_mode_values_do_not_crash(self) -> None:
        for field, value in (("schema_version", {}), ("mode", {})):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as temporary:
                target = Path(temporary)
                self.init(target)
                system_path = target / ".agents" / "SYSTEM.json"
                system = json.loads(system_path.read_text())
                system[field] = value
                system_path.write_text(
                    json.dumps(system, indent=2) + "\n", encoding="utf-8"
                )
                result = run_cli("upgrade", "--target", str(target))
                self.assertEqual(result.returncode, 2)
                self.assertNotIn("Traceback", result.stderr)

    def test_upgrade_conflict_aborts_all_schema_and_program_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            self.init(target)
            self.make_schema2(target)
            knowledge_path = target / ".agents" / "knowledge" / "shared" / "failures.json"
            knowledge = json.loads(knowledge_path.read_text())
            knowledge["entries"][0]["title"] = "Locally changed"
            knowledge["entries"][0]["source"]["content_hash"] = PROJECT_OS.entry_content_hash(
                knowledge["entries"][0]
            )
            knowledge_path.write_text(
                json.dumps(knowledge, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            before = file_hashes(target)
            result = run_cli("upgrade", "--target", str(target))
            self.assertEqual(result.returncode, 2)
            self.assertIn("Upgrade conflicts", result.stderr)
            self.assertEqual(file_hashes(target), before)

    def test_closed_program_upgrade_conflict_does_not_archive_or_delete(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            self.init(target)
            definition = write_program_definition(target)
            self.assertEqual(
                run_cli(
                    "program",
                    "start",
                    "--target",
                    str(target),
                    "--definition",
                    str(definition),
                ).returncode,
                0,
            )
            (target / ".agents" / "history").mkdir()
            self.make_schema2(target, mode="full")
            knowledge_path = target / ".agents" / "knowledge" / "shared" / "failures.json"
            knowledge = json.loads(knowledge_path.read_text())
            knowledge["entries"][0]["title"] = "Local conflict"
            knowledge["entries"][0]["source"]["content_hash"] = PROJECT_OS.entry_content_hash(
                knowledge["entries"][0]
            )
            knowledge_path.write_text(
                json.dumps(knowledge, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            before = file_hashes(target)

            result = run_cli(
                "upgrade",
                "--target",
                str(target),
                "--legacy-program-state",
                "closed",
                "--disposition",
                "stopped",
                "--closed-on",
                "2026-09-07",
                "--reason",
                "The legacy audit was already closed.",
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("Upgrade conflicts", result.stderr)
            self.assertEqual(file_hashes(target), before)
            self.assertTrue((target / ".agents" / "PROGRAM.md").is_file())
            self.assertFalse((target / ".agents" / "history" / "index.json").exists())

if __name__ == "__main__":
    unittest.main()
