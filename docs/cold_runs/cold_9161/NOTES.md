# Cold run 9161 -- 0 interventions; TV antennas on the Empties' roofs, and the odd dish: no new mesh, no measurable frame

gas_block_001, seed 9080, `empties: "across"`, `--bake-lights`. The first run
priced with Level Factory 0.141.0's two-pass harness.

**Stack.** The comps' rowhome has "a TV antenna on the roof", and the street
has "the odd early satellite dish".
- **Deli Counter 0.185.0** authors them per house: an antenna on 8 of the 12
  rowhomes, a dish on 2. It writes them on the roof slot with `front`, the
  facing of the wall that holds the front door.
- **Patina 0.29.0** orders them on the roof, set back from the front
  parapet so a street-level eye sees them. The antenna's boom points at the
  transmitter (325, Roxborough) and the dish faces the satellite (211).
  Each house draws its own, keyed by its building id.
- **Zoo 1.74.0** builds a mast, boom and tapering elements, and an 18-inch
  dish tilted up 41 degrees. Both are in the gutters' white aluminium, so
  they merge into the side's existing metal mesh.

**Result:** every leg ran, `INTERVENTIONS: 0`.
- Shell: 3 candidates, all distinct; 0 blockers.
- Art exited 1 on 55 findings, as before.
- No `STEM COLLISION`.
- The walk copy is this run's.
- The row is 9160's own: same seed, same library, 25 houses. So the price
  compares one layout with itself.

## In the level

`patches/zoo_roof_fixtures/roof_census.py 9161 9160`:
- **14 antennas and 2 dishes** across the 25 houses.
- Every design's dressing GLB has the same mesh count as in 9160 (10 or
  11), with no node renamed.

## Before the run

- **Suites:**
  - Zoo 3,313 passed;
  - Patina 380;
  - Deli Counter's `check.py`, after `build.py --all`, passed every check
    (1,193 tests);
  - Level Factory 1,882.
- **Each new test failed on the version before it:** Zoo 5 of 5 pure tests
  (the Blender one skips there), Patina 8 of 8, Deli Counter 4 of 6.
  Deli Counter's other two are the unchanged-roof control and the
  built-family check, which is vacuous when nothing is asked for.
- **Zoo's Blender test** passed (`patches/zoo_roof_fixtures/run_bpy_test.py`):
  a house's covers with an antenna and a dish merge to the same 8 meshes
  as without them.
- **Stem plan:** 0 collisions in 145 buildings, 8,728 modules, unchanged.
- **Pre-flight** (`patches/zoo_roof_fixtures/preflight_roof.py`, Blender,
  against 9160's manifests and skins), on `b` (antenna and dish), `k` (dish)
  and `d` (antenna, two storeys):
  - the same 11 / 10 / 10 meshes as 9160 for those designs;
  - no new material;
  - renders from across the street and from above.
- **Changed because of the render:** the dish's bowl stood 0.45 m over the
  parapet. From across the road, `k`'s 1.0 m parapet left only the feed arm
  and a sliver of bowl in view, so the bowl went up to 0.6 m.

## Frames

`docs/findings/empties_roof_9161/`.
- From across the street, the antennas stand against the night sky over
  the roofline, each at its own height.
- `patches/zoo_roof_fixtures/project_antennas.py` puts each placed
  antenna's parts through the shot's camera. All four in the street frame
  land where the frame shows them. For example, `j`'s mast top projects to
  (225, 125) and the frame has it there.

**Found in the same frame, and NOT this run's:** two long dashed lines in
the sky over `gs_empty_rowhome_l`'s roof. They are in 9160's frame from the
same camera, before any antenna existed. No antenna projects onto them.
- **What the projection supports:** the gutter Patina hangs along the top
  of the taller neighbour's (`e10`, `f`) west party wall projects from
  (865, 201) to (751, 283). That is the lines' slope, about 30 px lower
  than they are drawn.
- **What it would mean:** lit covers along a party wall exposed above a
  two-storey neighbour, against an unlit wall. They read as lines floating
  in the sky.
- **Not established:** which covers they are. The 30 px is unexplained;
  the roof's edge strip along the same wall is the candidate.
- **Worth acting on either way:** Patina gutters every top-storey wall,
  party walls included. A rowhouse roof drains front and back, and the
  downspouts already keep to faces with openings.

## The price

A = 9160's package, B = 9161's, A2 = 9160's again, with the two-pass
harness (`price_roof.txt`, `price_roof_robust.txt`).
- **Draws:** median 0, mean +0.55 a view; at most +10, at camera_socket_0
  180. The control is 0 at every heading. Where the +10 comes from is not
  established. A merged metal mesh that now reaches 3 m higher, and so
  survives culling at a few more views, is an untested candidate.
- **Median frame**, against the mean of A and A2 over all 53 headings:
  +0.012 ms. The control's median is -0.037, and **none of its headings
  disagreed by more than 1 ms**: the first price taken with passes.
- **Light census:** 61 over the cap, unchanged.

## The ceiling on the Empties' cost (the walker's "then optimise them")

The same package with every Empty hidden
(`patches/lf_empties/make_noempties.py`: `visible = false` on the 25
`blocker_*` nodes in `presentation/lux.applied.tscn`), against 9161 twice
(`docs/findings/empties_ceiling_9161/`).
- **Draws:** median -816 a view, mean -1,210, up to -3,951. This is
  robust; the control's draws differed by at most 84.
- **Frame: not usable from this set.** The second 9161 run was slower than
  the first at every heading (median +1.09 ms, never below +0.22). Its own
  passes disagreed by more than 1 ms at 17 headings, and the hidden run's
  at 21 (largest 34 ms). The first three runs of the session were quiet
  (0 to 3). The machine changed under the last two -- an antivirus agent
  was at about 15 % CPU afterwards -- and the frame half is to be measured
  again, interleaved, with a cool-down between runs.
