# A ramp's slab cut ran half a run past its head (Deli Counter 0.241.0)

**How it was found.** Install test 10 (`docs/findings/stranger_install/`), certifying factory 1.41.0: the package
unzipped into a folder that had never held a factory, `setup --venv` clean (0 drift lines), and `make` on the first
level, `docs/first_level/`, with its seed left to the pick. The pick took seed 9205 (PASS 100 over 9003 and 9104),
whose lot stands `deli_a01`, `supermarket_a01` and a `parking_garage` at plan (59, -0.99), and the export **stopped**
at Level Factory's drop-edge gate (roadmap 173): 54 unguarded edges, **33 undeclared indoors**, the class it refuses
(`drop_edges_scan_install_test_10.json`: declared 0, ladder hole 6, outdoors 4, stair side 2, a thing's top 9). The
walk that follows `make` stopped on the same 33. No cold run since the gate shipped (Level Factory 0.216.0) had drawn
a parking garage: they named seed 9003, whose lot has none.

**What the 33 were** (`garage_rows.py` over `drop_edges_install_test_10.json`, the garage's frame, metres;
`garage_rows_install_test_10.out.txt`). The garage's one ramp is a box 3 m wide, centred on (13, 0), climbing 10 m
along +Y from the ground floor at y -5 to storey 1 at y +5 (`Builder._ramps`). `stairwell.ramp_hole` cut storey 1's
slab from y 0 to y 10 and from x 11.3 to 14.7:
- **24 over nothing**: the cut's far half, y 5 to 10 past the ramp's head, and the 0.2 m either side of the ramp,
  rows from storey 1's slab straight down to the ground floor's -- 3.00 m at all of them.
- **9 onto the ramp**: the cut's entry edge at y 0 and its west side, storey 1's slab dropping 0.75 to 1.20 m onto
  the ramp, unguarded.
- Reported, not refused: the ramp's own sides and its top end dropping to the ground floor, which stand on the ramp's
  collider, not a floor (`drop_edges._floor_like`).

**Every library ramp did it** (`ramp_census.py`, `ramp_census_0240.out.txt`): nine ramps in six specs --
cbp_town_finale_midbalanced_schemafixed (three), cr_garage, foundry_heist_vertical, parking_garage, parking_garage_a01
and parking_garage_a02 (two) -- each cut 5 to 8 m past its head, all along Y. `ramp_hole` centred the cut half a run
along +Y with a run's length: "at the head of the climb", its docstring said, but the box it was cut for is centred
on (x, y), so the cut began at the ramp's middle and ended half a run beyond its top. An X ramp's cut was not shifted
at all; no library ramp runs along X.

**What Deli Counter 0.241.0 does** (`patches/patch_dc_ramp_cut.py`, `patches/dc_ramp_cut/`):
- The cut runs from the ramp's middle -- where it always began -- to its head, never past it (`ramp_cut_span`).
- `stair_guards` rails it as it rails a flight's hole: both long edges and the entry end, 1.07 m, on storey 1; the
  head open. Painted steel where the palette has it.
- `ramp_landing`: a wall void past the head, as deep as the ramp is wide or IBC's 60 in, reaching back 0.2 m over the
  cut, so no wall stands across a ramp's arrival. Two did, clipped only by the old overshoot: foundry_heist_vertical's
  `int_0_4`, its centreline on the head, and parking_garage_a02's wall at y 6. A landing begun at the head left
  `int_0_4` standing (`hole_cuts` decides by the centreline, strictly inside); `test_ramp_cut.py` found it first.

**What is left, and why it waits.**
- **Where the cut begins.** At each cut's start the clearance between the slab's underside and the ramp's top face is
  1.04 to 1.55 m, under a body's 1.8 m: a body walking up a library ramp meets the slab's edge, so the ramps carry no
  one between storeys today (the stairs do). The agent contract's `min_headroom_m` (2.0) would open each cut 1.4 to
  3.2 m further down its ramp (the census prints both) -- under furniture that furnish lays without reading a ramp's
  cut: foundry's forklift and pallets, cbp_town's chairs. Furnish learning ramps comes first, then this.
- **A ramp's own sides.** Reported, not refused; walls or rails along them change the garages' ground floors.

**Proven in a package.** Cold run 9356 (`docs/cold_runs/cold_9356/`) made install test 10's level -- the first
level's brief at seed 9205 -- under Deli Counter 0.241.0 at 0 interventions: the drop-edge gate's undeclared indoor
edges 33 -> 0 and its "a thing's top" 9 -> 1, the rest of its report install test 10's; the three rails
(`stair_guard_rail_7` to `_9`) are the only slots, surfaces and merged meshes the export gained. The one edge left
round the ramp (`garage_rows_cold_9356.out.txt`) is on its west side 2 m up from its foot, from the ramp's collider
to the ground floor, 0.75 m: reported, as a ramp is not floor-like, and roadmap 270's. Install test 11
(`docs/findings/stranger_install/`) then made the same level from a fresh unzip of the set's package, and its
export shipped it: 0 undeclared indoors.
