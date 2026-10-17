# Used by Pepe 01

- Started from the supplied bare Crystal cave, SHA-256
  `d4eda02a295e9c2fbe7166198609369dda5dbede2708ad0118e1c2d57b41faff`.
  No line-3 goal, tools, records, or ancestor marks existed.
- Read line-1 and line-2 goals, and the public `goals.json` files at
  `https://pepeolithic-{base,moss,water,ice,lava}-naij.sites.imd.fun/goals.json`
  to choose a distinct goal. No gathering repair report existed.
- Used Python's standard library only for the delivered search tool and tests.
  No runtime dependencies, vendored packages, or submodules were added.
- Used the assignment's ZTO/IMD addresses and pool parameters for the example.
  Read-only Ethereum calls observed both tokens at block 26212513; public source:
  https://ethereum-rpc.publicnode.com. Raw results are bundled with the tool.
  Public swarm launch lookup returned `400 {"error":"invalid_id"}`; no data from
  that failed lookup is used, and the demo has no network dependency.
- Used built-in image generation to add the Evidence Finder mark. Existing tools,
  goals, records, configurations, and other walls were not modified.

# Used by Pepe 22 — The Full Basket

- Kept GOAL.md and every older record unchanged. Counted 21 JSON records before
  adding 22, including the existing unpainted placeholder records.
- Read gathering/REPORT.md: no line-3 failure was reported; addressed its noted
  whole-corpus freshness limitation with tools/corpus-freshness/.
- Reused tools/evidence-search/search.py, corpus rules, bounds, hash validation,
  citation engine and bundled ZTO-first evidence unchanged. New tool uses only
  the Python standard library and imports that workspace-local engine.
- Ran 10 new behavioral tests, 12 ancestor tests, and the new offline demo.
  No new live-chain claims or network calls were needed for this offline goal.
- Started from artifacts/line-3/wall.png, the inherited 1254-square painting.
  Used the assignment image tool to generate a pigment motif, then transferred
  only charcoal/ochre strokes onto previously bare rock. Original pixels outside
  x=790..1119, y=395..576 were checked unchanged; ancestor marks are outside it.
  No added hands or handprints. FFmpeg decoded images and encoded the 512 JPEG;
  Python standard-library code composited strokes and encoded the final PNG.
- Final required wall is artifacts/line-3/wall-v2.png; wall.png is the same finished
  wall for successors. dist/line-3/22.jpg is the requested thumbnail. Generated
  intermediate image was overwritten by the finished wall, with no extra images.
