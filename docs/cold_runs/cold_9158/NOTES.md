# Cold run 9158 -- 0 interventions; the Empties' front doors painted house by house, two iron security doors

gas_block_001, seed 9080, `empties: "across"`, `--bake-lights`.

**Stack:**
- Deli Counter 0.182.0 authors each rowhome's front door on its spec,
  `door_finish` and `security_door`:
  - a navy + iron;
  - b white;
  - c oxblood;
  - d green;
  - e black + iron (the vacant one);
  - f stained.

  It carries them on the front door's slot, and names the finish into the
  module as `_e<finish>`.
- Zoo 1.72.0 paints the leaf in the finish (`core/doors.py`) and builds the
  security door in the bars' iron.
- Patina 0.28.0 orders the security door.
- Unchanged: 9157's seams, trim and fixtures.

**Result:** every leg ran in 33 minutes, `INTERVENTIONS: 0`. Art exited 1
on 55 findings, as before. No `STEM COLLISION`. The walk copy is this
run's.

## Why authored

A seeded draw over the six rowhomes, computed before writing the code, gave
three finishes (green, green, navy, navy, stained, stained) and no iron door
at all.
- That is the same failure that made `vacant` authored rather than drawn
  (0.179.0).
- The family table now says each house's door, as it says its wall.

## Found on the way, fixed before shipping

**The first build wrote a house's finish as -0.22.** The preset
`empty_rowhome` already had a local `door`, the front door's POSITION along
the wall, and a new parameter of that name was shadowed by it.
`empty_panes.door` refused the value, which is what it is for. The
parameter is `door_finish`, the patch says why, and the patch was re-applied
from a clean tree so it records what shipped.

## Before the run

- **Tests:**
  - every suite passed: Deli Counter's `check.py` after `build.py --all`,
    with 138 shells through the nav gate; Patina 372; Zoo 3,306;
  - each new test failed on the version before it.
- **Planning:** Zoo planned all 139 built buildings with 0 stem collisions.
- **The Blender pre-flight on rowhome_a** (`patches/zoo_front_doors/preflight_doors.py`):
  - the front doorway module is `..._mbrick_enavy_o3e3b2d`, its leaf
    `M_Skin_metal_painted_delco_1997_212b45`, the navy tint;
  - the back door is unchanged, `wood_panel`;
  - the security door merges into the south side's iron with the bars;
  - it hangs at y -6.09..-6.13 against the face at -6.15 (2-6 cm into the
    reveal, in front of the leaf), z 0.005-2.295 in the 2.3 m opening, and
    5 mm clear of each jamb.

## What the run built

- **Dressing:** rowhome e, a security door and no bars, gains one iron
  mesh. Rowhome a's joins its bars. Lightmap users went 5,190 -> 5,192: e's
  two placements.
- **Frames:** `docs/findings/empties_doors_9158/`;
  `doors_closeups_9158.png` crops five front doors across the street:
  - oxblood under its lintel, twice (two placements of c);
  - green on the stone house;
  - stained wood;
  - a navy door behind an iron grille.

## The price

A = 9157's package, B = 9158's, A2 = 9157's again: 53 station x heading
pairs, back to back. All 53 are stable between A and A2.

- **Draws:** median 0, mean +0.6, at most +3 a view. The control: 0.
- **Median frame**, against the mean of A and A2: median +0.018 ms. The
  control's own median is +0.005, so the median view's cost is about
  0.01 ms.
- **The light census:** 61 meshes over the cap, the same 61.
- **Three headings rose 1-3 ms with no draw changed at all**, a hitch in
  run B:
  - defender_spawn_21 at 270: +3.06 ms, p95 5.2 -> 13.7;
  - camera_socket_0 at 270: +2.25 ms;
  - defender_spawn_21 at 0: +1.17 ms.

  They are why the mean reads +0.148.

**The instrument, again.** It is the third run in a row in which one of
three runs hitches at a few headings: camera_socket_6 at 270 in 9155 and
9156, defender_spawn_22, and now these. A harness that measures each
heading once turns one hitch into a price. Sampling each heading more than
once, or the whole station set twice, would make a single run believable.

Outputs: `price_doors.txt` (`compare_price.py`) and
`price_doors_robust.txt` (`price_robust.py`).
