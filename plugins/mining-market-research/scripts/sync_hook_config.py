"""Generate hook registration from the dispatcher's bundled alias contract."""
import argparse
import json
from pathlib import Path
import sys

PLUGIN = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(PLUGIN / 'skills/mining-market-research/scripts'))
from runtime_contract import hook_config


def sync(*, write=False):
    path = PLUGIN / 'hooks/hooks.json'
    expected = json.dumps(hook_config(), indent=2) + '\n'
    if path.read_text() != expected:
        if not write:
            raise ValueError('hook config drift; run sync_hook_config.py --write')
        path.write_text(expected)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--write', action='store_true')
    group.add_argument('--check', action='store_true')
    args = parser.parse_args()
    sync(write=args.write)
    print('hook config synchronized')
