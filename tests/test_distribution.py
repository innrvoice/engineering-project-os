"""Verify reviewer inputs and runtime behavior from the exact distributable ZIP."""

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from test_project_os import ROOT, file_hashes

SPEC = importlib.util.spec_from_file_location("package_plugin", ROOT / "scripts/package_plugin.py")
PACKAGE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PACKAGE)


class DistributionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.base = Path(cls.temporary.name).resolve()
        cls.archive = cls.base / "plugin.zip"
        cls.manifest = PACKAGE.build_zip(ROOT, cls.archive)
        cls.extracted = cls.base / "extracted"
        with zipfile.ZipFile(cls.archive) as archive:
            archive.extractall(cls.extracted)
        cls.skill = cls.extracted / "skills/project-os"
        cls.cases = json.loads((cls.skill / "evals/submission.json").read_text())["cases"]

    def command(self, script, *arguments, cwd=None):
        return subprocess.run([sys.executable, "-B", str(script), *arguments], cwd=cwd,
                              capture_output=True, text=True, check=False)

    def test_reproducible_complete_zip_excludes_repository_control_plane(self):
        second = self.base / "second.zip"
        self.assertEqual(PACKAGE.build_zip(ROOT, second), self.manifest)
        with zipfile.ZipFile(self.archive) as archive:
            names = archive.namelist()
            self.assertFalse(any(name.startswith((".agents/", ".git/", "tests/")) for name in names))
            self.assertIn("skills/project-os/assets/templates/core/.agents/STATE.md", names)
            self.assertIn("docs/USAGE.md", names)
            self.assertIn("docs/PACKAGING.md", names)
            self.assertIn("skills/project-os/evals/prepare_fixture.py", names)
            for name in names:
                self.assertEqual(archive.read(name), (ROOT / name).read_bytes(), name)
        with self.assertRaises(FileExistsError):
            PACKAGE.build_zip(ROOT, second)

    def test_packaged_document_link_check_detects_missing_guide(self):
        broken = self.base / "missing-guide.zip"
        with zipfile.ZipFile(self.archive) as source, zipfile.ZipFile(broken, "w") as output:
            for member in source.infolist():
                if member.filename != "docs/USAGE.md":
                    output.writestr(member, source.read(member.filename))
        with self.assertRaisesRegex(ValueError, "Broken packaged document link"):
            PACKAGE.validate_zip(broken)

    def test_markdown_layout_rejects_wrapped_prose_and_list_items(self):
        self.assertEqual(PACKAGE.markdown_layout_errors("README.md", "One paragraph on one line.\n"), [])
        self.assertEqual(PACKAGE.markdown_layout_errors("README.md", "One paragraph\nwrapped here.\n"), ["README.md:2"])
        self.assertEqual(PACKAGE.markdown_layout_errors("README.md", "- One list item\n  wrapped here.\n"), ["README.md:2"])
        self.assertEqual(PACKAGE.markdown_layout_errors("README.md", "~~~text\nwrapped\ncontent\n~~~\n"), [])

    def test_packaged_markdown_avoids_oxford_commas(self):
        with zipfile.ZipFile(self.archive) as archive:
            for name in archive.namelist():
                if name.endswith(".md"):
                    self.assertNotIn(", and ", archive.read(name).decode("utf-8"), name)

    def test_each_submission_fixture_is_self_contained_and_matches_runtime(self):
        helper = self.skill / "scripts/project_os.py"
        setup = self.skill / "evals/prepare_fixture.py"
        for case in self.cases:
            with self.subTest(case=case["name"]):
                target = self.base / case["name"]
                prepared = self.command(setup, "--case", case["name"], "--target", str(target))
                self.assertEqual(prepared.returncode, 0, prepared.stdout + prepared.stderr)
                before = file_hashes(target)
                refused = self.command(setup, "--case", case["name"], "--target", str(target))
                self.assertEqual(refused.returncode, 2)
                self.assertEqual(file_hashes(target), before)
                if case["name"].startswith("bootstrap-"):
                    self.assertFalse((target / ".agents").exists())
                    preview = self.command(helper, "init", "--target", str(target), "--dry-run")
                    self.assertEqual(preview.returncode, 0, preview.stderr)
                    self.assertEqual(file_hashes(target), before)
                    applied = self.command(helper, "init", "--target", str(target))
                    self.assertEqual(applied.returncode, 0, applied.stderr)
                    for name, digest in before.items():
                        self.assertEqual(file_hashes(target)[name], digest)
                    system = json.loads((target / ".agents/SYSTEM.json").read_text())
                    self.assertEqual(system["mode"], "standard")
                    self.assertFalse((target / ".agents/PROGRAM.md").exists())
                    self.assertFalse((target / ".agents/history").exists())
                    if "expo" in case["name"]:
                        self.assertIn("mobile", system["packs"])
                        self.assertNotIn("web", system["packs"])
                        self.assertEqual(system["overlays"], ["react-native-expo"])
                if (target / ".agents/SYSTEM.json").exists():
                    checked = self.command(helper, "check", "--target", str(target))
                    self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
                if case["name"] == "upgrade-current-repository-is-idempotent":
                    preview = self.command(helper, "upgrade", "--target", str(target), "--dry-run")
                    self.assertEqual(preview.returncode, 0, preview.stdout + preview.stderr)
                    self.assertFalse(any(line.startswith(("create:", "update:", "delete:")) for line in preview.stdout.splitlines()))
                    applied = self.command(helper, "upgrade", "--target", str(target))
                    self.assertEqual(applied.returncode, 0, applied.stdout + applied.stderr)
                    self.assertEqual(file_hashes(target), before)
                elif case["name"] == "unrelated-code-request-does-not-create-state":
                    failed = subprocess.run([sys.executable, "-B", "-m", "unittest", "-v", "test_handler.py"], cwd=target, capture_output=True, text=True)
                    self.assertEqual(failed.returncode, 1)
                    self.assertIn("NoneType", failed.stderr)
                    self.assertEqual(file_hashes(target), before)
                elif not case["name"].startswith("bootstrap-"):
                    self.assertEqual(file_hashes(target), before)

    def test_checker_accepts_documented_block_and_resume_registry_transitions(self):
        target = self.base / "plan-transition"
        prepared = self.command(self.skill / "evals/prepare_fixture.py", "--case",
                                "resume-blocked-plan-after-condition-clears", "--target", str(target))
        self.assertEqual(prepared.returncode, 0, prepared.stderr)
        index = target / ".agents/plans/index.json"
        value = json.loads(index.read_text())
        self.assertEqual(value["plans"][0]["status"], "blocked")
        self.assertTrue((target / "sample.txt").is_file())
        value["plans"][0]["status"] = "active"
        value["execution_state"] = "running"
        value["active_plan"] = "001"
        index.write_text(json.dumps(value, indent=2) + "\n")
        (target / ".agents/STATE.md").write_text("# Checkpoint\n\nPlan 001 is active. Next: validate sample.txt contents.\n")
        checked = self.command(self.skill / "scripts/project_os.py", "check", "--target", str(target))
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
        self.assertIn("- [ ]", (target / ".agents/plans/001-review.md").read_text())
