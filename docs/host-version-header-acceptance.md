# Host version-header integration acceptance

Status: original A/B header delivery failed; corrected Codex build now returns
delegated/client_managed after user installation and App restart. Exact received
version/build log correlation and session isolation remain pending. Phase two
is NOT fully passed. Claude hosts remain untested.

## Evidence collected

- Native `codex plugin list --json` reports enabled installation
  `mining-market-research@Anchises-Analysis`, version
  `0.6.0-dev.13+codex.20260914033532`, sourced from this repository's plugin directory.
- The installed `.mcp.json` has HTTP type and the production MCP URL, but no
  version headers. The repository source configuration also has no headers.
- Reading `.mcp.json` from both local release tags
  `mining-market-research/codex/v0.6.0-dev.12` and
  `mining-market-research/codex/v0.6.0-dev.13` shows no version headers.
  This is inspection of local tag contents, not a fresh remote release lookup.
- The native MCP status call observed during the preceding server check returned
  a successful business response and this `structuredContent.plugin_runtime`:

```json
{
  "schema_version": 1,
  "update_check_owner": "client",
  "version_basis": "unknown",
  "session_scope_verified": false,
  "check_status": "unavailable",
  "reason": "client_version_unknown"
}
```

- That response's text content did not include the runtime object. Consumers
  must inspect structured content; this does not prove every host exposes it.
- `command -v claude` did not locate Claude Code on the current shell PATH.
  This does not establish whether another installation exists elsewhere.
- No server-side request logs were accessed. Exact received version/build and
  request-to-conversation mapping remain unverified.

## Host matrix

| Host | Version headers | Upgrade refresh | Session isolation | Reminder deduplication | Phase three |
| --- | --- | --- | --- | --- | --- |
| Codex desktop | A/B headers packaged, but native responses remain client_version_unknown | New task loads B; old task retains A evidence; wire declaration unknown | Unverified | No server notices observed; Hook deduplication unverified | Not ready |
| Claude Code | Pending; CLI unavailable on current PATH | Pending | Pending | Pending | Not ready |
| Claude Chat (web/app) | Pending | Pending | Pending | Pending | Not ready |

## Next gate

Choose explicitly between two local integration builds and two new published
development releases. Existing dev.12/dev.13 cannot establish a version-header
A-to-B change because neither contains the headers. Do not modify historical
release tags or pretend synthetic HTTP calls are native plugin tests.

For either route, generate headers from each package's finalized release
metadata; never construct version values in model prompts. Keep owner `client`.
Collect server log receipts for exact received version/build/platform/channel,
without credentials or business payloads. For each test, record host version,
package identity, actual loaded Skill metadata separately from connection
declarations, request time, tool name, runtime result, and server correlation.

Install A, use a new conversation, make a native business-tool call, then
perform an explicitly authorized B upgrade. Compare the original conversation
and a new conversation. A connection declaration changing to B is not evidence
that the old conversation loaded B's Skills. Separately test reconnect, resumed
conversations, simultaneous conversations/versions, and another device.

Do not enable server ownership. PostToolUse remains diagnostic-only; runtime
fields must not suppress local checking. Preserve failure fallback and verify
local check/notice behavior in the actual host, not just unit tests.

No installation, release, hook trust change, or server modification was performed
while collecting the original baseline above.

## Local A/B run (2026-09-14 UTC)

User authorized two local integration builds. Native installation used
`codex plugin add mining-market-research@Anchises-Analysis` (CLI 0.149.0).
Both preserve SemVer `0.6.0-dev.13` and differ in build metadata. This tests
build refresh, not a change of the SemVer prefix.

| Build | Release ID | Local snapshot |
| --- | --- | --- |
| A | codex.20260914064701 | /tmp/mmr-native-ab.Fr14rF/A |
| B | codex.20260914064758 | /tmp/mmr-native-ab.Fr14rF/B |

Both installed successfully into versioned Codex cache directories. Both
configurations contain `headers` generated from package release metadata:
version, build, platform=codex, channel=dev, update-owner=client. Installed
configuration presence is not evidence of transport delivery.

MCP configuration SHA-256:

