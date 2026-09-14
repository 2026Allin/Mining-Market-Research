#!/usr/bin/env python3
"""Non-blocking policy Hook. Never installs, changes arguments or grants access."""
import json
import os
from pathlib import Path
import re
import sys
import time

sys.dont_write_bytecode = True
CORE = Path(__file__).resolve().parents[1] / 'skills/mining-market-research'
sys.path.insert(0, str(CORE / 'scripts'))
import update_state as updates

# Explicit aliases only: matcher is an optimization, not the trust boundary.
TOOL = re.compile(r'^(?:mcp__mining_market_research__|mcp__plugin_mining-market-research_mining_market_research__|mining_market_research:)([a-z_]+)$')
TOOLS = {'get_connection_status', 'get_stock_schema', 'screen_stocks', 'create_csv_export',
         'resolve_company_identity', 'get_company_report', 'prepare_company_report_generation',
         'list_news_filters', 'search_news', 'get_news_article'}
TOOLS.update({'get_available_dates', 'get_available_exchanges', 'get_latest_dates',
              'get_table_schema', 'list_stock_tables', 'prepare_news_web_research',
              'run_readonly_sql', 'validate_readonly_sql'})


def server_capability(response):
    """Proposed v1 envelope, diagnostic-only until end-to-end negotiation exists."""
    if not isinstance(response, dict):
        return 'absent'
    body = response.get('structuredContent', response)
    if not isinstance(body, dict):
        return 'invalid'
    runtime = body.get('plugin_runtime')
    if runtime is None:
        return 'absent'
    if (not isinstance(runtime, dict) or type(runtime.get('schema_version')) is not int
            or runtime['schema_version'] != 1
            or runtime.get('update_check_owner') not in ('server', 'client')):
        return 'invalid'
    return 'server_unverified' if runtime['update_check_owner'] == 'server' else 'client'


def handle(event, *, platform, allow_network=False, lookup=updates.lookup_refs, now=None):
    name = event.get('tool_name', '')
    match = TOOL.fullmatch(name) if isinstance(name, str) else None
    kind = event.get('hook_event_name')
    if not match or match[1] not in TOOLS or kind not in ('PreToolUse', 'PostToolUse'):
        return {}
    metadata = updates.checker._load_metadata(updates.checker.metadata_path_for_platform(platform))
    context = updates.initialize_host_session(metadata, event.get('session_id'))
    loaded = context['loaded_release']
    metadata = {**metadata, 'version': updates.installer._base_version(loaded, platform=platform)}
    store = updates.session_context(metadata, context['session_id'], loaded)
    now = time.time() if now is None else now
    receipt = {'trigger': kind, 'owner': 'local', 'network_queries': 0,
               'notice_emitted': False, 'at': now}
    if kind == 'PostToolUse':
        receipt['server_capability'] = server_capability(event.get('tool_response'))
        with store.transaction() as state:
            state['last_hook_receipt'] = receipt
        return {}
    # Trusting a Hook is not a grant to change network policy. Opt in only when
    # the fixed lookup is permitted. Do not create a failure backoff otherwise:
    # the Skill may have a permitted direct-Git path.
    if allow_network:
        result = updates.check_request(store, metadata, now=now, allow_network=True,
                                       lookup=lookup, clock=lambda: now)
    else:
        result = {'action': 'silent', 'reason': 'network_not_authorized', 'network_queries': 0}
    receipt.update(result=result['action'], network_queries=result['network_queries'])
    if 'reason' in result:
        receipt['reason'] = result['reason']
    with store.transaction() as state:
        first = not state.get('hook_route_injected')
        state['hook_route_injected'] = True
        state['update_check_owner'] = 'local'
        state['last_hook_receipt'] = receipt
        state['last_hook_check_receipt'] = receipt
    # Pass the same context to the Skill. Do not reserve/ack a notice here:
    # injected context is not proof of user-visible delivery.
    text = 'Mining Market Research update context_file: ' + context['context_file'] + '. '
    text += 'Reuse this context for check/notice; no separate init. Hook check result: ' + result['action'] + '. '
    text += 'At prose finalization, use notice and ack only for an actual update footer. Never install without explicit plugin-upgrade consent.'
    if first:
        text += ' Read the task-matching Mining Market Research Skill. News/price impact uses the fusion workflow; reports follow the MCP report status.'
    return {'hookSpecificOutput': {'hookEventName': kind, 'additionalContext': text}}


def main():
    try:
        raw = sys.stdin.buffer.read(262145)
        if len(raw) > 262144:
            print('{}'); return
        event = json.loads(raw)
        # Native host signals precede the staged marker: the source tree has
        # both manifests and can be installed directly by either host. Codex
        # exports PLUGIN_ROOT plus the Claude compatibility variable.
        if os.environ.get('PLUGIN_ROOT'):
            platform = 'codex'
        elif os.environ.get('CLAUDE_PLUGIN_ROOT'):
            platform = 'claude'
        else:
            platform = (Path(__file__).parent / 'platform.txt').read_text().strip()
        if platform not in ('codex', 'claude') or not isinstance(event, dict):
            print('{}'); return
        result = handle(event, platform=platform,
                        allow_network=os.environ.get('MMR_HOOK_ALLOW_NETWORK') == '1')
        print(json.dumps(result))
    except Exception:
        # Automatic maintenance must not deny or alter a business call.
        print('{}')


if __name__ == '__main__':
    main()
