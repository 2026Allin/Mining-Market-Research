---
name: mining-market-research
description: Coordinate Mining Market Research for product health, status, connection, access, plugin-version/current checks; install, update, or release-check permission requests; mixed deliverables; or ambiguous requests. For any Mining Market Research status request, run unified diagnostics by calling mining_market_research:get_connection_status once and independently reading the active host's bundled release metadata and running its Tag checker; never stop after service status. Return every fixed receipt field—service, access, coverage/data policy, platform/current version, update status, and check source—in the user's language, without business advice or follow-up. Otherwise classify exactly one primary task and route to plugin operations, Company Brief, Company Report, Company Comparison, Market Analysis, or News Analysis under the shared contract. Do not replace a clearly matching specialized Skill, trigger on unrelated health/status, treat incidental company mentions as research, retrieve filings.
---

# Mining Market Research

Act as the thin coordination entry for the Mining Market Research plugin. Let users
ask in natural language; do not require tool names, SQL, schemas, tickers,
credentials, or local setup.

## Route operational intent first

First distinguish a pending company-report refresh from a plugin upgrade.
Unambiguous assent to refreshing a report goes to Company Report and its
validated `refresh_action`, not installation. Clarify when both are pending.

For Claude Chat, read [the Chat adapter](references/hosts/claude-chat.md).
Use the [shared routing contract](references/runtime-routing.md) for task selection.
For no-Hook or connector-only access, read [remote MCP boundaries](references/hosts/remote-mcp.md).
Its session-only release checks and manual-update rules override native CLI
checks in the diagnostic gate below; preserve the independent service check.

For an explicit plugin-only update check or upgrade, including `$upgrade`,
read [workflows/upgrade.md](workflows/upgrade.md) and execute that dedicated
workflow without MCP. Check-only bypasses the TTL and never installs. This
rule takes priority over the general product diagnostics below.

When the user explicitly asks to inspect Mining Market Research health, status,
connection, access, plugin version, update availability without installation,
or whether the product is available and current, set
`primary_task=diagnostics`. Require Mining Market Research context or explicit
`$mining-market-research` or `/mining-market-research` invocation; unrelated uses of
“health”, “status”, “connection”, or “version” do not trigger it. This route
has priority over business classification and bypasses
`query-interpretation.md`.

For `primary_task=diagnostics`, execute this completion gate before answering:

1. Read [references/diagnostics.md](references/diagnostics.md) and the one
   active-host adapter and release file it names. Treat these reads as required
   diagnostic work, not optional background.
2. Call `mining_market_research:get_connection_status` exactly once with `{}`.
3. Run the selected host's bundled release checker once as defined in the
   diagnostic reference. Initialize once per conversation, then reuse context_file
   for check. Normal status uses the session cache; explicit update checks use
   --force. Never use the legacy disk cache or native inventory for this check.
4. Populate both `diagnostic_service_check` and `diagnostic_plugin_check`
   before composing the response. `unknown` is a valid terminal plugin-check
   result. A successful service call never permits skipping the plugin check,
   and a plugin-check failure never permits dropping the service result.
5. Return the fixed receipt below in the user's language. For Chinese, use
   these labels in this order and include every line:

   ```text
   Mining Market Research 状态

   - 服务：<可用 / 不可用 / 无法确认>
   - 访问：<无需登录 / OAuth / 待批准 / 无法确认等>
   - 覆盖与数据策略：<简要摘要>
   - 插件：<Codex 或 Claude>，当前版本 <x>
   - 更新：<已是最新版 / 可更新到 y / 插件版本暂时无法确认>
   - 检查来源：<最近有效结果 / 刚刚重新检查>
   ```

If Skill-file reading, shell execution, permission, or network access is
unavailable, record the affected plugin result as `unknown`, obtain the
current version from the selected bundled release metadata when readable, and
still return all receipt lines. Never replace the fixed Tag check with MCP,
web search, or a guessed version. Do not expose raw errors. Execute the
diagnostic and stop; do not continue to the business check or business
classification below.

For every non-diagnostic Mining Market Research request, read
[references/global-contract.md](references/global-contract.md),
[references/service-access.md](references/service-access.md) before business
classification.

If the message is an explicitly authorized Mining Market Research installation or
update, a persistent release-check permission request, a decline of the
offered update, or an acknowledgement after a completed update, use the
applicable operational route in `plugin-update.md`. Do not call MCP for these
routes; an authorized update receives fresh refs through the fixed Git
network segment. “Check and install the Mining Market Research update” is
`plugin_update`, not `diagnostics`, and must not call MCP. Keep these routes
separate from business classification. A bare
“yes”, “是”, “install”, or “安装” is not explicit update authorization.
Execute the selected operational route and stop.

## Check a business request once

