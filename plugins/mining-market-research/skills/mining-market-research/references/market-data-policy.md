# Market-data results, pagination and exports

This is the canonical rule source for previews, complete-history analysis and
CSV downloads. Other market workflows reference it rather than redefining gates.

The maintainer-owned bundled policy is not a user setting. Never mention it,
offer a setting for it, or send it to MCP; neither state restores removed checks.

## Preserve the requested query

Use the requested exchanges, verified instruments, dates and fields. Do not
add filters, Top-N, ticker exclusions or shorter dates to obtain export eligibility.
Select relevant fields for performance; explicit fields are not an export prerequisite.
The bundled policy cannot reintroduce checks removed from MCP in either state.

Present database results faithfully. Missing values are not zero; absent rows
are not evidence of suspension or market closure. Do not fill missing dates,
prices or volumes. Do not audit full-market or all-trading-day coverage, compare
against other issuers, or issue a COUNT(*) to certify completeness. Counting is
appropriate only when the user requests a count/statistic, not as a hidden check.
Distinguish completion of this query from completeness of the database.

Do not read or depend on `contains_complete_partition`; its absence is normal.
Do not infer whether the result contains every stock in an exchange-day.
Do not create a local export-size or market-completeness checker. The service
owns access and resource limits; never evade an actual refusal by splitting
filters, dates, tickers, fields or files.

## Choose the delivery mode

- Preview: read the requested page, state the observed range and offer a next
  page only when available. Do not fetch unrequested pages.
- Complete historical analysis: the user's request authorizes necessary cursor
  continuation of the same query; do not ask for permission after every page.
  Accumulate the returned pages needed for the analysis, within actual limits.
- CSV only: after the first query yields an eligible query ID, attempt export
  immediately. Reading all preview pages is not required.
- Analysis plus CSV: track these separately. Export success does not prove that
  the host read or analyzed all rows; an analyzed preview is not full history.

## Counts and continuation

`data.analysis.matched_row_count=null` means the total has not been counted.
It is not zero, failure or an empty result. Use the actual rows and displayed
range. If total count is unknown, say “已读取 200 行，还有后续数据；总行数尚未统计”
when a cursor exists; never claim 200 is the total. Do not add a counting query.

Read the next cursor only from top-level `page.next_cursor`. For continuation
use the same tool with only that unmodified cursor and its optional size:
`screen_stocks`: `page_size`; `run_readonly_sql`: `max_rows`.
Never resend instruments, exchanges, filters, fields, dates, sort, Top-N,
base_query_id or SQL. Do not construct/decode a cursor or move it between tools.

Check `page.truncated` AND `data.analysis.pagination_limit_reached`, alongside
the cursor and any returned next-action/warnings:
- A valid cursor with no reached limit allows continuation in the selected mode.
- A reached limit, refinement requirement or truncation without a cursor means
  the complete result has not been obtained. Stop and state the retrieved scope.
- No cursor alone, or `pagination_next_action=none` alone, is not proof of
  completeness. Only finish as complete when the returned indicators agree
  that no rows remain; unknown/conflicting indicators require a qualified answer.

Stop on repeated/non-progressing cursors, an expired cursor, a service refusal
or failure. Never silently restart, splice a new query into old pages, or claim
whole-period statistics from a partial series. Preserve the original intent and
explain the limitation. For a user-requested metric that can be aggregated by the
server, prefer that supported aggregate over needless row transfer; this does
not authorize an extra completeness/count audit.

## Host output truncation (not a service limit)

A host may shorten the visible tool message even when the service page itself
is complete. That does not mean the model has retained all returned rows.
Prefer consuming the intact native structured result programmatically when the
host exposes it. Never claim access to a hidden object that is not available.

Do not repeat an identical oversized request hoping to recover hidden rows.
If only the host display was truncated, recover once by restarting the SAME
logical scope with a smaller display page (for example page_size=25), retaining
all user-required fields. Follow that new query's cursor through all needed
pages; do not splice the lost original page into the restarted result. Explain
the recovery in diagnostics, not as a change to the user's requested range.
If messages still cannot be retained, disclose partial evidence and stop retrying.
This exception does not permit restarting after a service refusal, a reached
browsing limit or a non-progressing cursor; those remain stopping conditions.
For anticipated large baseline data, choose a retainable display page initially;
200 is a ceiling, not a mandatory page size.

## CSV exports

Use `create_csv_export` only for a user-requested download with the original
query's current `query_id`, `data.export_policy.eligible_by_query=true`, and an
allowed source tool in `source_tools_allowed`. Do not query other data to
revalidate eligibility, count rows, check policy freshness or estimate file size.
An expired query response is handled when actually returned.

`eligible_by_query=true` is provisional when the count is unknown; it permits
an export attempt, not a promise of a file. The actual export response determines
success. MCP checks rows, columns, cells and bytes during export replay.
Do not pre-reject complete exchange-day results, omitted fields or SQL exports.

On success, deliver the returned temporary HTTPS URL and expiry. Do not invent
a file, local path or link. Omit `expires_in_seconds` for the default lifetime,
or use the bounds in the active schema (currently 60 through 3,600 seconds,
default 60-minute lifetime). Protect query IDs and bearer download URLs
from unrelated sharing.

On an actual size/row/column/cell or other resource refusal, explain the returned
reason and offer scope choices. Do not execute a shortened date range, smaller
field set, Top-N or replacement ticker set until the user chooses it.
Preserve valid analysis when only export fails. For temporary unavailability,
offer a later retry without changing the query. For an expired query ID, rerun
the original query unchanged if still authorized; use its new ID and do not mix
old and new analysis pages. Bound retries; never loop on a repeated failure.
Do not maintain legacy complete-market denial rules or proactively apply old
error codes. Explain any unexpected actual refusal without rebuilding its logic.

## SQL boundary

Prefer `screen_stocks` for single-day, multi-day and multi-stock requests.
Only use SQL for a requested analysis that the screen cannot express: one
allowlisted read-only SELECT or WITH ... SELECT, validated before execution.
Use stable ordering for row pagination and never SQL OFFSET. Ordinary cursor
accumulation for requested full analysis is allowed; reconstructing a refused
dataset through alternate queries is not.
