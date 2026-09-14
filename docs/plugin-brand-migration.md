# Mining Market Research identity migration

This migration is included in dev.12; it does not replace any historical Tag.

## Three naming layers

- Product and plugin display name: **Mining Market Research**.
- Plugin ID and directory: `mining-market-research`.
- Functional Skill slugs remain `mining-market-research`, `company-brief`,
  `company-report`, `company-comparison`, `market-analysis`, `news-analysis`,
  and `upgrade`. Specialist display names use `Mining Market Research — <function>`.

The host controls whether it renders `plugin:skill`. The new installation
therefore uses `mining-market-research:company-brief`, for example; this package
cannot guarantee removal of all namespace prefixes. Users can ask naturally
without naming a Skill.

## Installation boundary

Changing the plugin ID creates a different installation identity. The native
updater intentionally does not treat a differently named installation as this
plugin, silently uninstall it, or migrate its state. Install the new package,
verify its identity and MCP connection, then explicitly disable/remove the
previous installation in the host UI to avoid duplicate Skills. Start a new
session after installation. Existing sessions retain their loaded names.

Claude Chat uses the new upload package and manual installation; it cannot
verify or modify the desktop installation from its sandbox. Update checks in
Chat remain session-only and agent-driven checks remain best-effort.

Repository URLs, publisher identity, and registered marketplace identifiers
remain unchanged for source validation. They are technical provenance, not
product display labels. The new release namespaces are
`mining-market-research/codex/v*` and `mining-market-research/claude/v*`.
Historical Tags and release notes remain unchanged. A release in these new
namespaces must be published before they can provide a new-version reminder;
do not interpret old-namespace Tags as releases of the new identity.
