# cold run: cold_9003

begun 2026-09-09 07:19:34
2427 source files hashed across 10 tools

| when | kind | what |
|---|---|---|
| 2026-09-09 07:21:02 | observation | operator error, not a pipeline fault: 'batch create' was given a path relative to the factory root while -C had already moved the CWD to the workspace. Re-invoked with an absolute path. Recorded here rather than silently corrected; it is not counted as an intervention because nothing about the tools or the inputs changed. |
| 2026-09-09 07:21:47 | observation | plan reports the brief's theme 'delco_1997' has NO Pixelcoat profile (pixelcoat carries 'delco', not 'delco_1997') and no Zoo species carrying that style across 56 scanned -- the kit would fall back to flat colour. The brief is a shipped example (level_factory/examples/delco_batch/briefs/restaurant_row_001.json), so a shipped input names a theme the shipped theme library does not have. Not touched: this run targets graybox, where it does not bite. Recorded because fixing it by editing the brief would be exactly the failure mode item 17 is named for. |
| 2026-09-09 07:21:48 | observation | plan is clean otherwise: 3 candidates (seeds 9003/9104/9205), 12 jobs, deli_generate -> lot_assemble -> laser_tag_evaluate + walktest_navqa per candidate. |
| 2026-09-09 07:23:56 | intervention | INTERVENTION 1: brief archetype 'commercial_strip' matched no DC preset, so deli_generate raised UnknownArchetype and NOTHING ran. Fixed in the TOOL, not the brief: added commercial_strip -> corner_deli to level_factory's _ARCHETYPE_ALIASES. Chose the tool side because editing the brief fixes one run and the alias fixes every consumer who writes a plausible archetype name -- and the resolver's own docstring offers both as equal-cost. Chose corner_deli over facade_storefront because the brief's objectives are enter_kitchen / reach_office / crack_safe: the crew must get INSIDE, and a facade preset is a non-enterable shell. |
| 2026-09-09 07:24:07 | observation | the failed run exited 0. 'internal error: brief archetype ... matches no DC preset' was printed, no mission ran ('status' says so), and the shell exit code was 0 -- so a wrapper or CI step keying on the exit code would have recorded this cold run as a success. Not fixed during the run; filed as a defect afterwards. |
| 2026-09-09 07:32:19 | observation | all 12 jobs succeeded, 3 candidates built and distinct, 0 blockers, 69 findings. Laser Tag on all three: player_stuck_events 0 and enemy_stuck_events 0 -- the corpse-collider fix (roadmap 124, Laser Tag 0.13.0) holds on a map it was not developed against. route_completion_rate is still 0.0 on all three, and the graders say why: INSTANT_CONTACT at 0.4-0.7s ('spawns may be too close') and NO_REACTION_TIME with survival 2.4-3.8s. The crew is under fire before it can move, which is spawn placement, not traversal. |
| 2026-09-09 07:32:19 | observation | CAUTION ON AN INSTRUMENT I BUILT THIS SESSION: the 0.12.0 cover measure reads almost identically on two different maps -- market_row_001 has_cover 0.752 / fully_open 0.214 / avg_open 3.66, restaurant_row_001 0.764 / 0.211 / 3.70. Either both sites are genuinely similar (both are Lot strips of the same generated shell) or the measure does not discriminate between maps. Two maps cannot tell those apart. Not a finding, a flag against trusting it as a comparator until it has been read on a site that should score differently. |
| 2026-09-09 07:32:48 | observation | TWO INSTRUMENTS DISAGREE, and neither is obviously wrong. Lot's LOT_ENEMY_SPAWN_STANDOFF ran on all 3 candidates, moved 1-2 of 6 enemy spawns, and reports the opening as fair -- seed_9003: 'the nearest enemy to the crew spawn is Enemy_4 at 23.4 m ... It is a fair opening because a building stands between the two'. Its message names the exact symptom it exists to prevent: 'Without this the opening engagement starts before the crew can move, which Laser Tag reports as INSTANT_CONTACT and which ends the run in a team wipe inside ten seconds.' Laser Tag then reports INSTANT_CONTACT at 0.4-0.7s and team wipes at 2.4-3.8s on all three. So either the building is not between them at runtime, or standoff distance is not what decides it. Not investigated during the run; this is the next thing to chase. |
| 2026-09-09 07:34:08 | observation | advancing the target graybox -> dispatch-handoff. Not counted as a re-run with different arguments: it is the next phase of the documented flow (run -> approve brief + candidate -> run to target), not the same step re-invoked with a flag added to make it pass. |
| 2026-09-09 07:41:56 | observation | export refused after dispatch-handoff: 'nothing for the entry scene to instance -- no presentation/lux.applied.tscn and no site.tscn'. Not a defect and not counted: the handoff output is structurally identical to cold_9002's, which exported fine, and cold_9002 had also run the art/light layer (lux_apply, patina_apply, patina_dressing, lux_fixture_gate). A portable export needs the presentation scene, so the flow is run --art --target presentation, then export. Proceeding to that -- which is also where the delco_1997 theme gap observed at plan time will actually bite. |
| 2026-09-09 07:45:43 | intervention | INTERVENTION 2: the art layer refused -- 'refusing to run an art layer against a theme that does not resolve' -- because the brief's theme delco_1997 has no Pixelcoat profile. This gap is OLD: themes.py's own docstring records cold_7002 hitting the identical error, and roadmap 72 responded by adding the pre-flight CHECK rather than the profile, so the content gap has stood since. Fixed by GROWING THE OWNING TOOL, per USING_THE_FACTORY.md's gap protocol: pixelcoat/profiles/themes/delco_1997.json, a real profile built only from grammars already in the library. NOT aliased to delco -- an alias routes around the gap and leaves the next consumer naming a period theme with nothing behind it. NOT a copy of delco either: it differs where 1997 differs, bronze anodized storefront glass instead of mirror blue, VCT floor instead of generic tile, orange-peel drywall, Delco plastic. |
| 2026-09-09 07:47:57 | observation | gated package produced: export -> LF_restaurant_row_001.portable-godot, and portability-test PASS with scene_instantiated true, 34 resources, 0 missing, 0 absolute paths, 0 external references, 0 parser errors, 0 shader errors, engine_check passed. Item 17's acceptance condition is met. The run ends here; anything after this is not counted. |


