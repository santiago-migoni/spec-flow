"""Portable CLI behavior tests."""

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
CLI = PLUGIN_ROOT / "scripts" / "spec-flow.py"


class CliTests(unittest.TestCase):
    def run_cli(self, root, operation, payload):
        input_path = root / "input.json"
        input_path.write_text(json.dumps(payload))
        return subprocess.run(["python3", "-B", CLI, "--root", str(root), operation, "--input", str(input_path)],
                              capture_output=True, text=True)

    def test_cli_initializes_minimal_config(self):
        with tempfile.TemporaryDirectory(prefix="spec flow cli ") as temp:
            root = Path(temp)
            result = self.run_cli(root, "initialize", {})
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads((root / ".spec-flow" / "config.json").read_text()), {"schema_version": 1})

    def test_cli_rejects_retired_operations(self):
        with tempfile.TemporaryDirectory(prefix="spec flow cli ") as temp:
            result = subprocess.run(["python3", CLI, "--root", temp, "start", "--input", "/dev/null"],
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("invalid choice", result.stderr)

    def test_cli_exposes_document_operations(self):
        result = subprocess.run(["python3", CLI, "--help"], capture_output=True, text=True, check=True)
        for operation in ("initialize", "digest", "validate", "approve", "gate", "hook-check", "migrate-preview"):
            self.assertIn(operation, result.stdout)


if __name__ == "__main__":
    unittest.main()
