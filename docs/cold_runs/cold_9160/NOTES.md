# Cold run 9160 -- 0 interventions; twelve rowhome Empties, not six: the row shows 10 of 12, none more than 5 times

gas_block_001, seed 9080, `empties: "across"`, `--bake-lights`.

**Stack.** Deli Counter 0.184.0 adds `gs_empty_rowhome_g` to `_l`.
Between the twelve houses, every wall kind and every door finish is worn
exactly twice, and no two houses share both. Cold run 9159's 26-house row
was drawn from six designs and showed `_f` seven times.

**Result:** every leg ran, `INTERVENTIONS: 0`.
- Shell: 3 candidates, all distinct; 0 blockers.
- Art exited 1 on 55 findings, as before.
- No `STEM COLLISION`.
- The walk copy is this run's (`cold-9160-ws` in its reference scan).

## The row, measured

`patches/dc_more_rowhomes/count_terrace.py` over each candidate's drawn
site. It reads `blockers[]` marked `empty`, and refuses any other shape.

| run | seed | houses | designs used | most of one design |
|---|---|---|---|---|
| 9159 | 9080 | 26 | 6 of 6 | 7 (`_f`) |
| 9160 | 9080 | 25 | 10 of 12 | 5 (`_f`) |
| 9160 | 9181 | 31 | 12 of 12 | 6 (`_i`) |
| 9160 | 9282 | 29 | 10 of 12 | 5 (`_d`, `_l`) |

No two neighbours are the same house in any of them.

**This is better than six designs, and it is not "each about twice".** That
expectation was mine, and it was wrong. `level_factory/packages/pipeline/
empties.py:97` draws each house uniformly
(`usable[next(stream) % len(usable)]`) and turns away only an immediate
repeat. A bigger library moves the mean; the spread is the draw's. On the
exported seed, `_a` and `_g` were never drawn.

The fix belongs in the tool: deal from a shuffled bag of every design, so a
row of n houses from k designs shows each floor(n/k) or one more times. It
is written as Level Factory 0.142.0 (`patches/patch_lf_terrace_deal.py`).
It goes in its own run, so the next run's price stays attributable.

## Before the run

- Deli Counter's family tests passed (21). `check.py` failed on one item,
  `CATALOG.md is stale`, as six new shells make it. The catalog was
  regenerated (48 lines added, none removed), and the commit hook's
  `check.py` then passed every check.
  - **Found on the way:** `python catalog.py --help` ignores its argument
    and writes the catalog. That was the fix wanted here, but it is not
    what `--help` means anywhere else.
- **Stem plan:** Zoo's own `plan_kit` over every built building
  (`patches/dc_more_rowhomes/plan_stems.py`) found 0 stem collisions and 0
  unknown material slots in 145 buildings and 8,728 modules.

## Frames

`docs/findings/empties_twelve_9160/`.
- From above, the row reads as different houses: three bricks, siding,
  Formstone and painted fronts.
- The two-storey houses step down between the threes.
- The roofs are flat and bare. That is the next block.

## The price

A = 9159's package, B = 9160's, A2 = 9159's again: 53 station x heading
pairs, back to back (`price_twelve.txt`, `price_twelve_robust.txt`).

- **Draws:** median -49 a view, mean -88, from -459 to +76. The control is
  0 at every heading. This is the row's new layout: 25 houses in place of
  26, in a different mix. It is not a cost of having twelve designs.
- **Median frame**, against the mean of A and A2 over the 51 headings where
  A and A2 agree within 1 ms: -0.022 ms. The control's own median is
  -0.013, so there is nothing to price.
- **The package:** 134 MB to 144 MB, from the six new designs' shells and
  kit modules.
- **Light census:** 61 meshes over the cap, the same count, out of 5,027
  meshes (5,246 in 9159).
- **The control hitched again:** attacker_spawn_1 at 90 and 270, A 13.1 /
  12.2 ms against A2 11.7 / 10.7. That is the fifth run in a row. Level
  Factory 0.141.0 (`patches/patch_lf_perf_passes.py`) measures each heading
  twice and keeps the pass with the lower p95. It is next.
