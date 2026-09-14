"""Keep the distributed identity and all seven Skill surfaces consistent."""
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "mining-market-research"


class PluginBrandingTest(unittest.TestCase):
    def test_native_id_matches_source_and_marketplaces(self):
        for host in ("codex", "claude"):
            manifest = json.loads((PLUGIN / f".{host}-plugin/plugin.json").read_text())
            self.assertEqual(manifest["name"], PLUGIN.name)
        for path in (".agents/plugins/marketplace.json", ".claude-plugin/marketplace.json"):
            entries = json.loads((ROOT / path).read_text())["plugins"]
            entry = next(item for item in entries if item["name"] == PLUGIN.name)
            source = entry["source"]
            self.assertEqual(source["path"] if isinstance(source, dict) else source,
                             "./plugins/mining-market-research")

    def test_every_skill_has_branded_content_and_distinct_slug(self):
        expected = {
            "mining-market-research": "Mining Market Research",
            "company-brief": "Mining Market Research — Company Brief",
            "company-report": "Mining Market Research — Company Report",
            "company-comparison": "Mining Market Research — Company Comparison",
            "market-analysis": "Mining Market Research — Market Analysis",
            "news-analysis": "Mining Market Research — News Analysis",
            "upgrade": "Mining Market Research — Upgrade",
        }
        self.assertEqual({p.parent.name for p in (PLUGIN / "skills").glob("*/SKILL.md")},
                         set(expected))
        for slug, title in expected.items():
            skill = PLUGIN / "skills" / slug
            text = (skill / "SKILL.md").read_text()
            self.assertIn(f"name: {slug}\n", text)
            self.assertIn(f"# {title}\n", text)
            self.assertIn("Mining Market Research", text.split("description: ", 1)[1].split("\n", 1)[0])
            ui = (skill / "agents/openai.yaml").read_text()
            self.assertIn(f'display_name: "{title}"', ui)
            self.assertIn(f"${slug}", ui)
            self.assertNotIn("allow_implicit_invocation: false", ui)

    def test_old_plugin_namespace_is_absent_from_distributed_skills(self):
        for path in (PLUGIN / "skills").rglob("*"):
            if path.is_file() and path.suffix in {".md", ".json", ".yaml", ".py"}:
                self.assertNotIn("anchises-analysis", path.read_text(), str(path))
                self.assertNotIn("Anchises Analysis", path.read_text(), str(path))
                if path.suffix in {".md", ".yaml"}:
                    self.assertNotIn("Anchises-Analysis", path.read_text(), str(path))


if __name__ == "__main__":
    unittest.main()
