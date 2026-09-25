# cold run: cold_9078

begun 2026-09-25 07:34:11
3072 source files hashed across 10 tools

| when | kind | what |
|---|---|---|
| 2026-09-25 08:15:27 | observation | GRABOX LEG CLEAN: 12/12 jobs succeeded, 3 distinct candidates, blockers open 0, total findings 43, exit 0. Laser Tag grades: seed_9078 PASS_WITH_TUNING (4 WARN/3 PASS), seed_9179 WARN (5/2), seed_9280 PASS_WITH_TUNING (4/3). |
| 2026-09-25 08:15:28 | observation | CANDIDATE seed_9280 SELECTED, on the default rule (best laser_tag grade) since this run's purpose -- Pixelcoat 0.47.0 pack digests and LF 0.111.0/0.112.0 cache+intactness -- is candidate-independent, unlike 9077's. Two candidates tie at PASS_WITH_TUNING with an identical 4 WARN/3 PASS split, so the tiebreak is metrics: seed_9078 reports avg_player_survival_seconds 10.13 against seed_9280's 72.46 and seed_9179's 126.89. 10 s is a seven-fold outlier and reads as a meat grinder; engagement distance 22.01 m vs 18.96 m does not offset it. Recorded rather than acted on: nothing here is a defect claim, and no geometry was touched. |
| 2026-09-25 08:19:00 | observation | ART+GAMEPLAY LEG CLEAN, exit 0, blockers 0, 63 total findings. All 3 candidates' graybox jobs read 'cache' -- correct, they were built in the graybox leg of this same run and nothing upstream changed. presentation_compose SUCCEEDED, where it exited 3 on the chronic z-fight gate on runs 9072, 9073, 9075, 9076 and 9077. NOT ATTRIBUTED TO THIS RUN'S CHANGES: nothing in Pixelcoat 0.47.0 or LF 0.111.0/0.112.0 touches coplanar geometry, and the scenes are not comparable -- site.tscn here carries 59 solids with 0 coplanar pairs, against 9077's reported 525 solids and 79 pairs. Different candidate, different site, 9x the solid count. The per-building composes DO still report stair-vs-floor coplanar findings (base:stair0_0_N against floor_parts_back / floor_stockroom / floor_main_floor, areas 0.311-0.418) and did not block. Recorded so the next run does not read this as a fix. |
