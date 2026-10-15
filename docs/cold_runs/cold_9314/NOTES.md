# Cold run 9314 -- the layers shown, the venv's pins held, the ground unshaded (urban_row_001)

**What it tested:** three Level Factory releases of the morning of 2026-10-15 on cold run 9313's toolchain, brief
and seed (urban_row_001, seed_9104 named). Staged from 9313.
- **0.213.0 (46dc828), the factory's roadmap 257, the walker's ask:** `output_layers.json`'s label spelled by the
  planner (`graybox+art+light+gameplay` where the export spelled `graybox+art+gameplay` of a package carrying the
  light), HANDOFF.md's last paragraph on the layers, an `[export] layers:` log line.
- **0.214.0 (d7c5586), roadmap 256:** the venv's nine dependencies held by a constraints file. Nothing in a package.
- **0.215.0 (56fd144), roadmap 252:** the backdrop's ground unshaded, `shading_mode = 0` on its material, the
  priced arm's bytes.

**Result: 0 interventions (journal 0, unattributed files 0). The four files the two package-facing releases name
moved, nothing else but Godot's per-save ids and the metadata, and the lightmap and every GLB are 9313's bytes.**

- **The changes** (`layers_ground.py`, `layers_ground.out.txt`; `metadata_9313_9314.out.txt`):
  - `output_layers.json`: `layers` `["art", "gameplay", "light"]` in both runs; `label` `graybox+art+gameplay` ->
    `graybox+art+light+gameplay`.
  - `HANDOFF.md`: 17 -> 18 lines, 3,097 -> 3,863 bytes, the paragraph "WHAT THIS PACKAGE IS MADE OF: ... THE
    LIGHT IS A LAYER OF ITS OWN, APART FROM THE ART. This package carries it. The same build exports without it as
    `--mode art-unlit` ..." -- see the finding below.
  - `site_backdrop.tscn`: the ground's material `albedo_color ..., roughness = 1.0` -> `albedo_color ...,
    shading_mode = 0, roughness = 1.0`, line for line the arm `ground_price.sh` priced.
  - `backdrop_layer.json`: `ground.shaded` absent -> `false`.
  - The export's log: `[export] layers: art, gameplay, light (graybox+art+light+gameplay); the light is Lux's
    result, a layer apart from the art`.
- **The bake's input did not move, so its output did not:** `bake.exr` the same bytes as 9313's; all 329 GLBs the
  same bytes; the log's bake line as 9313's (349 models, 112 primitives, 3,160 users); 2,490 files in each package,
  none only in one.
- **The grades:** every candidate as in 9313 -- seed_9003 PASS_WITH_TUNING 89, seed_9104 PASS 100, seed_9205 PASS
  90 -- with the same enemy and crew spawns and 0 of 32 summary fields moved on each
  (`fight_fields_9313_9314.out.txt`). Findings 76 at the candidates and 109 after the export, as 9313's.
- **The 26 files that differ, each attributed:** the 4 above; 12 are Godot's per-save ids, roadmap 247's residue
  (the presentation, `bake.tscn` and the ten standing Empties' `site.tscn`, 0 lines once masked); 10 are the
  metadata that records times, paths and the hashes of the above (`LF_MANIFEST.json`'s `archive_name`,
  `built_utc` and closure fingerprint; `build.lock.json`; `LICENSES.json`; `export_closure_scan.json`;
  `glb_reference_scan.json`; `light_bake.json`'s editor log path and times; `portable_resource_manifest.json`;
  `validation/report.{html,json,md}`).

**FOUND: the layers paragraph is not a paragraph.** `HANDOFF_LANGUAGE` ends with one newline, and 0.213.0 appended
the layers text straight after it, so in this package "...online correctness.\\nWHAT THIS PACKAGE IS MADE OF: ..."
is one paragraph to a Markdown reader, the new text the last line of the one before it. Fixed in Level Factory
0.215.1 (`handoff_text`: the language, a blank line, the paragraph; a test on the composed text), the join
proven by the test; the next cold run's package shows it.

## The time

    run    shell   art     export   walk   retire   the drive
    9313   114 s   221 s   211 s    12 s    6 s     9.8 min (585 s)
    9314   113 s   220 s   213 s    10 s    4 s     9.7 min (579 s)

Neither is a speed measurement. 9314 ran beside file reads and a memory note; nothing opened a window and no suite
ran.
