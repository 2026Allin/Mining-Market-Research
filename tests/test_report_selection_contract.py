"""Schema and shared-instruction regression checks; not host behavioral certification."""
import copy
import json
from pathlib import Path
import unittest
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/mining-market-research"
CORE = PLUGIN / "skills/mining-market-research"


class ReportSelectionContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tools = {t["name"]: t for t in json.loads(
            (PLUGIN / "contracts/hosted-mcp-v1.json").read_text())["tools"]}

    def test_modes_and_news_context_constraints(self):
        args = dict(exchange="LSE", ticker="RIO", company_name="Rio Tinto plc",
                    output_locale="zh-CN", mode="auto", news_codes=[123456],
                    research_focus="Funding impact?")
        validator = Draft202012Validator(self.tools["get_company_report"]["inputSchema"])
        validator.validate(args)
        validator.validate({**args, "mode": "refresh"})
        for patch in ({"mode": "cached"}, {"news_codes": [1,2,3,4,5,6]},
                      {"news_codes": [1,1]}, {"news_codes": [0]},
                      {"news_codes": ["123456"]}, {"research_focus": "x" * 2001}):
            self.assertTrue(list(validator.iter_errors({**args, **patch})), patch)
        prepared = {k:v for k,v in args.items() if k != "mode"}
        Draft202012Validator(self.tools["prepare_company_report_generation"]["inputSchema"]).validate(prepared)

    def test_three_output_states_and_restricted_refresh_action(self):
        variants = self.tools["get_company_report"]["outputSchema"]["properties"]["data"]["oneOf"]
        states = {v["properties"]["status"]["const"]: v for v in variants}
        self.assertEqual(set(states), {"report_available", "generation_ready", "not_eligible"})
        props = states["report_available"]["properties"]
        self.assertEqual(props["report"]["properties"]["language"]["const"], "en")
        self.assertIn("generated_at", props["report"]["required"])
        validator = Draft202012Validator(props["refresh_action"])
        action = {"tool_name": "get_company_report", "arguments": {
            "exchange": "LSE", "ticker": "RIO", "company_name": "Rio Tinto plc",
            "output_locale": "zh-CN", "mode": "refresh", "news_codes": [123456]}}
        validator.validate(action)
        invalid = copy.deepcopy(action)
        invalid["tool_name"] = "run_shell"
        self.assertTrue(list(validator.iter_errors(invalid)))
        invalid = copy.deepcopy(action)
        invalid["arguments"]["mode"] = "auto"
        self.assertTrue(list(validator.iter_errors(invalid)))
        self.assertEqual(states["generation_ready"]["properties"]["persistence"]["const"], "none")

    def test_news_cards_expose_master_identity_not_guessed_tickers(self):
        companies = self.tools["search_news"]["outputSchema"]["properties"]["data"]["properties"]["items"]["items"]["properties"]["companies"]
        self.assertEqual(set(companies["items"]["required"]), {"exchange", "ticker", "company_name"})

    def test_shared_workflow_guardrails(self):
        workflow = " ".join((CORE / "references/report-workflow.md").read_text().split())
        formatting = " ".join((CORE / "references/report-format.md").read_text().split())
        finalizer = " ".join((CORE / "references/response-finalization.md").read_text().split())
        for token in ("mode=auto", "mode=refresh", "report_available", "generation_ready",
                      "refresh_action.tool_name=get_company_report", "news.read",
                      "never infer installation approval", "New conversations use MCP again"):
            self.assertIn(token, workflow)
        for token in ("report.generated_at", "report_predates_linked_news=true",
                      "No web access is needed to translate", "Do not inject new facts"):
            self.assertIn(token, formatting)
        self.assertIn("replaces the semantic question", finalizer)
        self.assertNotIn("Do not read a prior stored report first", workflow)
        self.assertNotIn("Call `prepare_company_report_generation` directly", workflow)

    def test_continuation_gate_precedes_identity_and_selection(self):
        text = (CORE / "references/report-workflow.md").read_text()
        self.assertLess(text.index("## 0. Continue or start research"), text.index("## 1. Establish"))
        self.assertIn("No second confirmation or preliminary `auto` call", text)

    def test_auto_golden_cases_do_not_require_unconditional_live_research(self):
        fixtures = json.loads((ROOT / "tests/fixtures/golden_prompts.json").read_text())
        cases = {c["id"]: c for c in fixtures["positive"]}
        for name in ("company-name-live-report", "mixed-company-and-market-analysis",
                     "inactive-company-live-report", "external-market-live-report",
                     "mining-financial-quality"):
            behavior = cases[name]["expected_behavior"]
            self.assertIn("report_available", behavior)
            self.assertIn("generation_ready", behavior)
        context = cases["context-reference-live-report"]
        self.assertNotIn("resolve_company_identity", context["expected_tools"])
        self.assertIn("verified", context["context"])

    def test_reviewer_report_cases_use_new_states(self):
        fixtures = json.loads((ROOT / "tests/fixtures/reviewer_cases.json").read_text())
        for case in fixtures["positive"]:
            if "get_company_report" in case.get("expected_workflow", []):
                self.assertNotIn("Host live web research", case["expected_workflow"])
                self.assertNotIn("status=ready", case.get("expected_shape", []))


if __name__ == "__main__":
    unittest.main()
