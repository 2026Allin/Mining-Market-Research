# Mining Market Research — Codex report acceptance

Scope: Codex only. Shared-source unit tests may validate both manifest formats;
this does not launch or certify Claude Code or Claude Chat.

## Evidence levels

- Schema/fixture checks verify contract constraints and specified expectations.
- Mock protocol checks exercise synthetic responses and parameter preservation.
- Direct MCP smoke checks run from Codex verify the service, not native Skill
  discovery or Codex tool selection. They do not execute returned research prompts.
- Native acceptance requires a fresh Codex session loading the new Skill and
  exposing `get_company_report` in its actual tool catalog. If absent, record
  this as blocked; do not substitute direct HTTP and call native acceptance passed.

## Reproducible direct smoke

```sh
RUN_LIVE_MCP_TESTS=1 PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests -p test_live_hosted_contract.py -k report_selection_auto_and_refresh -v
```

This performs handshake/catalog lookup and two read-only report requests for
ASX:BHP. It prints status receipts only; it does not persist report content.
An `auto` result of `generation_ready` does not test real stored-report display.
Do not broaden issuer searches just to manufacture a stored-report success.

## Native session cases

Run with controlled fixtures where required, marking synthetic inputs clearly.
Keep actual tool-call receipts; never reconstruct missing calls from instructions.

| Case | Observable pass condition |
|---|---|
| Existing English report, Chinese request | Original date/timezone, faithful numbers/currencies/citations/risk, no research calls |
| No selected report | `auto` followed by `generation_ready`, live sources and completed report, no second consent |
| Explicit latest research | First report call uses `refresh`, no preliminary `auto` |
| Accept report refresh | Exactly one validated action, same identity/locale/news/focus, no repeat confirmation |
| Report predates news | Warning follows the returned flag, not a local date calculation |
| Multiple companies or listings | Resolve the user's target or ask once, no guessed ticker |
| News access/association error | No retry with deleted news IDs; explain the unavailable scope |
| Web unavailable | Supplied report can be translated; new research cannot be fabricated |
| News/brief/comparison/market only | No report-tool call |
| Same-report follow-up/new session | Follow-up uses current report; a new session queries MCP again |
| Report refresh and plugin upgrade both pending | Ambiguous assent prompts clarification, no installation |
| Invalid response or missing tool | Explain limitation, no implicit prepare fallback |

Actual native sessions and a real `report_available` translation remain separate
acceptance work until their tool and answer traces have been observed. Passing
schema tests does not establish translation quality or multi-turn Agent behavior.
