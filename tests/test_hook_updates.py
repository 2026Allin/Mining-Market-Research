"""Phase-one local ownership; all network results are synthetic."""
import concurrent.futures
import importlib.util
import json
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch
import zipfile

from test_update_state import updates
from test_update_optimization import load

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / 'plugins/mining-market-research'
spec = importlib.util.spec_from_file_location('mmr_hook', PLUGIN / 'hooks/dispatch.py')
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)


class HookUpdatesTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.patch = patch.object(updates.tempfile, 'gettempdir', return_value=self.temp.name)
        self.patch.start()
        self.meta = updates.checker._load_metadata()
        self.event = {'hook_event_name': 'PreToolUse', 'session_id': 'native-session-1',
                      'tool_name': 'mcp__mining_market_research__search_news'}

    def tearDown(self):
        self.patch.stop()
        self.temp.cleanup()

    def store(self):
        context = updates.initialize_host_session(self.meta, self.event['session_id'])
        return updates.session_context(self.meta, context['session_id'], context['loaded_release'])

    def refs(self):
        return 'a'*40 + '\trefs/heads/main\n' + 'a'*40 + '\trefs/tags/' + self.meta['tag_prefix'] + '99.0.0\n'

    def run_main(self, payload):
        output, errors = io.StringIO(), io.StringIO()
        stdin = Mock(buffer=io.BytesIO(payload))
        with patch.object(hook.sys, 'stdin', stdin), patch.object(hook.sys, 'stdout', output), \
                patch.object(hook.sys, 'stderr', errors):
            hook.main()
        return json.loads(output.getvalue()), errors.getvalue()

    def diagnostics(self):
        return [json.loads(line) for line in hook.diagnostic_path().read_text().splitlines()]

    def test_main_diagnostic_success_and_redaction(self):
        payload = {**self.event, 'tool_input': {'token': 'PRIVATE'},
                   'tool_response': 'PRIVATE'}
        result, errors = self.run_main(json.dumps(payload).encode())
        self.assertIn('hookSpecificOutput', result)
        records = self.diagnostics()
        self.assertEqual([r['stage'] for r in records],
                         ['entered', 'event_received', 'initializing', 'context_ready', 'completed'])
        self.assertEqual(len({r['invocation'] for r in records}), 1)
        self.assertNotIn('PRIVATE', errors + json.dumps(records))
        self.assertNotIn(self.event['session_id'], json.dumps(records))

    def test_main_initialization_failure_is_visible_and_fail_open(self):
        with patch.object(updates, 'initialize_host_session', side_effect=OSError('PRIVATE')):
            result, errors = self.run_main(json.dumps(self.event).encode())
        self.assertEqual(result, {})
        self.assertEqual(self.diagnostics()[-1]['stage'], 'dispatch_failed')
        self.assertNotIn('PRIVATE', errors)
        self.assertNotIn('context_ready', [r['stage'] for r in self.diagnostics()])

    def test_invalid_input_and_rejected_tool_are_visible(self):
        result, _ = self.run_main(b'not json PRIVATE')
        self.assertEqual(result, {})
        self.assertEqual(self.diagnostics()[-1]['stage'], 'input_invalid')
        result, errors = self.run_main(json.dumps({**self.event, 'tool_name': 'PRIVATE'}).encode())
        self.assertEqual(result, {})
        self.assertIn('matcher_rejected', errors)
        self.assertNotIn('PRIVATE', errors)

    def test_diagnostic_log_bound_and_symlink_rejection(self):
        with patch.object(hook.sys, 'stderr', io.StringIO()):
            emit = hook.diagnostic_writer()
            for _ in range(600):
                emit('entered')
            path = hook.diagnostic_path()
            self.assertLessEqual(path.stat().st_size, 65536)
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.diagnostics()  # Every retained line is valid JSON.
            path.unlink()
            target = Path(self.temp.name) / 'untouched'
            target.write_text('keep')
            path.symlink_to(target)
            emit('entered')
            self.assertEqual(target.read_text(), 'keep')

    def test_log_failure_does_not_change_output(self):
        with patch.object(hook.os, 'open', side_effect=PermissionError()):
            result, errors = self.run_main(b'{}')
        self.assertEqual(result, {})
        self.assertIn('entered', errors)

    def test_diagnostic_only_never_enters_update_flow(self):
        with patch.object(hook.sys, 'argv', ['dispatch.py', '--diagnostic-only']), \
                patch.object(hook, 'handle', side_effect=AssertionError('must not run')):
            for name in ('exec', 'Bash', self.event['tool_name']):
                result, errors = self.run_main(json.dumps({**self.event, 'tool_name': name}).encode())
                self.assertEqual(result, {})
                self.assertIn('probe_completed', errors)
                self.assertEqual(self.diagnostics()[-1]['tool'], name)

    def test_all_contract_tools_matched(self):
        contract = json.loads((PLUGIN / 'contracts/hosted-mcp-v1.json').read_text())
        self.assertEqual(set(contract['oauth']['tool_scopes']), hook.TOOLS)

    def test_shipped_hooks_are_not_temporary_probes(self):
        config = json.loads((PLUGIN / 'hooks/hooks.json').read_text())['hooks']
        for event, timeout in [('PreToolUse', 20), ('PostToolUse', 5)]:
            self.assertEqual(len(config[event]), 1)
            rule = config[event][0]
            self.assertEqual(rule['matcher'], '^mcp__mining_market_research__.*')
            import re
            for tool in hook.TOOLS:
                self.assertIsNotNone(re.fullmatch(rule['matcher'], 'mcp__mining_market_research__' + tool))
            for tool in ('exec', 'Bash', 'mcp__other__search_news'):
                self.assertIsNone(re.search(rule['matcher'], tool))
            self.assertNotIn('--diagnostic-only', rule['hooks'][0]['command'])
            self.assertEqual(rule['hooks'][0]['timeout'], timeout)

    def test_concurrent_context_join_and_isolation(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            contexts = list(pool.map(lambda _: updates.initialize_host_session(self.meta, 'same'), range(8)))
        self.assertEqual(len({c['context_file'] for c in contexts}), 1)
        other = updates.initialize_host_session(self.meta, 'other')
        self.assertNotEqual(other['context_file'], contexts[0]['context_file'])
        changed = {**self.meta, 'version': '99.0.0'}
        self.assertEqual(updates.initialize_host_session(changed, 'same')['loaded_release'], contexts[0]['loaded_release'])

    def test_hook_and_skill_share_success_ttl(self):
        lookup = Mock(return_value=self.refs())
        result = hook.handle(self.event, platform='codex', allow_network=True, lookup=lookup, now=100)
        self.assertIn('context_file', result['hookSpecificOutput']['additionalContext'])
        lookup.assert_called_once()
        store = self.store()
        cached = updates.check_request(store, self.meta, now=101, allow_network=True, lookup=lookup)
        self.assertEqual(cached['action'], 'cached')
        self.assertEqual(cached['network_queries'], 0)
        hook.handle(self.event, platform='codex', allow_network=True, lookup=lookup, now=21700)
        self.assertEqual(lookup.call_count, 2)

    def test_context_injected_only_on_first_use_or_changed_status(self):
        lookup = Mock(return_value=self.refs())
        self.assertTrue(hook.handle(self.event, platform='codex', allow_network=True, lookup=lookup, now=100))
        self.assertEqual(hook.handle(self.event, platform='codex', allow_network=True, lookup=lookup, now=101), {})
        self.assertEqual(lookup.call_count, 1)
        self.assertTrue(hook.handle(self.event, platform='codex', allow_network=True, lookup=lookup, now=21700))
        self.assertEqual(lookup.call_count, 2)

    def test_network_permission_is_only_on_pre_hook_command(self):
        config = json.loads((PLUGIN / 'hooks/hooks.json').read_text())['hooks']
        self.assertTrue(config['PreToolUse'][0]['hooks'][0]['command'].startswith('MMR_HOOK_ALLOW_NETWORK=1 '))
        self.assertNotIn('MMR_HOOK_ALLOW_NETWORK', config['PostToolUse'][0]['hooks'][0]['command'])

    def test_no_permission_does_not_poison_skill_fallback(self):
        lookup = Mock(side_effect=AssertionError('no network'))
        hook.handle(self.event, platform='codex', lookup=lookup, now=100)
        with self.store().transaction() as state:
            self.assertIsNone(state['last_success_at'])
            self.assertEqual(state['retry_after'], 0)
            self.assertFalse(state['last_hook_receipt']['notice_emitted'])

    def test_network_failure_preserves_business_and_backs_off(self):
        lookup = Mock(side_effect=OSError())
        hook.handle(self.event, platform='codex', allow_network=True, lookup=lookup, now=100)
        hook.handle(self.event, platform='codex', allow_network=True, lookup=lookup, now=101)
        self.assertEqual(lookup.call_count, 1)
        with self.store().transaction() as state:
            self.assertIsNone(state['last_success_at'])

    def test_hook_never_acknowledges_display(self):
        hook.handle(self.event, platform='codex', allow_network=True, lookup=lambda:self.refs(), now=100)
        with self.store().transaction() as state:
            self.assertIsNone(state['notice_shown_cycle_id'])
            self.assertIsNone(state['notice_lease'])

    def test_old_and_unverified_server_no_takeover_or_payload_logging(self):
        for response, expected in [({}, 'absent'), ({'plugin_runtime': []}, 'invalid'),
             ({'plugin_runtime': {'schema_version':1,'update_check_owner':'server'},
               'plugin_update': {'shell':'secret-untrusted-command'}}, 'server_unverified')]:
            event = {**self.event, 'hook_event_name':'PostToolUse','tool_response':response}
            self.assertEqual(hook.handle(event, platform='codex', now=100), {})
            with self.store().transaction() as state:
                self.assertEqual(state['last_hook_receipt']['server_capability'], expected)
                self.assertNotIn('secret', json.dumps(state))

    def test_unrelated_or_spoofed_namespace_ignored(self):
        for tool in ['mcp__other__search_news', 'evil_mining_market_research:search_news',
                     'mcp__mining_market_research__install_plugin']:
            self.assertEqual(hook.handle({**self.event,'tool_name':tool},platform='codex'), {})
        self.assertEqual(list(Path(self.temp.name).iterdir()), [])

    def test_header_generation_and_claude_package(self):
        builder = load('build_test_package')
        with tempfile.TemporaryDirectory(dir=self.temp.name) as out:
            receipt = builder.build(out, version_headers=True)
            with zipfile.ZipFile(receipt['archive']) as archive:
                self.assertEqual(archive.read('hooks/platform.txt'), b'claude\n')
                self.assertIn('hooks/dispatch.py', archive.namelist())
                headers = json.loads(archive.read('.mcp.json'))['mcpServers']['mining_market_research']['headers']
                self.assertEqual(headers['X-MMR-Plugin-Build'], receipt['release_id'])
                self.assertEqual(headers['X-MMR-Platform'], 'claude')
                self.assertEqual(headers['X-MMR-Update-Owner'], 'client')
                payload = {name: archive.read(name) for name in archive.namelist()}
                config = json.loads(payload['.mcp.json'])
                config['mcpServers']['mining_market_research']['headers']['X-MMR-Plugin-Build'] = 'wrong'
                payload['.mcp.json'] = json.dumps(config).encode()
                with self.assertRaisesRegex(ValueError, 'header metadata mismatch'):
                    builder.validate_payload(payload)
        renderer = load('render_mcp_config')
        source = json.loads((PLUGIN / '.mcp.json').read_text())
        clean = {'mcpServers': {'mining_market_research': {'url': 'https://example.test'}}}
        self.assertEqual(renderer.render(clean, self.meta), clean)
        codex = renderer.render(clean, {**self.meta, 'platform': 'codex'}, True)
        server = codex['mcpServers']['mining_market_research']
        self.assertIn('http_headers', server)
        self.assertNotIn('headers', server)
        claude = renderer.render(codex, {**self.meta, 'platform': 'claude'}, True)
        self.assertNotIn('http_headers', claude['mcpServers']['mining_market_research'])
        self.assertEqual(renderer.render(claude, self.meta), clean)


if __name__ == '__main__':
    unittest.main()
