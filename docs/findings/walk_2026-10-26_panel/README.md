# The walker's first run of the authoring loop in a windowed editor, 2026-10-26

Roadmap 318. The walker opened `level_factory/apps/godot` in Godot 4.7, made a Restaurant Row level
(`levels/restaurant_row`, revision 1, Evening), generated three layouts, chose seed 9205 and walked it. Everything
below is what they hit, in their words where they gave them, with what was measured and what was done.

## The panel

| # | The walker | Measured / cause | Done |
|---|---|---|---|
| P1 | Setup tab: every column cut off ("warnin", "This tool is new...") -- `frames/01_setup_tab.png` | the tree's columns in a narrow dock, nothing showing the whole text | LF 0.256.0: tooltips, wider readiness column |
| P2 | "revision 1.0", "Seed 9003.0" -- `frames/02_level_tab_layouts.png` | Godot parses every JSON number as a float | LF 0.256.0: `LevelPanel.whole` |
| P3 | "its increasing the number of steps as it goes, so the percentage goes up then down" | progress counted finished jobs over the jobs the index had met so far | LF 0.256.0: `run` records its plan; progress counts against it |
| P4 | 99% for minutes on "Building the walk preview" -- "stuck or completing soon?" | the last stage counts nothing, so the art stage's number stayed | LF 0.256.0: "Stage n of m", a moving bar where a stage cannot count |
| P5 | the panel reloaded at 11:16 mid-walk and lost the walk | the walk went on (worker alive, result 11:22:35); the new panel did not know it | LF 0.256.0: the client records its operation, the tab re-attaches |
| P6 | nothing opened a walk already built | -- | LF 0.256.0: "Open the last walk" |
| P7 | closing the editor dirtied the repo | the editor rewrote `apps/godot/project.godot` in its own format (comment header replaced) | restored; owed: commit it in the editor's format |

## The level

| # | The walker | Measured | Status |
|---|---|---|---|
| L1 | "fell through the floor of the first building i walked in" | **the walk's headless `--import` timed out after 600 s** (started 11:12:22; walk log: `WARNING: headless import failed ... timed out after 600 seconds`) and the walk still finished `ok`, self-check `findings`. 96 of 758 imports had no cache file, every building's `site_base.glb` (the shell and its floors) among them; a Godot opening a project to play does not import, so they never loaded. The walk bot had failed both ladders at `ground`. After the walker ran the import by hand: 763 imported, 0 missing, "floor holds now". | owed: LF 0.257.0 -- the walk fails on an import that did not finish; its timeout the light bake's 1,800 s. Why it ran past 600 s is NOT known: this session's own test suites were running heavily on the machine at the time (hypothesis, unmeasured) |
| L2 | "i can't use this wide ramp to go up or down?" -- `frames/03_garage_ramp.webp`, parking_garage storey 1, pos 71.9, 4.6, -6.3 | the ramp's head (the side the walker stood on) is open by design; the slab cut over the ramp begins at its MIDDLE, leaving 1.04-1.55 m between slab and ramp where 1.8 m is needed (`docs/findings/ramp_cut_241/`) | roadmap 270, OPEN, not started |
| L3 | "What is it, doesn't look finished" (the same ramp) | the ramp's surface is a plain yellow slab | open, unmeasured |
| L4 | "far too dark in the super market" (pos 24.4, 1.6, -6.8, supermarket_a01) | MEASURED (`light_check_after_fix.txt`, `frames/05_sales_floor_station.png`): the sales floor's station reads p50 **3** against the ROW floor 10 -- FAIL -- while the back stock reads 77 and the cash office 13. The aisle shelving reads pure black on every face under lit fixtures. Hypothesis, unmeasured: the shelves (`supermarket_a01_fixtures.glb`, one of the 96 the walk never imported) were imported afterwards by hand and their lightmap UV2 no longer matches the bake. Also failing: the deli's basement vault, p50 3 against MOODY 5. **The first light check passed all 29 stations on blank frames** (`light_check_blank_frames.txt`): every frame was Godot's clear colour, luma 76, because `light_census.default_scene` picked `player_walk.tscn`; fixed in the factory's tools (`patches/patch_root_scene_choice.py`): the run/main_scene first, and a flat frame FAILS as NO FRAME | open: re-walk on LF 0.257.0 (a complete import) and re-check; if the sales floor still reads 3, the lights |
| L5 | "lot of seams visible on these doors in the supermarket" (pos 7.3, 1.6, -13.5, int_0_0_open1, a Doorway) | Zoo 1.126.0's casing is in place: full-height strips either side of the opening, because the doorway module's joint runs full height. They read as pilasters with their own lines; the left strip's 15 mm side face shows a dashed dark line (thin face vs lightmap resolution: unmeasured) | open: the casing as built does not read as a door casing (`docs/findings/walk_2026-10-23_9386/` finding 2 is its origin) |
| L6 | "highly visible seams and pieces here...breach?" (deli_a01, pos -54.1, 1.6, -5.6) and a second wall in the deli (pos -65.9, 1.6, -9.7; overlay: `bldg int_0_0_open1  zoo`, `look Wall`) | an OPENING slot drawn as a wall is an intact breach panel: its own module and lightmap rect, so a different shade, with Zoo 1.126.0's full-height casing strips at both ends showing as dashed lines. Same root as L5. The deli carries breach slots on exterior walls N, S and W (`lot/deli_a01/site.tscn`: `ext_0_N_open1`, `ext_0_S_open2`, `ext_0_W_open0`) and interior ones | open: with L5, the casing does not hide an interactive slot's joint; the walker's goal stands ("hide the seam for breaches", 2026-10-24) |
| L7 | "not consistent: textures" -- `frames/04_window_module_inconsistent.webp` (deli_a01, pos -49.7, 1.6, -6.7; overlay `look ext_col_0_E_open1_pane`) | the window's module wall reads lighter and its texture discontinuous with the merged wall beside it: an opening module with its own bake, as L5 and L6. Three kinds of opening (door, breach panel, window) share one root | open: the fix must cover every opening module, not a casing per type |

## Instruments kept here

- `floor_probe.gd` and `footprints_9205.json`: rays straight down on a 1 m grid (offset 0.31 / 0.47 m) inside each
  building's footprint, from 1.0 m above its origin, reporting what each hits and at what height.
- `floor_probe_unimported.out.txt`: its run on the preview BEFORE the import was completed. 866 of 999 rays in the
  deli and every ray in the supermarket and garage hit nothing. That run measured an unimported project, not the
  level: kept because it is what an unimported preview looks like to physics, and so that nobody reads it as the
  level's floors. The probe is not yet re-run on the completed import.
