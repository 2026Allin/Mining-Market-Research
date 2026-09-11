# Update reminder acceptance

## Evidence boundary

User-reported Claude Chat evidence for build `claude.20260911131511` confirms
the installed helper options and the low-level first-check/record/cache/silent
sequence. One business request executed probe/notice; a following request
omitted them. This is NOT a complete automatic-trigger pass.

The new compact interface and stronger entry gates require another real-host
run. Automated scenarios validate code, not whether an agent follows instructions.
Claude Code native upgrade, Cowork, and actual manual-upload reload remain
separate acceptance items. No GitHub release is authorized by this test plan.

## Deterministic offline regression

Run `python3 plugins/anchises-analysis/scripts/run_update_scenarios.py`.
Its JSON marks evidence as `offline-synthetic-not-host-certification`.
Synthetic version 999.0.0 and clock values exist only in the test harness,
outside the distributed plugin. All state lives in a temporary directory.
It checks:

- Newer release yields one manual notice, with session-loaded version basis.
- Refusal/ignore do not authorize installation, reset success time or repeat a notice.
- Every subsequent request still calls check, but cached checks do not fetch.
- At 21,600 seconds, another check can remind about the SAME version.
- Another conversation gets independent first-use state.
- A simulated newly loaded version does not trigger a downgrade/reinstall notice.

Run the unit suite for permission denial, timeout/backoff, malformed refs,
stale tickets, interrupted notice reservations, native behavior and package integrity.
There are no production CLI flags for injecting fake refs, time or state paths
into the new automatic `check` action. Legacy record still accepts captured refs.

## Real Claude Chat validation (pending for each new build)

Mount/parameter repair: host documents now live inside the core Skill at
`references/hosts/`. Chat first executes `init --platform claude --surface claude-chat`
and reuses its exact `context_file` with `--context-file`; it does not invent
session IDs or loaded-version strings. Check `invalid_arguments` separately from
storage failure; invalid inputs report `network_queries: 0` before any lookup.
The flattened core-only mount test validates init/probe/record/check/notice in
an isolated subprocess environment. This is still not a real Claude App pass.

1. Upload the newly generated ZIP and start a genuinely NEW conversation.
   Verify release_id against build-receipt.json and `--help` includes `check`
   and `--allow-network`. Do not reuse session IDs from another conversation.
2. Ask only: “使用 Mining Market Research 查询最近 3 条黄金矿业新闻。”
   Then ask another business question without mentioning update checks.
3. After both answers, request actual prior execution logs, with no retroactive
   calls. First request should run check; second must also run check and normally
   return cached with network_queries=0. Both use the same session ID. When no
   newer release exists, business answers must contain no update-related text.
4. Start another new conversation and repeat. It must generate a NEW session ID
   and check afresh. A copied token or cached result from the old conversation fails.
5. If helper network execution is denied, business should continue silently.
   It must not ask for broad Python permissions, install a CLI or falsely report success.

For an actionable-notice UI rehearsal, explicitly ask the agent to use a separate
temporary test database and the low-level probe/record/notice/ack commands with
synthetic refs and a clearly labeled simulated outcome. Never feed synthetic refs
to the native installer, publish a fake tag, touch normal session state or call it
a real release. The offline runner is the reference scenario, not evidence that
the UI rehearsal happened. Do not ship test instructions inside business Skills.

Actual upgrade acceptance needs an actual newer package. On Chat, manually upload
it and start a new conversation, then compare the loaded build with its receipt.
On Codex/Claude Code, verify native inventory after an explicitly authorized
upgrade and then test in a new session. No old session may claim hot reloading.

Record for each run: surface, full loaded build, new/same conversation, request,
actual check/notice/ack JSON, network query count, visible footer, and pass/fail.
Do not record credentials, full private conversations or bearer URLs.
