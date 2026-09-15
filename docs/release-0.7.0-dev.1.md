# Mining Market Research 0.7.0-dev.1 (preview)

## Changes

- Canonical MCP endpoint: https://mcp.miningmarketresearch.com/mcp.
- Canonical release repository: https://github.com/2026Allin/Mining-Market-Research.
- Synchronize manifests, platform metadata, fixed update-check commands,
  repository allowlists, Skill references, contract tooling and tests.
- Refresh the 18-tool output schemas from the new endpoint. The reviewed change
  adds optional, strictly defined `plugin_runtime` diagnostics; business input
  schemas are unchanged. Server takeover remains disabled.
- Retain one Claude ZIP, capability-based host behavior and explicit installation
  authorization. No automatic repository rewrite, uninstall or permission edit.

## Explicit migration

An installation registered under the old Git repository can fail source validation
even if GitHub redirects it. This is expected; do not bypass the guard or treat
the redirect as permission to install.

1. Inspect the host's current marketplace source and installed plugin version.
2. With explicit user authorization, use the host's marketplace controls to
   register/migrate to `https://github.com/2026Allin/Mining-Market-Research.git`
   on `main`. Preserve the existing marketplace identifiers: `Anchises-Analysis`
   for Codex and `anchises-capital` for Claude. Do not rename those identifiers.
3. If the host cannot replace the source in place, explain the affected scope
   and obtain approval before any removal/re-addition. Never silently uninstall.
4. Install this release using the verified new source, or use the unified Claude
   ZIP through the host's available manual installation controls. No CLI needs
   to be installed just to enable updates.
5. Open a new session. Verify version `0.7.0-dev.1`, the platform build ID and the
   actual MCP connection URL. Review changed Hooks where supported. An installed
   version or a connection declaration does not prove that Skills were loaded.

Existing local-directory marketplaces do not need to become Git marketplaces;
maintainers can reinstall from the updated local source. Updating a development
checkout's Git remote is separate from updating an installed plugin.

Older clients may keep the former repository allowlist and session connection.
Use explicit manual migration when their guarded updater cannot proceed.

## Verification

The new domain has passed direct, read-only initialization, four business-tool
calls and strict contract comparison. This is not a native-host installation
certification. Offline tests cover rejection of old/wrong sources without
installation retries. New-session host acceptance remains separate.

This is a development prerelease, not a stable release. The repository and MCP
migration does not authorize service-side changes or server-owned update checks.
