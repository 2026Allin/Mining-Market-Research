# Upgrade and verify Mining Market Research

On Claude Chat, read [the Chat adapter](../references/hosts/claude-chat.md)
and follow its explicit-check/manual-upgrade section, then stop. Do not execute
the native installation steps below or require a CLI installation inventory.

Read [the shared update policy](../references/plugin-update.md), then only the
active host's linked adapter. This workflow owns plugin update checks and
explicit upgrade requests on Codex and Claude Code; it does not call MCP.

## Check versus install

- An explicit request to upgrade this plugin authorizes one native upgrade
  attempt. Do not ask the user to repeat clear authorization. Host execution
  approvals still apply.
- A check-only request performs a fresh fixed-repository lookup through the
  adapter's checker, reports the result, and stops without running the updater.
  Use the shared session context with check --force, comparing the session-loaded
  version. Native installed inventory is required for installation, not checking.
- A refusal, “稍后”, or an unrelated next question authorizes nothing. Do not
  reset the six-hour clock, retry, or ask again. There is no permanent suppression,
  skip-version or seven-day snooze option. The next due plugin use may remind again.
- Generic assent such as “好” or “继续” is not explicit upgrade authorization.

## Execute an authorized upgrade

First establish the actual supported installation path. Claude is distributed as
one package across Chat and Code; the current session may still load an old build.
App Code is not inherently prohibited from native installation, but requires a
working supported CLI and matching enabled plugin inventory/source, just like CLI
sessions. Do not install a CLI to make an upgrade possible. A desktop label, missing
CLI or absent Hooks does not establish the other capabilities.
If no supported native installation path is available, stop before the updater:
offer the host's actually visible plugin-management action or a maintainer-provided
ZIP, then require a new session to verify loaded version/build. Do not promise an
Update button exists. This is manual guidance, not a successful disk installation.

For either check-only or upgrade, also read
[update-notifications.md](../references/update-notifications.md). Acquire
Initialize/reuse this conversation's context as documented there. For an
authorized install acquire `update_state.py probe --force --context-file <returned-path>` and feed the SAME captured
refs to its `record` action (or `failed` on lookup failure). Never fetch twice.
This resets the six-hour clock only after a successful fresh check. If another
check holds the lease, proceed with the explicitly requested check but do not
overwrite its state. Do not append an automatic reminder to this operational
answer. Do not reserve or ack merely because a version appears in an operational
response. If explicitly presenting an update reminder, use the shared exact footer
and native delayed-confirmation protocol; never ack a draft before sending.
All no-Hook sessions use attempt-only notices without review/ack or conversation input.

1. Capture one fresh `git ls-remote` result from the fixed repository using the
   active adapter; do not use a cached reminder as an installation target.
2. Pass the refs to the bundled `update_installed_plugin.py`. It reads native
   installation/source state, validates the release, refreshes the marketplace,
   installs with the native CLI, and verifies the final enabled version.
3. Never bypass an unsupported source or inconsistent release; no uninstall,
   source switching, arbitrary remote commands, permission edits, or fallback.
4. Report the actual fixed failure step without claiming the existing install
   stayed unchanged: a failed operation may have partially changed disk state.
5. On success, state the verified installed version and explicitly require the
   user to restart the session / start a new conversation. Disk installation is
   not proof that the running session has loaded new Skills or MCP tools.

Suggested success receipt:

> Mining Market Research 已升级到 `<version>`，安装检查通过。请重启会话或新建对话，再使用新版及新增 Skills；当前会话尚未验证已加载新版。

If already installed at the target, do not reinstall. Compare the actual
installed release with the session's recorded loaded release; if they differ,
require restarting the session. Do not claim a live MCP or research check was
performed by the installer. New-session functional acceptance is separate.
