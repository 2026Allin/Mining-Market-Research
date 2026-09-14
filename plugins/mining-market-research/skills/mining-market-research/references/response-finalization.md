# Global response finalization

Apply this policy exactly once after the answer body, data caveats, and
analytical-information disclaimer are ready. The substantive answer and the
operational plugin-update footer are separate. Finalize all business questions
first. Follow [update-notifications.md](update-notifications.md) for the
six-hour agent-driven probe and once-per-cycle notice reservation. No update
text appears without a validated `update_available` or `reload_required` notice.
Explicit diagnostic or update operations consult [plugin-update.md](plugin-update.md).

In fusion mode finalize once after all evidence components. Do not offer market
reaction or macro analysis already completed. A relevant unanswered validation
question may be used; naming a future signpost does not schedule monitoring.
For partial fusion with no remaining introductions, state the missing evidence;
ask a recovery question only if needed, not a mandatory extra semantic question.

## Determine whether the answer is substantive

Treat a successful Brief, full report, company comparison, news analysis,
market screen, ranking, historical analysis, or quantitative interpretation as
substantive. A connection-status receipt, export link, or similarly narrow
operation may use `response_status=mechanical_result`.

For `primary_task=diagnostics`, use the fixed mechanical receipt in
[diagnostics.md](diagnostics.md). Do not add an analytical-information
disclaimer, business suggestion, recovery advice, continuation question, or
semantic question. Append the fixed update notice only for a validated
`update_available` result.

## Apply the question matrix

Use `suggestions_allowed=false` when the user asks for no suggestions,
recommendations, next steps, or follow-up questions.

| `response_status` | Suggestions | Remaining introductions | Required ending |
|---|---|---|---|
| `success` | allowed | none | exactly one semantic question |
| `partial` | allowed | present | one continuation question, then one semantic question |
| `success` | disallowed | none | no question |
| `partial` | disallowed | present | exactly one continuation question |
| `needs_clarification` | either | either | exactly one focused clarification question |
| `failed` | either | either | no semantic question; give safe recovery guidance |
| `mechanical_result` | either | either | no question required |

A continuation question is necessary to finish the original request and is not
an optional product suggestion.

## Write continuation questions

When `remaining_intro_entities` is non-empty:

- Preserve their established order.
- For a concise explicit or contextual set, list every remaining company.
- For a long discovered set already shown in a ranked table, state the
  remaining count and ask whether to continue with the next five in that order
  or select companies from the table.
- Never ask to refresh or rerun the owning workflow unless the user requested
  fresh data.

## Choose one semantic question

For `full_report` with `report_available`, the report-refresh question defined
in [report-format.md](report-format.md) replaces the semantic question below.
Do not add a peer/market/risk follow-up as a second question. Honor explicit
no-question constraints. Keep any plugin upgrade footer clearly labeled as
plugin installation, not company-report refresh; ambiguous assent must be
clarified, never treated as permission to install software.

Choose the most relevant unanswered direction for the completed work:

- `company_brief`: comparison, developments, catalysts and risks, market
  performance, or a full report for one completed company
- `full_report`: requested market measures, peer comparison, or a deeper
  examination of one unresolved catalyst or risk
- `comparison`: expand the comparison set, add market measures, or produce a
  full report for one compared company
- `market_data` or structured `discovery`: narrow the screen, introduce
  selected result companies, compare catalysts, or prepare a focused export
- `news`: assess impact, compare affected companies, or inspect market reaction

When introductions remain, the semantic question may concern only
`current_intro_batch`, even when the owning table displayed more companies.

Inspect the two most recent assistant messages. Classify their semantic
follow-ups by the families above, ignoring continuation questions. Exclude a
recent family when another relevant unanswered family exists. Reuse it only
when alternatives would be materially irrelevant, and avoid near-duplicate
wording.

Never use a generic question such as “Anything else?” Never offer work already
completed. Do not randomly rotate question families.

## Preserve final order

Use this order:

```text
answer body
-> data and risk caveats
-> analytical-information disclaimer
-> continuation question, when required
-> semantic question, when required
-> operational update footer, only when required
```

When a semantic question is required, it must be the final sentence of the
business answer. When only a continuation question is required, it must be the
final sentence of the business answer. An operational update footer may follow
as a separate final paragraph; it never replaces, merges with, or answers a
business question.

For business answers, the session-only notice reservation is authoritative.
`silent`, `cached`, `busy`, `check_required`, failed checks and unsuitable answers produce no
update text. A decline or ignored question does not reset the successful-check
clock: the next plugin use after six hours may remind again, even for the same
release. No permanent opt-out or ignored-version state exists. See
[update-notifications.md](update-notifications.md) for reservation/acknowledgement.
Explicit operations use their own requested status response.
