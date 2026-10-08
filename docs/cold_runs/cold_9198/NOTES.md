# Cold run 9198 -- 0 interventions; the getaway van at the spawn, and a crew member inside it

bank_block_001, 9197's brief and seeds. Tests roadmap 206's phase 2, the
first run with the getaway van:
- **Lot 0.98.0** parks Zoo's `step_van` at the kerb nearest the spawn
  building's street door, and puts the crew's spawn and extraction at its
  door.
- **Level Factory 0.155.0** makes the extraction the spawn building.
- **Laser Tag 0.25.0** counts a route as walked only when every point was
  reached.

Tool versions hashed at `--begin`: Laser Tag 0.25.0, Level Factory 0.155.0,
Lot 0.98.0, Zoo 1.85.0, Deli Counter 0.203.0, Lux 0.68.2, Dispatch 0.5.2,
Patina 0.29.1, Pixelcoat 0.61.0, Pipeline 0.6.0.

**`INTERVENTIONS: 0`.** Every leg ran: the journal holds no entries, and the
diff has nothing changed, added, removed or unattributed.

## The van stands where it was asked to

It was parked on all three candidates, each in two kerb bays, with no
`LOT_GETAWAY_NONE`. Reach is from the crew's point to the spawn building's
door:

| candidate | bays | van centre | crew point | reach |
|---|---|---|---|---|
| seed_9054 | L13-14, road 0 | (-2.5, -17.5) | (-4.15, -14.95) | 3.97 m |
| seed_9155 | L25-26, road 0 | (63.5, -20.0) | (61.85, -17.45) | 4.50 m |
| seed_9256 | L3-4, road 1 | (21.362, -0.15) | (18.812, -1.8) | 6.09 m |

**Picked: seed_9054.** It had 0 majors and route completion 1.00. In 9197 it
had 0.84; the picker took seed_9155 then. The frames were shot from the walk
copy by `tools/look_shots.py`, at full scale after the warm-up (208 frames),
GL Compatibility on an RTX 2060, and sent to the walker. They show the van in
the bays outside THE BROKE BANK CASINO, the spawn building, with the crew's
door on the sidewalk side.

**This level is night and rain.** The van reads as a silhouette. The ghost
lettering and the chalky patina do not show at all.

## Seed_9256 was never played: a crew member stood in the van

**What Laser Tag reported.** It refused seed_9256 before a single run --
`SPAWN_IN_COLLISION: LT_PlayerSpawn_1 is inside world collision` -- and
graded it BROKEN on 0 runs (`LT_NOT_EVALUATED`).
- `site_spawns.crew_spawns` puts the crew's other members on rings
  `CREW_SPACING` (2.0 m) out, starting along +X, and tested each point
  against the buildings and blockers only.
- The van's slot stood 1.25 m off the spawn on that side, x 20.062 to
  22.662.
- Member 1 went to (20.812, -1.8), inside it.

**Fixed in Lot 0.98.1** (`patches/patch_lot_crew_clear_of_cover.py`).
`cover_rects` is asked beside `solid_rects`, every piece grown by
`WALL_MARGIN`. The fixture is this candidate's drawn site, byte for byte, and
4 of 6 tests fail without the fix. Cold run 9199 is the proof.

## The fight got easy, and why

Laser Tag flagged `LT_MAP_TRIVIAL_ENCOUNTER` on **seed_9155**: the crew lost
nobody in 25 runs.

**RETRACTED, kept above what replaced it.** While attributing this run, the
finding was first put on seed_9054. It is not there. Seed_9054 lost exactly
one crew member in 25 runs, which escapes the gate's "not a single member".

Crew losses over 25 runs, the same lot on each seed:

| | 9197 | 9198 |
|---|---|---|
| seed_9054: crew deaths, team wipes | 48, 4 | 1, 0 |
| seed_9155: crew deaths | 19 | 0 |
| seed_9054: shots fired a run (median) | 67 | 27 |

**The one-leg spread is the measured difference.** 0.98.0 spreads the
enemies along the one leg of a there-and-back route. It said the crew
"passes them going in and coming out", and that is wrong.
- **The enemies do not wait.** `LT_EnemyBrain._physics_process` sends an
  enemy without a sightline to SEEK, `set_destination(target.global_position)`,
  from the first frame. Every enemy's median time of death was 3.5 to 10.7 s
  on both seeds in both runs, whichever leg it stood on.
- **Where an enemy stands only sets when and from where it arrives.** In
  9198 all six stand at one bearing from the crew, at even steps: seed_9054
  at 16.7, 22.0, 27.2, 32.5, 40.6 and 50.3 m, at -137 to -153 deg.
- **In 9197 the danger was an accident of geography.** Its second leg ran to
  another building. That put two enemies behind the crew on seed_9054, at
  33.5 and 35.7 m on -12 and -22 deg against four at -135 to -158. On
  seed_9155 it put two pairs at one distance each, 77.3/80.2 and
  102.2/103.7 m.

