"""Portable CLI and completion-wrapper behavior tests."""

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from helpers import make_project

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
CLI = PLUGIN_ROOT / "scripts" / "spec-flow.py"
CHECK_COMPLETE = PLUGIN_ROOT / "scripts" / "check-complete.sh"


class CompletionCliTests(unittest.TestCase):
    def test_cli_configures_profiles_without_launching_agents_or_creating_runs(self):
        with tempfile.TemporaryDirectory(prefix="spec flow profiles ") as temp:
            root = Path(temp)
            input_path = root / 'input.json'
            profiles = {'orchestrator': {'id': 'custom-owner', 'effort': 'low'},
                        'implementer': {'id': 'custom-worker', 'effort': 'medium'},
                        'reviewer': {'id': 'custom-reviewer', 'effort': 'high'}}
            for operation, payload in [('initialize', {}), ('configure-profiles', {'profiles': profiles})]:
                input_path.write_text(json.dumps(payload))
                result = subprocess.run(['python3', '-B', CLI, '--root', root, operation, '--input', input_path], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)['applies_to'], 'new_runs_only')
            config = json.loads((root / '.spec-flow/config.json').read_text())
            self.assertEqual(config['profiles'], profiles)
            self.assertEqual(config['retry_limit'], 3)
            self.assertEqual(list((root / '.spec-flow/runs').iterdir()), [])

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
