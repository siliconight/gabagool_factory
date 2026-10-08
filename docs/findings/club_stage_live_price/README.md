# The club's stage lights: as shipped, live, and what live costs (roadmaps 207, 213)

**Question.** Lot 0.99.1 let Lux build a strip club's stage lights (roadmap
207). Do they light the stage in a frame? The light bake bakes them, which
freezes their colour cycle (roadmap 213). What would keeping them live cost?

**Subject.** Cold run 9204's club_block_014, seed_9181. The club is b0, and
its stages sit at site (-62, -7) and (-67, 5) -- Godot (-62, 7) and
(-67, -5). Each stage rig is two unshadowed SpotLight3D lamps, read from the
package's `presentation/lux.applied.tscn`:

| rig | throw | energy | range | cone |
|---|---|---|---|---|
| `b0_main_floor_stage` | 4.28 m | 8.98 | 5.35 m | 19.3 degrees |
| `b0_vip_wing_stage` | 5.23 m | 13.39 | 6.53 m | 16.0 degrees |

- **Energy** is Lux's solve for the throw.
- **Both rigs cycle** seven colours every 4 s.
- **Both resources shipped** `bake_mode = 1`, "Stage Light (baked)".

## The stage in a frame

`tools/look_shots.py`, GL Compatibility, RTX 2060, 1600x900. Station
`main_stage_close`: eye (-55.5, 2.4, 7.0), target (-63.5, 0.6, 7.0), Godot
frame.

| `stage_as_shipped.png` | `stage_live_x1.png` | `stage_live_x10.png` |
|---|---|---|
| the package as built: the stage rigs baked | the stage rigs live at Lux's energy | live at ten times Lux's energy |
| a dim red-brown wash on the stage top; the pole barely shows | the same wash a little brighter, and the pole lit | a magenta pool on the stage and a lit pole |

**Against the control:** the share of pixels whose largest channel moved more
than 8 codes, then the largest move (`tools/shot_diff.py --images`).

| comparison | main stage, 12 m | close | VIP stage |
|---|---|---|---|
| on against on, a second launch | 0.00%, 17 | 0.00%, 25 | 0.00%, 237 |
| live at Lux's energy against on | 0.05%, 65 | 0.46%, 221 | 0.09%, 238 |
| live at ten times against on | 0.18%, 204 | 1.06%, 255 | 0.19%, 255 |

**THE DIAL IS THE RESOURCE.** `lux_stage_light_rig.gd`'s `_rebuild()` frees
every saved lamp at load and makes it again from the rig's resource.
- **The void attempt.** An earlier on/off edited the saved lamps. It changed
  nothing, because the edits never ran, so it is void. It is recorded in
  `docs/cold_runs/cold_9204/NOTES.md` as retracted.
- **What this comparison edits.** `make_live_copy.py` edits the resource:
  `bake_mode = 1` to 0 on both stage rigs, and with `--energy-scale` their
  energy.
- **It reproduces the hand-made copy.** Run on the raw package, it
  reproduces the price's hand-made live copy byte for byte.

**What the frames say, and what they do not.**
- **They say:** the beams land on the stage and the pole, where a stage
  light should, at Lux's own energy too.
- **They say:** at Lux's energy the stage does not read lit, baked or live.
  Live adds a lit pole and a slightly brighter pool; it does not add a show.
- **They do not say:** what energy is right. Ten times is a dial turned far
  to see whether the light lands anywhere, not a proposal.
- **They do not say whose light the wash is.** It could be the stage lamps,
  baked. It could be the stage lip's neon, also baked, orange like the main
  stage's first colour, and reaching 2.5 m. Nothing here separates the two;
  a bake without the stage rigs would.
- **They do not show live alone.** The live copies keep the package's
  lightmap, which was baked with the stage rigs in it. So a live frame is
  the baked light plus the live lamps. A live stage shipped for real would
  be baked without them, and would lose whatever part of the wash is
  theirs.
- **Each live frame catches one colour.** The cycle is 4 s per colour, and
  a frame is one instant of it.

## How bright: the level the stage ships at

The walker, 2026-10-08: "Stage can be brighter, im ok with live or baked,
whatever you think is the best". Live frames of the same station at more
multiples of Lux's level (`CLUB_STAGE_LEVEL` 3), each against the shipped
package (`shot_diff --images`):

| frame | stage level | close: pixels moved, largest | pixels clipped |
|---|---|---|---|
| `stage_live_x1.png` | 3 | 0.46%, 221 | +0.00% |
| `stage_live_x4.png` | 12 | 0.75%, 255 | +0.00% |
| `stage_live_x8.png` | 24 | 0.96%, 255 | +0.00% |
| `stage_live_x10.png` | 30 | 1.06%, 255 | +0.00% |

- **4x** is lit, but at the room's own wash level (`CLUB_WASH_LEVEL` 12)
  it is no brighter than the room.
- **8x** is the brightest thing in the room, with the pole lit and nothing
  clipped. `vip_live_x8.png` is the VIP stage at the same level.
- **10x** hardly differs from 8x: the tonemapper's shoulder.
- **So Lux 0.69.0 lights the stage at 24,** twice the wash, chosen against
  these frames rather than derived. Level Factory 0.160.0 keeps the
  cycling rig live through the bake.
