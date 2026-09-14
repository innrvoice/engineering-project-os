"""Observable regressions from the independent whole-project audit."""

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import test_project_os as test_helpers
from test_project_os import PROJECT_OS, file_hashes, run_cli, write_program_definition


class AuditRegressionTests(unittest.TestCase):
    def test_create_flush_failure_preserves_concurrent_in_place_edit(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            destination = root / "record.txt"

            def change_and_fail(descriptor):
                destination.write_text("concurrent edit")
                raise OSError("injected fsync failure")

            with mock.patch.object(PROJECT_OS.os, "fsync", side_effect=change_and_fail):
                with self.assertRaisesRegex(PROJECT_OS.ProjectOSError, "rollback incomplete"):
                    PROJECT_OS.execute_sync_transaction(root, [(destination, "created")], [])
            self.assertEqual(destination.read_text(), "concurrent edit")

    def test_rollback_preserves_changed_deletion_backup_for_review(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            destination = root / "record.txt"
            destination.write_text("original")

            def change_and_fail():
                next(root.glob(".record.txt.project-os-delete.*")).write_text("concurrent edit")
                raise PROJECT_OS.ProjectOSError("injected validation failure")

            with self.assertRaisesRegex(PROJECT_OS.ProjectOSError, "rollback incomplete"):
                PROJECT_OS.execute_sync_transaction(
                    root, [], [], [(destination, hashlib.sha256(b"original").hexdigest())],
                    after_write=change_and_fail,
                )
            self.assertFalse(destination.exists())
            self.assertEqual(next(root.glob(".record.txt.project-os-delete.*")).read_text(), "concurrent edit")

    def test_create_parent_swap_at_syscall_never_redirects_write_or_rollback(self):
        for initializer in (False, True):
            with self.subTest(initializer=initializer), tempfile.TemporaryDirectory() as temporary:
                base = Path(temporary).resolve()
                root, outside = base / "repo", base / "outside"
                parent = root / "managed"
                parent.mkdir(parents=True)
                outside.mkdir()
                destination = parent / "record.txt"
                original_open = PROJECT_OS.os.open
                swapped = False

                def swap(name, flags, *args, **kwargs):
                    nonlocal swapped
                    if name == destination.name and flags & PROJECT_OS.os.O_CREAT and not swapped:
                        swapped = True
                        parent.rename(root / "saved")
                        parent.symlink_to(outside, target_is_directory=True)
                    return original_open(name, flags, *args, **kwargs)

                # Capability checks inspect function identity, so retain support for the wrapper.
                with mock.patch.object(PROJECT_OS.os, "open", side_effect=swap) as patched:
                    with mock.patch.object(PROJECT_OS.os, "supports_dir_fd", PROJECT_OS.os.supports_dir_fd | {patched}):
                        with self.assertRaises(PROJECT_OS.ProjectOSError):
                            if initializer:
                                PROJECT_OS.execute_operations(root, [("create", destination, "created")], False)
                            else:
                                PROJECT_OS.execute_sync_transaction(root, [(destination, "created")], [])
                self.assertTrue(swapped)
                self.assertFalse((outside / destination.name).exists())
                self.assertFalse((root / "saved" / destination.name).exists())

    def test_delete_parent_swap_restores_original_in_anchored_directory(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            root, outside = base / "repo", base / "outside"
            parent = root / "managed"
            parent.mkdir(parents=True)
            outside.mkdir()
            destination = parent / "record.txt"
            destination.write_text("original")
            (outside / destination.name).write_text("outside")
            original_replace = PROJECT_OS.os.replace

            def swap(source, target, **kwargs):
                parent.rename(root / "saved")
                parent.symlink_to(outside, target_is_directory=True)
                return original_replace(source, target, **kwargs)

            with mock.patch.object(PROJECT_OS.os, "replace", side_effect=swap):
                with self.assertRaises(PROJECT_OS.ProjectOSError):
                    PROJECT_OS.execute_sync_transaction(
                        root, [], [], [(destination, hashlib.sha256(b"original").hexdigest())]
                    )
            self.assertEqual((outside / destination.name).read_text(), "outside")
            self.assertEqual((root / "saved" / destination.name).read_text(), "original")
            self.assertEqual(list((root / "saved").iterdir()), [root / "saved" / destination.name])

    def test_replacement_parent_swap_never_writes_to_symlink_target(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            root, outside = base / "repo", base / "outside"
            parent = root / "managed"
            parent.mkdir(parents=True)
            outside.mkdir()
            destination = parent / "record.txt"
            destination.write_text("original")
            (outside / destination.name).write_text("original")
            original_write = PROJECT_OS.atomic_write_text

            def swap(*args, **kwargs):
                parent.rename(root / "saved")
                parent.symlink_to(outside, target_is_directory=True)
                return original_write(*args, **kwargs)

            with mock.patch.object(PROJECT_OS, "atomic_write_text", side_effect=swap):
                with self.assertRaises(PROJECT_OS.ProjectOSError):
                    PROJECT_OS.execute_sync_transaction(
                        root, [], [(destination, "changed", hashlib.sha256(b"original").hexdigest())]
                    )
            self.assertEqual((outside / destination.name).read_text(), "original")
            self.assertEqual((root / "saved" / destination.name).read_text(), "original")

    def test_upgrade_preserves_system_change_during_planning(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            self.assertEqual(run_cli("init", "--target", str(root)).returncode, 0)
            system_path = root / ".agents/SYSTEM.json"
            original_plan = PROJECT_OS.plan_managed_release_update

            def change_system(*args):
                value = json.loads(system_path.read_text())
                value["toolchain_signals"] = ["python"]
                system_path.write_text(json.dumps(value, indent=2) + "\n")
                return original_plan(*args)

            with mock.patch.object(PROJECT_OS, "plan_managed_release_update", side_effect=change_system):
                with self.assertRaisesRegex(PROJECT_OS.ProjectOSError, "changed"):
                    PROJECT_OS.upgrade_project(root, None, None, None, None, False)
            self.assertEqual(json.loads(system_path.read_text())["toolchain_signals"], ["python"])

    def test_upgrade_refuses_newer_release_without_writes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            self.assertEqual(run_cli("init", "--target", str(root)).returncode, 0)
            system_path = root / ".agents/SYSTEM.json"
            value = json.loads(system_path.read_text())
            value["project_os_version"] = "2.0.2"
            system_path.write_text(json.dumps(value, indent=2) + "\n")
            before = file_hashes(root)
            for dry_run in (False, True):
                with self.subTest(dry_run=dry_run):
                    with self.assertRaisesRegex(PROJECT_OS.ProjectOSError, "newer|downgrade"):
                        PROJECT_OS.upgrade_project(root, None, None, None, None, dry_run)
                    self.assertEqual(file_hashes(root), before)

    def test_system_snapshot_is_guarded_in_sync_start_and_close(self):
        for operation, boundary in (("sync", "default_system"), ("start", "render_program_definition"), ("close", "load_history_for_mutation")):
            with self.subTest(operation=operation), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary).resolve()
                self.assertEqual(run_cli("init", "--target", str(root)).returncode, 0)
                definition = write_program_definition(root)
                if operation == "close":
                    self.assertEqual(run_cli("program", "start", "--target", str(root), "--definition", str(definition)).returncode, 0)
                system_path = root / ".agents/SYSTEM.json"
                original = getattr(PROJECT_OS, boundary)

                def change_system(*args, **kwargs):
                    value = json.loads(system_path.read_text())
                    value["toolchain_signals"] = ["python"]
                    system_path.write_text(json.dumps(value, indent=2) + "\n")
                    return original(*args, **kwargs)

                with mock.patch.object(PROJECT_OS, boundary, side_effect=change_system):
                    with self.assertRaisesRegex(PROJECT_OS.ProjectOSError, "changed"):
                        if operation == "sync":
                            PROJECT_OS.sync_knowledge(root, "selected", "selected", False)
                        elif operation == "start":
                            PROJECT_OS.start_program(root, definition, False)
                        else:
                            PROJECT_OS.close_program(root, "completed", None, False)
                self.assertEqual(json.loads(system_path.read_text())["toolchain_signals"], ["python"])

    def test_release_precedence_includes_prereleases_and_ignores_build_metadata(self):
        ordered = ["1.9.9", "2.0.0-alpha", "2.0.0-alpha.2", "2.0.0-alpha.10", "2.0.0-rc.1", "2.0.0", "2.0.1"]
        self.assertEqual(sorted(ordered, key=PROJECT_OS.release_order), ordered)
        self.assertEqual(PROJECT_OS.release_order("2.0.1+build.4"), PROJECT_OS.release_order("2.0.1"))
        for value in ("02.0.1", "2.0.1-01", None, [], "future"):
            with self.subTest(value=value), self.assertRaises(PROJECT_OS.ProjectOSError):
                PROJECT_OS.release_order(value)

    def test_program_close_refuses_plan_change_after_preview(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            self.assertEqual(run_cli("init", "--target", str(root)).returncode, 0)
            definition = write_program_definition(root)
            self.assertEqual(run_cli("program", "start", "--target", str(root), "--definition", str(definition)).returncode, 0)
            (root / ".agents/plans/001.md").write_text("# Plan 001\n\nOutcome: concurrent work.\n")
            before = file_hashes(root)
            plans_path = root / ".agents/plans/index.json"

            def activate_plan(*args):
                value = json.loads(plans_path.read_text())
                value["execution_state"] = "running"
                value["plans"] = [{"id": "001", "outcome": "Concurrent work", "status": "active", "path": ".agents/plans/001.md"}]
                plans_path.write_text(json.dumps(value, indent=2) + "\n")

            with mock.patch.object(PROJECT_OS, "print_transaction_preview", side_effect=activate_plan):
                with self.assertRaises(PROJECT_OS.ProjectOSError):
                    PROJECT_OS.close_program(root, "completed", None, False)
            after = file_hashes(root)
            before.pop(".agents/plans/index.json")
            after.pop(".agents/plans/index.json")
            self.assertEqual(after, before)

    def test_all_standard_private_key_markers_are_rejected(self):
        for prefix in ("", "RSA ", "EC ", "DSA ", "OPENSSH ", "ENCRYPTED "):
            with self.subTest(prefix=prefix):
                self.assertIn("private key", PROJECT_OS.private_material_labels(
                    {"mechanism": "-----BEGIN " + prefix + "PRIVATE KEY-----\nsynthetic"}
                ))

    def test_checker_rejects_pkcs8_marker_even_with_valid_content_baselines(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            self.assertEqual(run_cli("init", "--target", str(root)).returncode, 0)
            shared_path = root / ".agents/knowledge/shared/failures.json"
            value = json.loads(shared_path.read_text())
            entry = value["entries"][0]
            entry["mechanism"] = "-----BEGIN PRIVATE KEY-----\nsynthetic-marker-only"
            entry["source"]["content_hash"] = PROJECT_OS.entry_content_hash(entry)
            shared_path.write_text(json.dumps(value, indent=2) + "\n")
            system_path = root / ".agents/SYSTEM.json"
            system = json.loads(system_path.read_text())
            system["managed_knowledge"][entry["id"]] = entry["source"]["content_hash"]
            system_path.write_text(json.dumps(system, indent=2) + "\n")
            checked = run_cli("check", "--target", str(root))
            self.assertEqual(checked.returncode, 1)
            self.assertIn("private key", checked.stdout)

    def test_close_and_legacy_migration_recheck_plans_after_final_validation(self):
        for legacy in (False, True):
            with self.subTest(legacy=legacy), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary).resolve()
                self.assertEqual(run_cli("init", "--target", str(root)).returncode, 0)
                definition = write_program_definition(root)
                self.assertEqual(run_cli("program", "start", "--target", str(root), "--definition", str(definition)).returncode, 0)
                if legacy:
                    test_helpers.UpgradeTest().make_schema2(root, "full")
                (root / ".agents/plans/001.md").write_text("# Concurrent plan\n\nOutcome: concurrent work.\n")
                before = file_hashes(root)
                plans_path = root / ".agents/plans/index.json"
                original_check = PROJECT_OS.require_passing_check

                def activate_after_check(*args):
                    original_check(*args)
                    value = json.loads(plans_path.read_text())
                    value.update({"execution_state": "running", "active_plan": "001", "plans": [{
                        "id": "001", "status": "active", "outcome": "Concurrent work", "path": ".agents/plans/001.md"
                    }]})
                    plans_path.write_text(json.dumps(value, indent=2) + "\n")

                with mock.patch.object(PROJECT_OS, "require_passing_check", side_effect=activate_after_check):
                    with self.assertRaisesRegex(PROJECT_OS.ProjectOSError, "changed"):
                        if legacy:
                            PROJECT_OS.upgrade_project(root, "closed", "completed", "2026-09-07", None, False)
                        else:
                            PROJECT_OS.close_program(root, "completed", None, False)
                after = file_hashes(root)
                before.pop(".agents/plans/index.json")
                after.pop(".agents/plans/index.json")
                self.assertEqual(after, before)

    def test_non_object_package_json_has_diagnostic_without_traceback(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            for value in ([], None, 42, "text"):
                with self.subTest(value=value):
                    (root / "package.json").write_text(json.dumps(value))
                    before = file_hashes(root)
                    result = run_cli("detect", "--target", str(root))
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn("package.json must contain an object", result.stdout)
                    self.assertEqual(file_hashes(root), before)