- A: `4573ff525b59694504ccf8882cd23fb662dfa766fb8882d34cc153857798ca4b`
- B: `67d76a6c4b5c8e99d4470a288b66bac20c3496249cbfc55edecb8366670397ee`

Native desktop task A: `01a09eab-fe51-75d0-89a0-ce41c735f80d`.
Native desktop task B: `01a09ead-db43-7121-84d1-417613da543d`.

A read its loaded Skill and metadata from the A cache, and made these native
calls (no synthetic HTTP):

| Stage | Tool | UTC start | Result |
| --- | --- | --- | --- |
| A before B install | get_connection_status | 06:48:32.707 | success; client_version_unknown |
| A before B install | get_available_exchanges | 06:48:39.470 | success; client_version_unknown |
| Original A task after B install | get_connection_status | 06:51:41.937 | success; client_version_unknown |
| New B task | get_connection_status | 06:51:31.805 | success; client_version_unknown |
| New B task | get_available_exchanges | 06:51:36.955 | success; client_version_unknown |

All five returned the same runtime object shown above. No `plugin_update`
was present, and neither runtime nor update was in text content. No exact
connection version/build was observable. Old-task loaded Skill evidence remained A.

No actual Hook context/receipt injection was observed in A. Skill fallback
`init` succeeded, `check` returned `network_not_authorized` with zero network
queries, and `diagnose` reported local ownership, null Hook receipts, no last
success, trust not observable, and server takeover disabled. This verifies
local fallback execution, not successful network checking or Hook activation.

After B installation, source manifest, release metadata and `.mcp.json` were
restored to their pre-test values; A/B snapshots and installed B keep the test
headers. This avoids contaminating shared Claude packaging with Codex headers.
An intermediate Hook test failed because of that cross-platform mismatch;
after source restoration all nine `test_hook_updates.py` tests passed.
Plugin validation passed for both builds using the repository virtualenv.
No release was published and no host trust or server settings were changed.

B independently read its B-cache Skill, release metadata and all five headers.
Its native calls still returned unavailable/client_version_unknown, not
delegated/client_managed. No real Hook injection was observed. Its local Skill
fallback also ran without authorizing network access. Thus installation/cache
refresh and fallback execution are observed, but wire delivery, trusted Hook
execution, successful update lookup, and remote session isolation are NOT proven.

Current installation is local B. Source remains the original published build
identity plus the pre-existing phase-one development edits. Do not reinstall
from restored source and expect the B test headers to remain.

Next diagnostic: distinguish plugin JSON parsing, desktop MCP connection
selection/reload, any intermediary header forwarding, and server ingestion by
matching real native request timestamps to server-side header logs. Do not
attribute the failure to a specific layer from client_version_unknown alone.

## Follow-up: configuration discrepancy and timed native request

User reports the public six-scenario server checks pass, explicit headers are
accepted, and Nginx does not strip these headers. These are user-provided server
observations; matching A/B server logs remain unavailable.

Both `codex mcp list --json` and the desktop-bundled binary's
`mcp get mining_market_research --json` resolve an enabled same-URL HTTP server
with `http_headers`, `env_http_headers`, and `http_headers_helper` all null.
The installed B plugin file has the five headers. This is a discrepancy between
installed package and CLI-resolved configuration, not a captured desktop wire
request. No matching direct entry was found in the user config.toml; the project
has no .codex/config.toml. A command-local plugin-enabled=false override still
resolved the server, but precedence/override semantics were not established;
this does not prove a duplicate connection or its origin. No persistent config
was changed.

Fresh native `get_connection_status({})` in the original task began and ended
within **2026-09-14 06:58:31 UTC** (clock precision one second). Business status
active, isError=false; runtime still client/unknown/unavailable with reason
client_version_unknown and session_scope_verified=false; no plugin_update.
Use a server log window of 06:58:25–06:58:40 UTC for correlation. No manual HTTP
request was substituted. No complete desktop reconnect was performed.

The local Skill checker was retained and returned network_not_authorized,
network_queries=0. Server takeover remains disabled. Full host reconnect and
effective-connection origin tracing remain pending.

## Follow-up: plugin-origin isolation

