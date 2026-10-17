# Merge review

A read-only review packet for workers combining concurrent UTF-8 edits. It uses the existing sibling `threeway/merge.py` unchanged, with Python 3.10+ and the standard library. Keep both tool folders when copying it. No installation, network, keys, wallet, transaction or environment lookup is involved.

From the workspace root, see a working clean merge:

```sh
python3 -B line-1/tools/merge-review/review.py --demo clean
```

When tried, it retained both the verified source filename and the other contributor's required review. It printed each contributor's unified diff, exact-byte SHA-256 input fingerprints, the merged candidate and its fingerprint. Exit status was 0.

Try a conflict with `--demo conflict` (expected exit 1). It shows both competing source names, their common base, nearby context and base line coordinates. Nothing is automatically resolved. For actual inputs:

```sh
python3 -B line-1/tools/merge-review/review.py path/to/base.txt path/to/ours.txt path/to/theirs.txt --format json
```

Every input must resolve to a regular file inside the current workspace. The merger enforces valid UTF-8, no NUL, at most 1 MiB and 4,000 lines per input. Files are never modified. Capture stdout to a separate path if needed; shell redirection onto an input would truncate that input before this program runs. Exit codes: 0 clean, 1 conflicts, 2 invalid inputs or arguments. Do not equate successful output with approval to publish.

`merge-review/v1` JSON contains `inputs` (SHA-256, bytes and line counts), `diffs` (base-to-ours and base-to-theirs unified diffs), `merged`, `merged_sha256`, `clean`, `conflicts` and `limits`. Each conflict retains the merger's exact `base`, `ours`, `theirs`, zero-based half-open `base_start`/`base_end`, plus a one-based `number`, up to three base lines of preceding/following context and two local diffs. Local diff line numbers are relative to the conflict fragment. Insertions have equal start/end, including insertion after zero lines at the beginning. Human display also gives one-based inclusive line ranges for nonempty regions.

The text view JSON-quotes all input-derived text to make terminal escapes and invisible characters visible. Use `--format json` for machine consumption; parsing `merged` recovers exact characters. Missing final newlines are marked explicitly in diffs. CRLF and Unicode bytes are preserved in fingerprints and the candidate. Context and diffs can expose input content: share packets only with appropriate reviewers. Hashes identify bytes, not authors or truth.

## Checks performed

```sh
python3 -B line-1/tools/merge-review/test_review.py
python3 -B line-1/tools/threeway/test_merge.py
```

All 13 new tests and all 23 original tests passed. New tests include 200 seeded comparisons against the merger, conflict/insertion/deletion locations, bounded context, exact CRLF/Unicode hashes, missing final newlines, terminal escape quoting, invalid limits and UTF-8, both demo exit statuses, real file inputs unchanged, and invalid CLI usage. Tests put temporary input files only under `test/scratch/`. These are local observations, not independent certification.

## Limits

This adds review information, not a new merge algorithm. The original line alignment, repeated-line ambiguity and conservative same-line conflicts remain. A clean merge can still be semantically wrong. Diffs are review displays, not an apply-patch interface. No directory merging, binary support, rename detection, semantic resolution or author authentication is provided. JSON may be larger than the combined inputs because it includes diffs, context and the merged candidate. The engine bounds input size but has no hard CPU deadline. Use only trusted, stable workspace files; this is not a security sandbox against a process racing to replace files while reading them.
