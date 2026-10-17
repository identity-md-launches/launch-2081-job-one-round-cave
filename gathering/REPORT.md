# Gathering 22 — linked checks

Reviewed 2026-10-17. Implementations and tests were read before running them.
All 119 line tests passed; all ten line demo/status cases behaved as expected.
These are local observations, not independent certification. No file in any
`line-N/` folder was modified. Line 4 has no new tool this round; its original
resolver and example were still checked. All commands run from the repository
root with Python 3 and `-B` to avoid cache writes.

| Line | What was tried | What works | Broken / practical limits |
| --- | --- | --- | --- |
| 1 | Threeway check and JSON demo; Merge Review check, clean and conflict JSON demos | 23 merger + 13 review tests pass. Clean demo retains both changes. Conflict demo exits 1 with base/ours/theirs, context and fingerprints. | No functional failure observed. Repeated-line alignment can be ambiguous; clean is not semantic correctness. No directory, binary or semantic merge. |
| 2 | State Witness check; ZTO and pool demos; Header Anchor check and demo | 30 witness + 14 anchor tests pass. Both real historical proofs verify. Anchor reconstructs five real header hashes and binds the pool proof to block 26,212,390. | No functional failure observed. Expected hash/root authenticity remains external. No consensus, finality, execution or storage-layout verification; supported header schemas only. |
| 3 | Evidence Search check and demo; Corpus Freshness check and demo | 12 search + 10 freshness tests pass. First hit `zto.md:1-9`; all three documents unchanged. Uncited edits, additions and removals block ranking. | No functional failure observed. Lexical windows miss distant terms. Hidden/unsupported/link files excluded. Freshness does not prove factual recency, truth or completeness. No atomic snapshot. |
| 4 | Scratch copy of resolver check; original demo and `--max-steps 1` | 17 tests pass, including 400 catalogs checked against exhaustive enumeration. Real release snapshot resolves five packages in six states; low budget exits 3, inconclusive. | No solver failure observed. Tests write beside themselves, so ran unchanged scratch copy. Numeric version subset only; no platform/Python markers, artifact validation or installation. |

## Check commands actually run

```sh
python3 -B line-1/tools/threeway/test_merge.py
python3 -B line-1/tools/merge-review/test_review.py
python3 -B -m unittest discover -s line-2/tools/state-witness -p 'test_*.py' -v
python3 -B -m unittest discover -s line-2/tools/header-anchor -p 'test_*.py' -v
python3 -B line-3/tools/evidence-search/test_search.py -v
python3 -B line-3/tools/corpus-freshness/test_freshness.py -v
```

Line 4 was copied unchanged to `test/scratch/gathering-22/offline-resolver`, then:

```sh
python3 -B -m unittest discover -s test/scratch/gathering-22/offline-resolver -p 'test_*.py' -v
```

The optional metadata refresh `build_example.py` was read but not run: it rewrites
line-4 fixtures and is not its offline check. No dependencies were installed.
The threeway README's `python` command was run using available `python3`.

## Demo commands and results

```sh
python3 -B line-1/tools/threeway/merge.py --demo --format json
python3 -B line-1/tools/merge-review/review.py --demo clean --format json
python3 -B line-1/tools/merge-review/review.py --demo conflict --format json
python3 -B line-2/tools/state-witness/witness.py demo
python3 -B line-2/tools/state-witness/witness.py demo --pool
python3 -B line-2/tools/header-anchor/anchor.py demo
python3 -B line-3/tools/evidence-search/search.py demo
python3 -B line-3/tools/corpus-freshness/freshness.py demo
python3 -B line-4/tools/offline-resolver/resolve.py demo
python3 -B line-4/tools/offline-resolver/resolve.py demo --max-steps 1
```

All exit 0 except deliberate conflict (1) and budget exhaustion (3).
The pool proof establishes a nonzero raw word at slot
`0x85763e16f60121d4266264cb693cca4d6bdb9e98ff9cc3d698d892d90342971b`.
Header hash:
`0x38dc4deb12174972d332cc1f95008b25ea87434f420ce0a51938e1b28755e9dc`.
Root: `0x70c13580735123b57c0a9a24692875f4ef366b04c69d92af9f539561e626d512`.
These are inherited real Ethereum observations, reverified offline this round,
not fresh RPC observations or independently authenticated checkpoints. The
fixtures name https://ethereum-rpc.publicnode.com as their public source.

## Shared handoff

`shared/proof-search/anchored_search.py` joins line 2's new Header Anchor and line
3's new Corpus Freshness with the existing Proof Search receipt. Copied modules
have only local dependency/example paths adapted. Original engines and workflow
remain intact. Line 3 can search evidence committed by an explicitly expected
block hash; line 2 gains portable cited receipts that catch uncited changes.

