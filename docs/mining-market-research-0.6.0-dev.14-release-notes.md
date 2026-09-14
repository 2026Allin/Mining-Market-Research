# Mining Market Research 0.6.0-dev.14 — development preview

This preview adds client-owned update coordination and connection version
declarations. It does not enable server-side update ownership or automatic installation.

- Codex uses the natively verified `http_headers` field to declare version,
  build, platform, channel and client ownership. Declarations are connection
  metadata, not proof that a conversation loaded matching Skill content.
- Native PreToolUse/PostToolUse Hook support shares temporary per-conversation
  state with the Skill fallback. Checks require host network permission; failures
  fail open and do not stop business tools. Server responses remain diagnostic only.
- Successful checks have a six-hour conversation-local cache. Displaying a
  reminder does not authorize installation. Refusal or no response does not
  permanently suppress future reminders. Upgrades require a new conversation.
- Claude ZIP packaging strips Codex declarations and validates package identity,
  links and content. Claude headers remain opt-in pending native host acceptance.
- Builds: `0.6.0-dev.14+codex.20260914085519` and
  `0.6.0-dev.14+claude.20260914085519`.

## Installation

Codex: install/update `mining-market-research@Anchises-Analysis`, then open a new
task. A full host restart may be needed to refresh an old task's MCP connection.
Claude Code: install/update `mining-market-research@anchises-capital`, then open
a new session. Claude Chat: upload the attached
`mining-market-research-0.6.0-dev.14-claude.zip` using Customize > Plugins > Add >
Upload plugin. Do not upload GitHub's whole-repository source archive.

## Acceptance and limitations

Pre-release regression: 283 tests, no failures, 10 skipped. Offline tests cover
version comparison, six-hour boundaries, reminder acknowledgement, failure
backoff, session-state isolation and unverified-server fallback.

Codex real-host tests verified build declarations and their refresh after new
tasks and a host restart. Actual Hook auto-invocation, real conversation/transport
session isolation, Claude live-host behavior and real dev.13-to-dev.14 upgrade
acceptance are not certified by those tests. Multi-device testing is deferred.
Automatic reminders remain best effort, not guaranteed background updates.
