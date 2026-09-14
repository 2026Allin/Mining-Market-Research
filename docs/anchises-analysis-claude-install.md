# Mining Market Research: Claude Code installation

Both native hosts load the same plugin package, seven Skills and remote MCP.
Claude Chat, Claude Desktop and Cowork are not certified by Claude Code tests;
their installation and runtime capabilities require separate validation.

## Package identity

- Plugin: `mining-market-research`
- Marketplace: `anchises-capital`
- Install ID: `mining-market-research@anchises-capital`
- Source: `plugins/mining-market-research`
- MCP: `https://mcp.anchisesdata.com/mcp`
- Product version: `0.6.0-dev.11`
- New update namespace: `mining-market-research/claude/v<semver>`; see the
  [identity migration boundary](plugin-brand-migration.md). This identity change
  is unpublished and does not rename an existing installation.

## Install and migrate

Published GitHub installation (local changes are not published automatically):

```bash
claude plugin marketplace add 2026Allin/anchises-stock-qa@main
claude plugin install mining-market-research@anchises-capital
```

For an existing root-layout installation, refresh the marketplace before the
upgrade so its source resolves to the new self-contained package:

```bash
claude plugin marketplace update anchises-capital
claude plugin update mining-market-research@anchises-capital
```

For local testing of the current uncommitted source:

```bash
claude --plugin-dir ./plugins/mining-market-research
```

Start a fresh session after installation or update. Do not install a copied
coordinator directory: sibling Skills, shared host adapters and MCP configuration
belong to the complete plugin package.

## Verify

Confirm all seven Skills are discovered: mining-market-research, company-brief,
company-report, company-comparison, market-analysis, news-analysis, upgrade. Confirm the
configured MCP URL and 17 required tools, then run the shared acceptance cases
in [native-plugin-architecture.md](native-plugin-architecture.md).
A successful installation is not proof of successful tool execution.

Ordinary research probes the six-hour success cache and checks Git tags only
when due. Without an actionable update, no update-related content is shown.
Explicit status uses the coordinator; checks/upgrades use the dedicated `upgrade`
Skill and bundled
platform-specific release checker. Installation requires explicit authorization;
a failed check never authorizes changing user settings or bypassing access.

## Release checks

```bash
python3 plugins/mining-market-research/scripts/sync_plugin_release.py --platform all --check
```

Both platform manifests must carry the same product version. Keep separate
platform cache identifiers and existing Tag namespaces for compatibility.
Publish neither platform until both pass acceptance against the same commit.
