import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import Mock, patch
import zipfile

from test_update_state import updates, RELEASE

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'plugins/mining-market-research/scripts'


def load(name):
    import sys
    sys.path.insert(0, str(SCRIPTS))
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class UpdateOptimizationTest(unittest.TestCase):
    def test_release_snapshot_preserves_source_identity(self):
        builder = load('build_test_package')
        source = json.loads((builder.PLUGIN / '.claude-plugin/plugin.json').read_text())
        with tempfile.TemporaryDirectory() as temp:
            receipt = builder.build(temp, release_snapshot=True)
            self.assertEqual(receipt['version'], source['version'])
            with zipfile.ZipFile(receipt['archive']) as archive:
                manifest, meta = builder.validate_payload({name: archive.read(name) for name in archive.namelist()})
                self.assertEqual(manifest['version'], source['version'])
                self.assertEqual(meta['release_id'], source['version'].split('+')[1])
            with self.assertRaises(ValueError):
                builder.build(temp, release_snapshot=True)

    def test_controlled_reminder_scenarios(self):
        result = load('run_update_scenarios').run_scenarios()
        self.assertTrue(result['passed'])
        self.assertEqual(result['network_requests'], 0)
        self.assertGreaterEqual(len(result['events']), 9)

    def test_compact_check_permission_failure_and_backoff(self):
        meta = updates.checker._load_metadata()
        with tempfile.TemporaryDirectory() as temp:
            store = updates.StateStore(Path(temp) / 'test.db', 'test')
            lookup = Mock(side_effect=AssertionError('must not access network'))
            result = updates.check_request(store, meta, now=100, lookup=lookup)
            self.assertEqual(result['network_queries'], 0)
            lookup.assert_not_called()
            failure = Mock(side_effect=subprocess.TimeoutExpired('git', 15))
            result = updates.check_request(store, meta, now=2000, allow_network=True,
                                           lookup=failure, clock=lambda: 2015)
            self.assertEqual(result['reason'], 'lookup_failed')
            failure.assert_called_once()
            with store.transaction() as state:
                self.assertIsNone(state['last_success_at'])
                self.assertEqual(state['retry_after'], 3815)
            result = updates.check_request(store, meta, now=2016, allow_network=True, lookup=lookup)
            self.assertEqual(result['action'], 'silent')
            lookup.assert_not_called()

    def test_fixed_lookup_timeout_and_noninteractive(self):
        with patch.object(updates.subprocess, 'run', return_value=Mock(returncode=1)) as run:
            with self.assertRaises(ValueError):
                updates.lookup_refs()
            self.assertEqual(run.call_args.args[0], ['git', 'ls-remote', '--',
                'https://github.com/2026Allin/Mining-Market-Research.git'])
            self.assertEqual(run.call_args.kwargs['timeout'], 15)
            self.assertEqual(run.call_args.kwargs['env']['GIT_TERMINAL_PROMPT'], '0')

    def test_package_unique_ids_integrity_and_source_unchanged(self):
        builder = load('build_test_package')
        manifest = builder.PLUGIN / '.claude-plugin/plugin.json'
        before = manifest.read_bytes()
        with tempfile.TemporaryDirectory() as temp:
            now = builder.datetime(2026, 9, 11, tzinfo=builder.timezone.utc)
            one = builder.build(temp, now=now)
            two = builder.build(temp, now=now)
            self.assertNotEqual(one['release_id'], two['release_id'])
            self.assertEqual(manifest.read_bytes(), before)
            for receipt in (one, two):
                with zipfile.ZipFile(receipt['archive']) as archive:
                    payload = {name: archive.read(name) for name in archive.namelist()}
                    builder.validate_payload(payload)
                    self.assertEqual(set(payload), set(receipt['files']))
                    self.assertNotIn('scripts/run_update_scenarios.py', payload)
                    self.assertEqual(len(receipt['skills']), 7)
                self.assertEqual(builder.hashlib.sha256(Path(receipt['archive']).read_bytes()).hexdigest(), receipt['sha256'])

    def test_package_rejects_missing_chat_capabilities(self):
        builder = load('build_test_package')
        with tempfile.TemporaryDirectory() as temp:
            receipt = builder.build(temp)
            with zipfile.ZipFile(receipt['archive']) as archive:
                payload = {name: archive.read(name) for name in archive.namelist()}
            del payload['skills/mining-market-research/references/hosts/claude-chat.md']
            with self.assertRaises(ValueError):
                builder.validate_payload(payload)

    def test_all_business_entries_have_per_request_gate(self):
        plugin = ROOT / 'plugins/mining-market-research'
        for name in ('mining-market-research', 'news-analysis', 'company-brief',
                     'company-report', 'company-comparison', 'market-analysis'):
            with self.subTest(skill=name):
                text = (plugin / 'skills' / name / 'SKILL.md').read_text()
                self.assertIn('every substantive request', text.lower())
                self.assertIn('notice', text)
