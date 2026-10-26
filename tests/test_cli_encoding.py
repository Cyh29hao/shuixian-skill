"""Black-box UTF-8 output checks under a deliberately legacy Windows encoding."""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CliEncodingTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='shuixian-cli-encoding-')
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name) / '镜像 练习'

    def run_cli(self, filename, *arguments):
        result = subprocess.run(
            [sys.executable, str(ROOT / 'tools' / filename), *map(str, arguments)],
            capture_output=True,
            env={**os.environ, 'PYTHONIOENCODING':'cp936'},
        )
        return result.returncode, result.stdout.decode('utf-8'), result.stderr.decode('utf-8')

    def test_create_list_and_duplicate_error_are_utf8(self):
        arguments = ('--preset','close-friend-same-form','--slug','encoding-trial',
                     '--name','慢慢来 🪷','--base-dir',self.base)
        code, out, err = self.run_cli('demo_builder.py', *arguments)
        self.assertEqual(code, 0, err)
        target = self.base / 'shuixian-encoding-trial'
        self.assertIn(str(target), out)
        before = {p.relative_to(target):p.read_bytes() for p in target.rglob('*') if p.is_file()}
        code, out, err = self.run_cli('skill_writer.py','--action','list','--base-dir',self.base)
        self.assertEqual(code, 0, err)
        self.assertIn('慢慢来 🪷', out)
        code, out, err = self.run_cli('demo_builder.py', *arguments)
        self.assertNotEqual(code, 0)
        self.assertIn(str(target), err)
        self.assertEqual(before, {p.relative_to(target):p.read_bytes() for p in target.rglob('*') if p.is_file()})

    def test_version_error_preserves_chinese_path(self):
        code, out, err = self.run_cli('version_manager.py','--action','list','--slug','absent','--base-dir',self.base)
        self.assertNotEqual(code, 0)
        self.assertIn(str(self.base / 'shuixian-absent'), err)

    def test_import_profile_and_source_archive_report_unicode_paths(self):
        self.base.mkdir(parents=True)
        source = self.base / 'chosen.txt'
        source.write_text('[unknown-time] me: hello\n', encoding='utf-8')
        original = source.read_bytes()
        destinations = [
            ('transcript_importer.py', self.base / '转录 🪷.txt', '--output'),
            ('mirror_profiler.py', self.base / '画像 🪷.md', '--output'),
            ('source_importer.py', self.base / '归档 🪷', '--skill-dir'),
        ]
        for script, destination, flag in destinations:
            with self.subTest(script=script):
                code, out, err = self.run_cli(script, '--input', source, flag, destination)
                self.assertEqual(code, 0, err)
                self.assertIn(str(destination), out)
                self.assertTrue(destination.exists())
                self.assertEqual(source.read_bytes(), original)

    @unittest.skipUnless(importlib.util.find_spec('PIL'), 'Artwork uses optional Pillow')
    def test_artwork_cli_reports_unicode_destination(self):
        code, out, err = self.run_cli('render_readme_pngs.py','--runtime-only','--output-dir',self.base)
        self.assertEqual(code, 0, err)
        self.assertIn(str(self.base / 'runtime-dialogue-v1.png'), out)
        self.assertTrue((self.base / 'runtime-dialogue-mobile-v1.png').is_file())


if __name__ == '__main__':
    unittest.main()
