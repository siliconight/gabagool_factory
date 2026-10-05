## [0.141.0] - The fixed-station harness measures every heading twice and keeps the lower pass

Four price runs on 2026-10-05 had the same problem. Cold runs 9155, 9156,
9158 and 9159 were each priced A / B / A2, the same package measured twice
as the control. Each time a heading jumped 1-4 ms in one of the three runs
with no draw changed:
- camera_socket_6 at 270, twice;
- defender_spawn_21 and _22;
- camera_socket_0.

One run's median frame at camera_socket_6 read 29.7 ms against its twin's
23.9, and its p95 43.0 against 25.5. Each had to be argued away by hand
(`patches/zoo_cover_merge/price_robust.py`, the mean-of-two control and a
list of the headings that disagreed).

A hitch -- a stall in the OS, the driver, a late shader -- only ever ADDS
time, so the fastest of repeated measurements is the estimate.

- **`perf_stations.gd` measures the whole station set `PASSES` (2) times**,
  back to back, so a heading's two passes are a full pass apart in time.
  - Each heading keeps the pass with the **lower p95**. p95 is what a
    station's worst heading is chosen by and what the budget judges. A spike
    of three frames moves it and barely moves the median, so choosing by
    median could keep a spiked p95. A slowdown across the whole window moves
    both.
  - Every field comes from that one pass, so a heading's draws and frame
    times describe one measurement.
  - The heading records every pass (`passes`: median, p95, draws) and the
    p95 spread (`pass_spread_ms`), so a hitch shows rather than vanishing.
  - The report's schema is unchanged, and `ms_median` / `ms_p95` mean the
    kept pass.
- **`perf_stations_run.py` prints how many headings' passes differed by more
  than 1 ms p95**, the largest spread, and how many headings drew a different
  number of draws between passes. A different count would mean the two
  passes did not see the same frame. A report from before passes existed is
  said to be one pass per heading.
- **Measured**, on a quiet machine, against this session's single-pass
  controls. Each row is one package measured twice back to back (A, A2),
  at 53 station x heading pairs:

  | control | headings off > 1 ms (median) | off > 1 ms (p95) | largest median gap | largest p95 gap |
  |---|---|---|---|---|
  | 9158's package, one pass | 2 | 5 | 3.51 ms | 8.52 ms |
  | 9159's package, one pass | 2 | 11 | 1.49 ms | 11.24 ms |
  | 9160's package, two passes | 0 | 1 | 0.24 ms | 1.13 ms |

  - The typical gap did not move (median of the median gaps 0.021 and
    0.033 ms against 0.027 ms). What went is the tail.
  - Within each two-pass run, 11 and 5 of the 53 headings' passes differed
    by more than 1 ms p95 (largest 8.66 and 7.01 ms). Those are the hitches
    the lower pass discounted.
  - No heading drew a different count between its passes.
  - One two-pass pair against two one-pass pairs: the before side is the
    better sampled.
  - A run took 91 and 93 s from probe start to report, against 51 and 53 s
    for one pass.
- **The watchdog stays at 600 s.**
  - One run took 52 s from probe start to report on cold run 9159's package,
    three runs out of three (the mtimes of the copied probe and of its
    report), and two passes took 91 to 93 s, well inside it.
  - This patch's first draft doubled it to 1200 s, past the runner's own
    900 s timeout. The runner kills the process tree and keeps nothing, so
    a stalled run would have died before the watchdog could write what it
    had. A test now holds the watchdog under the timeout.
