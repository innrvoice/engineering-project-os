"""Exercise complete supplied-tree snapshots and refusal before publication."""

import importlib.util
import hashlib
import io
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock
import zipfile


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/project-os/scripts/snapshot.py"
SPEC = importlib.util.spec_from_file_location("project_os_snapshot_test", SCRIPT)
SNAPSHOT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SNAPSHOT)
PROPOSAL = "campaign-output/proposals/ownership.json"


def file_bytes(root):
    return {path.relative_to(root).as_posix(): path.read_bytes()
            for path in root.rglob("*") if path.is_file() and not path.is_symlink()}


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.root = self.base / "payload"
        self.root.mkdir()
        for name, content in {
            ".agents/STATE.md": b"# State\r\n\r\n<!-- project-os-checkpoint: {\"complete\":true} -->\r\n",
            PROPOSAL: '{"lesson":"Straße"}\r\n'.encode("utf-8"),
            "MANIFEST.json": b'{"original":"preserve"}\n',
            "AUDIT.json": b'{"original":"audit"}\n',
            "app/data.bin": bytes(range(256)),
        }.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        (self.root / "empty").mkdir()
        self.output = self.base / "snapshot.zip"

    def command(self, *args):
        return subprocess.run([sys.executable, "-B", str(SCRIPT), *map(str, args)],
                              capture_output=True, text=True)

    def forged_zip(self, snapshot, manifest=None):
        if manifest is None:
            manifest = {"format": "project-os-byte-snapshot", "schema_version": 1,
                        "algorithm": "sha256", "required_paths": [],
                        "directories": snapshot["directories"], "files": [
                            {"path": name, "size": len(content),
                             "sha256": hashlib.sha256(content).hexdigest()}
                            for name, content in sorted(snapshot["files"].items())]}
        with io.BytesIO() as handle:
            with zipfile.ZipFile(handle, "w") as archive:
                entries = dict(snapshot["files"])
                entries.update({name + "/": b"" for name in snapshot["directories"]})
                entries[SNAPSHOT.MANIFEST] = json.dumps(manifest).encode()
                for name, content in entries.items():
                    entry = zipfile.ZipInfo(name)
                    entry.external_attr = ((stat.S_IFDIR | 0o755) if name.endswith("/")
                                           else (stat.S_IFREG | 0o600)) << 16
                    archive.writestr(entry, content)
            return handle.getvalue()

    def colliding_snapshots(self):
        for names, directories in [
            (["AGENTS.md", "agents.md"], []),
            (["caf\u00e9.md", "cafe\u0301.md"], []),
            (["Stra\u00dfe.md", "STRASSE.md"], []),
            (["Docs/a", "docs/b"], ["Docs", "docs"]),
            (["caf\u00e9/a", "cafe\u0301/b"], ["caf\u00e9", "cafe\u0301"]),
            (["Folder/a", "folder/b"], []),
            (["Docs", "docs/file"], []),
            (["bundle"], ["Bundle"]),
            (["same"], ["same"]),
        ]:
            yield {"files": {name: name.encode() for name in names},
                   "directories": directories, "identities": {}}

    def test_colliding_names_refuse_serialization_before_writing(self):
        for snapshot in self.colliding_snapshots():
            with self.subTest(paths=list(snapshot["files"])), io.BytesIO() as handle:
                with self.assertRaisesRegex(SNAPSHOT.SnapshotError, "collision"):
                    SNAPSHOT.write_zip(handle, snapshot, [])
                self.assertEqual(handle.getvalue(), b"")

    def test_forged_case_unicode_directory_and_prefix_alias_archives_are_rejected(self):
        for snapshot in self.colliding_snapshots():
            data = self.forged_zip(snapshot)
            with self.subTest(paths=list(snapshot["files"])):
                with self.assertRaisesRegex(SNAPSHOT.SnapshotError, "collision"):
                    SNAPSHOT.verify_zip(data, snapshot, [])

    def test_portable_source_case_collision_refuses_on_case_sensitive_filesystem(self):
        source = self.base / "case-source"
        source.mkdir()
        (source / "AGENTS.md").write_bytes(b"owner instructions")
        (source / "agents.md").write_bytes(b"different instructions")
        if len(list(source.iterdir())) != 2:
            self.skipTest("Source filesystem aliases case; Linux CI exercises distinct source entries")
        before = file_bytes(source)
        for dry_run in [True, False]:
            with self.assertRaisesRegex(SNAPSHOT.SnapshotError, "collision"):
                SNAPSHOT.create(source, self.output, dry_run=dry_run)
            self.assertFalse(self.output.exists())
        snapshot = {"files": before, "directories": [], "identities": {}}
        self.output.write_bytes(self.forged_zip(snapshot))
        with self.assertRaisesRegex(SNAPSHOT.SnapshotError, "collision"):
            SNAPSHOT.check(source, self.output)
        self.assertEqual(file_bytes(source), before)

    def test_portable_source_unicode_collision_refuses_on_normalization_sensitive_filesystem(self):
        source = self.base / "unicode-source"
        source.mkdir()
        (source / "caf\u00e9.md").write_bytes(b"first bytes")
        (source / "cafe\u0301.md").write_bytes(b"second bytes")
        if len(list(source.iterdir())) != 2:
            self.skipTest("Source filesystem aliases canonical forms; Linux CI exercises distinct entries")
        before = file_bytes(source)
        for dry_run in [True, False]:
            with self.assertRaisesRegex(SNAPSHOT.SnapshotError, "collision"):
                SNAPSHOT.create(source, self.output, dry_run=dry_run)
            self.assertFalse(self.output.exists())
        self.assertEqual(file_bytes(source), before)

    def test_manifest_alias_paths_are_rejected_even_with_distinct_archive_entries(self):
        snapshot = {"files": {"AGENTS.md": b"instructions"}, "directories": [], "identities": {}}
        manifest = SNAPSHOT.inventory(snapshot, [])
        for changed in [
            dict(manifest, files=manifest["files"] + [dict(manifest["files"][0], path="agents.md")]),
            dict(manifest, directories=["Docs", "docs"]),
            dict(manifest, directories=["agents.md"]),
            dict(manifest, directories=["caf\u00e9", "cafe\u0301"]),
        ]:
            with self.subTest(manifest=changed):
                with self.assertRaisesRegex(SNAPSHOT.SnapshotError, "collision"):
                    SNAPSHOT.verify_zip(self.forged_zip(snapshot, changed), snapshot, [])

    def test_distinct_unicode_paths_retain_original_spellings_and_bytes(self):
        snapshot = {"files": {"Caf\u00e9.md": b"original accent bytes\r\n",
                              "other/Stra\u00dfe.txt": b"original sharp-s bytes\x00\xff"},
                    "directories": ["other"], "identities": {}}
        with io.BytesIO() as handle:
            SNAPSHOT.write_zip(handle, snapshot, [])
            data = handle.getvalue()
        SNAPSHOT.verify_zip(data, snapshot, [])
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            for name, content in snapshot["files"].items():
                self.assertIn(name, archive.namelist())
                self.assertEqual(archive.read(name), content)

    def test_nested_proposal_hidden_receipt_binary_and_original_manifests_roundtrip(self):
        before = file_bytes(self.root)
        result = SNAPSHOT.create(self.root, self.output, [PROPOSAL, ".agents"])
        self.assertEqual(result["transport_integrity"], "VERIFIED")
        self.assertEqual(result["project_os_validation"], "NOT_PERFORMED")
        with zipfile.ZipFile(self.output) as archive:
            for name, content in before.items():
                self.assertEqual(archive.read(name), content, name)
            self.assertIn("empty/", archive.namelist())
            manifest = json.loads(archive.read(SNAPSHOT.MANIFEST))
            self.assertEqual({entry["path"] for entry in manifest["files"]}, set(before))
            extracted = self.base / "extracted"
            archive.extractall(extracted)
            extracted_files = file_bytes(extracted)
            self.assertEqual(set(extracted_files), set(before) | {SNAPSHOT.MANIFEST})
            for name, content in before.items():
                self.assertEqual(extracted_files[name], content, name)
        checked = SNAPSHOT.check(self.root, self.output, ["campaign-output/proposals"])
        self.assertEqual(checked["sha256"], result["sha256"])
        self.assertEqual(file_bytes(self.root), before)

    def test_two_snapshots_are_byte_identical(self):
        SNAPSHOT.create(self.root, self.output, [PROPOSAL])
        other = self.base / "second.zip"
        SNAPSHOT.create(self.root, other, [PROPOSAL])
        self.assertEqual(self.output.read_bytes(), other.read_bytes())

    def test_cli_dry_run_writes_nothing_then_check_is_readonly(self):
        before = file_bytes(self.base)
        preview = self.command("create", "--root", self.root, "--output", self.output,
                               "--require", PROPOSAL, "--dry-run")
        self.assertEqual(preview.returncode, 0, preview.stderr)
        report = json.loads(preview.stdout)
        self.assertFalse(report["archive_created"])
        self.assertEqual(report["transport_integrity"], "NOT_PERFORMED")
        self.assertNotIn("sha256", report)
        self.assertEqual({row["path"] for row in report["inventory"]["files"]},
                         set(file_bytes(self.root)))
        self.assertIn(PROPOSAL, {row["path"] for row in report["inventory"]["files"]})
        self.assertEqual(file_bytes(self.base), before)
        applied = self.command("create", "--root", self.root, "--output", self.output,
                               "--require", PROPOSAL)
        self.assertEqual(applied.returncode, 0, applied.stderr)
        before = file_bytes(self.base)
        checked = self.command("check", "--root", self.root, "--archive", self.output,
                               "--require", PROPOSAL)
        self.assertEqual(checked.returncode, 0, checked.stderr)
        self.assertEqual(file_bytes(self.base), before)

    def test_wide_tree_create_dry_run_and_check_with_256_descriptor_limit(self):
        for number in range(300):
            directory = self.root / f"sibling-{number:03d}"
            directory.mkdir()
            (directory / "payload.txt").write_bytes(b"complete source bytes\n")
        before = file_bytes(self.root)
        runner = (
            "import resource, runpy, sys; "
            "soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE); "
            "limit = 256 if hard == resource.RLIM_INFINITY else min(256, hard); "
            "resource.setrlimit(resource.RLIMIT_NOFILE, (limit, hard)); "
            "sys.argv = sys.argv[1:]; runpy.run_path(sys.argv[0], run_name='__main__')"
        )
        for args in [
            ["create", "--root", self.root, "--output", self.output, "--dry-run"],
            ["create", "--root", self.root, "--output", self.output],
            ["check", "--root", self.root, "--archive", self.output],
        ]:
            with self.subTest(operation=args[0], dry_run="--dry-run" in args):
                result = subprocess.run(
                    [sys.executable, "-B", "-c", runner, str(SCRIPT), *map(str, args)],
                    capture_output=True, text=True,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                report = json.loads(result.stdout)
                self.assertEqual(report["files"], len(before))
                self.assertEqual(report["project_os_validation"], "NOT_PERFORMED")
                if "--dry-run" in args:
                    self.assertFalse(self.output.exists())
                else:
                    self.assertEqual(report["transport_integrity"], "VERIFIED")
                self.assertEqual(file_bytes(self.root), before)

    def test_same_byte_directory_replacement_after_traversal_is_rejected(self):
        original_write = SNAPSHOT.write_zip
        proposals = self.root / "campaign-output/proposals"
        moved = self.base / "original-proposals"

        def replace_after_write(*args):
            original_write(*args)
            proposals.rename(moved)
            shutil.copytree(moved, proposals)

        with mock.patch.object(SNAPSHOT, "write_zip", side_effect=replace_after_write):
            with self.assertRaisesRegex(SNAPSHOT.SnapshotError, "changed"):
                SNAPSHOT.create(self.root, self.output, [PROPOSAL])
        self.assertFalse(self.output.exists())
        self.assertEqual(file_bytes(proposals), file_bytes(moved))

    def test_directory_replacement_during_traversal_is_rejected(self):
        original_read = SNAPSHOT.bounded_read_at
        proposals = self.root / "campaign-output/proposals"
        moved = self.base / "original-proposals"

        def replace_after_read(directory_fd, name, limit):
            result = original_read(directory_fd, name, limit)
            if name == "ownership.json" and not moved.exists():
                proposals.rename(moved)
                shutil.copytree(moved, proposals)
            return result

        with mock.patch.object(SNAPSHOT, "bounded_read_at", side_effect=replace_after_read):
            with self.assertRaisesRegex(SNAPSHOT.SnapshotError, "directory changed"):
                SNAPSHOT.create(self.root, self.output, [PROPOSAL])
        self.assertFalse(self.output.exists())
        self.assertEqual(file_bytes(proposals), file_bytes(moved))

    def test_missing_required_or_empty_directory_refuses_without_output(self):
        before = file_bytes(self.base)
        for name in ["campaign-output/proposals/missing.json", "empty"]:
            with self.subTest(name=name), self.assertRaisesRegex(SNAPSHOT.SnapshotError, "Required"):
                SNAPSHOT.create(self.root, self.output, [name])
        self.assertEqual(file_bytes(self.base), before)

    def test_unsafe_required_paths_fail_without_output(self):
        for name in ["", ".", "../payload", "/absolute", "a\\b", "a//b", "a/./b", "C:/path"]:
            with self.subTest(name=name), self.assertRaises(SNAPSHOT.SnapshotError):
                SNAPSHOT.create(self.root, self.output, [name])
        self.assertFalse(self.output.exists())

    def test_output_inside_source_and_existing_output_are_never_written(self):
        with self.assertRaisesRegex(SNAPSHOT.SnapshotError, "outside"):
            SNAPSHOT.create(self.root, self.root / "out.zip")
        self.output.write_bytes(b"owner artifact")
        with self.assertRaisesRegex(SNAPSHOT.SnapshotError, "overwrite"):
            SNAPSHOT.create(self.root, self.output)
        self.assertEqual(self.output.read_bytes(), b"owner artifact")

    def test_reserved_manifest_collision_refuses(self):
        (self.root / SNAPSHOT.MANIFEST).write_bytes(b"owner inventory")
        with self.assertRaisesRegex(SNAPSHOT.SnapshotError, "reserved"):
            SNAPSHOT.create(self.root, self.output)
        self.assertFalse(self.output.exists())

    def test_reserved_manifest_case_alias_file_and_directory_refuse_without_data_loss(self):
        alias = self.root / "PROJECT-OS-SNAPSHOT.JSON"
        alias.write_bytes(b"original owner manifest")
        before = file_bytes(self.root)
        with self.assertRaisesRegex(SNAPSHOT.SnapshotError, "reserved"):
            SNAPSHOT.create(self.root, self.output)
        self.assertEqual(file_bytes(self.root), before)
        self.assertFalse(self.output.exists())
        alias.unlink()
        alias.mkdir()
        (alias / "owner.txt").write_bytes(b"original owner directory")
        before = file_bytes(self.root)
        with self.assertRaisesRegex(SNAPSHOT.SnapshotError, "reserved"):
            SNAPSHOT.create(self.root, self.output)
        self.assertEqual(file_bytes(self.root), before)
        self.assertFalse(self.output.exists())

    def test_source_symlink_and_fifo_are_rejected_without_following(self):
        secret = self.base / "outside.txt"
        secret.write_bytes(b"not a payload")
        link = self.root / "linked"
        link.symlink_to(secret)
        with self.assertRaisesRegex(SNAPSHOT.SnapshotError, "regular"):
            SNAPSHOT.create(self.root, self.output)
        link.unlink()
        os.mkfifo(self.root / "pipe")
        with self.assertRaisesRegex(SNAPSHOT.SnapshotError, "regular"):
            SNAPSHOT.create(self.root, self.output)
        self.assertFalse(self.output.exists())
        self.assertEqual(secret.read_bytes(), b"not a payload")

    def test_root_and_output_parent_symlinks_are_rejected(self):
        alias = self.base / "alias"
        alias.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(SNAPSHOT.SnapshotError):
            SNAPSHOT.create(alias, self.output)
        outside = self.base / "exports"
        outside.mkdir()
        target = self.base / "exports-link"
        target.symlink_to(outside, target_is_directory=True)
        with self.assertRaises(SNAPSHOT.SnapshotError):
            SNAPSHOT.create(self.root, target / "snapshot.zip")
        self.assertEqual(list(outside.iterdir()), [])

    def test_source_filename_with_backslash_is_rejected(self):
        (self.root / "unsafe\\name").write_bytes(b"content")
        with self.assertRaisesRegex(SNAPSHOT.SnapshotError, "Unsafe"):
            SNAPSHOT.create(self.root, self.output)
        self.assertFalse(self.output.exists())

    def test_self_consistent_partial_archive_is_rejected_against_actual_root(self):
        SNAPSHOT.create(self.root, self.output, [PROPOSAL])
        partial = self.base / "partial.zip"
        with zipfile.ZipFile(self.output) as original, zipfile.ZipFile(partial, "w") as changed:
            for entry in original.infolist():
                if entry.filename == PROPOSAL:
                    continue
                content = original.read(entry.filename)
                if entry.filename == SNAPSHOT.MANIFEST:
                    manifest = json.loads(content)
                    manifest["files"] = [row for row in manifest["files"] if row["path"] != PROPOSAL]
                    manifest["required_paths"] = []
                    content = json.dumps(manifest).encode()
                changed.writestr(entry, content)
        with self.assertRaisesRegex(SNAPSHOT.SnapshotError, "actual source inventory"):
            SNAPSHOT.check(self.root, partial)

    def test_archive_changed_bytes_unsafe_type_and_extra_path_are_rejected(self):
        SNAPSHOT.create(self.root, self.output)
        for kind in ["bytes", "symlink", "extra"]:
            with self.subTest(kind=kind):
                changed_path = self.base / (kind + ".zip")
                with zipfile.ZipFile(self.output) as original, zipfile.ZipFile(changed_path, "w") as changed:
                    for entry in original.infolist():
                        content = original.read(entry.filename)
                        if entry.filename == "app/data.bin":
                            if kind == "bytes":
                                content = content[::-1]
                            if kind == "symlink":
                                entry.external_attr = (stat.S_IFLNK | 0o777) << 16
                        changed.writestr(entry, content)
                    if kind == "extra":
                        changed.writestr("../escape", b"outside")
                with self.assertRaises(SNAPSHOT.SnapshotError):
                    SNAPSHOT.check(self.root, changed_path)

    def test_post_export_source_changes_fail_readonly_check(self):
        SNAPSHOT.create(self.root, self.output)
        (self.root / PROPOSAL).write_bytes(b"changed proposal")
        before = file_bytes(self.base)
        with self.assertRaises(SNAPSHOT.SnapshotError):
            SNAPSHOT.check(self.root, self.output)
        self.assertEqual(file_bytes(self.base), before)

    def test_source_file_and_path_drift_during_serialization_refuses_publication(self):
        original_write = SNAPSHOT.write_zip
        for kind in ["edit", "add", "remove", "directory"]:
            with self.subTest(kind=kind):
                source = self.base / ("source-" + kind)
                shutil.copytree(self.root, source)
                output = self.base / (kind + ".zip")

                def change_after_write(*args):
                    original_write(*args)
                    if kind == "edit":
                        (source / PROPOSAL).write_bytes(b"new approved content")
                    elif kind == "add":
                        (source / "new.txt").write_bytes(b"new owner file")
                    elif kind == "remove":
                        (source / "app/data.bin").unlink()
                    else:
                        (source / "new-empty-directory").mkdir()

                with mock.patch.object(SNAPSHOT, "write_zip", side_effect=change_after_write):
                    with self.assertRaisesRegex(SNAPSHOT.SnapshotError, "changed"):
                        SNAPSHOT.create(source, output, [PROPOSAL])
                self.assertFalse(output.exists())
        self.assertFalse(list(self.base.glob(".project-os-snapshot-*.tmp")))

    def test_concurrent_destination_creation_is_preserved(self):
        original_open = SNAPSHOT.open_output

        def occupy_then_open(directory_fd, name):
            self.output.write_bytes(b"concurrent owner artifact")
            return original_open(directory_fd, name)

        with mock.patch.object(SNAPSHOT, "open_output", side_effect=occupy_then_open):
            with self.assertRaises(FileExistsError):
                SNAPSHOT.create(self.root, self.output)
        self.assertEqual(self.output.read_bytes(), b"concurrent owner artifact")
        self.assertFalse(list(self.base.glob(".project-os-snapshot-*.tmp")))

    def test_source_change_after_output_creation_reports_unverified_output(self):
        original_write = SNAPSHOT.write_output

        def mutate_after_write(*args):
            original_write(*args)
            (self.root / PROPOSAL).write_bytes(b"concurrent proposal update")

        with mock.patch.object(SNAPSHOT, "write_output", side_effect=mutate_after_write):
            with self.assertRaisesRegex(SNAPSHOT.SnapshotError, "unverified output may remain"):
                SNAPSHOT.create(self.root, self.output)
        self.assertTrue(self.output.exists())
        self.assertEqual((self.root / PROPOSAL).read_bytes(), b"concurrent proposal update")

    def test_error_after_output_creation_never_claims_success_or_deletes_by_name(self):
        original_write = SNAPSHOT.write_output

        def write_then_error(*args):
            original_write(*args)
            raise OSError("error after output write")

        with mock.patch.object(SNAPSHOT, "write_output", side_effect=write_then_error):
            with self.assertRaisesRegex(SNAPSHOT.SnapshotError, "unverified output may remain"):
                SNAPSHOT.create(self.root, self.output)
        self.assertTrue(self.output.exists())
        self.assertFalse(list(self.base.glob(".project-os-snapshot-*.tmp")))

    def test_concurrent_final_entry_replacement_survives_postcreation_failure(self):
        original_write = SNAPSHOT.write_output

        def replace_after_write(*args):
            original_write(*args)
            self.output.unlink()
            self.output.write_bytes(b"concurrent owner replacement")

        with mock.patch.object(SNAPSHOT, "write_output", side_effect=replace_after_write):
            with self.assertRaisesRegex(SNAPSHOT.SnapshotError, "unverified output may remain"):
                SNAPSHOT.create(self.root, self.output)
        self.assertEqual(self.output.read_bytes(), b"concurrent owner replacement")

    def test_output_parent_swap_cannot_redirect_publication_or_cleanup(self):
        folder = self.base / "exports"
        folder.mkdir()
        output = folder / "snapshot.zip"
        moved = self.base / "original-exports"
        original_write = SNAPSHOT.write_zip

        def swap_after_write(*args):
            original_write(*args)
            folder.rename(moved)
            folder.mkdir()
            output.write_bytes(b"unrelated replacement")

        with mock.patch.object(SNAPSHOT, "write_zip", side_effect=swap_after_write):
            with self.assertRaisesRegex(SNAPSHOT.SnapshotError, "Directory changed"):
                SNAPSHOT.create(self.root, output)
        self.assertEqual(output.read_bytes(), b"unrelated replacement")
        self.assertEqual(list(moved.iterdir()), [])

    def test_file_growing_after_stat_cannot_trigger_an_unbounded_read(self):
        path = self.base / "growing"
        path.write_bytes(b"x")
        original_fdopen = SNAPSHOT.os.fdopen
        sizes = []

        class GrowOnRead:
            def __init__(self, descriptor, mode):
                self.handle = original_fdopen(descriptor, mode)
                self.grew = False

            def __enter__(self):
                return self

            def __exit__(self, *args):
                self.handle.close()

            def fileno(self):
                return self.handle.fileno()

            def read(self, size=-1):
                sizes.append(size)
                self.test_size = size
                if size < 0:
                    raise AssertionError("unbounded file read")
                if not self.grew:
                    path.write_bytes(b"x" * 4096)
                    self.grew = True
                return self.handle.read(size)

        directory = os.open(self.base, os.O_RDONLY | os.O_DIRECTORY)
        try:
            with mock.patch.object(SNAPSHOT.os, "fdopen", side_effect=GrowOnRead):
                with self.assertRaisesRegex(SNAPSHOT.SnapshotError, "byte limit"):
                    SNAPSHOT.bounded_read_at(directory, path.name, 16)
        finally:
            os.close(directory)
        self.assertTrue(sizes)
        self.assertTrue(all(0 < size <= 17 for size in sizes))


if __name__ == "__main__":
    unittest.main()
