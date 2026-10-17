"""Behavior checks. Temporary corpora live only in test/scratch/."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import freshness as tool


class FreshnessTests(unittest.TestCase):
    def setUp(self):
        scratch = Path.cwd() / 'test' / 'scratch'
        scratch.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.docs = self.root / 'docs'
        self.docs.mkdir()
        self.write('zto.md', 'ZTO decimals 18\r\n')
        self.write('unrelated.txt', 'Other material\n')
        self.index = tool.engine.build_index(self.docs)

    def write(self, name, value):
        path = self.docs / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(value.encode())
        return path

    def test_unchanged_citations_and_no_writes(self):
        before = {p: p.read_bytes() for p in self.docs.iterdir()}
        result = tool.checked_query(self.index, self.docs, 'ZTO decimals', require_all=True)
        self.assertTrue(result['freshness']['fresh'])
        hit = result['search']['hits'][0]
        self.assertEqual(hit['citation'], 'zto.md:1-1')
        self.assertEqual(hit['text'], 'ZTO decimals 18')
        self.assertEqual(before, {p: p.read_bytes() for p in self.docs.iterdir()})

    def test_uncited_change_blocks_even_no_match_query(self):
        self.write('unrelated.txt', 'Changed unrelated material\n')
        for query in ('ZTO', 'notpresent'):
            with patch.object(tool.engine, 'search', side_effect=AssertionError('must not rank')):
                result = tool.checked_query(self.index, self.docs, query)
            self.assertIsNone(result['search'])
            self.assertEqual(result['freshness']['changed'], ['unrelated.txt'])

    def test_sorted_added_removed_changed_and_rename(self):
        self.write('nested/new.md', 'new evidence')
        self.write('a.rst', 'new evidence')
        (self.docs / 'unrelated.txt').rename(self.docs / 'renamed.txt')
        self.write('zto.md', 'ZTO changed')
        report = tool.audit(self.index, self.docs)
        self.assertEqual(report['added'], ['a.rst', 'nested/new.md', 'renamed.txt'])
        self.assertEqual(report['removed'], ['unrelated.txt'])
        self.assertEqual(report['changed'], ['zto.md'])
        self.assertFalse(report['fresh'])

    def test_same_length_same_mtime_change_detected(self):
        import os
        path = self.docs / 'zto.md'
        stat = path.stat()
        self.write('zto.md', 'ZTO decimals 06\r\n')
        os.utime(path, ns=(stat.st_atime_ns, stat.st_mtime_ns))
        self.assertEqual(tool.audit(self.index, self.docs)['changed'], ['zto.md'])

    def test_hidden_unsupported_and_symlink_additions_excluded(self):
        self.write('.hidden.md', 'ignored')
        self.write('.hidden/secret.txt', 'ignored')
        self.write('code.py', 'raise RuntimeError()')
        (self.docs / 'link.md').symlink_to(self.docs / 'zto.md')
        self.assertTrue(tool.audit(self.index, self.docs)['fresh'])

    def test_source_replaced_by_link_reported_removed(self):
        path = self.docs / 'zto.md'
        path.unlink()
        path.symlink_to(self.docs / 'unrelated.txt')
        report = tool.audit(self.index, self.docs)
        self.assertFalse(report['fresh'])
        self.assertEqual(report['removed'], ['zto.md'])

    def test_bad_utf8_and_budget_errors_never_fresh(self):
        self.write('bad.md', 'normal')
        (self.docs / 'bad.md').write_bytes(b'\xff')
        with self.assertRaises(tool.engine.SearchError):
            tool.audit(self.index, self.docs)
        (self.docs / 'bad.md').unlink()
        with patch.object(tool.engine, 'MAX_FILES', 1):
            with self.assertRaises(tool.engine.SearchError):
                tool.audit(self.index, self.docs)

    def test_forged_index_and_traversal_rejected(self):
        self.index['documents'][0]['text'] = 'forged'
        with self.assertRaises(tool.engine.SearchError):
            tool.audit(self.index, self.docs)
        with self.assertRaises(tool.engine.SearchError):
            tool.audit({'format': tool.engine.FORMAT, 'documents': []}, '../escape')

    def test_empty_corpus_and_order_independence(self):
        self.assertTrue(tool.compare(self.index, dict(self.index, documents=list(reversed(self.index['documents']))))['fresh'])
        for path in self.docs.iterdir():
            path.unlink()
        empty = tool.engine.build_index(self.docs)
        self.assertTrue(tool.audit(empty, self.docs)['fresh'])
        self.assertEqual(tool.checked_query(empty, self.docs, 'ZTO')['search']['hits'], [])

    def test_cli_statuses_reports_and_errors(self):
        filename = self.root / 'index.json'
        tool.engine.write_index(filename, self.index)
        def run(args):
            with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()) as err:
                status = tool.main(args)
            return status, out.getvalue(), err.getvalue()
        base = [str(self.docs), '--index', str(filename)]
        self.assertEqual(run(['check'] + base)[0], 0)
        self.assertEqual(run(['query'] + base + ['ZTO'])[0], 0)
        self.assertEqual(run(['query'] + base + ['missing'])[0], 1)
        self.assertEqual(run(['query'] + base + ['ZTO', '--limit', '0'])[0], 2)
        self.write('added.md', 'ZTO new')
        status, out, err = run(['query'] + base + ['ZTO'])
        self.assertEqual(status, 1)
        self.assertIsNone(json.loads(out)['search'])
        self.assertEqual(err, '')
        self.assertEqual(run(['check'] + base)[0], 1)
        (self.docs / 'bad.md').write_bytes(b'\xff')
        status, out, err = run(['check'] + base)
        self.assertEqual(status, 2)
        self.assertEqual(out, '')
        self.assertIn('UTF-8', json.loads(err)['error'])


if __name__ == '__main__':
    unittest.main()
