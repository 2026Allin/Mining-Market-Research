# Claude Code native host

Load all shared skills and the same remote MCP through the native plugin
manifest. Resolve logical tool names against the active connection; namespace
prefixes are host-owned. Do not infer tool availability from installed files.

Use the available native web capability for live research. If absent, report
the missing supplement and preserve supported evidence. Do not replace a
prepared research prompt with an assertion that research was completed.
Present temporary CSV URLs as download links; persist files only when requested.

Read bundled plugin-update-claude instructions only for explicit installation,
update, or diagnostic requests. Ordinary research follows shared
`update-notifications.md`: init once per conversation, then check/notice using
the returned context_file. The six-hour cache is session-only in temporary
storage, comparing the session-loaded version without native inventory.
Native inventory remains mandatory for authorized upgrades.
Use fixed Git lookup only when due. Trusted plugin Hooks may share this context;
see [Hook setup](../hooks.md). No automatic installation,
or changes to host permission settings. Reload through the supported host workflow
before testing an updated installation.

Stop verifies the exact pending footer using last_assistant_message, not an
assumption that the transcript is already flushed. UserPromptSubmit tracks a
local turn when the host supplies no turn_id; PreToolUse can recover prior
positive evidence. These operations are local-only and fail open. Never send
ack or review from the agent. If Hooks are unavailable, use attempt_only with no
conversation input, including App Code. Surface=native does not enable evidence
mode; the helper requires an actual matching open-turn Hook receipt.

Claude uses one package across web Chat, App Chat and App Code. Loaded builds may
lag installation until a new session. Capabilities, not separate package names,
choose the path; no CLI installation is required just to use this plugin.
For explicit upgrade, verify the supported installer and matching inventory/source.
If unavailable, provide only an actually available UI action or maintainer ZIP and
verify loaded build in a new session. Never promise an Update button or infer CLI
availability from the desktop label. Cowork capability remains separately verified.