Execute the shared `update_state.py check` on EVERY substantive request, even
after a cached result on the previous turn. Only the helper decides whether six
hours have elapsed. At successful finalization execute `notice`, copy its
`footer_text` exactly at the end, and never ack before sending. Use the shared
native delayed-confirmation protocol only with matching Hook evidence. All no-Hook hosts use permitted local
maintenance and attempt-only notices: no review/ack or conversation input; skip
unapproved maintenance without blocking business work. Never infer that the previous result is
still fresh. Reuse one actual check only across components of this request.

A successful Hook check from this request also satisfies this gate. Reuse its
context_file; if no Hook receipt exists, execute the Skill fallback. Follow the
shared update policy for host-session joining; never initialize a parallel cache.

For a substantive business request, call `get_connection_status` once and
retain service-access state. Follow
[references/update-notifications.md](references/update-notifications.md) once,
including on later requests in this same session. Reuse both checks for modifiers.

## Classify once

Read [references/query-interpretation.md](references/query-interpretation.md)
before selecting any workflow. Assign exactly one `primary_task`, then extract
modifiers and user- or context-supplied entities. Select presentation policies
before execution, but apply result-dependent windows only after the owning
workflow has materialized discovered entities. Do not let a downstream Skill
reclassify the request.

Use this workflow map:

| `primary_task` | Owning workflow |
|---|---|
| `diagnostics` | This Skill; follow `references/diagnostics.md` only |
| `plugin_update` | Dedicated `upgrade` Skill; follow [workflows/upgrade.md](workflows/upgrade.md) |
| `plugin_update_permission` | This Skill; follow the permission setup in `references/plugin-update.md` only |
| `company_brief` | [workflows/company-brief.md](workflows/company-brief.md) |
| `full_report` | [workflows/company-report.md](workflows/company-report.md) |
| `comparison` | [workflows/company-comparison.md](workflows/company-comparison.md) |
| `market_data` | [workflows/market-analysis.md](workflows/market-analysis.md) |
| supported structured `discovery` | [workflows/market-analysis.md](workflows/market-analysis.md) |
| `news` | [workflows/news-analysis.md](workflows/news-analysis.md) |
| official-record retrieval | Host web or a purpose-built source connector, not a generated report |
| `ambiguous` | Ask one focused question, then classify once from the answer |

This Skill coordinates; it does not duplicate the specialized delivery
workflows. Read exactly one linked workflow after classification. On either supported host, a
clearly matching specialized Skill may start directly through its thin entry,
but it must load the same canonical workflow, read the same arbitration
reference, and verify that it owns the resulting task.

For mixed deep research plus market data, retain `primary_task=full_report`.
The `company-report` Skill presents the selected report first, then applies the
market-data modifier without merging the two evidence sets.

For a market screen, ranking, or evidence filter with attached standalone
company introductions, retain `primary_task=market_data` and set
`company_introductions=true`. The market workflow materializes the ranked
company set before applying the shared introduction component.

For news- or market-led event/price explanations, use analysis_mode=fusion as
specified by query-interpretation.md. The selected owner must load the shared
workflows/event-market-analysis.md; do not require both specialized Skills to
trigger. Browsing headlines and CSV-only requests do not activate fusion.

## Prepare shared state

Company Report defaults to `get_company_report(mode=auto)`: faithfully present
or translate `report_available` with its original date; execute live research
on `generation_ready`; stop on `not_eligible`. Explicit new research uses
`refresh`. MCP alone selects valid reports. Never save/upload generated reports
or translations. Detailed rules live in the owning workflow, not this router.

Maintain the conceptual state defined in
[references/global-contract.md](references/global-contract.md), including
separate requested, contextual, and discovered entities.

Reuse the service check already made for this request. Do not repeat it
when a modifier adds another workflow.

Before a company brief, full report, comparison, or single-company market-data
workflow, read
[references/company-resolution.md](references/company-resolution.md).
Resolve each in-scope company separately. Ask only when exchange, issuer, or
share-class ambiguity remains after context, candidates, and light
primary-source verification.

Pass only the extracted company query fields to MCP. Never send the full
conversation, unrelated personal information, credentials, or copied web-page
text.

## Apply conditional components

When `company_introductions=true`, read
[references/company-introductions.md](references/company-introductions.md)
after the owning workflow has produced the applicable company set. Apply its
window only to standalone introduction blocks, never to the owning table,
ranking, comparison matrix, or report.

Read [references/common-errors.md](references/common-errors.md) for shared
failure handling. Assign `response_status`, then read
[references/response-finalization.md](references/response-finalization.md)
exactly once after the body and disclaimer are ready.

Always identify the product, plugin, and bundled MCP service as **Mining Market
Research** in user-facing text. Keep technical URLs unchanged when needed as
links, but do not repeat stale product labels surfaced by backend or historical
metadata.
