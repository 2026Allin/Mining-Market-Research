# Mining Market Research

One self-contained MCP + Skills plugin for Codex and Claude Code. Both native
manifests load the same seven Skill entries and `.mcp.json`; no generated copies
or conversion layer. The public endpoint is `https://mcp.anchisesdata.com/mcp`.

## Release identity and architecture

- Product version: `0.6.0-dev.11`; platform cache identifiers remain separate.
- Display name: Mining Market Research. Technical slug: `anchises-analysis`.
- Codex marketplace: `Anchises-Analysis`; Claude marketplace: `anchises-capital`.
- Entries: mining-market-research, company-brief, company-report, company-comparison,
  market-analysis, news-analysis, upgrade.
- Canonical workflows and policies: `skills/mining-market-research/workflows` and
  `references`; host-only instructions: `skills/mining-market-research/references/hosts`.
- Raw MCP snapshot: `contracts/hosted-mcp-v1.json`; tool ownership and example
  arguments: `contracts/capabilities.yaml`.
- Market and date coverage are discovered dynamically. The current snapshot
  contains 17 tools; extra tools require review, not an automatic count failure.
- Both hosts use the same task classification, evidence and safety requirements.
  Tool namespace prefixes, authorization UI and file presentation may differ.

The package does not depend on a Developer Mode App ID. Local and cross-workspace
Repo Marketplace installations use the same workflow core. A public directory
submission must submit and scan the production MCP URL directly.

Ordinary research obtains service state once and probes the six-hour update
cache. Only due checks fetch Git tags; only actionable updates produce reminders.
Explicit diagnostics and update requests retain their guarded
platform-specific release check. No installer changes host permission settings.
Claude Chat/Cowork require separate validation; Claude Code support is not proof
of their compatibility.

## News

News analysis searches the corpus first, respects NEWS_ACCESS and selects at
most five articles per user request. Web research preparation returns a prompt,
not web results. Only actual host browsing can support claims of live research.
News retrieval can also supply evidence to reports, briefs and comparisons
without changing their primary task.

## Company briefs

The `company-brief` Skill handles explicit or semantically equivalent requests
for quick context on named companies or a clearly referenced company set. It
classifies the request once, preserves user order, resolves each selected
identity, and uses Host web research without calling the seven-section report
preparation tool.

Each company receives three or four source-linked sentences covering its core
business, a dated official development, and a dated independent news item.
Any standalone company-introduction section covers at most five companies,
including an introduction section attached to Market Analysis or Company
Comparison. Market tables, rankings, and comparison matrices are not capped by
this rule. When introductions remain, the response asks how to continue and
offers one relevant follow-up concerning only the completed batch.

Successful substantive Brief, Report, Comparison, news, and Market Analysis
answers use one response-finalization matrix. The disclaimer appears before
required questions; a successful completed answer ends with one semantic
question, while a successful partial introduction batch ends with one
continuation question followed by one semantic question. Explicit requests for
no suggestions and failed or mechanical workflows use the documented
exceptions.

## Company identity and live research

For a company name, ticker, exchange-ticker pair, or clear chat reference, the
Skill calls `resolve_company_identity` with only the extracted query fields.
It uses current chat context and light primary-source web verification to
resolve exchange, ticker, and company name without sending the full transcript.

An explicit company-research request calls
`prepare_company_report_generation` directly with all four required fields:

```json
{
  "exchange": "NASDAQ",
  "ticker": "AAPL",
  "company_name": "Apple Inc.",
  "output_locale": "zh-CN"
}
```

For a ready result, the Host executes the returned prompt with live web search
and writes the final report in the current conversation. The MCP does not
perform the search or persist the result. External, inactive, and delisted
companies may use the `Others` prompt after primary-source identity and listing
verification. ETF and Fund records are not eligible for an operating-company
report.

## Structured stock data

