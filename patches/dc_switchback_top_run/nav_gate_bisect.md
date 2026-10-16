# The seam wall's underside, bisected on the nav gate (2026-10-15)

`patch_dc_switchback_top_run.py`'s first cut (a seam wall from the storey floor to the slab underside) failed
Deli Counter's pre-commit hook on ONE shell of 157: `cbp_town_finale_midbalanced_schemafixed`, stair 0,
`no_path (endpoints on disjoint islands (lower on 82, upper on 46))`, grid sweep false at all 8 origins. Its
mirror, stair 1 (same stair at x +34, same facing), passed. At 0.224.1 both passed (the previous hook log,
`nav-gate: 157 shell(s) passed`), so the change caused it; `navgate_baseline.json`'s entry for this shell is
historical and not what the gate reads.

Each variant: a temporary edit, `python build.py specs/cbp_town_finale_midbalanced_schemafixed.json`, then
`python nav_gate.py build/cbp_town_finale_midbalanced_schemafixed.glb`; the edit reverted after each.

| variant | seam wall | result for stair 0 |
|---|---|---|
| A, as first written | floor (4.0) to slab underside, y -28.05..-21.065 at x -33.945 | no_path; lower island 101 polys, y 0.3..2.25; upper 612 polys, y 0.3..8.25 |
| C | no seam pieces (cut change only) | ok |
| B | seam rail kept, seam wall dropped | ok |
| E1 | wall bottom +1.0 m (5.0..7.7) | ok |
| stepped | bottom follows the flight below + body height + a riser, in 1 m boxes (4.0 for the first 4 m, then 4.58, 5.19, 5.80) | no_path; the SAME 101 polygons, y_max 2.25 |
| shipped | bottom at the floor + the contract's body height (5.8..7.7), one box | ok |

The lower island tops out at 2.25 m, i.e. the lower flight is cut about 3.6 m along its run -- where
`security_console_cluster` (a spec volume at storey 1, z 4.0..5.8, x -33..-27, y -26.2..-23.8) already leans a
metre over the lower run from the other side (`STAIR_VOLUME_INVADED`, a warning the spec carries). The mirror
stair's volume (`cash_counting_tables`) stops short of its run, which is why the mirror passed.

**What the stepped variant refutes:** that the bake objects to headroom under the strip as such. The stepped
underside gave the band at 2.25 m 2.3 m of headroom and the gate still cut the flight on exactly the same
polygons; a uniform bottom at 5.0 or 5.8 did not cut it. The mechanism in the bake is not settled here, and
the shipped rule is the one measured clean, not the one reasoned to. A probe that prints the bake's walkable
spans across that band is what would settle it; it was not built, because the wall's placement over the lower
run is the part worth changing if this ever recurs (a balustrade on the upper flight's own edge would not stand
over the lower run at all).

The whole-library hook run after the shipped rule is the proof for the other 156 shells (`dc_commit_hook_0225b.log`
in the session's scratchpad; its verdict is in the commit).
