# Cold run 9273 -- the stoops' iron railings

**What it tested:** Zoo 1.105.0, Deli Counter 0.212.0 and Level Factory 0.197.0 in a real drive of
restaurant_row_001. The walker's calls of 2026-10-13: "3 risers, concrete, railings both sides -- build
the railings". On every rowhome Empty's stoop (Deli Counter 0.211.x, cold run 9272), one iron railing
stands each side:

- Zoo's new `stoop_railing`, in two slots a side: a level section along the landing and a flight down
  to a post on the bottom tread;
- 5 cm inside the stoop's side, turned so each flight rises to the house;
- their colliders Deli Counter's: a box along the landing and a slab under each flight's rail;
- read by Level Factory's terrace as the stoop's, not the house's.

Everything else as in 9272.

**Result: 0 interventions, 0 tool files changed.** seed_9104 picked as before, the candidates' grades as
in 9272. **Findings 117 -> 117**, and the same 117: every issue id and every code's count is 9272's.

## As built

- **Zoo** built the two modules the slots ask for in each of the twelve rowhome folders:
  `prop_stoop_railing_delco_1997_05_w90_d4_h91_flevel` and `..._w52_d4_h127_fflight`.
- **The composer** placed each turned as Deli Counter wrote it. The composed `site.tscn`'s basis rows are
  (0, 0, 1), (0, 1, 0), (-1, 0, 0), so the module's +X, its high end, points at Godot -Z, the house. The
  flight runs from z 7.5748 at its post up to 7.05 at the landing's edge.
- **Its z-fight gate** reads every rowhome with four solids more (89 -> 93 on gs_empty_rowhome_a) and
  finds 0 pairs, 0 buried, ok on all twelve.
- **The merge** takes the railings in: 12 scenes, 1,145 meshes of 1,744 surfaces into 172 merged meshes,
  998 colliders kept. 9272's numbers were 1,097 of 1,696 into 160, and 998. The difference is 48 meshes
  and 48 surfaces in (four a rowhome design) and 12 merged meshes out (one iron mesh each). The colliders
  did not move: Zoo's railing carries none.
- **The bake** has 3,392 lightmap users: 9272's 3,369 plus one iron mesh for each of the 23 houses. It
  has 567 models: 9272's 543 plus the 24 railing GLBs, two in each of the twelve folders. The bake took
  29.59 s and its editor 55.8 s.

## The walk (`rail_walk.gd`, `rail_walk_9272.out.txt`, `rail_walk_9273.out.txt`)

gs_empty_rowhome_a's scene from each package, the contract body with no step-up code, 3 s at 4 m/s:

    arm       9272 (no railings)                     9273 (railings)
    up        z 10 -> 6.500, feet 0.534 m            the same, to the millimetre
    off_w     moved 11.934 m, feet 0.001 m (off)     moved 0.312 m, feet 0.534 m (on the landing)
    off_e     moved 11.934 m, feet 0.000 m (off)     moved 0.312 m, feet 0.534 m
    flight_w  moved 11.934 m, feet 0.001 m (off)     moved 0.312 m, feet 0.434 m (on the ramp)

- **9272 is the control.** It shows the instrument sees a body leave the stoop at all.
- **0.312 m** is the 0.662 m from the door's centre line to a railing's inner face, less the body's
  0.35 m radius.
- **The flight's 0.434 m** is the ramp's 0.370 m where the body stopped (z 7.306), plus what a capsule's
  hemisphere stands off a 32.5 deg slope (0.35 (1/cos - 1) = 0.065): 0.435.
- **Read after the tree was ready** (first physics frame): the four visuals and four colliders, at the
  slots' and `stoop.plan`'s positions, each flight slab turned 34.95 deg.

## The frames (`railings.sh`, `railings.png`)

9272 left (no railings), 9273 right (railings). 9272's four stations, and `front`, a view from the
sidewalk of blocker_10's stoop (gs_empty_rowhome_a):

    station   mean |d| (codes)     pixels over 8 codes   over 32
    front     3.97 / 2.24 / 2.01   11.679 %              1.433 %
    side      4.63 / 2.66 / 2.66   10.937 %              1.952 %
    stoop     3.73 / 2.16 / 1.95   10.812 %              1.312 %
    row       3.20 / 2.67 / 2.47    7.667 %              0.565 %
    hatch     2.34 / 1.93 / 2.08    0.031 %              0.001 %   (control)

Both railings stand on every stoop in view, black against the lit brick and sidewalk. Each flight drops
from its landing's edge to a post on the bottom tread. The rest of the movement is the lightmap's: 23 new
users repack the atlas (`cold_9269/lm_users.out.txt`).

## The price (`price/`, `price_2/`)

9272's package is both controls and 9273's the subject. This is the whole cost of the railings as they
ship. It was measured twice:

    controls' spread, median over 53 headings: p95 0.12 ms, draws 0.0 (the noise floor), both times
    run              draws +mean   draws +min   draws +max   p95 +median ms  p95 +max ms
    subject, price         8.0            0           31             0.12         2.61
    subject, price_2       8.0            0           31            -0.02         0.30

Draws go 795 -> 803 a heading on the mean, at most +31 (the worst heading 2,836 -> 2,867). The stoops
themselves cost +6.5 (9272). The p95's median moves +0.12 and -0.02 ms against a 0.12 ms floor.

**RETRACTED, KEPT:** `price/`'s +2.61 ms at its worst heading is not a cost of the railings.

- In `price/`, two headings carried it: station 13 yaw 270 (+2.61 ms on +27 draws, render CPU +1.7 ms)
  and station 5 yaw 270 (+1.68 ms on +17).
- Both had the subject's two passes 2.8 and 4.5 ms apart, where the controls' agreed within 0.25 and
  1.43.
- Measured again in `price_2/`, the same headings with the same added draws read +0.02 and +0.01 ms.
- The heading that gained the most draws (+31, station 6 yaw 90) read -0.07 ms in `price/`.

## The time

    run    shell   art     export   walk   retire   the drive
    9272   94 s    158 s   170 s    10 s    4 s     7.5 min (452 s)
    9273   94 s    169 s   173 s    12 s    3 s     7.8 min (469 s)

## What is evidence of what

- The findings: the driver's count, and the run's `validation/restaurant_row_001.json` against 9272's,
  issue by issue.
- The modules and their turn: the package's `lot/<rowhome>/art/zoo/`, and the compose job's
  `site.tscn` (the package's own is merged).
- The z-fight gate: each rowhome's `portable_resource_manifest.json` in the compose job.
- The merge: the export log's "Empties merged" line and the package's `merge_empties.json`.
- The bake: the export log's light bake line and the package's `light_bake.json`, diffed against 9272's.
- The walk: `rail_walk_9272.out.txt` and `rail_walk_9273.out.txt`.
- The look: `railings.png`, `railings.log`, and the PNGs under `_scratch/frames_9273_railings/`.
- The price: `price/` and `price_2/`. The count: `cold_run.py --end`.
