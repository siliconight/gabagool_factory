# Cold run 9327 -- urban_row_001 on Deli Counter 0.231.1 (2026-10-19): two machines a store, on the stores' partitions

Staged from 9326. The tool change between them is Deli Counter 0.231.1 (5f3c51c0): the store's video poker cabinet
is `distinct`, so two in one room are two different machines. 9326 had shown deli_a01's two as one machine twice.
Read with 9326's 0.231.0, this run is roadmap 196's last two changes in one level.

**Run:** 0 interventions (journal 0, unattributed files 0), drive exit 0. The pick is seed 9104 again, PASS 100.
Findings 107 -> 107.

**The light bake** keeps 9 module files dynamic where 9326 kept 8: deli_a01's two cabinets are two files now.
Baked models 353, users 3,171, as 9326.

**Priced against 9325**, the package before both releases, at its 53 headings, 9325 the control twice (`price/`;
the harness names the subject `glow`):

    measured control_1  53 headings  draws mean 715 worst 2573  p95 median 2.54 ms
    measured glow       53 headings  draws mean 716 worst 2569  p95 median 2.51 ms
    measured control_2  53 headings  draws mean 715 worst 2573  p95 median 2.53 ms
    controls' spread, median over 53 headings: p95 0.05 ms, draws 0.0 (the noise floor)
    run        draws +mean   draws +min   draws +max   p95 +median ms  p95 +max ms
    glow               0.1           -4            6            -0.00         0.94

Memory after the warm-up, MiB, control_1 / 9327 / control_2: textures 79.5 / 79.6 / 79.5. The buffer figure is not
read: the two controls disagree by 18.3 MiB between themselves (87.6 and 69.3).

So pharmacy_a01's second cabinet and stool, and deli_a01's vending machine, file cabinet and poster board coming
back, cost +0.1 draws a heading on the mean, between 4 fewer and 6 more at any heading, and nothing measurable in
frame time.

**Seen** (`cabinets_before_after.png`; `docs/cold_runs/cold_9324/cabinet_stations.py` aimed at each cabinet in the
0.231.1 specs, `cabinet_stations.txt` the arguments; the same stations in 9325's package and this one, in the
level's own light):

- **deli_a01's customer floor:** PIKE DRAW and LUCKY HOAGIE, each with its stool, against the partition between the
  customer floor and the deli counter, the doorway kept clear. In 9325 the two stood apart, each in a filler's
  place: PIKE DRAW on the customer floor where a vending machine had been, LUCKY HOAGIE in the market aisles where
  a file cabinet had been. Both fillers are back.
- **pharmacy_a01's retail floor:** its second cabinet, a PIKE DRAW, against the partition at the room's back. In
  9325 that wall was bare -- the unfurnished partition roadmap 196 named.

**The clean job** took one workspace, cold-9323-ws (1.4 GB), whose record is pushed and which is now beyond the
newest four.
