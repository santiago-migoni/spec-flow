import json
import tempfile
import unittest
from pathlib import Path

from harness.runtime.contracts import (
    ContractError,
    document_digest,
    normalize_release,
    read_document,
    safe_path,
    validate_document,
    validate_release,
)


def write_document(path, contract, prose="Approved decision content."):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(prose + "\n\n```spec-flow\n" + json.dumps(contract, indent=2) + "\n```\n", encoding="utf-8")
    return path


def base_contract(kind, *, identifier="DOC-001", depends_on=None, **extra):
    if kind == "spec":
        extra.setdefault("stories", [{"id": "US-001", "title": "Complete behavior", "description": "The user needs the behavior."}])
        criteria = extra.get("acceptance", [{"id": "AC-001", "description": "Works."}])
        extra["acceptance"] = [dict(item, story=item.get("story", "US-001")) for item in criteria]
    return {"schema_version": 1, "kind": kind, "revision": "R00", "id": identifier, "depends_on": depends_on or [], **extra}


def task(identifier="T-001", *, depends_on=None, acceptance=None):
    return {
        "id": identifier, "phase": "PH-01", "story": "US-001", "acceptance": acceptance or ["AC-001"],
        "depends_on": depends_on or [], "files": ["src/example.py"],
        "steps": [{"id": identifier + ".001", "action": "Implement the behavior.",
                    "verification": {"command": ["python3", "-m", "unittest"], "expected": "All tests pass."}}],
        "closure": "The behavior and verification are complete.",
    }


class NormalizeReleaseTests(unittest.TestCase):
    def test_normalizes_strict_numeric_semver(self):
        self.assertEqual(normalize_release("1.2.3"), "v1.2.3")
        self.assertEqual(normalize_release("v1.2.3"), "v1.2.3")

    def test_rejects_non_numeric_or_non_semver_release(self):
        for value in ("1.2", "v1.2.3-rc.1", "01.2.3", "1.2.3x", "release-1.2.3"):
            with self.subTest(value=value), self.assertRaises(ContractError):
                normalize_release(value)