Server-side correlation supplied by the user matched 06:58:31 UTC to
23:58:31.649 PDT (previous local date). The log had version/platform/channel
None and notification_emitted=false. Owner=client is the server's selection,
not proof of receipt of the owner header.

A fresh short-lived desktop-bundled app-server was started solely for
`config/read(includeLayers=true)` and terminated afterward. The returned
configuration exposed the plugin enabled setting from user config.toml, but
no direct mining_market_research MCP entry. This query did not attach to the
existing desktop process. A sandboxed startup failed; the approved diagnostic
startup succeeded. No persistent configuration was changed.

The read-only process-local comparison
`codex mcp get mining_market_research --json --disable plugins` returned
`No MCP server named 'mining_market_research' found`, whereas normal lookup
resolves it. This identifies the plugin-loading path as the source of the
CLI-resolved connection. The earlier per-plugin enabled=false experiment must
not be used as duplicate-connection evidence.

Targeted endpoint search under installed plugin files, temporary marketplace
files, and user/project agent configuration found only the B installed
`.mcp.json` among the searched JSON/TOML files. Searches do not exhaust every
possible desktop runtime override.

Remaining ambiguity: plugin file selection versus JSON parsing/conversion.
The installed B file contains headers while CLI-resolved transport omits them.
The local source was restored after B installation, so source-versus-cache
selection must be accounted for in a further controlled test. A's original
native calls already failed before that restoration; restoration alone cannot
explain all A/B observations. Do not claim a specific parser bug without evidence.

Full desktop exit/relaunch is still pending and would interrupt the active
task. No server changes, fallback version defaults, account-level declarations,
or server takeover were introduced.

## Controlled parser test: root cause identified

Source and installed B manifest, release metadata and .mcp.json were made
byte-identical (three diff checks passed); a fresh desktop-bundled CLI still
reported null headers. A temporary plugin mmr-header-probe@mmr-parser-probe
then declared three distinct loopback endpoints. Native CLI parsing returned:

| Plugin JSON field | Effective http_headers |
| --- | --- |
| headers | null |
| http_headers | {"X-MMR-Probe":"http_headers"} |
| httpHeaders | null |

No business MCP call was used for this experiment. This establishes the wrong
field name as a concrete cause in the tested Codex parser. The earlier renderer
assumption that all plugin JSON uses headers was incorrect.

Renderer now uses http_headers for Codex and headers for Claude; generated
X-MMR declarations are cleared across aliases before host-specific generation
or opt-out. Claude packaging strips source declarations before generating its
own finalized build headers. Nine Hook/package regression tests and plugin
validation pass. Claude host header delivery remains unverified.

Corrected source build: 0.6.0-dev.13+codex.20260914071528 (local, unpublished).
Source remains fixed for the next install/restart; it has not been restored.
Installation and removal of the temporary probe were blocked twice by automatic
approval infrastructure reporting reviewer model capacity failure. Neither
command batch executed. Installed main plugin remains B; temporary probe
registration still exists. Its source is preserved at
/tmp/mmr-parser-probe.n6OBvV/isolated. No full App restart or production wire
verification of the corrected field has been performed.

Pending authorized native commands:

```sh
codex plugin remove mmr-header-probe@mmr-parser-probe --json
codex plugin marketplace remove mmr-parser-probe --json
codex plugin add mining-market-research@Anchises-Analysis
codex mcp get mining_market_research --json
```

## Corrected build after user restart

User executed the pending cleanup/install commands successfully and supplied
effective configuration containing all five http_headers for build
codex.20260914071528, then reported restarting the App.

On **2026-09-14 07:20:19 UTC** (00:20:19 PDT, same date), the original task
called native get_connection_status once. No synthetic HTTP or manual header
injection was used. isError=false, business status active. Runtime:

```json
{
  "schema_version": 1,
  "update_check_owner": "client",
  "version_basis": "connection_declared",
  "session_scope_verified": false,
  "check_status": "delegated",
  "reason": "client_managed"
}
```

No plugin_update was returned. This is native evidence of accepted connection
declarations, not proof of the exact received version/build or session isolation.
Correlate server logs in 07:20:15–07:20:25 UTC against expected version
0.6.0-dev.13, build codex.20260914071528, platform codex, channel dev, owner client.
Local checker reused the original conversation context and returned silent with
network_queries=0; it was not disabled by the server runtime. No new release,
server ownership, or cross-session cache was enabled.

