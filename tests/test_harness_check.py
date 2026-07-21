import json
import tempfile
import unittest
from pathlib import Path

from tools.harness_check import check_active_plans, check_agent_map, check_markdown_links, check_project_config


class HarnessCheckTests(unittest.TestCase):
    def test_broken_relative_link_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "doc.md").write_text("[missing](nowhere.md)\n", encoding="utf-8")
            findings = check_markdown_links(root)
            self.assertEqual(1, len(findings))
            self.assertIn("broken local link", findings[0].message)

    def test_external_and_anchor_links_are_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "doc.md").write_text("[web](https://example.com) [section](#here)\n", encoding="utf-8")
            self.assertEqual([], check_markdown_links(root))

    def test_agent_map_has_a_size_budget(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "AGENTS.md").write_text("line\n" * 121, encoding="utf-8")
            self.assertEqual(1, len(check_agent_map(root)))

    def test_project_config_requires_canonical_commands(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "harness").mkdir()
            config = {"schemaVersion": 1, "name": "demo", "summary": "Demo", "commands": {}}
            (root / "harness/project.json").write_text(json.dumps(config), encoding="utf-8")
            findings = check_project_config(root)
            self.assertEqual(4, len(findings))

    def test_active_plan_requires_resumable_sections(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            active = root / "docs/exec-plans/active"
            active.mkdir(parents=True)
            (active / "plan.md").write_text("# Plan\n\nStatus: Active\n\n## Outcome\n", encoding="utf-8")
            findings = check_active_plans(root)
            self.assertEqual(8, len(findings))


if __name__ == "__main__":
    unittest.main()

