## [0.157.0] - The package says how responders arrive

**Roadmap 212.** The walker, 2026-10-08: "have responders show up after the
job, on the way back (and this would be on the gameplay layer, but we can make
thee assets and ensure there is clearance and routes for their arrival)".
What exists before this release:
- **Lot 0.99.0** plans each arrival -- the road end a vehicle appears at, the
  lane it drives in by, a stop it fits with its doors open -- and reserves
  the lane and the stop from everything it stands in the street.
- **0.156.0** put each stop in `gameplay_anchors.json` as an `ai_spawn`
  tagged `responder`, and cold run 9201 shipped three.

A Dispatch anchor holds a position and tags, and the rest of an arrival
reached no package.

### `responder_arrivals.json`

`write_responder_arrivals` writes one record per arrival, keyed by its
anchor's id:
- **where it starts and stops:** `entry` (the road end) and `stop`;
- **which way it faces:** `forward`, the unit vector from entry to stop;
- **its size:** `vehicle_m`;
- **what is kept clear:** `stop_box` and `lane_box`, the x/z extents nothing
  else stands in;
- **what the stop serves:** `toward`, the point of the crew's way back the
  stop was chosen for, with `to_way_back_m` and `run_m`.

**Frame:** Godot -- x, y up, z = -(site y) -- metres, the frame of every
position in `gameplay_anchors.json`.

**One counting of the ids.** `dispatch_inputs.site_marker_anchor_pairs` now
yields each site marker beside the anchor it becomes. The staging and this
file both read it, so an arrival names exactly the anchor Dispatch was given.
Two spellings of one id would be two places for it to drift.

**Where it is written:**
- **Before the glb scan, the closure verdict and the manifest walk,** so the
  file is inside the package each describes, and
  `portable_resource_manifest.json` lists it.
- **Listed in `closure._METADATA_FILES`:** its ids (`lot:responder_arrival_...`)
  are shaped like the NodePath strings the authoring-path test reads as
  paths, the reasoning that put `handoff_bindings.json` there.

**Only when Lot says so.** It is written only when Lot's gameplay carries a
`responder_plan`, which Lot 0.99.0 and later do. A package built from older
Lot output, or by a caller passing no `lot_gameplay`, is exactly what it was.

**`cmd_export`** passes the selected candidate's `site.site.gameplay.json`.

**HANDOFF.md** gains one paragraph, for whoever opens the package:
- `mission_start` and `extraction` are tagged at the getaway van on a heist;
- `responder` tags where responders can arrive, and this file says how;
- spawning and timing responders is the runtime's.

### Tests

`tests/unit/test_responder_arrivals_in_package.py` uses cold run 9200's
seed_9054 arrival records, verbatim:
- **The arrivals:** every one turned to the package's frame -- entry, stop,
  forward, boxes, vehicle -- and compared with the export's file.
- **The manifest** lists the file.
- **Each arrival names the anchor** `stage_dispatch_inputs` writes for the
  same gameplay.
- **No file** without Lot's gameplay, or with Lot output from before 0.99.0.

**On 0.156.0** the file cannot import: there is no
`RESPONDER_ARRIVALS_NAME`.

**Suite:** exit 0; 2,014 passed, 14 skipped (the real-tool smokes,
`LF_TOOLS_DIR` unset), 1 xfailed.
- That is 0.156.0's 2,008, plus this file's 5, plus the one case
  `test_sibling_locator.py` adds for every new source file.
- Tallied off the progress lines: the conftest prints no summary.

**Not yet:** a package built by the pipeline with the file in it. That is
the cold run after this.
