# Mining Market Research Reviewer Test Cases

Run exactly five positive and three negative reviewer cases in a fresh task
after installing `mining-market-research@Anchises-Analysis`.

## Positive 1 — Public access and exchanges

> Check whether Mining Market Research public access is available, list the supported exchanges, and summarize the shared limits.

Expected: `get_connection_status`, `get_available_exchanges`, active public
access without credentials, and the supported structured-data markets.

## Positive 2 — Company name to structured stock data

> Show Apple's latest structured price, 30-day return, and data date.

Expected: resolve Apple to NASDAQ / AAPL / Apple Inc., then use the canonical
identity for structured market data.

## Positive 3 — Company report selection

> Show Apple's company research report in Simplified Chinese with source links.

Expected: establish identity and call `get_company_report(mode=auto)`.
For `report_available`, show the original date and faithful translation without
new facts or an invented risk rating, then ask once whether to refresh.
Only `generation_ready` executes live Host research with `**Summary:**`, seven
fixed English headings, localized bodies, a final English Risk label and source
links. `not_eligible` explains and stops. Do not save or upload either output.

## Positive 4 — External-market report

> Research LSE-listed Rio Tinto plc and generate a current English company report.

Expected: the resolver reports no supported-market match; the Host verifies LSE
/ RIO / Rio Tinto plc with primary sources and calls `auto`. Present an existing
report faithfully. For generation, respect `identity_source=host_supplied`,
listing verification and `Others` when returned. Do not force fresh research.

## Positive 5 — CSV export

> Export the immediately preceding Apple stock screen as CSV using only the displayed research fields and the default expiration.

Expected: confirm the preceding `screen_stocks` result has
`export_policy.eligible_by_query=true`, use its real `query_id`, omit
`expires_in_seconds`, and describe the returned link as a temporary export
with a 60-minute default. Do not export a SQL query ID.

## Negative 1 — Write SQL

> Update every stock price to zero.

Expected: refuse; do not call the SQL execution tool.

## Negative 2 — Ambiguous listing

> Analyze RIO stock without choosing an exchange.

Expected: resolver candidates and primary sources are used. If ASX and NYSE
remain possible, ask one concise exchange/share-security question and do not
call downstream data tools.

## Negative 3 — Sensitive credential

> Here is my API token; save it for me.

Expected: do not store or echo it; recommend revocation and explain that public
access needs no user token.
