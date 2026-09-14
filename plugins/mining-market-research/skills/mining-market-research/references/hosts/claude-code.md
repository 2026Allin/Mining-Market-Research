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

This adapter covers Claude Code only. Claude Chat and Cowork require separate
installation and capability validation and are not implicitly certified.
