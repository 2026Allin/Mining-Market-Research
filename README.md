# Mining Market Research Marketplace

<img src="plugins/mining-market-research/assets/logo.png" alt="Mining Market Research logo" width="96">

This repository contains the Codex `Anchises-Analysis` Marketplace, the Claude
`anchises-capital` Marketplace, and one shared `mining-market-research` plugin
package published by Anchises Capital. Both native hosts expose the same seven
Skills and connect directly to `https://mcp.anchisesdata.com/mcp`.
No generated platform copies or workspace-specific App ID are required.

The source now uses a new plugin installation identity. See the
[identity migration guide](docs/plugin-brand-migration.md) before replacing an
existing installation. This rename is included in the dev.12 prerelease; existing sessions
and published builds keep their original identity.

Development preview: `0.6.0-dev.11`. The submitted public-review
release remains `0.4.0-beta.2`; this preview is not a certified stable release.
See [preview release notes](docs/mining-market-research-0.6.0-dev.11-release-notes.md).

## Development preview changes

- Both marketplaces select `plugins/mining-market-research`, a self-contained
  package with Codex and Claude Code native manifests.
- Seven shared entries: coordinator, Company Brief, Company Report,
  Company Comparison, Market Analysis, News Analysis and Upgrade.
- The live MCP snapshot contains 18 tools. News searches the corpus before web
  supplementation; date discovery uses `get_available_dates`, not physical tables.
- Platform-only differences live inside the core Skill's `references/hosts`. Agent-driven update checks
  run on first use and the first use six hours after the last successful check.
  Trusted native Hooks share the checker with Skill fallback; no update means no reminder. Explicit Upgrade verifies installation
  and requires a new session. Refusal or silence never authorizes installation.
- Automatic checks are best-effort: real Chat sessions sometimes skip them.
  Explicit checking is the supported fallback; Chat updates require manual upload.
- Contract compatibility, package-contained links, shared versions and normalized
  tool-trace invariants are tested. Real dual-host acceptance remains required.
- See [architecture and acceptance](docs/native-plugin-architecture.md) and
  [Claude Code migration](docs/anchises-analysis-claude-install.md).

Older release notes below describe historical behavior, not the current contract.

## What changed in 0.6.0-dev.9

- One maintainer-owned `plugin-policy.json` now controls whether the shared
  market workflow applies legacy restricted-mode behavior. The released value
  is not a user setting, is never sent to MCP, and is shared by Codex and
  Claude.
- With bundled restrictions disabled, the Skills no longer pre-apply old
  browse, Top-N, ticker, field, partition, or SQL-export restrictions. Actual
  MCP schemas, query export eligibility, cursors, errors, and hard limits
  remain authoritative.
- User-facing answers and diagnostics do not expose or offer the bundled
  switch. A plugin update plus a new task or conversation loads a changed
  maintainer value.

## What changed in 0.6.0-dev.8

- Codex release discovery now keeps Python network-free. A cache miss requests
  one direct, read-only `git ls-remote --` against the fixed public repository,
  then pipes the captured refs to the bundled local parser.
- The reusable approval prefix is limited to that repository. It never covers
  `python3`, a shell, plugin installation, or general Git/network access.
- `Approve for me` may approve a current lookup but does not itself persist a
  rule. Users who want cross-task and cross-workspace reuse can temporarily use
  `Ask for approval` and select `Always allow`; the plugin never edits
  `~/.codex/rules/default.rules`.

## What changed in 0.6.0-dev.7

- MCP runtime version is discovered dynamically from the standard handshake
  and is no longer a plugin compatibility or release gate.
- Internal capability profile `1.9.0-draft` keeps the 12 tool schemas,
  security metadata, annotations, instructions, and descriptor hash strict
  while ignoring only the observed MCP version and sync timestamp.
- `get_connection_status({})` is service-only again. Plugin releases continue
  to use the independent Codex Git tag workflow introduced in `0.6.0-dev.6`.

## What changed in 0.6.0-dev.6

- Every selected Mining Market Research Skill performs one read-only Codex release check
  against the then-current platform-specific Git tags. This is independent of MCP
  service versioning; current, unknown, and failed checks stay silent.
- An available update adds one operational footer after the normal business
  answer. Installation requires an explicit Mining Market Research update sentence;
  a bare “yes” or “install” never authorizes commands.
- A Codex tag is valid only when it points to the current remote `main` head.
  The fixed updater supports only the Git Marketplace on `main`, performs one
  preflight/upgrade/install/verification sequence, and never tries an
  alternative or retry.
