"""Recovery retains scope and unfinished work at compatibility boundaries."""

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from test_project_os import file_hashes, run_cli


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


class BriefCompatibilityTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.parent = Path(self.temporary.name).resolve()
        self.root = self.parent / "project"
        self.root.mkdir()
        initialized = run_cli("init", "--target", str(self.root), "--packs", "none")
        self.assertEqual(initialized.returncode, 0, initialized.stdout + initialized.stderr)
        self.index_path = self.root / ".agents/plans/index.json"
        self.contract_path = self.root / ".agents/plans/001-recovery.json"
        self.state_path = self.root / ".agents/STATE.md"

        evidence_path = self.root / ".agents/evidence/local-source.md"
        evidence_path.write_text("Synthetic local source check passed.\n", encoding="utf-8")
        self.excluded_reason = "The accepted synthetic scope excludes the retired transport."
        write_json(self.contract_path, {
            "schema_version": 1, "plan_id": "001", "revision": 1,
            "gates": [
                {"id": "local-source", "condition": "Local source is verified.",
                 "evidence_class": "source", "target": "local", "status": "verified",
                 "evidence": [{"path": ".agents/evidence/local-source.md",
                               "sha256": "sha256:" + hashlib.sha256(evidence_path.read_bytes()).hexdigest(),
                               "checked_on": "2026-11-01", "target": "local", "revision": 1}],
                 "next_action": "", "reason": ""},
                {"id": "retired-transport", "condition": "The retired transport is accepted.",
                 "evidence_class": "manual", "target": "owner", "status": "not_applicable",
                 "evidence": [], "next_action": "", "reason": self.excluded_reason},
                {"id": "owner-review", "condition": "The owner separately reviews the result.",
                 "evidence_class": "manual", "target": "owner", "status": "pending",
                 "evidence": [], "next_action": "Wait for the actual owner decision.", "reason": ""},
            ],
        })
        (self.root / ".agents/plans/001-recovery.md").write_text(
            "# Recovery fixture\n\nLocal proof does not authorize owner acceptance.\n", encoding="utf-8")
        index = json.loads(self.index_path.read_text())
        index.update(execution_state="running", active_plan="001", next_id=2)
        index["plans"] = [{"id": "001", "status": "active", "path": ".agents/plans/001-recovery.md",
                           "contract_path": ".agents/plans/001-recovery.json",
                           "outcome": "Preserve separate owner acceptance during recovery."}]
        write_json(self.index_path, index)
        self.request = {
            "id": "R-001", "recorded_on": "2026-11-01", "source_text": "Keep owner acceptance separate.",
            "interpretation": "Local proof does not grant the owner decision.",
            "origin_plan": "001", "target_plan": "001", "relation": "same_outcome", "status": "integrated",
            "gate_ids": ["owner-review"], "decision": "Await the independent owner decision.",
            "owner_note": {"preserve": True},
        }
        write_json(self.root / ".agents/requests.json", {
            "schema_version": 1, "next_id": 2, "requests": [self.request],
        })

    def checkpoint(self, active):
        draft = self.parent / "checkpoint.md"
        draft.write_text(
            "# Current checkpoint\n\nUpdated: 2026-11-01.\n"
            + ("Execution state: running.\nActive plan: 001.\n" if active else
               "Execution state: idle.\nActive plan: none.\n")
            + "Outcome: Preserve local scope and pending owner acceptance.\n"
              "Verified: Local source proof is retained in the contract.\n"
              "Remaining: The independent owner decision remains pending.\n"
              "Next action: Wait for owner acceptance before closure.\n", encoding="utf-8")
        result = run_cli("checkpoint", "--target", str(self.root), "--draft", str(draft))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def brief(self):
        result = run_cli("brief", "--target", str(self.root), "--json")
        self.assertEqual(result.stderr, "")
        return result, json.loads(result.stdout)

    def test_not_applicable_counts_and_blocked_idle_recovery_preserve_scope(self):
        self.checkpoint(active=True)
        before = file_hashes(self.root)
        result, report = self.brief()
        self.assertEqual(result.returncode, 0, report)
        self.assertEqual(report["active_plan"]["gate_counts"],
                         {"pending": 1, "verified": 1, "not_applicable": 1})
        self.assertEqual([gate["id"] for gate in report["active_plan"]["pending_gates"]], ["owner-review"])
        self.assertEqual(report["active_plan"]["readiness"], "NOT_READY")
        self.assertIn(".agents/plans/001-recovery.json", report["read_next"])
        self.assertEqual(json.loads(self.contract_path.read_text())["gates"][1]["reason"], self.excluded_reason)
        self.assertNotIn(self.excluded_reason, json.dumps(report))
        self.assertEqual(file_hashes(self.root), before)

        index = json.loads(self.index_path.read_text())
        index.update(execution_state="idle", active_plan=None)
        index["plans"][0]["status"] = "blocked"
        write_json(self.index_path, index)
        self.checkpoint(active=False)
        before = file_hashes(self.root)
        result, report = self.brief()
        self.assertEqual(result.returncode, 0, report)
        self.assertEqual(report["integrity"], "PASS")
        self.assertEqual(report["checkpoint"]["status"], "CURRENT")
        self.assertEqual(report["execution_state"], "idle")
        self.assertIsNone(report["active_plan"])
        self.assertEqual([(plan["id"], plan["status"]) for plan in report["other_plans"]], [("001", "blocked")])
        self.assertEqual(report["unresolved_requests"], [self.request])
        self.assertNotIn("readiness", report)
        self.assertEqual(file_hashes(self.root), before)

    def test_missing_receipt_fails_without_hiding_valid_pending_work(self):
        self.checkpoint(active=True)
        # Model an incomplete returned file, rather than synthesizing a new receipt.
        body = self.state_path.read_text().split("<!-- project-os-checkpoint:")[0].rstrip() + "\n"
        self.state_path.write_text(body, encoding="utf-8")
        before = file_hashes(self.root)
        result, report = self.brief()
        self.assertEqual(result.returncode, 1, report)
        self.assertEqual(report["integrity"], "FAIL")
        self.assertEqual(report["structure"], "PASS")
        self.assertTrue(report["records_available"])
        self.assertEqual(report["checkpoint"]["status"], "STALE")
        self.assertTrue(any("receipt" in error.lower() for error in report["checkpoint"]["errors"]))
        self.assertEqual(report["active_plan"]["readiness"], "NOT_READY")
        self.assertEqual([gate["id"] for gate in report["active_plan"]["pending_gates"]], ["owner-review"])
        self.assertEqual(report["unresolved_requests"], [self.request])
        self.assertEqual(file_hashes(self.root), before)


if __name__ == "__main__":
    unittest.main()
