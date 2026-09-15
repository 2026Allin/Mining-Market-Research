"""Local, bounded evidence for reminder delivery. Never network or install.

Host final-message evidence is not a UI/read receipt. Agent conversation review
is disabled. Keep at most two attempts per release-check cycle.
"""
import hashlib
import json
import os
from pathlib import Path
import stat

MAX_TEXT = 262144


def digest(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def footer(version, kind='update_available', manual=False, locale='zh-CN'):
    if locale == 'en':
        if kind == 'reload_required':
            return f'Mining Market Research {version}: start a new conversation to load the installed version.'
        return (f'Update: Mining Market Research {version} is available.\n' +
                ('Update the plugin manually, then start a new conversation.' if manual else
                 'To update, reply “Upgrade Mining Market Research”.'))
    if kind == 'reload_required':
        return f'Mining Market Research {version}：请新建对话以加载已安装版本。'
    return (f'更新提示：Mining Market Research 有新版 {version}。\n' +
            ('请手动更新插件，然后新建会话。' if manual else
             '需要更新时，请回复“升级 Mining Market Research”。'))


def contains_footer(text, expected):
    if not isinstance(text, str) or len(text.encode('utf-8')) > MAX_TEXT:
        return False
    # Only a standalone final footer, not quoted text, code or a mention.
    text = text.strip()
    if not text.endswith(expected):
        return False
    prefix = text[:-len(expected)]
    if prefix and not prefix.endswith('\n\n'):
        return False
    fence = None
    for line in prefix.splitlines():
        stripped = line.lstrip()
        if stripped.startswith(('```', '~~~')):
            mark = stripped[:3]
            fence = None if fence == mark else mark if fence is None else fence
    return fence is None


def attempts(state):
    return [p for p in state.get('notice_attempts', [])
            if p['cycle'] == state['check_cycle_id']]


def mode(state, *, allow_native=True):
    """A surface label or init is not evidence of a running Hook pipeline."""
    receipt = state.get('hook_event_receipts', {}).get('PreToolUse', {})
    turn = state.get('delivery_turn')
    if (allow_native and receipt.get('execution') == 'observed' and turn
            and receipt.get('turn') == turn and not state.get('delivery_turn_ended')):
        return 'evidence'
    return 'attempt_only'


def observe(state, *, ticket, text, source, now, turn=None):
    pending = next((p for p in attempts(state) if p['ticket'] == ticket), None)
    if not pending:
        return {'action': 'stale_ticket'}
    if pending.get('delivery_mode') == 'attempt_only':
        return {'action': 'confirmation_unknown', 'reason': 'attempt_only'}
    if pending['status'] == 'confirmed':
        return {'action': 'confirmed', 'evidence_source': pending['evidence_source']}
    if source not in ('host_final_message', 'host_transcript'):
        return {'action': 'invalid_evidence'}
    if not turn or pending.get('turn') != turn:
        return {'action': 'confirmation_unknown', 'reason': 'turn_unavailable'}
    if not contains_footer(text, pending['footer']):
        pending['status'] = 'unknown'
        return {'action': 'confirmation_unknown', 'reason': 'footer_not_verified'}
    pending.update(status='confirmed', evidence_source=source, confirmed_at=now)
    state['notice_shown_cycle_id'] = pending['cycle']
    state['notice_lease'] = None
    return {'action': 'confirmed', 'evidence_source': source}


def transcript_position(filename):
    """Only an exact host-provided private regular file, never a directory scan."""
    if not isinstance(filename, str) or not Path(filename).is_absolute():
        return None
    try:
        info = os.lstat(filename)
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid():
            return None
        return {'path': filename, 'offset': info.st_size, 'inode': info.st_ino}
    except OSError:
        return None


def recover(state, now):
    """Positive evidence only; unknown transcript formats never imply absence."""
    for pending in attempts(state):
        if pending['status'] == 'confirmed':
            continue
        pos = pending.get('transcript')
        if not pos or not pending.get('turn'):
            continue
        try:
            fd = os.open(pos['path'], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
            with os.fdopen(fd, 'rb') as handle:
                info = os.fstat(handle.fileno())
                if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid()
                        or info.st_ino != pos['inode'] or info.st_size < pos['offset']):
                    continue
                handle.seek(pos['offset'])
                raw = handle.read(MAX_TEXT + 1)
            if len(raw) > MAX_TEXT:
                continue
            # Codex response_item plus turn_context/event_msg; Claude end_turn
            # is accepted only with an explicit matching turn_id. Unsupported
            # versions retain unknown and use the bounded fallback.
            turn = pending['turn']
            for line in raw.splitlines():
                item = json.loads(line)
                payload = item.get('payload', {})
                if item.get('type') == 'turn_context':
                    turn = payload.get('turn_id')
                if item.get('type') == 'event_msg' and payload.get('type') == 'task_started':
                    turn = payload.get('turn_id')
                message = None
                if (item.get('type') == 'response_item' and payload.get('type') == 'message'
                        and payload.get('role') == 'assistant' and payload.get('channel') == 'final'):
                    message = ''.join(c.get('text', '') for c in payload.get('content', [])
                                      if c.get('type') in ('output_text', 'text'))
                elif item.get('type') == 'assistant':
                    msg = item.get('message', {})
                    if msg.get('stop_reason') == 'end_turn' and item.get('turn_id') == pending['turn']:
                        turn = item['turn_id']
                        message = ''.join(c.get('text', '') for c in msg.get('content', [])
                                          if c.get('type') == 'text')
                if message is not None and turn == pending['turn']:
                    result = observe(state, ticket=pending['ticket'], text=message,
                                     source='host_transcript', now=now, turn=turn)
                    if result['action'] == 'confirmed':
                        break
        except (OSError, ValueError, TypeError, AttributeError, KeyError):
            continue
