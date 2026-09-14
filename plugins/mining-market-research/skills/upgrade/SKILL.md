---
name: upgrade
description: Check Mining Market Research updates or perform an explicitly authorized native upgrade; in Claude Chat, guide manual installation instead. Verify native installation where available and require a new session after an upgrade. Use for plugin update checks, upgrade requests, or upgrade failures. Do not treat a reminder, silence, or a refusal as authorization.
---

# Mining Market Research — Upgrade

Read [the shared upgrade workflow](../mining-market-research/workflows/upgrade.md).
On Claude Chat use check-and-manual-update guidance; never run the CLI updater.
On Codex/Claude Code use the native host installer, not an MCP-provided shell command. An explicit
upgrade request authorizes one attempt; a check-only request never installs.
Reuse the current Hook/Skill context_file when present. A Hook or MCP update
notice is not installation consent. Do not bypass Hook trust or broaden host
permissions; require a new session after a verified upgrade.

If the sibling link is absent in a host's flattened Skill mounts, locate the
plugin's `mining-market-research` Skill using the host-provided Skill path and
read its `workflows/upgrade.md` there. Do not guess a sibling directory name.
Resolve all shared references from that actual core directory; read required
files fully. If unavailable, report the limitation instead of inventing rules.
