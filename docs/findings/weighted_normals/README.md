# Weighted normals: every bevelled part shipped as a dome (Zoo 1.87.0, roadmap 214, trial 1)

**Question.** The walker's modern low-poly standard asks for controlled
normals (section 5), and Addendum A.4 puts weighted normals first of four
trials, because they cost no texture and no triangles. Four things had to be
known before Zoo shipped them:
- what Zoo's normals were on a bevelled part;
- what weighing by area changes, and what it costs;
- where it changes nothing;
- how it looks.

**Frame and units.** Angles in degrees, between unit normals.
- **A "big face"** is a triangle over 0.01 m2. A corner's **splay** is the
  angle between its normal and its own face's normal.
- **Where the numbers come from:** GLBs are read back with a plain struct
  reader, Y up; Blender meshes are Z up. No angle here depends on the frame.
- **What was built:** Zoo's own build path, Blender 5.1.1. Every "1.87.0"
  run before the release landed was against a `git archive` of Zoo 1.86.0
  with `patches/patch_zoo_weighted_normals.py` applied (`ZOO_ROOT`); every
  "1.86.0" run was against the archive unpatched.

## What Zoo shipped: a dome

`api_probe.py`, on a 0.6 x 0.4 x 0.5 m crate with Zoo's 1.4 cm bevel, built
by `geometry.bm_to_object` and exported by `export.export_glb`:

| the crate | smoothing | vertices | big-face splay, default -> weighted | normals moved |
|---|---|---|---|---|
| `crate_50` | 50 deg, Zoo's default | 48 -> 48 | 28.89 -> 2.40 mean (2.61 max) | 48 of 48 |
| `crate_30` | 30 deg | 96 -> 96 | 0.00 -> 0.00 | 0 |
| `crate_1` | 1 deg, faceted | 96 -> 96 | 0.00 -> 0.00 | 0 |
| `tank_50` | 50 deg, a 14-sided cylinder | 94 -> 94 | (no big flat face) | 92 of 94, at most 20.70 |

- **Why 28.89.** `shade_by_angle` smooths every fold under 50 degrees, so
  the 45-degree chamfer joins both faces it touches. The default corner
  normal weighs a fan's faces by CORNER ANGLE, so the big face and the
  chamfer count about the same, and every big-face corner leans toward it.
- **The same figure, measured once before.** `bm_to_object`'s docstring
  records 28.9 degrees on `wall_delco_01_w200`: "the panel is therefore
  shaded as a dome". The walls were given `smooth_angle=0.0`. The props kept
  the dome.
- **Weighing by area** lets the big face keep its own normal, while the
  chamfer, squeezed between two big faces, rolls from one to the other.
- **The cost in vertices.** The faceted crates carry twice the vertices of
  the smoothed one: every hard edge splits them. Weighted, the smoothed
  crate's faces read flat at 48 vertices.

**Two API facts, Blender 5.1.1.**
- **Run 1 of `api_probe.py` asked `hasattr(bpy.types.Mesh, ...)`.** It said
  False for all four calls, including `normals_split_custom_set`, which the
  same run then called successfully on a mesh. The RNA class does not list
  them; an instance does. Kept in the probe, both columns printed.
- **Clearing.** `normals_split_custom_set` with zero vectors did NOT restore
  the default normals; the weighted ones stayed. Removing the
  `custom_normal` attribute did: 28.89 again.

## Through the export, the merge and ingest

`export_probe.py`, the same crate:

| | Zoo 1.86.0 | Zoo 1.87.0 |
|---|---|---|
| one part | 28.89 | 2.40; with `weighted_normals=False`, 28.89 |
| two parts of one family and material, which the merge packs into one mesh | 28.89 | 2.40, at 96 vertices and 88 triangles either way |
| ingest of a file whose two parts share a material, every normal authored straight up | 8 of 104 kept | 104 of 104 kept |

- **The merge had to change.** A packed mesh's normals are recomputed from
  its edges. That reproduced the parts' DEFAULT normals exactly, because
  nothing welds, and cannot reproduce custom ones. 1.87.0 copies each part's
  corner normals with its faces.
- **The ingest row is a defect 1.86.0 had, found here.** An imported mesh
  carries its author's normals. When two imported parts shared a material,
  the merge recomputed them. 1.87.0 keeps them, and ingest does not weigh
  them.

## Across the library

