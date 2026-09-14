#!/usr/bin/env python3
"""Non-blocking policy Hook. Never installs, changes arguments or grants access."""
import json
import os
from pathlib import Path
import re
import sys
import time
import stat
import tempfile
import uuid

sys.dont_write_bytecode = True
CORE = Path(__file__).resolve().parents[1] / 'skills/mining-market-research'
sys.path.insert(0, str(CORE / 'scripts'))

def diagnostic_path():
    return Path(tempfile.gettempdir()) / f'mining-market-research-hook-{os.getuid()}.jsonl'


def diagnostic_writer():
    """Bounded, best-effort diagnostics independent of the update state store."""
    invocation = uuid.uuid4().hex

    def emit(stage, event=None):
        record = {'schema_version': 1, 'invocation': invocation,
                  'at': time.time(), 'pid': os.getpid(), 'stage': stage}
        if isinstance(event, dict):
            kind = event.get('hook_event_name')
            record['event'] = kind if kind in ('PreToolUse', 'PostToolUse') else 'other'
            name = event.get('tool_name')
            # Never copy arbitrary input, arguments, results or exception text.
            match = TOOL.fullmatch(name) if isinstance(name, str) else None
            record['tool'] = name if match and match[1] in TOOLS else 'unrecognized'
            if name in ('exec', 'functions.exec', 'Bash', 'exec_command'):
                record['tool'] = name
        line = json.dumps(record, separators=(',', ':')) + '\n'
        try:
            sys.stderr.write('MMR_HOOK_DIAGNOSTIC ' + line)
            sys.stderr.flush()
        except Exception:
            pass
        try:
            import fcntl
            flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND | os.O_NOFOLLOW | os.O_NONBLOCK
            fd = os.open(diagnostic_path(), flags, 0o600)
            try:
                info = os.fstat(fd)
                if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid()
                        or info.st_nlink != 1 or stat.S_IMODE(info.st_mode) != 0o600):
                    return
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                data = line.encode('utf-8')
                if os.fstat(fd).st_size + len(data) > 65536:
                    os.ftruncate(fd, 0)
                os.write(fd, data)
            finally:
                os.close(fd)
        except Exception:
            pass  # Diagnostics must never block the business tool.
    return emit

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


def handle(event, *, platform, allow_network=False, lookup=None, now=None,
           diagnostic=lambda *args: None):
    name = event.get('tool_name', '')
    match = TOOL.fullmatch(name) if isinstance(name, str) else None
    kind = event.get('hook_event_name')
    if not match or match[1] not in TOOLS or kind not in ('PreToolUse', 'PostToolUse'):
        diagnostic('matcher_rejected', event)
        return {}
    diagnostic('initializing', event)
    import update_state as updates
    lookup = updates.lookup_refs if lookup is None else lookup
    metadata = updates.checker._load_metadata(updates.checker.metadata_path_for_platform(platform))
    context = updates.initialize_host_session(metadata, event.get('session_id'))
    loaded = context['loaded_release']
    metadata = {**metadata, 'version': updates.installer._base_version(loaded, platform=platform)}
    store = updates.session_context(metadata, context['session_id'], loaded)
    diagnostic('context_ready', event)
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
        # A successful check and its cached reuse represent the same status.
        signature = [context['context_file'],
                     'success' if result['action'] in ('recorded', 'cached') else result['action'],
                     result.get('reason'), state.get('last_success_at')]
        changed = state.get('hook_context_signature') != signature
        state['hook_context_signature'] = signature
        state['hook_route_injected'] = True
        state['update_check_owner'] = 'local'
        state['last_hook_receipt'] = receipt
        state['last_hook_check_receipt'] = receipt
    if not first and not changed:
        return {}
    # Pass the same context to the Skill. Do not reserve/ack a notice here:
    # injected context is not proof of user-visible delivery.
    text = 'Mining Market Research update context_file: ' + context['context_file'] + '. '
    text += 'Reuse this context for check/notice; no separate init. Hook check result: ' + result['action'] + '. '
    text += 'At prose finalization, use notice and ack only for an actual update footer. Never install without explicit plugin-upgrade consent.'
    if first:
        text += ' Read the task-matching Mining Market Research Skill. News/price impact uses the fusion workflow; reports follow the MCP report status.'
    return {'hookSpecificOutput': {'hookEventName': kind, 'additionalContext': text}}


def main():
    diagnostic = diagnostic_writer()
    diagnostic('entered')
    stage = 'input_invalid'
    event = None
    try:
        raw = sys.stdin.buffer.read(262145)
        if len(raw) > 262144:
            diagnostic('input_too_large')
            print('{}'); return
        event = json.loads(raw)
        if not isinstance(event, dict):
            diagnostic('input_invalid')
            print('{}'); return
        diagnostic('event_received', event)
        if sys.argv[1:] == ['--diagnostic-only']:
            diagnostic('probe_completed', event)
            print('{}'); return
        stage = 'platform_unavailable'
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
            diagnostic('platform_unavailable', event)
            print('{}'); return
        stage = 'dispatch_failed'
        result = handle(event, platform=platform,
                        allow_network=os.environ.get('MMR_HOOK_ALLOW_NETWORK') == '1',
                        diagnostic=diagnostic)
        diagnostic('completed', event)
        print(json.dumps(result))
    except Exception:
        # Automatic maintenance must not deny or alter a business call.
        diagnostic(stage, event)
        print('{}')


if __name__ == '__main__':
    main()