## CORRECTIONS FILED AFTER `--end`

Appended by hand on 2026-09-09, after the run was closed, because two entries
above are wrong and `CLAUDE.md` says a refutation is cheaper to keep than to
rediscover. The interventions count is NOT changed by either: the count is
2 and the hash detector agrees with the journal at 2.

**1. The exit-0 observation is RETRACTED. There is no such defect, and the
artefact was mine.** The entry at 07:24:07 says a failed run exited 0 and that
a CI step keying on the exit code would have called it a success. Tested
directly afterwards:

```
python level_factory/__main__.py ... run no_such_mission_xyz      -> exit 1
python level_factory/__main__.py ... run no_such_mission_xyz | tail -2  -> exit 0
```

A pipeline returns the exit status of its LAST command, so the 0 was `tail`'s.
Every run in this journal was invoked as `... 2>&1 | tail -N`, so every exit
code observed during it is `tail`'s and says nothing about the CLI. The code
path is also correct on inspection: `apps/cli/main.py` maps an unhandled
exception to `EXIT_INTERNAL` and `__main__.py` does `sys.exit(main())`, and
`UnknownArchetype` is not a `LevelFactoryError`, so the archetype failure
would have exited 5. `CLAUDE.md`'s first rule, earned again -- name what
produced an artefact before concluding anything from it.

**2. Intervention 1's FIX was wrong and has been reverted. The intervention
still counts.** The entry at 07:23:56 records adding
`commercial_strip -> corner_deli` to `_ARCHETYPE_ALIASES`, and argues the tool
side generalises better than the brief side. Roadmap 118 had already settled
that against the corpus: `archetype` means the BUILDING, 17 of the 19
multi-building briefs on disk already name one, and its expensive half says in
as many words that "aliasing here would resolve the error and keep the
confusion". `level_factory/tests/test_archetype_resolution.py` failed within
the hour, because `_KNOWN_UNRESOLVABLE` is written to fail when an entry
starts resolving. The pipeline had said so too, twice, in this run's own
output: `[site] 3 buildings, ONE archetype ... the same generated shell is
placed 3 times` -- which was the alias's own product, three identical delis
standing in for a restaurant row.

The alias was reverted before anything was committed. What shipped instead is
the brief naming its anchor building, `corner_deli`, in
`level_factory/examples/delco_batch/briefs/restaurant_row_001.json`.

**What this does to the run's result.** The gated package reported at 07:47:57
was real and its portability test passed, but it was standing on the wrong
fix: it placed one shell three times. The honest reading of cold run 9003 is
that `restaurant_row_001` was not buildable as shipped without a design
decision that the roadmap had recorded and this run did not read first.
