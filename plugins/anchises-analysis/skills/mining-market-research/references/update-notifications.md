# Agent-driven update reminders (no hooks)

Apply on every substantive Mining Market Research request, including requests
in an old conversation, even when only a specialist Skill was selected. The
agent invokes the helper; there is no background process or hook. Reuse one
probe per user request across all components. This is best-effort agent behavior,
not a promise of execution while the user is idle.

## At the start of the plugin request

### Preferred compact interface

On EVERY substantive request actually execute `update_state.py check` once,
including immediately consecutive turns. The helper performs probe, at most
one fixed Git lookup, and record/failed. Never substitute a remembered result.
Use the active host arguments below (Chat must also use its surface/session
arguments). Add `--allow-network` ONLY when the host already permits this
helper's fixed Git lookup. This flag cannot grant host permissions, and a rule
allowing a direct Git command does not automatically allow a Python wrapper.
Do not ask for broad Python/network permissions or elevate during automatic
business checks. Without permission, run without the flag: it remains silent
and backs off for 30 minutes. Never install anything from a check.

The compact flow is `check -> notice -> ack (only if shown)`. The `check`
result includes `network_queries` (0 or 1); success is `recorded`, a cache hit
is `cached`, and unavailable access/failure is silent. Do not call standalone
probe/Git/record additionally in the same request. Native explicit install
continues to use fresh captured refs and the guarded installer.

The low-level probe/record protocol below remains for diagnostics and hosts
that permit ONLY a direct Git invocation. Choose one protocol per request,
never both. Its separate network segment retains the narrow direct-Git approval.

Select the actual host first. Claude Chat (including Chat in Claude App) must
read [claude-chat.md](hosts/claude-chat.md) and apply its init/context-file
arguments and manual-update overrides throughout this protocol. The native
inventory and persistent profile behavior below applies ONLY to Codex/Claude Code.
Never infer Codex merely because the environment is not Claude Code.

Record the active host and the loaded plugin release once per session from its
bundled `plugin-release.json` (Codex) or `plugin-release-claude.json` (Claude).
Retain that full version plus build ID; never replace the session snapshot
with newer metadata after an on-disk upgrade. If the loaded release cannot be
established, do not claim that the session is current.

Resolve `scripts/update_state.py` to an absolute path relative to this reference's
parent Skill. Use `--platform claude` on Claude Code, or `--platform codex` on Codex.
The helper uses native read-only plugin inventory, persistent profile-scoped
state and short transactions. Only `check --allow-network` may open the network;
all low-level actions below are network-free. No action installs anything.

Run `python3 <script> probe --platform <host>` once.

- `cached`: no network. A pending unshown notice can still be delivered later.
- `busy` or `silent`: continue business without any update content.
- `check_required`: retain the opaque ticket. Only if network access is already
  permitted, execute one fixed command, with a short host-enforced timeout:
  `git ls-remote -- https://github.com/2026Allin/anchises-stock-qa.git`.
  Feed its captured stdout to `python3 <script> record --platform <host> --ticket <ticket>`.
  Do not put the whole transcript in stdin. On failure, denied access or timeout,
  use `python3 <script> failed --platform <host> --ticket <ticket>` and stay silent.
  Do not prompt repeatedly for permission as part of automatic business checks.

The successful check starts a six-hour cycle. Failure backs off for 30 minutes
without changing the last success time. A first use without a success record
checks immediately. A backwards clock adjustment expires the cache safely. Concurrent sessions
share a short check lease. Expired or superseded tickets cannot overwrite results.
Missing native inventory, denied storage or unsupported surfaces degrade silently;
do not claim cross-session deduplication when persistence is unavailable.

## At the end of the business answer

If the task succeeded and allows a normal prose footer, call:

`python3 <script> notice --platform <host> --loaded-release <session-loaded-release>`

Only append a footer for these actions:

- `update_available`: “更新提示：Mining Market Research 有新版 `<target_version>`。
  需要更新时，请回复‘升级 Mining Market Research’。”
- `reload_required`: “Mining Market Research 已更新，但当前会话仍使用旧版。
  请重启会话或新建对话以加载新版及新增 Skills。”

For `silent`, append nothing. Do not show checks, timestamps, failures, “no
updates”, or version content in ordinary answers without an actionable notice.
Do not invent release highlights: the refs checker does not retrieve changelogs.

Reserve a notice only when the final answer is ready. After composing the actual
footer, acknowledge its ticket with `python3 <script> ack --platform <host> --ticket <ticket>`
as the last helper action before sending. If delivery is interrupted, do not
acknowledge an unseen notice; a reservation expires after two minutes. There is
no transactional delivery callback: a crash between ack and send can suppress
that cycle's reminder, so do not promise exactly-once delivery.

Do not reserve/ack for strict JSON/CSV, clarification, failed tasks, or a refusal
acknowledgement. Preserve pending eligibility for a later suitable answer.

## After a reminder

Only explicit upgrade intent routes to [Upgrade](../workflows/upgrade.md).
“不升级”, “稍后提醒”, or ignoring the reminder means no installation and no
follow-up. Do not reset the clock or write a permanent suppression preference.
Within this six-hour cycle do not remind again. At the first plugin use after
the cycle expires, check again and, if still newer, the same version may be
reminded again. No seven-day snooze and no skip-version state exist.

Explicit check-only requests bypass the automatic TTL via the upgrade workflow;
do not run the automatic probe as a second check. New mechanisms cannot execute
inside a historical session that never loaded them: install and restart once
to establish this behavior for future long-running sessions.
