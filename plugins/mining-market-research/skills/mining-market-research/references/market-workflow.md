# Structured market workflow

Use the primary task, modifiers and ordered entities from
[query interpretation](query-interpretation.md). Do not reclassify the request here.
Read [market-data-policy.md](market-data-policy.md) for the canonical delivery,
count, pagination and export rules.

In fusion mode this file supplies evidence only: retain the owner's primary_task,
reuse checks and identities, and return actual rows/metrics without a separate
answer or finalizer. Do not redirect a news-owned fusion request to market_data.

## Query preparation

1. Reuse or obtain the request's single `get_connection_status`.
2. Resolve each explicitly named company that lacks a verified identity with
   `resolve_company_identity(purpose="stock_data")`. Reuse confirmed exchange,
   ticker and share class. Broad market screens do not require issuer enumeration.
3. Discover supported markets with `get_available_exchanges` when needed.
   For “latest”, use `get_latest_dates` with the required exchange array.
4. Confirm question-relevant fields using `get_stock_schema`. Field selection
   improves performance and does not determine export eligibility.
5. Use `get_available_dates` when the question requires actual trading-date
   selection, e.g. the last 20 trading days. Do not audit coverage for an explicit
   date-range request. Discover physical tables/columns only if SQL is needed.
   Price history uses `stock_daily`; never invent exchange-day table names.

For ambiguous identities, narrow with context or ask one focused question.
For listings outside structured coverage, explain that boundary. Do not switch
listing, exchange or ticker without the user's intent.

## Structured query

Prefer one `screen_stocks` for a single day, a multi-day history, multiple
stocks or multiple months. Cross-exchange named stocks use `instruments` with
exact `exchange`/`ticker` pairs, not independent exchange and ticker lists
that form a cross-product. Follow the active schema's combination rules.

Use `as_of_date` for one date, or `start_date` and `end_date` together.
Do not combine them. Use only discovered fields and supported filter operators.
Use Top-N only when the user wants a bounded ranking, with stable explicit sort;
it is not a page-size or export-eligibility workaround. Use `base_query_id`
only for a user-requested narrower refinement.

The initial call includes the complete logical request and no cursor. Interpret
`data_date` as source freshness, preserve warnings, and handle unknown totals,
cursor pages and export attempts through the canonical policy. A full history
request permits continuation; a CSV-only request does not require page traversal.

## SQL fallback and export

Use `validate_readonly_sql` then `run_readonly_sql` only when a supported
screen cannot express the user's analysis. Discover physical table and column
schemas first. Never add a COUNT(*) merely to fill in an unknown row total.
Use bounded date ranges where they express the user's intent, without silently
shortening the requested period.

For downloads use the original eligible screen/SQL `query_id` in
`create_csv_export`; no complete-partition check or pre-reading all pages.
Actual export results, not preview eligibility, determine whether a file exists.
For continuation use only the cursor and the tool's size field as specified in
[market-data-policy.md](market-data-policy.md).

Never call `prepare_company_report_generation` in this quantitative workflow.
Do not call `get_company_report` either. Preserve actual scope, missing values and incomplete
results in the answer; use [market-answer-format.md](market-answer-format.md).
