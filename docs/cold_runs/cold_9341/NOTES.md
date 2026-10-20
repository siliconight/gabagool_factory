# Cold run 9341 -- restaurant_row_001 on Deli Counter 0.236.1 (2026-10-20): the hole's greybox a ring, the stuck walkers gone

Staged from 9340. The tool change since 9340 is Deli Counter 0.236.1 (46a39afa, `patches/patch_dc_hole_ring.py`): a
`hole_edge`'s and a floor hatch's greybox are a ring of four boxes round the hole instead of one box over it, so the
walk test's navmesh -- Lot bakes it from the candidate's greybox lot with visual meshes in it -- no longer floors the
hole over. The prediction, from 9340's attribution: WALKTEST_WALKER_STUCK 8 -> 0, nothing else moved. The seed is
named, 9003, as on 9339 and 9340.

**Run:** 0 interventions (journal 0, unattributed files 0), DONE, drive 8.1 min.

**Findings 118 -> 110, WALKTEST_WALKER_STUCK 8 -> 0** -- the prediction, met: the shell leg's 81 and the art leg's
110 are 9339's own, and against 9339 (`../cold_9340/findings_diff.py workspaces/cold-9339-ws workspaces/cold-9341-ws`)
the one finding that differs is PRESENTATION_TINT_MATERIALS re-measured with the hole's nine new material entries
(73 -> 75 colour-only variants, 1,125 -> 1,134 entries), as on 9340.

**What else was read off the package**, against 9340's (which carried the same modules):

- The drop-edge gate: as 9340's -- 0 undeclared, 18 declared drop edges (9339: 20; the kit's two rim cells), 63,916
  standable and 55,451 reached.
- `interactives.json`: 33, as on 9339 and 9340.
- The light bake: 3,523 lightmap users, as on 9340 (9339: 3,514).
- The look is 9340's -- 0.236.1 moved no module, only the greybox the composer strips -- so 9340's frames stand for
  this package (`../cold_9340/holes_9339_vs_9340.jpg`). Checked, not assumed: the package's `lot/deli_a03/site_base.glb`
  keeps the hole slots' nodes by name -- the ring's four on 9341, the one box on 9340 -- and none carries a mesh.

**The hole's price** (`price/`): 9339's package, the holes absent, as the control twice, and this one, at the
package's 53 headings through `docs/findings/horizon_glow/price_glow.py` (the harness names the subject `glow`):

    measured control_1  53 headings  draws mean 734 worst 2115  p95 median 2.87 ms
    measured glow       53 headings  draws mean 735 worst 2115  p95 median 2.85 ms
    measured control_2  53 headings  draws mean 734 worst 2115  p95 median 2.83 ms
    controls' spread, median over 53 headings: p95 0.05 ms, draws 0.0 (the noise floor)
    run        draws +mean   draws +min   draws +max   p95 +median ms  p95 +max ms
    glow               1.4           -2            9            -0.02         1.13
    memory after the warm-up: video 130.1 -> 130.4 MiB (textures 77.4 both)

The draws are the hole's nine submissions (the edge, the spoil and the kit, three each) where a station sees them:
+9 at camera_socket_1 / 90, player_start_19 / 90 and patrol_point_12 / 270, +8 at camera_socket_0 / 90, +6 at
objective_2 / 90. Frame time does not move: the p95 median is inside the controls' 0.05 ms floor. **The +1.13 ms max
is not the hole's:** it was camera_socket_0 / 90, which also sees +8 draws, and the same run read attacker_spawn_5 / 90
+1.05 ms with no change in its draws; a second run of the subject (`perf_glow_2.json`) put camera_socket_0 / 90 at
9.10 ms, inside the controls' 9.04 and 9.23, and the whole run's p95 median at -0.00 ms. Eight submissions are about
0.03 ms by the cost per draw cold run 9062 measured (1,730 -> 6,376 draws, 9.49 -> 25.59 ms). Two things that run
read and that are not the hole's: the harness's exit 1 is `PERF_STATION_OVER_BUDGET` on attacker_spawn_5 / 90 at
2,115 draws against the provisional 2,000, which the controls read too; and attacker_spawn_4 / 90 read 1,593 draws
in the second subject run against 1,554 in the first and in both controls -- one package, two counts, the
instrument's variance and not attributed here.
