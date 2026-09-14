# Event and market synthesis

This is a shared component, not a new primary task or independently invoked Skill.
The owning news or market workflow calls it for analysis_mode=fusion. Reuse the
request's identity, service access, update check and evidence; finalize only once.

## Required method
Read these references fully before interpreting the evidence:
- [Company-type priorities](../references/mining-analysis-priorities.md)
- [Time alignment](../references/event-time-alignment.md)
- [Market metrics](../references/market-reaction-metrics.md)
- [Macro and metals context](../references/macro-metals-context.md)

Use [news retrieval](../references/news-retrieval.md) and
[market query](../references/market-workflow.md) as evidence components, not
independent deliveries. They must not reclassify, restart, or finalize this task.

## Execute
1. Establish the question, verified listing, observation window and company type.
   Reuse reliable returned companies; resolve incomplete or ambiguous identities.
   Classify from evidence, with multiple types allowed. Light official-source
   verification is enough; never generate a company report just to classify.
2. Load the applicable priorities and identify the economic variable at stake.
   An event-led request starts with the announcement. A market-led request may
   first locate the unusual period, then search relevant issuer news.
3. Retrieve relevant evidence within access and the shared five-article budget.
   Distinguish genuinely new information from repetitions, plans, completions
   and corrections. Retain IDs, sources and publication timestamps.
4. Align publication time and daily bars using the time reference. Query an
   appropriate pre-event baseline plus observable event/post-event rows, using
   one range per compatible query where possible. Map the selected fields to
   the actual schema before submission; analysis-window defaults do not imply
   that matching server indicator columns exist. State baseline scope; never
   expand an explicitly restricted user range. Reuse fetched rows and complete
   necessary cursor pages under market-data-policy.md. Do not audit market
   coverage, invent missing bars, or perform an unsolicited COUNT.
5. Evaluate relative AND absolute volume, persistence, price response and
   relevant technical state. Use verified MCP metrics or the bundled calculator.
   Do not claim a calculation from a script that was never successfully run.
6. Perform targeted host real-time web research for the relevant macro/metals
   channel unless the user excludes it or host access is unavailable. Historical
   analysis searches the historical window, not just today's headlines.
7. Compare the event explanation with sector/metal moves, financing mechanics
   and other actual concurrent events. Identify confirming and disconfirming
   evidence. Unresolved attribution is a valid conclusion.

## Before composing
Check actual evidence, not whether a reference was merely read: company type,
publication anchor, observed price/volume window and metric sample counts,
and macro/metals status (sourced, user-excluded, or unavailable after attempting
research). If a required channel could not be established, mention its effect
on the conclusion in the business answer itself, not only in a diagnostic audit.
Do not imply gold/sector-adjusted confirmation when that comparison was unavailable.

## One answer
Lead with the best-supported interpretation, then connect new event facts,
company-specific economic significance, observed price/volume and external
context in the same argument. Organize by judgments, not separate chapters
for news, stocks and macro. A compact aligned evidence table may support it.
Keep source identities and dates explicit; combining reasoning is not merging
provenance. An event's economic significance and its observed market reception
can disagree. Explain that disagreement instead of forcing one verdict.

Give evidence strength and its reason, not invented probabilities or scores.
Name observable facts that would strengthen/weaken the interpretation without
creating a monitor. Do not infer insider trading, trader identity, money inflows
or causality from daily volume. No automatic report, CSV, target price or trade.
If a required evidence channel is unavailable, state the partial scope and
avoid whole-period or causal claims. Return to the owner for attached modifiers
and one finalization; do not publish, upload or persist research automatically.
