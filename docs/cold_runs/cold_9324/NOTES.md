# Cold run 9324 -- urban_row_001 on Deli Counter 0.228.0 (2026-10-19): deli_a01 stands its two video poker cabinets

Staged from 9323. The tool change between them: Deli Counter 0.228.0 (3dd5d62e), where a store's video poker
cabinet with no free wall takes a file cabinet's slot, then a vending machine's, in its own room, and a building
holds two -- roadmap 196's regression, in which 0.202.0 left the six delis 2 of their 20 cabinets.

**Run:** 0 interventions (journal 0, unattributed files 0), drive exit 0, 10:16:01 to 10:25:37. The pick is seed
9104 again, PASS 100, route completion 1.00, 0 major -- as on 9317 to 9323. Findings 108 -> 108 against 9323.

**deli_a01, the building that changed,** read off the compose job's log for both runs:

    9323: 537 themed modules, 133 module GLBs bundled, placement 508/508, z-fight [WARN] 2 pairs across 755 solids
    9324: 538 themed modules, 136 module GLBs bundled, placement 509/509, z-fight [WARN] 2 pairs across 756 solids

The two z-fight pairs are 9323's, `ext_0_E_seg10 / int_0_1_seg18`, the partition seam roadmap 177 leaves; the
new pieces add none. One module more net is the spec's own change: +2 cabinets and +2 stools against a file
cabinet, a vending machine and a poster board fewer. The package carries both cabinets,
`lot/deli_a01/art/zoo/prop_video_poker_delco_1997_07_w65_d65_h175_n1.glb` and `_n2.glb`, and their stools.

**The light bake** (`light_bake.json`, `imports`): the dynamic set is 6 -> 8, and the two added are deli_a01's
cabinets. The bake keeps every lit machine in the level dynamic -- the six in 9323 were three cover trees, both
ATMs and pharmacy_a01's one cabinet -- so the cabinets join a rule, not an exception. Baked models 351 -> 352
and users 3,159 -> 3,160: the two stools lightmapped, and deli_a01's two poster boards -- 100 cm and 220 cm
wide in 9323 -- one 220 cm board.

**Laser Tag, seed 9104** (`lasertag.report.json` of each run's candidate): 0 of 32 summary fields moved, PASS
100 -> PASS 100, its 7 findings the same codes; 0 enemy and 0 player stuck events either side.

**Priced** against 9323's package at its 53 headings, 9323 the control twice (`price/`, the harness
`docs/findings/horizon_glow/price_glow.py` names the subject `glow`):

    measured control_1  53 headings  draws mean 715 worst 2569  p95 median 2.58 ms
    measured glow       53 headings  draws mean 715 worst 2573  p95 median 2.56 ms
    measured control_2  53 headings  draws mean 715 worst 2569  p95 median 2.60 ms
    controls' spread, median over 53 headings: p95 0.05 ms, draws 0.0 (the noise floor)
    run        draws +mean   draws +min   draws +max   p95 +median ms  p95 +max ms
    glow               0.7            0            4            -0.02         1.35

Memory after the warm-up, MiB, control_1 / 9324 / control_2: textures 78.8 / 79.5 / 78.8, buffers 79.3 / 83.5 /
83.4.

Two lit cabinets, two stools and a poster board fewer cost +4 draws at the heading that sees them most and
nothing measurable in frame time; textures +0.7 MiB. The buffer figure is not read: the two controls disagree by
4.1 MiB between themselves.

**Seen** (`cabinets_before_after.png`; `cabinet_stations.py` aims an eye 1.6 m up, 3 m in front of each cabinet
toward its room's centre, `cabinet_stations.txt` the arguments; the same stations in both packages, in the
level's own light):

- **The customer floor:** PIKE DRAW and its stool stand against the wall beside the ATM, where 9323 stood the
  lemonade vending machine.
- **The market aisles:** LUCKY HOAGIE and its stool stand where 9323 stood a file cabinet under the LOTTO HERE /
  OPEN 24 HRS poster board. The board went with it. In 0.227.0's spec it hung 1.20-1.80 m up over a file cabinet
  1.05 m tall; the cabinet on that spot is 1.75 m tall and overlaps the board's band in plan and height, and the
  market aisles hold no board in 0.228.0's. That is the poster board deli_a01 lost, the trade this rule makes,
  for the walker's eye; the dial is the recipe's order. The customer floor's 2.2 m board kept its place.

Shot exposure moved little (customer floor mean 54.3 -> 57.2, market aisles 66.6 -> 67.2; p95 160 -> 157 and
137 -> 137), the cabinets' screens lit as the vending machine's face was.

**The clean job** took one workspace, cold-9320-ws (1.5 GB), whose record is pushed and which is now beyond the
newest four.

**Checked and not a finding:** the driver's candidate line for seed 9104 read twelve shells to the eye, with no
pharmacy_a01, while the themed site stands it. The line was cut at 250 characters on the screen it was read
from; `lot_assemble`'s `out/buildings/` holds 13 GLBs, pharmacy_a01's among them, in both runs.
