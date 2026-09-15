"""Bundled host capabilities and tool aliases; no host guessing or side effects."""
import re
import json
from pathlib import Path

CORE = Path(__file__).resolve().parents[1]
TOOL_PREFIXES = ('mcp__mining_market_research__',
                 'mcp__plugin_mining-market-research_mining_market_research__',
                 'mining_market_research:')
TOOL_PATTERN = r'^(?:' + '|'.join(re.escape(p) for p in TOOL_PREFIXES) + r')([a-z_]+)$'
TOOL = re.compile(TOOL_PATTERN)
EVENTS = ('SessionStart', 'PreToolUse', 'PostToolUse', 'UserPromptSubmit', 'PreCompact', 'Stop')


def capabilities(platform, surface):
    native = platform in ('codex', 'claude') and surface == 'native'
    chat = platform == 'claude' and surface == 'claude-chat'
    return {
        'profile': 'native-hooks' if native else 'remote-mcp-no-hooks' if chat else 'unknown',
        'configured_events': list(EVENTS) if native else [],
        'hook_execution': 'unverified' if native else 'not_expected' if chat else 'unknown',
        'skill_visibility': 'unverified', 'skill_read': 'unverified',
        'local_execution_permission': 'not_inferred',
        'version_basis': 'session_loaded', 'chat_session_isolation': 'not_inferred_from_mcp',
        'server_takeover_enabled': False,
    }


def routing_text(core=CORE):
    text = (core / 'references/runtime-routing.md').read_text(encoding='utf-8')
    if len(text.encode('utf-8')) > 4096:
        raise ValueError('routing_block_too_large')
    return text.strip()


def hook_config():
    command = 'python3 "${CLAUDE_PLUGIN_ROOT}/hooks/dispatch.py"'
    result = {}
    for event in EVENTS:
        entry = {'hooks': [{'type': 'command', 'command': command, 'timeout': 5}]}
        if event in ('PreToolUse', 'PostToolUse'):
            entry['matcher'] = TOOL_PATTERN
        if event == 'PreToolUse':
            entry['hooks'][0].update(command='MMR_HOOK_ALLOW_NETWORK=1 ' + command, timeout=20)
        result[event] = [entry]
    return {'hooks': result}


def diagnostics(platform, surface, receipts=None):
    """Local package observations, never assertions about effective host config."""
    root = CORE.parents[1]
    try:
        manifest_matches = json.loads((root / 'hooks/hooks.json').read_text()) == hook_config()
    except (OSError, ValueError):
        manifest_matches = False
    return {
        'capabilities': capabilities(platform, surface),
        'bundled_hook_config': 'matches_contract' if manifest_matches else 'missing_or_drifted',
        'bundled_dispatcher': 'present' if (root / 'hooks/dispatch.py').is_file() else 'missing',
        'effective_host_registration': 'unverified', 'host_trust': 'unverified',
        'installed_version': 'not_inspected', 'skill_read': 'unverified',
        'events': {name: (receipts or {}).get(name, {'execution': 'unverified'}) for name in EVENTS},
        'remote_service_can_inspect_local_hooks': False,
    }
