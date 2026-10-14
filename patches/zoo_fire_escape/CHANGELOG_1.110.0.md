## [1.110.0] - a steel fire escape, a storey a slot: `fire_escape`

**Factory roadmaps 156 and 241.** The walker, 2026-09-13, with a photo of a brick walk-up: "this is something i'd
like to see in our toolset, fireescape stairs brick". Zoo had a ladder and a stair rail, and no landing, flight or
drop ladder (roadmap 156's survey). Roadmap 241's urban street stands rows of brick walk-ups now, and the factory's
`docs/proposals/FIRE_ESCAPE.md` puts a fire escape on them.

- **`core.fire_escape_forms`**, pure, drawn a storey at a time from a slot's box alone, in Zoo's frame (the wall at
  +Y):
  - `flight_a`, `flight_b`: a landing at the box's bottom, and a flight rising behind its front guard.
    - The landing is a deck frame with slats along the facade, a hatch at one end of its stair band, and guards on
      its three open sides.
    - The flight rises in the stair band, from the hatch's inner edge to the box's top at the far end. Its handrail
      runs along the landing's front line, springing from the front guard.
    - `b` is `a` reflected. A stack alternates and so switches back, each flight coming up through the next
      landing's hatch.
  - `top_a`, `top_b`: the top landing alone. Its guard is the box's height less the deck.
  - `drop`: the drop ladder, two rails and rungs.
  - `auto`: the form the box can be -- a ladder's width is the drop, a storey a flight, the rest a top landing. It
    is listed first in the genome, because a list's first option is a plan's default (`dna._resolve_params`) and
    the coplanar census names no form: its first run drew the min corner, a ladder's size, as a flight and could not.
- **The numbers where a source speaks:**
  - the flight 22 in wide, its risers at most 8 in: 2012 IEBC 405.4, as a code forum quotes it. The ICC's own text
    refused the fetch, so it was not read there;
  - guards 36 in: NFPA 101's existing guard in a dwelling;
  - pickets at 4 in clear, the stoop's.
  - Chosen: the steel's sizes, the 0.75 m hatch and the steep pitch. A 2.8 m bay at a 3.1 m storey has 14 treads of
    4 in at 55.9 degrees.
- **No face of one part lies on another's.**
  - The deck nests in levels; rails sink 10 mm into their posts, deeper than their sections nest, so two meeting in
    one post stay apart; the end guards stand a `NEST` under the front guard.
  - The treads stop a step short of the stringers' end, and the handrail has no foot post.
  - `prims.coincident_pairs` reads none over 1,968 sizes, the extents exact at every one.
  - That sweep found two pairs in the first drafts, kept in the module's docstring: a tread's end a millimetre or two
    off a handrail post's face, and the top tread's end off the stringers' at some storeys.
- **`fire_escape` genome:** `metal_painted`, in the stoop railing's black and styles; `tris_lod0` 1,500 (the most
  is 1,464, a 4 m bay at a 4.5 m storey); no collision. On `test_material_options_closed`'s painted list, and in
  `genome/minted.json`.
- **`tests/test_fire_escape.py`:** on 1.109.0 the module fails to import (`ImportError: cannot import name 'fire_escape_forms' from 'zoo_keeper.core'`). On 1.110.0, 377 pass and the Blender build skips outside Blender; inside Blender 5.1.1, all 378 pass, the build among them.
- **The coplanar census** (`CENSUS_BUILDS` 396 -> 399): `blender -b --python tools/coplanar_census.py -- --species fire_escape bollard`, on a copy of 1.109.0 with these files: "6 builds, 3 with coincident pairs, 0 that did not build" -- the fire escape's three corners 48 / 1,092 / 1,464 tris and 0 pairs, the bollard the control with its known three (`zoo_fire_escape/census.log`).
- **The suite:** `python -m pytest -q tests`: 5,352 passed, 462 skipped, 1 xfailed in 5 min 42 s, where 1.109.0 passed 4,970 and skipped 460 -- the new file's 377 pure checks, and the genome-wide sweeps and the painted list over a new genome; the new file's Blender check, and one sweep's over the new genome, skip outside Blender.
- **Seen** (the factory's `docs/findings/fire_escape/`, `stack_frame.py`): a stack as a five-storey walk-up stands
  it, from the far curb and from under the drop. Workbench frames, the form and not the look; for the walker.
