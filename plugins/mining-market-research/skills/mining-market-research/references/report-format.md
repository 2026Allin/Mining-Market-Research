# Company report answer format

Lead with the finding and return the completed source-linked report in the
current conversation. Do not show `prompt_text`.

## Existing report: faithful presentation or translation

For `report_available`, show the original `report.generated_at`. Preserve its
timezone; if converting, explicitly label the target timezone. Never replace it
with today's date or infer report validity from age.

For Chinese output, introduce it as “以下为 <原生成日期及必要时区> 生成的英文报告的中文译文。”
Translate summary and sections into the requested language, preserving numbers,
currencies, citations, risk rating and structure. Do not inject new facts,
force seven sections, invent missing risk ratings, or label a translation as
new research or the latest study. Preserve original citations without claiming
to have freshly checked them. No web access is needed to translate supplied content.

When `presentation.report_predates_linked_news=true`, add “这份报告早于当前新闻，
可能尚未反映该事件。” Do not recompute this flag from timestamps.

Ask “是否结合最新公告与新闻，重新生成一版？” once, subject to explicit no-question
user constraints. This replaces the usual semantic follow-up, not an extra
question. Keep any explicitly requested current market analysis in a separate,
dated section outside the translation. Then apply the shared finalizer.

## Newly researched report

For `generation_ready` (or explicit preparation `ready`), use:

- one localized `**Summary:**` paragraph
- all seven fixed English headings in the required order
- localized section bodies
- exact dates or reporting periods
- links placed next to the material claims they support
- exactly one report-closing English `**[Risk: Low]**`,
  `**[Risk: Medium]**`, or `**[Risk: High]**` label with justification,
  placed before any question required by the shared response finalizer

When `identity_source=host_supplied` or listing verification is required,
describe material identity or status findings with primary-source links. Do
not claim that Mining Market Research verified an external identity. If the record
is an ETF or Fund, explain why an operating-company report is not appropriate.

Do not claim that the report was saved, uploaded, published, sent back to MCP,
or made available as a file.

For a mixed request, complete the report before a distinct quantitative
market-data section. State the structured data date or range, filters, missing
values, warnings, and preview limits. Do not merge narrative web evidence with
calculated observations.
