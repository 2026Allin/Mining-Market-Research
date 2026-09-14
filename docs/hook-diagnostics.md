# Hook dispatch diagnostics

## Authorized local network check

The PreToolUse command now sets `MMR_HOOK_ALLOW_NETWORK=1` for that process
only, following explicit authorization for the fixed repository lookup. This
does not edit global environment or host network policy. PostToolUse remains
network-free. The existing helper uses a noninteractive `git ls-remote` against
the fixed repository with a 15-second timeout, a six-hour successful-check TTL,
and failure backoff. A failed attempt is not evidence of a successful comparison.
This command opt-in must be reviewed before distribution to other users/hosts.

Context is injected on first use or when the check status/success timestamp
changes. `recorded` and its `cached` reuse count as the same successful status.
Receipts still update on every matched call. No injection acknowledges a user
notification or authorizes installation. Native network and real A/B reminder
validation remain separate from synthetic test results.

## Completed temporary native dispatch probe

The local `codex.20260914120108` probe temporarily matched `exec`, `functions.exec`,
`Bash`, `exec_command`, and the Mining Market Research namespace. Both events
invoked `dispatch.py --diagnostic-only`, without loading the update module.
The native task `01a09fd1-a8d1-71e3-a67d-e35526b8cf83` produced PreToolUse and
PostToolUse diagnostics for all five MCP calls inside code mode on 2026-09-14.
This establishes dispatch support, not successful update checks.

The normal handler is restored. The successful native trial uses
`^mcp__mining_market_research__.*` for both matchers instead of the bare server name;
task `01a09fe7-67b9-7630-8e3c-454d9809266d`: five paired Hook executions,
context creation/injection, and Skill reuse were verified. Networking was not
authorized in that trial. This matches the observed canonical tool names,
not all aliases accepted by the dispatcher. In this trial,
neither command uses `--diagnostic-only`, and PreToolUse's timeout is 20 seconds.
The optional diagnostic-only script mode remains available for explicit testing;
it is not enabled by the shipped configuration. Native network verification
is still pending. Never bypass host trust when reviewing changed definitions.

The dispatcher emits best-effort `MMR_HOOK_DIAGNOSTIC` JSON lines to stderr
and a bounded local JSONL file. stdout remains exclusively the Hook response.
This does not enable networking, change matchers/trust, install anything, or
change update ownership. These records are not an update cache.

On macOS/Linux the file is `tempfile.gettempdir()` followed by
`mining-market-research-hook-<numeric uid>.jsonl`. To print the path without
executing a Hook:

```sh
python3 -c 'import os,tempfile; from pathlib import Path; print(Path(tempfile.gettempdir()) / ("mining-market-research-hook-%s.jsonl" % os.getuid()))'
```

Records contain timestamp (Unix seconds), PID, a random per-invocation ID,
stage, allowlisted event and recognized tool name. Unknown names are redacted.
No session ID, tool inputs/results, credentials, exception messages or report
content are recorded. The file is private (0600), refuses symlinks/hard links
and unsafe ownership/permissions, and resets at 64 KiB. Nonblocking file locking
avoids waiting on concurrent writers; a busy/unavailable file can lose records.
stderr is the independent fallback. Other platforms may only get stderr.

Interpretation:

- `entered`: Python reached the diagnostic entry point, before stdin is read.
- `event_received`: input parsed as an object.
- `matcher_rejected`: the dispatcher rejected the event/tool; this is distinct
  from the host not launching the dispatcher because its matcher did not match.
- `initializing` without `context_ready`, followed by `dispatch_failed`: failure
  during dependency loading, metadata reading or context initialization.
- `context_ready` then `dispatch_failed`: failure after context creation.
- `completed`: handler returned; not proof that the host delivered additionalContext,
  checked a remote version, or displayed a notification.
- `input_invalid`, `input_too_large`, `platform_unavailable`: fixed early errors.

No records alone cannot prove no execution: interpreter startup failure, host
timeout, unavailable logging or rotation can also explain absence. Correlate
timestamps/PIDs with native host logs. Manual invocation and unit-test records
are synthetic evidence, never evidence of native dispatch. The diagnostic file
is ephemeral and can contain multiple tasks; invocation IDs are not chat IDs.

## References and decisions

- Context Mode's [run-hook.mjs](https://github.com/mksglu/context-mode/blob/main/hooks/run-hook.mjs)
  uses an outer failure boundary, deferred imports, independent error logging and
  successful exit to avoid breaking business calls. We borrow this separation,
  but log fixed stages rather than exception messages/stacks.
- Its [pretooluse.mjs](https://github.com/mksglu/context-mode/blob/main/hooks/pretooluse.mjs)
  also uses best-effort temporary markers before stdout. We do not copy its
  installation-registry or settings self-healing behavior.
- Anthropic's [hook-development guide](https://github.com/anthropics/claude-plugins-official/blob/main/plugins/plugin-dev/skills/hook-development/SKILL.md)
  recommends testing actual host execution with debug logs and avoiding sensitive
  logs. Synthetic tests below are only the first layer of validation.

Run `python3 -m unittest discover -s tests -p 'test_hook_updates.py'` from the repo.
After a separately authorized package installation, make one native business
call and correlate its diagnostic records with host logs. Do not reset update
state or grant network access just to obtain a Hook receipt.
