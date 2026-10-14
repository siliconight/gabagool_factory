## [0.220.0] - a walk-up stands a fire escape on its front, a storey a slot

**Factory roadmaps 156 and 241.** The walker's photo of a brick walk-up: "this is something i'd like to see in our
toolset, fireescape stairs brick". Zoo 1.110.0 draws a fire escape a storey at a time (`fire_escape`); this stands
one on the urban street's walk-ups (the factory root's `docs/proposals/FIRE_ESCAPE.md`, step 2).

- **`fire_escape_stack.plan`**, pure: where each storey of it stands, in the building's frame.
  - **Which buildings:** a walk-up, six storeys or fewer (`WALKUP_STOREYS`), and not a corner block, whose awning
    runs the front. CHOSEN, not read from a code: the height a walk-up stops at before a building takes a lift and
    its stairs inside. Of the library's Empties that is `gs_midrise_a`, `_b`, `_g`, `_h` and `_i`.
  - **Where on the front:** centred on the window column at the end farther from the front door, a bay's spacing
    less 0.2 m either side and at most 2.8 m wide, 1.2 m out, its back 8 mm inside the wall's face.
  - **The storeys:** under each landing but the top, a flight bay a storey tall, its deck's top on the storey's
    walking surface -- `flight_a` and `flight_b` alternating from the second storey, so the stack switches back.
    The top landing is `top_a` or `top_b`, whichever the last flight comes up into.
  - **The drop ladder:** under the lowest landing's hatch, in the stair band, its foot 2.2 m over the ground floor.
  - **Zoo's numbers it draws to** (the deck's 2 in, the 36 in guard, the 22 in stair band, the 0.75 m hatch) are
    repeated here, because Deli Counter does not import Zoo. The tests pin them, and read them off Zoo's module
    where the Zoo repo stands beside this one.
- **`LevelSpec.fire_escape_stack`**, a side or None, and the schema carries it (0.218.0's lesson).
- **`_fire_escape_stack`** writes a `prop` slot a storey, and one for the drop, in `metal_painted`, each greyboxed as
  a visual box. No collision: the lowest landing stands a storey up, and Level Factory reads an Empty's street edge
  off its colliders.
- **`presets.empty_midrise(..., fire_escape=None)`:** None asks the walk-up rule; True or False overrides it. A
  block that stands one declares the painted steel in its palette.
- **`build_freshness`** lists `fire_escape_stack.py` among the sources baked into a shell.
- **The specs:** the five walk-ups' regenerated; every other mid-rise and corner block asserted unchanged;
  `specs/CATALOG.md` regenerated.
- **`test_walkup_fire_escape.py`:** on 0.219.0 it fails to collect (`ModuleNotFoundError: No module named 'fire_escape_stack'`). On 0.220.0, 11 of its 12 pass before the build -- its two Zoo checks against Zoo 1.110.0 beside it -- and the twelfth, every built walk-up carrying its stack, fails against 0.219.0's shells and passes after the build.
- **The suite:** `python -m pytest -q`: 1,528 passed, 2 skipped, exit 0, after the build -- 0.219.0's 1,516 and the new file's 12.
- **The build:** `build.py --all`: 154 shells' outputs byte-identical to 0.219.0's and 5 moved -- the five walk-ups, each its GLB and its spec -- none new or gone, by the shells' manifests; the two fuel-stop heist shells' manifests carry no hashes, as before. `gs_midrise_a`'s slots carry its five: three flights, the top landing and the drop.
