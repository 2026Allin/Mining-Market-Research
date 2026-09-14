import copy
import unittest

from host_trace_contract import validate_trace
from test_native_parity import load_contract


class HostTraceTest(unittest.TestCase):
    def test_due_check_allowed_but_install_needs_authorization(self):
        trace = {"task": "market_data", "calls": [], "release_check": True,
                 "update_probe_action": "check_required"}
        self.assertEqual(validate_trace(trace, load_contract()), [])
        trace["plugin_install"] = True
        self.assertIn("installation requires explicit upgrade authorization",
                      validate_trace(trace, load_contract()))

    def test_same_news_trace_is_valid_for_both_hosts(self):
        for host in ("codex", "claude-code"):
            trace = {"host": host, "task": "news", "calls": [
                {"tool": "get_connection_status"},
                {"tool": "list_news_filters"},
                {"tool": "search_news", "arguments": {"q": "gold drill"},
                 "evidence": {"news_codes": [123]}},
                {"tool": "get_news_article", "arguments": {"news_code": 123}},
            ]}
            self.assertEqual(validate_trace(trace, load_contract()), [])
            over_limit = copy.deepcopy(trace)
            over_limit["calls"] += [trace["calls"][-1]] * 5
            self.assertIn("at most five article calls per user request", validate_trace(over_limit, load_contract()))

    def test_rejects_bypassed_research_export_and_sql_gates(self):
        trace = {"task": "news", "release_check": True, "claims_web_research": True,
                 "trading_date_selection": True, "calls": [
            {"tool": "prepare_news_web_research", "arguments": {"q": "gold"}},
            {"tool": "get_news_article", "arguments": {"news_code": 999}},
            {"tool": "run_readonly_sql", "arguments": {"sql": "SELECT COUNT(*) FROM stock_daily"}},
            {"tool": "create_csv_export", "arguments": {"query_id": "qry_example12345678"}},
        ]}
        self.assertEqual(len(validate_trace(trace, load_contract())), 8)
