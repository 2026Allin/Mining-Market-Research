"""Synthetic trace acceptance, not proof of native Agent behavior.

Only test infrastructure interprets these receipts. No client query/count or
export-size checker is installed in the plugin.
"""
import copy
import unittest

from host_trace_contract import validate_trace
from test_native_parity import load_contract


def page_event(cursor=None, *, truncated=False, limited=False):
    return {
        "tool": "screen_stocks",
        "arguments": {"exchanges": ["ASX", "LSE"], "start_date": "2026-01-01", "end_date": "2026-06-30"},
        "evidence": {
            "query_id": "qry_example12345678",
            "page": {"row_count": 200, "total_count": None, "truncated": truncated, "next_cursor": cursor},
            "analysis": {"matched_row_count": None, "pagination_limit_reached": limited},
            "export_policy": {"eligible_by_query": True, "source_tools_allowed": ["screen_stocks"]},
        },
    }


class StockQueryDeliveryTest(unittest.TestCase):
    def setUp(self):
        self.contract = load_contract()

    def test_unknown_total_authorizes_paging_not_zero_or_count_probe(self):
        first = page_event("opaque-next", truncated=True)
        last = page_event()
        last["arguments"] = {"cursor": "opaque-next", "page_size": 200}
        trace = {"historical": True, "calls": [first, last], "claims_complete": True}
        self.assertEqual(validate_trace(trace, self.contract), [])
        # Date-range history does not require an extra coverage lookup.
        wrong = {"calls": [first], "claimed_total": 0, "claims_complete": True}
        self.assertIn("unknown total must not be replaced by displayed rows", validate_trace(wrong, self.contract))

    def test_continuation_only_uses_same_tool_cursor(self):
        first = page_event("opaque-next", truncated=True)
        last = page_event()
        last["arguments"] = {"cursor": "opaque-next", "page_size": 200, "exchanges": ["ASX"]}
        self.assertIn("continuation must not resend query arguments", validate_trace({"calls": [first, last]}, self.contract))
        last["arguments"] = {"cursor": "invented"}
        self.assertIn("continuation requires the preceding same-tool cursor", validate_trace({"calls": [first, last]}, self.contract))

    def test_no_cursor_at_limit_is_not_complete(self):
        trace = {"calls": [page_event(limited=True, truncated=True)], "claims_complete": True}
        self.assertIn("cannot claim complete analysis of a partial query", validate_trace(trace, self.contract))
        trace["claims_complete"] = False
        self.assertEqual(validate_trace(trace, self.contract), [])

    def test_csv_can_follow_first_page_without_fields_or_old_partition_flag(self):
        first = page_event("opaque-next", truncated=True)
        export = {"tool": "create_csv_export", "arguments": {"query_id": first["evidence"]["query_id"]},
                  "evidence": {"download_url": "https://example.invalid/export.csv"}}
        trace = {"export_requested": True, "calls": [first, export], "claims_export_success": True}
        self.assertEqual(validate_trace(trace, self.contract), [])
        failed = copy.deepcopy(trace)
        failed["calls"][1]["evidence"] = {"error": "export_cell_limit_exceeded"}
        self.assertIn("export eligibility is not export success", validate_trace(failed, self.contract))
        failed["claims_export_success"] = False
        self.assertEqual(validate_trace(failed, self.contract), [])

    def test_explicit_count_is_allowed_but_unsolicited_audit_is_not(self):
        sql = "SELECT COUNT(*) AS n FROM stock_daily WHERE exchange = 'ASX'"
        trace = {"calls": [
            {"tool": "validate_readonly_sql", "arguments": {"sql": sql}, "evidence": {"valid": True}},
            {"tool": "run_readonly_sql", "arguments": {"sql": sql}},
        ]}
        self.assertEqual(validate_trace(trace, self.contract), [])
        trace["calls"][1]["purpose"] = "completeness_audit"
        self.assertIn("no unsolicited database completeness audit", validate_trace(trace, self.contract))

    def test_cross_exchange_pairs_and_missing_values_are_preserved(self):
        from jsonschema import Draft202012Validator
        tool = next(t for t in self.contract["tools"] if t["name"] == "screen_stocks")
        args = {"instruments": [{"exchange": "ASX", "ticker": "BHP"},
                                {"exchange": "LSE", "ticker": "RIO"}],
                "start_date": "2026-01-01", "end_date": "2026-06-30"}
        Draft202012Validator(tool["inputSchema"]).validate(args)
        # Evidence retention, not client synthesis of absent dates or zeroes.
        event = page_event()
        event["arguments"] = args
        event["evidence"]["rows"] = [{"ticker": "BHP", "price": None, "volume": None}]
        before = copy.deepcopy(event)
        self.assertEqual(validate_trace({"calls": [event]}, self.contract), [])
        self.assertEqual(event, before)
