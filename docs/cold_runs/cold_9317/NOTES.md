# Cold run 9317 -- urban_row_001, Lot 0.124.0: an isolated building is a major finding; it reads zero

Staged from 9314 (`stage_batch.py 9317 9314`), driven `cold_drive.sh 9317 9314 urban_row_001 auto`. Tool state at
`--begin`: Lot 0.124.0 (732b4ad), Level Factory 0.215.1, Deli Counter 0.224.1, Zoo 1.113.1, Lux 0.77.0, Patina
0.32.0. What it tested: roadmap 178's graduation of Lot's isolation instrument -- `site_tactical.analyze` now
emits `LOT_ISOLATED_BUILDING` (severity major) in `report["findings"]` beside the warning string.

**INTERVENTIONS: 0** (`--end`: journal 0, unattributed files 0). **Drive exit 0**: shell 14:33, art 14:35,
export 14:38, findings 14:42, walk, retire, DONE 14:42.

- Three candidates: seed_9003 PASS_WITH_TUNING 89 (not counted: LOT_DESTINATION_ABOVE_FLOOR, LT_MAP_TRIVIAL_ENCOUNTER),
  seed_9104 PASS 100, seed_9205 PASS 90; picked seed_9104, as 9314 and 9313.
- `LOT_ISOLATED_BUILDING`: on 0 of the 3 candidates (`isolated_buildings: []` in each `site.site.gameplay.json`),
  and in no findings record. Every candidate's `tactical.findings` carries the other LOT_* codes as before
  (path ends off doors, the ground plate extended, the spawn moves); `lot.py` extends the list with
  `setdefault`, so the list `analyze` now starts is kept.
- Findings 109 -> 109 across the export: nothing moved.

The record of the change: the factory's `patches/patch_lot_isolated_finding.py`, `patches/lot_isolated_finding/`
(3 tests fail on 0.123.0's tree, Lot's suite 847 passed), `docs/findings/open_items_remeasure/README.md` ("178,
the isolation instrument graduated").