- **These frames keep the old bake's wash under the stage.** A live stage
  baked without its lamps will read a little darker on its top. The cold
  run that follows shows the real one.
  - *Refuted by that cold run* (9205, `docs/cold_runs/cold_9205/NOTES.md`).
    Baked without its lamps, the stage top reads 22.2 (luminance, 8-bit
    codes) against this 8x copy's 22.3, and the pole 56.5 against 56.5:
    not measurably darker.
  - **What did change is above the stage.** The two lamp housings are lit
    in every frame here, brightest pixel 640-644 and 547-551 whatever the
    live energy, in the colours the lamps start their cycle with. In 9205
    they read 9. That light was the old bake's: the show frozen on its
    first colours.

## What live costs

**In one line:** no draw calls, and 0.11 to 0.17 ms at a view facing a
stage, about 5% of those 3 ms frames. Elsewhere in the club it is less, and
beyond 50 m of a stage it does not measure.

**How it was priced.** `_runs/perf_inner/run.py` makes a fresh copy of a
package, imports it headless, and runs Level Factory's fixed-station harness
(`level_factory/tools/perf_stations_run.py`).
- **The stations:** 12 from the package's anchors, plus the highest vantage
  and the longest sightline. That is 53 station headings, each measured in
  two passes with the lower p95 kept.
- **The setup:** GL Compatibility, RTX 2060, 1280x720.
- **The four runs, in order:** `club_on` (the package as shipped),
  `club_live` (the stage rigs live at Lux's energy), `club_on2` (the shipped
  package again, the control) and `club_live2` (the live copy again).

**Draw calls: no change.** Live against shipped is 0 at every heading:
unshadowed lamps add no pass.
- **One exception, and it is not the stage.** `club_live2` shows -160 at
  `attacker_spawn_8`, yaw 0.
- **Why.** That heading draws 871 in one pass and 711 in the other in all
  four runs, the two controls included. The harness keeps whichever pass
  has the lower p95, and in `club_live2` that was the 711 pass.

**Level-wide: nothing measurable.** From `price_robust.txt`, against the
mean of the two controls:

| | the median frame moved | mean | range |
|---|---|---|---|
| `club_live` | +0.014 ms | +0.025 | -0.075 to +0.171 |
| `club_live2` | +0.001 ms | +0.004 | -0.120 to +0.160 |
| the controls, one against the other | +0.021 ms | +0.039 | -0.110 to +0.293 |

No heading was unstable between the controls (more than 1.0 ms apart).

**Where the stage is: a small cost that lives there.** From
`stage_headings.txt` (`club_live`) and `stage_headings_live2.txt`
(`club_live2`).

The two headings that face a stage, on frames of 2.7 and 3.1 ms:

| heading | what is ahead | `club_live` | `club_live2` | the controls' own difference |
|---|---|---|---|---|
| `patrol_point_18`, yaw 0 | the main stage, 5.9 m | +0.143 ms | +0.160 ms | -0.027 |
| `defender_spawn_15`, yaw 270 | the VIP stage, 5.1 m | +0.170 ms | +0.113 ms | +0.032 |

By each station's distance from the nearer stage:

| | `club_live`: mean, median | `club_live2`: mean, median |
|---|---|---|
| the 24 headings within 17 m | +0.047, +0.038 ms | +0.022, +0.013 ms |
| the 29 beyond 50 m | +0.006, +0.011 ms | -0.011, -0.007 ms |

*As first written:* "8 of the 9 largest differences are at stations within
17 m of a stage". It is retracted: ninth place is a tie at 0.075 ms between
a near heading and a far one, so the count reads 8 ranked by sign and 7
ranked by size.

**The light census cannot price this.** It reads the same in every run: 33
of 3,954 meshes over the cap of 8, worst 31. It counts every positional
light by its reach, baked or live (`perf_stations.gd`, `_light_census`), so
a change of bake mode cannot move it.
- **Not measured:** whether the four live lamps put any stage mesh over 8
  lights the renderer actually pairs with it.

## Records beside this README

- **The frames:** `stage_as_shipped.png`, `stage_live_x1.png`,
  `stage_live_x4.png`, `stage_live_x8.png`, `stage_live_x10.png` and
  `vip_live_x8.png`.
- **The shots:** `shots_on.json`, `shots_on2.json`, `shots_live_x1.json`,
  `shots_live_x4.json`, `shots_live_x8.json` and `shots_live_x10.json`, the
  `look_shots` manifests the frame deltas came from.
  - The deltas were read with `python tools/shot_diff.py <a> <b> --images`
    while every PNG existed.
  - Only the PNGs above were kept, so on these manifests `shot_diff` still
    compares the statistics but no longer the pixels.
- **The live copies:** `make_live_copy.py`.
- **The price:** `club_on.json`, `club_live.json`, `club_on2.json` and
  `club_live2.json`, with their logs.
  - `price_robust.txt` is `patches/zoo_cover_merge/price_robust.py` on them.
  - `stage_headings.txt` and `stage_headings_live2.txt` are
    `stage_headings.py` on them, one live run each.
  - The package copies the price ran on were deleted once their reports
    existed.
