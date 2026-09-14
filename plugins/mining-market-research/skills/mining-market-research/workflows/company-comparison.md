# Company Comparison

Do not call `get_company_report` for a comparison; a separately requested full
report belongs to Company Report under the shared routing rules.

Build a source-linked, dimension-by-dimension comparison through Mining Market
Research. Keep the comparative question—not a set of mini reports—as the
organizing principle.

## Establish shared access once

Read [the global contract](../references/global-contract.md) and
[service access](../references/service-access.md). Reuse or obtain one
`get_connection_status({})` result for this request. Follow [update-notifications.md](../references/update-notifications.md)
once per request; check only when the six-hour success cache is due.

## Confirm ownership once

Read
[../references/query-interpretation.md](../references/query-interpretation.md).
Proceed only when `primary_task=comparison`. Do not reclassify the request in
this Skill.

“Compare A and B and briefly say what they do” remains `comparison`; short
business descriptions support the relative answer. “Give A and B separate
three- or four-sentence Briefs, then compare them” remains `company_brief` and
belongs to the sibling Brief Skill.

## Establish access and identities

Reuse the single connection result already obtained
for this request. Never repeat the service check for an attached modifier.

Read
[../references/company-resolution.md](../references/company-resolution.md).
Resolve each selected company separately with `resolve_company_identity`.
Because the MCP enum has no comparison purpose, use
`purpose=company_report` for identity matching only.

That compatibility value does not authorize
`prepare_company_report_generation`. This Skill must never call that tool.

Preserve the user's explicit priority, then current-request order, then the
order of a clearly referenced recent company set. Do not add competitors,
customers, suppliers, or other companies discovered during research unless
the user asks to expand the comparison.

## Execute the comparison

Read
[../references/comparison-workflow.md](../references/comparison-workflow.md).
Use live Host web research for current business, positioning, official
developments, and independent context. Use structured Mining Market Research market tools
only for market-data dimensions the user requested or that are necessary to
support the stated comparison.

The standalone company-introduction window does not limit the comparison
entity set, one-line business context, or comparison matrix. If the number of
companies and requested dimensions would make a meaningful comparison
unreadable, ask one focused scope question or use an explicit user-supplied
grouping. Never silently compare only the first five.

When the user additionally requests a separate three- or four-sentence profile
for every compared company, set `company_introductions=true`, retain
`primary_task=comparison`, and read
[../references/company-introductions.md](../references/company-introductions.md).
The comparison may cover the full resolved set, while the standalone
introduction section uses `current_intro_batch`. Reuse identities already
resolved during this request.

## Answer

Read
[../references/comparison-format.md](../references/comparison-format.md).
Match the user's language, state the comparison basis and dates, and lead with
the most decision-useful differences.

For common access and quota failures, read
[../references/common-errors.md](../references/common-errors.md).
Assign `response_status`, then apply
[../references/response-finalization.md](../references/response-finalization.md)
exactly once.

Call the product **Mining Market Research**. Treat the comparison as analytical
information, not investment advice or official disclosure.
