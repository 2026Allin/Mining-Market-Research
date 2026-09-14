# Mining Market Research — Codex fusion acceptance

Scope: shared Skill implementation, local Codex reinstall and native fresh-task
tests. No GitHub release, no Claude runtime claim, no hook or background monitor.

## Implementation

- Keep seven Skills and shared business workflows with thin host adapters.
- News-led and price/volume-led impact questions enter the same fusion component.
- Maintainer-editable mining priorities select actual company stage and event type.
- Publication time is an anchor, not proof of first disclosure; daily-bar and
  unavailable-response-window limitations are explicit.
- Targeted host web research adds relevant, dated macro/metals evidence; explicit
  no-web constraints and missing sources narrow the conclusion.
- Offline arithmetic uses real observations, excludes the evaluated day from
  volume baselines, retains observed zeros and withholds unsupported metrics.
- Headlines, translations and CSV-only requests do not automatically expand into
  research. Existing report selection, pagination/export and access rules remain.

## Automated checks

`PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests -q`
ran 267 tests total: 257 passed and 10 skipped. Skips are not real-agent proof.
Both specialist Skill validators, plugin validation and `git diff --check` passed.
Coverage includes arithmetic edge cases, explicit-offset session alignment,
dependency reachability from both entries, bundle contents and existing regressions.

## First installed build and native task

- Build: `0.6.0-dev.11+codex.20260913161830`.
- Task: `01a09b90-a3ee-7382-a761-be58097160c6`.
- Cases: Scottie financing impact, BHP monthly price/volume attribution, latest
  three gold-mining headlines.
- Native calls observed: connection, filters, identity, news search/article,
  available exchanges, latest dates, stock schema, stock screens and news-web
  preparation. Actual host web and bundled arithmetic also executed.
- Failure observed: a preferred 20-observation baseline was incorrectly mapped
  to nonexistent server column `avg_volume_20day`. The task recovered using real
  schema fields. Shared instructions were strengthened before the next build:
  analytical windows do not create MCP columns; exact field mapping is required,
  and historical projections should avoid repeated bulky issuer metadata.
- Further first-round review found overly strong motive attribution from empty
  same-day news and a same-date LME/ASX comparison that did not establish data
  availability at the earlier ASX close. Both received explicit shared guards.
- Latest-news retrieval was clarified: supported facet-only browsing should not
  add generic full-text terms; metal tags do not establish the primary commodity.
- Native update helper returned `silent/state_unavailable`. This is an explicit
  environment limitation, not a passing automatic-update check. No host permission
  settings were changed.

## Retest

Corrected build `0.6.0-dev.11+codex.20260913163233` was installed after uninstalling
the first-round build. Installed Skill files match the source tree exactly.

- News-only entry task: `01a09b9d-86b8-7f20-ae76-34373ffd0f3d`.
- Market-only entry task: `01a09b9d-9723-7431-a162-c8fa41447e04`.

Both tasks completed. Market entry used lagged/pre-ASX LME observations instead
of same-date future fixings, separated ex-dividend price effects, and explicitly
rejected using empty news results as proof of investor motives. One global
concurrency refusal on list_news_filters was recovered with one later retry.
News entry used real 30-day fields and independently calculated its 20-day
baseline, distinguished proposed financing from completion, and examined an
overlapping drill announcement. Its macro search did execute but comparable
gold data was unavailable; that limitation appeared only in the audit, prompting
an explicit business-answer completion check in the next revision.

### Second-round observations and follow-up correction

Both isolated entry tasks actually read the shared priorities, timing, metrics
and macro references. Native stock queries no longer used nonexistent 20-day
server fields. News entry separated the latest snapshot from the OHLCV range.
However, it repeated identical OHLCV range requests after visible output was
clipped. A shared recovery rule was added: consume an intact native result if
available, otherwise restart once with smaller display pages and preserve the
same logical scope, then follow cursors; never splice old/new pages or bypass
service limits. Calculator output should be summarized programmatically rather
than repeatedly dumping an oversized series.

## Third local build

- Installed build: `0.6.0-dev.11+codex.20260913164516`.
- Prior build uninstalled through the app; new build installed from the confirmed
  local marketplace. Installed Skill tree matches the source.
- Fresh task: `01a09ba9-5f21-7420-9d39-4275b9d7bffc`.
- Initial analyst question: Scottie financing with three months of observed
  history, volume samples and cutoff, explicitly using database evidence only.
- Main case completed: one 64-row history query plus one dated market-cap
  snapshot, no duplicate history query, no cursor needed and zero web calls.
  Calculator ran successfully with a 20-observation volume baseline. The answer
  disclosed provisional daily data, estimated rather than official share count,
  only one event-day observation and the user-excluded macro comparison.
- The transport-truncation fallback was NOT triggered in R3; its policy guards
  are regression-tested, but this run is not proof of that exact recovery branch.
- Follow-up on pre-news activity: reused existing observations and declined to
  infer prior knowledge/insider trading. No new business-data or web lookup.
- Hypothetical post-close announcement: correctly treated as hypothetical and
  identified zero post-announcement observations in the existing dataset.
- Latest gold-primary headlines: facet-only `search_news` without generic q,
  four body reads within the five-call budget to verify commodity focus; three
  articles delivered. No stock, web, report or export calls.
- User-provided sentence translation: only the translation was returned; no
  MCP, web, calculator or update-check calls (not a substantive research request).
- Explicit technical follow-up completed through Market Analysis: actual
  `rsi_10`, `sma_20`, volume and indicator-quality fields were fetched for 28
  observations. The response named RSI(10), combined the trend/momentum and
  volume evidence with the financing terms, and disclosed provisional prices,
  the single event-day cutoff and the excluded macro comparison. No web,
  report or export calls; existing news and listing identity were reused.

## Final assessment

Three local reinstall rounds and four fresh Codex tasks completed. The tested
news/market entry points both reach shared fusion rules; targeted fixes were
followed by new-build retests rather than rewriting a running task's instructions.
Final build: `0.6.0-dev.11+codex.20260913164516`, installed and enabled; no other
Mining/legacy-name plugin appeared in the native installed inventory.

The sampled core acceptance behaviors passed. Do not interpret that as an
exhaustive or deterministic guarantee: exact host-output-truncation recovery was
not re-triggered in the final build, and update-state storage remained unavailable.
The final complete suite ran 267 tests successfully (257 passed, 10 skipped),
specialist Skill and plugin validation passed, and source/installed Skill trees
matched. Existing unrelated worktree changes were preserved; no remote release.

## Evidence locations

- [R1 audit](/Users/anchises/Documents/Codex/2026-09-13/mmr-fusion-live-test-r1/outputs/mmr-fusion-r1-audit.md)
- [R2 news audit](/Users/anchises/Documents/Codex/2026-09-13/mmr-fusion-news-r2/outputs/news-r2-audit.md)
- [R2 market audit](/Users/anchises/Documents/Codex/2026-09-13/mmr-fusion-market-r2/outputs/market-r2-audit.md)
- [R3 audit](/Users/anchises/Documents/Codex/2026-09-13/mmr-fusion-boundaries-r3/outputs/r3-audit.md)

## Scope limits

These are native Codex observations, not Claude runtime verification or proof
that all 18 tools and every company type were exercised. The default priorities
cover additional company types; royalty/developer variants beyond the actual
issuers remain candidates for further live evaluation. Unit fixtures cover
missing/zero values and time boundaries, not every possible live data condition.
Agent-driven instructions are best-effort, not a deterministic runtime engine.
The known update-state storage limitation remains separate from successful local
installation. No hooks, permission changes or GitHub publication were performed.
