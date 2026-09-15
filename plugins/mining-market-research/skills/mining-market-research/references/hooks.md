# Native Hook installation and diagnostics

Hooks ship inside the plugin at `hooks/hooks.json`; do not copy them to global
settings, hard-code a versioned cache path, or bypass trust review. Codex loads
the default path; native PLUGIN_ROOT/CLAUDE_PLUGIN_ROOT signals select the host,
with a staged `hooks/platform.txt` marker as a fallback outside native execution.
Review/trust the hooks through the host's native controls (Codex CLI: `/hooks`).
Changed definitions may require review again. Start a new session after upgrade.
Do not equate packaged, discovered, trusted and successfully executed.

The dispatcher uses Python 3 and the existing bundled standard-library checker.
Git is needed only for a due network lookup. The dispatcher fails open on
unsupported events or storage errors. A missing Python executable fails before
the dispatcher runs; diagnose it through the host and disable the Hook or use
the Skill fallback, never silently install a runtime. Untrusted hooks are skipped
according to host policy. Claude
Chat does not run plugin hooks; it uses bounded attempt-only notices without review. Cowork and
desktop-specific trust interfaces require separate host tests.

Automatic Hook network access is opt-in: `MMR_HOOK_ALLOW_NETWORK=1` in the
host-launched process environment, only after the user/admin permits the fixed
Git lookup. This is not a sandbox override. Without it the Hook initializes
context and injects routing guidance but performs zero network queries and does
not start a failure backoff; the Skill may use its permitted lookup path.
No Hook requests broader permissions or installs anything.

SessionStart joins the exact host session and emits the shared short routing
contract, actual core path, immutable loaded release and context_file. It makes
zero network calls, never reserves a notice, reads no transcript, and does not
claim other Hook events or Skills executed. Resume/compact reuses the same context.
PreCompact only marks the route for refresh; it stores no conversation summary.
If a startup-after-compact event is unavailable, the next matching PreToolUse
reinjects routing. Both lifecycle events are fail-open and ignore subagents.

PreToolUse validates the plugin namespace and one of the eighteen known tools,
joins the exact host session, performs the due local check, and supplies the
context to the agent. PostToolUse records only whether the proposed server
capability envelope was absent, invalid, client, or server_unverified. Phase one
never accepts server ownership or forwards remote update instructions.

Stop is local-only: for an existing plugin context it verifies the pending exact
footer against last_assistant_message, bound to the current native turn. It never
blocks, continues the model, installs, or claims a UI/read receipt. Claude Code
uses that field first because transcript final-message writes can lag Stop.
UserPromptSubmit and PreToolUse recover positive transcript evidence and track
turn boundaries. Unsupported transcript formats remain unknown. No context is
created for unrelated Stop/UserPromptSubmit events. These new Hooks require
native trust review and separate Codex/Claude Code live acceptance before release.
Cowork is not certified by those tests. MessageDisplay is not required or enabled.
Claude versions without turn_id use a local UserPromptSubmit sequence; this is
not a cross-device session identity. Subagent events never confirm parent notices.

Run `update_state.py diagnose --context-file <this-session-context>` for the
last Hook receipt and last successful check. It performs no network query.
For package capabilities without initializing a session, run
`update_state.py capabilities --platform claude --surface native` (or codex).
Use `--platform claude --surface claude-chat` for no-Hook Chat. Omitted/unknown
host data stays unknown. This does not inspect effective host registration or
trust: those remain unverified even if bundled hooks match their source contract.
Diagnose separately reports each observed event and whether context output was
prepared; neither proves the model consumed it or read a Skill. Remote service
status cannot inspect local Hook registration. A missing event is unverified,
not proof of platform non-support. Check the actual enabled plugin and effective
host configuration separately; a standalone MCP connector can exist without it.
The receipt contains event/time, local owner, result, network count and capability
classification, not user prompts, tool arguments/results, credentials or report
content. It is a last-event snapshot, not a full audit log. `notice_emitted=false`
means the Hook did not display a notice; model context is not proof of delivery.
Session state uses private temporary storage, not an account-level six-hour cache.
Disabling/uninstalling the plugin leaves no global Hook registration from us.

Version headers are opt-in test artifacts until each host's plugin ingestion is
verified. `scripts/render_mcp_config.py` (plugin root) generates a separate JSON
config, preserving existing fields. Claude test ZIPs accept `--version-headers`.
The fixed `X-MMR-Update-Owner: client` declares that this phase retains local
checks. Connection-declared version does not prove which Skill an old turn loaded.
Do not manually maintain version headers or install a proxy just to inject them.

Business fusion, report selection, pagination and export remain in Skills/MCP.
Hook routing guidance is advisory, not evidence that a Skill was actually read.
Delivery mode is independent of surface: default attempt_only, including App Code.
An observed PreToolUse receipt must match the current open turn for a new native
evidence-mode notice. Init and SessionStart alone do not qualify. Agents never
submit conversation text through review; only native Hook evidence can confirm.

Hook matchers and the dispatcher share `scripts/runtime_contract.py` under the
core Skill. Maintainers run the plugin-root `scripts/sync_hook_config.py --write`
after changing aliases/events; CI, release sync and ZIP validation check parity.
Do not broaden interception to other plugins or use look-around regexes that
some native matcher engines cannot parse. Native desktop acceptance remains a
separate test from synthetic event tests.
