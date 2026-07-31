# Migrations

One-shot scripts that have already run. **Do not delete them.**

Twice in one session a file the device bridge served stale was recovered by
applying the patches that followed an older backup and confirming the result
landed on the byte count the device reported. That works only because each
script records the exact before-and-after text it applied. These are the only
record of how the current source came to be.

Moved here by `tidy_migrations.ps1`. What stays at the root: the checkers
(`check_*.py`, `gdcheck.py`), the harnesses (`library_walk.py`,
`rebuild_buildings.py`), the standing tools, and the documents.

The split is a RULE, not a list -- `patch*.py` and `commit_*.ps1` are
generated name-spaces, so any enumeration of them is out of date the next time
somebody fixes something.

## 2026-07

| script | bytes | last written | what it did |
| --- | ---: | --- | --- |
| `commit_backup_cleanup.ps1` | 4209 | 2026-07-31 14:22 | Untrack the editor backups that just got committed, and stop enumerating. |
| `commit_gate_hardening.ps1` | 4299 | 2026-07-19 22:52 | commit_gate_hardening.ps1 |
| `commit_kerb_pass.ps1` | 5284 | 2026-07-29 23:18 | Commit the kerb-cut and step-gate work. Second pass; the navmesh/walker |
| `commit_nav_pass.ps1` | 9072 | 2026-07-29 21:40 | Commit the navmesh/walker pass across the repos it touched. |
| `commit_pass.ps1` | 9150 | 2026-07-19 10:31 | commit_pass.ps1  --  version bumps + CHANGELOG + commit + tag (4 tool repos) |
| `commit_placement_gate.ps1` | 3669 | 2026-07-19 13:42 | commit_placement_gate.ps1 |
| `commit_root_pass.ps1` | 5983 | 2026-07-30 07:43 | Commit the factory-root half of the step pass. The lot and deli_counter halves |
| `commit_scoped_failure.ps1` | 7548 | 2026-07-28 16:16 | Lot 0.30.0 + Level Factory 0.22.0 + factory 1.14.0. |
| `commit_session.ps1` | 5902 | 2026-07-27 10:58 | Commit the 2026-07-27 pipeline-integrity work, one repo at a time. |
| `commit_step_pass.ps1` | 8487 | 2026-07-30 00:17 | Commit the step-gate pass: the accessor, the player capsule, the derived slab |
| `commit_tools_pass.ps1` | 7088 | 2026-07-30 07:55 | Commit the tooling pass: the site_steps CLI, the build-freshness gate, and the |
| `commit_walkable_pass.ps1` | 8517 | 2026-07-30 16:38 | Commit the walkable-pack pass: the step-up fix, the site packager's host |
| `commit_walker_and_probe.ps1` | 4920 | 2026-07-28 20:26 | Lot 0.32.0 + factory 1.15.0, then the probe that settles item 16. |
| `patch_agent_accessor.py` | 8012 | 2026-07-29 23:44 | Let _agent() actually return the contract. |
| `patch_build_stamp.py` | 6939 | 2026-07-30 07:55 | Make rebuild_buildings.py record what each export was built from. |
| `patch_claude_md_endings.py` | 3494 | 2026-07-30 07:55 | Close the hole in the reconstruction rule: line endings. |
| `patch_claude_md_slope.py` | 5527 | 2026-07-31 04:02 | Record the SLOPE half of the contract tension, measured. |
| `patch_claude_md.py` | 7959 | 2026-07-30 07:43 | Write down what this pass cost, in the three places it belongs. |
| `patch_findings_source.py` | 14867 | 2026-07-31 08:31 | Phase 2: read findings from the thing that measured them. |
| `patch_gate_threshold.py` | 10631 | 2026-07-31 09:35 | Blocking is `major`. Moderate is advice, and advice does not fail a build. |
| `patch_gate_visible.py` | 3886 | 2026-07-29 23:37 | Make the step gate's output survive library_walk's filter. |
| `patch_gates_bind_text.py` | 2759 | 2026-07-31 13:35 | The major list still says it does not affect the verdict. It does now. |
| `patch_gates_bind.py` | 7408 | 2026-07-31 10:41 | Phase 1 step 3: a major gate finding fails the site. |
| `patch_gdcheck_invoke.py` | 7682 | 2026-07-30 08:37 | Stop gdcheck.py depending on a PATH entry that pip warns it did not create. |
| `patch_kerb_angle.py` | 20911 | 2026-07-30 00:17 | Make the kerb cut cover the crossing, the slab stack legal, and the gate honest. |
| `patch_kerb_cuts.py` | 8735 | 2026-07-28 21:22 | Drop the kerb where a route crosses it. |
| `patch_kerb_junction.py` | 8338 | 2026-07-30 17:00 | Drop the kerb where a ROAD crosses it, not only where a path does. |
| `patch_manifest_walk.py` | 4480 | 2026-07-30 09:03 | The pack manifest lists a flat directory. The pack is no longer flat. |
| `patch_nav_cell.py` | 8525 | 2026-07-29 19:28 | Let the bake tell a steep ramp from a tall step. |
| `patch_nav_climb.py` | 6653 | 2026-07-28 22:45 | Stop the navmesh promising climbs the body cannot make. |
| `patch_pack_paths.py` | 8888 | 2026-07-30 09:02 | Copy pack assets to the paths the scene actually references. |
| `patch_package_walkable.py` | 12675 | 2026-07-30 08:45 | Give the SITE packager what the BUILDING packager already has. |
| `patch_player_and_gate.py` | 11118 | 2026-07-29 23:29 | Wire the step gate for real, and stop hardcoding the player. |
| `patch_player_direction.py` | 8788 | 2026-07-30 16:50 | The step-up reads where the body ENDED UP, not where it is trying to go. |
| `patch_player_slope.py` | 5880 | 2026-07-30 20:43 | Don't try to step up a slope. Steps have walkable tops; ramps do not. |
| `patch_player_step.py` | 13511 | 2026-07-30 08:23 | Fix the step-up in the shipped player: it climbs tall steps and fails on curbs. |
| `patch_ramp_foot.py` | 15240 | 2026-07-28 22:25 | Land the stair ramp on the floor it starts from. |
| `patch_run_summary2.py` | 2341 | 2026-07-28 08:56 | Print eliminated candidates, and give each not-run job its reason. |
| `patch_stair_pitch_exact.py` | 10406 | 2026-07-30 16:57 | Measure the ramp's actual tilt, not the bounding box around it. |
| `patch_step_contract.py` | 5219 | 2026-07-28 21:16 | Record the step number a capsule actually obeys, and make Lot check it. |
| `patch_steps_cli.py` | 12239 | 2026-07-30 07:55 | Make site_steps.py's own command line able to report its own worst finding. |
| `patch_sweep_gates.py` | 9737 | 2026-07-31 04:21 | Phase 1 step 1: show what the gates found. Change no verdict. |
| `patch_walker_waypoint.py` | 8873 | 2026-07-29 18:27 | Stop the walker eating the waypoint that steers it round a corner. |
| `patch_walktest_timeout.py` | 6519 | 2026-07-29 19:51 | Make the walktest timeout reachable from outside walktest.py. |
| `patch_wp_default.py` | 3777 | 2026-07-29 21:02 | Make the waypoint radius derive from the body instead of sitting at 0.15. |
| `patch2_fixups.py` | 5419 | 2026-07-28 09:11 | Two fixups: my broken patch script, and a test I invalidated without updating. |

