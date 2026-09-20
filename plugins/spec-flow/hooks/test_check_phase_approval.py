"""Behavior checks for the supported patch approval hook."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


HOOK = Path(__file__).with_name("check-phase-approval.py")


class ApprovalHookTest(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        subprocess.run(["git", "init", "-q", self.root], check=True)
        subprocess.run(
            ["git", "checkout", "-q", "-b", "001-demo"], cwd=self.root, check=True
        )
        (self.root / ".specs" / "001-demo").mkdir(parents=True)

    def status(self, relative_path: str, value: str) -> None:
        target = self.root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            "| Name | Status |\n| --- | --- |\n| demo | " + value + " |\n",
            encoding="utf-8",
        )

    def decision(self, target: str) -> dict:
        event = {
            "cwd": str(self.root),
            "tool_name": "apply_patch",
            "tool_input": {"command": f"*** Begin Patch\n*** Add File: {target}\n+x\n*** End Patch"},
        }
        result = subprocess.run(
            [sys.executable, "-B", HOOK],
            input=json.dumps(event),
            text=True,
            capture_output=True,
            check=True,
        )
        return json.loads(result.stdout) if result.stdout else {}

    def test_artifact_write_requires_approved_predecessor(self) -> None:
        self.status(".specs/constitution.md", "Draft")
        denied = self.decision(".specs/001-demo/spec.md")
        self.assertEqual(denied["hookSpecificOutput"]["permissionDecision"], "deny")
        self.status(".specs/constitution.md", "Approved")
        self.assertEqual(self.decision(".specs/001-demo/spec.md"), {})

    def test_unknown_status_is_not_approval(self) -> None:
        self.status(".specs/001-demo/spec.md", "Pending")
        denied = self.decision(".specs/001-demo/plan.md")
        self.assertEqual(denied["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_code_write_requires_approved_tasks(self) -> None:
        self.assertEqual(
            self.decision("src/new.py")["hookSpecificOutput"]["permissionDecision"],
            "deny",
        )
        self.status(".specs/001-demo/tasks.md", "Draft")
        self.assertEqual(
            self.decision("src/new.py")["hookSpecificOutput"]["permissionDecision"],
            "deny",
        )
        self.status(".specs/001-demo/tasks.md", "Approved")
        self.assertEqual(self.decision("src/new.py"), {})

    def test_backlog_write_does_not_require_tasks_approval(self) -> None:
        self.assertEqual(self.decision(".specs/backlog.md"), {})

    def test_other_branches_are_not_opted_in(self) -> None:
        subprocess.run(
            ["git", "checkout", "-q", "-b", "maintenance"], cwd=self.root, check=True
        )
        self.assertEqual(self.decision("src/new.py"), {})


if __name__ == "__main__":
    unittest.main()
