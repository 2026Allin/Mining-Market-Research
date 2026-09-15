"""Delivery state/evidence tests; no real host, network or installation."""
import json
import unittest
import concurrent.futures
from pathlib import Path
from unittest.mock import Mock
import test_update_state as state_tests
import test_hook_updates as hook_tests
updates, RELEASE = state_tests.updates, state_tests.RELEASE
hook = hook_tests.hook


def host_observe(store, ticket, text, *, now):
    with store.transaction() as state:
        pending = next((p for p in updates.delivery.attempts(state) if p['ticket'] == ticket), {})
        return updates.delivery.observe(state, ticket=ticket, text=text,
            source='host_final_message', now=now, turn=pending.get('turn'))


class DeliveryTest(unittest.TestCase):
    setUp = state_tests.UpdateStateTest.setUp
    success = state_tests.UpdateStateTest.success
    def notice(self, now=101, **kwargs):
        # Synthetic observed Hook receipt; never use surface/init as capability.
        with self.store.transaction() as state:
            turn = state.get('delivery_turn')
            if not turn or turn.startswith('test-'):
                turn = 'test-' + str(now)
                state['delivery_turn'] = turn
            state['hook_event_receipts'] = {'PreToolUse': {'execution':'observed', 'turn':turn}}
        return state_tests.UpdateStateTest.notice(self, now, **kwargs)
    chat = state_tests.UpdateStateTest.chat
    def test_ack_never_confirms_and_lock_expiry_does_not_erase_evidence(self):
        self.success()
        n = self.notice()
        self.assertEqual(updates.acknowledge(self.store, n['ticket'], now=102)['action'], 'pending_confirmation')
        with self.store.transaction() as state:
            self.assertIsNone(state['notice_shown_cycle_id'])
        self.assertEqual(host_observe(self.store, n['ticket'], n['footer_text'], now=500)['action'], 'confirmed')
        self.assertEqual(self.notice(501)['action'], 'silent')

    def test_unknown_bounded_and_no_false_confirmed_state(self):
        self.success()
        self.notice(101)
        self.notice(222)
        self.assertEqual(self.notice(400)['reason'], 'retry_exhausted')
        with self.store.transaction() as state:
            self.assertIsNone(state['notice_shown_cycle_id'])
            self.assertEqual(state['last_success_at'], 100)
        self.success(21700)
        self.assertEqual(self.notice(21701)['action'], 'update_available')

    def test_quote_code_wrong_footer_and_missing_evidence_rejected(self):
        self.success()
        n = self.notice()
        for text in (None, 'draft', '> '+n['footer_text'], '```\n'+n['footer_text'],
                     n['footer_text']+'\nother text', n['footer_text'].replace('dev.12','dev.11')):
            self.assertEqual(host_observe(self.store, n['ticket'], text, now=102)['action'], 'confirmation_unknown')
        self.assertEqual(host_observe(self.store, n['ticket'], 'Result\n\n'+n['footer_text'], now=103)['action'], 'confirmed')

    def test_old_cycle_cannot_ack_new_cycle(self):
        self.success()
        n = self.notice()
        self.success(21700)
        self.assertEqual(host_observe(self.store, n['ticket'], n['footer_text'], now=21701)['action'], 'stale_ticket')

    def test_transcript_recovers_without_repeating_after_crash(self):
        transcript = Path(self.temp.name) / 'rollout.jsonl'
        transcript.write_text('')
        self.success()
        with self.store.transaction() as state:
            state['delivery_turn'] = 'turn1'
            state['delivery_transcript'] = updates.delivery.transcript_position(str(transcript))
        n = self.notice()
        transcript.write_text(json.dumps({'type':'response_item','payload':{'type':'message',
            'role':'assistant','channel':'final','content':[{'type':'output_text','text':n['footer_text']}]}})+'\n')
        self.assertEqual(self.notice(500)['action'], 'silent')
        with self.store.transaction() as state:
            self.assertEqual(state['notice_attempts'][0]['evidence_source'], 'host_transcript')

    def test_next_turn_or_tool_transcript_cannot_confirm(self):
        transcript = Path(self.temp.name) / 'rollout.jsonl'
        transcript.write_text('')
        self.success()
        with self.store.transaction() as state:
            state['delivery_turn'] = 'one'
            state['delivery_transcript'] = updates.delivery.transcript_position(str(transcript))
        n = self.notice()
        transcript.write_text('\n'.join(json.dumps(x) for x in [
            {'type':'turn_context','payload':{'turn_id':'two'}},
            {'type':'response_item','payload':{'type':'message','role':'assistant','channel':'final',
                'content':[{'type':'output_text','text':n['footer_text']}]}}])+'\n')
        with self.store.transaction() as state:
            updates.delivery.recover(state, 500)
            self.assertIsNone(state['notice_shown_cycle_id'])

    def test_chat_attempt_only_is_bounded_without_confirmation_or_transcript(self):
        store, loaded = self.chat()
        ticket = updates.probe(store, now=100)['ticket']
        updates.record(store, ticket, now=100, release=RELEASE)
        n = updates.chat_notice(store, now=101, loaded_release=loaded)
        self.assertIn('手动更新', n['footer_text'])
        self.assertEqual(n['delivery_status'], 'attempted')
        result = updates.review_notice(store, n['ticket'], n['footer_text'], now=300)
        self.assertEqual(result['reason'], 'conversation_review_disabled')
        with store.transaction() as state:
            self.assertIsNone(state['notice_shown_cycle_id'])
            self.assertIsNone(state['notice_attempts'][0]['transcript'])
        self.assertEqual(updates.chat_notice(store, now=222, loaded_release=loaded)['action'], 'update_available')
        self.assertEqual(updates.chat_notice(store, now=400, loaded_release=loaded)['reason'], 'retry_exhausted')

    def test_chat_confirmation_cli_rejects_before_stdin_or_database(self):
        import io
        from unittest.mock import patch
        with patch.object(updates.tempfile, 'gettempdir', return_value=self.temp.name):
            meta = updates.checker._load_metadata(updates.checker.metadata_path_for_platform('claude'))
            context = updates.initialize_chat(meta)
        for action in ('review', 'ack'):
            with patch.object(updates.sys, 'argv', ['update_state.py', action, '--context-file', context['context_file']]), \
                    patch.object(updates.tempfile, 'gettempdir', return_value=self.temp.name), \
                    patch.object(updates.sys, 'stdin') as stdin, \
                    patch.object(updates.sys, 'stdout', new_callable=io.StringIO) as stdout, \
                    patch.object(updates, 'session_context') as database:
                updates.main()
                self.assertEqual(json.loads(stdout.getvalue())['reason'], 'conversation_review_disabled' if action == 'review' else 'chat_delivery_confirmation_disabled')
                stdin.buffer.read.assert_not_called()
                database.assert_not_called()

    def test_legacy_migration_not_host_evidence(self):
        with self.store.transaction() as state:
            state.update(schema_version=3, check_cycle_id='old', notice_shown_cycle_id='old')
        with self.store.transaction() as state:
            self.assertEqual(state['schema_version'], 4)
            self.assertIsNone(state['notice_shown_cycle_id'])
            self.assertEqual(state['legacy_suppressed_cycle'], 'old')

    def test_parallel_reservation_and_idempotent_confirmation(self):
        self.success()
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(lambda _: self.notice(), range(4)))
        offers = [r for r in results if r['action'] == 'update_available']
        self.assertEqual(len(offers), 1)
        n = offers[0]
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(lambda _: host_observe(self.store, n['ticket'], n['footer_text'], now=200), range(4)))
        self.assertTrue(all(r['action'] == 'confirmed' for r in results))
        with self.store.transaction() as state:
            self.assertEqual(len(state['notice_attempts']), 1)

    def test_english_footer_is_exact_and_manual(self):
        self.success()
        with self.store.transaction() as state:
            state['delivery_turn'] = 'en'
            state['hook_event_receipts'] = {'PreToolUse': {'execution':'observed', 'turn':'en'}}
        n = updates.session_notice(self.store, now=101, loaded_release=state_tests.LOADED,
                                   platform='codex', locale='en')
        self.assertTrue(n['footer_text'].startswith('Update:'))
        self.assertEqual(host_observe(self.store, n['ticket'], n['footer_text'], now=200)['action'], 'confirmed')

    def test_transcript_symlink_is_not_evidence(self):
        target = Path(self.temp.name) / 'file'
        target.write_text('private')
        link = Path(self.temp.name) / 'link'
        link.symlink_to(target)
        self.assertIsNone(updates.delivery.transcript_position(str(link)))

    def test_same_native_turn_cannot_retry_after_timeout(self):
        self.success()
        with self.store.transaction() as state:
            state['delivery_turn'] = 'one'
        self.notice()
        self.assertEqual(self.notice(400)['reason'], 'awaiting_turn_completion')
        with self.store.transaction() as state:
            state['delivery_turn'] = 'two'
        self.assertEqual(self.notice(401)['action'], 'update_available')


