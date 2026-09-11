#!/usr/bin/env python3
"""Offline controlled acceptance of update logic, NOT real host certification.

Synthetic refs/time live only in this test harness. No network, installation,
publication or edits to production state. Every scenario uses a temporary DB.
"""
import json
from pathlib import Path
import sys
import tempfile
import uuid

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'skills/mining-market-research/scripts'))
import update_state as updates


def run_scenarios():
    meta = updates.checker._load_metadata(updates.checker.metadata_path_for_platform('claude'))
    loaded = meta['version'] + '+' + meta['release_id']
    # A fixed major version beyond this development series, never a real release.
    version = '999.0.0'
    refs = 'a' * 40 + '\trefs/heads/main\n' + 'a' * 40 + '\trefs/tags/' + meta['tag_prefix'] + version + '\n'
    events, queries = [], []

    def lookup():
        queries.append('synthetic-lookup')
        return refs

    with tempfile.TemporaryDirectory(prefix='mmr-update-acceptance-') as temp:
        store = updates.StateStore(Path(temp) / 'isolated.sqlite3', uuid.uuid4().hex)

        def check(label, now):
            result = updates.check_request(store, meta, now=now, allow_network=True,
                                           lookup=lookup, clock=lambda: now)
            events.append({'case': label, 'result': result})
            return result

        def notice(label, now):
            result = updates.chat_notice(store, now=now, loaded_release=loaded)
            events.append({'case': label, 'result': result})
            return result

        assert check('first-use', 100)['action'] == 'recorded'
        first = notice('new-version-manual-notice', 101)
        assert first['action'] == 'update_available' and first['update_method'] == 'manual'
        assert 'installed_release' not in first
        updates.acknowledge(store, first['ticket'], now=101)
        # Refusal/ignore do not mutate the success clock. Ack means notice emitted,
        # NOT user consent. A normal business request must still execute check.
        assert check('request-after-decline', 102)['action'] == 'cached'
        assert notice('no-repeat-after-decline', 102)['action'] == 'silent'
        assert check('request-after-ignored-notice', 103)['action'] == 'cached'
        assert notice('no-repeat-after-ignore', 103)['action'] == 'silent'
        assert check('one-second-before-six-hours', 21699)['action'] == 'cached'
        assert len(queries) == 1
        assert check('exact-six-hour-boundary', 21700)['action'] == 'recorded'
        assert notice('same-version-reminds-next-cycle', 21701)['action'] == 'update_available'
        assert len(queries) == 2
        with store.transaction() as state:
            assert state['last_success_at'] == 21700
        restarted = updates.StateStore(Path(temp) / 'new-session.sqlite3', uuid.uuid4().hex)
        assert updates.probe(restarted, now=21702)['action'] == 'check_required'
        events.append({'case': 'new-session-independent', 'result': {'action': 'check_required'}})
        # Same product-version metadata after a simulated manual update: no reload
        # claim and no further update notification. This is not an actual upload.
        loaded_new = version + '+claude.20260911131511'
        fresh = updates.StateStore(Path(temp) / 'reloaded.sqlite3', 'simulated-loaded-version')
        updates.check_request(fresh, meta, now=30000, allow_network=True,
                              lookup=lookup, clock=lambda: 30000)
        result = updates.chat_notice(fresh, now=30001, loaded_release=loaded_new)
        assert result['action'] == 'silent'
        events.append({'case': 'simulated-new-session-version-current', 'result': result})
    return {'mode': 'offline-synthetic-not-host-certification', 'passed': True,
            'network_requests': 0, 'installations': 0, 'events': events}


if __name__ == '__main__':
    print(json.dumps(run_scenarios(), indent=2))
