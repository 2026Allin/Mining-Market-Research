"""Synthetic host events only; does not certify real desktop Hook support."""
import io
import json
from pathlib import Path
from unittest.mock import Mock, patch
import unittest
import test_hook_updates as fixtures
hook, updates, PLUGIN = fixtures.hook, fixtures.updates, fixtures.PLUGIN
import runtime_contract as runtime


class RuntimeEntryTest(unittest.TestCase):
    setUp = fixtures.HookUpdatesTest.setUp
    tearDown = fixtures.HookUpdatesTest.tearDown
    store = fixtures.HookUpdatesTest.store
    refs = fixtures.HookUpdatesTest.refs

    def test_startup_no_network_no_notice_and_first_business_check(self):
        for platform in ('codex', 'claude'):
            event = {**self.event, 'hook_event_name': 'SessionStart', 'prompt': 'PRIVATE'}
            lookup = Mock(return_value=self.refs())
            with patch.object(updates.delivery, 'recover', side_effect=AssertionError('no transcript')):
                result = hook.handle(event, platform=platform, allow_network=True, lookup=lookup, now=10)
            text = result['hookSpecificOutput']['additionalContext']
            self.assertIn('news-analysis', text)
            self.assertIn('startup did not check', text)
            self.assertNotIn('PRIVATE', text)
            lookup.assert_not_called()
            meta = updates.checker._load_metadata(updates.checker.metadata_path_for_platform(platform))
            context = updates.initialize_host_session(meta, event['session_id'])
            store = updates.session_context(meta, context['session_id'], context['loaded_release'])
            with store.transaction() as state:
                self.assertIsNone(state['last_success_at'])
                self.assertIsNone(state['notice_lease'])
                self.assertTrue(state['hook_event_receipts']['SessionStart']['context_output'])
                self.assertNotIn('PRIVATE', json.dumps(state))
            hook.handle(self.event, platform=platform, allow_network=True, lookup=lookup, now=100)
            lookup.assert_called_once()

    def test_resume_joins_snapshot_without_reset_or_network(self):
        event = {**self.event, 'hook_event_name': 'SessionStart'}
        hook.handle(event, platform='codex', now=1)
        hook.handle(self.event, platform='codex', allow_network=True, lookup=self.refs, now=100)
        lookup = Mock(side_effect=AssertionError('no network'))
        for source in ('resume', 'compact'):
            hook.handle({**event, 'source': source}, platform='codex', lookup=lookup, now=110)
        with self.store().transaction() as state:
            self.assertEqual(state['last_success_at'], 100)
        lookup.assert_not_called()

    def test_compact_marks_only_and_pretool_reinjects(self):
        hook.handle(self.event, platform='codex', allow_network=True, lookup=self.refs, now=100)
        event = {**self.event, 'hook_event_name': 'PreCompact', 'transcript_path': '/PRIVATE', 'prompt':'PRIVATE'}
        with patch.object(updates.delivery, 'recover', side_effect=AssertionError('no transcript')):
            self.assertEqual(hook.handle(event, platform='codex', now=101), {})
        result = hook.handle(self.event, platform='codex', allow_network=True, lookup=self.refs, now=102)
        self.assertIn('news-analysis', result['hookSpecificOutput']['additionalContext'])
        with self.store().transaction() as state:
            self.assertNotIn('PRIVATE', json.dumps(state))
            self.assertEqual(state['last_success_at'], 100)

    def test_no_context_for_unrelated_compact_or_unknown_platform(self):
        self.assertEqual(hook.handle({**self.event, 'hook_event_name':'PreCompact'}, platform='codex'), {})
        self.assertEqual(hook.handle({**self.event, 'hook_event_name':'SessionStart'}, platform='unknown'), {})
        self.assertEqual(list(Path(self.temp.name).iterdir()), [])

    def test_no_startup_for_subagent(self):
        self.assertEqual(hook.handle({**self.event, 'hook_event_name':'SessionStart', 'agent_id':'child'}, platform='codex'), {})
        self.assertEqual(list(Path(self.temp.name).iterdir()), [])

    def test_capabilities_never_guess_host_and_create_no_state(self):
        for args, profile in [([], 'unknown'), (['--platform','claude','--surface','claude-chat'], 'remote-mcp-no-hooks')]:
            with patch.object(updates.sys, 'argv', ['update_state.py','capabilities', *args]), \
                    patch.object(updates.sys, 'stdout', new_callable=io.StringIO) as output:
                updates.main()
            result = json.loads(output.getvalue())
            self.assertEqual(result['capabilities']['profile'], profile)
            self.assertEqual(result['effective_host_registration'], 'unverified')
            self.assertEqual(result['network_queries'], 0)
        self.assertEqual(list(Path(self.temp.name).iterdir()), [])

    def test_diagnostics_distinguish_observation_from_registration(self):
        hook.handle({**self.event, 'hook_event_name':'SessionStart'}, platform='codex', now=10)
        with self.store().transaction() as state:
            result = runtime.diagnostics('codex', 'native', state['hook_event_receipts'])
        self.assertEqual(result['events']['SessionStart']['execution'], 'observed')
        self.assertEqual(result['events']['PreToolUse']['execution'], 'unverified')
        self.assertEqual(result['effective_host_registration'], 'unverified')
        self.assertEqual(result['skill_read'], 'unverified')

    def test_shipped_manifest_matches_dispatch_contract(self):
        self.assertEqual(json.loads((PLUGIN/'hooks/hooks.json').read_text()), runtime.hook_config())
        for name, rules in runtime.hook_config()['hooks'].items():
            if name != 'PreToolUse':
                self.assertNotIn('ALLOW_NETWORK', rules[0]['hooks'][0]['command'])
        self.assertLess(len(runtime.routing_text().encode()), 4096)