## Server correlation confirmed by user

The user matched server logs to the 07:20:19 UTC native call and confirmed valid
version 0.6.0-dev.13, platform codex, channel dev, owner client, status delegated,
and no server notification. Native transmission of version/platform/channel
passes this round. This server evidence is supplied by the user, not obtained
through direct server log access by the plugin agent.

The existing server log does not include build. Receipt of
codex.20260914071528 is therefore NOT confirmed. Local configuration and runtime
connection_declared cannot fill that evidence gap.

Current phase-two acceptance:

| Item | Status |
| --- | --- |
| Codex native version/platform/channel after restart | Passed, server-correlated |
| Exact validated build received by server | Pending; log field unavailable |
| Declaration change in old/new conversations after upgrade | Pending |
| Multiple conversation/device isolation | Pending |
| Server ownership | Disabled; retain client checks |
| Claude Code / Claude Chat | Not verified |

Next prerequisite is server-side validated build diagnostics, implemented by
the server owner. Log a bounded, validated build value and explicit absent or
invalid state, never a fallback copied from client configuration. Preserve
existing request correlation and avoid logging credentials or arbitrary raw
headers. Once available, correlate the current build before repeating the
native A-to-B installation/old-task/new-task comparison. No server modifications
or additional installation were performed for this record update.

## Complete declaration correlation and corrected A-to-B attempt

User correlated the native call with server time 2026-09-14 07:45:14.171 UTC:
version 0.6.0-dev.13, build codex.20260914071528 validated for format/platform,
platform codex, channel dev, client/delegated, no notification. Complete
declaration reception passes for that request. This does not attest installation
contents or loaded Skill state.

For the new corrected A-to-B run, A is codex.20260914071528. A fresh native
get_connection_status call before upgrade occurred at 2026-09-14 07:48:06 UTC
(one-second clock precision), isError=false, connection_declared,
delegated/client_managed, session_scope_verified=false. Its exact wire build
still requires its own server-log correlation.

Local B is codex.20260914074807; both builds preserve SemVer 0.6.0-dev.13.
Snapshots: /tmp/mmr-ab-verified.RO6NZY/A and /tmp/mmr-ab-verified.RO6NZY/B.
Source manifest, metadata and http_headers are synchronized to B. Plugin
validation and nine targeted tests pass. This is build-metadata refresh testing,
not SemVer-prefix upgrade testing.

The B install command was rejected before execution because the approval
reviewer reported model capacity failure. No post-upgrade old-task/new-task
calls were performed. User must complete or authorize installation before
continuing. Do not restart the App before the post-upgrade old-task call, as
that would add a reconnect variable to the comparison.

## Corrected B installed by user: old-task observation

User supplied successful native installation output for codex.20260914074807.
Without an assistant-initiated App restart, this original task called native
get_connection_status once at **2026-09-14 07:52:43–07:52:44 UTC**. Business
success, connection_declared, delegated/client_managed, no plugin_update,
session_scope_verified=false. Exact wire build remains pending server logs.

CLI effective http_headers now declare B. Importantly, the host-provided Skill
catalog for this old task's new turn also points to B, and B's Skill and release
metadata were read. Do not assert that old tasks necessarily retain only A's
Skills. This does not erase previous conversational instructions or change the
earlier update-checker's immutable snapshot.

New-task test 01a09ee7-ad74-7810-9a76-419650aef166 completed. It read B's
host-listed Skill and release metadata, and called native get_connection_status
exactly once at **2026-09-14T07:53:47.360Z–07:53:47.512Z**. isError=false,
connection_declared, delegated/client_managed, session_scope_verified=false,
no plugin_update. Specific received build is not in the response.
All stages preserve SemVer 0.6.0-dev.13 and client ownership.

Server correlation windows (UTC on 2026-09-14): pre-upgrade 07:48:06,
post-upgrade old task 07:52:43–44, post-upgrade new task 07:53:47.360–.512.
The user subsequently supplied the corresponding server logs below. This run
does not verify multi-device/session isolation.

## Corrected A-to-B server correlation: passed for new-task build refresh

