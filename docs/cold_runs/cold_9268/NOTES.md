# Cold run 9268 -- the rowhome Empties roofed in tar, in a real drive

**What it tested:** Deli Counter 0.210.0 in a real drive of restaurant_row_001: the twelve rowhome
Empties roofed in `tar` -- the membrane every other roof in a delco level already wears -- where they
were `concrete`. The walker's call of 2026-10-12, asked "should it be silver?... where are you getting
that from vs. concrete?" and shown `docs/reference/ROWHOUSE_ROOFS.md`: tar now, the aluminum coating
when a 1990s source says how common it was (roadmap 240's roofscape). Everything else as in 9267.

**Result: 0 interventions, 0 tool files changed.** seed_9104 picked as before. Findings 117 -> 117.

## As built

- **The roofs:** each Empty's Zoo kit builds `roof_delco_1997_01_w<width>_d1200.glb` skinned
  `M_Skin_tar_delco_1997` from Pixelcoat's `tar_neutral` pack, where 9267's built
  `roof_delco_1997_04_..._mconcrete.glb` in `M_Skin_concrete_delco_1997`. No `_m` tag: `tar` is the
  roof's own delco default. The composer found the plain name and the bake skinned the greybox slab
  from it -- no unknown material, no greybox slab in the logs.
- **The export** as in 9267: 497 models and 224 primitive meshes lightmapped, 3,338 users, the bake
  30.1 s and its editor 60.5 s.

## The frames (`roof_frames.sh`, `roofs.png`)

9267 left, 9268 right, at four stations: `over` (24 m up in front of the row, looking down on the
roofs), `along` (18 m up past the row's west end), and 9248's `hatch` and `street`, which see the
deli's roof -- already tar -- and so are the control.

    station   mean |d| (codes)    pixels over 8 codes   over 32
    over      3.6 / 3.2 / 3.4      9.4 %                  0.57 %
    along     3.3 / 3.1 / 3.3      6.8 %                  0.30 %
    hatch     2.3 / 1.9 / 2.1      0.007 %                0
    street    2.4 / 2.3 / 2.3      0.41 %                 0.018 %

The change is where the roofs are and nowhere else. At blue hour it is quiet: the tar reads a shade
darker and more even than the concrete did, as a membrane would; daylight would show more.

## The price (`roof_price.sh`, `price/`)

9267's package as both controls, 9268's the subject (the harness names it `glow`), Level Factory's 53
station headings, GL Compatibility:

    controls' spread, median over 53 headings: p95 0.87 ms, draws 0.0 (the noise floor)
    run        draws +mean   draws +min   draws +max   p95 +median ms  p95 +max ms
    control_1          0.3            0           16            -0.43        -0.13
    subject           -0.3          -16            0             0.24         0.82
    control_2         -0.3          -16            0             0.43         1.09

Draws 788 a heading in both, the subject as close to the controls as they are to each other (16 apart
at one heading); the p95's median 2.84 and 3.71 ms for the controls and 3.50 for the subject, +0.24 ms
against a 0.87 ms floor -- a noisy session, and nothing in it can tell the two apart. The roof was one
material and is one material.

## The time

    run    shell   art     export   walk   retire   the drive
    9267   93 s    158 s   167 s    10 s    4 s     7.5 min (449 s)
    9268   95 s    166 s   168 s    10 s    4 s     7.7 min (462 s)

## What is evidence of what

- The roofs: the twelve `zoo_kit_build.gs_empty_rowhome_*` jobs' GLBs and Deli Counter's rebuilt
  `build/gs_empty_rowhome_*.slots.json`.
- The look: `roofs.png`, `roof_frames.log`; the PNGs under `_scratch/frames_9268_roofs/`.
- The price: `price/`; the count: `cold_run.py --end`.
