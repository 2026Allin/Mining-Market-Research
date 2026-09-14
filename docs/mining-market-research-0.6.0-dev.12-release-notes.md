# Mining Market Research 0.6.0-dev.12 — development preview

This is a prerelease, not a stable or dual-host-certified release. Both platform
tags identify the same source commit.

## Included

- Mining Market Research plugin identity and directory migration; seven shared
  Skills with thin native host adapters and the 18-tool MCP contract.
- Company reports use get_company_report(auto/refresh): faithfully translate
  available reports or execute prepared live research in the current conversation.
- Stock queries support unknown totals, cursor pagination and actual server-side
  export decisions without obsolete complete-market checks.
- News/market fusion combines publication timing, daily prices, unusual volume,
  technical evidence, company-type priorities and live macro/metals research.
- Codex, Claude Code and Claude Chat now use isolated temporary session update
  state. New conversations check afresh; within a conversation the first use six
  hours after a successful check checks again. No hooks or background process.
- Dedicated upgrade Skill, explicit installation authorization, failure backoff,
  silent no-update behavior, and mandatory new conversation after installation.

## Installation and migration

The plugin ID is now `mining-market-research`. Older installations using the old
plugin ID/tag namespace may need manual migration; they are not guaranteed to
discover this release automatically. Existing tags are retained unchanged.

- Codex: refresh marketplace `Anchises-Analysis`, install
  `mining-market-research@Anchises-Analysis`, then open a new task.
- Claude Code: refresh marketplace `anchises-capital`, install
  `mining-market-research@anchises-capital`, then start a new session.
- Claude Chat: upload the attached `mining-market-research-0.6.0-dev.12-claude.zip`
  via Customize > Plugins > Add > Upload plugin, then start a new conversation.
  Do not upload GitHub's whole-repository source archive.

Release builds: `0.6.0-dev.12+codex.20260914025540` and
`0.6.0-dev.12+claude.20260914025540`.

## Validation and limitations

Codex local installation and session-state execution were tested. Shared automated
tests cover both platform contexts; this does not certify current Claude host
behavior. Claude Code/Chat live acceptance and Cowork certification remain open.
Agent-driven checks can be omitted by an agent despite instructions; reminders
are best effort, not guaranteed automatic software updates. Network permission
is host-owned. Storage/network failures must not be represented as current status.
Daily prices cannot establish intraday causality or prove insider activity.
Generated research and translations remain in the conversation, not MCP storage.
