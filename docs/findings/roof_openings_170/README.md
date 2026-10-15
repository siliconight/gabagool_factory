# Roof openings, roadmap 170: the split, measured

Roadmap 170 (the walker, 2026-09-23: "a building does not have an open hole in its roof") measured 58
`roof_access` ladders cutting the slab they arrive through and 74 `hatch` links doing the same, with no lid in
any tool. It also proposed the better answer for most of them -- a BULKHEAD, the little house a stair runs up
into, which turns a hole in a horizontal slab into a doorway in a vertical wall that Deli Counter already
builds -- and said the first thing to do was to split the population between a bulkhead (where a stair reaches
the roof) and a lid (where only a ladder does), measured rather than assumed. This folder is that split.

## Instrument

`census.py` reads every `deli_counter/specs/*.json` (446 on 2026-10-15) and, per spec, the stairs whose
`to_story` reaches the roof level (`n_stories`), the ladders that are roof access (`role`, `upper_surface`,
`transition` or `to_story`), and the `vertical_links` of kind `hatch` on the roof slab. Then the two
populations by what cuts the slab: a stair with `cut_slabs` leaves the hole at its head; a ladder leaves one
only where a hatch link sits at its own (x, y). Output: `census.out.txt`.

## What it reads

    specs                                       446
    stairs                                      511     to the roof   16
    ladders                                     124     roof access   69
    hatch links on the roof slab                 43     below it      37

    specs with a roof opening or a stair to the roof   73
      reached by a stair   (bulkhead)                   16
      reached by a ladder  (lid)                        57
      hatch link with neither                            0

The refinement that decides the build:

- **The 16 stairs are all switchbacks with `cut_slabs` true, in specs with no roof hatch link** -- so each
  leaves the roof slab open at its head. Nine of the sixteen are the mission's own generated shells
  (`lf_deli_001_*`, `lf_restaurant_row_001_*`, `lf_urban_row_001_*`, three seeds each). RETRACTED, kept: the
  first draft of this line said "every level made this week has a stair head open to the sky". Read against cold
  run 9316's package, the generated shell is built, composed and gated every run (the first
  `presentation_compose` arm, 0/0 modules) and reaches no package -- the site stands the library's buildings
  (`building_library.lot_for_brief`), and no file in the package carries the shell's hatch. So the bulkhead's
  SHIPPED population is two library buildings, cr_deli and night_deli; the five other library specs with such a
  stair (bank, corner_deli_heist_01, foundry_heist_vertical, harbor_score, rowhouse_raid) are prop-only kitbash
  specs with no walls and no roof slot. What the generated shell is for, when a lot library stands, is its own
  question.
- **Of the 69 roof ladders, 43 have a hatch link at their foot and 26 do not.** The 43 cut the slab (42 of
  them `interior` with `roof_hatch_exit`); the 26 are exterior, parapet or platform ladders (`parapet_crossover_platform`,
  `side_step_off`, or older specs with no placement recorded) that cut nothing and need no lid. Those 43 are
  the lid's population. The item's "58 of 58" counted built output; this counts the contract, and the hatch link
  is what cuts.

So: **16 bulkheads, 43 lids, and 26 roof ladders that were never a hole.**

## What this decides

Build order, by population and by cost:

