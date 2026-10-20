# Cold run 9339 -- restaurant_row_001 on Deli Counter 0.235.0 (2026-10-19): the drop off the kitchen wall, proven

Staged from 9338. The tool change since 9338 is Deli Counter 0.235.0 (4fed8011, `patches/patch_dc_ceiling_holes.py`,
the factory's roadmap 260): layout_lint L27, a wall under a hole in its ceiling, and the open-floor table sliding a hole
off a wall it stands. This lot's deli, deli_a03 (`b0`), is one of the six it moved: its 2.2 m "vertical attack angle"
drop went from spec (8, -4) to (8.5, -4), x 7.4..9.6, off the kitchen wall at x 7 and wholly over the kitchen.
deli_a03's furniture did not move; the refurnish moved pieces only in corner_deli_heist_01, cr_deli and night_deli.

**Run:** 0 interventions (journal 0, unattributed files 0), DONE, drive 8.7 min. The pick is seed 9003, PASS 90, as
every candidate graded on 9338; findings 81 / 110, as on 9338.

**What moved against 9338**, each read off the two packages (`workspaces/cold-9338-ws` and `cold-9339-ws`, the
exported `LF_restaurant_row_001.portable-godot`):

- The drop's nav link (`navigation_hints.json`, `lot:deli_a03_floor_hole_1_8_-4_navlink`) moved from x -43.0 to
  -42.5, and the hole it carries from x -44.1..-41.9 to -43.6..-41.4. It still falls from the first floor (y 3.3) to
  the ground (0.0) at plan y -1.49. The kitchen wall's centreline is at x -44.0 and its kitchen face at -43.825, so
  the hole that took the wall in on 9338 now stops 0.225 m short of its face. The link's id still reads `8_-4`: the
  builder writes a link's position into its id as whole metres (`%d`), so 8.5 reads as 8 -- an id, not a position.
- The drop-edge gate: 55,454 reached of 63,919 standable cells, as on 9338; 52 unguarded edges against 45 -- 11 a
  flight's own side, 20 at a declared drop (13 on 9338, 20 on 9335), 13 at a ladder's shaft, 8 outdoors -- and 0
  undeclared. The seven rows 9338 lost on the first floor's slab are back as declared drop edges: the hole's rim no
  longer looks down onto a wall's top.
- Nothing else checked moved: `interactives.json` is identical to 9338's (33 interactives, 23 of them doors, the
  kitchen door `b0 int_0_6_open0` and the slid stockroom gate among them); lightmap users 3,514, as on 9338.

**Frames:** `_scratch/review/shots_9339/` and `shots_9339i/` (the work light), the same four stations as 9338's,
given by hand from the package's own coordinates: the kitchen door from the aisles, the hole from the kitchen, the
hole from above, and the slid gate.

`hole_9338_vs_9339.jpg` (here) sets the two hole stations side by side, in the work light. From above, 9338's hole
shows a bright strip just inside its far edge -- the wall's top, 0.3 m down -- and 9339's shows none: the far side is
the slab's own cut face, full depth, with the wall's face below it. From the kitchen, 9338's hole runs into the wall,
which carries on up into the opening; 9339's is a whole rectangle, its four cut faces showing, with a strip of ceiling
between it and the wall, and the kitchen door beside it rather than under it.
