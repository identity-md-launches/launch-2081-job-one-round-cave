#!/usr/bin/env python3
"""Reverify block-bound receipts and audit their whole corpus before searching."""
import argparse
import json
from pathlib import Path
import sys

import anchor
import freshness
import proof_search

engine = freshness.engine
HERE = Path(__file__).resolve().parent


def documents(report):
    """Only cryptographically checked fields enter the two searchable documents."""
    state = dict(report['state'], trust=report['trust'])
    state['trust'] += ' Supplied block hash: ' + report['anchor']['blockHash']
    header = report['anchor']
    return {
        'receipt.md': proof_search.receipt(state),
        'anchor.md': '\n'.join([
            '# Execution header commitment',
            'Supplied block hash: ' + header['blockHash'],
            'Committed state root: ' + header['stateRoot'],
            'Block number: ' + header['blockNumber'],
            'Timestamp: ' + header['timestamp'],
            'Header encoding: ' + header['headerSchema'],
            'Trust: ' + report['trust'],
        ]) + '\n',
    }


def prepare(header_path, bundle_path, block_hash, address, slots, destination):
    header = anchor.load_header(engine.workspace_path(header_path))
    bundle = anchor.w.load_bundle(engine.workspace_path(bundle_path))
    report = anchor.verify(header, bundle, block_hash, address, slots)
    texts = documents(report)
    target = engine.workspace_path(destination)
    # Verify before writing; exclusive directory creation protects existing data.
    target.mkdir()
    for name, text in texts.items():
        (target / name).write_text(text, encoding='utf-8')
    # Preserve proof material for re-verification; discard all unproven labels.
    for name, value in [('header.json', header),
                        ('witness.json', {'format': 'state-witness/1', 'proof': bundle['proof']})]:
        (target / name).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
    engine.write_index(target / 'index.json', engine.build_index(target))
    return report


def query(directory, text, block_hash, address, slots, limit=5, require_all=False):
    root = engine.workspace_path(directory)
    # Never infer caller expectations from a receipt, index, header, or witness.
    header = anchor.load_header(engine.workspace_path(root / 'header.json'))
    bundle = anchor.w.load_bundle(engine.workspace_path(root / 'witness.json'))
    report = anchor.verify(header, bundle, block_hash, address, slots)
    index = engine.load_index(root / 'index.json')
    audit = freshness.audit(index, root)
    envelope = {'format': 'anchored-proof-search/v1', 'verification': report,
                'freshness': audit, 'search': None}
    if not audit['fresh']:
        return envelope
    expected = documents(report)
    # A forged receipt AND a matching forged index must not become proof evidence.
    actual = {doc['path']: doc['text'] for doc in index['documents']}
    if actual != expected:
        raise ValueError('receipt corpus does not match the reverified proof')
    envelope['search'] = engine.search(index, text, root, limit, require_all)
    return envelope


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    demo = sub.add_parser('demo', help='read-only historical ZTO/IMD pool example')
    demo.add_argument('text', nargs='?', default='Slot Value')
    make = sub.add_parser('prepare', help='create a new receipt directory')
    make.add_argument('header')
    make.add_argument('witness')
    make.add_argument('--output', required=True)
    find = sub.add_parser('query', help='reverify and search an unchanged receipt corpus')
    find.add_argument('directory')
    find.add_argument('text')
    find.add_argument('--limit', type=int, default=5)
    find.add_argument('--all', action='store_true')
    for command in (make, find):
        command.add_argument('--block-hash', required=True)
        command.add_argument('--address', required=True)
        command.add_argument('--slot', action='append', default=[])
    args = parser.parse_args(argv)
    try:
        if args.command == 'prepare':
            result = prepare(args.header, args.witness, args.block_hash,
                             args.address, args.slot, args.output)
            status = 0
        elif args.command == 'demo':
            result = query(HERE / 'examples' / 'anchored-receipt', args.text,
                           anchor.DEMO_HASH, anchor.w.POOL_MANAGER, [anchor.POOL_SLOT])
            result['demo'] = 'Historical RPC observation, not an independently authenticated checkpoint.'
            status = 0 if result['search'] and result['search']['hits'] else 1
        else:
            result = query(args.directory, args.text, args.block_hash,
                           args.address, args.slot, args.limit, args.all)
            status = 0 if result['search'] and result['search']['hits'] else 1
        print(json.dumps(result, indent=2, sort_keys=True))
        return status
    except (ValueError, OSError, KeyError, TypeError, RecursionError):
        print(json.dumps({'error': 'Invalid proof, checkpoint, receipt, corpus, or destination.'}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
