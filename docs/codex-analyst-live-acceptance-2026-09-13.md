# Mining Market Research — Codex analyst acceptance

Date: 2026-09-13. Scope: real native Codex calls only; no Claude execution.

Test task: `01a09993-b9ab-7960-841e-8dd5c4215d08`
(`Mining Market Research 移除旧版后验收`). Installed build:
`mining-market-research@Anchises-Analysis`,
`0.6.0-dev.11+codex.20260913065337`.

This records test prompts, observations and limitations, not report contents.
No installation, upgrade, publication, report upload or database write is part
of this acceptance run. Only the plugin's ordinary local update-state helpers
may attempt their normal state operations.

## Completed cases

### A0 — Baseline company report

Turn: `01a09993-bae7-7a01-a77f-1f0d27284e48` (previous test request).
Native access check → resolve ASX:BHP → `get_company_report(auto, zh-CN)` →
`generation_ready` → native web research → complete seven-section Chinese
report. No `prepare_company_report_generation`, report persistence or old
Skill namespace observed. Elapsed: 623.223 seconds.

Pass: the actual fresh-research branch. Does not cover a stored report or its
translation/refresh-confirmation branches. Full financial accuracy is not
certified solely by workflow completion.

### A1 — Investment committee challenges report numbers

Prompt:

> 先不要重新做整份报告。基于你刚才的 BHP 报告，投委会会追问：经营现金流减资本及勘探支出，为什么不等于你列的自由现金流？请把差额算清楚，区分已证实的解释和还缺的证据。另外，如果铜价下跌 20%，能不能据此直接说 BHP 利润也下降 20%？请指出这种推断的问题。用中文，控制在 800 字左右，不需要最后再问我问题。

Turn: `01a0999d-9b30-7082-9d01-8c5b00fb53ac`.

- One native `get_connection_status`, six web actions, no report-selection or
  report-preparation call. Existing conversation report was retained.
- Answer reconciled the cash-flow definition difference, separated supporting
  evidence from missing transaction detail, and qualified commodity-price
  sensitivity as a static extrapolation, not a profit forecast.
