#!/usr/bin/env python3
"""Agent-driven six-hour release checks. No hooks or installation.

The check action optionally performs one fixed Git lookup with --allow-network.
Other actions remain network-free and accept externally captured refs.
SQLite transactions serialize short state changes across concurrent sessions.
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

SUCCESS_SECONDS = 6 * 60 * 60
FAILURE_SECONDS = 30 * 60
CHECK_LEASE_SECONDS = 60
NOTICE_LEASE_SECONDS = 120
MAX_STATE_BYTES = 65536
LOOKUP_TIMEOUT_SECONDS = 15


class InputError(ValueError):
    """Safe machine-readable parameter error; no raw user input in the reason."""


def validate_chat_inputs(session_id, loaded_release):
    try:
        parsed = uuid.UUID(hex=session_id) if isinstance(session_id, str) else None
    except ValueError:
        parsed = None
    if parsed is None or parsed.hex != session_id or parsed.version != 4:
        raise InputError('invalid_session_id')
    if not loaded_release:
        raise InputError('missing_loaded_release')
    try:
        installer._base_version(loaded_release, platform='claude')
    except ValueError as exc:
        raise InputError('invalid_loaded_release') from exc


def initialize_chat(metadata):
    if metadata['platform'] != 'claude':
        raise InputError('chat_requires_claude_platform')
    session_id = uuid.uuid4().hex
    loaded = metadata['version'] + '+' + metadata['release_id']
    store = chat_context(metadata, session_id, loaded)
    store.path.parent.mkdir(mode=0o700, parents=True, exist_ok=False)
    path = store.path.parent / 'session.json'
    value = {'schema_version': 1, 'session_id': session_id, 'loaded_release': loaded}
    with path.open('x', encoding='utf-8') as handle:
        os.chmod(path, 0o600)
        json.dump(value, handle)
    common = ['--platform', 'claude', '--surface', 'claude-chat', '--context-file', str(path)]
    return {'action': 'initialized', 'context_file': str(path), **value,
            'network_queries': 0, 'version_basis': 'session_loaded',
            'check_args': ['check', *common], 'notice_args': ['notice', *common]}


def read_chat_context(filename):
    path = Path(filename)
    root = Path(tempfile.gettempdir())
    if (not path.is_absolute() or path.name != 'session.json'
            or path.parent.parent.resolve() != root.resolve()
            or not path.parent.name.startswith('mining-market-research-chat-')
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
    if not isinstance(value, dict) or value.get('schema_version') != 1:
        raise InputError('invalid_context_file')
    validate_chat_inputs(value.get('session_id'), value.get('loaded_release'))
    if path.parent.name != 'mining-market-research-chat-' + value['session_id']:
        raise InputError('invalid_context_file')
    return value['session_id'], value['loaded_release']


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
    return {"schema_version": 3, "last_success_at": None, "last_attempt_at": None,
            "retry_after": 0, "latest_release": None, "check_cycle_id": None,
            "notice_shown_cycle_id": None, "check_lease": None, "notice_lease": None}


def default_database(platform):
    if platform == "claude" and os.environ.get("CLAUDE_PLUGIN_DATA"):
        root = Path(os.environ["CLAUDE_PLUGIN_DATA"])
        if not root.is_absolute() or root == Path(root.anchor):
            raise ValueError("invalid plugin data directory")
    elif sys.platform == "darwin":
        root = Path.home() / "Library/Application Support/MiningMarketResearch"
    elif os.name == "nt":
        root = Path(os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData/Local"))) / "MiningMarketResearch"
    else:
        root = Path(os.environ.get("XDG_STATE_HOME", str(Path.home() / ".local/state"))) / "mining-market-research"
    return root / "updates-v3.sqlite3"


def scope_key(metadata, installation_scope="user"):
    platform = metadata["platform"]
    config = os.environ.get("CODEX_HOME" if platform == "codex" else "CLAUDE_CONFIG_DIR")
    profile = Path(config).resolve() if config else Path.home() / (".codex" if platform == "codex" else ".claude")
    identity = [platform, str(profile), metadata["plugin_id"], metadata["repository"],
                metadata["git_ref"], "prerelease" if "-" in metadata["version"] else "stable",
                installation_scope]
    return hashlib.sha256(json.dumps(identity).encode()).hexdigest()


def chat_context(metadata, session_id, loaded_release):
    """Explicit session-only mode: never query a native installer or user profile."""
    if metadata['platform'] != 'claude':
        raise InputError('chat_requires_claude_platform')
    validate_chat_inputs(session_id, loaded_release)
    root = Path(tempfile.gettempdir()) / ('mining-market-research-chat-' + session_id)
    scope = hashlib.sha256(loaded_release.encode()).hexdigest()
    return StateStore(root / 'updates.sqlite3', scope)


def chat_notice(store, *, now, loaded_release):
    # Reuse only comparison/lease logic; the loaded version is not installed inventory.
    result = reserve_notice(store, now=now, loaded_release=loaded_release,
                            installed_release=loaded_release, platform='claude')
    result.pop('installed_release', None)
    if result['action'] == 'update_available':
        result.update(version_basis='session_loaded', loaded_release=loaded_release,
                      update_method='manual')
    return result


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
                if not isinstance(parsed, dict) or parsed.get("schema_version") != 3:
                    raise ValueError("unsupported state")
                state.update(parsed)
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
                     check_cycle_id=ticket, notice_lease=None)
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


def reserve_notice(store, *, now, loaded_release, installed_release, platform):
    if not installed_release:
        return {"action": "silent"}
    loaded = installer._base_version(loaded_release, platform=platform)
    installed = installer._base_version(installed_release, platform=platform)
    with store.transaction() as state:
        last = state["last_success_at"]
        if not _timestamp(last) or not 0 <= now - last < SUCCESS_SECONDS:
            return {"action": "silent"}
        if now < state["retry_after"] or state["notice_shown_cycle_id"] == state["check_cycle_id"]:
            return {"action": "silent"}
        if _live_lease(state["notice_lease"], now):
            return {"action": "silent"}
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
        return {"action": kind, "ticket": ticket, "installed_release": installed_release,
                "target_version": release["version"] if kind == "update_available" else installed,
                "install_source_matches": release.get("install_source_matches", False)}


def acknowledge(store, ticket, *, now):
    with store.transaction() as state:
        lease = state["notice_lease"]
        if (not _live_lease(lease, now) or lease.get("ticket") != ticket
                or lease.get("cycle") != state["check_cycle_id"]):
            return {"action": "stale_ticket"}
        state["notice_shown_cycle_id"] = state["check_cycle_id"]
        state["notice_lease"] = None
        return {"action": "acknowledged"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["init", "check", "probe", "record", "failed", "notice", "ack"])
    parser.add_argument("--platform", choices=["codex", "claude"], default="codex")
    parser.add_argument("--ticket")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--loaded-release")
    parser.add_argument('--surface', choices=['native', 'claude-chat'], default='native')
    parser.add_argument('--session-id')
    parser.add_argument('--context-file', help='Exact context_file returned by init; never reuse across conversations')
    parser.add_argument('--allow-network', action='store_true',
                        help='Use only when the host already permits the fixed Git lookup')
    args = parser.parse_args()
    try:
        metadata = checker._load_metadata(checker.metadata_path_for_platform(args.platform))
        chat = args.surface == 'claude-chat'
        if args.action == 'init':
            if not chat:
                raise InputError('init_requires_claude_chat')
            if args.session_id or args.loaded_release or args.context_file:
                raise InputError('init_generates_context_automatically')
            print(json.dumps(initialize_chat(metadata)))
            return
        if args.context_file:
            if not chat or args.session_id or args.loaded_release:
                raise InputError('conflicting_context_arguments')
            args.session_id, args.loaded_release = read_chat_context(args.context_file)
        if chat:
            store = chat_context(metadata, args.session_id, args.loaded_release)
            installed = None
        else:
            installed, scope = installed_identity(metadata)
            if installed is None:
                print(json.dumps({"action": "silent", "reason": "installation_unknown", "network_queries": 0}))
                return
            store = StateStore(default_database(args.platform), scope_key(metadata, scope))
        now = time.time()
        if args.action == 'check':
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
            loaded = args.loaded_release or f"{metadata['version']}+{metadata['release_id']}"
            if chat:
                result = chat_notice(store, now=now, loaded_release=loaded)
            else:
                result = reserve_notice(store, now=now, loaded_release=loaded,
                                        installed_release=installed, platform=args.platform)
        else:
            result = acknowledge(store, args.ticket, now=now)
        print(json.dumps(result))
    except InputError as exc:
        print(json.dumps({'action': 'invalid_arguments', 'reason': str(exc), 'network_queries': 0}))
    except (OSError, ValueError, TypeError, KeyError, sqlite3.Error):
        # A broken/unavailable persistent store must not block business work.
        print(json.dumps({"action": "silent", "reason": "state_unavailable"}))


if __name__ == "__main__":
    main()