Use `get_available_exchanges` for current coverage and `get_available_dates`
for actual trading dates. `list_stock_tables` discovers physical SQL tables,
not dates. The 17 current Hosted MCP tools are:

- `get_connection_status`
- `get_available_exchanges`
- `get_latest_dates`
- `get_stock_schema`
- `get_available_dates`
- `list_stock_tables`
- `get_table_schema`
- `screen_stocks`
- `validate_readonly_sql`
- `run_readonly_sql`
- `resolve_company_identity`
- `prepare_company_report_generation`
- `list_news_filters`
- `search_news`
- `get_news_article`
- `prepare_news_web_research`
- `create_csv_export`

CSV exports default to 3600 seconds (60 minutes) and may be explicitly set from
60 through 3600 seconds. Full matched ranges may be analyzed server-side, and
each stock-row call displays no more than 200 rows. When the service returns
`call_same_tool_with_cursor`, the Host can fetch the next display page only
after the user explicitly asks. A continuation sends only the opaque cursor
and `page_size` or `max_rows`; it never resends the query or uses SQL `OFFSET`.

`top_n` bounds the complete logical ranked result rather than the current
display page. `get_connection_status.data_policy` and each result's
One shared `references/plugin-policy.json` file controls whether the Host
workflow applies legacy restricted-mode behavior. It is maintainer-owned,
bundled into both Codex and Claude releases, not user configurable, and never
sent to MCP. The current query's `data.export_policy` still defines dynamic
limits, permitted source tools, and the authoritative `eligible_by_query`
gate. A currently eligible `screen_stocks` or `run_readonly_sql` query ID may
be exported, while an actual service refusal is never bypassed through split
queries.

## Cross-workspace Codex installation

The public repository can be installed from a different OpenAI workspace
without creating an Mining Market Research App ID:

```bash
codex plugin marketplace add \
  https://github.com/2026Allin/anchises-stock-qa.git \
  --ref main \
  --sparse .agents/plugins \
  --sparse plugins/anchises-analysis

codex plugin add anchises-analysis@Anchises-Analysis
```

The plugin install supplies both the seven Skills and the remote MCP definition;
a separate `codex mcp add` is not required. Managed workspaces may require an
administrator to allowlist the Git source and exact MCP URL. Start a new Codex
task after installing or updating the plugin.

`0.6.0-dev.6` is the bootstrap release and must be installed manually once.
Later Codex releases are detected from their explicit Git tags. MCP-only
updates remain independent and do not trigger a plugin installation notice.

## Claude installation from GitHub

Claude Code installs the same package from the root Claude Marketplace:

```bash
claude plugin marketplace add \
  2026Allin/anchises-stock-qa@main \
  --sparse .claude-plugin plugins/anchises-analysis

claude plugin install anchises-analysis@anchises-capital
```

Claude Code loads the same seven Skills. Other Claude surfaces require separate
validation. See [the Claude guide](../../docs/anchises-analysis-claude-install.md)
and [architecture](../../docs/native-plugin-architecture.md).

## Upgrade and update reminders

Every business entry requires an actual per-request `update_state.py check`;
previous-turn cache results must not be used to skip it. `check --allow-network`
combines probe, one fixed 15-second Git lookup when due, and result recording.
The host must already allow this execution; the flag is not a permission grant.
Finalization uses `notice`, then `ack` only for a notice included in the answer.
No background execution or guaranteed agent compliance is claimed.

### Build and verify a Claude test package

Run from the repository root:

```sh
python3 plugins/anchises-analysis/scripts/run_update_scenarios.py
python3 plugins/anchises-analysis/scripts/build_test_package.py --output-root /tmp/mining-market-research-builds
```

