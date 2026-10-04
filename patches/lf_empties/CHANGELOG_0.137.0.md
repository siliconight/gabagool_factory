## [0.137.0] - Empties across the street

Roadmap 106. The walker, 2026-10-04: Empties -- non-enterable buildings --
stand around the walkable level and across its streets, so the far side of
the through road is a street and not the plate's blank perimeter wall.
Deli Counter 0.174.0 builds the first family, six rowhomes with real fronts;
the comps and the agreed families are in the factory root's
`docs/reference/EMPTIES_COMPS.md`.

`empties: "across"` on the brief (opt-in, in the functional signature only
when set, so no evaluated mission moves) stands a terrace of them along the
far side of the through road. `packages/pipeline/empties.py` lays it out:
- **On one line.** Every Empty is turned to face the road, its street edge
  (read per side off its collider hulls, `street_line.shell_extents`) on
  one line 2.0 m behind the far sidewalk -- the near side's own frontage.
- **Varied.** No two neighbours are the same shell, and an alley of 3 m
  breaks the row every five to eight houses.
- **Clear of roads.** It stays 4 m in from the plate's ends and off any road
  that runs south (its band and frontage).
- **On the plate.** The plate grows to hold the row's backs.

The Empties are Lot `blockers` -- instanced from a shell scene like a
building, read by no walk, dumpster, field or entry gate.

THEMED LIKE THE BUILDINGS. `building_library.empties_for_brief` is one list
for three readers:
- the planner, which fans each Empty's art jobs out: its kit, its Patina
  pass, its dressing. No fixtures and no fixture gate: an Empty has no
  lights, its lit windows are to be paint, so `require_art_inputs` is not
  asked of it;
- the compose rows, so each is composed into `lot/<id>/site.tscn`;
- the site spec, which stands the themed scene where compose published it
  and the greybox shell otherwise.

`empty_rows` offers only what Deli Counter calls a facade and prefixes
`gs_empty_`; the two sealed boxes from before are not.

Also: the Deli Counter adapter's preset set learns `empty_rowhome`; the
front-door survey (0.132.0) skips Empties, which have no front door to
find by design.

`tests/unit/test_empties_terrace.py`: every front on one line 2 m behind the
far walk and the plate reaching past the deepest back (literals); no two
neighbours alike, touching within a run, a 3 m alley between runs of five to
eight; on the plate and off a road running south; the same seed the same
row; a brief asks for Empties, only prefixed facades are offered, and the
signature names them only then; the planner themes an Empty without fixtures.
The cold run that puts them in a level is 9146.
