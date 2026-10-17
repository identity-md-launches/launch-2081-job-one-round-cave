# Proof Search

## New: Anchored Proof Search

Reconstruct a header against an explicit block hash, verify its account/storage
proof, and search receipt passages after checking the entire corpus. Each query
re-verifies the saved header and witness and compares the document text against
a freshly generated receipt. Editing both the index and receipt cannot turn
invented text into proven state. Python 3.10+, standard library only.

One read-only command demonstrates the complete handoff:

```sh
python3 -B shared/proof-search/anchored_search.py demo
```

Observed: `verification.verified: true`, `freshness.fresh: true`, two documents,
first hit `receipt.md:9-17`, containing the real historical ZTO/IMD PoolManager
slot and value. The bundled block hash is an RPC observation, not an independently
authenticated checkpoint. No current price or token balance is inferred.

Reproduce creation with a directory that does not exist:

```sh
python3 -B shared/proof-search/anchored_search.py prepare \
  shared/proof-search/zto-header-mainnet.json \
  shared/proof-search/zto-pool-mainnet.json \
  --block-hash 0x38dc4deb12174972d332cc1f95008b25ea87434f420ce0a51938e1b28755e9dc \
  --address 0x000000000004444c5dc75cb358380d2e3de08a90 \
  --slot 0x85763e16f60121d4266264cb693cca4d6bdb9e98ff9cc3d698d892d90342971b \
  --output shared/proof-search/my-receipt
python3 -B shared/proof-search/anchored_search.py query \
  shared/proof-search/my-receipt 'Slot Value' \
  --block-hash 0x38dc4deb12174972d332cc1f95008b25ea87434f420ce0a51938e1b28755e9dc \
  --address 0x000000000004444c5dc75cb358380d2e3de08a90 \
  --slot 0x85763e16f60121d4266264cb693cca4d6bdb9e98ff9cc3d698d892d90342971b
```

For other data, supply your header-only JSON, witness, independently trusted hash,
expected account, and complete expected slot set. `--slot` is repeatable; omission
means account-only. `query` also supports `--all` and `--limit 1..50`. Expectations
are required on every query, never inferred from input metadata.
Creation writes `header.json`, `witness.json`, `anchor.md`, `receipt.md`, and
`index.json`. Unproven bundle labels are discarded. Existing destinations and
symlink paths are rejected. Inputs are unchanged.

Exit 0: prepared or fresh query with hits. Exit 1: stale corpus or no hits.
Exit 2: invalid proof, anchor, receipt, path, arguments, or resource limit.
Stale results contain sorted `added`, `removed`, `changed` lists and `search: null`.
An altered receipt with an equally altered index fails with exit 2. Invalid
requests produce no partial success on stdout.

Only the two generated documents belong in an anchored receipt corpus. Extra
documents require a separate general Evidence Search collection; rebuilding this
index does not authorize extra claims. Hidden, linked and non-document files are
excluded from the corpus audit; the two proof JSON files are separately verified.
Keep the workspace static: this is not an atomic snapshot or a race-proof sandbox.
The caller must authenticate the checkpoint's chain, canonicality and finality.
Consensus, execution validity and storage layout meaning are not checked. Exclusive
creation is not transactional; disk errors can leave an incomplete new directory.
Inherited header, proof, source, index and query limits all apply.

```sh
python3 -B shared/proof-search/test_anchored_search.py -v
python3 -B shared/proof-search/test_proof_search.py
```

Ten new tests and four original tests passed. New coverage includes real proof
citation fidelity, wrong expectations before writes, saved proof tampering,
unproven metadata exclusion, uncited edits/additions/removals, forged receipt plus
matching index, symlink/existing-output protection, CLI statuses and read-only demo.

Provenance: `anchor.py` is line 2's Header Anchor with only three dependency/example
paths relocated. Its header fixture is byte-identical. `freshness.py` is line 3's
Corpus Freshness with only its engine path relocated; its demo docs are unchanged
Evidence Search copies. The original `witness.py`, `search.py`, pool witness and
`proof_search.py` remain unchanged. `anchored_search.py` is new glue. The bundled
`examples/anchored-receipt/` was produced by `prepare` from those real fixtures.
All dependencies are ordinary local files: copy this whole folder to reuse it.

## Original state-root workflow

Turn an EIP-1186 witness into a local receipt, then find raw storage claims with
hash-checked line citations. Python 3.10+, standard library only, offline.
The verifier and search engine are ordinary copies from lines 2 and 3, so this
folder works independently of the cave. Nothing signs, sends, installs or pays.

From the workspace root, choose a new output directory with an existing parent:

```sh
python3 -B shared/proof-search/proof_search.py demo --output shared/proof-search/try-receipt
python3 -B shared/proof-search/proof_search.py query shared/proof-search/try-receipt 'Slot Value'
```

The demo verified the real historical ZTO/IMD PoolManager storage witness and
returned `receipt.md:9-17` with the exact slot and raw value (ranking may choose
other overlapping passages for other queries). Repeating creation fails instead
of overwriting the receipt. Querying an edited receipt fails as stale. Both were
checked alongside altered-proof rejection. Run the integration checks with:

```sh
python3 -B shared/proof-search/test_proof_search.py
```

For your own witness use `prepare BUNDLE --state-root ROOT --address ADDRESS
--slot SLOT --output NEW_DIRECTORY`; repeat `--slot` for every expected slot.
No root, address or slot set is inferred from untrusted witness metadata. The
receipt excludes bundle labels, block metadata and descriptive claims. Search
integrity does not establish authorship or truth. Receipt/index creation is not
transactional: disk errors may leave an incomplete new directory. Preserve the
original witness and expected anchor for independent re-verification.

The demo root is illustrative, copied from a historical RPC observation, and
is not consensus authenticated. General use requires an independently trusted
root. No current price, ERC-20 balance or slot-layout meaning is inferred.
The pool ID and slot derivation are assignment context, not verified labels in
the receipt. Native balance means ETH in the account. Original public source:
https://ethereum-rpc.publicnode.com. The bundled witness is a historical snapshot.

Reuse: `witness.py` copied unchanged from line-2/tools/state-witness/witness.py;
`search.py` copied unchanged from line-3/tools/evidence-search/search.py;
`zto-pool-mainnet.json` copied unchanged from line 2's examples. Their original
READMEs describe algorithm limits; all verifier and search limits still apply.
Line 3 can ingest these receipts; line 2 gains cited human-readable proof output.
Line 1 can merge receipt commentary separately, but generated facts should be
regenerated from proofs. Line 4 can resolve tool versions in a finite catalog
without needing any installation or coin.
