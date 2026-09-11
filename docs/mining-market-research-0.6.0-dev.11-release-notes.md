# Mining Market Research 0.6.0-dev.11 — development preview

This is a maintainer-authorized prerelease, not a stable or dual-host-certified
release. Both platform Tags identify the same source commit.

## Included

- Mining Market Research branding; coordinator renamed to `mining-market-research`.
- One native plugin package, seven shared Skills, and the 17-tool MCP contract.
- News workflow, dynamic historical date discovery, and capability checks.
- Dedicated `upgrade` Skill: explicit check/upgrade intent, guarded native
  installation on Codex/Claude Code, manual updates in Claude Chat, restart required.
- No hooks. Six-hour success-cache logic, silent no-update behavior, no permanent
  opt-out, and no automatic installation. Claude Chat caches within a session only.
- Chat `init` generates a context file and version snapshot; no hand-built IDs.
- Host instructions inside the core Skill for flattened Chat mounts, explicit
  parameter errors, controlled regression scenarios and verified test packaging.

## Known limitations — read before installing

- **Automatic triggering is not reliable.** Actual Claude Chat business requests
  have skipped the checker despite Skill instructions. Do not rely on software-like
  automatic update alerts or guaranteed six-hour checks. Ask explicitly to check.
- User-reported Chat execution verified init, authorized lookup, record and cache
  reuse. Other automated tests do not prove that agents follow every workflow step.
- Chat cannot inspect native installation inventory; comparisons use the current
  session's loaded version. ZIP installs update manually, then require a new session.
- Full Claude Code native upgrade and dual-host behavioral acceptance remain
  incomplete. Cowork is not certified. No public Plugin Directory approval is implied.
- A network permission flag does not grant host permission. Denial remains silent
  for background business checks and must never be treated as a successful check.
- Sessions predating these mechanisms must manually install and reload once.
  dev.11 test builds share the base version with this release: do not expect a
  same-base-version update reminder; compare full build IDs manually.

## Installation

Claude Chat: download the attached `mining-market-research-dev11.zip`, use
Customize > Plugins > Add > Upload plugin, and start a new conversation.
Do not upload GitHub's automatically generated whole-repository source archive.

Claude Code: refresh marketplace `anchises-capital`, update
`anchises-analysis@anchises-capital`, then restart the session. The marketplace
now points at `plugins/anchises-analysis`, not the repository root.

Codex: refresh marketplace `Anchises-Analysis`, install/update
`anchises-analysis@Anchises-Analysis`, then start a new task.

Expected release builds:

- Codex: `0.6.0-dev.11+codex.20260911142026`
- Claude: `0.6.0-dev.11+claude.20260911142026`

Ask to check updates without installing if you only want version information.
No upgrade may run merely because an update reminder was shown or ignored.
