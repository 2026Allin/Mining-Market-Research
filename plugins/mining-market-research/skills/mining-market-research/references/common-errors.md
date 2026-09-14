# Common error handling

Follow safe returned guidance without probing hidden state:

- `rate_limited`: retry only after the supplied delay when a retry remains
  useful.
- `concurrency_limited`: wait for the existing query to finish; do not start a
  retry loop.
- `usage_limit_exceeded`: state the returned reset information. Do not invent
  usage counts or reset dates.
- `resource_not_found`: rerun the original workflow only when needed; never
  edit or probe an opaque capability.
- `service_not_activated`, an authentication challenge, or HTTP 503: stop,
  state the public-service condition, and suggest retrying later without an
  automatic loop.

Do not reveal internal request, connection, policy, or principal identifiers.
Preserve user-safe warnings and recovery guidance returned by the service.
Workflow-specific report and market-data errors remain with their owning
Skills.
# Company-report selection failures

For `get_company_report`, unknown states, missing report content, malformed
refresh actions, or identity mismatches are not cache misses. Explain the
limitation; do not silently use fresh preparation. Report calls require
`stock.read` and linked `news_codes` additionally require `news.read` where
scope-based authorization applies. Never remove news IDs or research focus to
bypass access/association errors. Noauth mode does not require users to log in.
If the new tool is absent from the loaded catalog, explain that reconnecting
or a new session may be needed; never claim to have invoked it.

## Fusion evidence limitations
Unknown publication timezone/session permits date-level analysis only. A daily
cutoff before publication cannot establish post-news reaction. Missing baseline,
zero baseline or incompatible price/volume basis makes the affected metric
unavailable. Macro web failure limits external attribution. Report partial scope
without inventing timestamps, observations or metrics. Never manufacture another
issuer, drop news filters, or generate a report to work around unavailable data.