class DeliveryHookTest(unittest.TestCase):
    setUp = hook_tests.HookUpdatesTest.setUp
    tearDown = hook_tests.HookUpdatesTest.tearDown
    refs = hook_tests.HookUpdatesTest.refs
    store = hook_tests.HookUpdatesTest.store
    def test_native_without_hooks_defaults_to_attempt_only(self):
        context = updates.initialize_host_session(self.meta, self.event['session_id'])
        store = self.store()
        ticket = updates.probe(store, now=100)['ticket']
        updates.record(store, ticket, now=100, release={**RELEASE, 'version':'99.0.0'})
        n = updates.session_notice(store, now=101, loaded_release=context['loaded_release'], platform='codex')
        self.assertEqual(n['delivery_mode'], 'attempt_only')
        self.assertEqual(n['update_method'], 'resolve_on_upgrade')
        hook.handle(self.event, platform='codex', now=102)
        hook.handle({**self.event, 'hook_event_name':'Stop', 'last_assistant_message':n['footer_text']}, platform='codex', now=103)
        with store.transaction() as state:
            self.assertIsNone(state['notice_shown_cycle_id'])

    def test_startup_and_closed_or_wrong_turn_do_not_enable_evidence(self):
        hook.handle({**self.event, 'hook_event_name':'SessionStart'}, platform='codex', now=1)
        with self.store().transaction() as state:
            self.assertEqual(updates.delivery.mode(state), 'attempt_only')
        hook.handle({**self.event, 'turn_id':'one'}, platform='codex', now=10)
        with self.store().transaction() as state:
            self.assertEqual(updates.delivery.mode(state), 'evidence')
            state['delivery_turn'] = 'other'
            self.assertEqual(updates.delivery.mode(state), 'attempt_only')
            state['delivery_turn'] = 'one'
            state['delivery_turn_ended'] = True
            self.assertEqual(updates.delivery.mode(state), 'attempt_only')

    def test_native_review_rejected_without_reading_stdin(self):
        import io
        from unittest.mock import patch
        with patch.object(updates.sys, 'argv', ['update_state.py','review','--platform','codex']), \
                patch.object(updates.sys, 'stdin') as stdin, \
                patch.object(updates.sys, 'stdout', new_callable=io.StringIO) as output:
            updates.main()
            self.assertEqual(json.loads(output.getvalue())['reason'], 'conversation_review_disabled')
            stdin.buffer.read.assert_not_called()
    def test_stop_both_platforms_confirm_without_network_or_agent_ack(self):
        for platform in ('codex', 'claude'):
            event = {**self.event, 'session_id': platform, 'turn_id': 'turn1'}
            meta = updates.checker._load_metadata(updates.checker.metadata_path_for_platform(platform))
            refs = 'a'*40 + '\trefs/heads/main\n' + 'a'*40 + '\trefs/tags/' + meta['tag_prefix'] + '99.0.0\n'
            hook.handle(event, platform=platform, allow_network=True, lookup=lambda:refs, now=100)
            context = updates.initialize_host_session(meta, platform)
            store = updates.session_context(meta, context['session_id'], context['loaded_release'])
            n = updates.session_notice(store, now=101, loaded_release=context['loaded_release'], platform=platform)
            stop = {**event, 'hook_event_name':'Stop', 'last_assistant_message':n['footer_text']}
            lookup = Mock(side_effect=AssertionError('no network'))
            for _ in range(2):
                self.assertEqual(hook.handle(stop, platform=platform, allow_network=True, lookup=lookup, now=105), {})
            with store.transaction() as state:
                self.assertEqual(state['notice_attempts'][0]['status'], 'confirmed')
                self.assertEqual(state['notice_attempts'][0]['evidence_source'], 'host_final_message')
            lookup.assert_not_called()

    def test_lifecycle_without_plugin_context_does_not_initialize(self):
        for kind in ('Stop', 'UserPromptSubmit'):
            self.assertEqual(hook.handle({'hook_event_name':kind,'session_id':'unrelated'}, platform='codex'), {})
        self.assertEqual(list(Path(self.temp.name).iterdir()), [])

    def test_wrong_turn_stop_does_not_confirm(self):
        event = {**self.event,'turn_id':'one'}
        hook.handle(event, platform='codex', allow_network=True, lookup=lambda:self.refs(), now=100)
        context = updates.initialize_host_session(self.meta, event['session_id'])
        n = updates.session_notice(self.store(), now=101, loaded_release=context['loaded_release'], platform='codex')
        hook.handle({**event,'hook_event_name':'Stop','turn_id':'two','last_assistant_message':n['footer_text']}, platform='codex', now=105)
        with self.store().transaction() as state:
            self.assertIsNone(state['notice_shown_cycle_id'])

    def test_claude_no_turn_id_and_missing_stop_evidence(self):
        self.meta = updates.checker._load_metadata(updates.checker.metadata_path_for_platform('claude'))
        hook.handle(self.event, platform='claude', allow_network=True, lookup=lambda:self.refs(), now=100)
        context = updates.initialize_host_session(self.meta, self.event['session_id'])
        updates.session_notice(self.store(), now=101, loaded_release=context['loaded_release'], platform='claude')
        hook.handle({**self.event,'hook_event_name':'Stop'}, platform='claude', now=103)
        with self.store().transaction() as state:
            self.assertIsNone(state['notice_shown_cycle_id'])
            old_turn = state['delivery_turn']
        hook.handle({**self.event,'hook_event_name':'UserPromptSubmit'}, platform='claude', now=300)
        with self.store().transaction() as state:
            self.assertNotEqual(state['delivery_turn'], old_turn)
