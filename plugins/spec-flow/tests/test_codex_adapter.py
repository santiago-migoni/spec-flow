import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from harness.runtime.codex_adapter import AdapterError, NativeCodexAdapter


class CodexAdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.root = self.base / "project"
        self.root.mkdir()
        self.sessions = self.base / "codex" / "sessions" / "2026" / "10" / "14"
        self.sessions.mkdir(parents=True)
        self.adapter = NativeCodexAdapter(self.root)
        self.owner = "owner-1111"
        self.child = "child-2222"

    def tearDown(self):
        self.temp.cleanup()

    def write_session(self, ident, *, model="gpt-6-sol", effort="high", parent=None, agent_path=None,
                      events=("task_started", "task_complete"), marker=None, malformed=None, metadata_source=None):
        source = {}
        if parent is not None:
            source = {"subagent": {"thread_spawn": {"parent_thread_id": parent, "agent_path": agent_path}}}
        if metadata_source is not None:
            source = metadata_source
        rows = [
            {"type": "session_meta", "payload": {"id": ident, "source": source}},
            {"type": "turn_context", "timestamp": "2026-10-14T12:00:00Z", "payload": {"model": model, "collaboration_mode": {"settings": {"reasoning_effort": effort}}}},
        ]
        if marker:
            rows.append({"type": "response_item", "payload": {"type": "message", "role": "user", "content": [{"text": marker}]}})
        rows.extend({"type": "event_msg", "payload": {"type": kind}} for kind in events)
        path = self.sessions / ("rollout-2026-10-14T12-00-00-" + ident + ".jsonl")
        with path.open("w", encoding="utf-8") as stream:
            for row in rows:
                stream.write(json.dumps(row) + "\n")
            if malformed:
                stream.write(malformed)
        return path

    def test_capability_report_requires_native_probes_and_owner_attestation(self):
        self.write_session(self.owner)
        report = {"inventory_reference": "native inventory snapshot ref",
                  "operations": {name: True for name in self.adapter.OPERATIONS},
                  "probe_evidence": {name: "native probe result" for name in self.adapter.OPERATIONS}}
        with patch.dict(os.environ, {"CODEX_HOME": str(self.base / "codex")}):
            result = self.adapter.capabilities(report, self.owner)
            self.assertEqual(result["owner_session"]["model"], "gpt-6-sol")
            self.assertTrue(result["owner_session"]["record_hashes"]["session_meta"])
            self.assertTrue(result["owner_session"]["attestation_sha256"])
            report["operations"]["spawn_agent"] = False
            with self.assertRaises(AdapterError) as ctx:
                self.adapter.capabilities(report, self.owner)
        self.assertEqual(ctx.exception.code, "native_capability_unavailable")

    def test_every_turn_context_must_match_explicit_profile(self):
        path = self.write_session(self.owner)
        rows = path.read_text(encoding="utf-8") + json.dumps({"type": "turn_context", "payload": {"model": "gpt-6-astra", "collaboration_mode": {"settings": {"reasoning_effort": "high"}}}}) + "\n"
        path.write_text(rows, encoding="utf-8")
        with patch.dict(os.environ, {"CODEX_HOME": str(self.base / "codex")}):
            with self.assertRaises(AdapterError) as ctx:
                self.adapter.attest_session(self.owner, "orchestrator")
        self.assertEqual(ctx.exception.code, "host_profile_mismatch")

    def test_child_must_match_parent_path_packet_marker_and_terminal_status(self):
        marker = "SPEC_FLOW_PACKET_SHA256=abc123"
        self.write_session(self.child, model="gpt-6-luna", parent=self.owner, agent_path="/root/T-001", marker=marker)
        with patch.dict(os.environ, {"CODEX_HOME": str(self.base / "codex")}):
            result = self.adapter.attest_session(self.child, "implementer", parent_session=self.owner,
                                                 agent_path="/root/T-001", task_marker=marker,
                                                 after="2026-10-14T11:59:00Z", require_finished=True)
            self.assertEqual(result["agent_lifecycle"], "completed")
            with self.assertRaises(AdapterError) as ctx:
                self.adapter.attest_session(self.child, "implementer", parent_session="other",
                                            agent_path="/root/T-001", task_marker=marker)
        self.assertEqual(ctx.exception.code, "host_parent_mismatch")

    def write_spawn(self, owner, task_name, agent_path, *, output_path=None, output_error=None, role="implementer"):
        parent_path = self.sessions / ("rollout-2026-10-14T12-00-00-" + owner + ".jsonl")
        call_id = "call-spawn-" + task_name
        arguments = {"task_name": task_name,
                     "model": "gpt-6-sol" if role == "reviewer" else "gpt-6-luna", "reasoning_effort": "high",
                     "fork_turns": "none", "message": "encrypted-prompt-payload"}
        call = {"type": "response_item", "timestamp": "2026-10-14T12:00:01Z",
                "payload": {"type": "function_call", "namespace": "collaboration", "name": "spawn_agent",
                            "call_id": call_id, "arguments": json.dumps(arguments)}}
        output_value = {"task_name": output_path or agent_path}
        if output_error:
            output_value["error"] = output_error
        output = {"type": "response_item", "timestamp": "2026-10-14T12:00:02Z",
                  "payload": {"type": "function_call_output", "call_id": call_id,
                              "output": json.dumps(output_value)}}
        with parent_path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(call) + "\n")
            stream.write(json.dumps(output) + "\n")
        return call_id

    def test_encrypted_native_prompt_uses_hash_bearing_spawn_name_and_linked_output(self):
        packet_hash = "a" * 64
        marker = "SPEC_FLOW_PACKET_SHA256=" + packet_hash
        agent_path = "/root/T-001"
        self.write_session(self.owner)
        task_name = self.adapter.native_task_name("implementer", marker)
        self.write_spawn(self.owner, task_name, agent_path)
        self.write_session(self.child, model="gpt-6-luna", parent=self.owner, agent_path=agent_path, marker=None)
        with patch.dict(os.environ, {"CODEX_HOME": str(self.base / "codex")}):
            result = self.adapter.attest_session(self.child, "implementer", parent_session=self.owner,
                                                 agent_path=agent_path, task_marker=marker,
                                                 after="2026-10-14T11:59:00Z")
        self.assertEqual(result["packet_marker_source"], "native_spawn_task_name")
        self.assertTrue(result["record_hashes"]["delegation"])

    def test_phase_review_marker_binds_full_run_phase_and_tree_in_native_name(self):
        marker = "SPEC_FLOW_PHASE_REVIEW=run-9/PH03/" + ("d" * 40)
        agent_path = "/root/review-PH03"
        self.write_session(self.owner)
        name = self.adapter.native_task_name("reviewer", marker)
        self.write_spawn(self.owner, name, agent_path, role="reviewer")
        self.write_session(self.child, parent=self.owner, agent_path=agent_path, marker=None)
        with patch.dict(os.environ, {"CODEX_HOME": str(self.base / "codex")}):
            result = self.adapter.attest_session(self.child, "reviewer", parent_session=self.owner,
                                                 agent_path=agent_path, task_marker=marker)
        self.assertEqual(result["packet_marker_source"], "native_spawn_task_name")

    def test_encrypted_native_spawn_output_must_return_exact_child_path(self):
        marker = "SPEC_FLOW_PACKET_SHA256=" + ("e" * 64)
        agent_path = "/root/T-001"
        self.write_session(self.owner)
        self.write_spawn(self.owner, self.adapter.native_task_name("implementer", marker),
                         agent_path, output_path=agent_path + "-prefix")
        self.write_session(self.child, model="gpt-6-luna", parent=self.owner, agent_path=agent_path, marker=None)
        with patch.dict(os.environ, {"CODEX_HOME": str(self.base / "codex")}):
            with self.assertRaises(AdapterError) as ctx:
                self.adapter.attest_session(self.child, "implementer", parent_session=self.owner,
                                            agent_path=agent_path, task_marker=marker)
        self.assertEqual(ctx.exception.code, "host_task_marker_missing")

    def test_encrypted_native_spawn_error_output_cannot_bind(self):
        marker = "SPEC_FLOW_PACKET_SHA256=" + ("f" * 64)
        agent_path = "/root/T-001"
        self.write_session(self.owner)
        self.write_spawn(self.owner, self.adapter.native_task_name("implementer", marker), agent_path,
                         output_error="spawn failed")
        self.write_session(self.child, model="gpt-6-luna", parent=self.owner, agent_path=agent_path, marker=None)
        with patch.dict(os.environ, {"CODEX_HOME": str(self.base / "codex")}):
            with self.assertRaises(AdapterError) as ctx:
                self.adapter.attest_session(self.child, "implementer", parent_session=self.owner,
                                            agent_path=agent_path, task_marker=marker)
        self.assertEqual(ctx.exception.code, "host_task_marker_missing")

    def test_encrypted_native_prompt_rejects_wrong_or_unlinked_spawn_evidence(self):
        packet_hash = "b" * 64
        marker = "SPEC_FLOW_PACKET_SHA256=" + packet_hash
        agent_path = "/root/T-001"
        self.write_session(self.owner)
        wrong_marker = "SPEC_FLOW_PACKET_SHA256=" + ("c" * 64)
        self.write_spawn(self.owner, self.adapter.native_task_name("implementer", wrong_marker), agent_path)
        self.write_session(self.child, model="gpt-6-luna", parent=self.owner, agent_path=agent_path, marker=None)
        with patch.dict(os.environ, {"CODEX_HOME": str(self.base / "codex")}):
            with self.assertRaises(AdapterError) as ctx:
                self.adapter.attest_session(self.child, "implementer", parent_session=self.owner,
                                            agent_path=agent_path, task_marker=marker,
                                            after="2026-10-14T11:59:00Z")
        self.assertEqual(ctx.exception.code, "host_task_marker_missing")

    def test_packet_marker_in_agent_output_does_not_attest_delegated_prompt(self):
        marker = "SPEC_FLOW_PACKET_SHA256=abc123"
        self.write_session(self.owner)
        path = self.write_session(self.child, model="gpt-6-luna", parent=self.owner, agent_path="/root/T-001", marker=None)
        rows = path.read_text(encoding="utf-8") + json.dumps({"type": "response_item", "payload": {"type": "message", "role": "assistant", "content": marker}}) + "\n"
        path.write_text(rows, encoding="utf-8")
        with patch.dict(os.environ, {"CODEX_HOME": str(self.base / "codex")}):
            with self.assertRaises(AdapterError) as ctx:
                self.adapter.attest_session(self.child, "implementer", parent_session=self.owner,
                                            agent_path="/root/T-001", task_marker=marker)
        self.assertEqual(ctx.exception.code, "host_task_marker_missing")

    def test_no_spawn_reconciliation_requires_current_empty_native_inventory(self):
        self.write_session(self.owner)
        task_state = {"packet_sha256": "abc123", "prepared_at": "2026-10-14T11:59:00Z", "attempt_baseline": {}}
        inventory = {"owner_session": self.owner, "inventory_reference": "list_agents result ref",
                     "checked_at": "2026-10-14T12:01:00Z", "agents": []}
        with patch.dict(os.environ, {"CODEX_HOME": str(self.base / "codex")}):
            result = self.adapter.attest_no_spawn(self.owner, task_state, inventory)
            self.assertEqual(result["packet_marker"], "SPEC_FLOW_PACKET_SHA256=abc123")
            with self.assertRaises(AdapterError) as ctx:
                self.adapter.attest_no_spawn(self.owner, task_state, {**inventory, "agents": [{"agent_path": "/root/T-001", "status": "active"}]})
        self.assertEqual(ctx.exception.code, "native_agent_still_active")

    def test_no_spawn_accepts_foreign_non_thread_metadata_without_claiming_a_child(self):
        # F-02: an unrelated compact/service session is not a thread child and
        # must not crash the global scan or confer any delegation authority.
        self.write_session(self.owner)
        task_state = {"packet_sha256": "abc123", "prepared_at": "2026-10-14T11:59:00Z", "attempt_baseline": {}}
        inventory = {"owner_session": self.owner, "inventory_reference": "actual empty fixture inventory",
                     "checked_at": "2026-10-14T12:01:00Z", "agents": []}
        with patch.dict(os.environ, {"CODEX_HOME": str(self.base / "codex")}):
            for subagent in ("compact", None, [], 7):
                with self.subTest(subagent=subagent):
                    self.write_session("foreign-service", metadata_source={"subagent": subagent})
                    result = self.adapter.attest_no_spawn(self.owner, task_state, inventory)
                    self.assertEqual(result["child_record_hashes"], [])
                    self.assertEqual(result["packet_marker"], "SPEC_FLOW_PACKET_SHA256=abc123")

    def test_non_thread_metadata_cannot_attest_required_child_lineage(self):
        self.write_session(self.child, model="gpt-6-luna", metadata_source={"subagent": "compact"})
        with patch.dict(os.environ, {"CODEX_HOME": str(self.base / "codex")}):
            with self.assertRaises(AdapterError) as ctx:
                self.adapter.attest_session(self.child, "implementer", parent_session=self.owner,
                                            agent_path="/root/T-001")
        self.assertEqual(ctx.exception.code, "host_parent_mismatch")

    def test_foreign_non_thread_metadata_does_not_hide_own_children(self):
        self.write_session("foreign-service", metadata_source={"subagent": "compact"})
        self.write_session(self.owner)
        marker = "SPEC_FLOW_PACKET_SHA256=abc123"
        self.write_session(self.child, model="gpt-6-luna", parent=self.owner, agent_path="/root/T-001", marker=marker)
        task_state = {"packet_sha256": "abc123", "prepared_at": "2026-10-14T11:59:00Z", "attempt_baseline": {}}
        base = {"owner_session": self.owner, "inventory_reference": "current fixture inventory",
                "checked_at": "2026-10-14T12:01:00Z"}
        cases = (([], "native_inventory_incomplete"),
                 ([{"agent_path": "/root/T-001", "status": "active"}], "native_agent_still_active"),
                 ([{"agent_path": "/root/T-001", "status": "completed"}], "task_agent_found_bind_before_reconcile"))
        with patch.dict(os.environ, {"CODEX_HOME": str(self.base / "codex")}):
            for agents, expected in cases:
                with self.subTest(agents=agents):
                    with self.assertRaises(AdapterError) as ctx:
                        self.adapter.attest_no_spawn(self.owner, task_state, {**base, "agents": agents})
                    self.assertEqual(ctx.exception.code, expected)

    def test_packet_child_found_during_no_spawn_inspection_requires_late_binding(self):
        self.write_session(self.owner)
        marker = "SPEC_FLOW_PACKET_SHA256=abc123"
        self.write_session(self.child, model="gpt-6-luna", parent=self.owner, agent_path="/root/T-001", marker=marker)
        task_state = {"packet_sha256": "abc123", "prepared_at": "2026-10-14T11:59:00Z", "attempt_baseline": {}}
        inventory = {"owner_session": self.owner, "inventory_reference": "list_agents result ref",
                     "checked_at": "2026-10-14T12:01:00Z", "agents": [{"agent_path": "/root/T-001", "status": "completed"}]}
        with patch.dict(os.environ, {"CODEX_HOME": str(self.base / "codex")}):
            with self.assertRaises(AdapterError) as ctx:
                self.adapter.attest_no_spawn(self.owner, task_state, inventory)
        self.assertEqual(ctx.exception.code, "task_agent_found_bind_before_reconcile")

    def test_no_spawn_reconciliation_rejects_unattributed_new_child(self):
        self.write_session("foreign-service", metadata_source={"subagent": "compact"})
        self.write_session(self.owner)
        self.write_session(self.child, model="gpt-6-luna", parent=self.owner, agent_path="/root/unrelated", marker=None)
        task_state = {"packet_sha256": "abc123", "prepared_at": "2026-10-14T11:59:00Z", "attempt_baseline": {}}
        inventory = {"owner_session": self.owner, "inventory_reference": "list_agents result ref",
                     "checked_at": "2026-10-14T12:01:00Z", "agents": [{"agent_path": "/root/unrelated", "status": "completed"}]}
        with patch.dict(os.environ, {"CODEX_HOME": str(self.base / "codex")}):
            with self.assertRaises(AdapterError) as ctx:
                self.adapter.attest_no_spawn(self.owner, task_state, inventory)
        self.assertEqual(ctx.exception.code, "native_child_unattributed")

    def test_malformed_or_partial_log_fails_closed(self):
        path = self.write_session(self.owner)
        with path.open("a", encoding="utf-8") as stream:
            stream.write("{bad json}\n")
        with patch.dict(os.environ, {"CODEX_HOME": str(self.base / "codex")}):
            with self.assertRaises(AdapterError) as ctx:
                self.adapter.attest_session(self.owner, "orchestrator")
        self.assertEqual(ctx.exception.code, "host_log_corrupt")

    def test_primary_checkout_cannot_acquire_production_run_lease(self):
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        self.adapter = NativeCodexAdapter(self.root)
        with self.assertRaises(AdapterError) as ctx:
            self.adapter.acquire("run-1", "v1.2.3", self.owner)
        self.assertEqual(ctx.exception.code, "linked_worktree_required")

    def test_linked_worktree_shares_persistent_repository_lease(self):
        primary = self.base / "primary"
        linked = self.base / "linked"
        linked2 = self.base / "linked2"
        primary.mkdir()
        subprocess.run(["git", "init", "-q", str(primary)], check=True)
        subprocess.run(["git", "-C", str(primary), "-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "--allow-empty", "-qm", "init"], check=True)
        subprocess.run(["git", "-C", str(primary), "worktree", "add", "-q", "-b", "codex/test", str(linked)], check=True)
        subprocess.run(["git", "-C", str(primary), "worktree", "add", "-q", "-b", "codex/test2", str(linked2)], check=True)
        first = NativeCodexAdapter(linked)
        second = NativeCodexAdapter(linked2)
        first.acquire("run-1", "v1.2.3", self.owner)
        with self.assertRaises(AdapterError) as ctx:
            second.acquire("run-2", "v1.2.4", "owner-3333")
        self.assertEqual(ctx.exception.code, "run_already_active")
        completed_state = {"run_id": "run-1", "release": "v1.2.3", "worktree": str(linked),
                           "owner": self.owner, "status": "completed"}
        first.release(completed_state)
        first.release(completed_state)
        self.assertFalse((first._git_directories()[1] / "spec-flow-active-controller.json").exists())

    def test_second_takeover_attests_child_against_its_original_parent(self):
        primary = self.base / "primary"
        linked = self.base / "linked"
        primary.mkdir()
        subprocess.run(["git", "init", "-q", str(primary)], check=True)
        subprocess.run(["git", "-C", str(primary), "-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "--allow-empty", "-qm", "init"], check=True)
        subprocess.run(["git", "-C", str(primary), "worktree", "add", "-q", "-b", "codex/second-takeover", str(linked)], check=True)
        adapter = NativeCodexAdapter(linked)
        original_owner = "owner-1111"
        previous_owner = "owner-3333"
        next_owner = "owner-4444"
        child_id = "child-5555"
        marker = "SPEC_FLOW_PACKET_SHA256=packet-hash"
        self.write_session(original_owner, events=("task_started", "task_complete"))
        self.write_session(previous_owner, events=("task_started", "task_complete"))
        self.write_session(next_owner, events=("task_started",))
        self.write_session(child_id, model="gpt-6-luna", parent=original_owner,
                           agent_path="/root/T-001", marker=marker)
        state = {"run_id": "run-second-takeover", "release": "1.2.3", "owner": previous_owner,
                 "status": "interrupted", "active_task": "T-001", "tasks": {"T-001": {
                     "packet_sha256": "packet-hash", "prepared_at": "2026-10-14T11:59:00Z",
                     "agent": {"session_id": child_id, "agent_path": "/root/T-001",
                               "parent_session": original_owner}}}}
        adapter.acquire(state["run_id"], state["release"], previous_owner)
        with patch.dict(os.environ, {"CODEX_HOME": str(self.base / "codex")}):
            outcome = adapter.takeover(state, next_owner)
        self.assertEqual(outcome["native_agent"]["parent_session"], original_owner)

    def test_takeover_retry_recovers_lease_written_before_run_event(self):
        primary = self.base / "primary"
        linked = self.base / "linked"
        primary.mkdir()
        subprocess.run(["git", "init", "-q", str(primary)], check=True)
        subprocess.run(["git", "-C", str(primary), "-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "--allow-empty", "-qm", "init"], check=True)
        subprocess.run(["git", "-C", str(primary), "worktree", "add", "-q", "-b", "codex/takeover", str(linked)], check=True)
        adapter = NativeCodexAdapter(linked)
        self.write_session(self.owner, events=("task_started", "task_complete"))
        new_owner = "owner-3333"
        self.write_session(new_owner, events=("task_started",))
        state = {"run_id": "run-takeover", "release": "1.2.3", "owner": self.owner,
                 "status": "interrupted", "active_task": None, "tasks": {}}
        adapter.acquire(state["run_id"], state["release"], self.owner)
        with patch.dict(os.environ, {"CODEX_HOME": str(self.base / "codex")}):
            first = adapter.takeover(state, new_owner)
            self.assertEqual(first["new_owner"], new_owner)
            # Simulate a crash after registry replacement and before
            # Engine._takeover appends ownership_transferred.
            second = adapter.takeover(state, new_owner)
        self.assertEqual(second["new_owner"], new_owner)
        registry = adapter._git_directories()[1] / "spec-flow-active-controller.json"
        self.assertEqual(json.loads(registry.read_text(encoding="utf-8")),
                         {"run_id": state["run_id"], "release": state["release"],
                          "worktree": str(linked.resolve()), "owner": new_owner})


if __name__ == "__main__":
    unittest.main()
