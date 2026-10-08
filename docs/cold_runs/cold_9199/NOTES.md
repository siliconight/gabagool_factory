# Cold run 9199 -- 0 interventions; the crew keeps out of the getaway van

bank_block_001, 9198's brief and seeds. Tests **Lot 0.98.1**
(`patches/patch_lot_crew_clear_of_cover.py`): `crew_spawns` keeps the crew's
other members out of every cover piece, grown by `WALL_MARGIN`. In 9198 one
of them stood inside the van on seed_9256, and Laser Tag refused to play that
candidate. Roadmap 206, phase 2.

Tool versions hashed at `--begin`: Lot 0.98.1, then as 9198 -- Laser Tag
0.25.0, Level Factory 0.155.0, Zoo 1.85.0, Deli Counter 0.203.0, Lux 0.68.2,
Dispatch 0.5.2, Patina 0.29.1, Pixelcoat 0.61.0, Pipeline 0.6.0.

**`INTERVENTIONS: 0`.** The journal holds no entries, and the diff has
nothing changed, added, removed or unattributed. Every leg ran.

## The fix holds

**Seed_9256 was played: 25 runs, where 9198 played none.**
`LT_MAP_SPAWN_IN_COLLISION` went 1 -> 0 and `LT_NOT_EVALUATED` 1 -> 0.

The crew stands where the test said it would. Read from the staged
`level.tscn` and turned to site space:

| member | 9198 | 9199 |
|---|---|---|
| `LT_PlayerSpawn` | (18.812, -1.8) | (18.812, -1.8) |
| `LT_PlayerSpawn_1` | (20.812, -1.8), in the van | (18.812, 0.2) |
| `LT_PlayerSpawn_2` | (18.812, 0.2) | (16.812, -1.8) |
| `LT_PlayerSpawn_3` | (16.812, -1.8) | (17.855, -4.110) |

The van's slot is x 20.062 to 22.662. All four members now stand west of the
kerb, on the sidewalk side.

**Picked: seed_9054 again**, at 0 majors and completion 1.00. Seed_9155 had
1 major at completion 0.88, as in 9198. Seed_9256 had 1 major at completion
0.84: its survival FAIL, below.

## Seed_9256's fight corrects 9198's reading

Played with the van for the first time, seed_9256 was the opposite of
trivial:

| | 9197 (two legs) | 9199 (one leg) |
|---|---|---|
| crew deaths in 25 runs | 49 | 41 |
| team wipes, timeouts | 4, 0 | 2, 2 |
| crew survival (median) | 12.0 s | 6.1 s |
| grade | PASS_WITH_TUNING 79 | WARN 60 |

**9198's notes read the one-leg spread as six enemies arriving single file
from one side.** That was true of seed_9054 (1 death) and seed_9155 (0), and
it is not true here.
- **Why it differs here.** The straight line from the van to the vault runs
  through the spawn building, b1, a parking garage spanning x -23 to 13. So
  `place_enemies` pushed the samples it put there out to either side:
  Enemy_0 to 1.0 m past the garage's south wall, Enemy_1 to 1.2 m past its
  north wall.
- **The result is a pincer.** Enemy_0 and Enemy_1 stand 17.7 and 23.4 m from
  the crew, 94 deg apart. The other four stand 44 to 57 m out.

**The better reading, across all three seeds and both runs.** Crew deaths
track enemies arriving together from more than one direction. The one-leg
spread produces that on some sites and not on others.
- It is still a reading, not a proof: no variant was run.
- It does not change what happens next. The walker's answer is responders
  arriving after the job (roadmap 212).
- Lot 0.98.1's comment in `place_enemies` states the single-file account as
  general. The next Lot release corrects it.

## Findings against 9198, 59 -> 63, every item attributed

All six moved codes come from seed_9256 being played. Each matches a line of
its Laser Tag report:
- `LT_MAP_SPAWN_IN_COLLISION` 1 -> 0 and `LT_NOT_EVALUATED` 1 -> 0: the fix.
- `LT_MAP_PLAYER_STUCK` 2 -> 3: 11 stuck events.
- `LT_MAP_ENEMY_STUCK` 1 -> 2: 34 events, 0.23 per enemy per run.
- `LT_MAP_OVEREXPOSED_ZONE` 1 -> 2: 30% of positions visible to 3 or more
  enemy spawns.
- `LT_MAP_INSTANT_CONTACT` 1 -> 2: under fire at 2.4 s.
- `LT_MAP_OVEREXPOSED` 0 -> 1: "players died within seconds of first
  contact".
- `LT_MAP_NO_REACTION_TIME` 0 -> 1: average survival 6.1 s, the FAIL that is
  seed_9256's major.

## Other figures

- **Shell:** 3 candidates, all distinct; 0 blockers of 44 findings.
- **Art:** 0 blockers of 63 findings. The leg exits 1, as 9197's and 9198's
  did.
- **The bake:** 415 models and 1,366 primitive meshes lightmapped, 9 kept
  dynamic; 81 steady rigs baked, 21 failing left live; 217 room fills;
  3,645 users, 86.2 s in the editor. That is 9198's to the model, as the
  same pick should be.

**Not checked:**
- frames: the same lot and the same van as 9198, whose frames went to the
  walker;
- the van's frame cost, priced on 9198's package in
  `docs/findings/getaway_van_price/`.
