## [1.92.0] - the box truck and the litter bin, drawn

### What the walker asked for
Roadmap 219 note 5, from the walk of club_block_014 on 2026-10-09: "i dont
know what this giant grey box is". It was `box_truck`. That species and
`litter_bin` were the last two placeholder silhouettes in the library, each
one grey box minted by `tools/new_species.py` on 2026-09-12. Both ship in
club_block_014:
- Lot parks box trucks as cover between buildings (roadmap 22);
- Lot stands a litter bin at each crossing, 1.5 m before the cut.

### `box_truck`: a 1990s cab-over delivery truck, in one of four invented Delco fleets
`recipes/box_truck.py`, every number from `core/box_truck_forms.py`, which
is pure.
- **The shape.** The cab sits over the front wheels: a flat face, a big
  raked windshield, round plan corners. A taller, wider cargo box stands
  behind it on the frame, with a roll-up rear door of slat seams, aluminium
  corner caps and rails. Under it: single front wheels and dual rears, a step
  bumper, frame rails and crossmembers, an aluminium fuel tank on the kerb
  side, and mud flaps.
- **No maker's mark anywhere.** It is not the crew's step van, which is
  one-of-a-kind and parked at the spawn. These are the street's working
  trucks.
- **The glass shows something.** Glass in the windshield and both doors,
  with a dash, two seats and the wheel behind it.
- **The fleets** (`FLEETS`, `module_variants: 4`). Each has its own cab
  colour, a white box, the name on both sides and a stripe along the foot,
  set in the shop's voice, Blue Highway Bold:
  - BLUE ROUTE MOVERS, "WE'VE ONLY DROPPED ONE PIANO";
  - HOAGIE HAUL, "WIT OR WITOUT. WE DELIVER.";
  - NANA'S BASEMENT SELF STORAGE, "WE DON'T ASK WHAT'S IN THE BOXES";
  - DOWN THE SHORE PARTY RENTALS, "TENTS. TABLES. NO REFUNDS."
- **Five materials, so five draws a truck,** the step van's set:
  - the paint: the livery on the box's sides, and the colour per corner in
    `Wear`. The cab's colour is set against the art's margin, so it lands
    exactly on the fleet's;
  - one painted material for every tinted part;
  - rubber;
  - the cab's cloth;
  - its glass.
- **Measured:** 7,918 triangles at the default 2.4 x 6.0 x 2.8 slot and
  8,318 at the largest. The genome's budget is 8,800, a regression
  detector and not a frame cost.
- **Cover, as roadmap 22 wants:** taller than 1.3 m all along. Its
  collision is the slot's box.
- **The slot is exact.** Width is the mirror heads, depth the front bumper
  and the tail lamps, height the box's clearance lamps.

### `litter_bin`: a 1990s municipal street bin
`recipes/litter_bin.py`, from `core/litter_bin_forms.py`.
- **The shape:** a square body of vertical steel slats in the township's
  green, a lid with a square mouth and the black bag showing in it (a cup's
  rim, a wrapper, a flyer), and four short feet.
- **The placard,** LITTER over "KEEP DELCO CLASSY-ISH", is on two faces, in
  an institution's voice (Aileron).
- **One atlas and one material,** so one draw a bin, as the dumpster's is.
  The slats are painted, not modelled: a bin stands at every crossing, so
  its price is its count. 84 triangles.
- `card_art.paint` sends the `litter_` tiles to `litter_bin_forms.paint`.

### Tests
- **`tests/test_box_truck.py`.**
  - The pure checks:
    - the slot's edges;
    - the cab-over's order (the front axle under the cab, the box taller
      and wider);
    - cover all along at the genome's smallest and largest slots;
    - a longer slot is a longer box behind the same cab;
    - the cab's round corners;
    - four fleets, one a variant;
    - no real mark in any fleet;
    - every livery sets;
    - the livery lands on the box's sides and nowhere else;
    - the cab's exact colour;
    - grime rising from the road.
  - The bpy half: exact fit with every part at three slots, five materials,
    and no two faces sharing a plane at the smallest slot.
- **`tests/test_litter_bin.py`.**
  - The pure checks: every prim a quad on the one atlas (84 triangles); the
    slot and the collision; every tile paints and the placard sets; an
    unknown tile is refused.
  - The bpy half: one part and one material at three slots, and no shared
    planes.
- **Run inside Blender 5.1:** both files, 32 passed.
- **Found by those tests and fixed before they passed,** at the genome's
  smallest slot:
  - a seat shared a B-pillar's plane;
  - the bumper bracket's top fell under its bottom.

Suite: 4,081 passed, 414 skipped, 1 xfailed (1.91.0: 4,067, 400 and 1). The new files add 15 passes and 13 Blender skips. `test_recipe_reads_its_genome` now skips the litter bin as it does the dumpster: the recipe builds its material through the shared atlas and calls no `make_material` of its own. Both species' files, run inside Blender 5.1: 32 passed.
