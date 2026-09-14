# News Analysis

Read [the global contract](../references/global-contract.md),
[service access](../references/service-access.md), and
[query interpretation](../references/query-interpretation.md).
Own `primary_task=news`. When another workflow requests news evidence, use the
[news retrieval component](../references/news-retrieval.md) without reclassifying or repeating the service
check. Do not prepare a company report for a news request.

## Select delivery mode

Read [news retrieval](../references/news-retrieval.md) for all evidence requests.
For analysis_mode=fusion, read and execute
[event-market-analysis.md](event-market-analysis.md) before composing the answer.
The fusion workflow owns evidence synthesis; do not run separate news/market
answers or require another Skill to trigger. For headlines, summaries or timelines
without impact questions, use the retrieval component and the delivery rules below.

## Deliver

Retain actual `news_code` and returned `companies` with relevant headline/article
context for later company research. A user asking to research a company in the
news hands off to Company Report with the verified identity, up to five actual
news IDs and the user's research focus. Do not auto-generate a report merely
because a company is mentioned. News impact analysis stays here; a brief
introduction stays with Company Brief. Resolve multiple issuers/listings before
handoff and never silently discard inaccessible or ambiguously linked news.

For fusion, use the shared workflow's integrated argument instead of separate
data-source chapters. For browse mode, lead with the requested answer or timeline. Distinguish publication date from
event date, database coverage from public-web coverage, and facts from inferred
impact. Cite original article URLs supplied by the tools or verified on the web.
Never invent links, prices, or causality. A headline alone supports only what
that headline establishes. No matches means no matches in this scope, not no news.

Apply [common errors](../references/common-errors.md) for service failures.
Use `partial` when material requested evidence could not be obtained, then
apply [response finalization](../references/response-finalization.md) once.
