# News Analysis

Read [the global contract](../references/global-contract.md),
[service access](../references/service-access.md), and
[query interpretation](../references/query-interpretation.md).
Own `primary_task=news`. When another workflow requests news evidence, use the
same retrieval component below without reclassifying or repeating the service
check. Do not prepare a company report for a news request.

## Retrieve evidence

1. Reuse or obtain one `get_connection_status({})` result for this request.
   Respect the current NEWS_ACCESS option. Never infer access from a cached
   plugin contract or attempt to broaden the server's ceiling.
2. Call `list_news_filters` before choosing tags or exchange facets. Map the
   user's language to official returned English facets; do not invent values.
3. For issuer-specific news, resolve the issuer using `resolve_company_identity`.
   Send `exchange` and `ticker` together only when resolved. Otherwise search
   verified company terms in `q` and disclose identity uncertainty.
4. Call `search_news`: `q` contains the relevant user request plus English search
   terms, at most 200 characters. Keep meaning when shortening; do not send the
   full conversation. Use published-date bounds within the 365-day maximum.
   Tags and exchanges outside the access option reject the query. Do not drop
   requested filters to bypass this rejection; disclose the unavailable scope.
   Validate facets against list_news_filters and follow the currently loaded
   schema's limits. Verify returned scope before claiming the filter was enforced.
5. Review headline cards first. Deduplicate repeated coverage and select only
   articles relevant to the question. Call `get_news_article` with exact
   `news_code` values from these cards, at most five calls across the entire
   user request, including attached workflows. A returned body may be truncated;
   do not present it as the full original article.
6. For an empty corpus result or requested latest public coverage after the
   database search, call `prepare_news_web_research` with `q` and optional
   `tags`/`exchanges`. It accepts no `web_q`, ticker, or date parameters.
   This prepares instructions only: execute relevant research using the host's
   web capability. Preserve the user's date and company scope on the host.
   If web access is unavailable, deliver the supported evidence and clearly
   mark the missing supplement. Do not describe a prompt as completed research.

News pages contain at most 50 cards. Continue only on an explicit user request,
using the exact opaque cursor and optional page_size, not the original filters.
Never enumerate the corpus, bypass NEWS_ACCESS, or fetch every article.

## Deliver

Lead with the requested answer or timeline. Distinguish publication date from
event date, database coverage from public-web coverage, and facts from inferred
impact. Cite original article URLs supplied by the tools or verified on the web.
Never invent links, prices, or causality. A headline alone supports only what
that headline establishes. No matches means no matches in this scope, not no news.

Apply [common errors](../references/common-errors.md) for service failures.
Use `partial` when material requested evidence could not be obtained, then
apply [response finalization](../references/response-finalization.md) once.
