## [1.85.0] - the getaway van's hero pass: real tyres and wheels, hung wipers, West Coast mirrors, and the details a street reads a working truck by

### Why now

The walker, 2026-10-08: "this van is also going to be the foundation of a
hero prop that get's reused in multiple missions, so we can afford to really
make it look good".

**Priced the way the draw-call rule prices.** There is one van a level, and
its frame cost is its submissions. Those stay five. Everything here is
triangles on materials the van already had, so detail goes where a player
sees it.

### The wheels

**The tyre.** `van_forms.tyre_profile` is a 22-point section:
- the bead;
- a sidewall bulging `TYRE_BULGE` (6 mm) past the tyre's width;
- a rounded shoulder;
- a tread with two `TYRE_GROOVE` (10 mm) grooves;
- the same back down the other side.

It is lathed at 28 segments (the genome's range is now 10-32), where 1.82.0
lathed six points at 14 and the tyre read as a cut log. 28 is a multiple of
4, so a vertex points straight down and `axle_height` is r itself.

**The steel wheel.** Its parts nest, each starting inside the one before:
- a disc that runs into the tyre's bead (`DISC_R` 0.63 r, past the bead's
  0.60);
- a hub proud of the disc (`HUB_R`);
- eight lug nuts on the hub's bolt circle (`LUG_CIRCLE`, `LUG_R`);
- a cap in the middle (`CAP_R`).

### The cab

- **Wipers hung from the header.** A step van's wipers pivot at the top of
  its windshield and hang across the glass, as the walker's P30 comp shows.
  The pivot runs into the header; the arm and the blade stand in front of
  the glass. The blade runs past the arm's end, so the two never share an
  end face. `WIPER_X`, `WIPER_ARM` and `WIPER_TILT` live in `van_forms`.
- **West Coast mirrors.** The head is now wide across and thin along, clear
  of the body on two arms: the lower into the cab's side, the upper back
  into the A-pillar along the rake. The glass is on its back, and its
  heights follow the belt. 1.82.0's head was 7 cm across and 12 cm deep, a
  mirror seen edge-on from behind. The slot's width is still the heads'
  outer faces.
- **The crew's step.** A plate stands 2 cm out of the kerb-side sill under
  the door the crew uses.

### The box and the tail

- Side marker lamps, amber ahead and red behind, high and low, 9 mm proud
  (the ribs stand 6).
- A drip rail under each roof edge.
- Three red identification lamps over the rear doors and a clearance lamp
  either side.
- Three hinges a door. Their backs sit 4 mm behind the seams', which they
  enclose; flush, they would share the seams' plane.
- Aluminium caps on the box's rear corners, wrapping both faces 10 mm proud.
- A diamond-plate step on the rear bumper.
- A mud flap behind each rear pair, past the arch and into the body.

### Built

| | default (2.6 x 6.8 x 3.05) |
|---|---|
| validation | PASS, exact fit |
| triangles | 13,792 (13,572 and 14,012 at the genome's corners) |
| submissions | five |
| coincident pairs | 0 at six probed sizes, and by the census, on the first build |

The budget moves 6,000 -> 16,000. It is a regression detector, and the van's
price is its five draw calls.

**What it costs that this release cannot measure.** No frame time exists
with the van in a level. Nothing places it yet (roadmap 206, phase 2), and
the price owed there is the performance contract's: draw calls and frame
time at fixed stations, with a control.

### Tests

**`tests/test_step_van.py`: 484 pure, 8 built.** All 492 passed inside
Blender 5.1.1. New or changed:
- the tread touches the ground at every count from 10 to 32 segments, and
  the shipped count points a vertex down;
- the tyre's section is closed and symmetric, bulges `TYRE_BULGE`, and has
  four groove points;
- the steel wheel nests: the disc in the bead, the nuts on the hub, the cap
  inside the bolt circle;
- the wipers hang over their own panes at every corner, reading the
  recipe's `PILLAR_IN` off its source with `ast`, because the recipe
  imports bmesh;
- the chassis' tyre clearance is judged against the bulge and the bead;
- MEASURED holds the six probed sizes.

The census note in `test_coincident_faces.py` records the redraw: same three
builds, count unchanged at 363.

**Suite:** 3,876 passed, 395 skipped, 1 xfailed in 322 s (`python -m pytest -q`): 1.84.0's 3,782 and 395, and test_step_van.py's 94 new pure tests (its 8 built ones skipped without Blender, as before).

