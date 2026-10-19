# Asset flags: G looks good, P needs love (roadmap 253)

The walker, 2026-10-14, after the demo: "I want a way to flag assets that look good and assets that need more
polish/love". Until now a look was judged in chat, frame by frame, and nothing kept the verdicts. This is roadmap
18's missing gate from the walker's side.

## How to use it

1. Walk any walk copy: `_runs/walk_export_<mission>/`, which every cold run builds, or `tools/walk_export.py` by hand.
2. Rest the crosshair on a thing and press **G** if it looks good, **P** if it needs love. A banner says what was
   flagged. Each press appends one record to the copy's `asset_flags.jsonl` and saves a 640-wide frame under its
   `asset_flags/`.
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
visible meshes, nearest first. It names the asset by the nearest instanced ancestor's file. For example,
`res://lot/deli_a01/art/zoo/wall_delco_1997_02_w200_mdrywall.glb` is the module
`wall_delco_1997_02_w200_mdrywall` in the building `deli_a01`. The physics hit is recorded beside it, and stands in
when no mesh is hit; the record's `how` says which.

**Known gaps.** A MultiMesh, such as Lot's surface dressing, is not a MeshInstance3D, so the physics hit stands
in for it. Merged Empties' meshes carry their merged name, not a module's. And the keys see only what a walk
passes; a review board over every species would be the systematic sweep.

## The proof

- `selftest.out.txt`: `tools/walk_asset_flags_selftest.gd` headless, 14 checks. It builds a module over a
  greybox collider, presses G and checks that the record names the module and not the collider. It hides the
  mesh, presses P and checks that the collider stands in. An echo and a key release must write nothing.
- `tools/asset_flags.py --selftest`: counts and ranking per asset, a frame copied, and two unreadable lines
  counted, named and failing the run rather than vanishing.
- `tools/test_walk_export_asset_flags.py`: `walk_export.py` puts the handler in every walk copy.

**What would close 253:** the walker flags assets on a walk, and the ledger names each one rightly, its frames
beside it.
