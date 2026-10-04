## [0.177.0] - A parapet is a wall the art pass dresses

Nothing ever skinned a parapet. Cold run 9148's package carried 324 greybox
surfaces (2,744.7 m2 in `gb_wall`), every one a `parapet_*`, attributed per
archetype off the shipped bases:
- 260 on the 26 Empties, where the parapet is the cornice: a grey band along
  the top of every house;
- 64 on the bank tower and the freight terminal.

The worldskin has a pass for slabs, stairs and ladders and none for
parapets. The greybox gate counts parapets and does not refuse them.

A parapet is the wall below it carried past the roof, so it is recorded as
that wall. For a modular build, `_parapets` records one wall slot per visual
tile (`_record_parapet_slot`):
- **Named as the tile**, so the composer's base strip removes exactly that
  greybox piece, as it does for a wall segment.
- **In the material of the top storey's wall on that side**: an explicit
  `ext_walls` entry when there is one, else the default.
- **Exterior on both faces.** Its inner face looks onto the roof, so it
  carries no `material_in`.
- **Its own height.** Where a parapet tile shares a width with a storey wall,
  0.176.0's `mark_height_keys` keeps the two names apart.

Zoo builds each as a wall module, exact-fit, collision as a wall's. The
greybox collision box (`parapet_<side>_col`) is unchanged.

`test_parapet_slots.py`:
- every tile is a wall slot named as the tile, in the wall-below's material
  -- a siding front over a brick house gives a siding front parapet and
  brick sides (fails on 0.176.0);
- the control: a non-modular build records none.

The library-wide name check (0.176.0) then caught a smaller collision the
new slots exposed. `floors.slab_tiles` snaps interior cuts to whole
millimetres, so a parapet run's equal tiles can be 4.666 and 4.667 m, both
named `w467`. A name carries centimetres, so they are one module. The check
and `mark_height_keys` now both ask at whole centimetres: one question at the
resolution the name can answer.

`themed_tscn.py` joins `build_freshness.GEOMETRY_SOURCES`: since 0.176.0 the
slot manifest's marking is decided there as it is written, and a change to it
moved every slots.json without making a shell stale.

9 library buildings carry parapet tiles and no parapet slots. Every one
records no wall slot at all (non-modular), and keeps its greybox by design.
