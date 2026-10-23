# Cold run 9384 -- 0 interventions; restaurant_row_001, seed 9003: the walker's walk of 9383, findings 1 and 2

**What it was for.** The walker's walk of cold run 9383 (`docs/findings/walk_2026-10-23_deli/`), the level they had
walked, staged from 9383. Moved since: Deli Counter 0.261.0 (67decde8, every opening's landing lit in a moody room);
the root's `tools/walk_ladders.gd` (the walk copy climbs the package's own ladder volume) and `tools/light_check.py`
(a station looking down every opening); `tools/cold_drive/cold_drive.sh` runs the light check on every walk copy.

**Every leg ran, `INTERVENTIONS: 0`**; 10.6 min (08:50:26 to 09:00:59). The drive's new light step ran and reported
FAIL 5, PASS 31, REPORT 1 without stopping the run, as it is meant to (`light_check.txt`).

**Finding 2, the roof ladder: fixed in this walk copy.** `docs/findings/walk_2026-10-23_deli/ladder_probe.gd`, run
headless on `_runs/walk_9384_restaurant_row_001` as shipped: the climb peaks at feet 7.603 m against the roof's 6.6
(`ladder_probe.out.txt`); on 9383's walk copy it peaked at 4.463 and bobbed. 7.603 is the investigator's
"package volume in the group" arm to the millimetre.

**Finding 1, the black opening: NOT fixed by this run, and the cause was elsewhere.** The landing lamps reached the
package (`cold_storage_landing`, `basement_corridor_landing` in `lot/deli_a03/art/fixtures/deli_a03_fixtures.glb`) and
changed the basement stair's view by nothing measurable: through its rim p50 31.3 on 9383, 31.5 here. The ground
floor's ladder hole into the basement read black inside its rim on both (p50 0, p95 9 and 12) with a lamp lit beside
it below. The cause is Level Factory 0.211.0's backdrop ground, a plane at y -0.10 inside every ground slab that shows
through every hole into a basement as a black lid; hidden alone, the hole shows the ladder and the lit floor. Traced in
the finding's README. Fixed in Level Factory 0.237.0 (`patches/patch_lf_backdrop_frame.py`), to be proven by the next
cold run.

**The light check, read against the frames.** Its first verdicts on openings were wrong both ways: it FAILED the
broken-floor hole (frame p50 9) and the roof hatch (frame p50 0), which both show their lit landing, and PASSED the
black ladder hole (frame p50 42). The frame is mostly the floor round an opening. It now judges an opening through its
rim (`patches/patch_light_check_through_rim.py`); re-run on this walk copy, the ladder hole FAILS at through-p95 12 and
the other five openings pass (`patches/light_check_through_rim/light_check_9384_as_shipped.txt`). The three rooms that
failed on 9383 still fail: deli_a03's basement vault (p50 3 under MOODY 5), the office lobby (8 under 10), the
pharmacy's retail floor (2 under 10).

**Finding 4, the stair's open underside, is not in this run**: Deli Counter 0.262.0 builds it solid, after the run.

The walk copy `_runs/walk_9384_restaurant_row_001` handed to the walker.
