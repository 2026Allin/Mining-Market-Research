# Claude Chat: session-only update checks

Use only when the active host is known to be Claude Chat, including Chat in the
Claude App. Missing CLIs alone do not identify a host; do not classify every
unknown environment as Chat. Cowork needs its own capability validation.

Resolve logical MCP names against the current connection. Use available host
web tools for evidence; never infer loaded tools from the package snapshot.
Do not assume CLI installation or persistent user-profile storage is available.
See [remote MCP boundaries](remote-mcp.md) when only connector tools are visible.
Skill visibility, local script permission and native Hooks are separate capabilities.

## Session-only checks

Use the compact `check -> notice -> send` interface when local execution is permitted.
Maintenance is not a prerequisite for business queries. If execution is denied or
requires ungranted approval, skip maintenance and continue business work; do not
repeatedly seek approval or claim that skipped checks succeeded.
Execute `check` on every permitted request; never skip based on a previous
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
3. Check internally handles probe, authorized fixed Git lookup and recording.
   Do not run an additional probe/Git/record sequence. Failures are silent with
   a 30-minute retry backoff, not success; silent alone does not mean up to date.
4. At successful business finalization use `notice` as in the shared
   policy. Only `update_available` produces text: copy `footer_text` exactly.
   Never run `review` or `ack`, read transcripts, or pass conversation text to
   maintenance scripts. The CLI rejects these confirmation actions for Chat
   before reading stdin. Notice records `attempted`, not delivered or confirmed.
   At most two attempts per check cycle are allowed, separated by the two-minute
   lock; this bounds possible duplicates but cannot guarantee delivery.
   No Hooks run in web/Desktop Chat.
   Never report an installed-disk version or emit `reload_required` in this mode.
5. Decline or silence never installs, resets the clock, or permanently suppresses
   a version. New conversations check afresh, even within six hours of another
   conversation. Within this conversation the helper enforces the attempt cap.

The temporary file is only a within-conversation cache. If the container/file
or conversation token is lost, the next use may recheck; no cross-session or
durable exactly-once guarantee is made. No hooks or background process.

## Local data and permission boundary

`init` reads bundled release metadata and creates a private temporary session
directory (0700), `session.json` (0600), and session state as needed.
`check`/`notice` use `updates.sqlite3` in that session directory; they do not use
an account-wide six-hour cache or another conversation's state. Notice stores its
own footer, digest, attempt count and release identifiers, not business answers.
No conversation body is required, persisted or uploaded by this Chat flow.
Only an authorized `check --allow-network` invokes the fixed read-only Git tag
lookup at https://github.com/2026Allin/Mining-Market-Research.git. Without the flag,
check does not query that repository. Init/notice do not access the network.
Plugin instructions do not grant shell or network permission. Do not install,
upload, elevate or widen permissions as a side effect of maintenance.

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
requested result, even when `notice` is silent. If a notice is included, use its
exact footer without review/ack. Failed or skipped checks report uncertainty.

For upgrade intent, first do this fresh check. If newer, provide manual guidance:
open Customize > Plugins, select the existing plugin and use any update action
actually shown. For ZIP installs upload a maintainer-supplied newer plugin ZIP
through Add > Upload plugin, then start a new conversation. Do not invent a ZIP
download URL or suggest uploading a whole repository archive as a plugin.
If no newer release exists, do not recommend downgrading or reinstalling.
Never execute `update_installed_plugin.py`, install a CLI, alter permissions,
or claim installation succeeded. Only a new session's metadata can confirm its
loaded version; even that is not native installation inventory.