- Evaluator independently checked the relevant cash-flow reconciliation and
  sensitivity rows in the [official FY2026 annual report](https://www.bhp.com/-/media/documents/investors/annual-reports/2026/260818_bhpannualreport2026.pdf).
- No unwanted follow-up question. Pass for this observed case.
- Elapsed: 227.100 seconds; 28 shell commands, largely instruction reads and
  line-count checks. This is an efficiency observation, not proof that all
  elapsed time was caused by instruction reads.

## Open findings

### A2 — London mining morning brief: mixed result

Prompt:

> 我在准备矿业晨会。请找过去 7 天在伦敦上市矿业公司的最新 3 条重要公告或新闻，优先融资、项目进展和并购。每条列出发布时间、公司及上市代码、发生了什么、潜在影响和目前不能下的结论，并附原始来源。不要扩展到其他交易所凑数，也不要生成公司报告；不足 3 条就如实说。中文简洁回答，不要附后续提问。

Turn: `01a099a1-6d2e-7593-8118-9d767ce7a098`, 279.315 seconds.
Native calls: access, facets, search (failed), search (succeeded), web-research
preparation. Then 21 native web actions; no report-generation call.

- First search used `LSE`, September 7–13 and six event labels which were
  present in the preceding `list_news_filters.events` response.
- Actual error: “A news filter is invalid or outside the current news policy.
  Check list_news_filters and news_policy; no filters were dropped.”
- Agent then retried without the entire `tags` array, preserving exchange and
  date bounds. It did not establish that the refusal was merely a safe syntax
  issue, and the final answer did not disclose this retry.
- This fails the current Skill's explicit no-dropping-filter failure rule.
  The displayed facet labels versus rejected search also merit MCP contract
  investigation; the exact rejected value/reason was not reported by the tool.
- The successful search returned two oil/gas-related cards, not hard-mining
  candidates. Agent did not mislabel these as the requested three mining items;
  it used `prepare_news_web_research` and real web sources instead.
- Final answer selected three AIM-listed companies and separated events,
  analytical implications and unsupported conclusions, with original links.
  It disclosed database versus web supplementation and did not generate reports.
- Classification: business scope/answer structure passed; error recovery failed.
  Individual announcement facts were not exhaustively independently audited.

### Update-check persistence unavailable

Baseline `check` and `notice` returned `silent / state_unavailable`.
The default macOS state directory
`/Users/anchises/Library/Application Support/MiningMarketResearch` did not
exist when inspected read-only by the evaluator. It is outside ordinary project
write roots. A sandbox storage denial is plausible, but the helper collapses
multiple exception types into the same reason; exact cause is not established.

Business continuity and silence are expected degradation, not a successful
six-hour update check. Do not claim either a fresh remote lookup or a verified
up-to-date version from this response. The exception response also lacks
`network_queries`, contrary to the compact-interface documentation's promise.

### Repeated instruction loading

Short same-report follow-up generated many instruction-read commands. Consider
a compact continuation path and reuse of fully read, unchanged shared
instructions within a session, subject to host skill-loading requirements.
No runtime instruction changes have been made by this test.

## Additional completed cases

### A3 — Same-market price/liquidity comparison: mixed result

Prompt:

> 再看交易层面的比较：只比较澳交所的 BHP、Rio Tinto 和 Fortescue，最近 20 个共同交易日谁表现最强？请列区间首尾收盘价、价格回报、日均成交额，并说明成交额口径及是否复权。今天没有数据就用三家公司都有数据的最近日期，不能把不同日期、币种或其他上市地混在一起。用一张表加简短结论，不写三份公司报告，不需要 CSV 或最后的提问；没有的数据标缺失，不要估造。

Turn: `01a099a5-fe90-7a62-9653-0e5579b41f38`.

- `get_latest_dates({})` failed; `exchanges` is required. Agent then discovered
  exchanges and succeeded with `exchanges=["ASX"]`.
- Discovered stock schema, physical table schema and available trading dates.
- Validated a CTE selecting 20 dates with all three symbols present, then
  requested at most 200 rows ordered by date/symbol through `run_readonly_sql`.
- SQL execution was issued at `2026-09-13T07:25:14.326Z` and still pending at
  `07:28:12Z`. A slow native query is an observation; its database/server/network
  cause is not established. No fake completed result is counted.
- No new identity resolver calls preceded the query. Only BHP had a previously
  observed canonical identity; Rio Tinto and Fortescue were directly mapped to
  RIO/FMG. This does not meet the shared verified-identity prerequisite.
- SQL failed after 200.250 seconds with `Stock data is unavailable.` No detailed
  database cause was exposed; do not equate this message with a proven DB timeout.
- Agent switched to `screen_stocks` over ASX, August 17–September 11, the same
  three symbols, ordered by date/symbol, page size 200. This returned in 119.496
  seconds with 60 rows, no truncation, no warnings and no continuation cursor.
- Evaluator independently recomputed the three returns and close-times-volume
  averages from that actual tool response: all final rounded figures match.
  All three had 20 observations, identical endpoints, AUD units and `valid`
  adjustment status; returned raw/adjusted prices were equal.
- Final correctly labelled turnover as an estimate rather than actual traded
  value, identified non-dividend price returns, and did not generate reports,
  export a CSV or fetch unrelated exchanges.
- Total elapsed: 559.280 seconds. Numerical output passed against returned
  data; identity prerequisite and initial argument validation failed; latency
  needs investigation. This is not an independent audit of vendor price data.

### A4 — Existing research only; user declines new research

Prompt:

> 回到刚才晨会里的 Beowulf Mining。我想先看研究库里已有的公司报告，中文展示，保留原来的研究日期；这轮先不要重新开展实时研究。如果目前没有可供展示的报告，就说明限制并停下。重点想了解融资能否支撑 Kallak 推进，但不要把刚才新闻中的新事实混进已有报告译文。

Turn: `01a099ae-f839-7052-95ab-0d07b092598f`, 101.187 seconds.
Actual access check → identity resolver → `get_company_report(auto, zh-CN)` for
LSE:BEM, with the user's financing/Kallak focus preserved.

- Real return was `generation_ready`, not `report_available`.
- Agent respected the user's explicit refusal of new research: no native web
  calls, no generated report, no invented original report date or translation.
- No fabricated news code: the preceding Beowulf story came from a public web
  announcement, not an MCP news card with an ID.
- Pass for the stop/no-new-research boundary. Does not validate stored-report
  translation or MCP-linked news-ID propagation.

### A5 — ETF versus operating-company scope and ticker collision

Prompt:

> 我还想把 GDX 纳入矿业研究名单。请给纽约市场的 VanEck Gold Miners ETF（GDX）做一份公司研究报告，重点看它自己拥有的矿山、黄金产量和采矿成本。如果这个研究口径不适用，请先指出问题，不要把基金持仓公司的资产说成基金自己经营的矿山，也先别换成其他公司生成报告。

Turn: `01a099b0-fdcf-71b1-9f11-b8dbef227126`, 103.823 seconds.

- Initial bare `GDX` resolution hit another issuer. Agent rejected the mismatch,
  resolved the full fund name and checked VanEck's official website.
- Initial report call used `NYSE Arca` and failed; corrected `NYSEARCA` call
  succeeded. Exchange-code input normalization needs improvement.
- **Actual MCP status was `generation_ready`, not `not_eligible`.** Returned
  company used `instrument_type=unknown`, `classifier_sector=Others`, and
  `instrument_verification_required=true` for the externally supplied identity.
- Agent correctly stopped at the ETF/company boundary based on verified fund
  identity. No report for an unrelated GDX issuer or a holding was generated.
- Pass: host-level identity conflict handling and company/fund scope. Not a
  pass for server-side ETF classification or the `not_eligible` response branch.

### A6 — Junior gold equity-financing quick take

Prompt:

> 最后帮我做一个小矿企融资快评：在 TSXV 上市的黄金矿企里，找最近 30 天最新的一条股权融资公告，实际读取公告正文。用中文说明发行价、计划或已完成的募资额、是否带认股权证、资金用途，以及能否算出对现有股东的稀释比例；缺少已发行股数就不要硬算。区分“宣布融资”和“融资交割完成”，只分析这一条，不生成完整公司报告，不下载或保存文件，也不需要后续提问。

Turn: `01a099b4-17f7-7931-bb54-67807b409994`, 168.252 seconds.

- Access → facets → two successful searches → one `get_news_article` using the
  exact returned ID `100000038863` → web preparation and two host web actions.
- Article result was `found`, `content_truncated=false`, with a verified
  `companies` entry for TSXV:SCOT. This was an actual body read, not only a card.
- Web supplement checked for more recent coverage and opened the same original
  announcement; no report call, CSV export, report upload or file download.
- Answer distinguished announced versus completed financing, share subscription
  terms versus possible finder warrants, planned proceeds versus cash received,
  and did not fabricate a dilution percentage without the pre-issue share count.
- Pass for the observed retrieval/analysis boundary. Minor terminology issue:
  `flow-through shares` was rendered as `流通股税务优惠股`; use an accurate Chinese
  tax-flow-through term with the English label, not `流通股` alone.
- Latest means latest found within this query and public-web checks, not a
  completeness guarantee for all TSXV disclosures.

## Overall outcome and next priorities

Seven completed scenarios including the baseline. Six new natural analyst
questions were sent separately into the same native task, without naming the
desired tools in those business prompts. Sixteen distinct MCP tools were
actually invoked. Invocation is not success: SQL failed and there were invalid
argument/filter calls. `prepare_company_report_generation` and
`create_csv_export` were deliberately not forced into unrelated requests.

1. **High: forbidden filter-drop recovery.** Correct the news rejection branch;
   diagnose the displayed-facet/search disagreement with the MCP implementation.
2. **High: update persistence.** Establish a permitted storage approach and
   accurate diagnostic receipts. Silent degradation is not a working reminder.
   Ordinary checks did not use `--allow-network`; storage repair alone would
   not establish authorization for remote lookups.
3. **High: identity gate.** Require verified identities before market queries,
   not only company reports; keep the successful same-ticker conflict guard.
4. **Performance: bounded history retrieval.** Investigate the 200-second SQL
   failure and 119-second screen; use known date bounds and supported structured
   queries where possible, with bounded retries that preserve scope. Do not
   label the exact server/database cause as proven.
5. **Medium: argument and terminology quality.** Avoid missing exchange arrays
   and display-name exchange codes; improve flow-through-share terminology.
6. **Efficiency: instruction loading.** Reduce needless rereads for unchanged
   same-report follow-ups without bypassing host-required Skill instructions.

Not certified: real `report_available` translation, accepted stored-report
refresh preserving news IDs, server `not_eligible`, denied network/OAuth cases,
simultaneous report-refresh/plugin-upgrade consent, CSV export, standalone Brief
or fundamental-comparison Skill coverage, and Claude environments. No mock
response was substituted to manufacture these passes. No fixes or releases
were performed; the only repository change in this test turn is this record.
