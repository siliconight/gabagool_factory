# Cold run 9204 -- 0 interventions; every club rig built, the stages not shown lit

club_block_014, seed auto, from cold run 9167's brief -- the last run on this
mission, and one that carried `LUX_CLUB_REFUSED`. Tool paths came from 9203,
because 9167's workspace no longer exists. Tests **Lot 0.99.1** (roadmap 207,
`patches/patch_lot_light_targets.py`): a stage light's `target` is carried
into site space with its `pos`, where it had been copied in the building's
frame.

Tool versions hashed at `--begin`: Lot 0.99.1, Level Factory 0.158.0, Laser
Tag 0.25.0, Zoo 1.85.0, Deli Counter 0.203.0, Lux 0.68.2, Dispatch 0.5.2,
Patina 0.29.1, Pixelcoat 0.61.0, Pipeline 0.6.0.

**`INTERVENTIONS: 0`.** The journal holds no entries; 0 files are
unattributed. Every leg ran.
- **Three tool files did change:** `deli_counter/specs/lf_club_block_014_*.json`,
  one per candidate.
- **Level Factory writes those every run**, and the run's diff attributes
  them so ("Level Factory writes one DC spec per candidate, per run"). No
  repo shows them dirty.

**Picked: seed_9181**, at 0 majors and route completion 0.84. Seed_9080 had 1
major at 0.76, and seed_9282 1 major at 0.92.

## Roadmap 207: the refusal is gone

| | cold run 9197 | cold run 9204 |
|---|---|---|
| Lux's club log | 42 of 44 club rigs | "Baked 44 club rig(s) from 44 club anchor(s)" |
| `LUX_CLUB_REFUSED` | 1 | 0 |
| main stage throw | 73.03 m | 4.28 m |
| VIP stage throw | 74.03 m | 5.23 m |

- **The stages aim where the building says.** b0's stage lights aim at
  (-62, -7, 1.68) and (-67, 5, 1.68), in both the candidate's
  `site.site.lights.json` and the themed site's.
- **The hardware matches.** Lux's hardware check: 13 club lights of a type
  Zoo builds hardware for, 0 with none within 0.05 m.

## The stages in a frame -- not shown, and the attempt retracted

**What was shot.** `tools/look_shots.py` on the walk copy, three given
stations: the main stage from 12 m, from 8 m and higher, and the VIP stage.
- **What they show:** a dark club -- posters, the lit back bar, a round
  stage with a red rim.
- **What they don't show:** a visible pool of light on either stage.
- **Luminance:** means of 1.1 to 3.4 out of 255.

**RETRACTED, kept above what replaced it.** The four stage spots'
`light_energy` was then zeroed in a copy, and separately their `spot_range`
was raised to 16 m. Neither moved a pixel beyond the control:

| comparison | max delta: main | close | VIP |
|---|---|---|---|
| on against on (the control) | 17 | 25 | 237 |
| on against off | 16 | 26 | 237 |
| on against range 16 m | 16 | 25 | 236 |

That was read first as "the stage spotlights make no measurable
difference", and then as "the range is the limit". Both readings are void,
for two reasons:
- **The edits never ran.** `lux_stage_light_rig.gd`'s `_rebuild()` frees
  every saved `Light3D` child at load and makes the lamps again from the
  rig's resource, so the edited values were thrown away.
- **The light is baked.** The rig's resource reads `bake_mode = 1`, "Stage
  Light (baked)". Its light is in the lightmap, which no scene edit reaches.

A null result from a dial that was not the dial refutes nothing.

**What would answer it:** an export with the stage rigs removed before the
bake, compared with this one at the same stations, or a station inside a
stage's own cone.

## Found on the way: the bake freezes the stage show (roadmap 213)

**Why it happens.**
- **The bake's rule.** Level Factory's light bake marks every Lux rig whose
  resource carries no `failing_kind` as baked.
- **What a baked rig does.** It stops cycling: `_cycles()` returns false for
  `bake_mode == 1`.
- **The stage rig cycles but is not failing.** It carries
  `cycle_period_s = 4.0` and seven colours, and it is not a failing fixture.

So every club package ships its stage show frozen on one colour. This is the
first package whose stage rigs exist at all. Live or baked is the walker's
call: four dynamic spot lights in a club, priced, or a frozen show, said.

## Findings

This is the first run of club_block_014 since 9167, and 9167's workspace is
gone. So the driver's diff reads "0 -> 60": every code counted as new.
Nothing here is compared code by code with 9167. 207's code is the one that
matters, and it is absent.

Also present, all known shapes, none attributed further here:
- `LOT_RESPONDER_ENTRY_NO_STOP` 2. Lot 0.99.0's arrivals: two road ends on
  this mission found no stop.
- `ZOO_FIXTURES_MARKERLESS` 1, info: 13 of 18 club fixtures are hardware
  with no emitter marker by design.
- `LUX_NO_ROOM_PROBES` 1.
- `PRESENTATION_ZFIGHT` 1.

## Other figures

- **Shell:** 3 candidates, all distinct; 0 blockers of 43 findings.
  **Art:** 0 blockers of 60.
- **The bake:** 432 models and 1,528 primitive meshes lightmapped, 7 kept
  dynamic; 78 steady rigs baked, 13 failing left live; 172 room fills;
  3,898 users, 91.6 s in the editor.
