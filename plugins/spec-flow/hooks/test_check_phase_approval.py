"""Behavior tests for the shared-engine PreToolUse authorization boundary."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
TEST_ROOT = PLUGIN_ROOT / "tests"
for import_root in (PLUGIN_ROOT, TEST_ROOT):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

from harness.runtime.engine import Engine, EngineError
from helpers import FakeAdapter, approve_release, make_project, start_run

HOOK = Path(__file__).with_name("check-phase-approval.py")


class ApprovalHookTest(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.docs = make_project(self.root)
        subprocess.run(["git", "init", "-q", self.root], check=True)
        subprocess.run(["git", "config", "user.name", "Hook Test"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.email", "hook@example.test"], cwd=self.root, check=True)
        subprocess.run(["git", "add", "."], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-qm", "baseline"], cwd=self.root, check=True)

    def event_result(self, event: dict) -> dict:
        result = subprocess.run([sys.executable, "-B", HOOK], input=json.dumps(event), text=True,
                                capture_output=True, check=True, cwd=self.root)
        return json.loads(result.stdout) if result.stdout else {}

    def event(self, tool_name: str, tool_input: dict) -> dict:
        return {"cwd": str(self.root), "tool_name": tool_name, "tool_input": tool_input}

    def test_yaml_sources_still_require_current_registry_approval(self) -> None:
        self.assertTrue(self.docs['constitution'].read_text().startswith('---\n'))
        engine = Engine(self.root, adapter=FakeAdapter())
        engine.dispatch('initialize', {})
        self.assertFalse(engine.dispatch('gate', {'path': '.specs/roadmap.md'})['ready'])
        approve_release(engine, self.docs)
        self.assertTrue(engine.dispatch('gate', {'path': '.specs/release-v1.2.3/tasks.md'})['ready'])
        source = self.docs['constitution']
        source.write_text(source.read_text().replace('Approved source decision.', 'Changed governing decision.'))
        with self.assertRaises((EngineError, ValueError)):
            engine.dispatch('hook-check', {'paths': ['.specs/roadmap.md']})

    def test_malformed_supported_write_is_denied(self) -> None:
        denied = self.event_result(self.event("Write", {"content": "no path"}))
        self.assertEqual(denied["hookSpecificOutput"]["permissionDecision"], "deny")
        patch = self.event_result(self.event("apply_patch", {"command": "*** Begin Patch\n*** Update File:\n*** End Patch"}))
        self.assertEqual(patch["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_unapproved_canonical_artifact_write_is_denied_by_runtime_approval_ledger(self) -> None:
        denied = self.event_result(self.event("Write", {"file_path": ".specs/release-v1.2.3/plan.md", "content": "new plan"}))
        self.assertEqual(denied["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_legacy_release_directory_is_fail_closed_and_requires_migration(self) -> None:
        legacy = self.root / ".specs" / "001-demo"
        legacy.mkdir()
        (legacy / "tasks.md").write_text("# old task list\n", encoding="utf-8")
        denied = self.event_result(self.event("Edit", {"file_path": "src/example.py", "old_string": "", "new_string": "x"}))
        self.assertEqual(denied["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_unmanaged_non_git_directory_is_not_gated(self) -> None:
        unrelated = Path(self.directory.name) / "unmanaged"
        unrelated.mkdir()
        result = subprocess.run([sys.executable, "-B", HOOK], input=json.dumps({
            "cwd": str(unrelated), "tool_name": "Write", "tool_input": {"file_path": "notes.txt", "content": "hello"}}),
            text=True, capture_output=True, check=True)
        self.assertEqual(result.stdout, "")

    def test_adopted_non_git_strategy_authoring_uses_constitution_approval(self) -> None:
        import shutil
        shutil.rmtree(self.root / ".git")
        engine = Engine(self.root, adapter=FakeAdapter())
        engine.dispatch("initialize", {})
        engine.dispatch("approve", {"path": ".specs/constitution.md", "actor": "user",
                                    "statement": "Approve the constitution.", "source": "conversation"})
        event = {"cwd": str(self.root), "tool_name": "Write",
                 "tool_input": {"file_path": ".specs/architecture.md", "content": "Architecture notes."}}
        result = subprocess.run([sys.executable, "-B", HOOK], input=json.dumps(event), text=True,
                                 capture_output=True, check=True)
        self.assertEqual(result.stdout, "")

    def test_edit_alias_can_supply_apply_patch_command(self) -> None:
        event = self.event("Edit", {"command": "*** Begin Patch\n*** Update File: .specs/release-v1.2.3/plan.md\n@@\n-old\n+new\n*** End Patch"})
        denied = self.event_result(event)
        self.assertEqual(denied["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_active_task_scope_is_branch_agnostic_and_denies_out_of_scope(self) -> None:
        subprocess.run(["git", "checkout", "-q", "-b", "maintenance"], cwd=self.root, check=True)
        engine = Engine(self.root, adapter=FakeAdapter())
        engine.dispatch("initialize", {})
        approve_release(engine, self.docs)
        run_id = start_run(engine)
        engine.dispatch("prepare", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        engine.dispatch("bind-agent", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001",
                                        "agent_id": "/root/T-001", "session_id": "fixture-agent", "agent_path": "/root/T-001"})
        self.assertTrue(engine.dispatch("hook-check", {"paths": ["src/example.py"]})["allowed"])
        with self.assertRaises(EngineError) as ctx:
            engine.dispatch("hook-check", {"paths": ["outside.py"]})
        self.assertEqual(ctx.exception.code, "out_of_scope_changes")

    def test_task_cannot_edit_dependency_context_file(self) -> None:
        docs = make_project(self.root, task_items=[
            __import__("helpers").task("T-001", files=["src/base.py"]),
            __import__("helpers").task("T-002", dependencies=["T-001"], files=["src/second.py"]),
        ])
        engine = Engine(self.root, adapter=FakeAdapter())
        engine.dispatch("initialize", {})
        approve_release(engine, docs)
        run_id = start_run(engine)
        engine.dispatch("prepare", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        (self.root / "src/base.py").write_text("base\n", encoding="utf-8")
        engine.dispatch("result", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001", "result": {"summary": "base"}})
        engine.dispatch("verify", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        engine.dispatch("review", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001", "verdict": "pass", "evidence": "Reviewed."})
        engine.dispatch("close", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        engine.dispatch("prepare", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-002"})
        engine.dispatch("bind-agent", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-002",
                                        "agent_id": "/root/T-002", "session_id": "fixture-agent-2", "agent_path": "/root/T-002"})
        with self.assertRaises(EngineError) as ctx:
            engine.dispatch("hook-check", {"paths": ["src/base.py"]})
        self.assertEqual(ctx.exception.code, "out_of_scope_changes")

    def test_runtime_registry_paths_cannot_be_patched(self) -> None:
        engine = Engine(self.root, adapter=FakeAdapter())
        engine.dispatch("initialize", {})
        with self.assertRaises(EngineError) as ctx:
            engine.dispatch("hook-check", {"paths": [".spec-flow/runs/forged/events.jsonl"]})
        self.assertEqual(ctx.exception.code, "protected_runtime_state")


if __name__ == "__main__":
    unittest.main()
