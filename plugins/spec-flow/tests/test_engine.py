import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from harness.runtime.engine import Engine, EngineError
from harness.runtime.contracts import ContractError, document_digest
from helpers import FakeAdapter, FixtureProductionAdapter, approve_release, make_project, start_run, task

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
CLI = PLUGIN_ROOT / "scripts" / "spec-flow.py"


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.docs = make_project(self.root)
        self.engine = Engine(self.root, adapter=FakeAdapter())

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

    def test_exact_approval_retry_reuses_receipt_but_new_statement_is_recorded(self):
        self.engine.dispatch("initialize", {})
        path = self.docs["constitution"].relative_to(self.root).as_posix()
        payload = {"path": path, "actor": "user", "statement": "Approve constitution.", "source": "conversation"}
        first = self.engine.dispatch("approve", payload)
        retry = self.engine.dispatch("approve", payload)
        changed = self.engine.dispatch("approve", {**payload, "statement": "Approve constitution revision."})
        rows = self.engine.store.approvals()
        self.assertEqual(first["sequence"], retry["sequence"])
        self.assertTrue(retry["already_approved"])
        self.assertNotEqual(changed["sequence"], first["sequence"])
        self.assertEqual(len(rows), 2)

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

    def test_packet_contains_only_selected_task_and_transitive_dependencies(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            docs = make_project(root, task_items=[
                __import__("helpers").task("T-001"),
                __import__("helpers").task("T-002"),
            ])
            engine = Engine(root, adapter=FakeAdapter())
            engine.dispatch("initialize", {})
            approve_release(engine, docs)
            run_id = start_run(engine)
            result = engine.dispatch("prepare", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
            packet = json.loads(Path(result["packet_path"]).read_text())
            tasks_source = next(item for item in packet["sources"] if item["path"].endswith("/tasks.md"))
            self.assertEqual([item["id"] for item in tasks_source["contract"]["tasks"]], ["T-001"])
            self.assertEqual(packet["source_digests"][".specs/release-v1.2.3/tasks.md"], document_digest(docs["tasks"]))

    def test_packet_section_projection_preserves_nested_decision_headings(self):
        selected = Engine._packet_sections("## Edge cases and non-goals\nIntro\n### Exclusions\nDo not modify billing\n## Other\nOmit this", {"Edge cases and non-goals"})
        self.assertIn("Do not modify billing", selected)
        self.assertNotIn("Omit this", selected)

    def test_packet_preserves_current_spec_quality_and_acceptance_context(self):
        from harness.runtime.contracts import read_document

        template = PLUGIN_ROOT / "skills/specify/assets/spec-template.md"
        document = read_document(template)
        prose = document["prose"].replace("[Measurable target]", "p95 latency below 250 ms")
        projected = self.engine._packet_source_projection(
            ".specs/release-v1.2.3/spec.md", document["contract"], prose,
            {"acceptance": ["AC-003"]}, {},
        )
        self.assertEqual([item["id"] for item in projected["contract"]["stories"]], ["US-001"])
        self.assertEqual([item["id"] for item in projected["contract"]["acceptance"]], ["AC-003"])
        self.assertIn("NFR-001", projected["prose"])
        self.assertIn("p95 latency below 250 ms", projected["prose"])
        self.assertIn("## Scope and exclusions", projected["prose"])
        self.assertIn("## Rules, acceptance, and examples", projected["prose"])
        self.assertIn("## Edge cases, errors, and compatibility", projected["prose"])
        self.assertIn("## Assumptions, dependencies, and open questions", projected["prose"])
        self.assertNotIn("## User stories", projected["prose"])
        self.assertNotIn("## Readiness for planning, approval, and amendments", projected["prose"])

    def test_packet_preserves_legacy_spec_context(self):
        from harness.runtime.contracts import read_document

        document = read_document(self.docs["spec"])
        headings = ("Release outcome", "Release-specific nonfunctional requirements",
                    "Edge cases and non-goals", "Outcome measurement", "Open questions")
        prose = "\n\n".join("## " + heading + "\n\nLegacy decision " + str(index)
                             for index, heading in enumerate(headings))
        projected = self.engine._packet_source_projection(
            ".specs/release-v1.2.3/spec.md", document["contract"], prose,
            {"acceptance": ["AC-001"]}, {},
        )
        self.assertEqual(projected["prose"], prose)

    def test_prepare_adopts_orphan_packet_without_changing_creation_time_or_hash(self):
        run_id = self.initialize_approve_start()
        with patch.object(self.engine, "_append", side_effect=RuntimeError("simulated crash after packet write")):
            with self.assertRaises(RuntimeError):
                self.engine.dispatch("prepare", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        packet_path = next((self.root / ".spec-flow" / "runs" / run_id / "packets").glob("T-001-1.json"))
        original = json.loads(packet_path.read_text())
        adopted = self.engine.dispatch("prepare", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        self.assertEqual(adopted["packet_sha256"], original["packet_sha256"])
        self.assertEqual(json.loads(packet_path.read_text())["created_at"], original["created_at"])

    def test_fixture_attested_native_lifecycle_binds_result_and_closes_idempotently(self):
        adapter = FixtureProductionAdapter()
        engine = Engine(self.root, adapter=adapter)
        engine.dispatch("initialize", {})
        approve_release(engine, self.docs)
        run_id = engine.dispatch("start", {
            "release": "1.2.3", "owner": "sol-session-1", "phases": ["PH-01"],
            "authorization": {"actor": "user", "statement": "Execute PH-01.", "source": "conversation"},
            "capabilities": {"inventory_reference": "fixture inventory", "operations": {}, "probe_evidence": {}},
        })["run_id"]
        prepared = engine.dispatch("prepare", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        (self.root / "src/example.py").write_text("# implemented\n", encoding="utf-8")
        engine.dispatch("bind-agent", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001",
                                        "agent_id": "/root/T-001", "session_id": "luna-session-1", "agent_path": "/root/T-001"})
        result = {"summary": "Implemented the behavior.", "files_modified": ["src/example.py"],
                  "checks": [{"step_id": "T-001.001", "check": "python check", "result": "passed"}],
                  "evidence": [{"kind": "diff", "reference": "src/example.py", "description": "Changed the implementation."}],
                  "blockers": []}
        engine.dispatch("result", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001", "result": result})
        engine.dispatch("verify", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        engine.dispatch("review", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001", "verdict": "pass", "evidence": "Reviewed the diff."})
        closed = engine.dispatch("close", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        duplicate = engine.dispatch("close", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        events = engine.store.read_events(run_id)
        result_event = next(item for item in events if item["event"] == "result_received")
        self.assertTrue(prepared["packet_sha256"])
        self.assertEqual(result_event["data"]["host_attestation"]["attestation_sha256"], "fixture-hash")
        self.assertFalse(closed["run_completed"])
        self.assertTrue(duplicate["already_completed"])
        self.assertEqual(adapter.releases, 0)

    def test_production_retry_clears_previous_binding_and_uses_packet_created_at(self):
        adapter = FixtureProductionAdapter()
        adapter.attest_calls = []
        original_attest = adapter.attest_session
        def record_attest(session_id, role, **kwargs):
            adapter.attest_calls.append((session_id, role, kwargs))
            return original_attest(session_id, role, **kwargs)
        adapter.attest_session = record_attest
        engine = Engine(self.root, adapter=adapter)
        engine.dispatch("initialize", {})
        approve_release(engine, self.docs)
        run_id = engine.dispatch("start", {
            "release": "1.2.3", "owner": "sol-session-1", "phases": ["PH-01"],
            "authorization": {"actor": "user", "statement": "Execute PH-01.", "source": "conversation"},
            "capabilities": {"inventory_reference": "fixture inventory", "operations": {}, "probe_evidence": {}},
        })["run_id"]
        first = engine.dispatch("prepare", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        first_packet = json.loads(Path(first["packet_path"]).read_text())
        (self.root / "src/example.py").write_text("# attempt one\n", encoding="utf-8")
        engine.dispatch("bind-agent", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001",
                                        "agent_id": "/root/T-001-one", "session_id": "luna-session-1", "agent_path": "/root/T-001-one"})
        result = {"summary": "First attempt.", "files_modified": ["src/example.py"],
                  "checks": [{"step_id": "T-001.001", "check": "python check", "result": "passed"}],
                  "evidence": [{"kind": "diff", "reference": "src/example.py", "description": "Attempt one change."}],
                  "blockers": []}
        engine.dispatch("result", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001", "result": result})
        with patch("harness.runtime.engine.subprocess.run", return_value=subprocess.CompletedProcess([], 1, "failed\n")):
            with self.assertRaises(EngineError):
                engine.dispatch("verify", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        engine.dispatch("retry", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001",
                                   "reason": "First verification failed.", "hypothesis": "A clean second attempt will pass."})
        second = engine.dispatch("prepare", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        state = engine.dispatch("status", {"run_id": run_id})["tasks"]["T-001"]
        second_packet = json.loads(Path(second["packet_path"]).read_text())
        self.assertEqual(state["attempt"], 2)
        self.assertIsNone(state.get("agent"))
        self.assertIsNone(state.get("result"))
        self.assertIsNone(state.get("review"))
        self.assertEqual(state["prepared_at"], second_packet["created_at"])
        # Simulate an already-recorded native attempt from before the explicit
        # prepared_at event field existed; state loading must recover the pinned
        # packet timestamp, not trust a later event timestamp or re-prepare.
        events = engine.store.read_events(run_id)
        second_prepared = [event for event in events if event["event"] == "prepared"][1]
        second_prepared["data"].pop("prepared_at")
        events_path = engine.store.run_dir(run_id) / "events.jsonl"
        events_path.write_text("".join(json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n" for event in events), encoding="utf-8")
        recovered = engine._state(run_id)["tasks"]["T-001"]
        self.assertEqual(recovered["prepared_at"], second_packet["created_at"])
        prepared_events = [event["data"] for event in engine.store.read_events(run_id) if event["event"] == "prepared"]
        self.assertEqual(state["baseline"], prepared_events[0]["baseline"])
        self.assertEqual(state["attempt_baseline"], prepared_events[1]["baseline"])
        self.assertNotEqual(state["attempt_baseline"], state["baseline"])
        engine.dispatch("bind-agent", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001",
                                        "agent_id": "/root/T-001-two", "session_id": "luna-session-2", "agent_path": "/root/T-001-two"})
        second_bind = [item for item in adapter.attest_calls if item[0] == "luna-session-2"][-1]
        self.assertEqual(second_bind[2]["after"], second_packet["created_at"])

    def test_restore_packet_recovers_missing_task_cache_without_resetting_attempt_or_binding(self):
        adapter = FixtureProductionAdapter()
        engine = Engine(self.root, adapter=adapter)
        engine.dispatch("initialize", {})
        approve_release(engine, self.docs)
        run_id = engine.dispatch("start", {
            "release": "1.2.3", "owner": "sol-session-1", "phases": ["PH-01"],
            "authorization": {"actor": "user", "statement": "Execute PH-01.", "source": "conversation"},
            "capabilities": {"inventory_reference": "fixture inventory", "operations": {}, "probe_evidence": {}},
        })["run_id"]
        prepared = engine.dispatch("prepare", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        packet_path = Path(prepared["packet_path"])
        packet = json.loads(packet_path.read_text())
        engine.dispatch("bind-agent", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001",
                                        "agent_id": "/root/T-001", "session_id": "luna-session-1", "agent_path": "/root/T-001"})
        packet_path.unlink()
        restored = engine.dispatch("restore-packet", {"run_id": run_id, "owner": "sol-session-1", "kind": "task", "task_id": "T-001"})
        self.assertTrue(restored["restored"])
        again = engine.dispatch("restore-packet", {"run_id": run_id, "owner": "sol-session-1", "kind": "task", "task_id": "T-001"})
        self.assertFalse(again["restored"])
        self.assertEqual(restored["packet_sha256"], prepared["packet_sha256"])
        self.assertEqual(json.loads(packet_path.read_text()), packet)
        state = engine.dispatch("status", {"run_id": run_id})["tasks"]["T-001"]
        self.assertEqual(state["attempt"], 1)
        self.assertEqual(state["agent"]["session_id"], "luna-session-1")
        engine.dispatch("interrupt", {"run_id": run_id, "owner": "sol-session-1"})
        resumed = engine.dispatch("resume", {"run_id": run_id, "owner": "sol-session-1"})
        self.assertTrue(resumed["reconciliation_required"])

    def test_restore_packet_fails_closed_for_stale_sources_and_corrupt_existing_cache(self):
        adapter = FixtureProductionAdapter()
        engine = Engine(self.root, adapter=adapter)
        engine.dispatch("initialize", {})
        approve_release(engine, self.docs)
        run_id = engine.dispatch("start", {
            "release": "1.2.3", "owner": "sol-session-1", "phases": ["PH-01"],
            "authorization": {"actor": "user", "statement": "Execute PH-01.", "source": "conversation"},
            "capabilities": {"inventory_reference": "fixture inventory", "operations": {}, "probe_evidence": {}},
        })["run_id"]
        prepared = engine.dispatch("prepare", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        packet_path = Path(prepared["packet_path"])
        packet_path.unlink()
        original = self.docs["spec"].read_text(encoding="utf-8")
        self.docs["spec"].write_text(original + "\nChanged after approval.\n", encoding="utf-8")
        with self.assertRaises(EngineError) as stale:
            engine.dispatch("restore-packet", {"run_id": run_id, "owner": "sol-session-1", "kind": "task", "task_id": "T-001"})
        self.assertEqual(stale.exception.code, "approval_stale")
        self.docs["spec"].write_text(original, encoding="utf-8")
        packet_path.write_text("{corrupt", encoding="utf-8")
        with self.assertRaises(EngineError) as corrupt:
            engine.dispatch("restore-packet", {"run_id": run_id, "owner": "sol-session-1", "kind": "task", "task_id": "T-001"})
        self.assertEqual(corrupt.exception.code, "packet_corrupt")
        self.assertEqual(packet_path.read_text(encoding="utf-8"), "{corrupt")

    def test_fixture_takeover_preserves_original_luna_parent_for_reconciliation(self):
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
        engine.dispatch("bind-agent", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001",
                                        "agent_id": "/root/T-001", "session_id": "luna-session-1", "agent_path": "/root/T-001"})
        (self.root / "src/example.py").write_text("# interrupted implementation\n", encoding="utf-8")
        engine.dispatch("interrupt", {"run_id": run_id, "owner": "sol-session-1"})
        takeover = engine.dispatch("takeover", {"run_id": run_id, "previous_owner": "sol-session-1",
                                                  "owner": "sol-session-2", "reconciliation": "Inspected old owner and child terminal records."})
        self.assertEqual(takeover["authorized_phases"], ["PH-01"])
        resumed = engine.dispatch("resume", {"run_id": run_id, "owner": "sol-session-2"})
        self.assertTrue(resumed["reconciliation_required"])
        task_state = engine.dispatch("status", {"run_id": run_id})["tasks"]["T-001"]
        self.assertEqual(task_state["agent"]["parent_session"], "sol-session-1")

    def test_interrupted_unbound_spawn_can_be_late_bound_before_reconciliation(self):
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
        engine.dispatch("interrupt", {"run_id": run_id, "owner": "sol-session-1"})
        engine.dispatch("resume", {"run_id": run_id, "owner": "sol-session-1"})
        with self.assertRaises(EngineError) as before_binding:
            engine.dispatch("reconcile", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001",
                                            "disposition": "retry", "evidence": "No result accepted."})
        self.assertEqual(before_binding.exception.code, "agent_binding_required")
        engine.dispatch("bind-agent", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001",
                                        "agent_id": "/root/T-001", "session_id": "luna-session-1", "agent_path": "/root/T-001"})
        original_code = (self.root / "src/example.py").read_text(encoding="utf-8")
        (self.root / "src/example.py").write_text("# unbound child may have changed this\n", encoding="utf-8")
        with self.assertRaises(EngineError) as changed:
            engine.dispatch("reconcile", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001",
                "disposition": "no_spawn", "evidence": "Inventory has no child, but files changed.",
                "native_inspection": {"owner_session": "sol-session-1", "inventory_reference": "fixture:list_agents:current",
                                      "checked_at": "2099-01-01T00:00:00Z", "agents": []}})
        self.assertEqual(changed.exception.code, "no_spawn_worktree_changed")
        (self.root / "src/example.py").write_text(original_code, encoding="utf-8")
        reconciled = engine.dispatch("reconcile", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001",
                                                     "disposition": "retry", "evidence": "Inspected the terminal child session before retry.",
                                                     "reason": "The interrupted agent has no accepted result.",
                                                     "hypothesis": "A new attempt will complete the task."})
        self.assertTrue(reconciled["retry_ready"])

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

    def test_verify_rejects_command_that_mutates_task_code_after_passing_check(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            checks = task(command=["python3", "-c", "from pathlib import Path; p=Path('src/example.py'); assert 'GOOD' in p.read_text(); print('verification passed', flush=True); p.write_text('BROKEN\\n')"])
            checks["steps"].append({"id": "T-001.002", "action": "Restore the file after the first check.",
                                    "verification": {"command": ["python3", "-c", "from pathlib import Path; p=Path('src/example.py'); assert 'BROKEN' in p.read_text(); print('verification passed', flush=True); p.write_text('GOOD\\n')"],
                                                      "expected": "verification passed"}})
            docs = make_project(root, task_items=[checks])
            (root / "src/example.py").write_text("GOOD\\n", encoding="utf-8")
            engine = Engine(root, adapter=FakeAdapter())
            engine.dispatch("initialize", {})
            approve_release(engine, docs)
            run_id = start_run(engine)
            engine.dispatch("prepare", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
            engine.dispatch("result", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001", "result": {"summary": "implemented"}})
            with self.assertRaises(EngineError) as ctx:
                engine.dispatch("verify", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
            self.assertEqual(ctx.exception.code, "verification_mutated_code")
            state = engine.dispatch("status", {"run_id": run_id})
            self.assertNotEqual(state["tasks"]["T-001"]["status"], "verified")
            with self.assertRaises(EngineError):
                engine.dispatch("review", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001", "verdict": "pass", "evidence": "Review passed."})

    def test_retry_cannot_launder_out_of_scope_change_into_new_baseline(self):
        run_id = self.initialize_approve_start()
        self.engine.dispatch("prepare", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        self.engine.dispatch("result", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001", "result": {"summary": "attempt one"}})
        (self.root / "outside.py").write_text("unrelated change\n", encoding="utf-8")
        with self.assertRaises(EngineError) as ctx:
            self.engine.dispatch("verify", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        self.assertEqual(ctx.exception.code, "out_of_scope_changes")
        self.engine.dispatch("retry", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001",
                                         "reason": "Remove unrelated change.", "hypothesis": "Retry keeps original scope baseline."})
        self.engine.dispatch("prepare", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        self.engine.dispatch("result", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001", "result": {"summary": "attempt two"}})
        with self.assertRaises(EngineError) as retry_error:
            self.engine.dispatch("verify", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        self.assertEqual(retry_error.exception.code, "out_of_scope_changes")

    def test_verify_rejects_empty_and_zero_test_results(self):
        for command in (["python3", "-c", "pass"], ["python3", "-c", "print('Ran 0 tests')"]):
            with self.subTest(command=command), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                docs = make_project(root, command=command)
                engine = Engine(root, adapter=FakeAdapter())
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
            engine = Engine(root, adapter=FakeAdapter())
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

    def test_next_phase_requires_prior_phase_commit_even_after_authorization(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            docs = make_project(root, task_items=[
                __import__("helpers").task(),
                __import__("helpers").task("T-002", phase="PH-02", dependencies=["T-001"]),
            ])
            engine = Engine(root, adapter=FakeAdapter())
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
            with self.assertRaises(EngineError) as ctx:
                engine.dispatch("prepare", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-002"})
            self.assertEqual(ctx.exception.code, "phase_dependency_not_committed")

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


    def _complete_fixture_task(self, run_id):
        self.engine.dispatch("prepare", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        (self.root / "src/example.py").write_text("# implemented\n", encoding="utf-8")
        self.engine.dispatch("result", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001",
                                         "result": {"summary": "Implemented."}})
        self.engine.dispatch("verify", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        self.engine.dispatch("review", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001",
                                         "verdict": "pass", "evidence": "Inspected implementation and checks."})
        self.engine.dispatch("close", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})

    def _abandon(self, run_id):
        return self.engine.dispatch("abandon", {"run_id": run_id, "owner": "sol-session-1",
                                                  "reason": "Approved sources changed; restart with current pins.",
                                                  "authorization": {"actor": "user", "statement": "Abandon this run and preserve its history.", "source": "conversation"}})

    def test_production_abandon_retries_lease_release_without_duplicate_event(self):
        adapter = FixtureProductionAdapter()
        engine = Engine(self.root, adapter=adapter)
        engine.dispatch("initialize", {})
        approve_release(engine, self.docs)
        run_id = engine.dispatch("start", {
            "release": "1.2.3", "owner": "sol-session-1", "phases": ["PH-01"],
            "authorization": {"actor": "user", "statement": "Execute PH-01.", "source": "conversation"},
            "capabilities": {"inventory_reference": "fixture", "operations": {}, "probe_evidence": {}},
        })["run_id"]
        with patch.object(adapter, "release", side_effect=[RuntimeError("crash after abandonment event"), None]):
            with self.assertRaises(RuntimeError):
                engine.dispatch("abandon", {"run_id": run_id, "owner": "sol-session-1", "reason": "Restart safely.",
                                              "authorization": {"actor": "user", "statement": "Abandon this run.", "source": "conversation"}})
            replay = engine.dispatch("abandon", {"run_id": run_id, "owner": "sol-session-1", "reason": "Restart safely.",
                                                   "authorization": {"actor": "user", "statement": "Abandon this run.", "source": "conversation"}})
        events = engine.store.read_events(run_id)
        self.assertTrue(replay["already_abandoned"])
        self.assertEqual(sum(item["event"] == "abandoned" for item in events), 1)

    def test_abandon_preserves_completed_evidence_for_exact_pins(self):
        run_id = self.initialize_approve_start()
        self._complete_fixture_task(run_id)
        abandoned = self._abandon(run_id)
        self.assertEqual(abandoned["status"], "abandoned")
        self.assertIn("history_preserved", abandoned)
        next_run = start_run(self.engine)
        state = self.engine.dispatch("status", {"run_id": next_run})
        self.assertEqual(state["tasks"]["T-001"]["status"], "completed")
        self.assertEqual(state["tasks"]["T-001"]["prior_run_id"], run_id)
        self.assertTrue(Path(self.root / state["tasks"]["T-001"]["evidence_path"]).is_file())

    def test_production_prepare_crash_before_spawn_needs_inventory_and_no_change_reconciliation(self):
        adapter = FixtureProductionAdapter()
        engine = Engine(self.root, adapter=adapter)
        engine.dispatch("initialize", {})
        approve_release(engine, self.docs)
        run_id = engine.dispatch("start", {
            "release": "1.2.3", "owner": "sol-session-1", "phases": ["PH-01"],
            "authorization": {"actor": "user", "statement": "Execute PH-01.", "source": "conversation"},
            "capabilities": {"inventory_reference": "fixture", "operations": {}, "probe_evidence": {}},
        })["run_id"]
        engine.dispatch("prepare", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        engine.dispatch("interrupt", {"run_id": run_id, "owner": "sol-session-1"})
        engine.dispatch("resume", {"run_id": run_id, "owner": "sol-session-1"})
        with self.assertRaises(EngineError) as ctx:
            engine.dispatch("reconcile", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001",
                                           "disposition": "no_spawn", "evidence": "No child was launched."})
        self.assertEqual(ctx.exception.code, "native_inventory_invalid")
        original_code = (self.root / "src/example.py").read_text(encoding="utf-8")
        (self.root / "src/example.py").write_text("# unbound child may have changed this\n", encoding="utf-8")
        inventory = {"owner_session": "sol-session-1", "inventory_reference": "fixture:list_agents:current",
                     "checked_at": "2099-01-01T00:00:00Z", "agents": []}
        with self.assertRaises(EngineError) as changed:
            engine.dispatch("reconcile", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001",
                "disposition": "no_spawn", "evidence": "Inventory has no child, but files changed.", "native_inspection": inventory})
        self.assertEqual(changed.exception.code, "no_spawn_worktree_changed")
        (self.root / "src/example.py").write_text(original_code, encoding="utf-8")
        reconciled = engine.dispatch("reconcile", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001",
            "disposition": "no_spawn", "evidence": "Owner inventory inspected; no matching child exists; task files unchanged.",
            "native_inspection": inventory})
        self.assertEqual(reconciled["disposition"], "no_spawn")
        self.assertEqual(engine.dispatch("status", {"run_id": run_id})["tasks"]["T-001"]["status"], "needs_changes")
        self._abandon(run_id)
        self.assertEqual(engine.dispatch("status", {"run_id": run_id})["status"], "abandoned")

    def test_abandon_rejects_active_attempt_until_reconciled(self):
        run_id = self.initialize_approve_start()
        self.engine.dispatch("prepare", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"})
        with self.assertRaises(EngineError) as ctx:
            self._abandon(run_id)
        self.assertEqual(ctx.exception.code, "active_task_requires_reconciliation")
        self.engine.dispatch("interrupt", {"run_id": run_id, "owner": "sol-session-1"})
        self.engine.dispatch("resume", {"run_id": run_id, "owner": "sol-session-1"})
        self.engine.dispatch("reconcile", {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001",
                                             "disposition": "retry", "evidence": "No native child was started in this mechanics fixture.",
                                             "reason": "Restart from a clean attempt.", "hypothesis": "No implementation changes were made."})
        self._abandon(run_id)
        self.assertEqual(self.engine.dispatch("status", {"run_id": run_id})["status"], "abandoned")

    def test_abandon_then_restart_carries_attempt_limit_and_does_not_reuse_stale_source_evidence(self):
        run_id = self.initialize_approve_start()
        self._complete_fixture_task(run_id)
        self._abandon(run_id)
        self.docs["tasks"].write_text(self.docs["tasks"].read_text(encoding="utf-8").replace("Approved source decision.", "Updated task source decision."), encoding="utf-8")
        self.engine.dispatch("approve", {"path": ".specs/release-v1.2.3/tasks.md", "actor": "user",
                                          "statement": "Approve updated task source.", "source": "conversation"})
        next_run = start_run(self.engine)
        state = self.engine.dispatch("status", {"run_id": next_run})
        self.assertEqual(state["tasks"].get("T-001", {}).get("status"), None)
        prepared = self.engine.dispatch("prepare", {"run_id": next_run, "owner": "sol-session-1", "task_id": "T-001"})
        self.assertEqual(prepared["attempt"], 2)
        self.engine.dispatch("interrupt", {"run_id": next_run, "owner": "sol-session-1"})
        self.engine.dispatch("resume", {"run_id": next_run, "owner": "sol-session-1"})
        self.engine.dispatch("reconcile", {"run_id": next_run, "owner": "sol-session-1", "task_id": "T-001",
                                             "disposition": "retry", "evidence": "Second attempt was reconciled.",
                                             "reason": "Run is stale after source change.", "hypothesis": "No unapproved code changed."})
        self._abandon(next_run)
        final_run = start_run(self.engine)
        third_attempt = self.engine.dispatch("prepare", {"run_id": final_run, "owner": "sol-session-1", "task_id": "T-001"})
        self.assertEqual(third_attempt["attempt"], 3)


    def _exhausted_native_failure_fixture(self):
        adapter = FixtureProductionAdapter()
        self.docs = make_project(self.root, command=["python3", "-c", "print('injected failure'); raise SystemExit(1)"])
        engine = Engine(self.root, adapter=adapter)
        engine.dispatch("initialize", {})
        approve_release(engine, self.docs)
        run_id = start_run(engine)
        payload = {"run_id": run_id, "owner": "sol-session-1", "task_id": "T-001"}
        for attempt in range(1, 4):
            engine.dispatch("prepare", payload)
            path = "/root/luna-" + str(attempt)
            engine.dispatch("bind-agent", {**payload, "agent_id": path, "agent_path": path, "session_id": "luna-" + str(attempt)})
            engine.dispatch("result", {**payload, "result": {
                "summary": "Intentionally insufficient fixture implementation.", "files_modified": [],
                "checks": [{"step_id": "T-001.001", "check": "Canonical command", "result": "injected failure"}],
                "evidence": [{"kind": "inspection", "reference": "fixture", "description": "Failure is deliberate."}], "blockers": []}})
            with self.assertRaises(EngineError) as failed:
                engine.dispatch("verify", payload)
            self.assertEqual(failed.exception.code, "verification_failed")
            if attempt < 3:
                with self.assertRaises(EngineError) as early:
                    engine.dispatch("abandon", self._exhausted_abandon_payload(run_id))
                self.assertEqual(early.exception.code, "active_task_requires_reconciliation")
                engine.dispatch("retry", {**payload, "reason": "Correct the injected failure.", "hypothesis": "Next attempt may pass."})
        return engine, adapter, run_id, payload

    @staticmethod
    def _exhausted_abandon_payload(run_id):
        return {"run_id": run_id, "owner": "sol-session-1", "reason": "Escalate exhausted failed task without accepting it.",
                "authorization": {"actor": "user", "statement": "Abandon this exhausted run and preserve all history.", "source": "conversation"}}

    def test_exhausted_failed_task_abandon_preserves_failure_history_and_restart_budget(self):
        engine, adapter, run_id, payload = self._exhausted_native_failure_fixture()
        before = engine.dispatch("status", {"run_id": run_id})
        prior_events = engine.store.read_events(run_id)
        code = (self.root / "src/example.py").read_bytes()
        for op, extra, error in (("retry", {"reason": "Fourth attempt.", "hypothesis": "Should remain blocked."}, "retry_limit"),
                                 ("review", {"verdict": "pass", "evidence": "Cannot accept failed verification."}, "verification_required"),
                                 ("close", {}, "review_required")):
            with self.assertRaises(EngineError) as blocked:
                engine.dispatch(op, {**payload, **extra})
            self.assertEqual(blocked.exception.code, error)
        result = engine.dispatch("abandon", self._exhausted_abandon_payload(run_id))
        after = engine.dispatch("status", {"run_id": run_id})
        self.assertEqual(result["status"], "abandoned")
        self.assertIsNone(after["active_task"])
        self.assertEqual(after["tasks"], before["tasks"])
        self.assertEqual(after["tasks"]["T-001"]["status"], "verification_failed")
        self.assertEqual(engine.store.read_events(run_id)[:-1], prior_events)
        abandonment = engine.store.read_events(run_id)[-1]["data"]["unresolved_task"]
        self.assertEqual(abandonment["task_id"], "T-001")
        self.assertEqual(abandonment["attempt"], 3)
        self.assertEqual(abandonment["host_attestation"]["session_id"], "luna-3")
        self.assertEqual((self.root / "src/example.py").read_bytes(), code)
        self.assertNotIn(run_id, adapter.leases)
        repeated = engine.dispatch("abandon", self._exhausted_abandon_payload(run_id))
        self.assertTrue(repeated["already_abandoned"])
        self.assertEqual(len(engine.store.read_events(run_id)), len(prior_events) + 1)
        next_run = start_run(engine)
        with self.assertRaises(EngineError) as exhausted:
            engine.dispatch("prepare", {**payload, "run_id": next_run})
        self.assertEqual(exhausted.exception.code, "retry_limit")

    def test_exhausted_failure_abandon_rejects_live_or_unattestable_child_without_mutation(self):
        from harness.runtime.codex_adapter import AdapterError
        engine, adapter, run_id, _ = self._exhausted_native_failure_fixture()
        events = engine.store.read_events(run_id)
        original = adapter.attest_session
        def active_child(session_id, role, **kwargs):
            return {**original(session_id, role, **kwargs), "agent_lifecycle": "running" if role == "implementer" else "completed"}
        def missing_child(session_id, role, **kwargs):
            if role == "implementer":
                raise AdapterError("host_session_missing", "Child log unavailable.")
            return original(session_id, role, **kwargs)
        for callback, expected in ((active_child, "agent_still_active"), (missing_child, "host_session_missing")):
            with self.subTest(expected=expected), patch.object(adapter, "attest_session", side_effect=callback):
                with self.assertRaises(EngineError) as blocked:
                    engine.dispatch("abandon", self._exhausted_abandon_payload(run_id))
                self.assertEqual(blocked.exception.code, expected)
            self.assertEqual(engine.store.read_events(run_id), events)
            self.assertIn(run_id, adapter.leases)

    def test_exhausted_failure_abandon_requires_owner_authorization_and_lease(self):
        engine, adapter, run_id, _ = self._exhausted_native_failure_fixture()
        payload = self._exhausted_abandon_payload(run_id)
        events = engine.store.read_events(run_id)
        for changed, expected in (({**payload, "owner": "wrong"}, "wrong_owner"),
                                  ({**payload, "authorization": {"actor": "user", "statement": "", "source": "conversation"}}, "invalid_input")):
            with self.assertRaises(EngineError) as blocked:
                engine.dispatch("abandon", changed)
            self.assertEqual(blocked.exception.code, expected)
        adapter.leases.remove(run_id)
        with self.assertRaises(EngineError) as no_lease:
            engine.dispatch("abandon", payload)
        self.assertEqual(no_lease.exception.code, "ownership_lease_missing")
        self.assertEqual(engine.store.read_events(run_id), events)

    def test_exhausted_failure_abandon_recovers_crash_after_event_without_reattesting_child(self):
        engine, adapter, run_id, _ = self._exhausted_native_failure_fixture()
        with patch.object(adapter, "release", side_effect=RuntimeError("crash before lease release")):
            with self.assertRaises(RuntimeError):
                engine.dispatch("abandon", self._exhausted_abandon_payload(run_id))
        with patch.object(adapter, "attest_session", side_effect=AssertionError("Already abandoned; do not require terminal child log again.")):
            result = engine.dispatch("abandon", self._exhausted_abandon_payload(run_id))
        self.assertTrue(result["already_abandoned"])
        self.assertNotIn(run_id, adapter.leases)
        self.assertEqual(sum(e["event"] == "abandoned" for e in engine.store.read_events(run_id)), 1)


if __name__ == "__main__":
    unittest.main()
