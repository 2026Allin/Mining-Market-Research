# Codex plugin update adapter

Use this adapter only in Codex. The shared trigger, reminder, authorization,
decline, failure, and final-order rules are defined in
[plugin-update.md](plugin-update.md).

## Check the Codex release

Follow [update-notifications.md](update-notifications.md) for session initialization
and checking. Use `init --platform codex` at first use, then
`check --context-file <returned-path>`; explicit update checks add `--force`.
No legacy `--cache-only` flow or cross-session cache is used.
Compare this session's loaded version. Native installation inventory is only
required when executing an authorized upgrade.
Use the shared direct-Git probe/record alternative if the host permits only the
Git segment. Capture exactly once, feed that same stdout to record and, for an
authorized install, the guarded updater. Never fetch twice.
Only the fixed repository https://github.com/2026Allin/anchises-stock-qa.git
and `mining-market-research/codex/v*` namespace are allowed.
A reusable approval must cover only the exact direct Git prefix:
`git ls-remote -- https://github.com/2026Allin/anchises-stock-qa.git`.
Never request one for Python, a script, a shell, or general network access.
Do not edit permissions or elevate automatic business checks.
For a user-requested check, ask only for the narrow Git operation if required;
denial remains unknown and must not be retried.

For an explicit check requiring approval, request the direct Git command only:

```json
{
  "cmd": "git ls-remote -- https://github.com/2026Allin/anchises-stock-qa.git",
  "sandbox_permissions": "require_escalated",
  "justification": "允许只读检查 Mining Market Research 的已发布版本吗？",
  "prefix_rule": [
    "git",
    "ls-remote",
    "--",
    "https://github.com/2026Allin/anchises-stock-qa.git"
  ]
}
```

Record its captured stdout using the same context_file and probe ticket.
This permission does not cover running an installer.

## Set up reusable Codex release-check permission

Treat “为 Mining Market Research 启用永久版本检查” or an equally explicit request
as `plugin_update_permission`. Do not call MCP or install anything. Bypass the
cache and issue the same fixed Git-plus-parser request so Codex can propose only
its exact Git prefix.

Explain that **Approve for me** is Auto-review: it may approve the current
lookup but does not itself create a persistent allow rule. For reusable
permission, the user must temporarily use **Ask for approval** and choose
**Always allow** for the exact Git prefix. The Codex UI owns that decision and
may write `~/.codex/rules/default.rules`; this plugin must never create, edit,
or delete that file. The user may then return to Approve for me.

Do not claim persistence unless the user explicitly confirms **Always allow**.
If denied, say that reusable checking was not enabled and leave the plugin
functional; do not try another command or weaken the prefix.

## Update through the Codex CLI

After explicit authorization, pipe one fresh lookup to the updater exactly
once:

```text
git ls-remote -- https://github.com/2026Allin/anchises-stock-qa.git | python3 <absolute-skill-directory>/scripts/update_installed_plugin.py --remote-refs-stdin
```

Prefer captured refs from the shared upgrade workflow; do not repeat the lookup
if already captured in this request. Installer execution has separate host
permissions and must not reuse a Git-only grant. The updater accepts no target version, Tag, repository, branch, or
command argument and never opens the network. It executes each command at most
once, in this order:

```text
codex plugin list --json
codex plugin marketplace list --json
codex plugin marketplace upgrade <validated-metadata.marketplace> --json
codex plugin add <validated-metadata.plugin_id> --json
codex plugin list --json
```

The placeholders above are populated only by the bundled updater from validated
release metadata; do not run them literally or substitute a guessed identity.
The supported source is exactly the registered marketplace in that metadata, repository
`https://github.com/2026Allin/anchises-stock-qa.git`, and Git ref `main`. If
Codex omits or returns `null` for `marketplaceSource.refName`, accept it only
when the captured remote `HEAD`, `refs/heads/main`, and selected release Tag
resolve to the same commit. A local Marketplace, wrong repository, explicit
non-`main` ref, incomplete source metadata, or commit mismatch stops the
update. The compatibility check must not execute an additional command.

Never attempt `git pull`, `git clone`, Tag creation, commit, push, merge,
uninstall-first, Marketplace removal or re-addition, `config.toml` or
Marketplace JSON edits, force, rollback, or GUI fallback. Creating or
publishing a Codex Tag is a separate maintainer-only release action.

On `updated`, say:

> Mining Market Research 已更新到 `<version>`。当前对话仍使用启动时加载的旧 Skill 和 MCP catalog，请新建一个 Codex 对话后再使用新版本。