Server evidence supplied by the user, UTC on 2026-09-14:

| Stage | Server time | Received build |
| --- | --- | --- |
| Before upgrade | 07:48:06.917 | codex.20260914071528 (A) |
| After upgrade, original task | 07:52:44.201 | codex.20260914071528 (A) |
| After upgrade, new task | 07:53:47.427 | codex.20260914074807 (B) |

All three: version 0.6.0-dev.13, valid build, delegated/client_managed, no server
notification. New-task build declaration refresh passes this specific run.

The original task's Skill directory pointed to B while its native connection
still declared A. Skill directory, connection declaration, and the local
checker's version snapshot must be treated as distinct observations. Do not
infer one from another or overwrite a snapshot merely from a connection header.

Both builds have the same SemVer. This does not test newer-version comparison,
upgrade reminders, or isolation of update cycles. Neither connection identity
nor differing builds establish a reliable chat-session identity.

Next acceptance is multiple tasks, connection/restart lifecycle, resumed tasks,
and multiple devices. Server ownership stays disabled; retain client checks.

## Same-device multi-task sampling

Original task native get_connection_status sampled at 2026-09-14
08:10:32–08:10:33 UTC: isError=false, connection_declared,
delegated/client_managed, session_scope_verified=false, no plugin_update.
No usable transport session/connection identity was returned. No fabricated
UUID header or manual HTTP call was introduced.

Dispatch to existing B task 01a09ee7-ad74-7810-9a76-419650aef166 was rejected
by automatic approval infrastructure (reviewer model capacity); that sample
did not execute. Fresh-task sample was created as
01a09ef8-5bb4-75b0-8bce-577fbd8d0f66 and completed: exactly one native call at
2026-09-14T08:11:58.658467Z–08:11:58.892132Z. Loaded metadata B,
isError=false, delegated/client_managed, connection_declared,
session_scope_verified=false, no plugin_update. No usable connection/session
or request correlation ID was exposed in the response. Server comparison of
this sample and 08:10:32–33 UTC is pending; isolation is not passed.

Correlation must distinguish per-request IDs, transport session/connection IDs,
and real host chat IDs. Distinct request IDs alone cannot prove isolation.
If logs expose no session identity, record not observable rather than pass.
Use stable server-side redacted fingerprints where available, not raw tokens.
Reconnect and another-device tests require user participation and remain pending.

## Correlation and restart follow-up (2026-09-14)

User-supplied server logs confirm the same-device samples above: original task
08:10:33.558 UTC declared A; new task 08:11:58.935 UTC declared B. Both were
valid/client_managed with no notification. These supersede the pending
correlation status above, but do not establish chat-session isolation.

After the user restarted Codex and resumed the original task, its native call
was correlated to 08:42:22.180 UTC (01:42:22.180 PDT), request
6c189049ca934d079f17e2f77d61815c. The server received version 0.6.0-dev.13,
build codex.20260914074807, build_status=valid, build_reason=null,
platform=codex, channel=dev, owner=client, reason=client_managed,
status=delegated, notification_emitted=false. This specific restart refreshed
the old task's connection declaration to B. It does not attest Skill contents.

Multi-device testing is explicitly deferred by the user. Session isolation and
actual native Hook invocation remain unverified; server takeover remains off.

## Offline regression follow-up

44 targeted tests passed: 31 update-state/optimization, 9 Hook/renderer/package,
2 marketplace, and 2 corrected manifest assertions. Plugin validation passed.
The three obsolete headerless-config assertions now require exact Codex
http_headers, including version/build equality with the package manifest.

A new Codex synthetic dev.13-to-dev.14 test covers parsed remote refs, an update
notice, acknowledgement of display (not install consent), cached checks before
six hours, a new reminder at six hours, reload_required for an updated disk with
old loaded version, and silence after the loaded version catches up. Existing
tests cover refusal/no response, timeout/backoff, missing permission, temporary
state/session isolation, and no unverified server takeover. All use temporary
state and mocked lookups, not real publication, installation or host certification.

The full suite was not executed this round: escalation for loopback mock HTTP
services was rejected because the automatic approval reviewer was at capacity.
No permission workaround was used. Full-suite regression remains pending.
