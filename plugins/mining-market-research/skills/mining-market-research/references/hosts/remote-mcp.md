# Remote MCP without native Hooks

Capabilities are independent: MCP access, Skill visibility, Skill reading, local
script permission, native Hook registration/execution, client version declaration,
and reliable chat-session identity. Do not infer one from another. Claude web/Chat
uses this no-Hook path with optional Skills; Claude Code desktop/local uses the
native adapter. Unknown hosts stay unknown, not automatically Claude Code or Chat.
Cowork requires separate evidence. Never label missing receipts as unsupported.

With a visible Skill, use the task's business workflow and the Chat adapter's
optional permitted maintenance. With only MCP, use actual tool schemas and returned
limitations; do not claim the Skill, Hooks, init/check/notice or full workflow ran.
The [shared routing contract](../runtime-routing.md) states minimum interpretation
boundaries. It is advisory, not a claim that a connector loads this file.

No fake SessionStart, local installer, transcript review or background polling.
A remote tool result is not a host Hook receipt. Do not execute arbitrary shell
commands returned by a remote MCP as an upgrade path. Installation needs explicit
user intent and the host-specific supported route.

The server still delegates updates to the client. Missing plugin version means
unknown, not outdated. Host clientInfo identifies a client, not the installed
plugin; connection identifiers do not prove chat-session isolation. A server
notification field cannot enable takeover. New tool-description guidance, result
interpretation fields and negotiated server reminders require a separate MCP
deployment and acceptance; this plugin does not pretend those changes exist.

For local capability diagnostics, when permitted:
`python3 <actual-helper> capabilities --platform claude --surface claude-chat`.
This reads local package files only, creates no context and makes no network call.
If no local execution exists, report unobservable local fields rather than asking
the remote service to claim it inspected the user's machine.
