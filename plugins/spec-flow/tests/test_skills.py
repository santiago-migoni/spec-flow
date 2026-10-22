"""Structural checks for the release-centered public skill package."""
import json
import re
import unittest
from pathlib import Path
from harness.runtime.contracts import read_document

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
NAMES = ("using-spec-flow", "grilling", "constitution", "design", "roadmap", "specify",
         "plan", "tasks", "backlog", "implement",
         "review-release", "finishing-branch")
DOCUMENT_TEMPLATES = {
    "constitution": ("constitution", "constitution-template.md"),
    "architecture": ("design", "architecture-template.md"),
    "infrastructure": ("design", "infrastructure-template.md"),
    "structure": ("design", "structure-template.md"),
    "roadmap": ("roadmap", "roadmap-template.md"),
    "spec": ("specify", "spec-template.md"),
    "plan": ("plan", "plan-template.md"),
    "tasks": ("tasks", "tasks-template.md"),
}


class SkillPackageTests(unittest.TestCase):
    def test_claude_manifest_and_marketplace_are_packaged(self):
        manifest = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())
        self.assertEqual(manifest["name"], "spec-flow")
        self.assertRegex(manifest["version"], r"^[0-9]+\.[0-9]+\.[0-9]+$")
        marketplace = json.loads((ROOT.parents[1] / ".claude-plugin" / "marketplace.json").read_text())
        entry = next(item for item in marketplace["plugins"] if item["name"] == "spec-flow")
        self.assertEqual(entry["source"], "./plugins/spec-flow")
        self.assertFalse((ROOT / ".codex-plugin").exists())

    def test_skill_metadata_and_gates(self):
        discovered = {path.parent.name for path in SKILLS.glob("*/SKILL.md")}
        self.assertEqual(discovered, set(NAMES))
        direct_controller_skills = {owner for owner, _ in DOCUMENT_TEMPLATES.values()}
        direct_controller_skills.update(("using-spec-flow", "backlog"))
        for name in NAMES:
            with self.subTest(skill=name):
                text = (SKILLS / name / "SKILL.md").read_text()
                self.assertIn("name: " + name, text)
                self.assertIn("description:", text)
                self.assertIn("<HARD-GATE>", text)
                self.assertIn("</HARD-GATE>", text)
                if name in direct_controller_skills:
                    self.assertIn("spec-flow.py", text)

    def test_document_templates_have_one_contract_and_generated_tail(self):
        fence = chr(96) * 3
        for kind, (skill, filename) in DOCUMENT_TEMPLATES.items():
            with self.subTest(document=kind):
                path = SKILLS / skill / "assets" / filename
                self.assertTrue(path.is_file(), "Missing document template: " + str(path))
                text = path.read_text()
                self.assertTrue(text.startswith("---\n"))
                self.assertNotIn(fence + "spec-flow", text)
                contract = read_document(path)["contract"]
                self.assertEqual(contract["schema_version"], 1)
                self.assertEqual(contract["revision"], "R00")
                self.assertIn("depends_on", contract)
                self.assertEqual(contract["kind"], kind)
                if kind == "roadmap":
                    self.assertEqual(contract["releases"][0]["version"], "v1.0.0")
                    self.assertIn("objective", contract["releases"][0])
                    self.assertIn("status", contract["releases"][0])
                if kind == "plan":
                    self.assertEqual(contract["phases"][0]["id"], "PH-01")
                    self.assertIn("depends_on", contract["phases"][0])
                self.assertTrue(text.rstrip().endswith("<!-- spec-flow:generated:end -->"))

    def test_design_package_contains_one_skill_and_three_templates(self):
        design = SKILLS / "design"
        files = {path.relative_to(design).as_posix()
                 for path in design.rglob("*") if path.is_file()}
        self.assertEqual(files, {
            "SKILL.md", "assets/architecture-template.md",
            "assets/infrastructure-template.md", "assets/structure-template.md",
        })

    def test_release_paths_and_legacy_migration(self):
        bootstrap = (SKILLS / "using-spec-flow" / "SKILL.md").read_text()
        self.assertIn(".specs/release-vX.Y.Z", bootstrap)
        self.assertIn("migrate", bootstrap)
        self.assertIn("initialize", bootstrap)
        self.assertIn("design (applicable architecture, infrastructure, and structure)", bootstrap)
        self.assertNotIn("one active feature per release", bootstrap)


if __name__ == "__main__":
    unittest.main()
