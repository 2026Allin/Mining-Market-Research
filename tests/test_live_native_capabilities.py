"""Opt-in read-only production smoke checks for the newly integrated tools."""
import os
import unittest

from jsonschema import Draft202012Validator
from test_native_parity import load_contract
from sync_hosted_contract import MCPHttpClient


@unittest.skipUnless(os.environ.get("RUN_LIVE_NATIVE") == "1", "opt-in live native capability checks")
class LiveNativeCapabilitiesTest(unittest.TestCase):
    def test_dates_and_news_discovery_match_published_schemas(self):
        client = MCPHttpClient("https://mcp.anchisesdata.com/mcp")
        client.call("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                    "clientInfo": {"name": "native-capability-test", "version": "1.0.0"}}, 1)
        client.notify("notifications/initialized", {})
        tools = {t["name"]: t for t in load_contract()["tools"]}
        for i, (name, args) in enumerate([
            ("get_available_dates", {"page_size": 1}),
            ("list_news_filters", {}),
            ("search_news", {"q": "gold", "page_size": 1}),
            ("prepare_news_web_research", {"q": "gold"}),
        ], 2):
            with self.subTest(tool=name):
                result = client.call("tools/call", {"name": name, "arguments": args}, i)
                self.assertFalse(result.get("isError"), name)
                Draft202012Validator(tools[name]["outputSchema"]).validate(result["structuredContent"])
