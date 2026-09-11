---
name: market-analysis
description: Analyze structured stock-market data through Mining Market Research, including supported-exchange discovery, latest dates, prices, returns, technical indicators, full-range server-side screens, rankings, historical comparisons, bounded read-only stock SQL, and selective research CSV exports. Use when the primary deliverable is quantitative market data or supported-market instrument discovery, including screens that additionally request standalone introductions for the resulting companies. Do not use when introductions are the primary deliverable, for a full company report, a narrative company comparison, news-only work, official filings, or incidental company mentions.
---

# Market Analysis

Read and follow the complete canonical workflow at
[../mining-market-research/workflows/market-analysis.md](../mining-market-research/workflows/market-analysis.md).
The linked document is the workflow body for this Skill. Resolve its relative
links from its own directory and do not duplicate, shorten, or reinterpret it.

For EVERY substantive request, execute the shared update `check` once; never
skip it because a previous turn was cached. Reuse only within this request.
Read [update policy](../mining-market-research/references/update-notifications.md)
for host arguments and permission rules. At successful finalization call
`notice`; acknowledge only a notice actually included in the answer.

If the sibling link is absent in a host's flattened Skill mounts, locate the
plugin's `mining-market-research` Skill using the host-provided Skill path and
read its `workflows/market-analysis.md` there. Do not guess a sibling directory name.
Resolve all shared references from that actual core directory; read required
files fully. If unavailable, report the limitation instead of inventing rules.
