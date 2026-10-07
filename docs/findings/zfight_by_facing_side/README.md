# The z-fight gate counted contacts no camera can see

Measured 2026-10-06 on cold run 9189's composed buildings: the
`presentation_compose` job's `out/presentation/lot/<building>/` packages,
read by `zfight_gate`'s own functions (`coplanar_fights`, `visible_fights`,
`check_package`). This answers roadmap item 177's open question, "what are
the pairs", which no one had looked at in five months of FAIL lines.

**Frames and units.** GLB/Godot space: y is up. A pair's `axis` is 0 x, 1 y,
2 z. `side` is `min` when both faces look down their axis and `max` when both
look up it, since a counted pair always faces the same way. Planes are in
metres.

## What the gate counted, and what can be seen

| building | raw pairs | visible, the gate's rule (0.197.0) | buried by it | visible by the side the faces face |
|---|---|---|---|---|
| deli_a01 | 217 | 198 | 19 | **2** |
| office | 121 | 121 | 0 | **2** |
| rail_station_a02 | 117 | 117 | 0 | **1** |
| the 12 Empties | 0 | 0 | 0 | 0 |

**431 of the 436 were faces no camera can reach.**
- **Bottoms pressed on a slab:** a chair, counter, stool, shelf or cabinet
  and the room's floor module it stands in, or a stair tread and the
  stairwell's floor module. Both bottoms sit on the slab's top, facing down
  into it.
- **Caps sunk under the next slab:** crossing partitions' tops, 4 mm under
  the slab above, where the composer sinks wall-family modules
  (`themed_tscn.SLAB_CAP_SINK`).
- **Pieces over tile seams:** a desk or counter island standing across four
  slab tiles that meet in a corner under it.

**Why the gate saw them.** It buried a pair only inside a solid with matter
on BOTH sides of the plane. That holds for a wall's end inside another
wall's band, and never for a face pressed against a slab.

**The rule, Deli Counter 0.198.0.** A same-facing pair can be seen only from
the side its faces face. It is buried when solids starting within
`OUTWARD_GAP` of the plane on that side cover the shared rectangle, alone or
together in 2-D, to the gate's tolerance.
- `OUTWARD_GAP` is `SLAB_CAP_SINK + TOL`, 5.5 mm.
- A 5 cm gap reads the same on all three buildings.
- A "ground" rule (nothing below a building's lowest floor) adds nothing.

## Refuted, kept

- **The census's first 2-D cover had no tolerance.** It called every float32
  seam between slab tiles a hole: 9189's tiles meet at -9.333000183 and
  -9.332999944, 2.4e-7 m apart. It left 31 of deli_a01's pairs where the
  tolerant version leaves 2. Caught because a first, simpler pass had left
  9, and a stricter instrument cannot leave more than a laxer one.
- **The simpler first pass left 9, not 2.** It used the gate's 1-D joint
  cover, which needs one box to span the shared rectangle across, and it
  had no gap allowance for the sunk caps.

## The 5 left: worth a frame

| building | pair | where |
|---|---|---|
| deli_a01 | `ext_0_E_seg10` ~ `int_0_1_seg18`, z -5.825 (max) and -6.175 (min), 0.90 m2 | a partition's end inside the east exterior wall, where one wall segment is exactly the partition's width; the next segment toward the window at level y 7 may be the opening |
| rail_station_a02 | `ext_0_E_seg8` ~ `int_0_0_seg19`, z -5.150 (min), 0.70 m2 | the same junction shape |
| office | `base:VAULTLEDGE_0` ~ `reception_desk`, x +-2.5, 0.20 m2 each | the reception desk on a greybox ledge of exactly its width, their sides coplanar, facing the room |

**Frames, taken the same day** (`tools/look_shots.py` on 9189's walk copy
of its export, `_runs/walk_export_restaurant_row_001`, at stations given
rather than derived, aimed at each pair's centre):

| frame | mean luminance (/255) |
|---|---|
| `frame_9189_deli_junction_north.jpg` | 24.9 |
| `frame_9189_deli_junction_south.jpg` | 6.1 |
| `frame_9189_office_desk_east.jpg` | 4.1 |
| `frame_9189_office_desk_west.jpg` | 3.9 |
| `frame_9189_rail_junction_north.jpg` | 3.5 |

**What the frames show.**
- **deli_a01, north view:** the only one lit enough to read. It shows the
  corner where the partition meets the east wall beside the window, as a
  dark vertical seam, and no mottled stripe.
- **The other four** are under 7/255: the level's own night lighting.
  Nothing is visible at them, and nothing could be.

**Not established:** whether any of the five flickers when lit or in motion.
A still frame under 7/255 cannot show a coplanar stripe. So whether the gate
should block (177's owed decision) rests on the count alone: 5 pairs with
an open side, none seen on screen.

## Instrument

`zfight_hidden_census.py <compose lot dir> [--list]` counts each building's
raw pairs three ways: the gate's rule, by the facing side, and by the facing
side plus the ground. `ZF_GAP` in the environment sets the gap.
