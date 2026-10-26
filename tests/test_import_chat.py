"""User-facing import checks with isolated synthetic files and actual CLI runs."""
from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT/'tools/import_chat.py'


class GuidedImportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='shuixian-guided-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)/'中文 语料'
        self.root.mkdir()
        self.output = self.root/'新结果'

    def cli(self, *args):
        return subprocess.run([sys.executable, '-B', '-X', 'utf8', str(TOOL), *map(str,args)],
            capture_output=True, text=True, encoding='utf-8',
            env={**os.environ,'PYTHONIOENCODING':'cp936'}, timeout=30)

    def source(self, name='chosen.json', payload=None):
        path = self.root/name
        path.write_text(json.dumps(payload or [
            {'sender':'青禾','content':'终于改好了，先得意一下。'},
            {'sender':'阿遥','content':'你的人生光芒万丈，宝贝。'}],ensure_ascii=False),encoding='utf-8')
        return path

    def test_multi_format_directory_preserves_sources_and_self_attribution(self):
        a = self.source()
        b = self.root/'table.csv'
        b.write_text('\ufeff发送者,内容,时间\n青禾,"短句里有逗号,还有下一行\n是同一条",2026-10-27 10:00:00\n阿遥,表格对方,\n',encoding='utf-8')
        c = self.root/'telegram.json'
        c.write_text(json.dumps({'messages':[{'from':'青禾','text':['这句',{'type':'bold','text':'富文本'}],'date':'2026-10-27T11:00:00'}]},ensure_ascii=False),encoding='utf-8')
        d = self.root/'notes.jsonl'
        d.write_text('{"sender":"青禾","text":"JSONL一句"}\n',encoding='utf-8')
        (self.root/'image.png').write_bytes(b'not read')
        before={p:p.read_bytes() for p in (a,b,c,d)}
        result=self.cli(self.root,'--self-name','青禾','--output-dir',self.output)
        self.assertEqual(result.returncode,0,result.stderr)
        summary=json.loads((self.output/'summary.json').read_text(encoding='utf-8'))
        self.assertEqual(summary['message_count'],6)
        self.assertEqual(summary['self_message_count'],4)
        self.assertIn('未读取',result.stdout)
        profile=(self.output/'profile.md').read_text(encoding='utf-8')
        self.assertNotIn('光芒万丈',profile)
        self.assertIn('富文本',''.join(p.read_text(encoding='utf-8') for p in (self.output/'transcripts').glob('*')))
        self.assertTrue((self.output/'next-step.txt').is_file())
        self.assertEqual(before,{p:p.read_bytes() for p in before})

    def test_preview_needs_no_self_and_writes_nothing(self):
        source=self.source()
        before=set(self.root.iterdir())
        result=self.cli(source,'--preview')
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('青禾：1',result.stdout)
        self.assertEqual(before,set(self.root.iterdir()))

    def test_missing_or_wrong_self_writes_nothing(self):
        source=self.source()
        for options in ([],['--self-name','不存在']):
            with self.subTest(options=options):
                result=self.cli(source,*options,'--output-dir',self.output)
                self.assertNotEqual(result.returncode,0)
                self.assertFalse(self.output.exists())
                self.assertNotIn('Traceback',result.stderr)

    def test_unlabelled_notes_require_explicit_single_author(self):
        source=self.root/'日记.md'
        source.write_text('今天把事情说清楚了。\n先喝口水。\n',encoding='utf-8')
        original=source.read_bytes()
        refused=self.cli(source,'--self-name','青禾','--output-dir',self.output)
        self.assertNotEqual(refused.returncode,0)
        self.assertFalse(self.output.exists())
        allowed=self.cli(source,'--single-author','青禾','--output-dir',self.output)
        self.assertEqual(allowed.returncode,0,allowed.stderr)
        summary=json.loads((self.output/'summary.json').read_text(encoding='utf-8'))
        self.assertEqual(summary['self_message_count'],2)
        self.assertEqual(source.read_bytes(),original)

    def test_unknown_structured_sender_not_relabelled_as_diary(self):
        source=self.source(payload=[{'content':'未知作者'}])
        result=self.cli(source,'--single-author','青禾','--output-dir',self.output)
        self.assertNotEqual(result.returncode,0)
        self.assertFalse(self.output.exists())

    def test_bad_batch_and_existing_output_are_preserved(self):
        source=self.source()
        bad=self.root/'bad.json'
        bad.write_text('{oops',encoding='utf-8')
        result=self.cli(source,bad,'--self-name','青禾','--output-dir',self.output)
        self.assertNotEqual(result.returncode,0)
        self.assertFalse(self.output.exists())
        bad.unlink()
        self.output.mkdir()
        sentinel=self.output/'keep.txt'
        sentinel.write_bytes(b'keep')
        result=self.cli(source,'--self-name','青禾','--output-dir',self.output)
        self.assertNotEqual(result.returncode,0)
        self.assertEqual(list(self.output.iterdir()),[sentinel])
        self.assertEqual(sentinel.read_bytes(),b'keep')

    def test_tsv_and_aliases_no_implicit_user_sender(self):
        source=self.root/'chosen.tsv'
        source.write_text('sender\tcontent\nuser\tOTHER_ONLY\n青禾\t喜欢短句\n小青\t说完了\n',encoding='utf-8')
        result=self.cli(source,'--self-name','青禾','--self-name','小青','--output-dir',self.output)
        self.assertEqual(result.returncode,0,result.stderr)
        summary=json.loads((self.output/'summary.json').read_text(encoding='utf-8'))
        self.assertEqual(summary['self_message_count'],2)
        self.assertEqual(summary['message_count'],3)

    def test_linked_output_parent_is_refused(self):
        source=self.source()
        actual=self.root/'actual'
        actual.mkdir()
        alias=self.root/'alias'
        try:
            alias.symlink_to(actual,target_is_directory=True)
        except OSError:
            if os.name != 'nt':
                self.skipTest('Symlinks unavailable')
            made=subprocess.run(['cmd','/c','mklink','/J',str(alias),str(actual)],capture_output=True)
            if made.returncode:
                self.skipTest('Symlinks and junctions unavailable')
        result=self.cli(source,'--self-name','青禾','--output-dir',alias/'new')
        self.assertNotEqual(result.returncode,0)
        self.assertFalse((actual/'new').exists())

    def test_case_colliding_authors_are_not_silently_merged(self):
        source=self.source(payload=[{'sender':'Alice','content':'one'},{'sender':'alice','content':'two'}])
        result=self.cli(source,'--self-name','Alice','--output-dir',self.output)
        self.assertNotEqual(result.returncode,0)
        self.assertFalse(self.output.exists())


if __name__=='__main__':
    unittest.main()
