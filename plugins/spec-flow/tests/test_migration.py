import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from harness.runtime.engine import Engine, EngineError
from harness.runtime.contracts import document_digest
from helpers import contract, write_document, task
from harness.runtime.migration import Migration


def canonical_docs(root, release="v2.0.0"):
    specs = Path(root) / ".specs"
    constitution = write_document(specs / "constitution.md", contract("constitution", "CONSTITUTION"))
    roadmap = write_document(
        specs / "roadmap.md",
        contract("roadmap", "ROADMAP", depends_on=[{"path": ".specs/constitution.md", "digest": document_digest(constitution)}],
                 releases=[{"version": release, "objective": "Deliver the migrated release.", "status": "planned"}]),
    )
    release_dir = specs / ("release-" + release)
    spec = write_document(
        release_dir / "spec.md",
        contract("spec", "SPEC-2.0.0", depends_on=[{"path": ".specs/roadmap.md", "digest": document_digest(roadmap)}],
                 acceptance=[{"id": "AC-001", "description": "Migrated behavior works."}]),
    )
    plan = write_document(
        release_dir / "plan.md",
        contract("plan", "PLAN-2.0.0", depends_on=[{"path": ".specs/{}/spec.md".format(release_dir.name), "digest": document_digest(spec)}],
                 phases=[{"id": "PH-01", "description": "Implement migrated behavior.", "depends_on": []}]),
    )
    write_document(
        release_dir / "tasks.md",
        contract("tasks", "TASKS-2.0.0", depends_on=[{"path": ".specs/{}/plan.md".format(release_dir.name), "digest": document_digest(plan)}],
                 tasks=[task(files=["src/example.py"])]),
    )
    (Path(root) / "src").mkdir(parents=True, exist_ok=True)
    (Path(root) / "src/example.py").write_text("# baseline\n", encoding="utf-8")
    return specs


def git_commit(root):
    def run(*args):
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)
    run("init", "-q")
    run("config", "user.email", "migration-test@example.invalid")
    run("config", "user.name", "Migration Test")
    run("add", ".")
    run("commit", "-qm", "legacy baseline")
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True, capture_output=True, text=True).stdout.strip()


class MigrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "project"
        self.candidate_root = Path(self.temp.name) / "candidate"
        self.root.mkdir()
        self.candidate_root.mkdir()
        specs = self.root / ".specs"
        specs.mkdir()
        write_document(specs / "constitution.md", contract("constitution", "CONSTITUTION"))
        constitution = specs / "constitution.md"
        write_document(specs / "roadmap.md", contract(
            "roadmap", "ROADMAP", depends_on=[{"path": ".specs/constitution.md", "digest": document_digest(constitution)}],
            releases=[{"version": "v2.0.0", "objective": "Deliver the migrated release.", "status": "planned"}],
        ))
        legacy = specs / "001-demo"
        legacy.mkdir()
        (legacy / "spec.md").write_text("# Old approved specification\n\n- [x] T-001 Complete\n", encoding="utf-8")
        (legacy / "tasks.md").write_text("# Tasks\n\n- [x] T-001\n", encoding="utf-8")
        self.legacy = legacy
        self.candidate_specs = canonical_docs(self.candidate_root)
        # Canonical candidate references the exact shared strategic sources.
        candidate_roadmap = json.loads((self.candidate_specs / "roadmap.md").read_text().split("```spec-flow\n")[1].split("\n```")[0])
        current_roadmap = specs / "roadmap.md"
        write_document(current_roadmap, candidate_roadmap)
        (self.candidate_specs / "constitution.md").unlink()
        (self.candidate_specs / "roadmap.md").unlink()
        shutil.rmtree(self.candidate_root / "src")
        self.head = git_commit(self.root)
        self.engine = Engine(self.root)
        self.mapping = [{"legacy": ".specs/001-demo", "release": "v2.0.0"}]

    def tearDown(self):
        self.temp.cleanup()

    def preview(self, *, mapping=None, candidate=None, imports=None):
        payload = {"mapping": mapping or self.mapping, "candidate_dir": str(candidate or self.candidate_root)}
        if imports is not None:
            payload["imports"] = imports
        return self.engine.dispatch("migrate-preview", payload)

    def apply(self, preview, *, candidate=None):
        return self.engine.dispatch("migrate-apply", {
            "manifest": preview["manifest"], "digest": preview["digest"],
            "candidate_dir": str(candidate or self.candidate_root),
            "authorization": {"actor": "user", "statement": "Apply this migration.", "source": "conversation"},
        })

    def test_preview_is_read_only_and_deterministic(self):
        before = {p.relative_to(self.root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in self.root.rglob("*") if p.is_file()}
        one = self.preview()
        two = self.preview()
        after = {p.relative_to(self.root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(one, two)
        self.assertEqual(before, after)
        self.assertFalse((self.root / ".spec-flow").exists())

    def test_preview_requires_every_legacy_directory_mapped(self):
        (self.root / ".specs/002-other").mkdir()
        (self.root / ".specs/002-other/spec.md").write_text("unmapped\n")
        git_commit(self.root)
        with self.assertRaises(EngineError) as ctx:
            self.preview()
        self.assertEqual(ctx.exception.code, "migration_mapping_required")

    def test_preview_rejects_duplicate_release_and_candidate_collision(self):
        with self.assertRaises(EngineError) as ctx:
            self.preview(mapping=[*self.mapping, {"legacy": ".specs/001-copy", "release": "2.0.0"}])
        self.assertEqual(ctx.exception.code, "migration_mapping_invalid")
        collision = self.root / ".specs/release-v2.0.0/spec.md"
        collision.parent.mkdir(parents=True)
        collision.write_text("collision\n")
        git_commit(self.root)
        with self.assertRaises(EngineError) as ctx:
            self.preview()
        self.assertEqual(ctx.exception.code, "migration_collision")

    def test_preview_rejects_invalid_candidate_overlay(self):
        (self.candidate_specs / "release-v2.0.0/spec.md").write_text("not a contract\n")
        with self.assertRaises(EngineError) as ctx:
            self.preview()
        self.assertEqual(ctx.exception.code, "migration_candidate_invalid")

    def test_apply_rejects_stale_source_and_candidate(self):
        preview = self.preview()
        (self.legacy / "spec.md").write_text("concurrent source edit\n")
        with self.assertRaises(EngineError) as ctx:
            self.apply(preview)
        self.assertEqual(ctx.exception.code, "migration_source_stale")
        self.assertTrue(self.legacy.exists())
        (self.legacy / "spec.md").write_text("# Old approved specification\n\n- [x] T-001 Complete\n")
        git_commit(self.root)
        preview = self.preview()
        (self.candidate_specs / "release-v2.0.0/spec.md").write_text("changed candidate\n")
        with self.assertRaises(EngineError) as ctx:
            self.apply(preview)
        self.assertEqual(ctx.exception.code, "migration_candidate_stale")

    def test_apply_archives_sources_promotes_candidate_and_does_not_import_checkmarks(self):
        preview = self.preview()
        result = self.apply(preview)
        self.assertTrue(result["completed"])
        self.assertEqual(result["source_git_head"], self.head)
        self.assertFalse(self.legacy.exists())
        archive = self.root / ".spec-flow/legacy" / result["migration_id"] / "sources/001-demo"
        self.assertEqual((archive / "tasks.md").read_text(), "# Tasks\n\n- [x] T-001\n")
        self.assertTrue((self.root / ".specs/release-v2.0.0/tasks.md").is_file())
        self.assertEqual(self.engine.store.approvals(), [])
        self.assertTrue((self.root / ".spec-flow/config.json").is_file())
        self.assertTrue(self.engine.dispatch("migrate-resume", {"migration_id": result["migration_id"]})["completed"])

    def test_closed_mapping_archives_without_creating_release(self):
        result = self.apply(self.preview(mapping=[{"legacy": ".specs/001-demo", "archive": True}], candidate=str(self.candidate_root)))
        self.assertTrue(result["completed"])
        self.assertFalse((self.root / ".specs/release-v2.0.0").exists())
        self.assertTrue((self.root / ".spec-flow/legacy" / result["migration_id"] / "sources/001-demo/spec.md").is_file())

    def test_symlink_in_legacy_tree_is_rejected(self):
        target = self.root / "outside.txt"
        target.write_text("outside\n")
        (self.legacy / "linked.md").symlink_to(target)
        git_commit(self.root)
        with self.assertRaises(EngineError) as ctx:
            self.preview()
        self.assertEqual(ctx.exception.code, "migration_unsafe_source")

    def test_explicit_constitution_replacement_archives_old_strategy(self):
        old = self.root / ".specs/constitution.md"
        old.write_text("# Previous project purpose\n\nThe project serves existing users.\n", encoding="utf-8")
        roadmap = self.root / ".specs/roadmap.md"
        roadmap.unlink()
        new_constitution = write_document(self.candidate_specs / "constitution.md", contract("constitution", "CONSTITUTION"), "Approved source decision.")
        roadmap_path = write_document(self.candidate_specs / "roadmap.md", contract(
            "roadmap", "ROADMAP", depends_on=[{"path": ".specs/constitution.md", "digest": document_digest(new_constitution)}],
            releases=[{"version": "v2.0.0", "objective": "Deliver the migrated release.", "status": "planned"}],
        ))
        self.head = git_commit(self.root)
        equivalence = {"statement": "The user reviewed this strategy conversion.",
                       "source_excerpt": old.read_text(encoding="utf-8"),
                       "target_excerpt": new_constitution.read_text(encoding="utf-8")}
        preview = self.engine.dispatch("migrate-preview", {
            "mapping": self.mapping, "candidate_dir": str(self.candidate_root),
            "replacements": [{"path": ".specs/constitution.md", "source_sha256": hashlib.sha256(old.read_bytes()).hexdigest(), "equivalence": equivalence}],
        })
        result = self.apply(preview)
        archive = self.root / result["archive"] / "replacements/constitution.md"
        self.assertEqual(archive.read_text(), "# Previous project purpose\n\nThe project serves existing users.\n")
        self.assertIn("Approved source decision.", old.read_text())
        self.assertEqual(self.engine.store.approvals(), [])

    def test_changed_acceptance_cannot_inherit_historical_approval(self):
        source = self.legacy / "spec.md"
        target = self.candidate_specs / "release-v2.0.0/spec.md"
        shutil.copyfile(target, source)
        receipt_path = self.legacy / "approval.json"
        receipt = {"schema_version": 1, "kind": "spec-flow-approval-receipt",
                   "path": ".specs/001-demo/spec.md", "digest": hashlib.sha256(source.read_bytes()).hexdigest(),
                   "actor": "reviewer", "statement": "Approved the mapped specification.", "source": "legacy receipt"}
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
        data = json.loads(target.read_text().split("```spec-flow\n")[1].split("\n```")[0])
        data["acceptance"][0]["description"] = "A materially different acceptance decision."
        write_document(target, data)
        plan_path = self.candidate_specs / "release-v2.0.0/plan.md"
        plan_data = json.loads(plan_path.read_text().split("```spec-flow\n")[1].split("\n```")[0])
        plan_data["depends_on"][0]["digest"] = document_digest(target)
        write_document(plan_path, plan_data)
        tasks_path = self.candidate_specs / "release-v2.0.0/tasks.md"
        tasks_data = json.loads(tasks_path.read_text().split("```spec-flow\n")[1].split("\n```")[0])
        tasks_data["depends_on"][0]["digest"] = document_digest(plan_path)
        write_document(tasks_path, tasks_data)
        equivalence = {"statement": "The decision was structurally converted.",
                       "source_excerpt": source.read_text(encoding="utf-8"),
                       "target_excerpt": target.read_text(encoding="utf-8")}
        git_commit(self.root)
        preview = self.preview(imports={"approvals": [{"source": ".specs/001-demo/approval.json",
                                                        "target": ".specs/release-v2.0.0/spec.md",
                                                        "equivalence": equivalence}]})
        approval = preview["manifest"]["imports"]["approvals"][0]
        self.assertEqual(approval["status"], "pending")
        self.assertIn("changes decision", approval["reason"])

    def test_exact_historical_step_evidence_is_imported_and_credited_at_start(self):
        release_dir = self.candidate_specs / "release-v2.0.0"
        source_task_doc = self.legacy / "tasks.md"
        shutil.copyfile(release_dir / "tasks.md", source_task_doc)
        source_spec = self.legacy / "spec.md"
        shutil.copyfile(release_dir / "spec.md", source_spec)
        source_plan = self.legacy / "plan.md"
        shutil.copyfile(release_dir / "plan.md", source_plan)
        (self.root / "src").mkdir(exist_ok=True)
        (self.root / "src/example.py").write_text("# baseline\n", encoding="utf-8")
        receipt_path = self.legacy / "approval.json"
        receipt = {"schema_version": 1, "kind": "spec-flow-approval-receipt",
                   "path": ".specs/001-demo/spec.md", "digest": hashlib.sha256(source_spec.read_bytes()).hexdigest(),
                   "actor": "reviewer", "statement": "Approved the unchanged specification.", "source": "legacy receipt"}
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
        code_path = self.root / "src/example.py"
        code_files = {"src/example.py": hashlib.sha256(code_path.read_bytes()).hexdigest()}
        tasks = json.loads((release_dir / "tasks.md").read_text().split("```spec-flow\n")[1].split("\n```")[0])
        step = tasks["tasks"][0]["steps"][0]
        raw_evidence = {"schema_version": 1, "kind": "spec-flow-step-evidence", "task_id": "T-001",
                        "step_id": "T-001.001", "command": step["verification"]["command"],
                        "expected": step["verification"]["expected"],
                        "result": {"exit_code": 0, "output": "verification passed\n"},
                        "source_files": {".specs/001-demo/tasks.md": hashlib.sha256(source_task_doc.read_bytes()).hexdigest()},
                        "source_digests": {
                            ".specs/001-demo/spec.md": document_digest(source_spec),
                            ".specs/001-demo/plan.md": document_digest(source_plan),
                            ".specs/001-demo/tasks.md": document_digest(source_task_doc),
                            ".specs/roadmap.md": document_digest(self.root / ".specs/roadmap.md"),
                            ".specs/constitution.md": document_digest(self.root / ".specs/constitution.md"),
                        },
                        "code_files": code_files, "code_hash": hashlib.sha256(json.dumps(code_files, sort_keys=True, separators=(",", ":")).encode()).hexdigest()}
        evidence_path = self.legacy / "step-evidence.json"
        evidence_path.write_text(json.dumps(raw_evidence), encoding="utf-8")
        approval_equivalence = {"statement": "The original receipt covers this unchanged specification.",
                                "source_excerpt": source_spec.read_text(encoding="utf-8"),
                                "target_excerpt": (release_dir / "spec.md").read_text(encoding="utf-8")}
        evidence_equivalence = {"statement": "This record maps to the identical approved task step.",
                                "source_excerpt": evidence_path.read_text(encoding="utf-8"),
                                "target_excerpt": (release_dir / "tasks.md").read_text(encoding="utf-8")}
        git_commit(self.root)
        preview = self.preview(imports={
            "approvals": [{"source": ".specs/001-demo/approval.json", "target": ".specs/release-v2.0.0/spec.md", "equivalence": approval_equivalence}],
            "evidence": [{"source": ".specs/001-demo/step-evidence.json", "target": ".specs/release-v2.0.0/tasks.md", "equivalence": evidence_equivalence}],
        })
        self.assertEqual(preview["manifest"]["imports"]["approvals"][0]["status"], "imported")
        self.assertEqual(preview["manifest"]["imports"]["evidence"][0]["status"], "imported")
        candidate_spec = release_dir / "spec.md"
        candidate_plan = release_dir / "plan.md"
        candidate_tasks = release_dir / "tasks.md"
        originals = {path: path.read_text(encoding="utf-8") for path in (candidate_spec, candidate_plan, candidate_tasks)}
        changed_spec = json.loads(originals[candidate_spec].split("```spec-flow\n")[1].split("\n```")[0])
        changed_spec["acceptance"][0]["description"] = "New acceptance requirement not covered by the legacy check."
        write_document(candidate_spec, changed_spec)
        changed_plan = json.loads(originals[candidate_plan].split("```spec-flow\n")[1].split("\n```")[0])
        changed_plan["depends_on"][0]["digest"] = document_digest(candidate_spec)
        write_document(candidate_plan, changed_plan)
        changed_tasks = json.loads(originals[candidate_tasks].split("```spec-flow\n")[1].split("\n```")[0])
        changed_tasks["depends_on"][0]["digest"] = document_digest(candidate_plan)
        write_document(candidate_tasks, changed_tasks)
        changed_preview = self.preview(imports={
            "evidence": [{"source": ".specs/001-demo/step-evidence.json", "target": ".specs/release-v2.0.0/tasks.md", "equivalence": evidence_equivalence}],
        })
        self.assertEqual(changed_preview["manifest"]["imports"]["evidence"][0]["status"], "pending")
        for path, contents in originals.items():
            path.write_text(contents, encoding="utf-8")
        result = self.apply(preview)
        self.assertEqual(len(self.engine.store.approvals()), 1)
        imported_log = self.root / ".spec-flow/migrations" / result["migration_id"] / "imported-evidence.jsonl"
        self.assertEqual(len(imported_log.read_text().splitlines()), 1)
        self.engine.dispatch("migrate-resume", {"migration_id": result["migration_id"]})
        self.assertEqual(len(self.engine.store.approvals()), 1)
        self.assertEqual(len(imported_log.read_text().splitlines()), 1)
        for path in (".specs/constitution.md", ".specs/roadmap.md", ".specs/release-v2.0.0/plan.md", ".specs/release-v2.0.0/tasks.md"):
            self.engine.dispatch("approve", {"path": path, "actor": "user", "statement": "Approve migrated release.", "source": "conversation"})
        self.engine.dispatch("initialize", {})
        start_payload = {"release": "v2.0.0", "owner": "operator", "phases": ["PH-01"],
            "authorization": {"actor": "user", "statement": "Run migrated release.", "source": "conversation"},
            "capabilities": {"models": ["gpt-6-sol", "gpt-6-luna"]}}
        with patch.object(self.engine, "_credit_migrated_evidence", side_effect=RuntimeError("simulated crash after start event")):
            with self.assertRaises(RuntimeError):
                self.engine.dispatch("start", start_payload)
        started = self.engine.dispatch("start", start_payload)
        self.assertEqual(started["imported_completed"], ["T-001"])
        state = self.engine.dispatch("status", {"run_id": started["run_id"]})
        self.assertEqual(state["tasks"]["T-001"]["status"], "completed")
        self.assertEqual(sum(event["event"] == "migration_credited" for event in self.engine.store.read_events(started["run_id"])), 1)
        repeated = self.engine.dispatch("start", start_payload)
        self.assertTrue(repeated["already_completed"])
        self.assertEqual(sum(event["event"] == "migration_credited" for event in self.engine.store.read_events(started["run_id"])), 1)

    def test_resume_repairs_partial_promotion_without_duplicate_archive(self):
        preview = self.preview()
        from harness.runtime.migration import Migration as MigrationRuntime
        original = MigrationRuntime._promote

        def crash_after_one(instance, manifest, base):
            item = manifest["candidates"][0]
            source = base / "candidate/.specs" / Path(item["path"]).relative_to(".specs")
            instance._write(instance.root / item["path"], source.read_bytes())
            raise RuntimeError("simulated process interruption")

        with patch.object(MigrationRuntime, "_promote", crash_after_one):
            with self.assertRaises(RuntimeError):
                self.apply(preview)
        archive_dir = self.root / ".spec-flow/legacy" / preview["manifest"]["migration_id"] / "sources/001-demo"
        self.assertTrue(archive_dir.is_dir())
        result = self.engine.dispatch("migrate-resume", {"migration_id": preview["manifest"]["migration_id"]})
        self.assertTrue(result["completed"])
        self.assertTrue((self.root / ".specs/release-v2.0.0/tasks.md").is_file())
        self.assertTrue((archive_dir / "tasks.md").is_file())
        self.assertEqual((self.root / ".spec-flow/approvals.jsonl").read_text(), "") if (self.root / ".spec-flow/approvals.jsonl").exists() else None


if __name__ == "__main__":
    unittest.main()
