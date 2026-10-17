# Gathering 22: Two checks, one root

Delivered `artifacts/gathering/wall-v2.png`: RGB PNG, 1254 × 1254. The continuation
`wall.png` is a relative symlink to `wall-v2.png`, so both paths read identical
bytes without bundling a second full PNG. The required `wall-v2.png` remains an
untracked regular file for the separate artifact upload. Keep that exported file
beside the link when restoring the delivery; a source-only checkout needs the
separately delivered artifact before opening `wall.png`. Preserve the link when
archiving source rather than dereferencing it. `dist/gathering/22.jpg` is a 512 × 512 JPEG
below 100 KB. Record 22 hashes the finished PNG. Earlier records and all 100
unpainted placeholders remain unchanged. This is the second painted gathering;
22 follows the inherited numbered-record convention used by lines 1–3.

The new worn ochre rings represent linking a verified root to a checked document
collection. The installed image generator edited the inherited gathering wall.
Only its small new pigment motif was isolated and composited onto bare rock;
no ancestor was erased, moved or redrawn. All pixels outside the 210 × 165 area
at (780, 915) are identical to the ancestor; only 9,192 pixels changed inside it.
Rock shows through and between strokes. The tiny generated sprout is faint on
this rock; the two rings carry the meaning. No visible hands or handprints were
added. Ancestor Pepe's hands remain concealed. Both final image sizes were
visually inspected: no text, numbers, forbidden symbols, borders or signatures
observed. No unmet visual requirement identified; recognition is a local review.

`REPORT.md` gives per-line commands, results, limits and goal-scope guidance.
All 119 line tests, four existing shared tests and ten new integration tests
passed. The offline real ZTO/IMD pool demonstration is reproducible:

```sh
python3 -B shared/proof-search/anchored_search.py demo
```

It reconstructs the header against an explicit historical hash, re-verifies the
saved proof, audits both documents and cites `receipt.md:9-17`. The demo hash is
an RPC observation, not an authenticated checkpoint. See the shared README for
the external trust boundary and commands for your own independently trusted hash.
No dependency installation, network or line-folder access is needed by that tool.

`COINS.md` says none. No coin, deployment, payment or transaction was requested.
No line source was changed. The self-contained gallery contains 109 records,
grouped by wall and newest number first; unpainted slots can be expanded.
Full-size images use artifact URLs, with local JPEG fallback for painted walls.
No external scripts, styles or fonts are required. Rebuild it and the goals:

```sh
python3 -B gathering/build_gallery.py
```

The image generator's draft is not retained as another workspace image.
`finish_wall.py` documents the standard-library PNG pigment composition and
pixel comparison; it requires the original ancestor and the transient generated
draft and deliberately refuses to run twice. `make_thumbnail.py` uses the
machine's installed Blender only as an image resizer/JPEG encoder, with no 3D
rendering. Neither helper is a dependency of the delivered shared tool.
`REVIEW-22.json` records measurements, limits and review; `REVIEW.json` mirrors it.

The bundle-size repair replaces only the redundant source PNG with this link.
It removes 3,990,751 bytes of source payload before archive overhead. The wall,
thumbnail, record hash, gallery, tools and line folders are unchanged. The supplied
11,118,452-byte bundle diagnostic therefore projects to about 7.13 MB, below
8 MiB; this projection is not a rerun of the external bundle checker. Local
archive checks and decoded-pixel checks are recorded in `bundle-repair.json`.
