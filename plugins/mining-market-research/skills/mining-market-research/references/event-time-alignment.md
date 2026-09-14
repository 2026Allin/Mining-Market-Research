# Publication time and daily observations

The current news surface provides published_at, not a dedicated event date.
Use it as the known publication anchor, not proven first public disclosure.
Do not invent event_at, acquisition time or an intraday bar.

Check an earlier official disclosure when pre-news activity, a repeated article,
"previously announced", a correction, or the user's question makes it relevant.
Preserve the original timestamp and any verified earlier disclosure with sources.
Deduplicate syndicated repetitions; a material update may be a separate event.

## Align only with evidence
Use an explicit offset or verified source timezone; IANA exchange timezone and
dated session information must account for DST, special schedules and auctions.
Do not hard-code current UTC offsets or derive sessions from missing stock rows.
Near uncertain opening/closing auctions, classify as uncertain, not confidently
pre/post-market. A verified halt needs separate evidence.

| Timing | Daily-data treatment |
|---|---|
| Before session | Same session is the first possible response window |
| During session | Same-day bar mixes pre/post publication; inspect subsequent sessions |
| After session | Next actual tradable session is first possible response |
| Non-trading date | Next verified tradable session, not simply calendar date + 1 |
| Unknown timezone/time/session | Date-level comparison only, attribution limited |

Record both first possible response session and first observed bar when they
differ. Missing rows do not imply suspension, holidays or zero trading.

For intraday publication, never call the entire daily return/volume "after
the announcement". Daily data cannot establish minute-level sequencing,
order flow, buyer identity or net capital flows.

Use get_latest_dates when needed to establish the available daily cutoff.
If complete bars end before the response session, report event significance
and pre-news conditions; observed market response is not yet available.
Never fill future +1/+3/+5 windows or compare incomplete current-day volume
with full-session baselines. For historical reasoning distinguish information
known then from later evidence; do not use future news as contemporary proof.

The calculator accepts optional verified session intervals from the host.
It has no exchange calendar and must not be used to invent one.
