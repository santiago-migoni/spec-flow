"""Portable CLI and completion-wrapper behavior tests."""

import subprocess
import tempfile
import unittest
from pathlib import Path

from helpers import make_project

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
CLI = PLUGIN_ROOT / "scripts" / "spec-flow.py"
CHECK_COMPLETE = PLUGIN_ROOT / "scripts" / "check-complete.sh"


class CompletionCliTests(unittest.TestCase):
    def test_check_complete_uses_read_only_runtime_and_supports_spaces(self):
        with tempfile.TemporaryDirectory(prefix="spec flow ") as temp:
            root = Path(temp) / "project with spaces"
            root.mkdir()
            docs = make_project(root)
            result = subprocess.run(["/bin/sh", CHECK_COMPLETE, docs["tasks"]], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertIn('"complete": false', result.stderr)
            self.assertFalse((root / ".spec-flow").exists())

    def test_check_complete_invalid_path_returns_two(self):
        result = subprocess.run(["/bin/sh", CHECK_COMPLETE], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)

    def test_cli_exposes_e6_operations(self):
        for operation in ("phase-ready", "review-phase", "commit-phase", "refresh-evidence", "release-review", "complete", "hook-check"):
            result = subprocess.run(["python3", CLI, "--help"], capture_output=True, text=True, check=True)
            self.assertIn(operation, result.stdout)


if __name__ == "__main__":
    unittest.main()
