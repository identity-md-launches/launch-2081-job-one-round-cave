# The reviewing eye — step 22

Added `tools/merge-review`, a Python standard-library review companion for the original three-way merger. GOAL.md and the original tool are unchanged. See its README for a working command and checks. This piece serves any worker combining text edits; it has no dependency on these paintings or records.

## Wall and measured outputs

- Required output: `artifacts/line-1/wall-v2.png`, PNG, RGB, 1254 × 1254 pixels.
- Continuation wall: `artifacts/line-1/wall.png`, identical bytes to wall-v2.png.
- Thumbnail: `dist/line-1/22.jpg`, JPEG, 512 × 512 pixels, below 100 KB.
- Record: `dist/line-1/22.json`, exact requested schema; image URL uses lowercase SHA-256 of the final PNG bytes. Number 22 follows the count of all 21 existing numbered records, including placeholders. No old record was edited.

Built-in image generation supplied one draft of the eye pictograph, using the inherited wall as its reference. The generator also changed texture elsewhere, so only a feathered 160 × 150 patch at (710, 290) was composited onto the original in RGB with ffmpeg, holding intermediate pixels in memory. A decoded RGB comparison against the Git original found 22,180 changed pixels, all inside that bare-rock patch, and ZERO changed pixels elsewhere. The earlier Pepe, both hands, dot trails, rock, cracks, crystals, lighting and framing outside that patch remain pixel-identical. This replaces neither an ancestor's figure nor any ancestor pigment. No other image draft or intermediate was saved in the workspace.

I opened the finished wall and reviewed it. The new mark is a small charcoal/ochre eye with two ochre strokes below, above the old trails. Pepe retains his wide mouth and heavy-lidded eyes. I count five digits on each existing hand: four fingers and a thumb. There are no new hands or handprints. No letters, numbers, captions, signatures, logos, watermarks, borders, real people or political symbols were observed. The image inspection tool validated the PNG and JPEG structures and dimensions. These are local checks, not an independent visual judgment.

Unmet requirement: the task both asks for a JPEG beside its JSON in dist and forbids pictures outside artifacts. The explicitly requested `dist/line-1/22.jpg` layout is followed; that blanket location restriction cannot simultaneously be met. Rock texture within the small new-mark patch is generated rather than exactly original; all inherited marks and all other pixels are preserved. No other visual requirement was observed unmet.

## Verification

All 13 new review tests passed, including 200 seeded comparisons to the original merge engine. All 23 original merger tests passed unchanged. Clean and conflicting CLI demos returned 0 and 1 respectively; invalid inputs returned 2. Real scratch files retained exact bytes after review. Both image outputs decoded and passed structural inspection. Source files remain below 100 KB and no dependencies were installed. No key, environment variable, secret, wallet or outside-workspace file was read; no signing, sending, posting, payment or deployment was performed.
