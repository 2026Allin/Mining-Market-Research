# Company Brief

This workflow must not call `get_company_report`; viewing/researching a full
report belongs to Company Report, not a concise introduction.

Create compact, source-linked company snapshots through Mining Market Research
without entering the seven-section company-report workflow.

## Establish shared access once

Read [the global contract](../references/global-contract.md) and
[service access](../references/service-access.md). Reuse or obtain one
`get_connection_status({})` result for this request. Follow [update-notifications.md](../references/update-notifications.md)
once per request; check only when the six-hour success cache is due.

## Classify once

Before doing any research, read the canonical arbitration rules in
[../references/query-interpretation.md](../references/query-interpretation.md).
Proceed only when the resulting `primary_task` is `company_brief`. Do not
reclassify the request inside this workflow.

The user's intent must request or semantically require a separate quick
understanding of each company. Company names may come from the current request
or an explicit reference to the most recent relevant company set. Company-name
presence alone is not sufficient. Set `company_introductions=true`.

## Apply public service access

Reuse the single connection result already obtained
for this request. Apply the shared public-access, credential, privacy, outage,
and retry rules. Never repeat the service check for a modifier.

## Execute the shared introduction component

Read
[../references/company-introductions.md](../references/company-introductions.md)
and apply it to the ordered companies from the current request or explicit
recent-context reference. It owns ordering, the five-company window, identity
resolution, current web research, and the three- or four-sentence format.

Do not call `prepare_company_report_generation`. If the user explicitly asks
for a short comparison after the introductions, add one compact synthesis
paragraph after the completed introduction batch without expanding the entity
set.

## Finalize once

For common access or quota failures, read
[../references/common-errors.md](../references/common-errors.md).

After the component assigns `response_status`, read
[../references/response-finalization.md](../references/response-finalization.md)
exactly once. Call the product **Mining Market Research** in user-facing text.
