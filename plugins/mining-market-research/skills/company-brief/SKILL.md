---
name: company-brief
description: Use Mining Market Research to create concise, current 3-4-sentence introductions for one to five public companies when the user asks to understand, introduce, summarize, or get quick context on named companies or companies explicitly referenced from earlier conversation. Cover each company's core business, one dated recent official development, and one dated material independent news item. Use for quick company profiles and multi-company background, including requests such as “what does each company do?” Do not use merely because an assistant response mentions a company, for discovery lists, news-only questions, market-data requests, narrow comparisons, or full/deep company research.
---

# Mining Market Research — Company Brief

Read and follow the complete canonical workflow at
[../mining-market-research/workflows/company-brief.md](../mining-market-research/workflows/company-brief.md).
The linked document is the workflow body for this Skill. Resolve its relative
links from its own directory and do not duplicate, shorten, or reinterpret it.

For EVERY substantive request, execute the shared update `check` once; never
skip it because a previous turn was cached. Reuse only within this request.
Read [update policy](../mining-market-research/references/update-notifications.md)
for host arguments and permission rules. At successful finalization call
`notice`; acknowledge only a notice actually included in the answer.

If the sibling link is absent in a host's flattened Skill mounts, locate the
plugin's `mining-market-research` Skill using the host-provided Skill path and
read its `workflows/company-brief.md` there. Do not guess a sibling directory name.
Resolve all shared references from that actual core directory; read required
files fully. If unavailable, report the limitation instead of inventing rules.
