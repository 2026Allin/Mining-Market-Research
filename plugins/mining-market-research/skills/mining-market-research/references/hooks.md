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
Chat is not certified for native hooks; it keeps the Skill fallback. Cowork and
desktop-specific trust interfaces require separate host tests.

Automatic Hook network access is opt-in: `MMR_HOOK_ALLOW_NETWORK=1` in the
host-launched process environment, only after the user/admin permits the fixed
Git lookup. This is not a sandbox override. Without it the Hook initializes
context and injects routing guidance but performs zero network queries and does
not start a failure backoff; the Skill may use its permitted lookup path.
No Hook requests broader permissions or installs anything.

PreToolUse validates the plugin namespace and one of the eighteen known tools,
joins the exact host session, performs the due local check, and supplies the
context to the agent. PostToolUse records only whether the proposed server
capability envelope was absent, invalid, client, or server_unverified. Phase one
never accepts server ownership or forwards remote update instructions.

Run `update_state.py diagnose --context-file <this-session-context>` for the
last Hook receipt and last successful check. It performs no network query.
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
