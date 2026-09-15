# Shared update reminders: Hook and Skill fallback

Apply on every substantive Mining Market Research request, including requests
in an old conversation, even when only a specialist Skill was selected. The
agent or a trusted plugin Hook invokes the same helper; no daemon is used. Reuse one
probe per user request across all components. This is best-effort agent behavior,
not a promise of execution while the user is idle.

Claude web/Desktop Chat overrides: maintenance requires permitted local execution,
never gates business work, and uses attempt-only notices without review/ack or
conversation input. If permission is absent, skip maintenance without repeated
approval prompts. See the [Chat adapter](hosts/claude-chat.md) for data boundaries.

## Native Hook coordination (phase one)

Read [Hook installation and diagnostics](hooks.md) for setup or troubleshooting.
Phase one keeps `update_check_owner=local`. Proposed MCP `plugin_runtime` fields
are diagnostic-only; neither a header nor a server claim enables takeover.
If the Hook supplies a context_file, reuse that exact path, including for notice
and explicit upgrade checks. Never create a second context. If no context was
supplied but the native host exposes its exact session ID, use
`init --platform <host> --host-session-id <host-provided-id>` to join the same
context. Never invent an ID or scan other sessions. Chat keeps its existing init.
If a native host exposes neither a context nor an exact session ID, defer the
automatic check until the first already-needed business MCP call returns. Use
the Hook context if supplied; otherwise initialize the Skill fallback then.
Do not make an extra MCP call just to discover a Hook. This avoids a Skill-created
cache before the first Hook has had a chance to supply its shared context.

A recorded/cached Hook check from THIS request satisfies the request's check.
Otherwise execute the Skill check below using the same context. Absence of a
Hook is not proof it was disabled or untrusted. Only the host can report trust.
Hook context injection is not user-visible delivery: it never reserves or acks
a notice. The existing finalization/authorization rules below still apply.

## At the start of the plugin request

### Preferred compact interface

On EVERY substantive request without a successful current-request Hook receipt,
actually execute `update_state.py check` once,
including immediately consecutive turns. The helper performs probe, at most
one fixed Git lookup, and record/failed. Never substitute a remembered result.
Use the session context below on every host. Add `--allow-network` ONLY when the host already permits this
helper's fixed Git lookup. This flag cannot grant host permissions, and a rule
allowing a direct Git command does not automatically allow a Python wrapper.
Do not ask for broad Python/network permissions or elevate during automatic
business checks. Without permission, run without the flag: it remains silent
and backs off for 30 minutes. Never install anything from a check.

The compact flow is `check -> notice -> send -> delayed confirmation`. The `check`
result includes `network_queries` (0 or 1); success is `recorded`, a cache hit
is `cached`, and unavailable access/failure is silent. Do not call standalone
probe/Git/record additionally in the same request. Native explicit install
continues to use fresh captured refs and the guarded installer.

The low-level probe/record protocol below remains for diagnostics and hosts
that permit ONLY a direct Git invocation. Choose one protocol per request,
never both. Its separate network segment retains the narrow direct-Git approval.

Select the actual host first; never infer Codex solely from a missing Claude CLI.
Resolve `scripts/update_state.py` under this reference's parent Skill.
At first plugin use in EVERY new conversation run
`python3 <script> init --platform codex` or `init --platform claude`.
Claude Chat additionally uses `--surface claude-chat` and its
[manual-update adapter](hosts/claude-chat.md).
Retain the returned `context_file` in this conversation. Init generates the
UUID and snapshots the active host's bundled version. Never invent these values,
search other sessions' files, or replace the snapshot after an on-disk upgrade.

Every subsequent action uses only `--context-file <returned-path>` for identity.
Use returned `check_args` and `notice_args`; do not add session-id or loaded-release.
The helper uses a private temporary session directory and SQLite, never a shared
user-profile database or native installation inventory. New conversations check
afresh. Only `check --allow-network` may access the network; no action installs.

For the alternative low-level protocol run
`python3 <script> probe --context-file <returned-path>` once.

