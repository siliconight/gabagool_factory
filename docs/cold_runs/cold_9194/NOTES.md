# Cold run 9194 -- 0 interventions; the score is the bank, and the bank's basement wedges the crew on the way out

Proves Level Factory 0.152.0 (roadmap 201): the score is the building the brief
asked for. bank_block_001's brief, last run cold as 9168 on Level Factory
0.144.0, where the breadth sweep's own reading put its heist at b2, not the
bank. Tool versions hashed at `--begin` (11:00:41): Level Factory 0.152.0,
Lux 0.68.2, Deli Counter 0.202.0, Lot 0.97.4, Zoo 1.81.0, Laser Tag 0.23.2.

**`INTERVENTIONS: 0`** (journal 0, unattributed files 0; the three changed
files are the per-candidate Deli Counter specs Level Factory always writes).
One retry: the first drive stopped before building anything, at
`cp: cannot stat 'workspaces/cold-9168-ws/tools.local.json'` -- the driver
copies tool paths from the previous run's workspace, and 9168's is retired.
Only `init` had run; it was moved to `_scratch/cold_9194_stopped/`, the retry
journalled, and the driver re-run against PREV 9193
(`driver_stopped_tools_local.log` keeps the stop). Every leg then ran, 11:05
to 11:50 (44 minutes; 9168 took 22).

## Roadmap 201: the score is the bank

All three candidates, from their site specs:

| candidate | b0 (objective) | spawn | extraction | `objective_from` |
|---|---|---|---|---|
| seed_9054 (picked) | bank_branch_a04 | b1 casino_a03 | b2 strip_retail_a02 | archetype |
| seed_9155 | bank_tower_a01 | b2 strip_club_a01 | b1 freight_terminal_a03 | archetype |
| seed_9256 | bank_branch_a04 | b1 parking_garage | b2 rail_station_a03 | archetype |

The walk scene's objective point is each bank's own `OBJECTIVE_A` in its
`vault_room` (kind `secure`), in the basement: (-54, -3.9, -12.25) on
seed_9054, Godot frame. `LOT_DESTINATION_RESOLVED` (minor, 3) is the direct
consequence: bank_branch_a04's objective hook stood on a desk prop, and Lot
moved the point the bots path to 0.25 m onto walkable floor.

**The companions moved since 9168, the banks did not.** 9168's lots were
bank_branch_a04 + cr_garage + rail_station_a02, bank_tower_a01 +
freight_terminal_a03 + pharmacy_a01, and bank_branch_a04 + mansion_a01 +
pawn_shop_a01. The library grew between the runs and every seed's draw after
the anchor changed (the shape `library-growth-reshuffles-lots` describes).
So this is not a same-buildings comparison, and no finding delta below is
attributed to 0.152.0 unless it is read.

## What making the bank the score exposed

**The picked candidate's crew finishes its route 8% of the time.** Laser
Tag, 25 runs a candidate:

| candidate | route completion | route progress | PlayerStuck | grade |
|---|---|---|---|---|
| seed_9054 (picked) | 0.08 | 0.67 | 1,306 | WARN |
| seed_9155 | 1.00 | 0.99 | 5 | PASS |
| seed_9256 | 0.00 | 0.69 | 2,366 | PASS_WITH_TUNING |

**Where.** 1,302 of seed_9054's 1,306 PlayerStuck events, and 2,363 of
seed_9256's 2,366, stand in one 2 m cell. Mapped into the building's frame
(both b0s at rot 0), both are the SAME point of bank_branch_a04: local
(-16.88, -6.89) at the basement floor (-4.20), in `vault_antechamber`, 0.31 m
north of the lower landing of the service stair `a03_stair_bw` (basement to
`grand_lobby`; landing rect x -17.9..-16.7, y -8.8..-7.2; the stair's solid
block starts at x -16.7). The capsule is 0.36 m from that block's corner.

**When.** On the way OUT. On seed_9054 the crew reaches the vault about 30 s
in, and the first stuck event follows at about 44 s: of the 49 player-runs
that stuck, 45 stuck after reaching the vault. The extraction is east, at
(52, 0, 13); the wedge is 25 m west of the vault, at the stair the navmesh
routes the exit through.

**Two instruments disagree there, and which is right is not established.**
`walktest_navqa` passes on all three candidates. Its chain walks proxy_3 (the
vault, (-54, -4.2, -12)) to proxy_4 (ground floor, (-56, 0, 12)) -- path proof
ok, walkers 12 of 12 -- so a navmesh walker leaves that basement and Laser
Tag's crew does not. The walktest never walks the mission's own order (vault
to extraction, proxy_3 to proxy_12); Laser Tag's `LT_ROUTE_NEVER_COMPLETED`
text says it "walks the same spine", which holds for the anchors and not for
their order. Unattributed between bank_branch_a04's geometry at the stair
foot and Laser Tag's crew controller until a frame or a probe at that point
says which.

**Why the picker took it.** `tools/cold_drive/pick_candidate.py` drops a
candidate only for a failed walktest or a MAJOR Laser Tag route finding,
then takes the fewest major findings and the lowest seed. Laser Tag raises
`LT_ROUTE_NEVER_COMPLETED` only at 0% completion, so seed_9054's 8% carried
no major finding, tied seed_9155 at zero, and won on the lower seed. Route
completion and Laser Tag's grade were never read.

## Other figures

- **Shell:** 3 candidates, all distinct; 0 blockers of 46 findings.
- **Art:** 0 blockers of 66 findings.
- **The bake:** 415 models and 1,366 primitive meshes lightmapped, 9 kept
  dynamic; 82 steady rigs baked, 20 failing left live; **217 room fills**
  (Lux 0.68.x and Level Factory 0.151.0 on a second level; 9193 laid 267);
  3,651 users, 87.5 s in the editor.
- **Findings against 9168's record, 63 -> 66:** new `LOT_DESTINATION_RESOLVED`
  3 (above), `LOT_CREW_SPAWN_PUSHED` 1 (seed_9256's spawn moved 3.5 m off a
  building), `LT_ROUTE_NEVER_COMPLETED` 1 (seed_9256), `LT_MAP_BLIND_MAP` 1;
  `LOT_PATH_END_OFF_DOOR` 3 -> 5, `LOT_ROUTE_COVER_PLACED` 2 -> 4,
  `LOT_SIGHTLINE_UNBREAKABLE` 1 -> 2, `LT_MAP_ENEMY_STUCK` 1 -> 2; down:
  `LT_OPEN_SIGHTLINE` 6 -> 2, `LT_MAP_INSTANT_CONTACT` 3 -> 1,
  `LT_MAP_TRAVERSAL` 3 -> 2, `LOT_ENEMY_SPAWN_STANDOFF` 4 -> 3,
  `PRESENTATION_ZFIGHT` 1 -> 0. Companions and roles both moved; none of
  these is attributed further.
- **Lot's pacing** (not a gate): still judged against its 7-15 min default
  with no travel counted -- roadmap 200, whose fix (Level Factory 0.153.0)
  was written during this run, to apply after it.

**Not checked:** frames of the stair foot; frame time.
