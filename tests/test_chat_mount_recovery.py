"""Reproduce Chat's flattened, Skill-only mount without the plugin root."""
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from test_update_state import updates, ROOT


class ChatMountRecoveryTest(unittest.TestCase):
    def test_reported_bad_arguments_are_rejected_before_network(self):
        valid = '386687f2b193424a9f877db27fb9675e'
        cases = [
            (['--session-id', 'chat-20260911-gold'], 'missing_context_file'),
            (['--session-id', valid], 'missing_context_file'),
            (['--session-id', valid, '--loaded-release', '0.6.0-dev.11 claude.20260911133138'], 'missing_context_file'),
        ]
        for extra, reason in cases:
            with self.subTest(reason=reason), patch.object(sys, 'argv',
                    ['update_state.py', 'check', '--platform', 'claude', '--surface', 'claude-chat', '--allow-network', *extra]), \
                    patch.object(sys, 'stdout', new_callable=io.StringIO) as output, \
                    patch.object(updates.subprocess, 'run', side_effect=AssertionError('no network or native calls')):
                updates.main()
                self.assertEqual(json.loads(output.getvalue()),
                                 {'action': 'invalid_arguments', 'reason': reason, 'network_queries': 0})

    def test_init_generates_and_reuses_exact_context(self):
        meta = updates.checker._load_metadata(updates.checker.metadata_path_for_platform('claude'))
        with tempfile.TemporaryDirectory() as temp, patch.object(updates.tempfile, 'gettempdir', return_value=temp):
            first = updates.initialize_chat(meta)
            other = updates.initialize_chat(meta)
            self.assertNotEqual(first['context_file'], other['context_file'])
            self.assertEqual(updates.read_session_context(first['context_file'])['loaded_release'],
                             meta['version'] + '+' + meta['release_id'])
            self.assertEqual(first['network_queries'], 0)
            self.assertEqual(Path(first['context_file']).stat().st_mode & 0o777, 0o600)
            Path(first['context_file']).unlink()
            with self.assertRaisesRegex(updates.InputError, 'context_unavailable'):
                updates.read_session_context(first['context_file'])

    def test_flattened_core_mount_init_record_cached_without_plugin_root(self):
        source = ROOT / 'plugins/mining-market-research/skills/mining-market-research'
        with tempfile.TemporaryDirectory() as temp:
            mount = Path(temp) / 'skills/plugins/mining-market-research:mining-market-research'
            shutil.copytree(source, mount, ignore=shutil.ignore_patterns('__pycache__'))
            self.assertFalse((mount / '../../shared').resolve().exists())
            for host in ('claude-chat', 'claude-code', 'codex'):
                self.assertTrue((mount / f'references/hosts/{host}.md').exists())
            # Same-skill links never need the absent repository/shared root.
            import re
            for file in mount.rglob('*.md'):
                for link in re.findall(r'\]\(([^)]+)\)', file.read_text()):
                    target = link.split('#', 1)[0]
                    if target and '://' not in target:
                        resolved = (file.parent / target).resolve()
                        self.assertTrue(resolved.is_relative_to(mount.resolve()), str(resolved))
                        self.assertTrue(resolved.exists(), str(resolved))
            def run(action, *args, stdin=None):
                proc = subprocess.run([sys.executable, str(mount / 'scripts/update_state.py'), action,
                    '--platform', 'claude', '--surface', 'claude-chat', *args], input=stdin,
                    text=True, capture_output=True, check=True,
                    env={**os.environ, 'TMPDIR': temp, 'PYTHONDONTWRITEBYTECODE': '1'})
                return json.loads(proc.stdout)
            initialized = run('init')
            common = ['--context-file', initialized['context_file']]
            first = run('probe', *common)
            self.assertEqual(first['action'], 'check_required')
            refs = 'a'*40 + '\trefs/heads/main\n' + 'a'*40 + '\trefs/tags/mining-market-research/claude/v0.6.0-dev.10\n'
            self.assertEqual(run('record', *common, '--ticket', first['ticket'], stdin=refs)['action'], 'recorded')
            cached = run('check', *common)
            self.assertEqual(cached['action'], 'cached')
            self.assertEqual(cached['network_queries'], 0)
            self.assertEqual(run('notice', *common)['action'], 'silent')
