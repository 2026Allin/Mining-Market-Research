# News retrieval component

Use inside the owning workflow, without reclassification or separate delivery.
Reuse already verified identities, filters and article bodies within this request.
A user-provided real article ID may be read directly; do not guess IDs or search
again solely to rediscover an already selected card.

1. Reuse or obtain one `get_connection_status({})` result for this request.
   Respect the current NEWS_ACCESS option. Never infer access from a cached
   plugin contract or attempt to broaden the server's ceiling.
2. Call `list_news_filters` before choosing tags or exchange facets. Map the
   user's language to official returned English facets; do not invent values.
3. For issuer-specific news, reuse a verified issuer or resolve it using `resolve_company_identity`.
   Send `exchange` and `ticker` together only when resolved. Otherwise search
   verified company terms in `q` and disclose identity uncertainty.
4. Call `search_news`: `q` contains the relevant user request plus English search
   terms, at most 200 characters. Keep meaning when shortening; do not send the
   full conversation. Use published-date bounds within the 365-day maximum.
   Tags and exchanges outside the access option reject the query. Do not drop
   requested filters to bypass this rejection; disclose the unavailable scope.
   Validate facets against list_news_filters and follow the currently loaded
   schema's limits. Verify returned scope before claiming the filter was enforced.
   For a latest-headlines request fully expressed by supported facets/issuer/date
   filters, omit optional q when the active schema supports facet-only browsing.
   Do not add generic English words such as "latest news mining" that create an
   unintended full-text restriction. Retain genuine topic/search constraints;
   never remove them merely to obtain results. Verify the returned search mode.
5. Review headline cards first. Deduplicate repeated coverage and select only
   articles relevant to the question. Call `get_news_article` with exact
   `news_code` values from these cards, at most five calls across the entire
   user request, including attached workflows. A returned body may be truncated;
   do not present it as the full original article.
   A metal tag can include a by-product or incidental mention; do not equate
   "gold-tagged" with "primarily gold". Match the requested focus using available
   card/body evidence and label a tag-only selection honestly. Empty attachment
   placeholders are not substantive articles; skip them without inventing text.
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


Return evidence to the owner: actual IDs, company links, publication timestamps,
new facts, source URLs and truncation/access limits. No independent finalization.
