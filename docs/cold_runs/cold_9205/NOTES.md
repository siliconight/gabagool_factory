# Cold run 9205 -- 0 interventions; the stage ships live, brighter, and cycling

club_block_014, seed auto, staged from cold run 9204. Tests roadmap 213 as
decided: **Lux 0.69.0** (`CLUB_STAGE_LEVEL` 24, eight times the old level;
a lamp that cycles carries no indirect light) and **Level Factory 0.160.0**
(the light bake leaves a cycling rig live). Level Factory 0.159.0's census
is in this run too; it is a measuring tool and puts nothing in a package.

Tool versions hashed at `--begin`: Lot 0.99.1, Level Factory 0.160.0, Laser
Tag 0.25.0, Zoo 1.85.0, Deli Counter 0.203.0, Lux 0.69.0, Dispatch 0.5.2,
Patina 0.29.1, Pixelcoat 0.61.0, Pipeline 0.6.0.

**`INTERVENTIONS: 0`.** The journal holds no entries, and the run's diff is
empty: no tool file changed, none unattributed. Every leg ran.

**Picked: seed_9181** again, at 0 majors and route completion 0.84. Seed_9080
had 1 major at 0.76 and seed_9282 1 major at 0.92, as in 9204. Lot did not
change between the runs.

## Roadmap 213: what the package carries

Read from each package's `presentation/lux.applied.tscn` and the export
log:

| | cold run 9204 | cold run 9205 |
|---|---|---|
| the bake's rigs | 78 baked, 13 failing left live | 76 baked, 13 failing and 2 cycling left live |
| stage rig resource | `bake_mode = 1` | no `bake_mode`: the default, 0, Realtime |
| main stage lamps | `light_energy` 8.979 | 71.833 |
| VIP stage lamps | `light_energy` 13.393 | 107.140 |
| `light_indirect_energy`, all four | not written: the default, 1 | 0.0 |
| bake time in the editor | 91.6 s | 90.9 s |

- **The two cycling rigs are the two stages.** In 9205's scene, only
  `b0_main_floor_stage` and `b0_vip_wing_stage` carry `cycle_period_s`
  (4.0).
- **The baked count matches.** Exactly 76 rig resources carry
  `bake_mode = 1`, the bake log's count.
- **The energy is exactly eight times.** 71.833 / 8.979 and
  107.140 / 13.393 are both 8.000: level 24 against the old 3.
- **A name now misdescribes its rig.** The resource is still called
  "Stage Light (baked)". The loader names every club rig "(baked)", and
  `lux_lighting.gd` ranks shadows by those names, so the name was left as
  it is.

## The stage in a frame

`tools/look_shots.py` on the walk copy, using 9204's three given stations:
- the main stage from 12 m;
- the main stage close, from 8 m and higher: `stage_9205.png`;
- the VIP stage: `vip_9205.png`.

Manifest: `shots_9205.json`. Figures: `stage_measure.py`, output in
`stage_measure.txt`. The measurements are 8-bit codes at the close station.

| frame | stage top, lum | pole, lum | housings, brightest (left / right) |
|---|---|---|---|
| 9204 as shipped (baked, 1x) | 9.5 | 2.5 | 644 / 549 |
| 9204 hand copy, live 1x | 11.6 | 18.4 | 642 / 551 |
| 9204 hand copy, live 4x | 17.0 | 40.7 | 640 / 547 |
| 9204 hand copy, live 8x | 22.3 | 56.5 | 640 / 547 |
| 9204 hand copy, live 10x | 24.5 | 62.1 | 640 / 551 |
| **9205 as shipped** | **22.2** | **56.5** | **9 / 9** |

**The package reads as the copy the decision was taken from.**
- **On the stage and pole:** within 0.1 codes of the 8x hand copy in every
  channel.
- **Against 9204 as shipped:** the stage top is 2.3 times as bright, and
  the pole 22 times.
- **Every pixel, against the 8x copy** (`tools/shot_diff.py --images`):
  0.07% of the close frame moved by more than 8 codes, and 0.02% of each of
  the other two.
- **No null set was shot for this pair.** These are two exports with two
  bakes, so the figures bound the difference; they do not measure noise.

**The lamp housings went dark, and that is the frozen show going.**

| | brightest pixel, left / right |
|---|---|
| main stage, every 9204 frame | 640-644 / 547-551 |
| main stage, 9205 | 9 / 9 |
| VIP stage, 9204 at 8x | 631 / 535 |
| VIP stage, 9205 | 9 / 22 |

- **The 9204 glow was not live light.** A tenfold change in live energy
  did not move it.
- **It was the lamps' first colours.** Orange on the left, where Stage_0
  starts its cycle (1, 0.55, 0.08), and magenta on the right, where Stage_1
  starts it (1, 0, 0.8).
- **Only three things changed** in the product between the runs: the
  stage's level, a cycling lamp's indirect energy, and the bake skipping a
  cycling rig. So the glow was the 9204 bake's: the show frozen on its
  first frame, which is what 213 set out to remove.
- **Not measured:** which surface held the glow, and whether it arrived as
  direct light or bounce.
- **The decision frames show it; the package does not.** The frames the
  213 decision rests on (`stage_live_x4.png`, `stage_live_x8.png`) carry
  the lit housings. A lens that follows the lamp's colour would bring them
  back as a live look. It is not built and not priced.

**Not settled: whose light 9204's dim wash was.**
- **What the copy kept.** The 8x copy kept 9204's lightmap, which was baked
  with the stage rigs static.
- **What it shows.** On the stage top it reads the same as 9205, which
  baked nothing of them, to 0.1 codes. So whatever that bake held of the
  stage lamps did not reach the stage top measurably.
- **What would settle it.** The stage lip's neon remains the finding's
  candidate for the wash. It was not tested.

## The light census on the package

The root tool, `--count paired`, on the walk copy:
`mesh_light_census_9205_walk.txt`.

- **Nothing over the cap:** 0 meshes over 8 lights paired, worst 6 (b1's
  merged cover), and 3,898 lightmap users. 9204 read the same.
- **Reach is unmoved:** 33 meshes over 8, worst 31. Reach cannot see a bake.
- **The live lamps land where predicted.** Of the 33 rows, 10 changed their
  paired count, all in the club, b0, and none over 5:

| b0 meshes | paired lights, 9204 to 9205 |
|---|---|
| roof footprint, four merged covers | 1 to 5 each |
| main floor ceiling, main floor carpet | 0 to 4 each |
| VIP ceiling, VIP carpet | 1 to 3 each |
| one slab | 0 to 2 |

That is the shape `docs/findings/light_census_pairs/` predicted from the
hand copy: the four stage lamps bind, and no mesh is over the cap.

## Findings

60 to 60, every code at 9204's count. The driver prints a code only when its
count moves, and it printed none. That includes `LOT_RESPONDER_ENTRY_NO_STOP`
2, the van's mirrors in the inbound lane (roadmap 212), still open.

## Other figures

- **Shell:** 3 candidates, all distinct; 0 blockers of 43 findings.
- **Art:** 0 blockers of 60. The art leg exits 1, as 9204's did; the driver
  gates on "blockers open: 0".
- **The bake:** 432 models and 1,528 primitive meshes lightmapped, 7 kept
  dynamic; 172 room fills; 3,898 users; 90.9 s in the editor.
