# Reaction metrics

Read market-data-policy.md for query/pagination constraints. Existing MCP
indicators take priority when their period, date and methodology fit. Never
rename rsi_10 to RSI14 or use today's indicator to explain a historical event.
Analytical windows below are NOT MCP column names. Before querying, map every
requested field to the actual get_stock_schema result. Never synthesize names
such as avg_volume_20day from a preferred 20-observation baseline. If the schema
only supplies a 30-day average, either use and label that exact definition or
calculate the desired baseline from actual volume rows; do not rename it.
Keep range-query fields compact (relevant OHLCV, basis and needed indicators).
Do not repeat bulky market-cap inputs or issuer metadata on every historical
row merely to classify company size. Reuse verified snapshots where available.

## Minimal useful measures
- Price change using actual endpoint dates and consistent raw/adjusted basis.
- Opening gap and open-to-close change only from compatible OHLC observations;
  they are not pure causal event effects.
- Relative volume versus preceding observations, excluding the evaluated day.
  Default 20 observations; show valid sample count. Retain real zero volumes.
- Historical volume percentile when useful (default 60 observations), with
  ties and sample size disclosed; not a significance test.
- Persistence across observed sessions, not a universal "volume leads price" rule.
- Relative benchmark return only on matching dates, currency/return definitions
  and appropriate exposure; subtraction is not a factor-model abnormal return.

A pre-event-only normalization and a rolling baseline answer different questions.
Label the chosen basis. Short defaults are analyst conventions, not service gates.
Absolute volume matters alongside a ratio. Use actual traded value where available;
close times volume is only an estimate. Turnover needs dated, compatible share data.
A zero baseline, insufficient sample or incompatible corporate-action basis makes
a metric unavailable, not infinity or zero. Do not claim database completeness.

## Bundled calculator
Run scripts/event_market_metrics.py from the core Skill directory with JSON
on stdin; it reads no network, writes no files and does not query MCP.
Use ordinary non-interactive stdin; no PTY or interactive terminal is needed.
Adapt real tool rows explicitly, retain query IDs outside the calculator, and
never create synthetic observations to complete history.

Input version 1:
```json
{
  "schema_version": 1,
  "baseline_window": 20,
  "percentile_window": 60,
  "min_samples": 10,
  "price_basis": "raw",
  "volume_basis": "raw",
  "rows": [
    {"exchange":"ASX","ticker":"BHP","date":"2026-09-01",
     "open":40.0,"high":41.0,"low":39.0,"close":40.5,"volume":1000000}
  ]
}
```
Keys are normalized input names, not an MCP schema. Null is missing, zero volume
is observed zero. Each row is a completed daily bar for one exact listing.
Choose consistent series; do not mix raw/adjusted values within a listing.
Provide all actual rows needed for the requested calculation, not just a preview.
For unknown price or volume basis, use "unknown"; affected metrics are withheld.
Optional publication alignment: published_at with UTC offset and sessions
[{date, open_at, close_at}], each with explicit offsets and verified bounds.
Omit sessions if unknown. The script does not determine first public disclosure.

Output includes per-listing dates, row counts, missing counts, endpoint return,
average volume, per-observation gap/return/RVOL and historical midrank percentile,
sample counts, warnings, and formulas. Ratios use preceding rolling observations.
Select the relevant event windows from actual dated results in the host.
Unsupported/malformed inputs return an error; never present them as results.
Consume the calculator JSON programmatically and select relevant dated metrics,
sample counts and warnings for inspection if full-series stdout would be clipped.
Do not repeatedly dump an oversized result or treat clipped output as fully read.

Use the calculator for multi-row baseline statistics when needed, or an
equivalent transparent host calculation retaining the exact input rows.
If execution is unavailable, use verified returned metrics or qualitative
analysis; disclose unavailable calculations. No prediction, score or trading action.
