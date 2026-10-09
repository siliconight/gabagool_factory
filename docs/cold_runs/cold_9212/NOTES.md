# Cold run 9212 -- 0 interventions; the payphone, redrawn, in the level

club_block_014, seed auto, staged from cold run 9211. It tests **Zoo 1.88.0**
(roadmap 210): the payphone redrawn as a coin phone on an armoured cord, in
one of three enclosures, one atlas and one draw. The finding is
`docs/findings/payphone_redraw/`.

Tool versions hashed at `--begin`: Zoo 1.88.0, Lot 0.102.0, Level Factory
0.163.0, Laser Tag 0.25.0, Deli Counter 0.203.0, Lux 0.69.0, Dispatch 0.5.2,
Patina 0.29.1, Pixelcoat 0.61.0, Pipeline 0.6.0. Only Zoo moved since 9211.

**`INTERVENTIONS: 0`** (journal 0, unattributed files 0). Every leg ran.

**Picked: seed_9181**, on the same figures as 9206 to 9211.

**What held:**
- **Findings: 72 to 72.**
- **The art leg:** 0 blockers.
- **The light bake:** 432 models lightmapped and 7 kept dynamic, as before.
  Its users went from 3,898 to 3,892: three payphones, each 3 meshes before
  and 1 now.

## Where the level carries a payphone

Three, all built `auto`, so all three are booths:
- **One on the street,** `cover_101`, at Lot's bus stop: Godot
  (34.45, 1.25, -2.08), its open front to +X.
- **Two indoors,** Deli Counter's: the airport terminal (`airport_terminal_a02`)
  and the funeral home (`funeral_home_a03`). Each is `_mmetal`, style 4,
  against a wall.

## The package against 9211's

`docs/findings/weighted_normals/pkg_diff.py`, output `pkg_diff.txt`.

**What the redraw moved:**
- **The payphone GLBs:** 3 differ, the three payphones, each with a new mesh
  (their JSON chunks differ).
- **Their atlases:** 3 new, `Payphone_256x1243_*.png`, one beside each GLB
  as Zoo's texture sharing writes them.
- **The old handset's two plastic textures** have left `cover/`.
- **The bake.**

**What the pipeline moved on its own,** as the 9209-9210 control showed it
does with Zoo unchanged:
- five fixture and dressing GLBs, re-ordered, with the same triangles as
  multisets;
- the import sidecars, `.tscn` ordering and the manifests.

## The price

The weighted-normals method (`docs/findings/weighted_normals/README.md`):
- **The four runs:** `_runs/perf_inner/run.py` on 9211's package (`pp_off`),
  9212's (`pp_on`), 9211's again (`pp_off2`, the control) and 9212's again
  (`pp_on2`).
- **The harness:** Level Factory's fixed stations, 53 headings, GL
  Compatibility.
- **The reading:** `patches/zoo_cover_merge/price_robust.py`, against the
  mean of the two controls; output `price_robust.txt`, reports
  `pp_*.json` and `.log`.

| | median frame moved | mean | range |
|---|---|---|---|
| the controls, one against the other (stable headings) | -0.009 ms | +0.048 | -0.389 to +0.542 |
| `pp_on` | +0.029 ms | +0.024 | -0.468 to +0.565 |
| `pp_on2` | +0.079 ms | +0.064 | -0.342 to +0.910 |

- **The frame:** nothing measurable.
- **The draws:** 21 of 53 headings drop by 2 to 8, identically in both
  runs, and the controls agree with each other at all 21.
  - 2 is one payphone in view going from 3 draws to 1.
  - The larger drops are one in a shadow pass too, or more than one in view.
- **The one other heading that moved,** `patrol_point_18` at 180, differs
  between the two controls themselves (639 against 479). That is the
  harness keeping whichever of its two passes had the lower p95.
- **The scene:** 3,948 meshes against 3,954, and the 8-light cap the same,
  33 over.

## The payphone in the level, at midnight

`tools/look_shots.py` on the walk copy, two given stations on the sidewalk
side. Manifest: `payphone_shots_manifest.json`. Frame:
`payphone_in_level.png`.
- **Lot faces it to the sidewalk, back to the traffic.** `_stop_corner`
  turns the payphone 180 degrees from the mailbox and the racks, and
  `plate_facing` (Godot reads the transform's numbers as basis rows, as
  measured there) puts its open front toward the buildings. A kerbside
  payphone faces that way, so a caller stands on the pavement and not in
  the road.
- **Retracted, kept: "the booth faces the wall".** The first two shots
  stood the camera in the street, on the booth's back, and read the
  transform's numbers as columns. That was the wrong convention:
  `plate_facing` had it written down. The shots above are from the
  sidewalk.
- **At midnight the booth reads as a silhouette.** Its roof shades the
  instrument, and no light reaches the card, the keys or the stickers.
  1.87.0's half-booth was as dark.
  - **The fix is light, not art:** a backlit header (an emissive tile,
    the ATM topper's way) and a hood lamp at `ATT_hood`, which the recipe
    has carried for exactly that.
  - **Its cost:** one more draw a payphone (2, against 3 before the
    redraw). It is the walker's to call.
