#!/usr/bin/env python3
"""Build an isolated Claude test ZIP with a fresh build ID and verified receipt.

No source manifest changes, install, network, tags or publication. Reuse the
same output root to serialize build IDs, including simultaneous invocations.
"""
import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
import zipfile

sys.dont_write_bytecode = True
import sync_plugin_release as releases

PLUGIN = Path(__file__).resolve().parents[1]
SKILLS = {'mining-market-research', 'company-brief', 'company-report',
          'company-comparison', 'market-analysis', 'news-analysis', 'upgrade'}
ROOTS = ('.claude-plugin', '.mcp.json', 'skills', 'assets')


def validate_payload(payload):
    manifest = json.loads(payload['.claude-plugin/plugin.json'])
    meta = json.loads(payload['skills/mining-market-research/references/plugin-release-claude.json'])
    if manifest['name'] != 'anchises-analysis' or manifest['skills'] != './skills/':
        raise ValueError('invalid plugin identity or skills root')
    if manifest['version'] != meta['version'] + '+' + meta['release_id']:
        raise ValueError('release metadata mismatch')
    if not releases.FULL_VERSION_RES['claude'].fullmatch(manifest['version']):
        raise ValueError('invalid build version')
    found = {name.split('/')[1] for name in payload if re.fullmatch(r'skills/[^/]+/SKILL.md', name)}
    if found != SKILLS:
        raise ValueError('unexpected skill set')
    for skill in SKILLS:
        if f'name: {skill}\n' not in payload[f'skills/{skill}/SKILL.md'].decode():
            raise ValueError('skill name mismatch')
    helper = payload['skills/mining-market-research/scripts/update_state.py'].decode()
    for token in ('--surface', '--session-id', '--allow-network', '--context-file', 'def initialize_chat(', 'def check_request('):
        if token not in helper:
            raise ValueError('missing update capability: ' + token)
    if 'skills/mining-market-research/references/hosts/claude-chat.md' not in payload:
        raise ValueError('missing Chat adapter')
    for name, data in payload.items():
        if name.endswith('.md'):
            # All relative Markdown links must resolve within the package.
            import posixpath
            for target in re.findall(r'\]\(([^)]+)\)', data.decode()):
                target = target.split('#', 1)[0]
                if not target or '://' in target or target.startswith('#'):
                    continue
                resolved = posixpath.normpath(posixpath.join(posixpath.dirname(name), target))
                if resolved.startswith('../') or resolved not in payload:
                    raise ValueError(f'broken package link: {name} -> {target}')
    return manifest, meta


def build(output_root, plugin=PLUGIN, now=None):
    output_root = Path(output_root).resolve()
    plugin = Path(plugin).resolve()
    if output_root == plugin or plugin in output_root.parents:
        raise ValueError('output must be outside plugin source')
    payload = {}
    for root in ROOTS:
        source = plugin / root
        if source.is_symlink():
            raise ValueError('symlink package root')
        if not source.exists():
            raise ValueError('missing package root: ' + root)
        for path in ([source] if source.is_file() else sorted(source.rglob('*'))):
            if path.is_symlink():
                raise ValueError('symlinks are not allowed in package')
            if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc' and path.name != '.DS_Store':
                payload[path.relative_to(plugin).as_posix()] = path.read_bytes()
    manifest_path = '.claude-plugin/plugin.json'
    metadata_path = 'skills/mining-market-research/references/plugin-release-claude.json'
    manifest, metadata = validate_payload(payload)
    # Source metadata must already be synchronized before any staged changes.
    version = manifest['version'].split('+')[0]
    previous = datetime.strptime(metadata['release_id'].split('.', 1)[1], '%Y%m%d%H%M%S').replace(tzinfo=timezone.utc)
    stamp = max((now or datetime.now(timezone.utc)).replace(microsecond=0), previous + timedelta(seconds=1))
    output_root.mkdir(parents=True, exist_ok=True)
    while True:
        build_id = 'claude.' + stamp.strftime('%Y%m%d%H%M%S')
        directory = output_root / build_id
        try:
            directory.mkdir()
            break
        except FileExistsError:
            stamp += timedelta(seconds=1)
    manifest['version'] = version + '+' + build_id
    metadata['release_id'] = build_id
    payload[manifest_path] = (json.dumps(manifest, indent=2) + '\n').encode()
    payload[metadata_path] = (json.dumps(metadata, indent=2) + '\n').encode()
    validate_payload(payload)
    artifact = directory / 'mining-market-research-dev11.zip'
    with zipfile.ZipFile(artifact, 'x', zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(payload.items()):
            archive.writestr(name, data)
    with zipfile.ZipFile(artifact) as archive:
        if archive.testzip() is not None or set(archive.namelist()) != set(payload):
            raise ValueError('ZIP integrity failure')
        for name, data in payload.items():
            if archive.read(name) != data:
                raise ValueError('ZIP content mismatch')
    receipt = {'kind': 'local-test-package-not-published', 'release_id': build_id,
               'version': manifest['version'], 'archive': str(artifact),
               'sha256': hashlib.sha256(artifact.read_bytes()).hexdigest(),
               'skills': sorted(SKILLS),
               'files': {name: hashlib.sha256(data).hexdigest() for name, data in sorted(payload.items())}}
    (directory / 'build-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-root', required=True)
    args = parser.parse_args()
    result = build(args.output_root)
    print(json.dumps({key: result[key] for key in ('archive', 'version', 'sha256')}, indent=2))
