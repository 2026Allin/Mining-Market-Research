#!/usr/bin/env python3
"""Generate opt-in platform headers; transport verification is NOT implied."""
import argparse
import copy
import json
from pathlib import Path
import sync_plugin_release as releases


def render(config, metadata, enabled=False):
    value = copy.deepcopy(config)
    server = value['mcpServers']['mining_market_research']
    # Generated declarations must never leak across hosts or survive opt-out.
    for key in ('headers', 'http_headers', 'httpHeaders'):
        if key in server:
            server[key] = {k: v for k, v in server[key].items()
                           if not k.lower().startswith('x-mmr-')}
            if not server[key]:
                del server[key]
    if enabled:
        # Verified with native Codex plugin parsing, not TOML assumptions.
        key = 'http_headers' if metadata['platform'] == 'codex' else 'headers'
        headers = server.setdefault(key, {})
        headers.update({'X-MMR-Plugin-Version': metadata['version'],
                        'X-MMR-Plugin-Build': metadata['release_id'],
                        'X-MMR-Platform': metadata['platform'],
                        'X-MMR-Channel': 'dev' if '-dev.' in metadata['version'] else 'stable',
                        'X-MMR-Update-Owner': 'client'})
    return value


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--platform', choices=['codex', 'claude'], required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--version-headers', action='store_true')
    args = parser.parse_args()
    meta = releases.expected_release(platform=args.platform)
    config = json.loads((releases.PLUGIN_ROOT / '.mcp.json').read_text())
    with args.output.open('x') as output:
        json.dump(render(config, meta, args.version_headers), output, indent=2)
