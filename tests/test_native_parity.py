"""Shared-package and contract checks, not a claim of real agent E2E coverage."""
import copy
import json
import sys
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/mining-market-research"
sys.path.insert(0, str(PLUGIN / "contracts"))
from capability_contract import compatibility_changes, load_capabilities, required_tools
from hosted_contract import load_contract


class NativeParityTest(unittest.TestCase):
    def test_news_exchange_limit_and_rejected_scope_are_current(self):
        tools = {t['name']: t for t in load_contract()['tools']}
        for name in ('search_news', 'prepare_news_web_research'):
            self.assertEqual(tools[name]['inputSchema']['properties']['exchanges']['maxItems'], 100)
        workflow = (PLUGIN / 'skills/mining-market-research/workflows/news-analysis.md').read_text()
        self.assertIn('../references/news-retrieval.md', workflow)
        retrieval = (PLUGIN / 'skills/mining-market-research/references/news-retrieval.md').read_text()
        self.assertIn('outside the access option reject the query', retrieval)
        self.assertIn('Do not drop', retrieval)

    def setUp(self):
        self.contract = load_contract()
        self.capabilities = load_capabilities()

    def test_every_required_tool_has_valid_example_and_existing_skill(self):
        tools = {t["name"]: t for t in self.contract["tools"]}
        self.assertEqual(required_tools(), set(tools))
        for group in self.capabilities["groups"].values():
            for skill in group["skills"]:
                self.assertTrue((PLUGIN / "skills" / skill / "SKILL.md").is_file())
            for name, example in group["tools"].items():
                with self.subTest(tool=name):
                    Draft202012Validator(tools[name]["inputSchema"]).validate(example)

    def test_added_tools_and_reordering_are_not_breaking(self):
        changed = copy.deepcopy(self.contract)
        added = copy.deepcopy(changed["tools"][0])
        added["name"] = "future_tool"
        changed["tools"] = list(reversed(changed["tools"])) + [added]
        result = compatibility_changes(self.contract, changed)
        self.assertEqual(result["blocking"], [])
        self.assertEqual(len(result["notices"]), 1)

    def test_missing_tool_and_new_required_argument_block(self):
        changed = copy.deepcopy(self.contract)
        changed["tools"].pop()
        self.assertTrue(compatibility_changes(self.contract, changed)["blocking"])
        changed = copy.deepcopy(self.contract)
        changed["tools"][0]["inputSchema"]["required"] = ["token"]
        self.assertTrue(compatibility_changes(self.contract, changed)["blocking"])

    def test_optional_argument_and_description_are_review_only(self):
        changed = copy.deepcopy(self.contract)
        changed["tools"][0]["description"] = "New wording"
        changed["tools"][0]["inputSchema"]["properties"]["locale"] = {"type": "string"}
        self.assertEqual(compatibility_changes(self.contract, changed)["blocking"], [])

    def test_old_history_and_news_parameters_are_rejected(self):
        tools = {t["name"]: t for t in self.contract["tools"]}
        for name, args in [
            ("list_stock_tables", {"start_date": "2026-07-01"}),
            ("prepare_news_web_research", {"web_q": "gold"}),
            ("get_news_article", {"news_code": "invented"}),
        ]:
            self.assertFalse(Draft202012Validator(tools[name]["inputSchema"]).is_valid(args))

    def test_documentation_named_output_field_is_not_ignored(self):
        old = copy.deepcopy(self.contract)
        old["tools"][0]["outputSchema"]["properties"]["description"] = {"type": "string"}
        new = copy.deepcopy(old)
        del new["tools"][0]["outputSchema"]["properties"]["description"]
        self.assertTrue(compatibility_changes(old, new)["blocking"])

    def test_same_product_version_and_connection_on_both_hosts(self):
        manifests = [json.loads((PLUGIN / path / "plugin.json").read_text())
                     for path in (".codex-plugin", ".claude-plugin")]
        self.assertEqual(manifests[0]["version"].split("+")[0], manifests[1]["version"].split("+")[0])
        for key in ("skills", "mcpServers"):
            self.assertEqual(manifests[0][key], manifests[1][key])
        self.assertEqual(manifests[0]["interface"]["displayName"], manifests[1]["displayName"])


if __name__ == "__main__":
    unittest.main()
