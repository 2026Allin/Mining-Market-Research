# Mining Market Research 0.6.0-dev.15 (preview)

- Match canonical Mining Market Research MCP tool names for native Hooks.
- Add bounded, redacted Hook diagnostics independent of update-state storage.
- Enable the fixed repository's noninteractive read-only Git version lookup in
  PreToolUse. This does not change host network policy or authorize installation.
  Review the changed Hook command before trusting it. Python 3 and Git are required.
- Reuse the six-hour per-conversation success cache; inject shared context only
  on first use or check-status change. No update means no user-facing reminder.
- PostToolUse remains network-free and diagnostic-only for server ownership;
  server takeover is not enabled.

Codex CLI native execution verified: paired Pre/Post events, successful version
lookup, shared context, cached follow-up and one context injection across two
requests. Real newer-release notification/installation acceptance tests remain
pending. Claude native Hook execution has not been certified; Claude Chat retains
its Skill-driven fallback and manual installation workflow.

This is a development prerelease, not a stable release. After upgrading, start a
new session and review changed Hook definitions through the host. Never infer
installation consent from silence or a report-refresh confirmation.
