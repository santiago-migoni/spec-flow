import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from harness.runtime.engine import Engine, EngineError
from harness.runtime.contracts import ContractError, document_digest
from helpers import approve_release, make_project, start_run

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
CLI = PLUGIN_ROOT / "scripts" / "spec-flow.py"


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.docs = make_project(self.root)
        self.engine = Engine(self.root)

    def tearDown(self):
        self.temp.cleanup()

    def initialize_approve_start(self):
        self.engine.dispatch("initialize", {})
        approve_release(self.engine, self.docs)
        return start_run(self.engine)

    def test_initialize_writes_fixed_explicit_model_profiles(self):
        result = self.engine.dispatch("initialize", {})
        config = json.loads((self.root / ".spec-flow" / "config.json").read_text())
        self.assertEqual(result["status"], "initialized")
        self.assertEqual(config["schema_version"], 1)
        self.assertEqual(config["profiles"]["orchestrator"], {"id": "gpt-6-sol", "effort": "high"})
        self.assertEqual(config["profiles"]["implementer"], {"id": "gpt-6-luna", "effort": "high"})
        self.assertEqual(config["profiles"]["reviewer"], {"id": "gpt-6-sol", "effort": "high"})

    def test_initialize_rejects_legacy_feature_directories(self):
        (self.root / ".specs" / "001-old-feature").mkdir()
        with self.assertRaises(EngineError) as ctx:
            self.engine.dispatch("initialize", {})
        self.assertEqual(ctx.exception.code, "migration_required")

    def test_status_before_initialize_is_read_only_and_diagnostic(self):
        result = self.engine.dispatch("status", {})
        self.assertEqual(result["status"], "uninitialized")
        self.assertFalse((self.root / ".spec-flow").exists())

    def test_phase_gate_alias_returns_uninitialized_diagnostic(self):
        result = self.engine.dispatch("gate", {"phase": "specify"})
        self.assertFalse(result["ready"])
        self.assertEqual(result["reason"], "uninitialized")
        self.assertFalse((self.root / ".spec-flow").exists())

    def test_approval_requires_approved_dependencies_and_gate_reports_them(self):
        self.engine.dispatch("initialize", {})
        with self.assertRaises(EngineError) as ctx:
            self.engine.dispatch("approve", {"path": ".specs/roadmap.md", "actor": "user", "statement": "Approve", "source": "chat"})
        self.assertEqual(ctx.exception.code, "dependency_not_approved")
        gate = self.engine.dispatch("gate", {"path": ".specs/roadmap.md"})
        self.assertFalse(gate["ready"])
        self.assertIn(".specs/constitution.md", gate["missing_approvals"])

    def test_start_requires_all_current_release_approvals(self):
        self.engine.dispatch("initialize", {})
        with self.assertRaises(EngineError) as ctx:
            start_run(self.engine)
        self.assertEqual(ctx.exception.code, "approval_required")

    def test_prepare_pins_packet_and_wrong_owner_is_rejected(self):
        run_id = self.initialize_approve_start()
        result = self.engine.dispatch("prepare", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        packet = json.loads(Path(result["packet_path"]).read_text())
        self.assertEqual(packet["task"]["id"], "T-001")
        self.assertIn("sources", packet)
        with self.assertRaises(EngineError) as ctx:
            self.engine.dispatch("result", {"run_id": run_id, "owner": "wrong", "task_id": "T-001", "result": {"summary": "done"}})
        self.assertEqual(ctx.exception.code, "wrong_owner")

    def test_prepare_rejects_parallel_active_task_and_result_does_not_close(self):
        run_id = self.initialize_approve_start()
        self.engine.dispatch("prepare", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        with self.assertRaises(EngineError):
            self.engine.dispatch("prepare", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        self.engine.dispatch("result", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001", "result": {"summary": "implemented"}})
        status = self.engine.dispatch("status", {"run_id": run_id})
        self.assertNotEqual(status["tasks"]["T-001"]["status"], "completed")

    def test_verify_runs_real_argv_and_requires_nonempty_output(self):
        run_id = self.initialize_approve_start()
        self.engine.dispatch("prepare", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        self.engine.dispatch("result", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001", "result": {"summary": "implemented"}})
        result = self.engine.dispatch("verify", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        self.assertEqual(result["steps"][0]["exit_code"], 0)
        self.assertIn("verification passed", result["steps"][0]["output"])

    def test_verify_rejects_empty_and_zero_test_results(self):
        for command in (["python3", "-c", "pass"], ["python3", "-c", "print('Ran 0 tests')"]):
            with self.subTest(command=command), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                docs = make_project(root, command=command)
                engine = Engine(root)
                engine.dispatch("initialize", {})
                approve_release(engine, docs)
                run_id = start_run(engine)
                engine.dispatch("prepare", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
                engine.dispatch("result", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001", "result": {"summary": "implemented"}})
                with self.assertRaises(EngineError):
                    engine.dispatch("verify", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})

    def test_verify_requires_inspection_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            docs = make_project(root, inspection="Check the report heading.")
            engine = Engine(root)
            engine.dispatch("initialize", {})
            approve_release(engine, docs)
            run_id = start_run(engine)
            engine.dispatch("prepare", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
            engine.dispatch("result", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001", "result": {"summary": "implemented"}})
            with self.assertRaises(EngineError):
                engine.dispatch("verify", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
            result = engine.dispatch("verify", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001", "inspection_evidence": {"T-001.001": "Report heading is present."}})
            self.assertTrue(result["passed"])

    def test_verify_requires_result_and_result_cannot_replace_verified_result(self):
        run_id = self.initialize_approve_start()
        self.engine.dispatch("prepare", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        with self.assertRaises(EngineError) as ctx:
            self.engine.dispatch("verify", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        self.assertEqual(ctx.exception.code, "result_required")
        self.engine.dispatch("result", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001", "result": {"summary": "implemented"}})
        self.engine.dispatch("verify", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        with self.assertRaises(EngineError) as ctx:
            self.engine.dispatch("result", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001", "result": {"summary": "replacement"}})
        self.assertEqual(ctx.exception.code, "invalid_transition")

    def test_changes_after_verification_are_rechecked_before_review(self):
        run_id = self.initialize_approve_start()
        self.engine.dispatch("prepare", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        self.engine.dispatch("result", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001", "result": {"summary": "implemented"}})
        self.engine.dispatch("verify", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        (self.root / "outside.py").write_text("late change\n")
        with self.assertRaises(EngineError) as ctx:
            self.engine.dispatch("review", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001", "verdict": "pass", "evidence": "Review passed."})
        self.assertEqual(ctx.exception.code, "out_of_scope_changes")

    def test_snapshot_records_directory_symlinks_without_following(self):
        target = self.root / "real-directory"
        target.mkdir()
        link = self.root / "linked-directory"
        link.symlink_to(target, target_is_directory=True)
        snapshot = self.engine._snapshot_code()
        self.assertIn("linked-directory", snapshot)
        self.assertFalse(any(path.startswith("linked-directory/") for path in snapshot))

    def test_out_of_scope_changes_fail_verification(self):
        run_id = self.initialize_approve_start()
        self.engine.dispatch("prepare", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        self.engine.dispatch("result", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001", "result": {"summary": "implemented"}})
        (self.root / "outside.py").write_text("changed\n")
        with self.assertRaises(EngineError) as ctx:
            self.engine.dispatch("verify", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        self.assertEqual(ctx.exception.code, "out_of_scope_changes")

    def test_approval_change_invalidates_run_before_close(self):
        run_id = self.initialize_approve_start()
        self.engine.dispatch("prepare", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        self.engine.dispatch("result", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001", "result": {"summary": "done"}})
        self.engine.dispatch("verify", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        self.engine.dispatch("review", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001", "verdict": "pass", "evidence": "Diff meets the approved task."})
        text = self.docs["spec"].read_text().replace("The user can complete the behavior.", "Changed behavior.")
        self.docs["spec"].write_text(text)
        with self.assertRaises(EngineError) as ctx:
            self.engine.dispatch("close", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        self.assertEqual(ctx.exception.code, "approval_stale")

    def test_close_requires_review_records_checkbox_and_is_idempotent(self):
        run_id = self.initialize_approve_start()
        self.engine.dispatch("prepare", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        self.engine.dispatch("result", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001", "result": {"summary": "done"}})
        self.engine.dispatch("verify", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        with self.assertRaises(EngineError):
            self.engine.dispatch("close", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        self.engine.dispatch("review", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001", "verdict": "pass", "evidence": "Diff meets the approved task."})
        first = self.engine.dispatch("close", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        events_before = len((Path(first["run_dir"]) / "events.jsonl").read_text().splitlines())
        second = self.engine.dispatch("close", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        events_after = len((Path(first["run_dir"]) / "events.jsonl").read_text().splitlines())
        self.assertEqual(first["status"], "completed")
        self.assertTrue(second["already_completed"])
        self.assertEqual(events_before, events_after)
        self.assertIn("[x] T-001", self.docs["tasks"].read_text())
        self.assertEqual(document_digest(self.docs["tasks"]), first["tasks_digest"])

    def test_interrupt_and_resume_preserve_active_attempt_for_reconciliation(self):
        run_id = self.initialize_approve_start()
        self.engine.dispatch("prepare", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        self.engine.dispatch("interrupt", {"run_id": run_id, "owner": "sol-session-1"})
        resumed = self.engine.dispatch("resume", {"run_id": run_id, "owner": "sol-session-1"})
        self.assertTrue(resumed["reconciliation_required"])
        with self.assertRaises(EngineError):
            self.engine.dispatch("prepare", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})

    def test_resume_requires_explicit_reconciliation_before_verification(self):
        run_id = self.initialize_approve_start()
        self.engine.dispatch("prepare", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        self.engine.dispatch("interrupt", {"run_id": run_id, "owner": "sol-session-1"})
        self.engine.dispatch("resume", {"run_id": run_id, "owner": "sol-session-1"})
        with self.assertRaises(EngineError):
            self.engine.dispatch("verify", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        self.engine.dispatch("reconcile", {
            "run_id": run_id, "owner": "sol-session-1", "task_id": "T-001",
            "disposition": "accept_result", "evidence": "Inspected the interrupted attempt output.",
            "result": {"summary": "implementation survived interruption"},
        })
        result = self.engine.dispatch("verify", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        self.assertTrue(result["passed"])

    def test_authorize_next_phase_continues_same_run_after_dependency_completion(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            docs = make_project(root, task_items=[
                __import__("helpers").task(),
                __import__("helpers").task("T-002", phase="PH-02", dependencies=["T-001"]),
            ])
            engine = Engine(root)
            engine.dispatch("initialize", {})
            approve_release(engine, docs)
            run_id = start_run(engine)
            engine.dispatch("prepare", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
            engine.dispatch("result", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001", "result": {"summary": "done"}})
            engine.dispatch("verify", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
            engine.dispatch("review", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001", "verdict": "pass", "evidence": "Review passed."})
            engine.dispatch("close", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
            with self.assertRaises(EngineError):
                engine.dispatch("prepare", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-002"})
            engine.dispatch("authorize", {"run_id": run_id, "owner": "sol-session-1", "phases": ["PH-02"], "authorization": {"actor": "user", "statement": "Continue into PH-02.", "source": "conversation"}})
            result = engine.dispatch("prepare", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-002"})
            self.assertEqual(result["run_id"], run_id)

    def test_task_attempts_stop_after_three_rejected_reviews(self):
        run_id = self.initialize_approve_start()
        for attempt in range(3):
            self.engine.dispatch("prepare", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
            self.engine.dispatch("result", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001", "result": {"summary": "attempt {}".format(attempt + 1)}})
            self.engine.dispatch("verify", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
            self.engine.dispatch("review", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001", "verdict": "changes", "evidence": "Needs another change."})
        with self.assertRaises(EngineError) as ctx:
            self.engine.dispatch("prepare", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        self.assertEqual(ctx.exception.code, "retry_limit")

    def test_corrupt_event_log_fails_closed_and_state_rebuilds_from_events(self):
        run_id = self.initialize_approve_start()
        run_dir = self.root / ".spec-flow" / "runs" / run_id
        (run_dir / "state.json").write_text('{"forged":true}', encoding="utf-8")
        status = self.engine.dispatch("status", {"run_id": run_id})
        self.assertNotIn("forged", status)
        with (run_dir / "events.jsonl").open("a", encoding="utf-8") as stream:
            stream.write("{broken\n")
        with self.assertRaises(EngineError) as ctx:
            self.engine.dispatch("status", {"run_id": run_id})
        self.assertEqual(ctx.exception.code, "corrupt_log")

    def test_cli_returns_structured_json_and_nonzero_on_error(self):
        result = subprocess.run([sys.executable, str(CLI), "--root", str(self.root), "digest", "--input", str(self.root / "missing.json")], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["error"]["code"], "invalid_input")


if __name__ == "__main__":
    unittest.main()