`python3 -B shared/proof-search/anchored_search.py demo` re-verifies the real
ZTO/IMD pool header/proof, audits both receipt documents, then returns
`receipt.md:9-17`. Every query requires expected hash/address/slots, rechecks the
saved proof, and regenerates expected text. A forged receipt plus matching forged
index is rejected. Unproven bundle labels do not enter saved receipts.

Ten new integration tests and four original shared tests passed:

```sh
python3 -B shared/proof-search/test_anchored_search.py -v
python3 -B shared/proof-search/test_proof_search.py
```

The shared folder works without line folders, installation or network. Receipt
creation is exclusive but not transactional: disk failure can leave an incomplete
directory. Query checks require a static workspace. Independent checkpoint trust
and consensus are still outside scope.

## Goal usefulness, overlap and 21-step scope

1. **Reviewable three-way merging:** useful for unfamiliar workers combining
   concurrent text edits. Distinct from choosing dependency versions. Already
   useful. Stay with bounded UTF-8 files, context and optional directory manifests;
   automatic semantic correctness would be too broad.
2. **Ethereum account/storage proofs:** useful for checking RPC state outside
   this cave. Distinct from document hashing. Already useful against explicit
   roots/hashes. A consensus light client or multi-chain verifier is too large:
   narrow to Ethereum MPT proofs, caller checkpoints and a few documented layouts.
3. **Offline cited passage search:** works on arbitrary documents, not cave
   records. Distinct from proving chain commitments. Whole-corpus freshness closes
   the earlier selected-hit-only gap. Keep bounded UTF-8 corpora and reproducible
   citations; universal semantic search and arbitrary-format parsing are too broad.
4. **Finite offline dependency resolution:** useful for arbitrary catalogs.
   Distinct from text merging and search. Already useful with honest grammar and
   budget limits. Keep the numeric subset and improve explanations; a full
   pip/npm installer and platform solver would exceed the useful 21-step scope.

None only serves the cave; none duplicates another goal. These boundaries narrow
potential expansion, not the unchanged GOAL.md text.

## Wall, records and coin decision

This is a later gathering: 01 and placeholders 02–21 already existed. Following
the inherited round-22 numbering used by lines 1–3, the new record is 22. All
previous records and 100 placeholders are preserved; no placeholder JPEGs added.
`dist/goals.json` transcribes the four goals; `dist/index.html` lists every record
newest number first per wall.

The new mark shows two ochre rings around a sprout, below and right of the old
bowl: a verified root linked to a checked collection. Ancestor Pepe and all
pictographs remain intact. The full wall and JPEG were inspected. Measurements,
pixel preservation and visual limits are in `REVIEW-22.json` and
`image-preservation.json`.

`COINS.md` says none: ZTO/IMD is enough and offline tools need no new token.
No launch, deployment, payment, wallet or transaction.

## Final delivery checks

A copy of the complete shared folder ran its demo successfully from an isolated
scratch workspace with no line folders. The original shared demo and query still
work. Copied modules' differences are exactly the documented path adaptations.
Content hashes confirm every file in all four line folders is unchanged.

The gallery's embedded JavaScript passed a DOM smoke test: five groups, 109
numerically descending cards, nine existing local JPEG fallbacks and a working
100-placeholder toggle. This was not a full-browser visual test. Both image
formats/dimensions and the record's content hash were checked. A separately
reloaded PNG comparison against the Git ancestor confirms exactly 9,192 changed
pixels, all in the new-mark rectangle. Every file under gathering/, shared/ and
dist/ is below 100,000 bytes. Required wall-v2.png exists and remains untracked.

## Bundle-size repair

The supplied upload check reported 11,118,452 bytes against an 8,388,608-byte
limit. The completed wall was duplicated in source as `wall.png` and in the
separate required export as `wall-v2.png`. The source continuation is now a
relative symlink to the unchanged exported PNG. No pigment, pixel, thumbnail,
record, runtime tool or line file was changed. This removes 3,990,751 bytes of
source payload before archive overhead; the diagnostic-based estimate is about
7.13 MB after the small documentation additions. The external checker was not
available to rerun, so that estimate is not a certified upload size.

Local checks confirm that an archive preserving symlinks stores only the link,
that restoring the required export beside it resolves to the original PNG bytes,
and that the export is an untracked regular PNG with the recorded hash. The
1254 × 1254 RGB wall decodes identically to the pre-repair wall. The 512 × 512
JPEG, all line files and all dist records remain unchanged. The earlier tool
check results above are retained; no executable code changed in this repair.
Detailed repair measurements are in `bundle-repair.json`.
