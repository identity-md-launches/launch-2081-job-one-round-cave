"""Offline checks. Run: python3 -B line-1/tools/merge-review/test_review.py"""
import hashlib
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest

from review import engine, packet, render, unified

SCRIPT = str(Path(__file__).with_name('review.py').resolve())


class ReviewTests(unittest.TestCase):
    def test_clean_preserves_both(self):
        report = packet('a\nb\nc\n', 'A\nb\nc\n', 'a\nb\nC\n')
        self.assertTrue(report['clean'])
        self.assertEqual(report['merged'], 'A\nb\nC\n')
        self.assertIn('+A\n', report['diffs']['ours'])
        self.assertIn('+C\n', report['diffs']['theirs'])
        self.assertEqual(report['conflicts'], [])

    def test_conflict_context_and_exact_fragments(self):
        report = packet('a\nb\nc\nd\ne\n', 'a\nb\nOURS\nd\ne\n', 'a\nb\nTHEIRS\nd\ne\n')
        self.assertFalse(report['clean'])
        conflict = report['conflicts'][0]
        self.assertEqual((conflict['base_start'], conflict['base_end']), (2, 3))
        self.assertEqual(conflict['context_before'], 'a\nb\n')
        self.assertEqual(conflict['context_after'], 'd\ne\n')
        self.assertEqual(conflict['base'], 'c\n')
        self.assertEqual(conflict['ours'], 'OURS\n')
        self.assertEqual(conflict['theirs'], 'THEIRS\n')
        self.assertIn('base lines 3..3', render(report))

    def test_insertion_location(self):
        report = packet('a\n', 'X\na\n', 'Y\na\n')
        self.assertIn('insertion after 0 base lines', render(report))
        self.assertEqual(report['conflicts'][0]['base'], '')

    def test_delete_modify(self):
        report = packet('a\nb\n', 'a\n', 'a\nB\n')
        self.assertEqual(report['conflicts'][0]['ours'], '')
        self.assertIn('-b\n', report['conflicts'][0]['ours_diff'])

    def test_two_conflicts_numbered(self):
        report = packet('a\nb\nc\n', 'A\nb\nC\n', 'X\nb\nZ\n')
        self.assertEqual([c['number'] for c in report['conflicts']], [1, 2])

    def test_hashes_exact_crlf_unicode(self):
        value = '🐸\r\nno-final-newline'
        report = packet(value, value, value)
        expected = hashlib.sha256(value.encode('utf-8')).hexdigest()
        self.assertEqual(report['inputs']['base']['sha256'], expected)
        self.assertEqual(report['inputs']['base']['bytes'], len(value.encode('utf-8')))
        self.assertEqual(report['merged_sha256'], expected)
        self.assertEqual(report['merged'], value)
        self.assertEqual(json.loads(json.dumps(report)), report)

    def test_newline_diagnostic(self):
        diff = unified('old', 'new', 'BASE', 'OURS')
        self.assertEqual(diff.count('\\ No newline at end of file'), 2)
        self.assertIn('-old\n\\ No newline', diff)
        self.assertIn('+new\n\\ No newline', diff)

    def test_terminal_controls_escaped(self):
        text = '\x1b[2J\n\t\r\u202e'
        report = packet('', text, '')
        display = render(report)
        self.assertNotIn('\x1b', display)
        self.assertNotIn('\u202e', display)
        self.assertIn('\\u001b', display)
        self.assertIn('\\u202e', display)
        self.assertEqual(report['merged'], text)

    def test_invalid_inputs(self):
        for value in ('\x00', 'x' * (engine.MAX_BYTES + 1), '\n' * (engine.MAX_LINES + 1)):
            with self.assertRaises(ValueError):
                packet('', value, '')

    def test_seeded_report_matches_engine(self):
        rng = random.Random(73722)
        for _ in range(200):
            texts = [''.join(rng.choice(['a\n', 'b\n', 'c\r\n', '🐸']) for _ in range(rng.randrange(12))) for _ in range(3)]
            report, original = packet(*texts), engine.merge(*texts)
            self.assertEqual(report['merged'], original['merged'])
            self.assertEqual(report['clean'], original['clean'])
            self.assertEqual([{k: c[k] for k in ('base_start', 'base_end', 'base', 'ours', 'theirs')}
                              for c in report['conflicts']], original['conflicts'])

    def test_cli_demos(self):
        for demo, status in [('clean', 0), ('conflict', 1)]:
            run = subprocess.run([sys.executable, '-B', SCRIPT, '--demo', demo, '--format', 'json'], capture_output=True)
            self.assertEqual(run.returncode, status, run.stderr)
            self.assertEqual(json.loads(run.stdout)['clean'], status == 0)

    def test_cli_real_inputs_unchanged_and_bad_utf8(self):
        scratch = Path('test/scratch')
        scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as folder:
            paths = [Path(folder) / name for name in ('base', 'ours', 'theirs')]
            values = [b'a\r\nb\r\n', b'A\r\nb\r\n', b'a\r\nB\r\n']
            for path, value in zip(paths, values):
                path.write_bytes(value)
            run = subprocess.run([sys.executable, '-B', SCRIPT, *map(str, paths), '--format', 'json'], capture_output=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(json.loads(run.stdout)['merged'], 'A\r\nB\r\n')
            self.assertEqual([p.read_bytes() for p in paths], values)
            paths[1].write_bytes(b'\xff')
            run = subprocess.run([sys.executable, '-B', SCRIPT, *map(str, paths)], capture_output=True)
            self.assertEqual(run.returncode, 2)
            self.assertEqual(run.stdout, b'')

    def test_bad_args(self):
        for args in ([], ['--demo', 'clean', 'extra']):
            run = subprocess.run([sys.executable, '-B', SCRIPT, *args], capture_output=True)
            self.assertEqual(run.returncode, 2)
            self.assertEqual(run.stdout, b'')


if __name__ == '__main__':
    unittest.main()
