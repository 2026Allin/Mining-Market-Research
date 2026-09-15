"""Build-time rendering contracts, not claims about model compliance."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest
import zipfile
from test_update_optimization import load

entries = load('sync_skill_entries')
builder = load('build_test_package')


class GeneratedEntryTest(unittest.TestCase):
    def test_source_is_synchronized(self):
        self.assertEqual(entries.sync(), 0)

    def test_idempotence_and_preservation(self):
        template = (entries.PLUGIN / 'scripts/templates/business-entry.md').read_text()
        for name in entries.SKILLS:
            source = (entries.PLUGIN / f'skills/{name}/SKILL.md').read_text()
            result = entries.render(source, template, name)
            self.assertEqual(result, source)
            self.assertEqual(entries.render(result, template, name), result)
            altered = entries.render(source, template + '\nNew shared rule.\n', name)
            self.assertEqual(altered.split(entries.START)[0], source.split(entries.START)[0])
            self.assertEqual(altered.split(entries.END)[1], source.split(entries.END)[1])
            self.assertLess(altered.index('Initialize only'), altered.index('Perform the business'))

    def test_malformed_markers_fail_without_partial_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'plugin'
            shutil.copytree(entries.PLUGIN, root)
            first = root / f'skills/{entries.SKILLS[0]}/SKILL.md'
            first.write_text(first.read_text().replace('Initialize only', 'STALE'))
            last = root / f'skills/{entries.SKILLS[-1]}/SKILL.md'
            last.write_text(last.read_text().replace(entries.END, ''))
            before = first.read_bytes()
            with self.assertRaises(ValueError):
                entries.sync(root, write=True)
            self.assertEqual(first.read_bytes(), before)

    def test_drift_is_rejected_and_write_restores_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'plugin'
            shutil.copytree(entries.PLUGIN, root)
            path = root / 'skills/news-analysis/SKILL.md'
            path.write_text(path.read_text().replace('Never ack before sending.', 'Ack before sending.'))
            with self.assertRaisesRegex(ValueError, 'out of sync'):
                entries.sync(root)
            self.assertEqual(entries.sync(root, write=True), 1)
            self.assertEqual(entries.sync(root), 0)

    def test_zip_renders_stale_source_without_mutating_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'plugin'
            shutil.copytree(entries.PLUGIN, root)
            path = root / 'skills/news-analysis/SKILL.md'
            path.write_text(path.read_text().replace('Never ack before sending.', 'STALE'))
            before = path.read_bytes()
            receipt = builder.build(Path(tmp) / 'out', plugin=root)
            with zipfile.ZipFile(receipt['archive']) as archive:
                data = {name: archive.read(name) for name in archive.namelist()}
            self.assertEqual(path.read_bytes(), before)
            self.assertIn(b'Never ack before sending.', data['skills/news-analysis/SKILL.md'])
            builder.validate_payload(data)
            data['skills/news-analysis/SKILL.md'] = before
            with self.assertRaisesRegex(ValueError, 'entry mismatch'):
                builder.validate_payload(data)

    def test_operational_skills_not_wrapped(self):
        for name in ('upgrade', 'mining-market-research'):
            self.assertNotIn(entries.START, (entries.PLUGIN / f'skills/{name}/SKILL.md').read_text())
