---
name: news-analysis
description: Research mining, market, and company news with Mining Market Research. Use for headlines, recent events, catalysts, or news timelines as the primary deliverable. Search the news corpus first and supplement with host web research when needed. Do not replace a full company report, company introduction, or quantitative market analysis.
---

# News Analysis

Read and follow the canonical workflow at
[../mining-market-research/workflows/news-analysis.md](../mining-market-research/workflows/news-analysis.md).
Resolve its relative links from its own directory.

For EVERY substantive request, execute the shared update `check` once; never
skip it because a previous turn was cached. Reuse only within this request.
Read [update policy](../mining-market-research/references/update-notifications.md)
for host arguments and permission rules. At successful finalization call
`notice`; acknowledge only a notice actually included in the answer.

If the sibling link is absent in a host's flattened Skill mounts, locate the
plugin's `mining-market-research` Skill using the host-provided Skill path and
read its `workflows/news-analysis.md` there. Do not guess a sibling directory name.
Resolve all shared references from that actual core directory; read required
files fully. If unavailable, report the limitation instead of inventing rules.
