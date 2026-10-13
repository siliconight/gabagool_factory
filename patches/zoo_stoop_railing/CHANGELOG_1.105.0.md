## [1.105.0] - a stoop's iron railing: a level section along the landing, a flight down the steps

**Factory roadmap 240, the walker's calls of 2026-10-13**: "3 risers, concrete, railings both sides --
build the railings". The comps' rowhouse street has "three or four steps up to each door, with iron
railings" (the factory's `docs/reference/PHILLY_STREET_COMPS.md`); Deli Counter 0.211.0 built the steps.
Deli Counter 0.212.0 stands one railing a side as two slots of this species.

- **`stoop_railing`**, laid out in pure Python by `core/stoop_railing_forms.py` and built vertex for
  vertex through `bpylayer.prim_mesh` (the utility pole's pattern). Both forms are drawn from the slot's
  box alone, so a stoop of any rise or run is drawn without the module knowing it:
  - `level`: a post at each end, the top rail between them, the bottom rail and the pickets;
  - `flight`: a post at its low end on the bottom tread, the top rail from 36 in over the post's foot
    there to the box's top at the high end, where it meets the level section's post; the bottom rail
    parallel; the pickets sheared to the rails' pitch, so their ends stay in the rails at any pitch.
- **The numbers are the code's where it speaks** (IRC R311.7.8, R312, as adopting jurisdictions
  reproduce them). A handrail is 34 to 38 in over the nosings, drawn at 36. Pickets stand at 4 in
  clear, the guard rule's sphere. The bottom rail's underside is 9 cm up, inside the stair's 6 in
  triangle. A three-riser stoop needs neither handrail nor guard by that code: the comps' railing is
  drawn, at the code's numbers. The iron is the common ornamental sizes: a 1-1/4 in post, a 1-1/2 x 3/4
  in top rail, a 1 in bottom rail, and 5/8 in pickets, drawn a size up from the usual 1/2 in so a
  picket holds a pixel further out.
- **No face of one part lies on another's.** A rail's end stops 4 mm inside its post, a picket's ends
  lie on the rails' centre lines, a post stands 6 mm over the top rail, and each member is 3 mm a side
  narrower than the one it runs into. `prims.coincident_pairs` reads none over 60 sizes of both forms;
  its control sees a planted pair.
- **One material, one part, one submission:** black painted iron (`metal_painted`, its styles' colour
  0.06 / 0.06 / 0.065, worn by theme). **No collision** (`collision: false`): Deli Counter writes the
  railing's colliders with the stoop's, in the greybox the graders walk. Zoo's colliders are axis-aligned
  boxes, and one around a flight would stand a third of a metre over its low end.
- `stair_rail` -- the retro era's structural railing, stepped and chunky, five objects a run -- is
  left as it is. No building places it, and its role and intent tests are its own.

**Measured, Blender 5.1.1:**

- `blender -b --python tools/coplanar_census.py -- --species stoop_railing bollard`: the railing's three
  corners build at 72 / 132 / 240 tris with 0 pairs. The bollard is the control that the census sees a
  pair: its known 2 / 2 / 1. "6 builds, 3 with coincident pairs, 0 that did not build". `CENSUS_BUILDS`
  390 -> 393, and 240 is the genome's budget.
- Both forms through `zoo_cli --build-kit`, on slots shaped as Deli Counter 0.212.0 writes them: PASS.
  `..._w90_d4_h91_flevel` is 132 tris and `..._w52_d4_h127_fflight` 84, each one mesh, one primitive
  and one material, bounds the slot's to the millimetre, each built once for its two sides.

**Suite:** 4,566 passed, 449 skipped, 1 xfailed in 5 min 48 s, where 1.104.0 passed 4,192: the new file's 369 and the five material-option checks the sweep runs on every genome. The new file fails to collect on 1.104.0, run against an export of it. The one new skip is `test_recipe_that_builds_materials_reads_its_genome[stoop_railing]`, "builds no materials": it sees only a direct `make_material` call, and this recipe builds through `prim_mesh` as the utility pole does