**That is a reading, not a proof.** No variant was run to isolate it.

**Corrected by cold run 9199.** Seed_9256 was played with the van for the
first time and lost 41 crew in 25 runs (49 in 9197).
- **Why it was not single file.** The line from its van to its vault runs
  through the spawn building, so the spread pushed two enemies to either
  side of it. They stood 17.7 and 23.4 m from the crew, 94 deg apart.
- **The better reading.** Crew deaths track enemies arriving together from
  more than one direction. The one-leg spread produces that on some sites
  and not on others.

See `docs/cold_runs/cold_9199/NOTES.md`.

**Not changed.** Enemy placement is provisional until a gameplay layer owns
it (the walker, 2026-09-08). What the fight in a there-and-back heist should
be is the walker's call, so 0.98.1 corrects the comment and keeps the
behaviour. Roadmap 206 carries the question.

## Findings against 9197, 67 -> 59, every item attributed

**The van and the extraction at the spawn:**
- `LOT_SIGHTLINE_UNBREAKABLE` 1 -> 0 and `LT_OPEN_SIGHTLINE` 2 -> 0. All three
  were one 54.4 m line from the extraction to the crew spawn
  (`LT_ExtractionPoint -> LT_PlayerSpawn`, `Route_0`/`LT_PlayerSpawn` ->
  `Route_2`). The two points are now one point.
- `LOT_CREW_SPAWN_PUSHED` 1 -> 0. 9197's crew spawn stood within 1 m of a
  building and was moved 3.50 m. The van's door point stands 1.2 m in from
  the kerb.
- `LOT_COVER_PLACED` 4 -> 2 and `LOT_ROUTE_COVER_PLACED` 4 -> 2. Two Lot runs
  placed cover, 3 pieces and 1, where 9197's four runs placed 1 or 2 each.
  Read as one leg leaving fewer open lines to break; not attributed per run.

**The crew member in the van** (Lot 0.98.1):
- `LT_MAP_SPAWN_IN_COLLISION` 0 -> 1 and `LT_NOT_EVALUATED` 0 -> 1: seed_9256.
- `LT_MAP_OVEREXPOSED_ZONE` 2 -> 1 and `LT_MAP_PLAYER_STUCK` 3 -> 2: seed_9256
  played no runs, so it reports neither.
- `LT_MAP_ENEMY_STUCK` 2 -> 1, made of three changes:
  - 9197's two were seed_9054 (45 events) and seed_9256 (65);
  - this run's one is seed_9155, with 59 events against 3 in 9197;
  - seed_9054 recorded none and seed_9256 played no runs.

**The fight:**
- `LT_MAP_TRIVIAL_ENCOUNTER` 0 -> 1: seed_9155, above.
- `LT_MAP_TRAVERSAL` 1 -> 0: seed_9054 walked 89 % of its route in 9197 and
  100 % here, with no team wipe.

**The picked candidate changed** (seed_9155 -> seed_9054):
- `DISPATCH_FINDING` 7 -> 10. Two of the new items are the anchor types
  `hatch` and `ladder` (`lot:b0/HATCH_16_12`, `lot:b1/HATCH_2_-10`,
  `lot:ladder_0`), which are in 9197's seed_9054 gameplay too. The third is
  one nav bridge, `deli_counter:A` (-2.0, 14.0) to `lot:MAIN_W` (-2.4, 13.0),
  1.08 m apart. 9194's seed_9054 package carried the same pair, and the
  same `ladder` note.
- `LOT_DESTINATION_RESOLVED` 2 -> 3: bank_branch_a04's objective hook stands
  on a desk, as in 9194, the last run that shipped seed_9054.
- `LUX_CLUB_REFUSED` 1 -> 0 and `ZOO_FIXTURES_MARKERLESS` 1 -> 0: seed_9155's
  strip_club_a01 is no longer the shipped lot.
- `LOT_PATH_END_OFF_DOOR` 6 -> 5: a spur record on b1 or b2. Not attributed
  further.

## Other figures

- **Shell:** 3 candidates, all distinct; 0 blockers of 40 findings.
- **Art:** 0 blockers of 59 findings. The leg exits 1, as 9197's did.
- **The bake:** 415 models and 1,366 primitive meshes lightmapped, 9 kept
  dynamic; 81 steady rigs baked, 21 failing left live; 217 room fills;
  3,645 users, 87.6 s in the editor.

**Instruments here:** `findings_by_code.py` prints the findings whose count
moved, by code, with each item's message.

**Not checked:**
- the van's frame cost (`docs/findings/getaway_van_price/`, after 9199);
- the van in daylight;
- whether `site_audit`'s cover rects, filed in 0.98.1, moved any finding
  here.
