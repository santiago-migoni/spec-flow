"""E6 phase lifecycle mechanics exercised with temporary Git projects."""

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from harness.runtime.engine import Engine, EngineError
from helpers import FakeAdapter, FixtureProductionAdapter, approve_release, make_project, start_run, task


def git(root, *args):
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True).stdout.strip()


class PhaseLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.docs = make_project(self.root)
        git(self.root, "init", "-q")
        git(self.root, "config", "user.name", "Spec Flow Test")
        git(self.root, "config", "user.email", "spec-flow@example.test")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "test baseline")
        self.engine = Engine(self.root, adapter=FakeAdapter())
        self.engine.dispatch("initialize", {})
        approve_release(self.engine, self.docs)
        self.run_id = start_run(self.engine)

    def tearDown(self):
        self.temp.cleanup()

    def close_task(self):
        self.engine.dispatch("prepare", {"run_id": self.run_id, "owner": "sol-session-1", "task_id": "T-001"})
        (self.root / "src/example.py").write_text("# implementation\n", encoding="utf-8")
        self.engine.dispatch("result", {"run_id": self.run_id, "owner": "sol-session-1", "task_id": "T-001", "result": {"summary": "Implemented."}})
        self.engine.dispatch("verify", {"run_id": self.run_id, "owner": "sol-session-1", "task_id": "T-001"})
        self.engine.dispatch("review", {"run_id": self.run_id, "owner": "sol-session-1", "task_id": "T-001", "verdict": "pass", "evidence": "Inspected source and checks."})
        self.engine.dispatch("close", {"run_id": self.run_id, "owner": "sol-session-1", "task_id": "T-001"})

    def ready_review_commit(self):
        ready = self.engine.dispatch("phase-ready", {"run_id": self.run_id, "owner": "sol-session-1", "phase_id": "PH-01"})
        self.engine.dispatch("review-phase", {"run_id": self.run_id, "owner": "sol-session-1", "phase_id": "PH-01",
                                               "reviewer_session": "sol-review-2", "reviewer_agent_id": "/root/review-PH-01",
                                               "verdict": "pass", "evidence": "Reviewed staged phase diff."})
        committed = self.engine.dispatch("commit-phase", {"run_id": self.run_id, "owner": "sol-session-1", "phase_id": "PH-01",
                                                            "subject": "feat(example): implement behavior"})
        return ready, committed

    def release_review(self):
        return self.engine.dispatch("release-review", {"run_id": self.run_id, "owner": "sol-session-1",
                                                       "impact_status": "pending", "impact_evidence": []})

    def test_restore_packet_recovers_missing_phase_review_cache_with_same_pin(self):
        adapter = FixtureProductionAdapter()
        engine = Engine(self.root, adapter=adapter)
        engine.dispatch("initialize", {})
        approve_release(engine, self.docs)
        run_id = start_run(engine)
        engine.dispatch("prepare", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        (self.root / "src/example.py").write_text("# implementation\n", encoding="utf-8")
        engine.dispatch("bind-agent", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001",
                                        "agent_id": "/root/T-001", "session_id": "luna-session-1", "agent_path": "/root/T-001"})
        result = {"summary": "Implemented.", "files_modified": ["src/example.py"],
                  "checks": [{"step_id": "T-001.001", "check": "python check", "result": "passed"}],
                  "evidence": [{"kind": "diff", "reference": "src/example.py", "description": "Implementation diff."}],
                  "blockers": []}
        engine.dispatch("result", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001", "result": result})
        engine.dispatch("verify", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        engine.dispatch("review", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001", "verdict": "pass", "evidence": "Reviewed."})
        engine.dispatch("close", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        ready = engine.dispatch("phase-ready", {"run_id": run_id, "owner": "sol-session-1", "phase_id": "PH-01"})
        packet_path = Path(ready["packet_path"])
        original = json.loads(packet_path.read_text(encoding="utf-8"))
        packet_path.unlink()
        restored = engine.dispatch("restore-packet", {"run_id": run_id, "owner": "sol-session-1", "kind": "phase", "phase_id": "PH-01"})
        self.assertTrue(restored["restored"])
        self.assertEqual(restored["packet_sha256"], ready["packet_sha256"])
        self.assertEqual(json.loads(packet_path.read_text(encoding="utf-8")), original)
        self.assertEqual(engine.dispatch("status", {"run_id": run_id})["phases"]["PH-01"]["tree"], ready["tree"])

    def test_close_last_task_does_not_complete_run_or_release_lease(self):
        self.close_task()
        state = self.engine.dispatch("status", {"run_id": self.run_id})
        self.assertEqual(state["status"], "active")
        self.assertEqual(state["tasks"]["T-001"]["status"], "completed")
        pre_review = self.engine.dispatch("complete", {"release": "1.2.3"})
        self.assertFalse(pre_review["complete"])
        self.assertFalse(pre_review["technical_complete"])

    def test_phase_ready_review_commit_and_complete(self):
        self.close_task()
        ready, committed = self.ready_review_commit()
        self.assertRegex(ready["phase_marker"], r"^SPEC_FLOW_PHASE_REVIEW=[0-9a-f-]+/PH-[0-9]{2,}/[0-9a-f]{40}$")
        self.assertEqual(committed["phase_status"], "committed")
        status = self.engine.dispatch("status", {"run_id": self.run_id})
        self.assertEqual(status["phases"]["PH-01"]["status"], "committed")
        pre_review = self.engine.dispatch("complete", {"release": "1.2.3"})
        self.assertTrue(pre_review["complete"])
        self.assertTrue(pre_review["release_review_pending"])
        self.release_review()
        completion = self.engine.dispatch("complete", {"release": "1.2.3"})
        self.assertTrue(completion["complete"], completion)

    def test_phase_ready_detects_stale_completed_task_and_refreshes_checks(self):
        self.close_task()
        (self.root / "src/example.py").write_text("# relevant follow-up\n", encoding="utf-8")
        with self.assertRaises(EngineError) as ctx:
            self.engine.dispatch("phase-ready", {"run_id": self.run_id, "owner": "sol-session-1", "phase_id": "PH-01"})
        self.assertEqual(ctx.exception.code, "completed_evidence_stale")
        refreshed = self.engine.dispatch("refresh-evidence", {"run_id": self.run_id, "owner": "sol-session-1", "task_id": "T-001"})
        self.assertTrue(refreshed["refreshed"])
        self.assertEqual(self.engine.dispatch("status", {"run_id": self.run_id})["tasks"]["T-001"]["status"], "completed")
        self.engine.dispatch("phase-ready", {"run_id": self.run_id, "owner": "sol-session-1", "phase_id": "PH-01"})

    def test_release_review_writes_strict_derived_records_without_invalidating_sources(self):
        self.close_task()
        self.ready_review_commit()
        result = self.release_review()
        self.assertFalse(result["release_review"]["publication"])
        self.assertFalse(result["release_review"]["external_side_effects"])
        self.assertTrue(self.engine.dispatch("validate", {"release": "1.2.3"})["valid"])
        self.assertTrue(self.engine.dispatch("digest", {"path": ".specs/release-v1.2.3/spec.md"})["digest"])
        completion = self.engine.dispatch("complete", {"release": "1.2.3"})
        self.assertTrue(completion["complete"], completion)

    def test_release_review_rejects_stale_approved_spec_before_writing_derived_records(self):
        self.close_task()
        self.ready_review_commit()
        spec_path = self.docs["spec"]
        original = spec_path.read_text(encoding="utf-8")
        head = git(self.root, "rev-parse", "HEAD")
        events = (self.engine.store.run_dir(self.run_id) / "events.jsonl").read_bytes()
        spec_path.write_text(original.replace("Approved source decision.", "Changed after approval."), encoding="utf-8")
        changed = spec_path.read_bytes()
        with self.assertRaises(EngineError) as ctx:
            self.release_review()
        self.assertEqual(ctx.exception.code, "approval_stale")
        self.assertEqual(spec_path.read_bytes(), changed)
        self.assertEqual(git(self.root, "rev-parse", "HEAD"), head)
        self.assertEqual((self.engine.store.run_dir(self.run_id) / "events.jsonl").read_bytes(), events)
        self.assertIsNone(self.engine.dispatch("status", {"run_id": self.run_id}).get("release_review"))

    def test_release_review_rejects_changed_phase_code_before_writing_derived_records(self):
        self.close_task()
        self.ready_review_commit()
        spec_path = self.docs["spec"]
        original = spec_path.read_text(encoding="utf-8")
        head = git(self.root, "rev-parse", "HEAD")
        events = (self.engine.store.run_dir(self.run_id) / "events.jsonl").read_bytes()
        (self.root / "src/example.py").write_text("# changed after reviewed phase\\n", encoding="utf-8")
        with self.assertRaises(EngineError):
            self.release_review()
        self.assertEqual(spec_path.read_text(encoding="utf-8"), original)
        self.assertEqual(git(self.root, "rev-parse", "HEAD"), head)
        self.assertEqual((self.engine.store.run_dir(self.run_id) / "events.jsonl").read_bytes(), events)
        self.assertIsNone(self.engine.dispatch("status", {"run_id": self.run_id}).get("release_review"))

    def test_release_review_rejects_unrelated_head_advance_before_writing(self):
        self.close_task()
        self.ready_review_commit()
        spec_path = self.docs["spec"]
        original = spec_path.read_text(encoding="utf-8")
        (self.root / "unrelated.txt").write_text("unrelated\\n", encoding="utf-8")
        git(self.root, "add", "unrelated.txt")
        git(self.root, "commit", "-qm", "docs: unrelated change")
        head = git(self.root, "rev-parse", "HEAD")
        events = (self.engine.store.run_dir(self.run_id) / "events.jsonl").read_bytes()
        with self.assertRaises(EngineError):
            self.release_review()
        self.assertEqual(spec_path.read_text(encoding="utf-8"), original)
        self.assertEqual(git(self.root, "rev-parse", "HEAD"), head)
        self.assertEqual((self.engine.store.run_dir(self.run_id) / "events.jsonl").read_bytes(), events)
        self.assertIsNone(self.engine.dispatch("status", {"run_id": self.run_id}).get("release_review"))

    def test_release_review_allows_roadmap_record_from_reviewed_baseline(self):
        roadmap = self.docs["roadmap"]
        previous = {"schema": "spec-flow.derived-reference.v1", "kind": "roadmap-reference",
                    "release": "v1.2.2", "run_id": "prior-run",
                    "spec_path": ".specs/release-v1.2.2/spec.md", "impact_status": "pending"}
        text = roadmap.read_text(encoding="utf-8")
        roadmap.write_text(text.rstrip() + "\n\n<!-- spec-flow:generated:start -->\nSpec-Flow derived record:\n" +
                           json.dumps(previous, sort_keys=True, separators=(",", ":")) +
                           "\n<!-- spec-flow:generated:end -->\n", encoding="utf-8")
        self.close_task()
        self.ready_review_commit()
        result = self.release_review()
        current_text = roadmap.read_text(encoding="utf-8")
        self.assertIn('"release":"v1.2.3"', current_text)
        self.assertNotIn('"release":"v1.2.2"', current_text)
        self.assertIn("audit_commit_sha", result)

    def test_release_review_recovers_exact_partial_derived_write(self):
        self.close_task()
        self.ready_review_commit()
        controller = self.engine._phase_controller()
        original_write = controller._write_generated
        calls = 0

        def fail_after_spec(path, record, *, status=None):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise RuntimeError("crash after spec derived record")
            return original_write(path, record, status=status)

        with patch.object(controller, "_write_generated", side_effect=fail_after_spec):
            with self.assertRaises(RuntimeError):
                self.release_review()
        self.assertIsNone(self.engine.dispatch("status", {"run_id": self.run_id}).get("release_review"))
        result = self.release_review()
        self.assertIn("audit_commit_sha", result)
        self.assertTrue(self.engine.dispatch("complete", {"release": "1.2.3"})["complete"])

    def test_release_review_recovers_event_before_audit_commit(self):
        self.close_task()
        self.ready_review_commit()
        controller = self.engine._phase_controller()
        original_git = controller._git

        def fail_before_audit_commit(*args, **kwargs):
            if args and args[0] == "commit":
                raise EngineError("git_operation_failed", "simulated interruption before audit commit")
            return original_git(*args, **kwargs)

        with patch.object(controller, "_git", side_effect=fail_before_audit_commit):
            with self.assertRaises(EngineError):
                self.release_review()
        self.assertIsNotNone(self.engine.dispatch("status", {"run_id": self.run_id}).get("release_review"))
        self.assertEqual(controller._audit_candidates(self.run_id), [])
        recovered = self.release_review()
        self.assertIn("audit_commit_sha", recovered)

    def test_code_change_after_phase_commit_stays_incomplete_after_evidence_refresh(self):
        self.close_task()
        self.ready_review_commit()
        self.release_review()
        self.assertTrue(self.engine.dispatch("complete", {"release": "1.2.3"})["complete"])
        (self.root / "src/example.py").write_text("# post-review implementation change\n", encoding="utf-8")
        refreshed = self.engine.dispatch("refresh-evidence", {"run_id": self.run_id, "owner": "sol-session-1", "task_id": "T-001"})
        self.assertTrue(refreshed["refreshed"])
        completion = self.engine.dispatch("complete", {"release": "1.2.3"})
        self.assertFalse(completion["complete"])
        self.assertTrue(any("worktree changed" in item for item in completion["release_closure_reasons"]))

    def test_clean_commit_after_audit_cannot_replace_reviewed_phase_code(self):
        self.close_task()
        self.ready_review_commit()
        self.release_review()
        (self.root / "src/example.py").write_text("# changed and committed after audit\n", encoding="utf-8")
        git(self.root, "add", "src/example.py")
        git(self.root, "commit", "-qm", "fix(example): alter reviewed code")
        refreshed = self.engine.dispatch("refresh-evidence", {"run_id": self.run_id, "owner": "sol-session-1", "task_id": "T-001"})
        self.assertTrue(refreshed["refreshed"])
        completion = self.engine.dispatch("complete", {"release": "1.2.3"})
        self.assertFalse(completion["complete"])
        self.assertTrue(any("reviewed phase tree" in item for item in completion["reasons"]))

    def test_staged_unreviewed_file_keeps_technical_completion_false(self):
        self.close_task()
        self.ready_review_commit()
        self.release_review()
        (self.root / "outside.py").write_text("# staged after review\n", encoding="utf-8")
        git(self.root, "add", "outside.py")
        completion = self.engine.dispatch("complete", {"release": "1.2.3"})
        self.assertFalse(completion["complete"])
        self.assertTrue(any("worktree changed" in item for item in completion["reasons"]))

    def test_phase_ready_reuses_staged_tree_and_orphan_packet_after_crash(self):
        self.close_task()
        with patch.object(self.engine, "_append", side_effect=RuntimeError("crash after packet persistence")):
            with self.assertRaises(RuntimeError):
                self.engine.dispatch("phase-ready", {"run_id": self.run_id, "owner": "sol-session-1", "phase_id": "PH-01"})
        packet_path = next((self.root / ".spec-flow" / "runs" / self.run_id / "packets").glob("phase-PH-01-*.json"))
        original = json.loads(packet_path.read_text(encoding="utf-8"))
        adopted = self.engine.dispatch("phase-ready", {"run_id": self.run_id, "owner": "sol-session-1", "phase_id": "PH-01"})
        reread = json.loads(packet_path.read_text(encoding="utf-8"))
        self.assertEqual(adopted["packet_sha256"], original["packet_sha256"])
        self.assertEqual(reread["created_at"], original["created_at"])

    def test_commit_phase_adopts_unique_commit_after_receipt_write_crash(self):
        self.close_task()
        self.engine.dispatch("phase-ready", {"run_id": self.run_id, "owner": "sol-session-1", "phase_id": "PH-01"})
        self.engine.dispatch("review-phase", {"run_id": self.run_id, "owner": "sol-session-1", "phase_id": "PH-01",
                                               "reviewer_session": "sol-review-2", "reviewer_agent_id": "/root/review-PH-01",
                                               "verdict": "pass", "evidence": "Reviewed staged phase diff."})
        subject = "feat(example): implement behavior"
        with patch.object(self.engine.store, "write_json_atomic", side_effect=RuntimeError("crash after git commit")):
            with self.assertRaises(RuntimeError):
                self.engine.dispatch("commit-phase", {"run_id": self.run_id, "owner": "sol-session-1", "phase_id": "PH-01", "subject": subject})
        adopted = self.engine.dispatch("commit-phase", {"run_id": self.run_id, "owner": "sol-session-1", "phase_id": "PH-01", "subject": subject})
        self.assertTrue(adopted["adopted_after_crash"])
        self.assertEqual(len(self.engine._phase_controller()._commit_candidates(self.run_id, "PH-01")), 1)

    def test_commit_refuses_tree_mutation_after_review(self):
        self.close_task()
        self.engine.dispatch("phase-ready", {"run_id": self.run_id, "owner": "sol-session-1", "phase_id": "PH-01"})
        self.engine.dispatch("review-phase", {"run_id": self.run_id, "owner": "sol-session-1", "phase_id": "PH-01",
                                               "reviewer_session": "sol-review-2", "reviewer_agent_id": "/root/review-PH-01",
                                               "verdict": "pass", "evidence": "Reviewed staged phase diff."})
        (self.root / "src/example.py").write_text("# changed after review\n", encoding="utf-8")
        with self.assertRaises(EngineError) as ctx:
            self.engine.dispatch("commit-phase", {"run_id": self.run_id, "owner": "sol-session-1", "phase_id": "PH-01",
                                                   "subject": "feat(example): implement behavior"})
        self.assertEqual(ctx.exception.code, "phase_review_stale")

    def test_dependent_phase_prepare_rechecks_prior_commit_ancestry(self):
        self.temp.cleanup()
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.docs = make_project(self.root, task_items=[task("T-001"), task("T-002", phase="PH-02", dependencies=["T-001"])])
        git(self.root, "init", "-q")
        git(self.root, "config", "user.name", "Spec Flow Test")
        git(self.root, "config", "user.email", "spec-flow@example.test")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "test baseline")
        self.engine = Engine(self.root, adapter=FakeAdapter())
        self.engine.dispatch("initialize", {})
        approve_release(self.engine, self.docs)
        self.run_id = start_run(self.engine)
        self.close_task()
        ready, _ = self.ready_review_commit()
        parent = ready["parent"]
        self.engine.dispatch("authorize", {"run_id": self.run_id, "owner": "sol-session-1", "phases": ["PH-02"],
                                            "authorization": {"actor": "user", "statement": "Execute PH-02.", "source": "conversation"}})
        git(self.root, "update-ref", "HEAD", parent)
        with self.assertRaises(EngineError) as ctx:
            self.engine.dispatch("prepare", {"run_id": self.run_id, "owner": "sol-session-1", "task_id": "T-002"})
        self.assertEqual(ctx.exception.code, "phase_commit_not_ancestor")

    def test_fixture_production_adapter_holds_lease_until_final_audit_commit(self):
        adapter = FixtureProductionAdapter()
        engine = Engine(self.root, adapter=adapter)
        engine.dispatch("initialize", {})
        approve_release(engine, self.docs)
        run_id = engine.dispatch("start", {
            "release": "1.2.3", "owner": "sol-session-1", "phases": ["PH-01"],
            "authorization": {"actor": "user", "statement": "Execute PH-01.", "source": "conversation"},
            "capabilities": {"inventory_reference": "fixture inventory", "operations": {}, "probe_evidence": {}},
        })["run_id"]
        engine.dispatch("prepare", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        (self.root / "src/example.py").write_text("# implementation\n", encoding="utf-8")
        engine.dispatch("bind-agent", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001",
                                        "agent_id": "/root/T-001", "session_id": "luna-session-1", "agent_path": "/root/T-001"})
        result = {"summary": "Implemented.", "files_modified": ["src/example.py"],
                  "checks": [{"step_id": "T-001.001", "check": "python check", "result": "passed"}],
                  "evidence": [{"kind": "diff", "reference": "src/example.py", "description": "Implementation diff."}],
                  "blockers": []}
        engine.dispatch("result", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001", "result": result})
        engine.dispatch("verify", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        engine.dispatch("review", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001", "verdict": "pass", "evidence": "Reviewed."})
        engine.dispatch("close", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        self.assertEqual(adapter.releases, 0)
        engine.dispatch("phase-ready", {"run_id": run_id, "owner": "sol-session-1", "phase_id": "PH-01"})
        engine.dispatch("review-phase", {"run_id": run_id, "owner": "sol-session-1", "phase_id": "PH-01",
                                          "reviewer_session": "sol-review-2", "reviewer_agent_id": "/root/review-PH-01",
                                          "verdict": "pass", "evidence": "Reviewed phase tree."})
        engine.dispatch("commit-phase", {"run_id": run_id, "owner": "sol-session-1", "phase_id": "PH-01",
                                          "subject": "feat(example): implement behavior"})
        self.assertEqual(adapter.releases, 0)
        with patch.object(adapter, "release", side_effect=RuntimeError("crash after audit commit")):
            with self.assertRaises(RuntimeError):
                engine.dispatch("release-review", {"run_id": run_id, "owner": "sol-session-1", "impact_status": "pending", "impact_evidence": []})
        audit_candidates = engine._phase_controller()._audit_candidates(run_id)
        self.assertEqual(len(audit_candidates), 1)
        recovered = engine.dispatch("release-review", {"run_id": run_id, "owner": "sol-session-1", "impact_status": "pending", "impact_evidence": []})
        self.assertTrue(recovered["adopted_after_crash"])
        self.assertEqual(adapter.releases, 1)
        self.assertTrue(engine.dispatch("complete", {"release": "1.2.3"})["complete"])


if __name__ == "__main__":
    unittest.main()
