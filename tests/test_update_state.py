"""Deterministic reminder protocol tests; no real network or native installation."""
import copy
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
import uuid
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'plugins/mining-market-research/skills/mining-market-research/scripts'
sys.dont_write_bytecode = True
sys.path.insert(0, str(SCRIPTS))
import update_state as updates

LOADED = '0.6.0-dev.11+codex.20260911103514'
NEW = '0.6.0-dev.12+codex.20260912000000'
RELEASE = dict(version='0.6.0-dev.12', tag='mining-market-research/codex/v0.6.0-dev.12',
               commit='a' * 40, install_source_matches=True)


class UpdateStateTest(unittest.TestCase):
    def chat(self, session=None):
        metadata = updates.checker._load_metadata(updates.checker.metadata_path_for_platform('claude'))
        loaded = '0.6.0-dev.11+claude.20260911100753'
        with patch.object(updates.tempfile, 'gettempdir', return_value=self.temp.name):
            return updates.chat_context(metadata, session or uuid.uuid4().hex, loaded), loaded

    def test_chat_sessions_are_isolated_and_same_session_reuses_cache(self):
        token = uuid.uuid4().hex
        store, _ = self.chat(token)
        ticket = updates.probe(store, now=100)['ticket']
        updates.record(store, ticket, now=100, release=RELEASE)
        same, _ = self.chat(token)
        other, _ = self.chat()
        self.assertEqual(updates.probe(same, now=101)['action'], 'cached')
        self.assertEqual(updates.probe(other, now=101)['action'], 'check_required')
        self.assertEqual(updates.probe(same, now=21700)['action'], 'check_required')

    def test_chat_notice_is_manual_and_never_claims_installed_identity(self):
        store, loaded = self.chat()
        ticket = updates.probe(store, now=100)['ticket']
        updates.record(store, ticket, now=100, release=RELEASE)
        notice = updates.chat_notice(store, now=101, loaded_release=loaded)
        self.assertEqual(notice['action'], 'update_available')
        self.assertEqual(notice['update_method'], 'manual')
        self.assertEqual(notice['version_basis'], 'session_loaded')
        self.assertNotIn('installed_release', notice)
        updates.acknowledge(store, notice['ticket'], now=101)
        self.assertEqual(updates.chat_notice(store, now=102, loaded_release=loaded)['action'], 'silent')

    def test_chat_does_not_downgrade_loaded_preview(self):
        store, loaded = self.chat()
        ticket = updates.probe(store, now=100)['ticket']
        updates.record(store, ticket, now=100, release={**RELEASE, 'version': '0.6.0-dev.10'})
        self.assertEqual(updates.chat_notice(store, now=101, loaded_release=loaded)['action'], 'silent')

    def test_chat_cli_never_calls_native_inventory(self):
        with patch.object(updates.tempfile, 'gettempdir', return_value=self.temp.name):
            meta = updates.checker._load_metadata(updates.checker.metadata_path_for_platform('claude'))
            context = updates.initialize_chat(meta)
        args = ['update_state.py', 'probe', '--context-file', context['context_file']]
        with patch.object(sys, 'argv', args), patch.object(updates.tempfile, 'gettempdir', return_value=self.temp.name), \
                patch.object(updates, 'installed_identity', side_effect=AssertionError('native call')), \
                patch.object(sys, 'stdout', new_callable=io.StringIO) as stdout:
            updates.main()
            self.assertEqual(json.loads(stdout.getvalue())['action'], 'check_required')

    def test_chat_requires_explicit_valid_session_and_loaded_version(self):
        metadata = updates.checker._load_metadata(updates.checker.metadata_path_for_platform('claude'))
        for token in (None, '', '../bad', 'a' * 32):
            with self.subTest(token=token), self.assertRaises(ValueError):
                updates.chat_context(metadata, token, '0.6.0-dev.11+claude.20260911100753')
        with self.assertRaises(ValueError):
            updates.chat_context(metadata, uuid.uuid4().hex, None)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = updates.StateStore(Path(self.temp.name) / 'updates.sqlite3', 'test')
        self.metadata = updates.checker._load_metadata()

    def success(self, now=100, release=None):
        probe = updates.probe(self.store, now=now)
        self.assertEqual(probe['action'], 'check_required')
        updates.record(self.store, probe['ticket'], now=now, release=release or RELEASE)

    def notice(self, now=101, installed=LOADED, loaded=LOADED):
        return updates.reserve_notice(self.store, now=now, loaded_release=loaded,
                                      installed_release=installed, platform='codex')

    def test_first_use_and_exact_six_hour_boundary(self):
        self.success()
        self.assertEqual(updates.probe(self.store, now=21699)['action'], 'cached')
        self.assertEqual(updates.probe(self.store, now=21700)['action'], 'check_required')

    def test_codex_dev13_to_dev14_end_to_end_offline(self):
        """Synthetic remote refs; no publication, install, or real network."""
        loaded = '0.6.0-dev.13+codex.20260914074807'
        newer = '0.6.0-dev.14+codex.20260915000000'
        refs = ('a' * 40 + '\trefs/heads/main\n' + 'a' * 40 +
                '\trefs/tags/' + self.metadata['tag_prefix'] + '0.6.0-dev.14\n')
        with patch.object(updates, 'lookup_refs', return_value=refs) as lookup:
            def check(now):
                return updates.check_request(self.store, self.metadata, now=now,
                    allow_network=True, lookup=lookup, clock=lambda: now)
            self.assertEqual(check(100)['action'], 'recorded')
            notice = self.notice(101, installed=loaded, loaded=loaded)
            self.assertEqual(notice['action'], 'update_available')
            # Without Hooks, bounded attempts never claim display confirmation.
            self.assertEqual(notice['delivery_mode'], 'attempt_only')
            self.notice(222, installed=loaded, loaded=loaded)
            self.assertEqual(check(21699)['network_queries'], 0)
            self.assertEqual(self.notice(21699, installed=loaded, loaded=loaded)['action'], 'silent')
            self.assertEqual(check(21700)['action'], 'recorded')
            self.assertEqual(self.notice(21701, installed=loaded, loaded=loaded)['action'], 'update_available')
            self.assertEqual(lookup.call_count, 2)
            self.assertEqual(self.notice(22000, installed=newer, loaded=loaded)['action'], 'reload_required')
            self.assertEqual(self.notice(22200, installed=newer, loaded=newer)['action'], 'silent')

    def test_decline_or_ignore_does_not_suppress_next_cycle(self):
        for response in ('decline', 'ignore'):
            with self.subTest(response=response):
                start = 100 if response == 'decline' else 50000
                self.success(start)
                notice = self.notice(start + 1)
                self.assertEqual(notice['action'], 'update_available')
                updates.acknowledge(self.store, notice['ticket'], now=start + 1)
                self.assertEqual(self.notice(start + 2)['action'], 'silent')
                with self.store.transaction() as state:
                    self.assertEqual(state['last_success_at'], start)
                    self.assertNotIn('ignored_version', state)
                self.success(start + 21600)
                self.assertEqual(self.notice(start + 21601)['action'], 'update_available')

    def test_current_is_silent(self):
        self.success(release={**RELEASE, 'version': '0.6.0-dev.11'})
        self.assertEqual(self.notice()['action'], 'silent')

    def test_failure_backoff_does_not_change_success(self):
        self.success()
        ticket = updates.probe(self.store, now=21700)['ticket']
        updates.record(self.store, ticket, now=21701)
        with self.store.transaction() as state:
            self.assertEqual(state['last_success_at'], 100)
        self.assertEqual(updates.probe(self.store, now=23500)['action'], 'silent')
        self.assertEqual(updates.probe(self.store, now=23501)['action'], 'check_required')
        self.assertEqual(self.notice(21702)['action'], 'silent')

    def test_force_bypasses_cache_and_failure_backoff(self):
        self.success()
        probe = updates.probe(self.store, now=101, force=True)
        updates.record(self.store, probe['ticket'], now=102)
        self.assertEqual(updates.probe(self.store, now=103, force=True)['action'], 'check_required')

    def test_concurrent_check_and_stale_result(self):
        first = updates.probe(self.store, now=100)
        other = updates.StateStore(self.store.path, 'test')
        self.assertEqual(updates.probe(other, now=101)['action'], 'busy')
        second = updates.probe(other, now=160)
        self.assertEqual(updates.record(self.store, first['ticket'], now=161, release=RELEASE)['action'], 'stale_ticket')
        self.assertEqual(updates.record(other, second['ticket'], now=161, release=RELEASE)['action'], 'recorded')

    def test_interrupted_notice_retries_after_lease(self):
        self.success()
        first = self.notice(101)
        self.assertEqual(self.notice(102)['action'], 'silent')
        next_notice = self.notice(221)
        self.assertEqual(next_notice['action'], 'update_available')
        self.assertEqual(updates.acknowledge(self.store, first['ticket'], now=222)['action'], 'pending_confirmation')
        self.assertEqual(updates.review_notice(self.store, next_notice['ticket'], next_notice['footer_text'], now=222)['reason'], 'conversation_review_disabled')

    def test_disk_upgrade_requires_reload_not_reinstall(self):
        self.success()
        self.assertEqual(self.notice(installed=NEW)['action'], 'reload_required')

    def test_current_session_and_disk_same_is_silent(self):
        self.success()
        self.assertEqual(self.notice(installed=NEW, loaded=NEW)['action'], 'silent')

    def test_disk_older_build_is_not_called_updated(self):
        self.success(release={**RELEASE, 'version': '0.6.0-dev.11'})
        self.assertEqual(self.notice(installed=LOADED.replace('103514', '100000'))['action'], 'silent')

    def test_clock_moves_backwards(self):
        self.success()
        self.assertEqual(updates.probe(self.store, now=99)['action'], 'check_required')

    def test_profiles_scopes_channels_and_hosts_are_separate(self):
        with patch.object(updates.tempfile, 'gettempdir', return_value=self.temp.name):
            for platform in ('codex', 'claude'):
                meta = updates.checker._load_metadata(updates.checker.metadata_path_for_platform(platform))
                first = updates.initialize_session(meta)
                other = updates.initialize_session(meta)
                self.assertNotEqual(first['context_file'], other['context_file'])
                store = updates.session_context(meta, first['session_id'], first['loaded_release'])
                ticket = updates.probe(store, now=100)['ticket']
                updates.record(store, ticket, now=100, release=RELEASE)
                self.assertEqual(updates.probe(store, now=101)['action'], 'cached')
                separate = updates.session_context(meta, other['session_id'], other['loaded_release'])
                self.assertEqual(updates.probe(separate, now=101)['action'], 'check_required')

    def test_tag_discovery_survives_main_advancing_but_marks_unsafe_install(self):
        refs = f"{'b'*40}\trefs/heads/main\n{'a'*40}\trefs/tags/{RELEASE['tag']}\n"
        self.assertFalse(updates.parse_release(refs, self.metadata)['install_source_matches'])

    def test_missing_malformed_and_oversized_refs_are_not_success(self):
        for refs in ('', 'bad refs', f"{'b'*40}\trefs/heads/main\n", 'x' * 1048577):
            with self.subTest(size=len(refs)), self.assertRaises(ValueError):
                updates.parse_release(refs, self.metadata)

    def test_stable_channel_does_not_recommend_prerelease(self):
        refs = f"{'a'*40}\trefs/heads/main\n{'a'*40}\trefs/tags/{RELEASE['tag']}\n"
        with self.assertRaises(ValueError):
            updates.parse_release(refs, {**self.metadata, 'version': '0.6.0'})

    def test_unknown_inventory_is_not_assumed_current(self):
        with patch.object(updates.subprocess, 'run', side_effect=FileNotFoundError):
            self.assertEqual(updates.installed_identity(self.metadata), (None, 'unknown'))

    def test_symlink_store_rejected(self):
        link = Path(self.temp.name) / 'link'
        link.symlink_to(self.store.path)
        with self.assertRaises(ValueError):
            updates.probe(updates.StateStore(link, 'test'), now=100)

    def test_upgrade_wrapper_is_shared_and_requires_restart(self):
        plugin = ROOT / 'plugins/mining-market-research'
        for host in ('codex', 'claude'):
            manifest = json.loads((plugin / f'.{host}-plugin/plugin.json').read_text())
            self.assertEqual(manifest['skills'], './skills/')
        workflow = (SCRIPTS.parent / 'workflows/upgrade.md').read_text()
        self.assertIn('restart the session', workflow)
        self.assertIn('check-only', workflow)
        self.assertIn('without running the updater', workflow)
        self.assertTrue((plugin / 'hooks/hooks.json').is_file())


if __name__ == '__main__':
    unittest.main()
