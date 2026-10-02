# The real look, priced in a level: A against B

2026-10-02. Zoo 1.46.0's changelog left "frame time ... nobody has walked a
level with these in it" as not measured. This is that measurement.

## What was built

`gas_block_001`, seed 9080 (bank_tower_a02, freight_terminal_a01,
gas_station_a03), built twice by the whole pipeline from the same brief,
differing ONLY in which Zoo the workspace pointed at:

* **A** -- a worktree at Zoo 1.45.0 (`1f8ca29`): the pixel look.
* **B** -- a worktree at Zoo 1.46.0 (`66dea46`): the real look on the video
  poker, the ATMs and the counter's tills.

Every other tool was the live checkout (Level Factory 0.128.0). Not cold
runs: nothing was journalled. Workspaces `ab-zoo-a-ws`, `ab-zoo-b-ws`.

## What was measured

Level Factory's fixed-station harness on a fresh copy of each package, GL
Compatibility: 14 stations, 53 views. Run four times on an idle machine --
A, B, A again, B again -- so each package has a repeat that says how far two
passes over the same bytes differ. Reports: `perf_ab_a.json`,
`perf_ab_b.json`, `perf_ab_a2.json`, `perf_ab_b2.json`.

| pass | mean p95 ms | mean median ms | mean draws | views over 11 ms |
|---|---|---|---|---|
| A | 4.99 | 4.53 | 1079.2 | 1 |
| B | 5.13 | 4.62 | 1079.4 | 2 |
| A again | 5.14 | 4.61 | 1079.2 | 2 |
| B again | 5.16 | 4.62 | 1079.4 | 2 |

Per view, p95:

| pair | mean difference | mean absolute difference |
|---|---|---|
| A to A again (same package) | +0.15 ms | 0.26 ms |
| B to B again (same package) | +0.03 ms | 0.37 ms |
| A to B | +0.14 ms | 0.23 ms |
| A again to B again | +0.02 ms | 0.32 ms |

**Draws**: identical between the two passes of each package in all 53 views.
B differs from A in 10 views, by one draw each way: +8 in total, at most +1
and at least -1 in a view.

**Frame time**: A to B moves by no more than a package moves against
itself. The instrument can see 0.3 ms and saw nothing larger.

## Retracted: the first set of passes

Kept because it is cheaper to keep than to repeat. The first A, B, A passes
ran while Zoo's test suites were running on the same machine. They read A
6.30, B 5.55, A again 5.70 mean p95 -- the two passes of ONE package 0.6 ms
apart, more than A to B. Draws were already identical; frame time was not
usable. The table above is the rerun with nothing else running.

## And cold run 9135's perf table read high

Run 9135's package is B's lot built by Level Factory 0.127.0. Its harness
pass, recorded in `docs/cold_runs/cold_9135/NOTES.md`, read a mean p95 of
6.79 ms and 16.70 ms at `highest_vantage` yaw 90. The same view at the same
2,160 draws reads 9.30 to 9.67 ms in the four passes here; `longest_
sightline` yaw 90 read 14.39 there and 7.79 to 8.05 here at the same 1,884
draws. Same draws, same lot, much slower: that pass was not on an idle
machine either. 9135's "6 of 14 stations over budget" is not a figure to
compare anything with. The passes here have 1 to 2 views over 11 ms.

## Not measured

* Texture memory A against B in the level. (Level Factory 0.128.0's
  changelog has the related figure: 344.9 MB to 336.6 MB on 9135's package
  from compressing the eight filtered atlases.)
* Any hardware but this machine.
* Zoo 1.47.0 and 1.48.0 (the lottery dispensers, the cigarette art).
