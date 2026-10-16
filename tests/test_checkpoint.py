"""Durable bounded-operation handoffs and their file-only recovery guard."""

import contextlib
import hashlib
import io
import json
import os
import shutil
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

from test_project_os import PROJECT_OS, file_hashes, run_cli, write_program_definition
from test_reusable_knowledge import bundle, lesson, write_json


class CheckpointTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.parent = Path(self.tmp.name).resolve()
        self.root = self.parent / "destination"
        self.root.mkdir()
        result = run_cli("init", "--target", str(self.root), "--packs", "none")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.state = self.root / ".agents/STATE.md"
        self.draft = self.parent / "handoff.md"
        self.draft.write_text(
            "# Current checkpoint\n\nUpdated: " + date.today().isoformat() + ".\n"
            "Execution state: idle.\nActive plan: none.\n\n"
            "Outcome: Import the reviewed core lesson.\n"
            "Verified: The selected import and structural check passed locally.\n"
            "Remaining: No further work is authorized for this bounded operation.\n"
            "Next action: Wait for the owner's next instruction.\n",
            encoding="utf-8",
        )

    def write(self, *extra):
        return run_cli("checkpoint", "--target", str(self.root), "--draft", str(self.draft), *extra)

    def check(self):
        return run_cli("checkpoint", "--target", str(self.root), "--check", "--json")

    def test_initial_scaffold_is_not_a_current_handoff_and_cannot_be_reused_as_a_draft(self):
        before = file_hashes(self.root)
        result = self.check()
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["checkpoint"], "STALE")
        self.draft.write_bytes(self.state.read_bytes())
        result = self.write()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Outcome", result.stderr)
        self.assertEqual(file_hashes(self.root), before)

    def test_dry_run_preserves_all_files_and_apply_binds_the_actual_owner_bytes(self):
        before = file_hashes(self.root)
        result = self.write("--dry-run")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(file_hashes(self.root), before)
        result = self.write()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(self.check().stdout)
        self.assertEqual(report["checkpoint"], "CURRENT")
        inputs = {item["path"]: item["sha256"] for item in report["receipt"]["inputs"]}
        self.assertEqual(set(inputs), {
            ".agents/SYSTEM.json", ".agents/plans/index.json", ".agents/requests.json",
            ".agents/findings/findings.json", ".agents/knowledge/reusable/failures.json",
            ".agents/knowledge/project/failures.json",
        })
        for path, digest in inputs.items():
            self.assertEqual(digest, "sha256:" + hashlib.sha256((self.root / path).read_bytes()).hexdigest())
        self.assertLessEqual(len(self.state.read_text().splitlines()), 80)
        after = file_hashes(self.root)
        before.pop(".agents/STATE.md")
        after.pop(".agents/STATE.md")
        self.assertEqual(after, before)

    def test_completed_import_invalidates_old_handoff_until_reconciled_then_survives_files_only_recovery(self):
        self.assertEqual(self.write().returncode, 0)
        source = self.parent / "approved.json"
        write_json(source, bundle([lesson("CORE-OWNERSHIP-001")]))
        source_digest = hashlib.sha256(source.read_bytes()).hexdigest()
        imported = run_cli("knowledge", "import", "--target", str(self.root), "--source", str(source), "--ids", "CORE-OWNERSHIP-001")
        self.assertEqual(imported.returncode, 0, imported.stdout + imported.stderr)
        self.assertEqual(run_cli("check", "--target", str(self.root)).returncode, 0)
        self.assertEqual(self.check().returncode, 1)
        self.draft.write_text(self.draft.read_text().replace(
            "The selected import and structural check passed locally.",
            "CORE-OWNERSHIP-001 is imported; the selected import and structural check passed locally.",
        ))
        self.assertEqual(self.write().returncode, 0)
        recovered = self.parent / "fresh-files-only"
        shutil.copytree(self.root, recovered)
        recovered_before = file_hashes(recovered)
        checked = run_cli("checkpoint", "--target", str(recovered), "--check", "--json")
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
        self.assertEqual(json.loads(checked.stdout)["checkpoint"], "CURRENT")
        self.assertIn("CORE-OWNERSHIP-001", (recovered / ".agents/STATE.md").read_text())
        self.assertEqual(file_hashes(recovered), recovered_before)
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), source_digest)

    def test_edited_body_changed_registry_and_forged_receipt_fail_without_writes(self):
        self.assertEqual(self.write().returncode, 0)
        original = self.state.read_bytes()
        for mode in ("body", "registry", "duplicate", "malformed"):
            with self.subTest(mode=mode):
                self.state.write_bytes(original)
                requests = self.root / ".agents/requests.json"
                request_original = requests.read_bytes()
                if mode == "body":
                    self.state.write_text(self.state.read_text().replace("Outcome: Import", "Outcome: Changed import"))
                elif mode == "registry":
                    requests.write_bytes(request_original + b"\n")
                elif mode == "duplicate":
                    self.state.write_text(self.state.read_text() + self.state.read_text().splitlines()[-1] + "\n")
                else:
                    self.state.write_text(self.state.read_text().replace('"schema_version":1', '"schema_version":'))
                before = file_hashes(self.root)
                self.assertEqual(self.check().returncode, 1)
                self.assertEqual(file_hashes(self.root), before)
                requests.write_bytes(request_original)

    def test_unsafe_state_symlink_and_draft_symlink_or_hardlink_are_rejected(self):
        before = file_hashes(self.root)
        draft_original = self.draft.read_bytes()
        self.draft.unlink()
        self.draft.symlink_to(self.state)
        self.assertNotEqual(self.write().returncode, 0)
        self.draft.unlink()
        os.link(self.state, self.draft)
        self.assertNotEqual(self.write().returncode, 0)
        self.draft.unlink()
        self.draft.write_bytes(draft_original)
        self.assertEqual(file_hashes(self.root), before)
        outside = self.parent / "outside.md"
        outside.write_text("Owner content.\n")
        state_original = self.state.read_bytes()
        self.state.unlink()
        self.state.symlink_to(outside)
        self.assertNotEqual(self.write().returncode, 0)
        self.assertEqual(outside.read_text(), "Owner content.\n")
        self.state.unlink()
        self.state.write_bytes(state_original)
        system_path = self.root / ".agents/SYSTEM.json"
        system = json.loads(system_path.read_text())
        system["paths"]["state"] = "../outside.md"
        write_json(system_path, system)
        agents = self.root / "AGENTS.md"
        agents.write_text(agents.read_text().replace(".agents/STATE.md", system["paths"]["state"]))
        self.assertNotEqual(self.write().returncode, 0)
        self.assertEqual(outside.read_text(), "Owner content.\n")

    def test_custom_state_and_owner_paths_are_respected(self):
        system_path = self.root / ".agents/SYSTEM.json"
        system = json.loads(system_path.read_text())
        for key in ("state", "plans", "requests", "findings", "reusable_knowledge"):
            original = self.root / system["paths"][key]
            destination = self.root / "records" / (key + original.suffix)
            destination.parent.mkdir(exist_ok=True)
            original.rename(destination)
            system["paths"][key] = destination.relative_to(self.root).as_posix()
        write_json(system_path, system)
        agents = self.root / "AGENTS.md"
        agents.write_text(agents.read_text().replace(".agents/STATE.md", system["paths"]["state"]))
        result = self.write()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        checked = self.check()
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
        self.assertIn('"path": "records/reusable_knowledge.json"', checked.stdout)
        self.assertFalse(self.state.exists())

    def test_state_execution_and_required_fields_cannot_be_omitted_or_disagree_with_registry(self):
        original = self.draft.read_text()
        for change in ("Execution state: running.", "Active plan: 001.", "Verified: ", "Next action: ", "Updated: 2026-99-99."):
            with self.subTest(change=change):
                field = change.split(":", 1)[0]
                lines = [change if line.startswith(field + ":") else line for line in original.splitlines()]
                self.draft.write_text("\n".join(lines) + "\n")
                before = file_hashes(self.root)
                self.assertNotEqual(self.write().returncode, 0)
                self.assertEqual(file_hashes(self.root), before)
        self.draft.write_bytes(b"\xff")
        self.assertNotEqual(self.write().returncode, 0)

    def test_running_checkpoint_preserves_active_plan_and_never_closes_it(self):
        index_path = self.root / ".agents/plans/index.json"
        index = json.loads(index_path.read_text())
        index.update(execution_state="running", active_plan="001", next_id=2)
        index["plans"] = [{"id": "001", "status": "active", "path": ".agents/plans/001.md",
                           "contract_path": ".agents/plans/001.json", "outcome": "Verify a bounded sample."}]
        write_json(index_path, index)
        (self.root / ".agents/plans/001.md").write_text("# Sample plan\n\nThe local outcome remains pending.\n")
        write_json(self.root / ".agents/plans/001.json", {
            "schema_version": 1, "plan_id": "001", "revision": 1, "gates": [{
                "id": "sample", "condition": "Verify local sample.", "evidence_class": "local", "target": "local",
                "status": "pending", "evidence": [], "next_action": "Run the sample.", "reason": "",
            }],
        })
        self.draft.write_text(self.draft.read_text().replace("Execution state: idle.", "Execution state: running.").replace(
            "Active plan: none.", "Active plan: 001.").replace(
            "Remaining: No further work is authorized for this bounded operation.", "Remaining: Verify the sample gate."))
        before = index_path.read_bytes()
        result = self.write()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.check().returncode, 0)
        self.assertEqual(index_path.read_bytes(), before)
        self.assertEqual(json.loads(index_path.read_text())["plans"][0]["status"], "active")
        status = run_cli("plan", "status", "--target", str(self.root), "--require-ready", "--json")
        self.assertEqual(status.returncode, 1)
        contract_path = self.root / ".agents/plans/001.json"
        contract = json.loads(contract_path.read_text())
        contract["revision"] = 2
        write_json(contract_path, contract)
        self.assertEqual(run_cli("check", "--target", str(self.root)).returncode, 0)
        self.assertEqual(self.check().returncode, 1)
        self.assertEqual(self.write().returncode, 0)
        (self.root / ".agents/plans/001.md").write_text("# Revised active plan\n\nNew supported detail.\n")
        self.assertEqual(self.check().returncode, 1)

    def test_program_checkpoint_binds_current_program_definition(self):
        definition = write_program_definition(self.root)
        started = run_cli("program", "start", "--target", str(self.root), "--definition", str(definition))
        self.assertEqual(started.returncode, 0, started.stdout + started.stderr)
        result = self.write()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(self.check().stdout)
        self.assertIn(".agents/PROGRAM.md", [item["path"] for item in report["receipt"]["inputs"]])
        program = self.root / ".agents/PROGRAM.md"
        program.write_text(program.read_text() + "\nAn additional observed boundary.\n")
        self.assertEqual(self.check().returncode, 1)

    def test_checkpoint_draft_limit_reserves_space_for_receipt(self):
        original = self.draft.read_text()
        for line_count, returncode in ((78, 0), (79, 2)):
            with self.subTest(line_count=line_count):
                self.draft.write_text(original + "Observed detail.\n" * (line_count - len(original.splitlines())))
                result = self.write()
                self.assertEqual(result.returncode, returncode, result.stdout + result.stderr)
        self.assertEqual(len(self.state.read_text().splitlines()), 80)

    def test_read_only_check_detects_concurrent_dependency_or_state_edit(self):
        self.assertEqual(self.write().returncode, 0)
        for target in (self.root / ".agents/requests.json", self.state):
            with self.subTest(target=target.name):
                original_bytes = target.read_bytes()
                before = file_hashes(self.root)
                original = PROJECT_OS.checkpoint_receipt
                def race(*args, **kwargs):
                    value = original(*args, **kwargs)
                    target.write_bytes(original_bytes + b"\n")
                    return value
                with contextlib.redirect_stdout(io.StringIO()) as output, mock.patch.object(PROJECT_OS, "checkpoint_receipt", side_effect=race):
                    result = PROJECT_OS.checkpoint_check(self.root, True)
                self.assertEqual(result, 1)
                self.assertEqual(json.loads(output.getvalue())["checkpoint"], "STALE")
                self.assertEqual(target.read_bytes(), original_bytes + b"\n")
                after = file_hashes(self.root)
                relative = target.relative_to(self.root).as_posix()
                before.pop(relative)
                after.pop(relative)
                self.assertEqual(after, before)
                target.write_bytes(original_bytes)

    def test_write_or_final_validation_failure_rolls_back(self):
        for boundary in ("atomic_write_text", "require_passing_check"):
            with self.subTest(boundary=boundary):
                before = file_hashes(self.root)
                with contextlib.redirect_stdout(io.StringIO()), mock.patch.object(PROJECT_OS, boundary, side_effect=PROJECT_OS.ProjectOSError("injected failure")):
                    with self.assertRaises(PROJECT_OS.ProjectOSError):
                        PROJECT_OS.write_checkpoint(self.root, self.draft, False)
                self.assertEqual(file_hashes(self.root), before)

    def test_concurrent_registry_or_draft_edit_aborts_and_preserves_other_data(self):
        for boundary, target in (("print_transaction_preview", self.root / ".agents/requests.json"),
                                 ("require_passing_check", self.root / ".agents/requests.json"),
                                 ("require_passing_check", self.state),
                                 ("print_transaction_preview", self.draft),
                                 ("require_passing_check", self.draft)):
            with self.subTest(boundary=boundary, target=target.name):
                before = file_hashes(self.root)
                original_bytes = target.read_bytes()
                original = getattr(PROJECT_OS, boundary)
                def race(*args):
                    result = original(*args)
                    target.write_bytes(original_bytes + b"\n")
                    return result
                with contextlib.redirect_stdout(io.StringIO()), mock.patch.object(PROJECT_OS, boundary, side_effect=race):
                    with self.assertRaisesRegex(PROJECT_OS.ProjectOSError, "changed"):
                        PROJECT_OS.write_checkpoint(self.root, self.draft, False)
                self.assertEqual(target.read_bytes(), original_bytes + b"\n")
                after = file_hashes(self.root)
                if target.is_relative_to(self.root):
                    before.pop(target.relative_to(self.root).as_posix())
                    after.pop(target.relative_to(self.root).as_posix())
                self.assertEqual(after, before)
                target.write_bytes(original_bytes)


if __name__ == "__main__":
    unittest.main()
