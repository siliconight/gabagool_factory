# Cold run 9272 -- the stoops, clean and merged

**What it tested:** Deli Counter 0.211.1 and Level Factory 0.196.0 in a real drive of restaurant_row_001:
cold run 9271's stoops with its two findings fixed --

- the stoop's pieces are `stair` to Deli Counter's circulation gate, where 9271's twelve
  `PRESENTATION_CIRCULATION` findings read each landing as a prop 0.15 m into its own doorway;
- they merge with each Empty's front, where 9271 drew three modules a stoop, +22.7 draws a heading on
  the mean.

Everything else as in 9271.

**Result: 0 interventions, 0 tool files changed.** seed_9104 picked as before, the candidates' grades as
in 9270 and 9271. **Findings 129 -> 117: `PRESENTATION_CIRCULATION` 12 -> 0**, back to 9270's count.

## As built

- **The merge** takes the stoops in: 12 scenes, 1,097 meshes of 1,696 surfaces into 160 merged meshes,
  998 colliders kept. 9271's numbers were 1,061 of 1,660 into 148, and 962. The difference is 36 meshes,
  36 surfaces and 36 colliders in (three a rowhome design) and 12 merged meshes out (one each).
- **The bake** has 3,369 lightmap users. That is 9270's 3,346 plus one merged stoop for each of the 23
  houses, where 9271 had 69. 543 models; the bake 30.11 s and its editor 60.5 s.

## The walk (`stoop_walk.gd`, `stoop_walk.out.txt`)

The merge moved the stoop modules' colliders under `KitCollision`, so the climb was asked again. It
matches 9271's to the millimetre:

    arm     ends at z   feet      on floor
    stoop     6.500     0.534 m   yes      up the ramp onto the landing, against the door
    flat     -1.933     0.001 m   yes
    block     7.959     0.001 m   yes      stopped at a solid box the stoop's size
    riser     7.913     0.000 m   yes      stopped at one 7 in riser

## The frames (`stoops.sh`, `stoops.png`)

9271 left (three modules a stoop), 9272 right (merged), at 9271's stations:

    station   mean |d| (codes)     pixels over 8 codes   over 32
    stoop     2.44 / 1.97 / 1.81    4.625 %               0.276 %
    side      2.62 / 1.85 / 1.66    2.917 %               0.101 %
    row       2.76 / 2.50 / 2.32    4.045 %               0.252 %
    hatch     2.34 / 1.94 / 2.09    0.044 %               0.002 %   (control)

The stoops read the same. The movement is the lightmap's: the merged meshes are unwrapped anew at the
merge's texel and the atlas took 46 fewer users (`cold_9269/lm_users.out.txt` measured what a change in
the user count does). Past 32 codes, at most 0.28 % of a frame.

## The price (`price/`)

9270's package (no stoops) both controls, 9272's the subject -- the whole cost of the stoops as they ship:

    controls' spread, median over 53 headings: p95 0.06 ms, draws 0.0 (the noise floor)
    run        draws +mean   draws +min   draws +max   p95 +median ms  p95 +max ms
    control_1          0.0            0            0             0.01         0.42
    subject            6.5           -1           29             0.04         0.54
    control_2          0.0            0            0            -0.01         0.27

Draws 790 -> 796 a heading on the mean, at most +29 (the worst heading 2,807 -> 2,836), where 9271's
three modules a stoop cost +22.7 and +93. The p95's median moved +0.04 ms against a 0.06 ms floor.

## The time

    run    shell   art     export   walk   retire   the drive
    9271   95 s    161 s   171 s    11 s    3 s     7.6 min (455 s)
    9272   94 s    158 s   170 s    10 s    4 s     7.5 min (452 s)

## What is evidence of what

- The findings: the driver's count and the run's `validation/restaurant_row_001.json`.
- The merge: the export log's "Empties merged" line and the package's `merge_empties.json`.
- The walk: `stoop_walk.out.txt`; the look: `stoops.png`, `stoops.log`, the PNGs under
  `_scratch/frames_9272_stoops/`.
- The price: `price/`; the count: `cold_run.py --end`.
