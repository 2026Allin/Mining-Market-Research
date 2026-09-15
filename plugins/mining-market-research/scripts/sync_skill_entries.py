#!/usr/bin/env python3
"""Render minimal business execution gates from one source, never at runtime.

Run --write after changing templates/business-entry.md. CI/release checks reject
drift; Claude ZIP builds render in memory without changing the source tree.
Only generated regions are replaced; frontmatter and task-specific text survive.
"""
import argparse
from pathlib import Path
import sys

sys.dont_write_bytecode = True
PLUGIN = Path(__file__).resolve().parents[1]
SKILLS = ('company-brief', 'company-comparison', 'company-report', 'market-analysis', 'news-analysis')
START = '<!-- BEGIN GENERATED BUSINESS ENTRY -->'
END = '<!-- END GENERATED BUSINESS ENTRY -->'


def render(text, template, workflow):
    if text.count(START) != 1 or text.count(END) != 1:
        raise ValueError('missing or duplicate generated entry markers: ' + workflow)
    before, rest = text.split(START)
    _, after = rest.split(END)
    if END in before or START in after:
        raise ValueError('invalid generated entry markers')
    block = template.replace('{workflow}', workflow).strip()
    return before + START + '\n' + block + '\n' + END + after


def render_payload(payload, template):
    result = dict(payload)
    for name in SKILLS:
        key = f'skills/{name}/SKILL.md'
        result[key] = render(result[key].decode('utf-8'), template, name).encode('utf-8')
    return result


def sync(plugin=PLUGIN, *, write=False):
    plugin = Path(plugin)
    template = (plugin / 'scripts/templates/business-entry.md').read_text()
    # Validate all targets before writing any, so malformed markers fail cleanly.
    changes = []
    for name in SKILLS:
        path = plugin / 'skills' / name / 'SKILL.md'
        if path.is_symlink():
            raise ValueError('symlink skill entry')
        original = path.read_text()
        expected = render(original, template, name)
        if original != expected:
            changes.append((path, expected))
    if changes and not write:
        raise ValueError('generated Skill entries are out of sync; run sync_skill_entries.py --write')
    for path, expected in changes:
        path.write_text(expected)
    return len(changes)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.write and args.check:
        parser.error('choose --write or --check')
    try:
        count = sync(write=args.write)
        print(f'business entries synchronized: {len(SKILLS)} skills, {count} changed')
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
