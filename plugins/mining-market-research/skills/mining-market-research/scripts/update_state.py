#!/usr/bin/env python3
"""Shared agent/Hook six-hour release checks. No installation.

The check action optionally performs one fixed Git lookup with --allow-network.
Other actions remain network-free and accept externally captured refs.
SQLite transactions serialize short state changes within one conversation.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import json
import math
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import time
import tempfile
import uuid

sys.dont_write_bytecode = True
import check_plugin_update as checker
import update_installed_plugin as installer
import notice_delivery as delivery
import runtime_contract as runtime

SUCCESS_SECONDS = 6 * 60 * 60
FAILURE_SECONDS = 30 * 60
CHECK_LEASE_SECONDS = 60
NOTICE_LEASE_SECONDS = 120
MAX_STATE_BYTES = 65536
LOOKUP_TIMEOUT_SECONDS = 15


class InputError(ValueError):
    """Safe machine-readable parameter error; no raw user input in the reason."""


def validate_chat_inputs(session_id, loaded_release, platform='claude'):
    try:
        parsed = uuid.UUID(hex=session_id) if isinstance(session_id, str) else None
    except ValueError:
        parsed = None
    if parsed is None or parsed.hex != session_id or parsed.version != 4:
        raise InputError('invalid_session_id')
    if not loaded_release:
        raise InputError('missing_loaded_release')
    try:
        installer._base_version(loaded_release, platform=platform)
    except ValueError as exc:
        raise InputError('invalid_loaded_release') from exc


def initialize_session(metadata, surface='native'):
    if surface == 'claude-chat' and metadata['platform'] != 'claude':
        raise InputError('chat_requires_claude_platform')
    session_id = uuid.uuid4().hex
    loaded = metadata['version'] + '+' + metadata['release_id']
    store = session_context(metadata, session_id, loaded)
    store.path.parent.mkdir(mode=0o700, parents=True, exist_ok=False)
    path = store.path.parent / 'session.json'
    value = {'schema_version': 2, 'platform': metadata['platform'], 'surface': surface,
             'session_id': session_id, 'loaded_release': loaded}
    with path.open('x', encoding='utf-8') as handle:
        os.chmod(path, 0o600)
        json.dump(value, handle)
    common = ['--context-file', str(path)]
    return {'action': 'initialized', 'context_file': str(path), **value,
            'network_queries': 0, 'version_basis': 'session_loaded',
            'check_args': ['check', *common], 'notice_args': ['notice', *common]}


def initialize_chat(metadata):
    return initialize_session(metadata, 'claude-chat')


def initialize_host_session(metadata, host_session_id, *, existing_only=False):
    """Join only an exact host-provided session; never scan other sessions.

    A deterministic, private slot serializes Hook/Skill initialization. The
    public context still contains a generated UUID4 and immutable snapshot.
    """
    if (not isinstance(host_session_id, str) or not host_session_id
            or len(host_session_id) > 256 or any(ord(c) < 32 for c in host_session_id)):
        raise InputError('invalid_host_session_id')
    key = hashlib.sha256((str(os.getuid()) + ':' + metadata['platform'] + ':' + host_session_id).encode()).hexdigest()
    root = Path(tempfile.gettempdir()) / ('mining-market-research-host-' + key)
    if existing_only and not (root / 'index.sqlite3').is_file():
        return None
    root.mkdir(mode=0o700, exist_ok=True)
    if root.is_symlink() or root.stat().st_uid != os.getuid() or root.stat().st_mode & 0o077:
        raise InputError('unsafe_host_state_directory')
    index = StateStore(root / 'index.sqlite3', 'context')
    with index.transaction() as state:
        filename = state.get('context_file')
        if filename:
            value = read_session_context(filename)
            return {'action': 'initialized', 'context_file': filename, **value,
                    'network_queries': 0, 'check_args': ['check', '--context-file', filename],
                    'notice_args': ['notice', '--context-file', filename]}
        if existing_only:
            return None
        result = initialize_session(metadata)
        state['context_file'] = result['context_file']
        return result


def read_session_context(filename):
    path = Path(filename)
    root = Path(tempfile.gettempdir())
    if (not path.is_absolute() or path.name != 'session.json'
            or path.parent.parent.resolve() != root.resolve()
            or not path.parent.name.startswith('mining-market-research-session-')
            or path.is_symlink() or path.parent.is_symlink()):
        raise InputError('invalid_context_file')
    try:
        with path.open('rb') as handle:
            raw = handle.read(MAX_STATE_BYTES + 1)
        if len(raw) > MAX_STATE_BYTES:
            raise InputError('invalid_context_file')
        value = json.loads(raw)
    except (OSError, ValueError) as exc:
        raise InputError('context_unavailable') from exc
    if (not isinstance(value, dict) or value.get('schema_version') != 2
            or value.get('platform') not in {'codex', 'claude'}
            or value.get('surface') not in {'native', 'claude-chat'}
            or value['surface'] == 'claude-chat' and value['platform'] != 'claude'):
        raise InputError('invalid_context_file')
    validate_chat_inputs(value.get('session_id'), value.get('loaded_release'), value['platform'])
    if path.parent.name != 'mining-market-research-session-' + value['session_id']:
        raise InputError('invalid_context_file')
    return value


def lookup_refs():
    """Fixed, noninteractive lookup. No remote-supplied command or URL."""
    with tempfile.TemporaryFile() as output:
        result = subprocess.run(
            ['git', 'ls-remote', '--', 'https://github.com/2026Allin/anchises-stock-qa.git'],
            stdout=output, stderr=subprocess.DEVNULL, timeout=LOOKUP_TIMEOUT_SECONDS,
            env={**os.environ, 'GIT_TERMINAL_PROMPT': '0', 'GCM_INTERACTIVE': 'never'},
            check=False)
        output.seek(0)
        raw = output.read(checker.MAX_REMOTE_OUTPUT_BYTES + 1)
        if result.returncode or len(raw) > checker.MAX_REMOTE_OUTPUT_BYTES:
            raise ValueError('lookup failed')
        return raw.decode('utf-8')


def check_request(store, metadata, *, now, allow_network=False, force=False,
                  lookup=lookup_refs, clock=time.time):
    """One probe per request; at most one lookup and record. Never installs."""
    counter = [0]
    try:
        def counted_lookup():
            counter[0] += 1
            return lookup()
        result = _check_request(store, metadata, now=now, allow_network=allow_network,
                                force=force, lookup=counted_lookup, clock=clock)
        if result['action'] in {'cached', 'recorded'}:
            with store.transaction() as state:
                release = state['latest_release']
                result.update(version_basis='session_loaded',
                              latest_version=release['version'],
                              update_available=checker.compare_versions(release['version'], metadata['version']) > 0)
        return result
    except (OSError, ValueError, TypeError, KeyError, sqlite3.Error) as exc:
        return failure_result(exc, counter[0])


def _check_request(store, metadata, *, now, allow_network, force, lookup, clock):
    result = probe(store, now=now, force=force)
    if result['action'] != 'check_required':
        return {**result, 'network_queries': 0}
    ticket = result['ticket']
    if not allow_network:
        # Permission is owned by the host. Do not ask from a business check.
        record(store, ticket, now=now)
        return {'action': 'silent', 'reason': 'network_not_authorized', 'network_queries': 0}
    try:
        release = parse_release(lookup(), metadata)
    except (OSError, ValueError, subprocess.TimeoutExpired):
        record(store, ticket, now=clock())
        return {'action': 'silent', 'reason': 'lookup_failed', 'network_queries': 1}
    result = record(store, ticket, now=clock(), release=release)
    return {**result, 'network_queries': 1}


def empty_state():
    return {"schema_version": 4, "last_success_at": None, "last_attempt_at": None,
            "retry_after": 0, "latest_release": None, "check_cycle_id": None,
            "notice_shown_cycle_id": None, "check_lease": None, "notice_lease": None,
            "notice_attempts": [], "delivery_turn": None, "delivery_turn_ended": False}


def session_context(metadata, session_id, loaded_release):
    """Explicit session-only mode: never query a native installer or user profile."""
    validate_chat_inputs(session_id, loaded_release, metadata['platform'])
    root = Path(tempfile.gettempdir()) / ('mining-market-research-session-' + session_id)
    scope = hashlib.sha256((metadata['platform'] + ':' + loaded_release).encode()).hexdigest()
    return StateStore(root / 'updates.sqlite3', scope)


def chat_context(metadata, session_id, loaded_release):
    if metadata['platform'] != 'claude':
        raise InputError('chat_requires_claude_platform')
    return session_context(metadata, session_id, loaded_release)


def session_notice(store, *, now, loaded_release, platform, surface='native', locale='zh-CN'):
    # Reuse only comparison/lease logic; the loaded version is not installed inventory.
    result = reserve_notice(store, now=now, loaded_release=loaded_release,
                            installed_release=loaded_release, platform=platform,
                            manual=surface == 'claude-chat', locale=locale)
    result.pop('installed_release', None)
    if result['action'] == 'update_available':
        result.update(version_basis='session_loaded', loaded_release=loaded_release,
                      update_method='manual' if surface == 'claude-chat' else 'resolve_on_upgrade')
    return result


def chat_notice(store, *, now, loaded_release):
    return session_notice(store, now=now, loaded_release=loaded_release,
                          platform='claude', surface='claude-chat')


def failure_result(exc, network_queries=0):
    if isinstance(exc, sqlite3.OperationalError) and ('locked' in str(exc) or 'busy' in str(exc)):
        reason = 'database_locked'
    elif isinstance(exc, PermissionError):
        reason = 'state_directory_unwritable'
    elif isinstance(exc, sqlite3.DatabaseError):
        reason = 'database_unavailable'
    elif isinstance(exc, OSError):
        reason = 'state_io_error'
    else:
        reason = 'state_invalid'
    return {'action': 'silent', 'reason': reason, 'network_queries': network_queries}


class StateStore:
    def __init__(self, path, scope):
        self.path, self.scope = Path(path), scope

    @contextmanager
    def transaction(self):
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        if self.path.is_symlink():
            raise ValueError("state database must not be a symlink")
        fd = os.open(self.path, os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0), 0o600)
        os.close(fd)
        connection = sqlite3.connect(self.path, timeout=0.2)
        try:
            connection.execute("CREATE TABLE IF NOT EXISTS state (scope TEXT PRIMARY KEY, body TEXT NOT NULL)")
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute("SELECT body FROM state WHERE scope=?", (self.scope,)).fetchone()
            state = empty_state()
            if row:
                if len(row[0]) > MAX_STATE_BYTES:
                    raise ValueError("oversized state")
                parsed = json.loads(row[0])
                if not isinstance(parsed, dict) or parsed.get("schema_version") not in (3, 4):
                    raise ValueError("unsupported state")
                state.update(parsed)
                if parsed['schema_version'] == 3:
                    # Legacy ack is not evidence. Preserve old suppression only
                    # as an exhausted retry budget, never invent confirmation.
                    state['legacy_suppressed_cycle'] = parsed.get('notice_shown_cycle_id')
                    state['notice_shown_cycle_id'] = None
                    state['notice_lease'] = None
                state['schema_version'] = 4
            yield state
            connection.execute("INSERT OR REPLACE INTO state VALUES (?, ?)",
                               (self.scope, json.dumps(state, allow_nan=False)))
            connection.commit()
        finally:
            connection.close()


def _timestamp(value):
    return isinstance(value, (float, int)) and not isinstance(value, bool) and math.isfinite(value)


def _live_lease(lease, now):
    return isinstance(lease, dict) and _timestamp(lease.get("until")) and now < lease["until"]


def probe(store, *, now, force=False):
    with store.transaction() as state:
        if (_timestamp(state["last_attempt_at"]) and now < state["last_attempt_at"]
                or _timestamp(state["last_success_at"]) and now < state["last_success_at"]):
            state.update(check_lease=None, notice_lease=None, retry_after=0)
        if _live_lease(state["check_lease"], now):
            return {"action": "busy"}
        last = state["last_success_at"]
        if not force:
            if _timestamp(state["retry_after"]) and now < state["retry_after"]:
                return {"action": "silent"}
            if _timestamp(last) and 0 <= now - last < SUCCESS_SECONDS:
                return {"action": "cached", "cycle_id": state["check_cycle_id"]}
        ticket = uuid.uuid4().hex
        state["last_attempt_at"] = now
        state["check_lease"] = {"ticket": ticket, "until": now + CHECK_LEASE_SECONDS}
        return {"action": "check_required", "ticket": ticket}


def parse_release(refs, metadata):
    if not refs.strip() or len(refs.encode()) > checker.MAX_REMOTE_OUTPUT_BYTES:
        raise ValueError("invalid refs")
    branch, _, tags = checker._parse_remote_refs(
        refs, branch_ref=f"refs/heads/{metadata['git_ref']}", tag_prefix=metadata["tag_prefix"])
    # Stable installations do not automatically recommend development releases.
    if "-" not in metadata["version"]:
        tags = [tag for tag in tags if "-" not in tag[0]]
    latest = checker._latest_tag(tags)
    if latest is None:
        raise ValueError("no published release found")
    return {"version": latest[0], "tag": latest[1], "commit": latest[2],
            "install_source_matches": latest[2] == branch}


def record(store, ticket, *, now, release=None):
    with store.transaction() as state:
        lease = state["check_lease"]
        if not _live_lease(lease, now) or lease.get("ticket") != ticket:
            return {"action": "stale_ticket"}
        state["check_lease"] = None
        if release is None:
            state["retry_after"] = now + FAILURE_SECONDS
            return {"action": "silent"}
        state.update(last_success_at=now, retry_after=0, latest_release=release,
                     check_cycle_id=ticket, notice_lease=None, notice_attempts=[])
        return {"action": "recorded", "cycle_id": ticket}


def installed_identity(metadata):
    """Read-only native inventory, with no fallback to stale bundled metadata."""
    platform = metadata["platform"]
    try:
        result = subprocess.run([platform, "plugin", "list", "--json"],
                                capture_output=True, text=True, timeout=3, check=False)
        if result.returncode or len(result.stdout) > checker.MAX_REMOTE_OUTPUT_BYTES:
            return None, "unknown"
        item = installer._installed_plugin(json.loads(result.stdout), metadata["plugin_id"], platform=platform)
        if not item or not installer._installed_and_enabled(item, platform=platform):
            return None, "unknown"
        installer._base_version(item.get("version"), platform=platform)
        scope = item.get("scope", "user")
        if not isinstance(scope, str) or scope not in {"user", "project", "local"}:
            return None, "unknown"
        if scope != "user":
            scope += ":" + str(Path(item.get("projectPath") or os.getcwd()).resolve())
        return item["version"], scope
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return None, "unknown"


def reserve_notice(store, *, now, loaded_release, installed_release, platform, manual=False, locale='zh-CN'):
    if not installed_release:
        return {"action": "silent"}
    loaded = installer._base_version(loaded_release, platform=platform)
    installed = installer._base_version(installed_release, platform=platform)
    with store.transaction() as state:
        evidence = delivery.mode(state, allow_native=not manual) == 'evidence'
        if evidence:
            delivery.recover(state, now)
        last = state["last_success_at"]
        if not _timestamp(last) or not 0 <= now - last < SUCCESS_SECONDS:
            return {"action": "silent"}
        if now < state["retry_after"] or state["notice_shown_cycle_id"] == state["check_cycle_id"]:
            return {"action": "silent"}
        if _live_lease(state["notice_lease"], now):
            return {"action": "silent"}
        pending = delivery.attempts(state)
        if (len(pending) >= 2 or state.get('legacy_suppressed_cycle') == state['check_cycle_id']):
            return {'action': 'silent', 'reason': 'retry_exhausted'}
        if evidence and pending and pending[-1].get('turn') == state['delivery_turn']:
            return {'action': 'silent', 'reason': 'awaiting_turn_completion'}
        release = state["latest_release"]
        if release and checker.compare_versions(release["version"], installed) > 0:
            kind = "update_available"
        elif (checker.compare_versions(installed, loaded) > 0 or
              installed == loaded and installed_release > loaded_release):
            kind = "reload_required"
        else:
            return {"action": "silent"}
        ticket = uuid.uuid4().hex
        state["notice_lease"] = {"ticket": ticket, "until": now + NOTICE_LEASE_SECONDS,
                                 "cycle": state["check_cycle_id"]}
        target = release['version'] if kind == 'update_available' else installed
        text = delivery.footer(target, kind, manual, locale)
        state['notice_attempts'] = pending + [{
            'ticket': ticket, 'cycle': state['check_cycle_id'], 'target_version': target,
            'turn': state.get('delivery_turn') if evidence else None, 'created_at': now,
            'status': 'pending' if evidence else 'attempted',
            'delivery_mode': 'evidence' if evidence else 'attempt_only',
            'footer': text, 'footer_sha256': delivery.digest(text),
            'transcript': state.get('delivery_transcript') if evidence else None, 'evidence_source': None}]
        return {"action": kind, "ticket": ticket, "installed_release": installed_release,
                "footer_text": text, "delivery_status": "pending" if evidence else "attempted",
                "delivery_mode": 'evidence' if evidence else 'attempt_only',
                "target_version": release["version"] if kind == "update_available" else installed,
                "install_source_matches": release.get("install_source_matches", False)}


def acknowledge(store, ticket, *, now):
    """Compatibility: old pre-send ack can only record intent, never delivery."""
    with store.transaction() as state:
        pending = next((p for p in delivery.attempts(state) if p['ticket'] == ticket), None)
        if pending is None:
            return {"action": "stale_ticket"}
        pending['intent_recorded_at'] = now
        return {"action": "pending_confirmation"}


def review_notice(store, ticket, text, *, now):
    """Compatibility rejection; never process or persist conversation input."""
    return {'action': 'invalid_arguments', 'reason': 'conversation_review_disabled'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["init", "check", "probe", "record", "failed", "notice", "ack", "review", "diagnose", "capabilities"])
    parser.add_argument("--platform", choices=["codex", "claude"])
    parser.add_argument("--ticket")
    parser.add_argument('--locale', choices=['zh-CN', 'en'], default='zh-CN', help='Exact reminder template language')
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--loaded-release")
    parser.add_argument('--surface', choices=['native', 'claude-chat'])
    parser.add_argument('--session-id')
    parser.add_argument('--context-file', help='Exact context_file returned by init; never reuse across conversations')
    parser.add_argument('--host-session-id', help='Exact native host session ID; joins the Hook context, never invent one')
    parser.add_argument('--allow-network', action='store_true',
                        help='Use only when the host already permits the fixed Git lookup')
    args = parser.parse_args()
    try:
        if args.action == 'review':
            raise InputError('conversation_review_disabled')
        if args.action == 'capabilities':
            if args.context_file or args.session_id or args.host_session_id or args.loaded_release:
                raise InputError('capabilities_requires_host_not_session')
            print(json.dumps({'action': 'capabilities', 'network_queries': 0,
                **runtime.diagnostics(args.platform, args.surface)}))
            return
        if args.action == 'init':
            if args.session_id or args.loaded_release or args.context_file:
                raise InputError('init_generates_context_automatically')
            metadata = checker._load_metadata(checker.metadata_path_for_platform(args.platform or 'codex'))
            if args.host_session_id:
                if args.surface == 'claude-chat':
                    raise InputError('host_session_requires_native')
                result = initialize_host_session(metadata, args.host_session_id)
            else:
                result = initialize_session(metadata, args.surface or 'native')
            print(json.dumps(result))
            return
        if args.host_session_id:
            raise InputError('host_session_only_for_init')
        if not args.context_file:
            raise InputError('missing_context_file')
        if args.session_id or args.loaded_release:
            raise InputError('conflicting_context_arguments')
        context = read_session_context(args.context_file)
        if (args.platform and args.platform != context['platform']
                or args.surface and args.surface != context['surface']):
            raise InputError('conflicting_context_arguments')
        args.platform, args.surface = context['platform'], context['surface']
        if args.surface == 'claude-chat' and args.action in {'review', 'ack'}:
            # Reject before reading stdin or opening the state database.
            raise InputError('chat_delivery_confirmation_disabled')
        args.loaded_release = context['loaded_release']
        metadata = checker._load_metadata(checker.metadata_path_for_platform(args.platform))
        # Channel selection must remain based on this session, even after a disk upgrade.
        metadata = {**metadata, 'version': installer._base_version(args.loaded_release, platform=args.platform)}
        store = session_context(metadata, context['session_id'], args.loaded_release)
        now = time.time()
        if args.action == 'diagnose':
            with store.transaction() as state:
                result = {'action': 'diagnostics', 'owner': state.get('update_check_owner', 'local'),
                          'runtime': runtime.diagnostics(args.platform, args.surface, state.get('hook_event_receipts')),
                          'delivery_mode': delivery.mode(state, allow_native=args.surface != 'claude-chat'),
                          'last_hook_receipt': state.get('last_hook_receipt'),
                          'last_hook_check_receipt': state.get('last_hook_check_receipt'),
                          'last_delivery_receipt': state.get('last_delivery_receipt'),
                          'last_success_at': state['last_success_at'], 'network_queries': 0,
                          'notice_attempts': [{k: p.get(k) for k in ('ticket', 'cycle', 'target_version', 'status', 'evidence_source')}
                                              for p in delivery.attempts(state)],
                          'hook_trust': 'not_observable', 'server_takeover_enabled': False}
        elif args.action == 'check':
            result = check_request(store, metadata, now=now, allow_network=args.allow_network,
                                   force=args.force)
        elif args.action == "probe":
            result = probe(store, now=now, force=args.force)
        elif args.action in {"record", "failed"}:
            release = None
            if args.action == "record":
                raw = sys.stdin.buffer.read(checker.MAX_REMOTE_OUTPUT_BYTES + 1)
                try:
                    release = parse_release(raw.decode("utf-8"), metadata)
                except (ValueError, UnicodeError):
                    pass
            result = record(store, args.ticket, now=now, release=release)
        elif args.action == "notice":
            result = session_notice(store, now=now, loaded_release=args.loaded_release,
                                    platform=args.platform, surface=args.surface, locale=args.locale)
        else:
            result = acknowledge(store, args.ticket, now=now)
        print(json.dumps(result))
    except InputError as exc:
        print(json.dumps({'action': 'invalid_arguments', 'reason': str(exc), 'network_queries': 0}))
    except (OSError, ValueError, TypeError, KeyError, sqlite3.Error) as exc:
        print(json.dumps(failure_result(exc)))


if __name__ == "__main__":
    main()