class PathAndDocumentTests(unittest.TestCase):
    def test_safe_path_rejects_traversal_and_symlink_escape(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "project"
            root.mkdir()
            outside = Path(temp) / "outside"
            outside.mkdir()
            (root / "escape").symlink_to(outside, target_is_directory=True)
            with self.assertRaises(ContractError):
                safe_path(root, "../outside/file.md")
            with self.assertRaises(ContractError):
                safe_path(root, "escape/file.md")

    def test_read_document_returns_contract_and_surrounding_prose(self):
        with tempfile.TemporaryDirectory() as temp:
            path = write_document(Path(temp) / "constitution.md", base_contract("constitution"), "Purpose and principles.")
            document = read_document(path)
            self.assertEqual(document["contract"]["kind"], "constitution")
            self.assertEqual(document["prose"], "Purpose and principles.")

    def test_document_digest_ignores_only_progress_and_status(self):
        with tempfile.TemporaryDirectory() as temp:
            path = write_document(Path(temp) / "spec.md", base_contract("spec", status="approved", acceptance=[{"id": "AC-001", "description": "Works."}]))
            before = document_digest(path)
            text = path.read_text(encoding="utf-8").replace('"status": "approved"', '"status": "draft"')
            text += "<!-- spec-flow:generated:start -->\nprogress: 40%\n<!-- spec-flow:generated:end -->\n"
            path.write_text(text, encoding="utf-8")
            self.assertEqual(document_digest(path), before)
            path.write_text(path.read_text(encoding="utf-8").replace("Approved decision content.", "Changed decision content."), encoding="utf-8")
            self.assertNotEqual(document_digest(path), before)


class DocumentValidationTests(unittest.TestCase):
    def test_validates_a_complete_tasks_document(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = write_document(root / "tasks.md", base_contract("tasks", tasks=[task()]))
            result = validate_document(root, path)
            self.assertEqual(result["contract"]["kind"], "tasks")

    def test_rejects_missing_task_dependency_and_cycles(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = write_document(root / "tasks.md", base_contract("tasks", tasks=[task("T-001", depends_on=["T-002"]), task("T-002", depends_on=["T-001"])]))
            with self.assertRaises(ContractError):
                validate_document(root, path)

    def test_verifies_document_dependency_path_and_digest(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = write_document(root / "constitution.md", base_contract("constitution"))
            ref = {"path": "constitution.md", "digest": document_digest(source)}
            path = write_document(root / "architecture.md", base_contract("architecture", depends_on=[ref]))
            self.assertEqual(validate_document(root, path)["contract"]["kind"], "architecture")
            ref["digest"] = "0" * 64
            write_document(path, base_contract("architecture", depends_on=[ref]))
            with self.assertRaises(ContractError):
                validate_document(root, path)

    def test_rejects_placeholder_prose_and_empty_spec_acceptance(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = write_document(root / "spec.md", base_contract("spec", acceptance=[]), "TODO")
            with self.assertRaises(ContractError):
                validate_document(root, path)

    def test_accepts_later_revision_and_rejects_unknown_status(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = write_document(root / "constitution.md", base_contract("constitution", revision="R02", status="draft"))
            self.assertEqual(validate_document(root, path)["contract"]["revision"], "R02")
            write_document(path, base_contract("constitution", status="unknown"))
            with self.assertRaises(ContractError):
                validate_document(root, path)

    def test_rejects_unhashable_kind_or_status_as_contract_errors(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for changes in ({"kind": []}, {"status": {"unknown": True}}):
                with self.subTest(changes=changes):
                    contract = base_contract("constitution")
                    contract.update(changes)
                    path = write_document(root / "constitution.md", contract)
                    with self.assertRaises(ContractError):
                        validate_document(root, path)

    def test_rejects_generated_block_before_or_around_contract(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            contract = base_contract("constitution")
            contents = "Decision prose.\n\n<!-- spec-flow:generated:start -->\n" + json.dumps(contract) + "\n<!-- spec-flow:generated:end -->\n"
            path = root / "constitution.md"
            path.write_text(contents, encoding="utf-8")
            with self.assertRaises(ContractError):
                validate_document(root, path)

    def test_accepts_document_inspection_verification(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            item = task()
            item["steps"][0]["verification"] = {
                "inspection": "Confirm the generated template contains the required heading.",
                "expected": "The heading is present exactly once.",
            }
            path = write_document(root / "tasks.md", base_contract("tasks", tasks=[item]))
            self.assertEqual(validate_document(root, path)["contract"]["kind"], "tasks")

    def test_rejects_tasks_targeting_metadata_or_outside_root(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for filename in (".spec-flow/state.json", ".git/config", "../outside.py"):
                with self.subTest(filename=filename):
                    item = task()
                    item["files"] = [filename]
                    path = write_document(root / "tasks.md", base_contract("tasks", tasks=[item]))
                    with self.assertRaises(ContractError):
                        validate_document(root, path)


class ReleaseValidationTests(unittest.TestCase):
    def test_release_rejects_unknown_story_or_acceptance_cross_links(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            release = root / ".specs" / "release-v1.2.3"
            constitution = write_document(root / ".specs" / "constitution.md", base_contract("constitution"))
            roadmap = write_document(root / ".specs" / "roadmap.md", base_contract("roadmap", depends_on=[{"path": ".specs/constitution.md", "digest": document_digest(constitution)}], releases=[{"version": "v1.2.3", "objective": "Deliver the behavior.", "status": "planned"}]))
            spec_data = base_contract("spec", depends_on=[{"path": ".specs/roadmap.md", "digest": document_digest(roadmap)}], acceptance=[{"id": "AC-001", "story": "US-999", "description": "Works."}])
            spec = write_document(release / "spec.md", spec_data)
            plan = write_document(release / "plan.md", base_contract("plan", depends_on=[{"path": ".specs/release-v1.2.3/spec.md", "digest": document_digest(spec)}], phases=[{"id": "PH-01", "description": "Implement the release.", "depends_on": []}]))
            write_document(release / "tasks.md", base_contract("tasks", depends_on=[{"path": ".specs/release-v1.2.3/plan.md", "digest": document_digest(plan)}], tasks=[task(acceptance=["AC-001"])]))
            with self.assertRaisesRegex(ContractError, "unknown story"):
                validate_release(root, "v1.2.3")

    def test_release_checks_document_chain_and_acceptance_coverage(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            release = root / ".specs" / "release-v1.2.3"
            constitution = write_document(root / ".specs" / "constitution.md", base_contract("constitution"))
            roadmap = write_document(root / ".specs" / "roadmap.md", base_contract("roadmap", depends_on=[{"path": ".specs/constitution.md", "digest": document_digest(constitution)}], releases=[{"version": "v1.2.3", "objective": "Deliver the behavior.", "status": "planned"}]))
            spec = write_document(release / "spec.md", base_contract("spec", depends_on=[{"path": ".specs/roadmap.md", "digest": document_digest(roadmap)}], acceptance=[{"id": "AC-001", "description": "Works."}]))
            plan = write_document(release / "plan.md", base_contract("plan", depends_on=[{"path": ".specs/release-v1.2.3/spec.md", "digest": document_digest(spec)}], phases=[{"id": "PH-01", "description": "Implement the release.", "depends_on": []}]))
            write_document(release / "tasks.md", base_contract("tasks", depends_on=[{"path": ".specs/release-v1.2.3/plan.md", "digest": document_digest(plan)}], tasks=[task(acceptance=["AC-001"])]))
            result = validate_release(root, "1.2.3")
            self.assertEqual(result["release"], "v1.2.3")

    def test_release_rejects_uncovered_acceptance_criterion(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            release = root / ".specs" / "release-v1.2.3"
            constitution = write_document(root / ".specs" / "constitution.md", base_contract("constitution"))
            roadmap = write_document(root / ".specs" / "roadmap.md", base_contract("roadmap", depends_on=[{"path": ".specs/constitution.md", "digest": document_digest(constitution)}], releases=[{"version": "v1.2.3", "objective": "Deliver the behavior.", "status": "planned"}]))
            spec = write_document(release / "spec.md", base_contract("spec", depends_on=[{"path": ".specs/roadmap.md", "digest": document_digest(roadmap)}], acceptance=[{"id": "AC-001", "description": "Works."}]))
            plan = write_document(release / "plan.md", base_contract("plan", depends_on=[{"path": ".specs/release-v1.2.3/spec.md", "digest": document_digest(spec)}], phases=[{"id": "PH-01", "description": "Implement the release.", "depends_on": []}]))
            write_document(release / "tasks.md", base_contract("tasks", depends_on=[{"path": ".specs/release-v1.2.3/plan.md", "digest": document_digest(plan)}], tasks=[task(acceptance=["AC-999"])]))
            with self.assertRaises(ContractError):
                validate_release(root, "v1.2.3")

    def test_release_recursively_checks_roadmap_and_constitution(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            release = root / ".specs" / "release-v1.2.3"
            constitution = write_document(root / ".specs" / "constitution.md", base_contract("constitution"))
            roadmap = write_document(root / ".specs" / "roadmap.md", base_contract("roadmap", depends_on=[{"path": ".specs/constitution.md", "digest": document_digest(constitution)}], releases=[{"version": "v1.2.3", "objective": "Deliver the behavior.", "status": "planned"}]))
            spec = write_document(release / "spec.md", base_contract("spec", depends_on=[{"path": ".specs/roadmap.md", "digest": document_digest(roadmap)}], acceptance=[{"id": "AC-001", "description": "Works."}]))
            plan = write_document(release / "plan.md", base_contract("plan", depends_on=[{"path": ".specs/release-v1.2.3/spec.md", "digest": document_digest(spec)}], phases=[{"id": "PH-01", "description": "Implement the release.", "depends_on": []}]))
            write_document(release / "tasks.md", base_contract("tasks", depends_on=[{"path": ".specs/release-v1.2.3/plan.md", "digest": document_digest(plan)}], tasks=[task(acceptance=["AC-001"])]))
            write_document(constitution, base_contract("constitution"), "Changed constitutional decision.")
            with self.assertRaises(ContractError):
                validate_release(root, "v1.2.3")


if __name__ == "__main__":
    unittest.main()
