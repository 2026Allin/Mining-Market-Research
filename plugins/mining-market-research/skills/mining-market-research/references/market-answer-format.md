# Market analysis answer format

Lead with the requested result. Include source date/range, verified exchange
and company identities, applied filters, calculation basis and material warnings.
Use [market-data-policy.md](market-data-policy.md) for count, continuation and
export decisions; do not introduce additional eligibility or completeness gates.

For analysis_mode=fusion, follow the integrated format in
[../workflows/event-market-analysis.md](../workflows/event-market-analysis.md).
The evidence and numeric scope rules below still apply; do not create a separate
market-data chapter merely because the input came from MCP.

## Evidence scope

Distinguish:
- the actual rows read and used by the host;
- any statistic explicitly calculated over the query by the server;
- the displayed preview;
- an exported file, which need not have been read by the host.

Do not claim full-range analysis merely because server-side analysis is
supported. `matched_row_count=null` means unknown, never zero. For example:
“已读取第 1–200 行，还有后续数据；总行数尚未统计。”
After an exhausted, untruncated query, state the actual accumulated count.
If browsing stopped at a limit or error, identify the analyzed range and avoid
claims about unreceived rows. No cursor alone does not certify completion.

Missing dates/values are not zero, suspension or market closure. Do not fill
them or audit other stocks/the entire market to explain them.
For returns, distinguish price versus total returns, adjustment status, currency
and period endpoints. Describe estimated turnover as an estimate.

Use actual supported markets, not a hard-coded exchange list. Do not describe
public web quotes as MCP structured data.

## Downloads and closing

For a successful `create_csv_export`, show the real temporary HTTPS URL and
returned expiry. Preview eligibility does not prove file creation.
On refusal, explain the actual limit and offer choices without modifying the
user's original query. Do not invent a local path or a downloadable file.

A preview may offer an available next page once. A complete-analysis request
already authorizes necessary pagination; do not interrupt it with page-by-page
consent. If blocked, state the partial scope and relevant options.
Keep the analytical-information caveat concise and apply the shared response
finalizer once. Place the disclaimer immediately before any continuation or semantic
questions required by that finalizer.
