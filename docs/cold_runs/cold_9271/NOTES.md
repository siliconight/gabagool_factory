# Cold run 9271 -- the rowhomes three steps up, on stoops, in a real drive

**What it tested:** Deli Counter 0.211.0 and Level Factory 0.195.0 in a real drive of restaurant_row_001
(factory roadmap 240's rowhouse front; the design is `docs/proposals/ROWHOUSE_STOOP.md`).

- Every rowhome Empty stands three steps up on a stoop: the door and its window raised together.
- A landing and two treads, walked on one ramp riding the nosings (32.5 deg), 1.74 m deep.
- The terrace standing each house's front face on its line and the stoop in the 2.0 m frontage before
  it.

Everything else as in 9270.

**Result: 0 interventions, 0 tool files changed.** seed_9104 picked as before, the three candidates'
grades as in 9270 (1, 0 and 1 major, route completion 1.00 each). **Findings 117 -> 129:
`PRESENTATION_CIRCULATION` 0 -> 12**, attributed below and fixed in Deli Counter 0.211.1. The price found
the stoops drawing a module a piece, fixed in Level Factory 0.196.0. Both are proven in cold run 9272.

## As built

- **The stoops:** each of the 23 Empties in the far row carries its stoop. The bake took them as 69 more
  lightmap users (3,346 -> 3,415, three pieces a house) and 38 more models (505 -> 543); the bake 30.39
  s and its editor 61.1 s.
- **The terrace** stood every front face where 9270's stood. The blockers' `at` and sizes are
  unchanged: Level Factory 0.195.0 reads each house without its stoop.
- **The Empties' merge** read exactly as 9270's -- 1,061 meshes of 1,660 surfaces into 148, and 962
  colliders kept. So the stoop's pieces were never in it (below, the price).

## The walk (`stoop_walk.gd`, `stoop_walk.out.txt`)

The contract body is a capsule of radius 0.35 m and height 1.8 m, walking at 4.0 m/s. It runs with
`floor_max_angle` 45 deg and NO step-up code. Each arm drives it 3 s straight at gs_empty_rowhome_a's
front door. The house comes from a mirror of this run's package; the controls stand beside it:

    arm     ends at z   feet      on floor
    stoop     6.500     0.534 m   yes      up the ramp onto the landing, against the door (face 6.15 + 0.35)
    flat     -1.933     0.001 m   yes      nothing in the way: 11.9 m in 3 s
    block     7.959     0.001 m   yes      a solid box the stoop's size: stopped at its face
    riser     7.913     0.000 m   yes      one 7 in riser: stopped, as the contract says it must be

The instrument sees a body stopped (block, riser) and a body free (flat). The stoop carries the
contract body to its door with no step-up, where a single real riser stops it.

RETRACTED, KEPT in the probe and its output: its "loaded" lines read node positions before the scene
was inside the tree, so every one prints the origin. They place nothing.

## The frames (`stoops.sh`, `stoops.png`)

9270 left (no stoops), 9271 right, the same lot. The stations:

- `stoop`: e10's stoop (gs_empty_rowhome_a, door at x -11.35), three-quarters from the far sidewalk.
- `side`: the stoop from its side.
- `row`: down the row.
- `street`: the row from the road's centre.
- `hatch`: the deli's roof, the control.

    station   mean |d| (codes)     pixels over 8 codes   over 32
    stoop     4.93 / 2.69 / 2.08    13.141 %              3.257 %
    side      6.58 / 2.23 / 1.72    18.744 %              4.815 %
    row       5.46 / 4.09 / 3.13    13.809 %              3.167 %
    street    3.07 / 2.63 / 2.68     6.160 %              1.066 %
    hatch     2.34 / 1.94 / 2.08     0.047 %              0.004 %   (control)

The difference is the stoops and the raised doors and windows; the control did not move. In the frames
the steps rise off the frontage to each raised door. The landing reads from the side as a solid
masonry block. In the street view the row's fronts stand in blue hour's shadow, and the stoops in it
are hard to see at that scale. Railings are not built yet (Zoo, the comps' "iron railings").

## The findings: `PRESENTATION_CIRCULATION` 0 -> 12, one a rowhome design

    gs_empty_rowhome_a: 1 prop(s) stand in circulation (shell): stoop_landing 0.15 m into doorway:ext_0_S_open0

The same on all twelve designs. Deli Counter's own circulation gate (`circulation.check_shell`, run on
the greybox shell by the compose) asks of every surface whose role is `prop` whether it stands in a
doorway's walk-through volume. 0.211.0 drew the stoop's pieces as `prop`.

**The 0.15 m is the gate's, not the stoop's.** `doorway_volume` starts a door at its wall's bottom plus
its sill (0.3834). The builder opens the door at the slab's top (`floor_thick` / 2 = 0.15) plus its
sill: 0.5334, which is the landing's top. At grade the offset never showed, since the bottom 0.15 m is
slab and a prop stands on top of it.

**Deli Counter 0.211.1** draws the stoop's pieces as `stair`: a stoop is the way to the door, as a
flight's treads are. Its slots stay `prop`, so the art pass dresses them as before. The gate's offset is
recorded, not changed: moving every doorway volume moves every building's gate, and the fix is a slot
field Zoo reads too. Its new test fails 24 of 25 on 0.211.0's shells, reproducing the finding to the
millimetre.

## The price (`price/`)

9270's package both controls, 9271's the subject (the harness names it `glow`):

    controls' spread, median over 53 headings: p95 0.06 ms, draws 0.0 (the noise floor)
    run        draws +mean   draws +min   draws +max   p95 +median ms  p95 +max ms
    control_1          0.0            0            0             0.00         0.24
    subject           22.7            0           93             0.06         1.34
    control_2          0.0            0            0            -0.00         0.18

Draws 790 -> 812 a heading on the mean, +93 at the worst (2,807 -> 2,900). The p95's median rose
+0.06 ms against a 0.06 ms floor. The frame time cannot tell, but the draws are the budget, and +93 is
three a stoop, drawn one by one.

**Why:** `merge_empties.gd` merges only slot children whose names give a side (`ext_<storey>_<side>_*`,
`parapet_<side>_*`, `roof_*`); `stoop_landing` and `stoop_tread_<k>` give none. **Level Factory 0.196.0**
gives a `stoop_*` slot the front's side, S, where Deli Counter stands it, so its pieces merge by material
with the rest of the front.

## The time

    run    shell   art     export   walk   retire   the drive
    9270   92 s    166 s   167 s    11 s   18 s     7.8 min (470 s)
    9271   95 s    161 s   171 s    11 s    3 s     7.6 min (455 s)

## What is evidence of what

- The stoops: Deli Counter's `build/gs_empty_rowhome_*.glb` (six stoop nodes each) and the package's
  bake (`light_bake.json`); the terrace, the site spec's `blockers`.
- The walk: `stoop_walk.out.txt`, its import and run logs under `_scratch/frames_9271_stoops/`.
- The look: `stoops.png`, `stoops.log`; the PNGs under `_scratch/frames_9271_stoops/`.
- The findings: `workspaces/cold-9271-ws/.level_factory/validation/restaurant_row_001.json`.
- The price: `price/`; the count: `cold_run.py --end`.