1. **The lid** (43 openings): one Zoo species, a hatch cover sized to the hole (`SlabHole` is 1.5 x 1.5 m by
   default), closed, with collision, standing on the roof slab over each `hatch` link whose story is the roof.
   Deli Counter places it where it already emits the `HATCH_<x>_<y>` marker; the ladder's `roof_hatch_exit`
   transition is unchanged (the cover is the thing the climber opens, which is the game's, as the doors are).
2. **The bulkhead** (16 openings): a Zoo species -- four short walls, a flat or mono-pitch roof, a doorway on
   one side -- stood by Deli Counter over the top landing of a stair that reaches the roof, its doorway cut and
   derived like any door, and the roof slab under it no longer cut.

The look of both is the walker's reference (the tenement roofscape photo), and each is a look change: frames
before it ships.

## Step 1, the lid: Zoo 1.113.0 `roof_hatch` + Deli Counter 0.224.0

`patches/patch_roof_hatch.py`, record in `patches/roof_hatch/` (the Blender census, the specimen build log,
`prove_tests.out.txt`).

**The species.** A roof scuttle: a steel curb ring on the slot's edges and a lid plate hinged along the back
top edge (`roof_hatch_open.png` beside this file: the default state, built at Deli Counter's dims 1.66 x 1.66 x
0.2 m, 260 tris). The lid is the species' interactive -- Deli Counter's new `hatch` machine maps `open` and
`closed` to it, and the genome's `state_art: ["closed"]` is what makes Zoo build the closed lid rather than
defer it as identical art. Open stands the lid 100 degrees on its hinge, past vertical, leaning away from the
opening, with a collision box (a sheet of steel a body walks into; the walker's rule); closed lays it flush
with its own box over the hole. `fit_objects` is the curb, so the raised lid is art above the slot.

**Open is the default, and why.** The ladder's `roof_hatch_exit` is a route every walker takes -- the QA
walkers, Laser Tag's bots, the crew -- and nothing in the factory opens an interactive; doors today ship as
open apertures tagged `closed` (173's record). A closed lid would end every roof ladder at a sheet of steel.
So the lid ships standing, the hole reads as a hatch somebody built, and shutting it is the game's, as a door
is. The curb is 0.2 m: a step-up for a body (the contract's unassisted step is 0.1025 m, Laser Tag's step-up
0.5), not a wall.

**Which way it opens.** `roof_hatch.rot_for` turns the slot by the ladder's `facing` at the link's (x, y):
`ladder.climb_rect` reserves the climber's body `reach` along `facing`, so that side is the slot's local +Y and
the hinge is local -Y -- the lid rises behind the climber. A hatch with no ladder faces north. This is read
off the code, not a frame; the cold run's frames are where it is checked.

**What was measured before shipping.** The first cut built the curb from four boxes and the coincident-face
census read 8 pairs at every corner (each end wall's outer face on the long walls' end faces); the curb became
one ring of 16 shared vertices and the census reads 0 pairs at min / default / max, 260 tris each, with the
bollard control at its known 2 / 2 / 1 (`patches/roof_hatch/census.log`). `prop_species.SPECIES_OWNS_COLLISION`
gains the species, so the greybox puts no solid box over the hole.

**In the rebuilt library** (`build.py --all`, demanded by Deli Counter's pre-commit freshness gate): 40
`roof_hatch` slots in 40 of the 159 built specs, each with its `hatch` entry in `gameplay.json`; the authored
specs hold 43, and every one of the 43 has its ladder at the hatch's own (x, y) -- facings S 19, N 17, E 7 --
so `rot_for` always has a ladder to read and never falls back to north.

**Cold run 9315 stopped at the art pass, on two gates, and both were right** (`docs/cold_runs/cold_9315/`;
0 interventions, drive exit 2). The three generated precinct shells carried `roof_hatch_13_-9` at (13, -9, 7.3),
rot 180, open; the zoo kit build built `prop_roof_hatch_delco_04_w166_d166_h20` and its `_closed` variant
(PASS, `[state:closed]`); and `presentation_compose` refused the two library buildings that carry a hatch,
courthouse_a02 (`roof_hatch_-16_12`) and airport_terminal_a01 (`roof_hatch_24_8`):

- *The placement gate* (`portable_building.verify_placement`, 0.25 m) measures a module's whole visual footprint
  against its greybox slot, and the lid leaning 10 degrees past vertical read `placed [1.668, 1.835, 1.987]`
  against `greybox [1.66, 0.2, 1.66]` -- 0.33 m outside. **Zoo 1.113.1** stands the lid vertical on a hinge 4 cm
  inside the back wall, its edges 5 mm inside the curb's planes: the open footprint is the curb's, and the
  census re-run reads the same 260 tris and 0 pairs at every corner (`patches/roof_hatch/census_1131.log`;
  `roof_hatch_open.png` is the second cut).
- *The circulation gate* (`circulation.check_shell`) found the hatch's own greybox box 0.2 m inside
  `ladder:ladder_0`'s climb volume -- where it stands by construction, the climber comes up through it, as a
  stair's guard stands at its own hole's edge, which the gate has excused since 0.191.0. **Deli Counter 0.224.1**
  excuses a `roof_hatch_*` prop in a ladder's volume the same way (`excused_own_furniture`), lists it as excused,
  and keeps it a conflict anywhere else.

The z-fight gate read 0 pairs on courthouse_a02 with the hatch standing; the 2 + 2 pairs it printed are
airport_terminal_a01's and convenience_store_a01's `ext_0_N_seg5` against `int_0_1_open1`, the wall-beside-an-
opening class 177 records, not the hatch's. `patches/patch_roof_hatch_gates.py` is the second cut; proof in
`patches/roof_hatch/prove_tests_gates.out.txt`.

**Cold run 9316 (precinct_yard_001 again, seed_9203 picked as before): 0 interventions, drive exit 0**
(`docs/cold_runs/cold_9316/NOTES.md`). courthouse_a02: placement 340/340, circulation 0 conflicts with the hatch
listed as the 1 excused, z-fight 0 pairs across 521 solids; airport_terminal_a01 likewise placed and excused.
The package instances `prop_roof_hatch_delco_04_w166_d166_h20` on both with `metadata/interactive_state =
"open"` and the `_closed` variant built for the hidden state. The findings leg's remaining classes
(DISPATCH_FINDING, LUX_NO_ROOM_PROBES) are the ones 9279's package carried.

**Frames** (`docs/cold_runs/cold_9316/hatch_frames/`, three given cameras from `cold_9315/hatch_station.py`):
a rust-brown curb on the courthouse roof with its lid standing vertical on the far edge from the climber's side,
the opening and the ladder's rungs visible from above. For the walker's eye: the lid's size (1.66 m square,
because the hole is 1.5 m), its hinge side, the open default.

## Step 2, the bulkhead: sized, not built

`stair_heads.py` (`stair_heads.out.txt`) reads, for each of the 16 roof-reaching stairs, the hole `_stairs`
cuts in the roof slab -- `stairwell.hole_span` across the runs, `run / 2 + 0.3` behind the bottom step to
`run / 2 + WALKOFF_CLEAR` past the top landing -- and the roof left around it:

    hole width 3.60 .. 4.40 m     length 5.10 .. 7.50 m     roof to the edge 1.00 .. 2.25 m
    storeys 3.20 .. 5.00 m        parapets 1.0-1.1 m tall, 0.2-0.35 m thick (harbor_score none)
    the deli family (10 of 16): 3.60 x 6.60, facing S, 2.25 m to the edge

So a bulkhead is the stair's hole plus a wall each side -- about 4.0 x 7.0 m on a deli, a storey or a short
storey tall -- with its door on the walk-off end (the discharge bridge past the top landing, `sign` along the
stair's travel), the way the hatch's hinge was read off the ladder. The gates it will meet are the lid's two:
its footprint must be its slot's, and its box stands in its own stair's column, which `circulation` excuses for
a guard and would excuse for a bulkhead the same way (`stair:` volumes). Its shipped population today is cr_deli
and night_deli, when a brief's draw stands them.

**What a cold run was asked to show** (and did, bar the fight fields, which have no like-for-like baseline --
9279's library draw differs): the slot in the composed building with both state nodes (the closed one `visible = false`,
its collider off), the hatch in frames, no traversal or fight field moved by the ladder route, the z-fight gate
unchanged, and the draw cost (one module, two state meshes, one visible).
