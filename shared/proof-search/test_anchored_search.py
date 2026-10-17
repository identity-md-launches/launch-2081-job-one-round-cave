"""Offline end-to-end tests with the inherited real ZTO/IMD pool witness."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

import anchored_search as a


class AnchoredSearch(unittest.TestCase):
    def setUp(self):
        scratch = Path('test/scratch')
        scratch.mkdir(parents=True, exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.output = self.root / 'receipt'
        self.header = a.HERE / 'zto-header-mainnet.json'
        self.bundle = a.HERE / 'zto-pool-mainnet.json'
        self.hash = a.anchor.DEMO_HASH
        self.address = a.anchor.w.POOL_MANAGER
        self.slots = [a.anchor.POOL_SLOT]

    def prepare(self, **kw):
        return a.prepare(kw.get('header', self.header), kw.get('bundle', self.bundle),
                         kw.get('block_hash', self.hash), kw.get('address', self.address),
                         kw.get('slots', self.slots), self.output)

    def query(self, text='Slot Value', **kw):
        return a.query(self.output, text, kw.get('block_hash', self.hash),
                       kw.get('address', self.address), kw.get('slots', self.slots))

    def test_real_proof_citations_and_input_immutability(self):
        before = [p.read_bytes() for p in (self.header, self.bundle)]
        self.prepare()
        result = self.query()
        self.assertTrue(result['verification']['verified'])
        self.assertTrue(result['freshness']['fresh'])
        self.assertEqual(result['freshness']['indexed_documents'], 2)
        hit = result['search']['hits'][0]
        self.assertEqual(hit['path'], 'receipt.md')
        self.assertIn(self.slots[0], hit['text'])
        self.assertIn('0x30d400000001b32f000000000000010675ff9d949ea2d3c11613bc41', hit['text'])
        lines = (self.output / hit['path']).read_text().splitlines()
        self.assertEqual(hit['text'], '\n'.join(lines[hit['line_start']-1:hit['line_end']]))
        self.assertEqual(before, [p.read_bytes() for p in (self.header, self.bundle)])

    def test_wrong_checkpoint_address_and_slots_write_nothing(self):
        for kw in ({'block_hash': '0x' + '12' * 32}, {'address': a.anchor.w.ZTO},
                   {'slots': []}, {'slots': self.slots * 2}):
            with self.subTest(kw=kw), self.assertRaises(ValueError):
                self.prepare(**kw)
            self.assertFalse(self.output.exists())

    def test_tampered_proof_writes_nothing(self):
        bundle = json.loads(self.bundle.read_text())
        bundle['proof']['storageProof'][0]['value'] = '0x1'
        path = self.root / 'bad.json'
        path.write_text(json.dumps(bundle))
        with self.assertRaises(ValueError):
            self.prepare(bundle=path)
        self.assertFalse(self.output.exists())

    def test_metadata_never_enters_receipts_or_saved_witness(self):
        bundle = json.loads(self.bundle.read_text())
        bundle.update(block={'number': 'invented'}, label='invented', chainId='invented')
        path = self.root / 'labels.json'
        path.write_text(json.dumps(bundle))
        self.prepare(bundle=path)
        for file in self.output.iterdir():
            self.assertNotIn('invented', file.read_text())
        self.assertTrue(self.query()['verification']['verified'])

    def test_uncited_change_blocks_search(self):
        self.prepare()
        with (self.output / 'anchor.md').open('a') as stream:
            stream.write('unrelated added statement\n')
        result = self.query()
        self.assertIsNone(result['search'])
        self.assertEqual(result['freshness']['changed'], ['anchor.md'])

    def test_added_removed_and_no_match(self):
        self.prepare()
        self.assertEqual(self.query('absentword')['search']['hits'], [])
        (self.output / 'new.md').write_text('new document')
        (self.output / 'anchor.md').unlink()
        result = self.query()
        self.assertIsNone(result['search'])
        self.assertEqual(result['freshness']['added'], ['new.md'])
        self.assertEqual(result['freshness']['removed'], ['anchor.md'])

    def test_forged_receipt_and_matching_index_rejected(self):
        self.prepare()
        (self.output / 'receipt.md').write_text('Slot Value fabricated\n')
        (self.output / 'index.json').unlink()
        a.engine.write_index(self.output / 'index.json', a.engine.build_index(self.output))
        with self.assertRaisesRegex(ValueError, 'reverified proof'):
            self.query()

    def test_saved_proof_reverified_and_query_anchor_required(self):
        self.prepare()
        for kw in ({'block_hash': None}, {'block_hash': '0x' + '12' * 32}, {'slots': []}):
            with self.assertRaises(ValueError):
                self.query(**kw)
        path = self.output / 'witness.json'
        bundle = json.loads(path.read_text())
        bundle['proof']['storageProof'][0]['value'] = '0x1'
        path.write_text(json.dumps(bundle))
        with self.assertRaises(ValueError):
            self.query()

    def test_existing_output_and_symlinks_rejected(self):
        self.prepare()
        before = {p.name: p.read_bytes() for p in self.output.iterdir()}
        with self.assertRaises(FileExistsError):
            self.prepare()
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.output.iterdir()})
        link = self.root / 'link.json'
        link.symlink_to(self.header)
        with self.assertRaises(ValueError):
            self.prepare(header=link)
        with self.assertRaises(ValueError):
            a.query('../outside', 'Slot', self.hash, self.address, self.slots)

    def test_cli_demo_read_only_and_errors(self):
        before = {p: p.read_bytes() for p in (a.HERE / 'examples' / 'anchored-receipt').iterdir()}
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(a.main(['demo']), 0)
        self.assertTrue(json.loads(out.getvalue())['verification']['verified'])
        self.assertEqual(before, {p: p.read_bytes() for p in before})
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(a.main(['demo', 'absentword']), 1)
        with contextlib.redirect_stderr(io.StringIO()) as err, contextlib.redirect_stdout(io.StringIO()) as out:
            status = a.main(['query', str(self.root / 'missing'), 'Slot',
                             '--block-hash', self.hash, '--address', self.address])
        self.assertEqual(status, 2)
        self.assertEqual(out.getvalue(), '')
        self.assertIn('error', json.loads(err.getvalue()))


if __name__ == '__main__':
    unittest.main()
