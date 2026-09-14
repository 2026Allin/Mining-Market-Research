# Claude Chat: session-only update checks

Use only when the active host is known to be Claude Chat, including Chat in the
Claude App. Missing CLIs alone do not identify a host; do not classify every
unknown environment as Chat. Cowork needs its own capability validation.

Resolve logical MCP names against the current connection. Use available host
web tools for evidence; never infer loaded tools from the package snapshot.
Do not assume CLI installation or persistent user-profile storage is available.

## Session-only checks

Use the shared compact `check -> notice -> ack if shown` interface for business
requests. Execute `check` on every request; never skip based on a previous
cached/silent result. Add `--allow-network` only with existing host permission.
The low-level sequence below explains its semantics, not additional calls.

Use the shared `update-notifications.md` protocol with these overrides, for
every business entry, explicit check, and upgrade request:

1. At first plugin use in a NEW conversation execute:
   `python3 scripts/update_state.py init --platform claude --surface claude-chat`.
   Retain the returned `context_file` in conversation state. Init generates a
   valid UUID4 and snapshots bundled metadata automatically; do not invent an
   ID or concatenate version strings. Never search for another session's file.
2. Add ALL these options to every subsequent action:
   `--context-file <returned-path>`.
   Reuse exactly that path throughout this conversation, not across conversations.
   Use returned `check_args` / `notice_args` as argument arrays if supported.
   Add `--allow-network` to check only with existing host permission. For example:
   `python3 scripts/update_state.py check --context-file <returned-path> --allow-network`.
   This mode never calls `claude plugin list` or `codex plugin list`. It uses
   a temporary session-specific database, not a persistent installation profile.
3. On first use and first use six hours after last success, probe returns
   `check_required`. Run the same fixed Git lookup and record its stdout with
   the ticket. Failures are silent with a 30-minute retry backoff, not success.
4. At successful business finalization use `notice` and `ack` as in the shared
   policy. Only `update_available` produces text:
   “更新提示：Mining Market Research 有新版 `<target_version>`；当前会话加载的是
   `<loaded version>`。请手动更新插件，然后新建会话。”
   Never report an installed-disk version or emit `reload_required` in this mode.
5. Decline or silence never installs, resets the clock, or permanently suppresses
   a version. New conversations check afresh, even within six hours of another
   conversation. Within this conversation do not repeat a notice in its cycle.

The temporary file is only a within-conversation cache. If the container/file
or conversation token is lost, the next use may recheck; no cross-session or
durable exactly-once guarantee is made. No hooks or background process.

`invalid_arguments` is NOT a successful no-update result. Read its fixed reason;
correct only the parameter wiring using init's actual output, before any network
retry. Invalid session ID, missing/invalid loaded version and context conflicts
are rejected before network access with `network_queries: 0`. Do not present
argument/storage failures as “已是最新版”. Keep automatic-check failures out of
the business answer, but report them honestly when the user asks for diagnostics.

Read the owning workflow's required global-contract, service-access and query
interpretation references completely before business execution. A missing file
does not authorize guessing its rules. Service checks are per request, not per
conversation; do not reuse the previous request's get_connection_status result.

## Explicit checks and manual upgrade

For an explicit check prefer `check --force --allow-network` when permitted;
otherwise use the shared narrow direct-Git protocol, with `probe --force` and
record/failed. Never query twice. Preserve the same session ID and loaded release.
Report the validated latest version against the loaded-session version; no newer
tag means “未发现比当前会话加载版本更新的已发布版本”, not verified installed status.
Use check's latest_version and update_available fields for the latest release when composing this
requested result, even when `notice` is silent. If a notice is included, ack its
ticket to avoid another reminder in that cycle. Failed checks report uncertainty.

For upgrade intent, first do this fresh check. If newer, provide manual guidance:
open Customize > Plugins, select the existing plugin and use any update action
actually shown. For ZIP installs upload a maintainer-supplied newer plugin ZIP
through Add > Upload plugin, then start a new conversation. Do not invent a ZIP
download URL or suggest uploading a whole repository archive as a plugin.
If no newer release exists, do not recommend downgrading or reinstalling.
Never execute `update_installed_plugin.py`, install a CLI, alter permissions,
or claim installation succeeded. Only a new session's metadata can confirm its
loaded version; even that is not native installation inventory.
