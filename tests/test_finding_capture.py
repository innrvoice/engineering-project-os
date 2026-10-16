from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "skills/project-os/scripts/project_os.py"
SPEC = importlib.util.spec_from_file_location("project_os_findings", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
P = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(P)


class FindingCaptureTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.parent = Path(self.temporary.name).resolve()
        self.root = self.parent / "project"
        self.root.mkdir()
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(P.init_project(self.root, "none", "none", False, False), 0)
        self.registry_path = self.root / ".agents/findings/findings.json"
        self.evidence_path = self.root / ".agents/evidence/normalization.md"
        self.evidence_path.write_text("Observed normalize(None) raises AttributeError before the repair.\n")
        self.input_path = self.parent / "finding.json"
        self.definition = {
            "title": "None crashes normalization",
            "status": "confirmed",
            "impact": "The supported absent input raises an unintended AttributeError.",
            "evidence": [".agents/evidence/normalization.md"],
            "required_check": "None raises ValueError and text normalization still passes.",
        }
        self.write_input()

    def write_input(self) -> None:
        self.input_path.write_text(json.dumps(self.definition) + "\n")

    def record(self, identifier: str | None = None, dry_run: bool = False) -> int:
        with contextlib.redirect_stdout(io.StringIO()):
            return P.record_finding(self.root, self.input_path, identifier, dry_run)

    def registry(self) -> dict:
        return json.loads(self.registry_path.read_text())

    def snapshot(self) -> dict[str, bytes]:
        return {path.relative_to(self.root).as_posix(): path.read_bytes()
                for path in self.root.rglob("*") if path.is_file() and not path.is_symlink()}

    def test_reproduced_fixed_defect_persists_and_fresh_process_recovers(self) -> None:
        app = self.root / "normalization.py"
        app.write_text("def normalize(value):\n    return value.strip()\n")
        test = self.root / "test_normalization.py"
        test.write_text("import unittest\nfrom normalization import normalize\n"
                        "class NormalizationTest(unittest.TestCase):\n"
                        "    def test_none(self):\n"
                        "        with self.assertRaises(ValueError): normalize(None)\n"
                        "    def test_text(self):\n"
                        "        self.assertEqual(normalize(' hi '), 'hi')\n")
        command = [sys.executable, "-B", "-m", "unittest", "-v", "test_normalization.py"]
        before = subprocess.run(command, cwd=self.root, capture_output=True, text=True)
        self.assertNotEqual(before.returncode, 0)
        self.assertIn("AttributeError", before.stderr)
        self.evidence_path.write_text("Target: isolated local fixture.\nBefore repair:\n" + before.stderr)
        self.assertEqual(self.record(), 0)
        identifier = self.registry()["findings"][0]["id"]
        app.write_text("def normalize(value):\n    if value is None:\n        raise ValueError('None')\n    return value.strip()\n")
        after = subprocess.run(command, cwd=self.root, capture_output=True, text=True)
        self.assertEqual(after.returncode, 0, after.stderr)
        self.evidence_path.write_text(self.evidence_path.read_text() + "\nAfter repair:\n" + after.stderr)
        self.definition.update(status="verified", resolution="Reject None explicitly before stripping text.")
        self.write_input()
        # An explicit update can refresh changed proof while retaining the original ID.
        self.assertEqual(self.record(identifier), 0)
        recovered = subprocess.run([sys.executable, "-B", str(SCRIPT), "check", "--target", str(self.root)],
                                   capture_output=True, text=True)
        self.assertEqual(recovered.returncode, 0, recovered.stdout + recovered.stderr)
        entry = self.registry()["findings"][0]
        self.assertEqual(entry["id"], identifier)
        self.assertEqual(entry["status"], "verified")
        self.assertEqual(entry["evidence_sha256"][self.definition["evidence"][0]],
                         "sha256:" + hashlib.sha256(self.evidence_path.read_bytes()).hexdigest())
        self.assertEqual(self.registry()["next_id"], 2)

    def test_identical_capture_is_idempotent_and_title_does_not_merge_incidents(self) -> None:
        self.record()
        initial = self.registry_path.read_bytes()
        self.record()
        self.assertEqual(self.registry_path.read_bytes(), initial)
        self.definition["impact"] = "A different call site has the same short title."
        self.write_input()
        self.record()
        self.assertEqual([entry["id"] for entry in self.registry()["findings"]], ["F-001", "F-002"])

    def test_existing_prefix_and_fields_are_preserved(self) -> None:
        legacy = dict(self.definition, id="AUDIT-012", owner_note="Keep this local decision.",
                      observation="The original reproduction remains part of the incident.")
        self.registry_path.write_text(json.dumps({"schema_version": 1, "next_id": 1, "findings": [legacy]}))
        self.definition["title"] = "Another observed defect"
        self.write_input()
        self.record()
        self.assertEqual(self.registry()["findings"][1]["id"], "AUDIT-013")
        self.assertEqual(self.registry()["next_id"], 14)
        self.definition["title"] = "A clarified observed defect"
        self.write_input()
        self.record("AUDIT-012")
        self.assertEqual(self.registry()["findings"][0]["owner_note"], "Keep this local decision.")
        self.assertEqual(self.registry()["findings"][0]["observation"],
                         "The original reproduction remains part of the incident.")
        self.assertEqual(self.registry()["findings"][0]["id"], "AUDIT-012")
        before = self.registry_path.read_bytes()
        self.record()
        self.assertEqual(self.registry_path.read_bytes(), before)

    def test_custom_findings_path_and_unrelated_records_are_preserved(self) -> None:
        system_path = self.root / ".agents/SYSTEM.json"
        system = json.loads(system_path.read_text())
        destination = self.root / ".agents/local-incidents.json"
        self.registry_path.rename(destination)
        system["paths"]["findings"] = ".agents/local-incidents.json"
        system_path.write_text(json.dumps(system))
        self.registry_path = destination
        keep = self.root / "KEEP.md"
        keep.write_text("Unrelated owner data.\n")
        before = self.snapshot()
        self.record()
        for path, content in before.items():
            if path != ".agents/local-incidents.json":
                self.assertEqual((self.root / path).read_bytes(), content, path)

    def test_dry_run_changes_no_files(self) -> None:
        before = self.snapshot()
        self.record(dry_run=True)
        self.assertEqual(self.snapshot(), before)

    def test_rejects_unknown_id_invalid_input_and_unproven_verified_resolution(self) -> None:
        cases = [None, [], {}, dict(self.definition, status="done"),
                 dict(self.definition, evidence=[]), dict(self.definition, impact=""),
                 dict(self.definition, status="verified"), dict(self.definition, id="F-001")]
        before = self.snapshot()
        for value in cases:
            with self.subTest(value=value):
                self.input_path.write_text(json.dumps(value))
                with self.assertRaises(P.ProjectOSError):
                    self.record()
                self.assertEqual(self.snapshot(), before)
        self.write_input()
        with self.assertRaisesRegex(P.ProjectOSError, "Unknown finding ID"):
            self.record("F-999")
        self.assertEqual(self.snapshot(), before)

    def test_rejects_unsafe_missing_directory_and_symlink_evidence(self) -> None:
        outside = self.parent / "outside.md"
        outside.write_text("Outside bytes.\n")
        link = self.root / ".agents/evidence/link.md"
        link.symlink_to(outside)
        for path in ["../outside.md", str(outside), ".agents/evidence/missing.md",
                     ".agents/evidence", ".agents/evidence/link.md", ".agents/findings/findings.json",
                     ".agents/evidence/../evidence/normalization.md"]:
            with self.subTest(path=path):
                self.definition["evidence"] = [path]
                self.write_input()
                before = self.registry_path.read_bytes()
                with self.assertRaises((P.ProjectOSError, OSError)):
                    self.record()
                self.assertEqual(self.registry_path.read_bytes(), before)
                self.assertEqual(outside.read_text(), "Outside bytes.\n")

    def test_rejects_symlink_input(self) -> None:
        link = self.parent / "input-link.json"
        link.symlink_to(self.input_path)
        before = self.snapshot()
        with self.assertRaises(P.ProjectOSError):
            with contextlib.redirect_stdout(io.StringIO()):
                P.record_finding(self.root, link, None, False)
        self.assertEqual(self.snapshot(), before)

    def test_external_temporary_parent_alias_is_selected_once(self) -> None:
        alias = self.parent / "temporary-parent-alias"
        alias.symlink_to(self.parent, target_is_directory=True)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(P.record_finding(self.root, alias / self.input_path.name, None, False), 0)
        self.assertEqual(self.registry()["findings"][0]["id"], "F-001")
        self.assertTrue(alias.is_symlink())

    def test_internal_parent_symlink_is_still_rejected(self) -> None:
        alias = self.root / "input-alias"
        alias.symlink_to(self.parent, target_is_directory=True)
        before = self.snapshot()
        with self.assertRaises(P.ProjectOSError):
            with contextlib.redirect_stdout(io.StringIO()):
                P.record_finding(self.root, alias / self.input_path.name, None, False)
        self.assertEqual(self.snapshot(), before)

    def test_cli_missing_inputs_report_actionable_error_without_traceback(self) -> None:
        before = self.snapshot()
        for path in [self.parent / "missing-input.json", self.input_path]:
            self.definition["evidence"] = [".agents/evidence/missing.md"]
            self.write_input()
            result = subprocess.run([sys.executable, "-B", str(SCRIPT), "finding", "record",
                                     "--target", str(self.root), "--input", str(path)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn("error: Finding", result.stderr)
            self.assertNotIn("Traceback", result.stderr)
            self.assertEqual(self.snapshot(), before)

    def test_changed_evidence_fails_check_without_erasing_record(self) -> None:
        self.record()
        original = self.registry_path.read_bytes()
        self.evidence_path.write_text("A newer observation must be evaluated before retaining verified proof.\n")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(P.check_project(self.root), 1)
        self.assertIn("evidence changed", output.getvalue())
        self.assertEqual(self.registry_path.read_bytes(), original)

    def test_final_check_failure_rolls_back(self) -> None:
        before = self.snapshot()
        with mock.patch.object(P, "require_passing_check", side_effect=P.ProjectOSError("Injected final check failure")):
            with self.assertRaisesRegex(P.ProjectOSError, "rolled back"):
                self.record()
        self.assertEqual(self.snapshot(), before)

    def test_write_failure_leaves_records_untouched(self) -> None:
        before = self.snapshot()
        with mock.patch.object(P, "atomic_write_text", side_effect=OSError("Injected write failure")):
            with self.assertRaisesRegex(P.ProjectOSError, "rolled back"):
                self.record()
        self.assertEqual(self.snapshot(), before)

    def test_concurrent_input_edit_aborts_before_writing(self) -> None:
        before = self.snapshot()
        with mock.patch.object(P, "print_transaction_preview", side_effect=lambda *args: self.input_path.write_text("{}")):
            with self.assertRaisesRegex(P.ProjectOSError, "Finding input changed"):
                self.record()
        self.assertEqual(self.snapshot(), before)

    def test_concurrent_evidence_edit_before_write_is_preserved(self) -> None:
        original = self.registry_path.read_bytes()
        execute = P.execute_sync_transaction

        def change_then_execute(*args, **kwargs):
            self.evidence_path.write_text("Concurrent evidence.\n")
            return execute(*args, **kwargs)

        with mock.patch.object(P, "execute_sync_transaction", side_effect=change_then_execute):
            with self.assertRaisesRegex(P.ProjectOSError, "changed during operation"):
                self.record()
        self.assertEqual(self.registry_path.read_bytes(), original)
        self.assertEqual(self.evidence_path.read_text(), "Concurrent evidence.\n")

    def test_concurrent_evidence_edit_after_check_rolls_back_only_owned_write(self) -> None:
        original = self.registry_path.read_bytes()
        check = P.require_passing_check

        def check_then_change(*args):
            check(*args)
            self.evidence_path.write_text("Concurrent evidence after check.\n")

        with mock.patch.object(P, "require_passing_check", side_effect=check_then_change):
            with self.assertRaisesRegex(P.ProjectOSError, "changed during operation"):
                self.record()
        self.assertEqual(self.registry_path.read_bytes(), original)
        self.assertEqual(self.evidence_path.read_text(), "Concurrent evidence after check.\n")

    def test_concurrent_input_edit_after_check_rolls_back(self) -> None:
        original = self.registry_path.read_bytes()
        check = P.require_passing_check

        def check_then_change(*args):
            check(*args)
            self.input_path.write_text("{}")

        with mock.patch.object(P, "require_passing_check", side_effect=check_then_change):
            with self.assertRaisesRegex(P.ProjectOSError, "Finding input changed"):
                self.record()
        self.assertEqual(self.registry_path.read_bytes(), original)
        self.assertEqual(self.input_path.read_text(), "{}")

    def test_concurrent_system_edit_after_check_is_preserved(self) -> None:
        original = self.registry_path.read_bytes()
        system_path = self.root / ".agents/SYSTEM.json"
        check = P.require_passing_check
        changed = json.loads(system_path.read_text())
        changed["owner_note"] = "Concurrent owner update."
        changed_bytes = P.canonical_json(changed)

        def check_then_change(*args):
            check(*args)
            system_path.write_text(changed_bytes)

        with mock.patch.object(P, "require_passing_check", side_effect=check_then_change):
            with self.assertRaisesRegex(P.ProjectOSError, "changed during operation"):
                self.record()
        self.assertEqual(self.registry_path.read_bytes(), original)
        self.assertEqual(system_path.read_text(), changed_bytes)

    def test_concurrent_registry_edit_after_check_is_not_overwritten_by_rollback(self) -> None:
        check = P.require_passing_check
        concurrent = []

        def check_then_change(*args):
            check(*args)
            value = self.registry()
            value["owner_note"] = "Concurrent owner update."
            concurrent.append(P.canonical_json(value))
            self.registry_path.write_text(concurrent[0])

        with mock.patch.object(P, "require_passing_check", side_effect=check_then_change):
            with self.assertRaisesRegex(P.ProjectOSError, "rollback incomplete"):
                self.record()
        self.assertEqual(self.registry_path.read_text(), concurrent[0])

    def test_evidence_parent_swap_during_write_refuses_outside_file(self) -> None:
        outside = self.parent / "outside-evidence"
        outside.mkdir()
        outside_evidence = outside / "normalization.md"
        outside_evidence.write_text("Outside proof.\n")
        evidence_dir = self.evidence_path.parent
        preserved = evidence_dir.with_name("preserved-evidence")
        original = self.registry_path.read_bytes()
        execute = P.execute_sync_transaction

        def swap_then_execute(*args, **kwargs):
            evidence_dir.rename(preserved)
            evidence_dir.symlink_to(outside, target_is_directory=True)
            return execute(*args, **kwargs)

        with mock.patch.object(P, "execute_sync_transaction", side_effect=swap_then_execute):
            with self.assertRaises(P.ProjectOSError):
                self.record()
        self.assertEqual(self.registry_path.read_bytes(), original)
        self.assertEqual(outside_evidence.read_text(), "Outside proof.\n")

    def test_check_rejects_incomplete_or_malformed_proof_map(self) -> None:
        self.record()
        value = self.registry()
        for proofs in [{}, {".agents/evidence/normalization.md": "wrong"},
                       {"../outside.md": "sha256:" + "0" * 64}]:
            with self.subTest(proofs=proofs):
                value["findings"][0]["evidence_sha256"] = proofs
                self.registry_path.write_text(json.dumps(value))
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    self.assertEqual(P.check_project(self.root), 1)
                self.assertIn("evidence_sha256", output.getvalue())


if __name__ == "__main__":
    unittest.main()
