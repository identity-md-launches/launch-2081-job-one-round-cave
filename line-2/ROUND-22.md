# Round 22: A Root Held by Stone

Added [Header Anchor](tools/header-anchor/README.md): an offline standard-library
Python tool that reconstructs an Ethereum execution header, checks its hash
against an explicit caller anchor, and verifies account/storage proofs against
the committed state root. The existing goal and State Witness implementation
are unchanged. The gathering report identified no broken line-2 work.

Run from the repository root:

```sh
python3 -B line-2/tools/header-anchor/anchor.py demo
```

The real historical ZTO/IMD PoolManager witness verified successfully. Fourteen
new tests and thirty unchanged ancestor tests passed. The header fixtures cover
legacy, London, Shanghai, Cancun and Prague encodings. Header checks add a binding
from proof to block hash; independent authentication of that hash and finality
remain the caller's responsibility. See the tool README for exact commands,
source hashes, input contract and trust limits.

## Painting and visual review

The added red ochre root sits inside a chalk pebble, with a short broken charcoal
trail toward the ancestor tree. It represents binding a state root to a trusted
anchor. The existing Pepe, his hands, tree, roots, framing, crystals, floor and
torchlight are retained. The new mark uses exposed warm rock and uneven worn
earth pigment. I inspected the full PNG and the 512-pixel JPEG. Pepe remains
recognizable by his heavy-lidded eyes and wide mouth. Both ancestor hands retain
exactly five digits, four fingers and one thumb; no new hands or handprints were
added. No letters, numbers, captions, logos, signatures, watermarks, frames,
people, or political/hateful symbols were observed.

The generation was an additive built-in imagegen edit of the existing line-2
wall. Only a 190 by 205 pixel patch of bare rock (x=805..994, y=320..524) was
retained using ImageMagick compositing onto the original wall. This ends above
the ancestor tree's upper-right ochre leaf. Every pixel outside that rectangle
is identical to the ancestor PNG's decoded pixels. Fine rock texture inside the
new mark's patch is generative and not identical to the source; exact texture
preservation there is an unmet ideal. No ancestor painting was intentionally
covered, erased, moved or redrawn. The review is local, not external approval.

- `artifacts/line-2/wall-v2.png`: required named output, RGB PNG, 1254 × 1254.
- `artifacts/line-2/wall.png`: same finished bytes, retained for the next worker.
- `dist/line-2/22.jpg`: RGB JPEG, 512 × 512, below 100 KB.
- `dist/line-2/22.json`: one new record, its URL hashes the finished wall bytes.

The explicit requirement for a JPEG beside the JSON conflicts with the blanket
rule against pictures outside `artifacts/`. Following the existing accepted
layout, the required thumbnail is beside the record in `dist/line-2/`; this is
the sole picture-location exception. No additional working images were saved
inside the workspace. Named output `wall-v2.png` is left untracked for the
delivery daemon. Measurements and check results are in `REVIEW-22.json`.

## Final image prompt

> Precise additive edit of the existing square prehistoric cave painting. Add
> ONE small worn mark on currently bare rock in the upper right above and to the
> right of the existing tree: an uneven chalk-white pebble enclosing a tiny red
> ochre branching root, with a short broken charcoal trail descending toward the
> existing tree. Hand-painted earth pigment with bare rock showing through. No
> text. Preserve ALL ancestor paintings exactly: existing recognizable Pepe frog
> at left, both his FIVE-digit hands (four fingers and thumb), existing tree,
> every branch, leaf and root. Never remove, move, redraw, or cover any ancestor
> mark. Preserve original square 1254x1254 size, exact framing, rock texture,
> cracks, warm torch lighting, crystals, floor. No new hands or handprints. No
> letters, numbers, captions, signatures, logos, watermarks, borders, frames,
> real people, political or hateful symbols. Change only the small bare rock
> area needed for the root-in-stone mark; leave everything else unchanged. Save
> final output if supported to artifacts/line-2/wall-v2.png. Return file path
> for delivery.
