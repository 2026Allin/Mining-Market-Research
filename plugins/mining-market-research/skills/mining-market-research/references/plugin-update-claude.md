# Claude plugin update adapter

Use this adapter only in Claude Chat, Claude Desktop, Cowork, or Claude Code.
The shared trigger, reminder, authorization, decline, failure, and final-order
rules are defined in [plugin-update.md](plugin-update.md).

## Check the Claude release

Follow [update-notifications.md](update-notifications.md) for session initialization
and checking. Use `init --platform claude` at first use, then
`check --context-file <returned-path>`; explicit update checks add `--force`.
No legacy `--cache-only` flow or cross-session cache is used.
Compare this session's loaded version. Native installation inventory is only
required when executing an authorized upgrade.
Use the shared direct-Git probe/record alternative if the host permits only the
Git segment. Capture exactly once, feed that same stdout to record and, for an
authorized install, the guarded updater. Never fetch twice.
Only the fixed repository https://github.com/2026Allin/anchises-stock-qa.git
and `mining-market-research/claude/v*` namespace are allowed.
A reusable approval must cover only the exact direct Git prefix:
`git ls-remote -- https://github.com/2026Allin/anchises-stock-qa.git`.
Never request one for Python, a script, a shell, or general network access.
Do not edit permissions or elevate automatic business checks.
For a user-requested check, ask only for the narrow Git operation if required;
denial remains unknown and must not be retried.

## Handle reusable-check requests on Claude

Treat an explicit request to enable reusable release checking as
`plugin_update_permission`. Do not call MCP, install anything, or edit
`.claude/settings.json`, managed settings, or any permission file. Use only a
host-provided permission control for the exact Git segment when such a control
is visible. If the host offers no persistent choice, state that the current
read-only check may be approved but this plugin cannot make it permanent.

## Update in Claude Code

Use this automated path only when the active surface is unambiguously Claude
Code. After explicit authorization, pipe one fresh lookup to the updater:

```text
git ls-remote -- https://github.com/2026Allin/anchises-stock-qa.git | python3 <absolute-skill-directory>/scripts/update_installed_plugin.py --platform claude --remote-refs-stdin
```

The updater accepts no target version, Tag, repository, branch, Marketplace,
plugin ID, scope, or command argument. It executes each step at most once:

```text
claude plugin list --json
claude plugin marketplace list --json
claude plugin marketplace update anchises-capital
claude plugin update mining-market-research@anchises-capital
claude plugin list --json
```

The supported source is Marketplace `anchises-capital` from GitHub repository
`2026Allin/anchises-stock-qa` or the exact Git URL
`https://github.com/2026Allin/anchises-stock-qa.git`. An explicit ref must be
`main`. An omitted ref is accepted only when the captured remote `HEAD`,
`refs/heads/main`, and selected release Tag resolve to the same commit. Local,
URL-file, seed-managed, wrong-repository, explicit non-`main`, disabled,
duplicate, or incomplete installations fail closed.

Never attempt `git pull`, `git clone`, Tag creation, commit, push, merge,
uninstall-first, Marketplace removal or re-addition, settings edits, force,
rollback, or an interactive fallback. Creating or publishing a Claude Tag is a
separate maintainer-only release action.

On `updated`, say:

> Mining Market Research 已更新到 `<version>`。当前对话仍使用启动时加载的旧 Skill 和 MCP catalog，请新建一个 Claude 对话后再使用新版本。

## Hand off in Claude Chat, Desktop, and Cowork

These surfaces must not run the Claude CLI updater. After exact authorization,
perform one fresh Claude Tag recheck. If the validated update is still
available, reply with only the fixed handoff after any necessary one-sentence
context:

> 请在 `Customize → Plugins → Mining Market Research → Update` 完成更新；完成后新建一个 Claude 对话。此处尚未执行或确认安装。

Do not claim `updated`, do not write `installed_release_in_task`, and do not
guess another UI path. If the fresh result is current, say no update is needed;
if it is unknown or inconsistent, use the shared failure rule without exposing
raw errors.
