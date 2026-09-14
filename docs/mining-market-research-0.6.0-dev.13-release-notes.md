# Mining Market Research 0.6.0-dev.13 — development preview

This prerelease updates the plugin's visual identity. No research workflow,
MCP tool contract, update-check policy, or installation permission changes.

- Replace the plugin logo, dark-mode logo and composer icon with the supplied
  gold mountain and rising-arrow artwork. The original image is preserved.
- Codex and Claude packages share the updated assets.
- Release builds: `0.6.0-dev.13+codex.20260914033532` and
  `0.6.0-dev.13+claude.20260914033532`.

## Installation

- Codex: update/install `mining-market-research@Anchises-Analysis` from the
  configured marketplace, then start a new task.
- Claude Code: update/install `mining-market-research@anchises-capital`, then
  start a new session.
- Claude Chat: upload the attached `mining-market-research-0.6.0-dev.13-claude.zip`
  through Customize > Plugins > Add > Upload plugin, then start a new conversation.
  Do not upload GitHub's whole-repository source archive.

Hosts control icon rendering and caching; reopening the plugin page or restarting
the host may be necessary. No guarantee is made that every Claude surface exposes
the package artwork in its UI. Existing release assets and tags remain unchanged.

## Known limitations

This remains a development preview. Claude live-host acceptance and Cowork
certification remain incomplete. Agent-driven update checks are best effort,
not guaranteed background software updates. Old plugin installation identities
may require manual migration; consult the repository migration guide.
