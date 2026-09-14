import copy
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "plugins/mining-market-research/skills/mining-market-research"
SCRIPT = CORE / "scripts/event_market_metrics.py"
SPEC = importlib.util.spec_from_file_location("event_market_metrics", SCRIPT)
METRICS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(METRICS)


def payload(volumes=(0, 10, 20, 60)):
    return {"schema_version": 1, "baseline_window": 3, "percentile_window": 3,
            "min_samples": 3, "price_basis": "raw", "volume_basis": "raw",
            "rows": [{"exchange": "ASX", "ticker": "TEST", "date": f"2026-09-{i+1:02}",
                      "open": 10+i, "close": 11+i, "volume": v} for i, v in enumerate(volumes)]}


class EventMetricsTest(unittest.TestCase):
    def test_current_excluded_and_real_zero_retained(self):
        result = METRICS.analyze(payload())["instruments"][0]
        last = result["observations"][-1]
        self.assertEqual(last["baseline_n"], 3)
        self.assertEqual(last["baseline_mean"], 10)
        self.assertEqual(last["relative_volume"], 6)
        self.assertEqual(last["volume_midrank_percentile"], 100)
        self.assertEqual(result["average_volume"], 22.5)
        self.assertAlmostEqual(result["endpoint_return_pct"], (14/11-1)*100)

    def test_missing_not_zero_and_short_baseline_unavailable(self):
        result = METRICS.analyze(payload((None, 10, 20, 60)))["instruments"][0]
        self.assertEqual(result["missing_volume"], 1)
        self.assertEqual(result["volume_n"], 3)
        self.assertIsNone(result["observations"][-1]["relative_volume"])

    def test_zero_baseline_and_tie_percentile(self):
        result = METRICS.analyze(payload((0, 0, 0, 0)))["instruments"][0]["observations"][-1]
        self.assertIsNone(result["relative_volume"])
        self.assertIn("baseline_zero", result["warnings"])
        self.assertEqual(result["volume_midrank_percentile"], 50)

    def test_unknown_basis_withholds_affected_metrics(self):
        p = payload()
        p["price_basis"] = p["volume_basis"] = "unknown"
        result = METRICS.analyze(p)["instruments"][0]
        self.assertIsNone(result["endpoint_return_pct"])
        self.assertIsNone(result["average_volume"])
        self.assertIsNone(result["observations"][-1]["relative_volume"])

    def test_missing_endpoint_not_silently_replaced(self):
        p = payload()
        p["rows"][0]["close"] = None
        result = METRICS.analyze(p)["instruments"][0]
        self.assertIsNone(result["endpoint_return_pct"])
        self.assertEqual(result["start_date"], "2026-09-01")

    def test_exact_listings_separate_and_input_not_mutated(self):
        p = payload()
        other = copy.deepcopy(p["rows"])
        for row in other:
            row["exchange"] = "LSE"
            row["volume"] *= 2
        p["rows"].extend(other)
        before = copy.deepcopy(p)
        result = METRICS.analyze(p)
        self.assertEqual(len(result["instruments"]), 2)
        self.assertEqual(p, before)

    def test_invalid_numeric_and_duplicate_inputs(self):
        for value in (True, -1, float("nan"), "20"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                METRICS.analyze(payload((0, 10, 20, value)))
        p = payload()
        p["rows"].append(p["rows"][0])
        with self.assertRaises(ValueError):
            METRICS.analyze(p)

    def test_alignment_and_no_future_session_fabrication(self):
        sessions = [{"date": "2026-09-04", "open_at": "2026-09-04T09:00:00+10:00",
                     "close_at": "2026-09-04T16:00:00+10:00"},
                    {"date": "2026-09-07", "open_at": "2026-09-07T09:00:00+10:00",
                     "close_at": "2026-09-07T16:00:00+10:00"}]
        for stamp, expected in [("2026-09-04T08:00:00+10:00", "before_next_verified_session"),
                                ("2026-09-04T12:00:00+10:00", "intraday_mixed"),
                                ("2026-09-04T16:00:00+10:00", "boundary_uncertain"),
                                ("2026-09-07T17:00:00+10:00", "after_last_verified_session"),
                                ("2026-09-04T12:00:00", "unknown")]:
            self.assertEqual(METRICS.align_publication(stamp, sessions)["status"], expected)
        self.assertEqual(METRICS.align_publication("2026-09-05T12:00:00+10:00", sessions)["first_possible_session"], "2026-09-07")

    def test_explicit_dst_offsets_and_invalid_sessions(self):
        sessions = [{"date": "2026-03-09", "open_at": "2026-03-09T09:30:00-04:00",
                     "close_at": "2026-03-09T16:00:00-04:00"}]
        self.assertEqual(METRICS.align_publication("2026-03-09T13:00:00Z", sessions)["status"], "before_next_verified_session")
        with self.assertRaises(ValueError):
            METRICS.align_publication("2026-03-09T13:00:00Z", sessions*2)

    def test_cli_json_and_malformed_input(self):
        result = subprocess.run([sys.executable, str(SCRIPT)], input=json.dumps(payload()), text=True, capture_output=True)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["status"], "calculated")
        result = subprocess.run([sys.executable, str(SCRIPT)], input="{", text=True, capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["status"], "invalid_input")

    def test_both_entrances_reach_same_fusion_dependencies(self):
        def reachable(start):
            seen, pending = set(), [start.resolve()]
            while pending:
                path = pending.pop()
                if path in seen:
                    continue
                seen.add(path)
                self.assertTrue(path.is_file(), str(path))
                for link in re.findall(r"\[[^\]]+\]\(([^)]+\.md)\)", path.read_text()):
                    if "://" not in link:
                        pending.append((path.parent/link).resolve())
            return seen
        required = {CORE/"workflows/event-market-analysis.md", CORE/"references/mining-analysis-priorities.md",
                    CORE/"references/news-retrieval.md", CORE/"references/event-time-alignment.md",
                    CORE/"references/market-reaction-metrics.md", CORE/"references/macro-metals-context.md"}
        for name in ("news-analysis", "market-analysis"):
            self.assertTrue(required.issubset(reachable(CORE.parent/name/"SKILL.md")))

    def test_window_defaults_do_not_create_server_columns(self):
        reference = (CORE/"references/market-reaction-metrics.md").read_text()
        self.assertIn("NOT MCP column names", reference)
        self.assertIn("actual get_stock_schema result", reference)
        self.assertIn("do not rename it", reference)
        workflow = (CORE/"workflows/event-market-analysis.md").read_text()
        self.assertIn("actual schema before submission", workflow)
        self.assertIn("business answer itself", workflow)

    def test_empty_news_does_not_establish_trader_motive(self):
        priorities = (CORE/"references/mining-analysis-priorities.md").read_text()
        self.assertIn("not positive evidence of profit-taking", priorities)
        retrieval = (CORE/"references/news-retrieval.md").read_text()
        self.assertIn("omit optional q", retrieval)
        self.assertIn("Retain genuine topic/search constraints", retrieval)
        self.assertIn('"gold-tagged" with "primarily gold"', retrieval)
        macro = (CORE/"references/macro-metals-context.md").read_text()
        self.assertIn("same-calendar-date London/LME", macro)
        self.assertIn("non-synchronous context", macro)

    def test_transport_recovery_does_not_bypass_service_limits(self):
        policy = (CORE/"references/market-data-policy.md").read_text()
        self.assertIn("Do not repeat an identical oversized request", policy)
        self.assertIn("page_size=25", policy)
        self.assertIn("do not splice", policy)
        self.assertIn("does not permit restarting after a service refusal", policy)


if __name__ == "__main__":
    unittest.main()
