"""A compact inspection preserves source checks, blockers and record ownership."""

import contextlib
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from test_project_os import PROJECT_OS, file_hashes, run_cli, write_program_definition


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


class ProjectBriefTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.parent = Path(self.tmp.name).resolve()
        self.root = self.parent / "project"
        self.root.mkdir()
        result = run_cli("init", "--target", str(self.root), "--packs", "none")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.index = self.root / ".agents/plans/index.json"
        self.requests = self.root / ".agents/requests.json"

    def checkpoint(self, active=False):
        draft = self.parent / "checkpoint.md"
        draft.write_text(
            "# Current checkpoint\n\nUpdated: 2026-11-01.\n"
            + ("Execution state: running.\nActive plan: 001.\n" if active else
               "Execution state: idle.\nActive plan: none.\n")
            + "Outcome: Inspect local records.\nVerified: Synthetic local checks.\n"
            "Remaining: Follow the recorded gates.\nNext action: Read the named records.\n",
            encoding="utf-8",
        )
        result = run_cli("checkpoint", "--target", str(self.root), "--draft", str(draft))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def add_plan(self, identifier="001", status="active", verified=False):
        plan_path = f".agents/plans/{identifier}.md"
        contract_path = f".agents/plans/{identifier}.json"
        (self.root / plan_path).write_text("# Synthetic plan\n\nInspect local behavior.\n")
        evidence = []
        if verified:
            proof_path = f".agents/evidence/{identifier}.md"
            (self.root / proof_path).write_text("Synthetic verification evidence.\n")
            evidence = [{"path": proof_path,
                         "sha256": "sha256:" + hashlib.sha256((self.root / proof_path).read_bytes()).hexdigest(),
                         "checked_on": "2026-11-01", "target": "local", "revision": 1}]
        write_json(self.root / contract_path, {
            "schema_version": 1, "plan_id": identifier, "revision": 1,
            "gates": [{"id": "sample", "condition": "Verify the sample.", "evidence_class": "source",
                       "target": "local", "status": "verified" if verified else "pending",
                       "evidence": evidence, "next_action": "" if verified else "Run the sample.", "reason": ""}],
        })
        index = json.loads(self.index.read_text())
        index["plans"].append({"id": identifier, "status": status, "path": plan_path,
                               "contract_path": contract_path, "outcome": "Inspect local behavior."})
        index["next_id"] = int(identifier) + 1
        if status == "active":
            index.update(execution_state="running", active_plan=identifier)
        write_json(self.index, index)

    def brief(self):
        result = run_cli("brief", "--target", str(self.root), "--json")
        self.assertEqual(result.stderr, "")
        return result, json.loads(result.stdout)

    def test_idle_matches_source_checks_and_both_formats_preserve_every_file(self):
        self.checkpoint()
        before = file_hashes(self.root)
        result, report = self.brief()
        self.assertEqual(result.returncode, run_cli("check", "--target", str(self.root)).returncode)
        checkpoint = json.loads(run_cli("checkpoint", "--target", str(self.root), "--check", "--json").stdout)
        self.assertEqual(report["checkpoint"]["status"], checkpoint["checkpoint"])
        self.assertEqual(report["integrity"], "PASS")
        self.assertTrue(report["records_available"])
        self.assertEqual(report["execution_state"], "idle")
        self.assertIsNone(report["active_plan"])
        self.assertNotIn("readiness", report)
        text = run_cli("brief", "--target", str(self.root))
        self.assertEqual(text.returncode, 0)
        self.assertIn("Record integrity: PASS", text.stdout)
        self.assertEqual(file_hashes(self.root), before)

    def test_pending_gates_and_all_unresolved_requests_survive_reduction(self):
        self.add_plan()
        self.add_plan("002", "planned")
        self.add_plan("003", "blocked")
        entries = []
        for number, status in enumerate(("integrated", "captured", "withdrawn"), 1):
            entries.append({"id": f"R-{number:03}", "recorded_on": "2026-11-01",
                            "source_text": "Verify the sample.", "interpretation": "Keep this requirement visible.",
                            "origin_plan": "001", "target_plan": "001" if status == "integrated" else None,
                            "relation": "same_outcome", "status": status,
                            "gate_ids": ["sample"] if status == "integrated" else [],
                            "decision": "Synthetic request status.",
                            "owner_note": {"boundary": "Retain the original owner instruction."}})
        write_json(self.requests, {"schema_version": 1, "next_id": 4, "requests": entries})
        self.checkpoint(active=True)
        before = file_hashes(self.root)
        result, report = self.brief()
        source = json.loads(run_cli("plan", "status", "--target", str(self.root), "--json").stdout)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(report["active_plan"]["readiness"], "NOT_READY")
        self.assertEqual(report["active_plan"]["blockers"], source["readiness_blockers"])
        self.assertEqual(report["active_plan"]["pending_gates"], source["gates"])
        self.assertEqual([r["id"] for r in report["unresolved_requests"]], ["R-001", "R-002"])
        self.assertEqual(report["unresolved_requests"], entries[:2])
        self.assertEqual([p["status"] for p in report["other_plans"]], ["planned", "blocked"])
        self.assertEqual(report["counts"]["requests"], 3)
        self.assertIn(".agents/plans/001.json", report["read_next"])
        self.assertNotIn(".agents/plans/index.json", report["read_next"])
        self.assertNotIn(".agents/requests.json", report["read_next"])
        self.assertEqual(report["record_paths"]["requests"], ".agents/requests.json")
        self.assertEqual(file_hashes(self.root), before)

    def test_verified_gate_is_counted_and_ready_remains_scoped_to_the_active_plan(self):
        self.add_plan(verified=True)
        self.checkpoint(active=True)
        result, report = self.brief()
        self.assertEqual(result.returncode, 0)
        self.assertEqual(report["active_plan"]["readiness"], "READY")
        self.assertEqual(report["active_plan"]["pending_gates"], [])
        self.assertEqual(report["active_plan"]["gate_counts"]["verified"], 1)
        self.assertIn(".agents/plans/001.json", report["read_next"])

    def test_stale_checkpoint_fails_with_the_original_diagnostic_and_keeps_pending_work(self):
        self.add_plan()
        self.checkpoint(active=True)
        self.requests.write_bytes(self.requests.read_bytes() + b"\n")
        before = file_hashes(self.root)
        result, report = self.brief()
        source = json.loads(run_cli("checkpoint", "--target", str(self.root), "--check", "--json").stdout)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(report["structure"], "PASS")
        self.assertEqual(report["checkpoint"]["status"], "STALE")
        self.assertEqual(report["checkpoint"]["errors"], source["errors"])
        self.assertTrue(report["active_plan"]["pending_gates"])
        self.assertEqual(file_hashes(self.root), before)

    def test_invalid_evidence_and_malformed_records_return_json_without_a_trusted_summary(self):
        self.add_plan(verified=True)
        self.checkpoint(active=True)
        (self.root / ".agents/evidence/001.md").write_text("Changed evidence.\n")
        before = file_hashes(self.root)
        result, report = self.brief()
        self.assertEqual(result.returncode, 1)
        self.assertFalse(report["records_available"])
        self.assertEqual(report["structure"], "FAIL")
        self.assertTrue(any("hash" in error.lower() for error in report["errors"]))
        self.assertEqual(file_hashes(self.root), before)
        self.requests.write_text("{broken json")
        result, report = self.brief()
        self.assertEqual(result.returncode, 1)
        self.assertFalse(report["records_available"])
        self.assertTrue(report["errors"])

    def test_custom_record_paths_are_used_for_the_checkpoint_and_read_routing(self):
        system_path = self.root / ".agents/SYSTEM.json"
        system = json.loads(system_path.read_text())
        (self.root / "records").mkdir()
        for key in ("state", "plans", "requests"):
            original = self.root / system["paths"][key]
            relative = "records/" + key + original.suffix
            original.rename(self.root / relative)
            system["paths"][key] = relative
        write_json(system_path, system)
        agents = self.root / "AGENTS.md"
        agents.write_text(agents.read_text().replace(".agents/STATE.md", "records/state.md"))
        self.checkpoint()
        result, report = self.brief()
        self.assertEqual(result.returncode, 0, report)
        self.assertEqual(report["checkpoint"]["status"], "CURRENT")
        self.assertIn("records/state.md", report["read_next"])
        for key, relative in (("plans", "records/plans.json"), ("requests", "records/requests.json")):
            self.assertEqual(report["record_paths"][key], relative)
            self.assertNotIn(relative, report["read_next"])

    def test_bootstrap_and_upgrade_deliver_recovery_without_overwriting_owner_records(self):
        workflow = self.root / ".agents/WORKFLOW.md"
        expected = workflow.read_bytes()
        self.assertIn(b"brief --target <repository> --json", expected)
        self.assertIn(b"before reading full plan or request registries", expected)
        self.assertIn("brief --target <repository> --json", (self.root / "AGENTS.md").read_text())
        legacy = b"# Older managed workflow\n\nRead saved records before continuing work.\n"
        workflow.write_bytes(legacy)
        system_path = self.root / ".agents/SYSTEM.json"
        system = json.loads(system_path.read_text())
        system["managed_guidance"][".agents/WORKFLOW.md"] = "sha256:" + hashlib.sha256(legacy).hexdigest()
        write_json(system_path, system)
        owner_note = self.root / ".agents/owner-notes.md"
        owner_note.write_text("Preserve this owner-controlled content.\n")
        before = file_hashes(self.root)
        preview = run_cli("upgrade", "--target", str(self.root), "--dry-run")
        self.assertEqual(preview.returncode, 0, preview.stdout + preview.stderr)
        self.assertEqual(file_hashes(self.root), before)
        result = run_cli("upgrade", "--target", str(self.root))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(workflow.read_bytes(), expected)
        after = file_hashes(self.root)
        for allowed in (".agents/SYSTEM.json", ".agents/WORKFLOW.md"):
            before.pop(allowed)
            after.pop(allowed)
        self.assertEqual(after, before)
        stable = file_hashes(self.root)
        self.assertEqual(run_cli("upgrade", "--target", str(self.root)).returncode, 0)
        self.assertEqual(file_hashes(self.root), stable)

    def test_upgrade_refuses_a_locally_divergent_recovery_workflow(self):
        workflow = self.root / ".agents/WORKFLOW.md"
        legacy = b"# Older managed recovery\n"
        system_path = self.root / ".agents/SYSTEM.json"
        system = json.loads(system_path.read_text())
        system["managed_guidance"][".agents/WORKFLOW.md"] = "sha256:" + hashlib.sha256(legacy).hexdigest()
        write_json(system_path, system)
        workflow.write_bytes(legacy + b"\nOwner changed this guidance.\n")
        before = file_hashes(self.root)
        result = run_cli("upgrade", "--target", str(self.root))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("differs locally", result.stderr)
        self.assertEqual(file_hashes(self.root), before)

    def test_missing_setup_and_unsafe_record_paths_fail_without_writes(self):
        empty = self.parent / "empty"
        empty.mkdir()
        result = run_cli("brief", "--target", str(empty), "--json")
        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)["records_available"])
        self.assertEqual(list(empty.iterdir()), [])
        original = self.requests.read_bytes()
        self.requests.unlink()
        outside = self.parent / "requests.json"
        outside.write_bytes(original)
        self.requests.symlink_to(outside)
        result, report = self.brief()
        self.assertEqual(result.returncode, 1)
        self.assertTrue(report["errors"])
        self.assertEqual(outside.read_bytes(), original)

    def test_concurrent_input_change_cannot_produce_a_successful_summary(self):
        self.checkpoint()
        original = PROJECT_OS.checkpoint_report

        def changing_checkpoint(root):
            result = original(root)
            self.requests.write_bytes(self.requests.read_bytes() + b"\n")
            return result

        with mock.patch.object(PROJECT_OS, "checkpoint_report", side_effect=changing_checkpoint):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = PROJECT_OS.project_brief(self.root, True)
        report = json.loads(output.getvalue())
        self.assertEqual(result, 1)
        self.assertFalse(report["records_available"])
        self.assertTrue(any("changed" in error.lower() for error in report["errors"]))

    def test_system_owner_change_after_structural_check_returns_failure_json(self):
        self.checkpoint()
        system_path = self.root / ".agents/SYSTEM.json"
        original_system = system_path.read_bytes()
        before = file_hashes(self.root)
        original_check = PROJECT_OS.check_project
        for owner in ("state", "context"):
            with self.subTest(owner=owner):
                changed = [False]

                def changing_check(root):
                    result = original_check(root)
                    if not changed[0]:
                        system = json.loads(system_path.read_text())
                        system["paths"].pop(owner)
                        write_json(system_path, system)
                        changed[0] = True
                    return result

                output = io.StringIO()
                try:
                    with mock.patch.object(PROJECT_OS, "check_project", side_effect=changing_check):
                        with contextlib.redirect_stdout(output):
                            result = PROJECT_OS.project_brief(self.root, True)
                finally:
                    system_path.write_bytes(original_system)
                report = json.loads(output.getvalue())
                self.assertEqual(result, 1)
                self.assertEqual(report["integrity"], "FAIL")
                self.assertFalse(report["records_available"])
                self.assertTrue(any("changed" in error.lower() for error in report["errors"]))
                self.assertEqual(file_hashes(self.root), before)

    def test_restored_invalid_system_is_validated_before_its_owners_are_consumed(self):
        self.checkpoint()
        system_path = self.root / ".agents/SYSTEM.json"
        valid_system = system_path.read_bytes()
        before = file_hashes(self.root)
        original_check = PROJECT_OS.check_project
        for owner in ("state", "context"):
            with self.subTest(owner=owner):
                system = json.loads(valid_system)
                system["paths"].pop(owner)
                invalid_system = (json.dumps(system, indent=2) + "\n").encode()
                system_path.write_bytes(invalid_system)
                checked = [False]

                def changing_check(root):
                    if checked[0]:
                        return original_check(root)
                    checked[0] = True
                    system_path.write_bytes(valid_system)
                    try:
                        return original_check(root)
                    finally:
                        system_path.write_bytes(invalid_system)

                output = io.StringIO()
                try:
                    with mock.patch.object(PROJECT_OS, "check_project", side_effect=changing_check):
                        with contextlib.redirect_stdout(output):
                            result = PROJECT_OS.project_brief(self.root, True)
                finally:
                    system_path.write_bytes(valid_system)
                report = json.loads(output.getvalue())
                self.assertEqual(result, 1)
                self.assertEqual(report["integrity"], "FAIL")
                self.assertFalse(report["records_available"])
                self.assertTrue(any(owner in error for error in report["errors"]))
                self.assertEqual(file_hashes(self.root), before)

    def test_program_authority_is_routed_and_guarded_even_with_a_stale_checkpoint(self):
        definition = write_program_definition(self.root)
        started = run_cli("program", "start", "--target", str(self.root), "--definition", str(definition))
        self.assertEqual(started.returncode, 0, started.stdout + started.stderr)
        self.checkpoint()
        program_path = self.root / ".agents/PROGRAM.md"
        program_bytes = program_path.read_bytes()
        before = file_hashes(self.root)
        result, report = self.brief()
        self.assertEqual(result.returncode, 0, report)
        self.assertEqual(report["mode"], "program")
        self.assertEqual(report["record_paths"]["program"], ".agents/PROGRAM.md")
        self.assertIn(".agents/PROGRAM.md", report["read_next"])
        self.assertEqual(report["checkpoint"]["status"], "CURRENT")
        self.assertEqual(file_hashes(self.root), before)

        state_path = self.root / ".agents/STATE.md"
        state_path.write_text(state_path.read_text().split("<!-- project-os-checkpoint:")[0].rstrip() + "\n")
        stale_before = file_hashes(self.root)
        result, report = self.brief()
        self.assertEqual(result.returncode, 1, report)
        self.assertTrue(report["records_available"])
        self.assertEqual(report["mode"], "program")
        self.assertEqual(report["checkpoint"]["status"], "STALE")
        self.assertIn(".agents/PROGRAM.md", report["read_next"])
        self.assertEqual(file_hashes(self.root), stale_before)

        original_checkpoint = PROJECT_OS.checkpoint_report

        def changing_checkpoint(root):
            report = original_checkpoint(root)
            program_path.write_bytes(program_bytes + b"\nConcurrent authority change.\n")
            return report

        output = io.StringIO()
        try:
            with mock.patch.object(PROJECT_OS, "checkpoint_report", side_effect=changing_checkpoint):
                with contextlib.redirect_stdout(output):
                    result = PROJECT_OS.project_brief(self.root, True)
        finally:
            program_path.write_bytes(program_bytes)
        report = json.loads(output.getvalue())
        self.assertEqual(result, 1)
        self.assertFalse(report["records_available"])
        self.assertTrue(any("changed" in error.lower() for error in report["errors"]))
        self.assertEqual(file_hashes(self.root), stale_before)


if __name__ == "__main__":
    unittest.main()
