"""Exercise the repository's publication boundary using a real temporary Git index."""

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


class PublicTreeTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.run_command("git", "init", "--quiet", str(self.root))
        shutil.copyfile(ROOT / ".gitignore", self.root / ".gitignore")
        (self.root / "scripts").mkdir()
        shutil.copyfile(ROOT / "scripts/check_public_tree.py", self.root / "scripts/check_public_tree.py")

    def run_command(self, *command):
        return subprocess.run(command, cwd=self.root, capture_output=True, text=True, check=True)

    def write(self, name):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("synthetic fixture\n")

    def check(self, *args):
        return subprocess.run([sys.executable, "-B", str(self.root / "scripts/check_public_tree.py"),
                               *args], capture_output=True, text=True)

    def test_ignore_keeps_records_local_and_product_files_public(self):
        private = [".agents/STATE.md", ".agents/plans/001.md", ".agents/future/record.json",
                   ".agents/plugins/private-notes.md"]
        public = [".agents/plugins/marketplace.json",
                  "skills/project-os/assets/templates/core/.agents/STATE.md",
                  "tests/fixtures/sample/.agents/SYSTEM.json"]
        for name in private + public:
            self.write(name)
        self.run_command("git", "add", ".")
        tracked = self.run_command("git", "ls-files").stdout.splitlines()
        self.assertTrue(all(name not in tracked for name in private))
        self.assertTrue(all(name in tracked for name in public))
        self.assertEqual(self.check().returncode, 0)
        self.assertTrue(all((self.root / name).exists() for name in private))

    def test_gate_rejects_force_added_private_record(self):
        self.write(".agents/STATE.md")
        self.run_command("git", "add", "--force", ".agents/STATE.md")
        result = self.check()
        self.assertEqual(result.returncode, 1)
        self.assertIn(".agents/STATE.md", result.stdout)

    def test_export_gate_preserves_templates_and_rejects_private_records(self):
        self.write(".agents/plugins/marketplace.json")
        self.write("skills/project-os/assets/templates/core/.agents/STATE.md")
        self.assertEqual(self.check("--tree", str(self.root)).returncode, 0)
        self.write(".agents/evidence/internal.md")
        self.assertEqual(self.check("--tree", str(self.root)).returncode, 1)


if __name__ == "__main__":
    unittest.main()
