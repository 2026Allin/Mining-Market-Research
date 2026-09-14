"""All hosts use isolated temporary conversation state; no network or installation."""
import io
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

from test_update_state import updates, RELEASE


class SessionUpdateContextTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.temp_patch = patch.object(updates.tempfile, 'gettempdir', return_value=self.temp.name)
        self.temp_patch.start()
        self.addCleanup(self.temp_patch.stop)

    def cli(self, *args):
        with patch.object(sys, 'argv', ['update_state.py', *args]), \
                patch.object(sys, 'stdout', new_callable=io.StringIO) as out, \
                patch.object(updates, 'installed_identity', side_effect=AssertionError('inventory forbidden')):
            updates.main()
            return json.loads(out.getvalue())

    def test_context_only_cli_all_hosts_and_single_lookup(self):
        for platform, surface in [('codex', 'native'), ('claude', 'native'), ('claude', 'claude-chat')]:
            with self.subTest(platform=platform, surface=surface):
                init = self.cli('init', '--platform', platform, '--surface', surface)
                self.assertEqual(init['action'], 'initialized')
                self.assertEqual(init['check_args'], ['check', '--context-file', init['context_file']])
                context = ['--context-file', init['context_file']]
                # Patch the subprocess boundary, not the state/check sequence.
                def git_run(command, **kwargs):
                    self.assertEqual(command[:3], ['git', 'ls-remote', '--'])
                    refs = 'a'*40 + '\trefs/heads/main\n' + 'a'*40 + \
                           '\trefs/tags/mining-market-research/' + platform + '/v999.0.0\n'
                    kwargs['stdout'].write(refs.encode())
                    return Mock(returncode=0)
                with patch.object(updates.subprocess, 'run', side_effect=git_run) as run:
                    first = self.cli('check', *context, '--allow-network')
                    self.assertEqual(first['action'], 'recorded')
                    self.assertEqual(first['network_queries'], 1)
                    self.assertTrue(first['update_available'])
                    second = self.cli('check', *context)
                    self.assertEqual(second['action'], 'cached')
                    self.assertEqual(second['network_queries'], 0)
                    self.assertEqual(second['cycle_id'], first['cycle_id'])
                    notice = self.cli('notice', *context)
                    self.assertEqual(notice['action'], 'update_available')
                    self.assertEqual(notice['version_basis'], 'session_loaded')
                    self.assertNotIn('installed_release', notice)
                    self.assertEqual(notice['update_method'], 'manual' if surface == 'claude-chat' else 'native')
                    self.cli('ack', *context, '--ticket', notice['ticket'])
                    self.assertEqual(self.cli('notice', *context)['action'], 'silent')
                    run.assert_called_once()

    def test_context_conflicts_missing_and_symlink_rejected(self):
        init = self.cli('init', '--platform', 'codex')
        path = Path(init['context_file'])
        for extra in (['--platform', 'claude'], ['--loaded-release', init['loaded_release']],
                      ['--session-id', init['session_id']]):
            result = self.cli('check', '--context-file', str(path), *extra)
            self.assertEqual(result['reason'], 'conflicting_context_arguments')
            self.assertEqual(result['network_queries'], 0)
        content = path.read_text()
        path.unlink()
        self.assertEqual(self.cli('check', '--context-file', str(path))['reason'], 'context_unavailable')
        target = path.parent / 'other.json'
        target.write_text(content)
        path.symlink_to(target)
        self.assertEqual(self.cli('check', '--context-file', str(path))['reason'], 'invalid_context_file')

    def test_loaded_snapshot_survives_new_disk_metadata(self):
        init = self.cli('init', '--platform', 'codex')
        metadata = updates.checker._load_metadata()
        changed = {**metadata, 'version': '99.0.0', 'release_id': 'codex.20990101000000'}
        with patch.object(updates.checker, '_load_metadata', return_value=changed), \
                patch.object(updates, 'check_request', return_value={'action': 'silent', 'network_queries': 0}) as check:
            self.cli('check', '--context-file', init['context_file'])
            self.assertEqual(check.call_args.args[1]['version'], init['loaded_release'].split('+')[0])

    def test_storage_errors_keep_network_count_and_no_profile_fallback(self):
        init = self.cli('init', '--platform', 'codex')
        for error, reason in [(PermissionError('denied'), 'state_directory_unwritable'),
                              (sqlite3.OperationalError('database is locked'), 'database_locked')]:
            with patch.object(updates.StateStore, 'transaction', side_effect=error), \
                    patch.object(updates.subprocess, 'run', side_effect=AssertionError('network forbidden')):
                result = self.cli('check', '--context-file', init['context_file'], '--allow-network')
                self.assertEqual(result, {'action': 'silent', 'reason': reason, 'network_queries': 0})
        metadata = updates.checker._load_metadata()
        store = updates.session_context(metadata, init['session_id'], init['loaded_release'])
        refs = 'a'*40 + '\trefs/heads/main\n' + 'a'*40 + '\trefs/tags/' + RELEASE['tag'] + '\n'
        with patch.object(updates, 'record', side_effect=sqlite3.OperationalError('database is locked')):
            result = updates.check_request(store, metadata, now=100, allow_network=True,
                                           lookup=lambda: refs, clock=lambda: 101)
            self.assertEqual(result['reason'], 'database_locked')
            self.assertEqual(result['network_queries'], 1)

    def test_temp_creation_denied_is_classified(self):
        with patch.object(Path, 'mkdir', side_effect=PermissionError('denied')):
            result = self.cli('init', '--platform', 'codex')
            self.assertEqual(result['reason'], 'state_directory_unwritable')
            self.assertEqual(result['network_queries'], 0)
