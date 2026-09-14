---
name: news-analysis
description: Research mining, market, and company news with Mining Market Research. Use for headlines, recent events, catalysts, news timelines, and announcement-led market impact. Search the news corpus first and supplement with host web research when needed. Do not replace a full company report, company introduction, or quantitative market analysis.
---

# Mining Market Research — News Analysis

Read and follow the canonical workflow at
[../mining-market-research/workflows/news-analysis.md](../mining-market-research/workflows/news-analysis.md).
Resolve its relative links from its own directory.

For event impact or price/volume explanations, follow the owning workflow's
fusion branch and its shared company-type priorities and macro web research.
Do not assume another Skill or the coordinator has loaded those rules.
Headline-only and CSV-only tasks keep their lightweight paths.

For every substantive request, reuse this request's successful Hook check and
context_file, or execute the shared `check` fallback; never create a parallel cache.
Read [update policy](../mining-market-research/references/update-notifications.md)
for host arguments and permission rules. At successful finalization call
`notice`; acknowledge only a notice actually included in the answer.

If the sibling link is absent in a host's flattened Skill mounts, locate the
plugin's `mining-market-research` Skill using the host-provided Skill path and
read its `workflows/news-analysis.md` there. Do not guess a sibling directory name.
Resolve all shared references from that actual core directory; read required
files fully. If unavailable, report the limitation instead of inventing rules.
