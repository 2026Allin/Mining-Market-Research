---
name: company-report
description: View or faithfully translate existing Mining Market Research company reports, or perform live source-linked research when requested or prepared by MCP. Use for company report requests, deep research, due diligence, report refresh confirmations, and company research linked to news. Do not use for concise introductions, news-only impact analysis, official filing retrieval, narrow comparisons, incidental company mentions, or market-data-only work.
---

# Mining Market Research — Company Report

Read and follow the complete canonical workflow at
[../mining-market-research/workflows/company-report.md](../mining-market-research/workflows/company-report.md).
The linked document is the workflow body for this Skill. Resolve its relative
links from its own directory and do not duplicate, shorten, or reinterpret it.

For EVERY substantive request, execute the shared update `check` once; never
skip it because a previous turn was cached. Reuse only within this request.
Read [update policy](../mining-market-research/references/update-notifications.md)
for host arguments and permission rules. At successful finalization call
`notice`; acknowledge only a notice actually included in the answer.

If the sibling link is absent in a host's flattened Skill mounts, locate the
plugin's `mining-market-research` Skill using the host-provided Skill path and
read its `workflows/company-report.md` there. Do not guess a sibling directory name.
Resolve all shared references from that actual core directory; read required
files fully. If unavailable, report the limitation instead of inventing rules.
