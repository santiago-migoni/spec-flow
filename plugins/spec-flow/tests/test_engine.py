"""Document approval controller: initialization, approval chain, and invalidation."""

import json
import tempfile
import unittest
from pathlib import Path

from harness.runtime.contracts import document_digest
from harness.runtime.engine import Engine, EngineError
from helpers import approve_release, make_project


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.docs = make_project(self.root)
        self.engine = Engine(self.root)

    def tearDown(self):
        self.temp.cleanup()

    def approve(self, name):
        return self.engine.dispatch("approve", {
            "path": self.docs[name].resolve().relative_to(self.root).as_posix(),
            "actor": "user",
            "statement": "I approve this document.",
            "source": "conversation",
        })

    def _draft_constitution(self):
        self.engine.dispatch("initialize", {})
        path = self.docs["constitution"]
        path.write_text(path.read_text().replace("revision: R00\n", "revision: R00\nstatus: draft\n", 1))
        return path

    def test_approve_sets_header_status_without_changing_the_digest(self):
        path = self._draft_constitution()
        relative = path.relative_to(self.root).as_posix()
        before = self.engine.dispatch("digest", {"path": relative})["digest"]
        result = self.approve("constitution")
        self.assertTrue(result["status_written"])
        self.assertIn("status: approved\n", path.read_text())
        self.assertNotIn("status: draft", path.read_text())
        self.assertEqual(result["digest"], before)
        self.assertNotIn("warning", self.engine.dispatch("validate", {"path": relative}))

    def test_approve_adds_missing_status_and_retry_keeps_the_receipt(self):
        self.engine.dispatch("initialize", {})
        path = self.docs["constitution"]
        first = self.approve("constitution")
        second = self.approve("constitution")
        self.assertIn("status: approved\n", path.read_text())
        self.assertTrue(second["already_approved"])
        self.assertFalse(second["status_written"])
        self.assertEqual(first["digest"], second["digest"])

    def test_validate_warns_when_status_is_approved_but_the_document_changed(self):
        path = self._draft_constitution()
        self.approve("constitution")
        path.write_text(path.read_text().replace("Approved source decision.", "Changed decision."))
        relative = path.relative_to(self.root).as_posix()
        self.assertIn("warning", self.engine.dispatch("validate", {"path": relative}))

    def test_initialize_writes_minimal_config_without_profiles_or_runs(self):
        result = self.engine.dispatch("initialize", {})
        config = json.loads((self.root / ".spec-flow" / "config.json").read_text())
        self.assertEqual(result["status"], "initialized")
        self.assertEqual(config, {"schema_version": 1})
        self.assertFalse((self.root / ".spec-flow" / "runs").exists())
        self.assertIn("/lock", (self.root / ".spec-flow" / ".gitignore").read_text())

    def test_initialize_is_idempotent(self):
        self.engine.dispatch("initialize", {})
        result = self.engine.dispatch("initialize", {})
        self.assertTrue(result["already_initialized"])

    def test_uninitialized_project_rejects_approval(self):
        with self.assertRaises(EngineError) as ctx:
            self.approve("constitution")
        self.assertEqual(ctx.exception.code, "uninitialized")

    def test_approval_chain_follows_strategy_then_release_order(self):
        self.engine.dispatch("initialize", {})
        self.assertFalse(self.engine.dispatch("gate", {"path": ".specs/roadmap.md"})["ready"])
        self.approve("constitution")
        self.approve("roadmap")
        self.assertTrue(self.engine.dispatch("gate", {"path": ".specs/release-v1.2.3/spec.md"})["ready"])
        self.approve("spec")
        self.approve("plan")
        self.assertTrue(self.engine.dispatch("gate", {"path": ".specs/release-v1.2.3/tasks.md"})["ready"])

    def test_spec_is_blocked_until_roadmap_is_approved(self):
        self.engine.dispatch("initialize", {})
        self.approve("constitution")
        with self.assertRaises(EngineError) as ctx:
            self.engine.dispatch("approve", {
                "path": self.docs["spec"].resolve().relative_to(self.root).as_posix(),
                "actor": "user", "statement": "Approve spec.", "source": "conversation"})
        self.assertEqual(ctx.exception.code, "dependency_not_approved")

    def test_approval_is_idempotent_for_identical_receipt(self):
        self.engine.dispatch("initialize", {})
        first = self.approve("constitution")
        second = self.engine.dispatch("approve", {
            "path": ".specs/constitution.md", "actor": "user",
            "statement": "I approve this document.", "source": "conversation"})
        self.assertTrue(second["already_approved"])
        self.assertEqual(first["digest"], second["digest"])

    def test_editing_roadmap_invalidates_release_approvals(self):
        self.engine.dispatch("initialize", {})
        approve_release(self.engine, self.docs)
        self.assertTrue(self.engine.dispatch("gate", {"path": ".specs/release-v1.2.3/tasks.md"})["ready"])
        source = self.docs["roadmap"]
        source.write_text(source.read_text().replace("Approved source decision.", "Changed roadmap decision."))
        gate = self.engine.dispatch("gate", {"path": ".specs/release-v1.2.3/tasks.md"})
        self.assertFalse(gate["ready"])
        self.assertTrue(any("roadmap.md" in item for item in [row["reason"] for row in gate["invalid_prerequisites"]]))

    def test_digest_matches_document_bytes(self):
        result = self.engine.dispatch("digest", {"path": ".specs/constitution.md"})
        self.assertEqual(result["digest"], document_digest(self.docs["constitution"]))

    def test_validate_accepts_valid_release(self):
        result = self.engine.dispatch("validate", {"release": "1.2.3"})
        self.assertTrue(result["valid"])
        self.assertEqual(result["documents"], ["spec", "plan", "tasks"])

    def test_retired_execution_operations_are_rejected(self):
        self.engine.dispatch("initialize", {})
        for operation in ("start", "authorize", "prepare", "review", "close", "takeover", "complete", "status", "configure-profiles"):
            with self.subTest(operation=operation):
                with self.assertRaises(EngineError) as ctx:
                    self.engine.dispatch(operation, {})
                self.assertEqual(ctx.exception.code, "unknown_operation")

    def test_new_plan_is_blocked_until_spec_is_approved(self):
        self.engine.dispatch("initialize", {})
        self.approve("constitution")
        self.approve("roadmap")
        self.docs["plan"].unlink()
        with self.assertRaises(EngineError) as ctx:
            self.engine.dispatch("hook-check", {"paths": [".specs/release-v1.2.3/plan.md"]})
        self.assertEqual(ctx.exception.code, "dependency_not_approved")
        self.approve("spec")
        self.assertTrue(self.engine.dispatch("hook-check", {"paths": [".specs/release-v1.2.3/plan.md"]})["allowed"])

    def test_missing_prerequisite_is_reported_as_missing_approval(self):
        self.engine.dispatch("initialize", {})
        self.approve("constitution")
        self.docs["roadmap"].unlink()
        gate = self.engine.dispatch("gate", {"phase": "spec"})
        self.assertFalse(gate["ready"])
        self.assertEqual(gate["missing_approvals"], [".specs/roadmap.md"])
        self.assertEqual(gate["invalid_prerequisites"], [])
        self.docs["spec"].unlink()
        with self.assertRaises(EngineError) as ctx:
            self.engine.dispatch("hook-check", {"paths": [".specs/release-v1.2.3/spec.md"]})
        self.assertEqual(ctx.exception.code, "dependency_not_approved")
        self.assertIn("missing", str(ctx.exception))

    def test_text_after_generated_block_names_the_fix(self):
        self.engine.dispatch("initialize", {})
        constitution = self.docs["constitution"]
        constitution.write_text(constitution.read_text() + "\n<!-- spec-flow:generated:start -->\nProgress is maintained by the Spec-Flow harness.\n<!-- spec-flow:generated:end -->\n", encoding="utf-8")
        self.approve("constitution")
        self.approve("roadmap")
        constitution.write_text(constitution.read_text() + "\nTexto agregado despues del bloque.\n", encoding="utf-8")
        gate = self.engine.dispatch("gate", {"phase": "spec"})
        reasons = [row["reason"] for row in gate["invalid_prerequisites"]]
        self.assertTrue(any("move any text" in reason for reason in reasons), reasons)

    def test_legacy_numbered_directory_requires_migration(self):
        (self.root / ".specs" / "001-demo").mkdir()
        with self.assertRaises(EngineError) as ctx:
            self.engine.dispatch("initialize", {})
        self.assertEqual(ctx.exception.code, "migration_required")


if __name__ == "__main__":
    unittest.main()
