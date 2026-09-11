---
name: upgrade
description: Check or upgrade the installed Mining Market Research plugin, verify the installation, and require restarting the session afterward. Use when the user asks to check plugin updates, explicitly requests an upgrade, or reports an upgrade failure. Do not upgrade unrelated software or treat a reminder, silence, or a refusal as authorization.
---

# Mining Market Research Upgrade

Read [the shared upgrade workflow](../mining-market-research/workflows/upgrade.md).
On Claude Chat use check-and-manual-update guidance; never run the CLI updater.
On Codex/Claude Code use the native host installer, not an MCP-provided shell command. An explicit
upgrade request authorizes one attempt; a check-only request never installs.

If the sibling link is absent in a host's flattened Skill mounts, locate the
plugin's `mining-market-research` Skill using the host-provided Skill path and
read its `workflows/upgrade.md` there. Do not guess a sibling directory name.
Resolve all shared references from that actual core directory; read required
files fully. If unavailable, report the limitation instead of inventing rules.
