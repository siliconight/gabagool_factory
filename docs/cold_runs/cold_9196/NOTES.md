# Cold run 9196 -- 0 interventions; gas_block_001 ships, with the gas station as its score

gas_block_001, 9195's brief and seeds. Tests Deli Counter 0.203.0 (roadmap
205): a slot owns its own greybox nodes, never a sibling slot's, so
gas_station_a02's `cooler_run` measures its own 3.28 m and the art leg that
stopped 9195 passes. Tool versions hashed at `--begin`: Deli Counter 0.203.0,
Level Factory 0.153.0, Lux 0.68.2, Lot 0.97.4, Zoo 1.81.0, Laser Tag 0.23.2.

**`INTERVENTIONS: 0`** (journal 0, unattributed files 0; no tool source file
changed on disk). Every leg ran, 15:00 to 15:39.

## Roadmap 205: the art leg passes

- **Art:** 0 blockers of 69 findings. 9195 stopped here on one blocker,
  `PRESENTATION_PLACEMENT_MISMATCH`, gas_station_a02's `cooler_run`
  read at 25.442 m against a 3.28 m module.
- **Findings against 9195, `PRESENTATION_PLACEMENT_MISMATCH` 1 -> 0.**
  The rest of 52 -> 69 is the legs 9195 never reached:
  - `DISPATCH_FINDING` 0 -> 7 is the export's handoff;
  - one more of each `LOT_*` code (`LOT_COVER_PLACED`,
    `LOT_DESTINATION_RESOLVED`, `LOT_ENEMY_SPAWN_*`, `LOT_GROUND_EXTENDED`,
    `LOT_PACING_OUTSIDE_TARGET`, `LOT_ROUTE_COVER_PLACED`) is the themed
    site's own Lot run;
  - `LOT_PATH_END_OFF_DOOR` 6 -> 8;
  - `LUX_NO_ROOM_PROBES` 0 -> 1 is the Lux stage.
- **The gate on its own, before the run:** re-run on the real
  gas_station_a02 greybox with 9195's kit and the compose job's arguments,
  it read 167 of 167 matched. 9195's manifest read 166 and 1 on the same 167.

## The level

| | |
|---|---|
| picked | seed_9080 (seeds 9080 and 9181 tied at 0 majors and route completion 1.00; 9282 read 0.52) |
| score | b0, gas_station_a02 (`objective_from: archetype`) |
| spawn | b1, rail_station_a01 |
| extraction | b0 -- the score building itself (roadmap 206) |
| pacing | heist, about 2.8 min against the brief's 25-35, "likely TOO SHORT", non-blocking |

**The bake:** 443 models and 2,086 primitive meshes lightmapped, 7 kept
dynamic; 100 steady rigs baked, 20 failing left live; 172 room fills;
4,147 users, 104.1 s in the editor.

**The walker's calls this run already shows against:** the extraction is the
score building, where the walker's default is a getaway vehicle outside it
(roadmap 206); and the pacing window is not a hard rule (roadmap 200).

**Not checked:** frames, frame time.
