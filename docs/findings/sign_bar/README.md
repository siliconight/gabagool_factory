# The bar on the door sign (roadmap 220)

**Question.** Cold run 9217's frames showed a thin, light, vertical bar at the
centre of strip_club_a01's door sign. It ran from about mid-text down to the
bottom rule, and 9213 had it too (`docs/cold_runs/cold_9217/sign_bar_9213_9217.png`).
What draws it?

**Answer.** Patina's conduit run to the sign. It is a 0.05 x 0.04 x 0.27 m
concrete box standing on the sign's face plane, from the door head to the
face's middle.
- **The cause:** `anchors.conduit_targets` took Deli Counter's `sign` anchor
  as a conduit target, at its own position. That position is the sign's FACE,
  `_SIGN_OUT` (0.2 m) proud of the wall.
- **The stub:** the run went from the ground up to the face's centre.
  `openings.apply` then started it above the door the sign hangs over, which
  left the stub. 9217 ordered one on all three of its signed buildings:
  airport_terminal_a02, funeral_home_a03 and strip_club_a01.
- **Fixed by Patina 0.29.2:** a sign is no longer a conduit target. A cabinet
  sign is fed through the wall behind it.

**Frame and units.**
- Positions are in Godot metres, Y up. On the walk copy the club stands at
  (-62, 0, 2), unturned.
- "Building-local" means the club's GLBs' own glTF frame. "Spec" means Deli
  Counter's Z-up frame, which Patina's orders use.
- Luma is Rec.709 on the 8-bit frame, 0 to 255.
- Everything here was measured on cold run 9217's walk copy
  (`_runs/walk_export_club_block_014`).

## What was measured, in order

1. **`light_breakdown` at two sign stations**, head-on and 2 m to the side
   (`sign_head`, `sign_side`). See `bake_on_off.png`.
   - With the bake switched off the bar is still there, now dark against the
     emissive face.
   - So it is a lit object, not the face's texture and not its emission.
   - Live lamps and emission switched off changed nothing about it.
2. **`hide_and_seek.gd`**, in the walked level itself. It hid each
   VisualInstance3D within 2 m of the bar in turn and measured the bar's
   screen strip against the face beside it. See `hide_and_seek.log` and
   `hide_and_seek.png`.
   - Of 19 candidates, one moved it: `b0/Dressing/CoverN_concrete_delco_1997`,
     243 -> 90, against the face's 122.
   - Hiding the sign's own face left the bar standing (242.3), so the bar
     is in front of the face.
3. **That mesh in the club's dressing GLB.** Among its 2,772 triangles is a
   box at building-local x -5.025..-4.975, y 2.28..2.55, z 12.33..12.37.
   - The sign's face is the plane z = 12.35, centred at x = -5.0.
   - So the box straddles the face by 2 cm either way, from the door head
     (2.28) to the face's middle (2.55).
4. **The order behind it**, in Patina's `strip_club_a01.patina.dressing.json`
   from 9217's job:
   - `conduit_run`, pos (-5.0, -12.35, 2.415), size 0.27, `clipped_by`
     `ext_0_S_open0`;
   - the sign's anchor in `deli_counter/build/strip_club_a01.lights.json` is
     (-5.0, -12.35, 2.55).

## Refuted on the way (kept)

- **"Nothing stands in front of the face."** This was the first reading of
  `near_sign.gd`'s AABB census. The census DID list the culprit:
  `CoverN_concrete`'s box reached z 14.37, 2 cm in front of the face at
  14.35. It was set aside because a merged mesh's box spans its whole
  building, and its name said north while the sign faces south.
  - An AABB census can say that a merged mesh reaches a point. It cannot say
    which of its parts does.
  - Hiding things and looking settled it.
- **"Not a thing standing off the face"** (9217's notes). The parallax was
  read correctly: the bar keeps its place between the letters, because it
  straddles the face plane. The conclusion drawn from it, that the bar
  belonged to the face, was wrong.

## Found alongside, not fixed here (roadmap 221)

Patina's anchor-derived wall covers face INTO the building. In 9217's club
orders, in the spec frame:
- the south door's conduit has normal +y, and every west-face base course
  +x;
- the slot-derived gutters and downspouts face out, as they should.

Zoo's `dressing.cover_side` puts a wall-facing cover on the side its normal
leaves. So base courses and conduits merge with the opposite face's covers,
and roadmap 180's per-side merge no longer culls by side for concrete.

Vertex counts of each merged mesh, by the building face they lie on
(strip_club_a01's dressing GLB):

| mesh | its own face | the opposite face |
|---|---|---|
| CoverN_concrete | N 2,544 | S 480 |
| CoverS_concrete | S 1,344 | N 1,008 |
| CoverE_concrete | E 912 | W 672 |
| CoverW_concrete | W 1,008 | E 432 |

The four painted-metal meshes (gutters, downspouts) each lie on their own
face only.

Two smaller findings:
- **Buried base courses.** 22 of the 51 base courses stand on a wall's
  centre line, buried in a 0.3 m wall: 9 on the south face at y -12.000, 7
  west, 6 north. The other 29 stand on its outer face.
- **The wall packs' conduits still stand at the pack,** 0.15 m proud
  (`_WALL_PACK_OUT`). Each is a 0.17 m stub from the door head to the
  pack's housing, off the wall.

## Instruments

- `near_sign.gd`: headless. Every drawn node whose world box meets a box
  around the sign, with its materials.
- `hide_and_seek.gd`: windowed. Hides each candidate in turn and measures
  the bar.

      godot --path <walk project> --script <this>/hide_and_seek.gd -- -67.0,2.0,17.5 -67.0,2.5,14.34 -67.0,2.30,2.52,14.36 <out dir>

- `tools/light_breakdown.py` with the two `--station`s named above, and
  `--sources lightmap,live,emission`.