`census.py` builds every species once, at its genome's default corner, and
exports that one scene twice: weighted (ON) and with every custom normal
removed and `weighted_normals=False` (OFF, 1.86.0's shading). Output:
`census.json`, the table `census.txt` (`census_table.py`), the run's lines
`census_log.txt`.

- **Built:** 121 of 122. `boots` does not build through the kit path
  (`KeyError: 'shaft_h'`). It fails the same on 1.86.0 and is already
  recorded (`zoo/tests/test_coincident_faces.py`, `DID_NOT_BUILD`).
- **The cost: none measurable in the file.** Vertices, triangles,
  primitives and bytes are identical ON and OFF in 121 of 121.
- **Big-face corners over 10 degrees off their face,** all species: 15,114
  OFF, 5,498 ON.
- **81 species changed.** In the other 40, no triangle corner's normal moved
  more than 1 degree: the parts faceted on purpose (`fire_hydrant`,
  `vending_machine`), the walls, the flat panels (`poster`, `pennant_row`).
- **The largest move anywhere:** 40.08 degrees, `cheesesteak`. That is the
  figure `fan_probe.py` read in the mesh itself.

**The most domed species, before and after** (big-face corners over 10
degrees; mean splay):

| species | domed OFF -> ON | splay OFF -> ON |
|---|---|---|
| canopy_lights | 756 -> 0 | 14.44 -> 0.48 |
| safe_deposit_boxes | 540 -> 0 | 27.08 -> 3.68 |
| booth_seat | 480 -> 12 | 22.02 -> 3.32 |
| traffic_signal | 607 -> 156 | 23.14 -> 5.91 |
| water_tank | 436 -> 180 | 20.47 -> 4.99 |
| pallet_stack | 312 -> 0 | 25.90 -> 2.78 |
| pool_table | 276 -> 0 | 15.45 -> 1.06 |
| back_bar | 264 -> 0 | 14.28 -> 0.63 |
| stair_rail | 240 -> 0 | 25.12 -> 3.84 |
| payphone | 180 -> 0 | 24.22 -> 3.20 |
| cruiser | 888 -> 735 | 4.20 -> 3.61 |

**Curved things move least, and splay is the wrong measure of them.**
- The cars and the trees keep most of their splay. A curved body is meant
  to sit off its faces, so for them splay measures curvature, not a dome.
- `bus_shelter` keeps 12.39.
- **Whether those read better is a question for the frames.**

### Retracted: the 177-degree flips

**What run 1 reported.** Run 1 of `census.py` paired the two files'
vertices by index, guarded by "the position lists are identical"
(`census_run1_index_paired.txt`). It reported normals moved 177.5 degrees
on `weed_tuft`, 178.4 on `litter_scrap` and 177.6 on `london_plane`, 11
species over 45 degrees in all.

**`fan_probe.py`** read the meshes before export instead: the default
corner normals against the weighted ones, with each fan's coherence (|sum of
area x normal| / sum of area):

| species | largest move | the most incoherent fan |
|---|---|---|
| weed_tuft | 7.67 | 0.893 |
| litter_scrap | 18.55 | 0.946 |
| london_plane | 26.53 | 0.894 |
| jersey_barrier | 36.85 | 0.981 |
| cheesesteak | 40.08 | 0.713 |
| counter (hard surface) | 28.61 | 0.945 |

No fan came near cancelling, and nothing moved past 45 degrees.

**One instrument was wrong, and it was the census.**
- **The cause.** A thin card's front and back vertices share a position.
  So the position lists match whichever order the exporter writes the two
  in, and that order follows the normals, which are what changed. A front
  vertex paired with a back one reads as a flip.
- **The fix.** The census now pairs by TRIANGLE CORNER, which comes in face
  order, and checks each pair's positions equal first.
- **The result.** Its largest move is 40.08 degrees, the same `cheesesteak`
  corner the fan probe found.

## The frames

`render_pairs.py`, against the real Zoo tree with 1.87.0 applied (since
committed as 82ed7b6). Each species is built at its genome's default corner
by `tools/preview_specimen.py`'s kit path and rendered twice from that one
build: as built, and with `--no-weighted-normals`. The render is Cycles CPU,
40 samples, with the tool's sun, world and camera.
- **The control:** the payphone rendered OFF twice is identical, 0.000
  codes and 0.00% of pixels. So every difference below is the weighting.
- **The measure:** the mean change in 8-bit codes, and the share of pixels
  whose largest channel moved more than 8 codes (`frames.txt`).

| species | mean | pixels over 8 | frame |
|---|---|---|---|
| pallet_stack | 2.947 | 15.07% | `pallet_stack_pair.png` |
| booth_seat | 1.298 | 8.25% | `booth_seat_pair.png` |
| safe_deposit_boxes | 1.936 | 7.99% | `safe_deposit_boxes_pair.png` |
| counter | 1.388 | 7.07% | `counter_pair.png` |
| water_tank | 2.000 | 4.38% | `water_tank_pair.png` |
| payphone | 0.550 | 2.80% | `payphone_pair.png` |
| jersey_barrier | 0.349 | 0.99% | |
| traffic_signal | 0.133 | 0.62% | |
| london_plane | 0.065 | 0.14% | |
| cruiser | 0.080 | 0.09% | `cruiser_pair.png` |

**What the frames show** (left: default normals; right: weighted).
- **The hard surfaces read as made things.**
  - The payphone housing loses a bright band and a gradient that made a
    flat steel box look curved.
  - The counter's front loses the diagonal wedge `bm_to_object`'s
    docstring called "the stamped diagonal shadow".
  - The deposit-box cabinet loses a sheen that bent its front.
  - The pallet load and its boards stop looking pillowed.
  - The water tank loses a specular blob that made it look inflated. It
    reads as a cylinder with a lit rim.