Reuse that output root. Each build reserves a unique build-ID directory, stages
matching Claude manifest/metadata in the ZIP, verifies seven Skill names, Chat
parameters, package-relative links and ZIP bytes, and writes a SHA-256 receipt.
The source manifests and previously installed plugins are not modified.
No GitHub publication occurs. Only the ZIP is uploaded; keep its neighboring
receipt for identifying the exact build. Use the receipt's release_id, not the
source checkout's release_id, when verifying a newly loaded Chat session.
The offline scenario runner never queries a real repository or changes normal
update state. See the [acceptance plan](../../docs/update-reminder-acceptance.md)
for the separate real-host checks that remain required.

Claude Chat uses session-only checking: first use in every new conversation,
then six hours after its last successful check. Newer releases prompt manual
update/upload and a new conversation; no native CLI or installed-version claim.
Its temporary cache does not persist across conversations. The native behavior
below applies to Codex and Claude Code only. All surfaces remain silent when
there is no newer release; decline/ignore never authorizes installation.

Use the dedicated `upgrade` Skill to check or upgrade Mining Market Research.
A check-only request never installs; an explicit upgrade authorizes one guarded
native attempt. Successful installation is verified and requires restarting
the session / opening a new conversation to load updated Skills and MCP tools.

Every substantive plugin use probes shared persistent state. The first use,
and first use six hours after the last successful check, checks published tags.
No update or a failed automatic check produces no update-related answer text.
Refusal or silence means no installation and no timer reset: the next six-hour
cycle can remind about the same version. There is no permanent opt-out or hook.
Failed checks back off for 30 minutes. Existing pre-mechanism sessions need one
restart; agents cannot inject instructions into an already loaded old session.

## Contract synchronization

The checked-in descriptor snapshot is generated from the public service with a
credential-free, read-only JSON-RPC client:

```bash
.venv/bin/python plugins/anchises-analysis/contracts/sync_hosted_contract.py --check
```

The snapshot must contain the 17 current required descriptors, a semantic version
observed from `initialize.serverInfo.version`, the company-identity resolver,
a four-required-field prepare schema, noauth security, Prompt pack `5.1`,
opaque cursor pagination, dynamic data/export policy metadata, and no legacy
cached-report tools.

The synchronizer validates internal capability profile `1.9.0-draft` and a
service-only `get_connection_status({})` schema with no plugin release fields.
Compatibility checking ignores descriptive wording and observed service versions.
New tools and optional arguments produce review notices; required-tool deletion
and existing schema/security changes block automatic acceptance. Git tags are the only plugin update signal.

## Validation

From the repository root:

Before final validation, update the Codex cachebuster, set the Claude manifest
release suffix when publishing Claude, and synchronize both metadata files:

```bash
.venv/bin/python \
  ~/.codex/skills/.system/plugin-creator/scripts/update_plugin_cachebuster.py \
  plugins/anchises-analysis
.venv/bin/python plugins/anchises-analysis/scripts/sync_plugin_release.py --platform all
.venv/bin/python plugins/anchises-analysis/scripts/sync_plugin_release.py --platform all --check
```

Then run:

```bash
.venv/bin/python -m unittest discover -s tests -v

.venv/bin/python \
  plugins/anchises-analysis/skills/mining-market-research/scripts/validate_plugin_policy.py

.venv/bin/python \
  ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  plugins/anchises-analysis/skills/mining-market-research

.venv/bin/python \
  ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  plugins/anchises-analysis/skills/company-brief

.venv/bin/python \
  ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  plugins/anchises-analysis/skills/company-report

.venv/bin/python \
  ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  plugins/anchises-analysis/skills/company-comparison

.venv/bin/python \
  ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  plugins/anchises-analysis/skills/market-analysis

.venv/bin/python \
  ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py \
  plugins/anchises-analysis

claude plugin validate ./plugins/anchises-analysis --strict
```

The Claude validation command requires the Claude Code CLI. The unit suite
still validates both checked-in manifests, the same seven native
Skills, closed route targets, release identities, Tag parsers, fixed updater
sequences, shared workflow bodies, and the current MCP contract.
