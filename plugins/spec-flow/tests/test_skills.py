"""Structural checks for the release-centered public skill package."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
NAMES = ("using-spec-flow", "constitution", "architecture", "structure",
         "infrastructure", "roadmap", "specify", "clarify", "plan", "tasks",
         "analyze", "backlog")
DOCUMENTS = ("constitution", "architecture", "structure", "infrastructure",
             "roadmap", "specify", "plan", "tasks")


class SkillPackageTests(unittest.TestCase):
    def test_skill_metadata_and_gates(self):
        for name in NAMES:
            with self.subTest(skill=name):
                text = (SKILLS / name / "SKILL.md").read_text()
                self.assertIn("name: " + name, text)
                self.assertIn("description:", text)
                self.assertIn("<HARD-GATE>", text)
                self.assertIn("</HARD-GATE>", text)
                self.assertIn("spec-flow.py", text)

    def test_document_templates_have_one_contract_and_generated_tail(self):
        fence = chr(96) * 3
        for name in DOCUMENTS:
            with self.subTest(skill=name):
                path = SKILLS / name / "assets" / (("spec" if name == "specify" else name) + "-template.md")
                text = path.read_text()
                blocks = re.findall(fence + r"spec-flow\n(.*?)\n" + fence, text, re.S)
                self.assertEqual(len(blocks), 1)
                contract = json.loads(blocks[0])
                self.assertEqual(contract["schema_version"], 1)
                self.assertEqual(contract["revision"], "R00")
                self.assertIn("depends_on", contract)
                self.assertEqual(contract["kind"], "spec" if name == "specify" else name)
                if name == "roadmap":
                    self.assertEqual(contract["releases"][0]["version"], "v2.0.0")
                    self.assertIn("objective", contract["releases"][0])
                    self.assertIn("status", contract["releases"][0])
                if name == "plan":
                    self.assertEqual(contract["phases"][0]["id"], "PH-01")
                    self.assertIn("depends_on", contract["phases"][0])
                self.assertTrue(text.rstrip().endswith("<!-- spec-flow:generated:end -->"))

    def test_release_paths_and_legacy_migration(self):
        bootstrap = (SKILLS / "using-spec-flow" / "SKILL.md").read_text()
        self.assertIn(".specs/release-vX.Y.Z", bootstrap)
        self.assertIn("migrate", bootstrap)
        self.assertIn("initialize", bootstrap)
        self.assertIn("applicable shared system design", bootstrap)
        self.assertNotIn("one active feature per release", bootstrap)

    def test_read_only_analyze(self):
        text = (SKILLS / "analyze" / "SKILL.md").read_text()
        self.assertIn("read-only", text.lower())
        self.assertIn("Do not write any file", text)


if __name__ == "__main__":
    unittest.main()