- **The cruiser barely moves** at this distance, and the tree does not
  either. Curved bodies were never the dome's victims.
- **The booth seat is mixed, and it is the walker's call.**
  - Its side panels and base read correctly flat.
  - Its tufted back channels and seat cushions lose the plumpness the dome
    happened to give them. A vinyl booth IS puffy.
  - If the plump read is wanted, the fix is cushion geometry, or a per-part
    opt-out, rather than a dome across every hard surface.

**The walker, 2026-10-09, on the payphone, water tank, pallet and booth
frames: "yeah looks better".** They also noted that the payphone model has
no phone keypad or decals. That is true and was not this trial's to fix: it
is the 1.86.0 model with new normals. Roadmap 210 is its redraw.

## In a level: cold run 9211 against 9210

Cold run 9211 is 9210 with Zoo 1.87.0. Both runs picked seed_9181.

**The packages** (`pkg_diff.py`, `pkg_diff.txt`; the control, 9209
against 9210 with Zoo unchanged, is `pkg_diff_control.txt`):
- **What changed:** 143 GLBs. Their JSON chunks are identical, and
  2,760,672 of their differing bytes are NORMAL data.
- **The other 3,432 bytes, in 11 GLBs, are vertex order.** Each of those 11
  holds the same triangles (position, uv, colour) as a multiset. The
  exporter's de-duplication follows the normals.
- **Godot's lightmap unwrap read the new normals:** 119 caches changed,
  against 2 in the control. The baked lightmap is 0.81 MB smaller.
- **The rest are the pipeline's own run-to-run noise.** Import sidecars,
  `.tscn` ordering and the manifests differ in the control too.
  `docs/cold_runs/cold_9211/NOTES.md` attributes them.

**The price.**
- **How it was measured:** `_runs/perf_inner/run.py`, Level Factory's
  fixed-station harness, 53 station headings, each in two passes with the
  lower p95 kept. GL Compatibility, the package's own
  `renderer/rendering_method`; the report records no resolution. The
  harness's exit 1 on every run means "measured, and a station over
  budget": the same 5 of 14 stations in all four runs.
- **The four runs, in order:** `wn_off` (9210), `wn_on` (9211), `wn_off2`
  (9210, the control) and `wn_on2` (9211). Read by
  `patches/zoo_cover_merge/price_robust.py` (`price_robust.txt`) against
  the mean of the two controls.

| | median frame moved | mean | range |
|---|---|---|---|
| the controls, one against the other (stable headings) | +0.034 ms | -0.012 | -0.690 to +0.592 |
| `wn_on` | -0.316 ms | -0.288 | -1.579 to +0.738 |
| `wn_on2` | -0.066 ms | -0.061 | -0.612 to +0.358 |

- **The frame: nothing measurable.** If anything it is marginally faster,
  by about the size of the noise.
- **Unstable heading:** one, the longest sightline at yaw 90 (16.0 and
  14.7 ms in the two controls).
- **Draw calls: unchanged at the median.** Three headings differ in some
  run:
  - `attacker_spawn_8` at yaw 0 differs between the two controls
    themselves;
  - at the other two, `wn_on2` matches both controls.

  That is the harness keeping whichever pass had the lower p95, the effect
  `docs/findings/club_stage_live_price/` records at the same station.
- **The 8-light cap:** identical in all four, 33 of 3,954 meshes over 8.

**The frames** (`tools/look_shots.py`, derived stations plus four interiors,
on each run's walk copy, with 9210 shot twice as the null; `shot_diff.py
--null`, `level_shots_diff.txt`; manifests `level_shots_*.json`):
- 8 of 12 shots moved beyond their measured floor, 3 sit within it and 1 is
  marginal.
- **No regressions:** no clipping, crushing or uniform frame.
- **Mean luminance moves by 0.2 codes at most.** club_block_014 is a night
  level under mostly baked light, and the props the weighting changes most
  sit in shadow there.
- `level_extraction_pair.png` shows how little reads at night. It also
  shows today's street tree, a trunk under a few square leaf cards, which
  roadmap 216 takes up.

## Not settled

- **The booth seat's cushions.** They read flatter, and the walker's
  "looks better" covered the frames as a set. If plumper upholstery is
  wanted, the fix is rounded cushion geometry.
- **`bus_shelter` keeps 12.39 degrees mean splay.** Its curved roof is
  meant to curve; it was not looked at closely.
- **Daylight in a level was not shot.** The walker asked for five times of
  day per level; this run is midnight. The neutral Blender frames are the
  daylight evidence.
- **Trial 2, convex-edge wear,** is untouched. `wear_colors` multiplies
  COLOR_0, so it can darken an edge but not lighten one. A worn edge that
  reads brighter than its paint needs a design, not a constant.
