# Cold run 9287 -- the first urban street: a continuous mid-rise wall across the street

**What it tested:** Level Factory 0.200.0 (65cf5e7), roadmap 241's first cut, in a real drive. The mission,
`urban_row_001`, is restaurant_row_001's brief (cold run 9285) with `streetscape: "urban"` and nothing else
changed. That stands the far side of the through road as a continuous wall of Deli Counter 0.213.0's
mid-rise Empties (`gs_midrise_a` to `_f`, 5 to 12 storeys), with no alley every few houses, themed and lit as
the rowhome terrace is. On Deli Counter 0.216.0 and Lot 0.120.2; staged from cold run 9285.

**Result: 0 interventions (journal 0, unattributed files 0).**

- **The wall stood, themed.** Each candidate's site stood 8 or 9 mid-rise Empties across the street, all six
  shells used: `[site] 8 Empties across the street (an urban wall), 6 shell(s), themed`. The near side's
  lots are 9285's buildings exactly: deli_a03 or deli_a01, office and a pharmacy on each seed. So the far
  side is the only change.
- **The grader:**
  - seed_9104 was picked at PASS 90, as in 9285.
  - Enemy stuck 0 and crew stuck 0; blocked 1, where 9285 read 6.
  - All three candidates PASS 90, route completion 1.00.
- **Findings 117 -> 118.** The one more is Laser Tag's `LT_MAP_BLIND_MAP` (moderate), now on all three
  candidates where 9285 had it on two. It reads 52 to 63% of positions never seen from an enemy spawn. A
  taller, gapless wall cutting sightlines is the obvious reading, and it is not measured. Enemy spawns are
  provisional until a gameplay layer owns them.
- **The bake:** 506 models and 224 primitive meshes lightmapped, 3,037 users, where 9285 had 566, 224 and
  3,392. Fewer, larger shells replaced about two dozen rowhomes.

## Seen and priced against 9285 (`docs/findings/urban_street/`)

Same seed, same near side; the control is 9285's package, the subject 9287's.

- **Frames:** `ab_sheet.png`, two road ends, the spawn, the objective and four elevated views.
- **The price** (`price/price.txt`), 53 headings, Level Factory's fixed-station harness:
  - draws -71.6 a heading on the mean (-302 to +58);
  - p95 -0.15 ms at the median, against a 0.03 ms floor between the two controls;
  - textures 76.0 -> 74.4 MiB;
  - **buffers 47.9 -> 68.6 MiB, video 123.9 -> 142.9 MiB.**

  The wall draws cheaper and holds about 19 MiB more, all of it buffers.

## The time

    run    shell   art     export   walk   retire   the drive
    9285   96 s    161 s   176 s    11 s    4 s     7.5 min (451 s)
    9287   102 s   160 s   182 s    7 s     3 s     7.7 min (460 s)

## What is evidence of what

- **The wall:** `art.log` (`[site] ... an urban wall`), and each `lot_assemble` candidate's buildings in
  `driver.log`.
- **The grader:** `jobs/urban_row_001.laser_tag_evaluate.candidate.<seed>/1/out/lasertag.report.json` in
  `workspaces/cold-9287-ws/.level_factory/`.
- **The findings:** `validation/urban_row_001.json` there, against 9285's.
- **The frames and the price:** `docs/findings/urban_street/`.
- **The count:** `cold_run.py --end`.
