"""Package structure, English resources, and local-reference checks."""
import ast
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PackageTests(unittest.TestCase):
    def test_python_and_json_parse(self):
        for path in ROOT.rglob("*"):
            if path.suffix == ".py":
                ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            elif path.suffix == ".json":
                json.loads(path.read_text(encoding="utf-8"))

    def test_resources_are_english_and_no_machine_specific_paths(self):
        for path in ROOT.rglob("*"):
            if path.is_file() and path.suffix in (".md", ".py", ".sh", ".yaml", ".json"):
                content = path.read_text(encoding="utf-8")
                self.assertFalse(any(0x4E00 <= ord(c) <= 0x9FFF for c in content), str(path))
                self.assertNotIn("/home/" + "example-user/", content, str(path))

    def test_markdown_links_resolve(self):
        for path in ROOT.rglob("*.md"):
            for target in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
                if "://" not in target and not target.startswith("#"):
                    self.assertTrue((path.parent / target.split("#")[0]).exists(),
                                    f"{path}: {target}")

    def test_skill_name_and_ui_invocation_agree(self):
        skill = (ROOT / "SKILL.md").read_text()
        metadata = (ROOT / "agents/openai.yaml").read_text()
        self.assertTrue(skill.startswith("---\nname: run-agentic-dse\n"))
        self.assertIn("$run-agentic-dse", metadata)
        match = re.search(r'short_description: "([^"]+)"', metadata)
        self.assertIsNotNone(match)
        self.assertTrue(25 <= len(match[1]) <= 64)


if __name__ == "__main__":
    unittest.main()
