"""Existing connected repositories receive bounded-work guidance without losing instructions."""

import contextlib
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from test_project_os import PROJECT_OS as P, copy_fixture, file_hashes, run_cli


OWNER_TEXT = (
    "# Existing owner instructions\n\nKeep exact owner text and trailing spaces.  \n"
    "Read `.agents/CONTEXT.md` and `.agents/STATE.md`.\n\n"
    "Read `.agents/WORKFLOW.md` before non-trivial work and after context compaction.\n"
)


class WritebackRoutingTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.parent = Path(self.tmp.name).resolve()
        self.root = self.parent / "project"
        self.root.mkdir()
        result = run_cli("init", "--target", str(self.root), "--packs", "none")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def old_schema5_project(self):
        (self.root / "AGENTS.md").write_text(OWNER_TEXT)
        workflow = self.root / ".agents/WORKFLOW.md"
        workflow.write_text("# Previous managed workflow\n\nPrevious release guidance.\n")
        system_path = self.root / ".agents/SYSTEM.json"
        system = json.loads(system_path.read_text())
        system["project_os_version"] = "2.2.2"
        system["managed_guidance"][".agents/WORKFLOW.md"] = "sha256:" + hashlib.sha256(workflow.read_bytes()).hexdigest()
        system_path.write_text(json.dumps(system, indent=2) + "\n")

    def test_schema5_upgrade_previews_append_preserves_owner_bytes_and_is_idempotent(self):
        self.old_schema5_project()
        before = file_hashes(self.root)
        preview = run_cli("upgrade", "--target", str(self.root), "--dry-run")
        self.assertEqual(preview.returncode, 0, preview.stdout + preview.stderr)
        self.assertIn("preview: AGENTS.md", preview.stdout)
        self.assertIn(P.WORKFLOW_WRITEBACK_ROUTE, preview.stdout)
        self.assertEqual(file_hashes(self.root), before)
        applied = run_cli("upgrade", "--target", str(self.root))
        self.assertEqual(applied.returncode, 0, applied.stdout + applied.stderr)
        agents = (self.root / "AGENTS.md").read_text()
        self.assertTrue(agents.startswith(OWNER_TEXT))
        self.assertEqual(agents.count(P.WORKFLOW_WRITEBACK_ROUTE), 1)
        for path, digest in before.items():
            if path not in {"AGENTS.md", ".agents/SYSTEM.json", ".agents/WORKFLOW.md"}:
                self.assertEqual(file_hashes(self.root)[path], digest, path)
        current = file_hashes(self.root)
        repeated = run_cli("upgrade", "--target", str(self.root))
        self.assertEqual(repeated.returncode, 0, repeated.stdout + repeated.stderr)
        self.assertEqual(file_hashes(self.root), current)

    def test_new_template_route_is_not_duplicated_on_upgrade(self):
        agents = (self.root / "AGENTS.md").read_bytes()
        self.assertIn(b"Plan-free does not mean record-free.", agents)
        upgraded = run_cli("upgrade", "--target", str(self.root))
        self.assertEqual(upgraded.returncode, 0, upgraded.stdout + upgraded.stderr)
        self.assertEqual((self.root / "AGENTS.md").read_bytes(), agents)
        self.assertNotIn(P.WORKFLOW_WRITEBACK_ROUTE.encode(), agents)

    def test_bootstrap_with_existing_instructions_previews_and_appends_same_route(self):
        target = self.parent / "existing-instructions"
        target.mkdir()
        original = OWNER_TEXT.replace("Read `.agents/WORKFLOW.md` before non-trivial work and after context compaction.\n", "")
        (target / "AGENTS.md").write_text(original)
        before = file_hashes(target)
        preview = run_cli("init", "--target", str(target), "--packs", "none", "--allow-existing-agents", "--dry-run")
        self.assertEqual(preview.returncode, 0, preview.stdout + preview.stderr)
        self.assertIn("preview: AGENTS.md", preview.stdout)
        self.assertIn(P.WORKFLOW_WRITEBACK_ROUTE, preview.stdout)
        self.assertEqual(file_hashes(target), before)
        applied = run_cli("init", "--target", str(target), "--packs", "none", "--allow-existing-agents")
        self.assertEqual(applied.returncode, 0, applied.stdout + applied.stderr)
        text = (target / "AGENTS.md").read_text()
        self.assertTrue(text.startswith(original))
        self.assertEqual(text.count(P.WORKFLOW_WRITEBACK_ROUTE), 1)

    def test_adoption_previews_and_appends_same_route_preserving_existing_data(self):
        target = copy_fixture("mature-mobile", self.parent)
        agents_path = target / "AGENTS.md"
        original = agents_path.read_bytes()
        preview = P.discover_adoption(target)
        self.assertTrue(preview["safe_to_adopt"], preview["errors"])
        self.assertIn(P.WORKFLOW_WRITEBACK_ROUTE, preview["proposed_record_changes"]["AGENTS.md"])
        self.assertEqual(agents_path.read_bytes(), original)
        result = run_cli("adopt", "--target", str(target))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(agents_path.read_bytes().startswith(original))
        self.assertEqual(agents_path.read_text().count(P.WORKFLOW_WRITEBACK_ROUTE), 1)

    def test_local_workflow_conflict_aborts_before_appending_route(self):
        self.old_schema5_project()
        path = self.root / ".agents/WORKFLOW.md"
        path.write_text(path.read_text() + "\nLocal owner workflow change.\n")
        before = file_hashes(self.root)
        result = run_cli("upgrade", "--target", str(self.root))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("differs locally", result.stderr)
        self.assertEqual(file_hashes(self.root), before)

    def test_concurrent_agents_edit_is_preserved_and_other_changes_roll_back(self):
        self.old_schema5_project()
        path = self.root / "AGENTS.md"
        before = file_hashes(self.root)
        original_preview = P.print_transaction_preview

        def race(*args, **kwargs):
            original_preview(*args, **kwargs)
            path.write_text(OWNER_TEXT + "\nConcurrent owner instruction.\n")

        with contextlib.redirect_stdout(io.StringIO()), mock.patch.object(P, "print_transaction_preview", side_effect=race):
            with self.assertRaisesRegex(P.ProjectOSError, "changed"):
                P.upgrade_project(self.root, None, None, None, None, False)
        self.assertEqual(path.read_text(), OWNER_TEXT + "\nConcurrent owner instruction.\n")
        after = file_hashes(self.root)
        before.pop("AGENTS.md")
        after.pop("AGENTS.md")
        self.assertEqual(after, before)


if __name__ == "__main__":
    unittest.main()