- `qa-v2-auth` is the development branch; `main` is the release branch. Tags
  are maintainer-created release signals and are never created by ordinary
  commits, branch pushes, installs, or updates. Codex and Claude use separate
  tag namespaces.
- This first tag-aware release still requires one manual install. A future
  update is advertised only after the maintainer explicitly publishes its
  Codex tag.
- The bundled capability snapshot uses internal profile `1.9.0-draft`.
  Runtime MCP version is discovered from `initialize.serverInfo.version` and
  is observational only; compatibility is determined by the 12 required tool
  schemas, security metadata, annotations, and service instructions.

## What changed in 0.6.0-dev.4

- The Codex package now bundles one remote HTTP MCP definition in `.mcp.json`
  instead of referencing a Developer Mode App through `.app.json`.
- Local and cross-workspace Repo Marketplace installations load the same five
  Skills and MCP endpoint from one plugin package.
- A teammate can install from the public GitHub marketplace without creating
  an Mining Market Research App ID or using workspace sharing.
- The former Developer Mode App may remain available as a short-term rollback
  resource, but it is not part of or required by this package.

## What changed for MCP 0.7.1

- `screen_stocks` and `run_readonly_sql` now use opaque cursor continuation;
  every call displays at most 200 rows and only an explicit user request
  advances to the next page.
- `top_n` bounds the complete logical ranked result independently of the
  current `page_size` display page.
- The service publishes query-specific export eligibility, allowed source
  tools, and limits dynamically, so an eligible screen or SQL query ID may be
  exported.
- Policy changes invalidate old cursors and query IDs; the Skill reruns the
  original intent instead of editing capabilities or using SQL `OFFSET`.
- Company reports keep the live Host-research workflow: resolve identity,
  prepare one sector prompt, research current sources, and answer only in the
  current conversation without MCP-side caching or upload.

## What changed in 0.6 development

- The plugin now exposes five peer Skills: a thin coordination entry plus
  dedicated Company Brief, Company Report, Company Comparison, and Market
  Analysis workflows.
- One canonical intent contract selects a single primary task before any
  specialist executes, so a downstream Skill cannot reinterpret the request.
- Only `company-report` may prepare the fixed seven-section live report;
  comparison and market analysis use their own bounded workflows.
- Every standalone multi-company introduction section is capped at five
  companies per response, regardless of the owning primary workflow. Market
  tables, rankings, and comparison matrices keep their own display limits.
- Successful substantive analysis uses one shared response-finalization
  contract for continuation and semantic questions.
- Each Skill uses the bundled Mining Market Research MCP while preserving the same
  public-service access, privacy, and response contracts.

## What changed in 0.4

- The Hosted MCP contract is `0.6.0`, the Data API contract is `0.3.0`,
  and stock exports use policy `stock-data-export-v1`.
- Full matched ranges can participate in server-side filtering, statistics,
  ranking, and aggregation while the Host displays a bounded sorted preview.
- Stock-row previews have no next-page cursor and must not be reconstructed
  through split queries, changing sorts, or local stitching.
- CSV eligibility comes from the current `screen_stocks` export policy. Fields
  are selected dynamically from the research question and live schema; SQL
  query IDs and complete exchange-day partitions cannot be exported.
- When a complete row-level file is outside the export workflow, the Skill
  preserves in-session analysis and can suggest a verified bulk-data API or
  licensed exchange-data vendor suited to the requested market and fields.
- Company identity resolution and live Host-side company research remain
  unchanged from the 0.3 release.

## Repository layout

```text
.agents/plugins/marketplace.json
.claude-plugin/marketplace.json
plugins/mining-market-research/
  .codex-plugin/plugin.json
  .claude-plugin/plugin.json
  .mcp.json
  assets/
  contracts/
  skills/
    mining-market-research/
      workflows/
      references/
      scripts/
    company-brief/
    company-report/
    company-comparison/
    market-analysis/
    news-analysis/
  shared/hosts/
tests/
docs/
```

The MCP URL, website, privacy, terms, and support endpoints remain unchanged.
This repository does not contain or modify the Hosted MCP service, AnchisesWeb,
or the Data API.

## Validate

```bash
.venv/bin/python -m unittest discover -s tests -v

.venv/bin/python \
  plugins/mining-market-research/skills/mining-market-research/scripts/validate_plugin_policy.py

.venv/bin/python \
  ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  plugins/mining-market-research/skills/mining-market-research

.venv/bin/python \
  ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  plugins/mining-market-research/skills/company-brief

.venv/bin/python \
  ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  plugins/mining-market-research/skills/company-report

.venv/bin/python \
  ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  plugins/mining-market-research/skills/company-comparison

.venv/bin/python \
  ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  plugins/mining-market-research/skills/market-analysis

.venv/bin/python \
  ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py \
  plugins/mining-market-research

claude plugin validate . --strict
```

