"""Real Ethereum headers, real storage witness, and adversarial bindings."""
import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import unittest
from unittest import mock

spec = importlib.util.spec_from_file_location('anchor', Path(__file__).with_name('anchor.py'))
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)


class HeaderAnchor(unittest.TestCase):
    def setUp(self):
        self.header = a.load_header(a.HERE / 'examples' / 'zto-header-mainnet.json')
        self.bundle = a.w.load_bundle(a.HERE.parent / 'state-witness' / 'examples' / 'zto-pool-mainnet.json')

    def check(self, header=None, bundle=None, **kwargs):
        return a.verify(self.header if header is None else header,
                        self.bundle if bundle is None else bundle,
                        kwargs.get('block_hash', a.DEMO_HASH),
                        kwargs.get('address', a.w.POOL_MANAGER),
                        kwargs.get('slots', [a.POOL_SLOT]))

    def test_real_pool_header_and_storage(self):
        result = self.check()
        self.assertTrue(result['verified'])
        self.assertEqual(result['anchor']['blockHash'], a.DEMO_HASH)
        self.assertEqual(result['anchor']['stateRoot'], a.w.DEMO_ROOT)
        self.assertEqual(result['state']['storage'][0]['value'],
                         '0x30d400000001b32f000000000000010675ff9d949ea2d3c11613bc41')

    def test_all_supported_schemas_against_real_mainnet_hashes(self):
        hashes = {
            'legacy': '0xd4e56740f876aef8c010b86a40d5f56745a118d0906a34e69aec8c0db1cb8fa3',
            'london': '0x9b83c12c69edb74f6c8dd5d052765c1adf940e320bd1291696e6fa07829eee71',
            'shanghai': '0xe22c56f211f03baadcc91e4eb9a24344e6848c5df4473988f893b58223f5216c',
            'cancun': '0xa2917e0758c98640d868182838c93bb12f0d07b6b17efe6b62d9df42c7643791',
        }
        for schema, trusted in hashes.items():
            with self.subTest(schema=schema):
                h = a.load_header(a.HERE / 'examples' / ('header-' + schema + '.json'))
                self.assertEqual(a.verify_header(h, trusted)['headerSchema'], schema)

    def test_every_committed_field_is_bound(self):
        for name, size in a.BASE + a.TAIL:
            with self.subTest(field=name), self.assertRaises(a.w.Invalid):
                header = copy.deepcopy(self.header)
                if size is None:
                    header[name] = hex(int(header[name], 16) + 1)
                else:
                    raw = bytearray(a.w.hex_data(header[name]))
                    if raw:
                        raw[-1] ^= 1
                    else:
                        raw.append(1)
                    header[name] = a.w.hex0(raw)
                self.check(header=header)

    def test_claimed_hash_cannot_replace_actual_hash(self):
        header = dict(self.header, stateRoot='0x' + '12' * 32)
        with self.assertRaises(a.w.Invalid):
            self.check(header=header)
        header = dict(self.header, hash='0x' + '12' * 32)
        with self.assertRaises(a.w.Invalid):
            self.check(header=header)

    def test_rpc_hash_is_optional_but_anchor_is_required(self):
        header = dict(self.header)
        del header['hash']
        self.assertTrue(self.check(header=header)['verified'])
        with self.assertRaises(a.w.Invalid):
            self.check(block_hash=None)

    def test_every_missing_field_fails_against_fixed_hash(self):
        for name, _ in a.BASE + a.TAIL:
            with self.subTest(field=name), self.assertRaises(a.w.Invalid):
                header = dict(self.header)
                del header[name]
                self.check(header=header)

    def test_unsupported_suffixes_and_new_fields_fail_closed(self):
        for count in (3, 4):
            with self.subTest(count=count), self.assertRaises(a.w.Invalid):
                a.encode_header({k: self.header[k] for k, _ in a.BASE + a.TAIL[:count]})
        with self.assertRaises(a.w.Invalid):
            a.encode_header(dict(self.header, blockAccessListHash='0x' + '12' * 32))

    def test_data_lengths_and_canonical_quantities(self):
        cases = [('number', '0x00'), ('difficulty', True), ('gasUsed', '0x' + 'f' * 65),
                 ('logsBloom', '0x00'), ('nonce', '0x0'), ('extraData', '0x' + '12' * 33),
                 ('stateRoot', '0x' + '12' * 31), ('miner', '0x' + '12' * 21)]
        for name, value in cases:
            with self.subTest(field=name, value=value), self.assertRaises(a.w.Invalid):
                a.encode_header(dict(self.header, **{name: value}))

    def test_zero_is_rlp_empty_and_nonce_remains_eight_bytes(self):
        raw, schema = a.encode_header(self.header)
        fields = a.w.rlp_decode(raw)
        self.assertEqual(schema, 'prague')
        self.assertEqual(fields[7], b'')
        self.assertEqual(fields[14], bytes(8))

    def test_proof_tamper_and_wrong_caller_expectations(self):
        bundle = copy.deepcopy(self.bundle)
        bundle['proof']['storageProof'][0]['value'] = '0x1'
        with self.assertRaises(a.w.Invalid):
            self.check(bundle=bundle)
        for options in ({'address': a.w.ZTO}, {'slots': []}, {'slots': ['0x1']},
                        {'slots': [a.POOL_SLOT, a.POOL_SLOT]}):
            with self.subTest(options=options), self.assertRaises(a.w.Invalid):
                self.check(**options)

    def test_unproven_bundle_labels_are_not_reported(self):
        bundle = copy.deepcopy(self.bundle)
        bundle['block'] = {'hash': 'forged', 'number': 'forged', 'stateRoot': 'forged'}
        bundle['source'] = 'forged'
        bundle['chainId'] = 'forged'
        bundle['address'] = 'forged'
        bundle['slots'] = ['forged']
        result = self.check(bundle=bundle)
        self.assertNotIn('forged', json.dumps(result))
        self.assertNotIn('chainId', result['anchor'])

    def test_other_real_account_can_use_same_header(self):
        bundle = a.w.load_bundle(a.HERE.parent / 'state-witness' / 'examples' / 'zto-mainnet.json')
        result = self.check(bundle=bundle, address=a.w.ZTO, slots=['0x0', '0x1'])
        self.assertTrue(result['state']['accountExists'])
        self.assertFalse(result['state']['storage'][0]['exists'])

    def test_json_duplicates_size_and_workspace_boundary(self):
        with self.assertRaises(a.w.Invalid):
            a.w.parse_json('{"stateRoot": 1, "stateRoot": 2}')
        with mock.patch.object(a.w, 'workspace_path') as path:
            path.return_value.open.return_value.__enter__.return_value.read.return_value = b' ' * 65_537
            with self.assertRaises(a.w.Invalid):
                a.load_header('unused')
        with self.assertRaises(a.w.Invalid):
            a.w.workspace_path(Path.cwd().parent / 'outside.json')

    def test_cli_success_and_failure_statuses(self):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(a.main(['demo']), 0)
        self.assertTrue(json.loads(output.getvalue())['verified'])
        with contextlib.redirect_stderr(io.StringIO()) as error:
            self.assertEqual(a.main(['verify', str(a.HERE / 'examples' / 'zto-header-mainnet.json'),
                                     str(a.HERE.parent / 'state-witness' / 'examples' / 'zto-pool-mainnet.json'),
                                     '--block-hash', '0x' + '12' * 32,
                                     '--address', a.w.POOL_MANAGER, '--slot', a.POOL_SLOT]), 1)
        self.assertFalse(json.loads(error.getvalue())['verified'])


if __name__ == '__main__':
    unittest.main()
