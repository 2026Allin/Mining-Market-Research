# Mining Market Research

<img src="plugins/mining-market-research/assets/logo.png" alt="Mining Market Research logo" width="160">

Mining news, company research and market-data analysis.
One shared plugin connects Codex and Claude to the remote MCP service
at `https://mcp.miningmarketresearch.com/mcp`.

Development preview: `0.7.0-dev.1`. This is a development prerelease, not a
certified stable release.

- [Codex release](https://github.com/2026Allin/Mining-Market-Research/releases/tag/mining-market-research/codex/v0.7.0-dev.1)
- [Claude unified ZIP](https://github.com/2026Allin/Mining-Market-Research/releases/download/mining-market-research/claude/v0.7.0-dev.1/mining-market-research-0.7.0-dev.1-claude.zip)
- [Latest release notes](docs/release-0.7.0-dev.1.md)
- [Release history](https://github.com/2026Allin/Mining-Market-Research/releases)

## What changed in 0.7.0-dev.1

- Move the MCP connection to `https://mcp.miningmarketresearch.com/mcp`.
- Move release discovery and repository declarations to
  `2026Allin/Mining-Market-Research`.
- Require explicit migration of installations registered under the old Git
  source; redirects do not bypass the updater's exact-source validation.
- Synchronize the 18-tool contract with the live `plugin_runtime` diagnostics,
  preserving strict schemas and client-owned update checks.
- Keep one Claude package and the existing capability-aware Hook/Skill fallback.
  See the release notes for migration and verification requirements.

## Capabilities

Seven shared Skills: coordinator, Company Brief, Company Report, Company
Comparison, Market Analysis, News Analysis and Upgrade. Thin host adapters share
the same business workflows and policies.

- News analysis searches the corpus first and can combine announcements, daily
  prices, unusual volume, technical measures and live macro/metal research.
  Daily prices cannot establish an intraday causal sequence.
- Company reports default to `get_company_report(mode="auto")`: faithfully
  present an available report or execute live research when MCP prepares it.
  New research and translations stay in the conversation, without upload.
- Stock queries preserve the user's scope, use cursor pagination and treat
  unknown row totals as unknown. CSV exports use the query ID and actual server
  limits, without requiring all preview pages to be read first.
- The bundled MCP snapshot has 18 tools. Coverage, dates, access and export
  capabilities come from the service, not assumptions about complete markets.

Public access requires no Mining Market Research account. Host permissions and
service limits still apply. Research is informational, not investment advice.

## Sponsor

Sponsored by **Anchises Capital**.

## Install

For installation instructions, see the
[Quick Start guide](https://miningmarketresearch.com/ai?platform=codex).
