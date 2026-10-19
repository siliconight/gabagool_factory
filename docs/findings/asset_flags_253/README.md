# Asset flags: G looks good, P needs love (roadmap 253)

The walker, 2026-10-14, after the demo: "I want a way to flag assets that look good and assets that need more
polish/love". Until now a look was judged in chat, frame by frame, and nothing kept the verdicts. This is roadmap
18's missing gate from the walker's side.

## How to use it

1. Walk any walk copy: `_runs/walk_export_<mission>/`, which every cold run builds, or `tools/walk_export.py` by hand.
2. Rest the crosshair on a thing and press **G** if it looks good, **P** if it needs love. The thing is boxed until the
   walk quits, green for good and red for needs love, and a banner at the foot of the screen says what was flagged.
   Flagging it again repaints its box. Each press appends one record to the copy's `asset_flags.jsonl` and saves a
   640-wide frame under its `asset_flags/`.
3. Gather every copy's flags into the ledger:

```bash
python tools/asset_flags.py
```

That writes `ledger.json`, `LEDGER.md` and `frames/` here. LEDGER.md is ranked with what needs love first, by how
often, then what looks good. The frames are copied here because a walk copy is retired after thirty days.

## What "the asset" is

In these levels collision is Deli Counter's greybox, and the thing a body sees is a separate Zoo module instanced
over it. So the F3 overlay's physics ray names `slab_col_1` and never the floor tile on top of it. The handler
(`tools/walk_asset_flags.gd`) therefore picks by render first: the camera's ray against the triangles of the
visible meshes, nearest first, within 60 m. It names the asset by the nearest instanced ancestor's file. For example,
`res://lot/deli_a01/art/zoo/wall_delco_1997_02_w200_mdrywall.glb` is the module
`wall_delco_1997_02_w200_mdrywall` in the building `deli_a01`. The physics hit is recorded beside it, and stands in
when no mesh is hit; the record's `how` says which.

## What a flag leaves on screen (2026-10-19)

The walker's first walk with the keys, on cold run 9334's copy of county_hospital_001 on a rainy night, put five
presses on one parked car. All five landed (five records, five frames), and nothing on screen stayed to say so: the
banner drew at the top-left, under the F3 overlay's panel, and frame 004 of that walk shows it cut off between the
overlay's two panels. The walker then asked: "we should put a red line around an item that is flagged ... green for
looks good, red for needs more work ... and it persists for that session". Shipped by
`patches/patch_walk_asset_flag_outlines.py`:

- **The box** goes round the nearest instanced ancestor when that was instanced from a model (a GLB: a Zoo module, a
  prop such as the car), and otherwise round the node picked, which the banner then names by its path under the
  scene it sits in (`sidewalk_1L_1/mesh_t0_0`). Otherwise means a scene: a building's own `lot/<arch>/site.tscn`, or
  the level's `presentation/lux.applied.tscn`, which holds the whole site.
- **It is held 3 cm off the bounds**, its edges 2.5 cm beams plus a one-pixel line, unshaded and unfogged, and drawn
  pulled 10 cm toward the eye, so an edge that lands just inside the slab a flush wall module meets still draws. Two
  draw calls a box, in a debug walk only. The picks skip the boxes.
- **Flags from an earlier walk are in the file, not on screen** -- the walker's "for that session".

**REFUTED, kept.** The first rule was "box the ancestor unless it is a scene at the package's root". On the real
level a press on the sidewalk beside the car boxed the whole site, 760 m across, the banner calling it
`lux.applied`: the site is `presentation/lux.applied.tscn`, not at the root. And a press turned toward the street's
buildings picked Lux's horizon glow 405 m off, a mesh whose bounds hold every camera in the level: the pick's comment
said "none within RAY_LENGTH" and its triangle test did not hold it. Both fixed before shipping; both have checks.

### The proof

- `selftest.out.txt`: `tools/walk_asset_flags_selftest.gd` headless, 43 checks, 0 failed. The patch's own records
  (`patches/walk_asset_flag_outlines/`) hold the same selftest against the unpatched handler (24 fail) and against
  three handlers each missing one fix -- the skip (1 fails), the reach (9) and the target rule, put back to the
  refuted one (6) -- so each check is shown able to fail.
- `outline_frames/`: `outline_frames.py` runs `outline_frame.gd` on a mirror of the walk copy, in a 1152 x 648 window
  like the walker's, pressing from where the walker stood (their flags 1 and 4) and from four places worked from
  them. `outline_frames.json` holds each press's record and every box drawn, in Godot metres:

  | frame | press | picked | boxed |
  |---|---|---|---|
  | `p_behind_the_car` | P | the car, by render, 2.29 m | the car, 1.84 x 1.50 x 4.88 m, red |
  | `g_beside_the_car` | G | the car, 1.31 m | the same box, green |
  | `p_nine_metres_back` | P | the car, 8.37 m | the same box, red |
  | `p_turned_left` | P | the step van, by physics, 11.88 m | the van, 2.68 x 3.13 x 6.88 m |
  | `p_ground_right_of_the_car` | P | a sidewalk mesh, 3.26 m | that section, 3.09 x 0.18 x 25.41 m |
  | `p_nearest_building_wall` | P | the hospital's wall module, 5.00 m | `b0/ext_0_W_seg9`, 0.39 x 3.38 x 2.08 m |

  Godot 4.7, GL Compatibility, an RTX 2060; no line of its output said ERROR or SHADER. Not shown by these frames: a
  flush wall module seen from a room, where the pull is meant to keep a box's top edge out of the ceiling.

## The ledger so far

`LEDGER.md`, `ledger.json`, `frames/`: the walker's five flags of 2026-10-19, one asset,
`prop_simple_car_delco_1997_02_w175_d480_h142`, as **needs love**. They were pressed G; the walker, the same evening:
"oh yes i meant to use the needs work". Their records in the walk copy carry `verdict_pressed: "good"` beside the
corrected verdict, and the copy keeps the file as pressed (`asset_flags.as_pressed.jsonl`). Flags 002 and 003 share a
second and a camera: one press read twice, or two presses. The frames keep the names they were saved under.

**Known gaps.** A MultiMesh, such as Lot's surface dressing, is not a MeshInstance3D, so the physics hit stands in for
it. Merged Empties' meshes carry their merged name, not a module's. A pick in the level's own scene -- a sidewalk, a
kerb, a road -- is BOXED by itself but RECORDED under the level's file, so the ledger files every such flag under
`lux.applied`; the record wants the boxed node beside the asset, and the ledger wants to key on it. And the keys see
only what a walk passes; a review board over every species would be the systematic sweep.

**What would close 253:** the walker flags assets on a walk, and the ledger names each one rightly, its frames
beside it.
