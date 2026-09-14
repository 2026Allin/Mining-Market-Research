---
name: market-analysis
description: Analyze structured stock-market data through Mining Market Research, including prices, returns, screens, rankings, multi-stock historical analysis, and CSV downloads. Use for quantitative market data, unusual-volume or price-move explanations, or supported-market discovery, including screens with attached company introductions. Do not use for full company reports, narrative company comparisons, news-only work, or introductions as the primary deliverable.
---

# Mining Market Research — Market Analysis

Read and follow the complete canonical workflow at
[../mining-market-research/workflows/market-analysis.md](../mining-market-research/workflows/market-analysis.md).
The linked document is the workflow body for this Skill. Resolve its relative
links from its own directory and do not duplicate, shorten, or reinterpret it.

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
read its `workflows/market-analysis.md` there. Do not guess a sibling directory name.
Resolve all shared references from that actual core directory; read required
files fully. If unavailable, report the limitation instead of inventing rules.
