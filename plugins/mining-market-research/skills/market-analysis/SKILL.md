---
name: market-analysis
description: Analyze structured stock-market data through Mining Market Research, including prices, returns, screens, rankings, multi-stock historical analysis, and CSV downloads. Use for quantitative market data, unusual-volume or price-move explanations, or supported-market discovery, including screens with attached company introductions. Do not use for full company reports, narrative company comparisons, news-only work, or introductions as the primary deliverable.
---

# Mining Market Research — Market Analysis

<!-- BEGIN GENERATED BUSINESS ENTRY -->
## Execution order for this request

These maintenance steps surround the business workflow. Apply on every substantive request
when permitted, once across all components; maintenance is not a business prerequisite.
On any host, if local script execution is denied or needs ungranted approval, skip
maintenance and continue step 4; do not repeatedly request permission or claim a check ran.
Init/notice only read bundled metadata and write session-local temporary state;
check contacts the fixed release repository only with authorized --allow-network.
These actions do not upload chat content, install software or grant permissions.
An explicit plugin check/upgrade follows Upgrade instead, with no second check.

1. **Locate the helper and reuse context.** Locate the plugin's
   `mining-market-research` core Skill from the host-provided Skill path.
   Its `scripts/update_state.py` is `<helper>` below; use its actual absolute path.
   Do not guess a sibling directory name on flattened Claude mounts. Reuse the
   exact `context_file` supplied by a Hook or earlier in this conversation.
   Never borrow another conversation's file or invent a session ID/version.
2. **Initialize only when needed.** Claude web/Desktop Chat has no plugin Hooks:
   on first use run `python3 <helper> init --platform claude --surface claude-chat`.
   Native hosts: reuse a Hook context; if only an exact host session ID is available,
   join with `init --platform <codex|claude> --host-session-id <actual-id>`.
   If neither is available, let the first already-needed business MCP call return
   before fallback initialization: `init --platform <codex|claude>`. Do not make an
   extra MCP call just to obtain a Hook. Keep the returned context, not the example
   placeholders. Missing CLIs alone do not identify the host.
3. **Check once, even on consecutive requests.** A successful recorded/cached Hook
   receipt from THIS request satisfies this step. Otherwise run
   `python3 <helper> check --context-file <actual-context>` once. Add
   `--allow-network` only when the host already permits this helper's fixed Git
   lookup; never broaden permissions or prompt repeatedly for automatic checks.
   No flag means the helper may report network_not_authorized, not “up to date”.
   Do not run an extra probe/Git/record sequence. Failures remain silent and do not
   block business work; never claim a check ran when it did not.
4. **Perform the business workflow.** Read and follow the complete canonical workflow at
   [../mining-market-research/workflows/market-analysis.md](../mining-market-research/workflows/market-analysis.md).
   Resolve its relative links from its own directory. On flattened mounts, read
   `workflows/market-analysis.md` from the actual core Skill found in step 1. Read
   required business references fully; report unavailable evidence rather than
   inventing rules. The workflow owns the business result, not a separate Skill.
5. **Finalize once.** For a successful normal-prose answer run
   `python3 <helper> notice --context-file <actual-context> --locale <zh-CN|en>`.
   If update_available, copy returned `footer_text` exactly as the final standalone
   paragraph. For silent, append nothing. Do not reserve for strict JSON/CSV,
   clarification, failure or refusal acknowledgements. Never ack before sending.
6. **Let actual capabilities determine confirmation.** Never run review/ack or
   pass conversation text to maintenance scripts on any host. Without matching
   native Hook evidence, notice uses attempt_only, including App Code with no Hooks.
   At most two attempts per cycle are allowed; no agent confirmation call is needed.
   With matching Hook evidence, Stop/recovery may confirm; pending is not delivered.
   A native surface label, available CLI or successful init does not prove Hooks ran.

For permission-specific alternatives, lost context and diagnostic details, read
[update policy](../mining-market-research/references/update-notifications.md).
The helper owns six-hour timing and retries; a reminder never authorizes installation.
<!-- END GENERATED BUSINESS ENTRY -->

For event impact or price/volume explanations, follow the owning workflow's
fusion branch and its shared company-type priorities and macro web research.
Do not assume another Skill or the coordinator has loaded those rules.
Headline-only and CSV-only tasks keep their lightweight paths.