- `cached`: no network. A pending unshown notice can still be delivered later.
- `busy` or `silent`: continue business without any update content.
- `check_required`: retain the opaque ticket. Only if network access is already
  permitted, execute one fixed command, with a short host-enforced timeout:
  `git ls-remote -- https://github.com/2026Allin/anchises-stock-qa.git`.
  Feed its captured stdout to `python3 <script> record --context-file <returned-path> --ticket <ticket>`.
  Do not put the whole transcript in stdin. On failure, denied access or timeout,
  use `python3 <script> failed --context-file <returned-path> --ticket <ticket>` and stay silent.
  Do not prompt repeatedly for permission as part of automatic business checks.

The successful check starts a six-hour cycle. Failure backs off for 30 minutes
without changing the last success time. A first use without a success record
checks immediately. A backwards clock adjustment expires the cache safely.
Concurrent calls within this conversation share a short lease; other conversations
are isolated. Expired or superseded tickets cannot overwrite results.
If the context is lost, reinitialize at most once in the request, preserving a
known loaded-version snapshot rather than claiming newly read disk metadata was
loaded. If the snapshot no longer matches the bundled metadata, request a new
session for explicit diagnostics; silently skip automatic checks.
Storage failures degrade silently and never trigger permission escalation.
Explicit diagnostics report fixed reasons such as context_unavailable,
state_directory_unwritable or database_locked; none means “already current”.
Never reset context to evade a network failure's 30-minute backoff.

## At the end of the business answer

If the task succeeded and allows a normal prose footer, call:

`python3 <script> notice --context-file <returned-path>`

Only append a footer for these actions:

- `update_available`: “更新提示：Mining Market Research 有新版 `<target_version>`。
  需要更新时，请回复‘升级 Mining Market Research’。”
Checks compare the session-loaded version, not an installed-disk version.
After an explicitly verified native upgrade, require a new conversation and
suppress reminders for that verified installed target in this conversation;
do not mutate the loaded-version snapshot. Automatic checks do not infer reloads.

For `silent`, append nothing. Do not show checks, timestamps, failures, “no
updates”, or version content in ordinary answers without an actionable notice.
Do not invent release highlights: the refs checker does not retrieve changelogs.

Reserve only when the final answer is ready. Use `notice --locale zh-CN` for Chinese
or `notice --locale en` for English (other languages currently use the English
reminder template without changing the business answer's language).
Copy returned `footer_text` exactly,
as the final standalone paragraph (not a quotation or code block). Do not translate
or rephrase this machine-verified footer. Never call ack before sending. Legacy
ack records intent only and returns pending_confirmation, not delivery.

Native Stop checks the host final message; UserPromptSubmit/PreToolUse recover
positive evidence from the exact session transcript when its format is supported.
No receipt proves the user read the message. The two-minute lock is separate
from pending evidence. At most two reservations per six-hour cycle are allowed;
retry_exhausted is not confirmed. A native turn cannot reserve twice.

Claude web/Desktop Chat records only `attempted` notices, never confirmed delivery;
do not run review/ack or supply conversation text. The same two-attempt cycle cap
and lease bound retries. No transcript inspection or confirmation call is needed.

All no-Hook hosts, including App Code, use attempt_only. Never run review/ack
or pass conversation bodies to maintenance scripts. Review is rejected before
stdin is read on every host. Native evidence mode requires an observed PreToolUse
receipt matching the current open turn; init/surface/CLI presence is insufficient.
Hook loss cannot promote earlier attempted notices to confirmed. A later suitable
answer may make one compensating attempt after the lock expires; no repeated
reminders on refusal/error/JSON turns. Check caching and installation capability
are independent from delivery_mode. Maintenance permission denial never blocks business.
Lost context cannot guarantee deduplication: never borrow another session's file.

Do not reserve/ack for strict JSON/CSV, clarification, failed tasks, or a refusal
acknowledgement. Preserve pending eligibility for a later suitable answer.

## After a reminder

Only explicit upgrade intent routes to [Upgrade](../workflows/upgrade.md).
“不升级”, “稍后提醒”, or ignoring the reminder means no installation and no
follow-up. Do not reset the clock or write a permanent suppression preference.
Within this six-hour cycle do not remind again. At the first plugin use after
the cycle expires, check again and, if still newer, the same version may be
reminded again. No seven-day snooze and no skip-version state exist.

Explicit check-only requests bypass the automatic TTL via the upgrade workflow;
do not run the automatic probe as a second check. New mechanisms cannot execute
inside a historical session that never loaded them: install and restart once
to establish this behavior for future long-running sessions.
