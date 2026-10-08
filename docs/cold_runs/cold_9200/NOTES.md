# Cold run 9200 -- 0 interventions; responders have somewhere to arrive

bank_block_001, 9199's brief and seeds. Tests two Lot releases:
- **Lot 0.98.2** (roadmap 211): the audit measures cover by its depth, not
  its height.
- **Lot 0.99.0** (roadmap 212, phase 1): where responders arrive.
  - Each open road end gets an inbound lane and a stop where a 1990s
    cruiser fits with its doors open, nearest the crew's way back.
  - The stops and lanes are reserved before the street is parked or stood
    in, and read back after.
  - Each arrival is written as a `responder_spawn` site marker.

Tool versions hashed at `--begin`: Lot 0.99.0, then as 9199 -- Laser Tag
0.25.0, Level Factory 0.155.0, Zoo 1.85.0, Deli Counter 0.203.0, Lux 0.68.2,
Dispatch 0.5.2, Patina 0.29.1, Pixelcoat 0.61.0, Pipeline 0.6.0.

**`INTERVENTIONS: 0`.** The journal holds no entries, and the diff has
nothing changed, added, removed or unattributed. Every leg ran.

## The arrivals

Three on each candidate, no `LOT_RESPONDER_BLOCKED`, no
`LOT_RESPONDERS_NONE`, no `LOT_RESPONDER_ENTRY_NO_STOP`. "Off" is the stop's
distance from the crew's way back; "run" is the lane driven from the road's
end:

| candidate | from | stop | off | run |
|---|---|---|---|---|
| seed_9054 | road 1's end | (-29.9, -1.0) | 0.1 m | 30.5 m |
| | road 0's west end | (-14.0, -22.6) | 11.4 m | 72.5 m |
| | road 0's east end | (7.0, -19.8) | 12.1 m | 79.5 m |
| seed_9155 | road 1's end | (38.6, -12.5) | 1.1 m | 44.5 m |
| | road 0's west end | (52.0, -25.1) | 9.1 m | 144.5 m |
| | road 0's east end | (73.0, -22.2) | 12.1 m | 19.5 m |
| seed_9256 | road 1's end | (23.6, 10.0) | 12.7 m | 22.5 m |
| | road 0's east end | (14.0, -22.8) | 21.5 m | 79.5 m |
| | road 0's west end | (8.0, -25.6) | 25.2 m | 101.5 m |

Seed_9256's three match `tests/test_site_responders.py`'s pure plan of 9198's
site to the centimetre.

**The routes are walked.** Lot's nav QA spawns a bot at every
`responder_spawn`.
- **Bot spawns:** the walktest's count went from 3 to 6 on every candidate.
  Its bots walk from a spawn to the nearest crew point ("bot_spawn ->
  nearest proxy", `nav_qa_director.gd`).
- **Every arrival stop's bot reached its target** on the baked navmesh:
  - seed_9054: 15.7, 11.1 and 5.8 m;
  - seed_9155: 22.5, 11.2 and 6.0 m;
  - seed_9256: 11.7, 13.3 and 13.4 m.
- **Every candidate's walktest** is `ok`, with 0 proof failures and 0
  stranded anchors.

That proves each stop stands on the walkable navmesh with a route to the
nearest crew point. It does not prove a route to the van on every site.

## What the reservation moved

**seed_9054, the picked lot.** One parked car was kept out of bay L15 on road
0, at (6.5, -17.25), where it overlapped the road 0 east-end stop. That is
the bake's 3,645 -> 3,641 users: the four meshes of one car. Its Laser Tag
result is identical to 9199's.

**seed_9256.** Bay L6 on road 1 holds a 4.3 m sedan where 9198 and 9199
parked a 4.7 m SUV (`car_asked: suv`). Parking took the largest car that
keeps clear of the stop's door room. Its Laser Tag result is identical to
9199's.

**seed_9155: the reservation turned away a piece of cover, and the fight
changed.**
- **What moved.** 9199 stood a cargo container at (39.06, -6.73), on
  "route@3 -> Enemy_0", in what is now the road 1 arrival's lane. The
  keep-out refused it. The cover planner broke the line with one car at
  (41.8, -7.9), beside the lane, and dropped the car it had stood at (47.3,
  -10.9).
- **The result.** One fewer piece on the crew's route. Crew deaths in 25
  runs went 0 -> 6, with one team wipe; first contact came at 1.8 s; the
  grade went PASS_WITH_TUNING 81 -> WARN 70.
- **This is the tradeoff a clear lane makes:** a responder's lane is a
  stretch of street the cover planner can no longer stand a truck in. Here
  it made a trivial fight a real one. On another site it could leave a
  route barer than it should be. The cover planner reports any line it
  leaves open (`still_open`), and it left none here.

## Findings against 9199, 63 -> 63, every item attributed

- **`LT_MAP_TRIVIAL_ENCOUNTER` 1 -> 0:** seed_9155. Six crew lost where 9199
  lost none.
- **`LT_MAP_INSTANT_CONTACT` 2 -> 3:** seed_9155, under fire at 1.8 s.
- **Seed_9155's majors 1 -> 0,** with the trivial-encounter hold lifted.

Nothing else moved.

**The site audit** is printed in each Lot job's log, not counted among the
findings. Read from 9199's and 9200's logs:
- **`S_NO_RESPONDERS` (INFO) gave way to `S_RESPONDER_ARC` (MED)** on all
  three candidates. The arcs are 20, 5 and 30 degrees: every stop lies on
  the roads, and these roads all lie to one side of each objective.
- **No `S_RESPONDER_CAMP`.**
- **No `S_NAKED_ANCHOR` in either run,** so Lot 0.98.2's audit fix moved
  nothing here, as its census predicted.

## Other figures

- **Shell:** 3 candidates, all distinct; 0 blockers of 44 findings.
  **Art:** 0 blockers of 63.
- **The bake:** 415 models and 1,366 primitive meshes lightmapped, 9 kept
  dynamic; 81 steady rigs baked, 21 failing left live; 217 room fills; 3,641
  users, 85.7 s in the editor.

**Not checked:**
- **The package.** It carries none of the arrivals, and none of the van's
  markers either: Level Factory's Dispatch staging reads no site markers
  (roadmap 204).
- **Frames of the arrivals.** No vehicle exists to show; the cruiser is
  Zoo's, after the walker's comps.