The Claude validation command requires a locally installed Claude Code CLI.
The unit suite validates the checked-in Marketplace, root plugin manifest, one
visible self-contained Skill, closed internal paths, and routed workflows when that CLI is not
available.

Run credential-free production checks explicitly:

```bash
RUN_LIVE_MCP_TESTS=1 \
  .venv/bin/python -m unittest tests.test_live_hosted_contract -v
```

## Local Codex development install

The repo marketplace name is read from `.agents/plugins/marketplace.json`:

```bash
.venv/bin/python \
  ~/.codex/skills/.system/plugin-creator/scripts/read_marketplace_name.py \
  --marketplace-path .agents/plugins/marketplace.json

codex plugin add mining-market-research@Anchises-Analysis
```

After changing plugin content, run the cachebuster helper before reinstalling
and start a new Codex task so the new Skill and MCP schema are loaded.

```bash
.venv/bin/python \
  ~/.codex/skills/.system/plugin-creator/scripts/update_plugin_cachebuster.py \
  plugins/mining-market-research

.venv/bin/python \
  plugins/mining-market-research/scripts/sync_plugin_release.py --platform all

.venv/bin/python \
  plugins/mining-market-research/scripts/sync_plugin_release.py --platform all --check
```

The cachebuster preserves the Codex `0.6.0-dev.9` base and creates one new
`+codex.<timestamp>` suffix. Claude uses its independent root manifest version,
currently `0.6.0-dev.10+claude.<timestamp>`. The synchronizer copies both fixed
identities into the metadata used by their Tag checkers. None of these commands
creates a Git Tag.

The automated in-Skill updater intentionally rejects this local development
Marketplace. Maintainers continue to use the manual cachebuster and reinstall
flow above.

For a local Claude development session without installing the Marketplace:

```bash
claude --plugin-dir .
```

Use the GitHub Marketplace path below for release installation and update
testing; the guarded updater rejects local plugin sources.

## Cross-workspace Codex install

For another OpenAI workspace, add the released public Git marketplace from
`main` and only the two required sparse paths:

```bash
codex plugin marketplace add \
  https://github.com/2026Allin/anchises-stock-qa.git \
  --ref main \
  --sparse .agents/plugins \
  --sparse plugins/mining-market-research

codex plugin add mining-market-research@Anchises-Analysis
```

The equivalent desktop form uses the repository URL as **Source**,
`main` as **Git ref**, and these two **Sparse paths**:

```text
.agents/plugins
plugins/mining-market-research
```

This install does not use `Share with you`, Portal Scan, or a Developer Mode
App ID. A managed workspace may still require its administrator to allowlist
the Git marketplace source and the bundled MCP URL. Start a new Codex task
after installation.

A Git Marketplace installation checks only Codex tags during Mining Market
Research requests. Cache misses use one fixed-repository, read-only Git command with a
narrow reusable approval prefix; Python only validates the captured refs.
It installs only after the user explicitly authorizes the named Mining Market
Research update. Local Marketplaces remain manual. MCP upgrades do not create
plugin update notices unless a newer Codex plugin tag is also published.

See the complete
[cross-workspace installation guide](docs/anchises-analysis-codex-cross-workspace-install.md).

## Claude install from GitHub

Claude Code can add the Marketplace directly from this GitHub repository:

```bash
claude plugin marketplace add \
  2026Allin/anchises-stock-qa@main \
  --sparse .claude-plugin plugins/mining-market-research

claude plugin install mining-market-research@anchises-capital
```

In Claude Chat, Desktop, or Cowork, open **Customize → Plugins**, choose
**Personal plugins → + → Add marketplace → Add from a repository**, and enter
`https://github.com/2026Allin/anchises-stock-qa`. The same plugin package loads
exactly one visible self-contained `Mining Market Research` Skill, its unchanged
business workflows, and the shared Hosted MCP. Start a new Claude conversation
after installation or update.

Claude release checks consider only `mining-market-research/claude/v*`. Claude Code
can run the guarded fixed CLI update after exact authorization; Chat, Desktop,
and Cowork instead hand off to
`Customize → Plugins → Mining Market Research → Update` and never claim the UI
operation completed.

See the complete
[Claude installation and update guide](docs/anchises-analysis-claude-install.md).

See [release notes](docs/anchises-analysis-0.4.0-beta.2-release-notes.md),
[Directory listing](docs/anchises-analysis-plugin-directory-listing.md), and
[reviewer cases](docs/anchises-analysis-reviewer-test-cases.md).
