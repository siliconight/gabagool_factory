# The edge of the plate: a menu (roadmap 219, notes 8 and 12)

**A MOCKUP, NOT PIPELINE OUTPUT.** Every frame here comes from cold run
9219's walk copy of club_block_014 (seed 9181, midnight, Delco Night).
`edge_proto.gd` builds one option at run time, so every option and the
control come from one build. The walker picks a direction; then the owning
tools build it, and nothing here ships.

## What the walker asked for

- **Note 8:** "a diegetic perimeter that keeps the collision and the
  signal".
- **Note 12:** something past the sky's horizon, "to make the level not look
  like it's literally floating in space".
- **Already said, 2026-10-04,** on `docs/findings/backdrop_mock/`: "I like
  the idea of a fence between playable areas and non playable areas, thats
  good feedback to the player".

## The edge as it is

- **Lot's `perim_*`:** four boxes ringing the plate, 3 m tall and 0.3 m
  thick, in 78 lightmapped tiles. They are drawn in `PERIM_COLOR` (0.87,
  0.88, 0.90), which Lot's comment calls "the edge of the world: bright,
  flat, dead".
- **Beyond them, nothing:** the night sky reaches down to the wall's top.
- **In the frames** (`as is`, top left of each sheet):
  - at the east end of the main road, up the side road and across the open
    lot north of the buildings, the wall is a pale moonlit band, the
    brightest thing in the frame;
  - at the west end it is dark;
  - from the main road looking south, the rowhome row hides the wall and
    its roofline already holds the sky. Every option below frames
    identically there, so that sheet is not kept.

## The parts

Each part is a switch in `edge_proto.gd` (`EDGE_OPTION`).

- **`wall_dark`:** the wall's tiles keep their geometry, collision and
  bake. Their material becomes dark concrete block (the level's own
  `skins/concrete_delco_albedo.png` at 0.36, triplanar), under a 16 cm
  concrete cap.
- **`fence`:** the wall's tiles are hidden and its collision is kept. Zoo's
  chain-link (`chain_link_fence`, Zoo 1.77.0; the 14.9 m run the level
  already ships) stands 0.25 m inside the wall.
- **`glow`:** a ring 380 m out: a sodium sky-glow at the horizon over dark
  land, fading out by 140 m up, about 20 degrees.
- **`trees`:** 385 tree crowns and trunks in a belt 2.5 to 38 m beyond the
  edge.
- **`houses`:** 357 rowhome blocks of two to three storeys, in three bands
  4 to 14, 38 to 49 and 80 to 92 m out. 266 windows are lit, one in five,
  and one in five of those is a TV's blue. Street lamps stand between the
  bands.
- **`tower`:** a water tower 90 m beyond the north edge, with a red lamp.

**The glow, refuted twice and kept here.** The first ring showed in no
frame:
- **The fog.** Delco Night's fog (exponential, density 0.006) leaves a
  tenth of anything 380 m out.
- **The wall.** The glow had faded by 4 degrees up. From 26 m away, a
  3.2 m wall already covers the first 3.2 degrees above the horizon.

So the ring now ignores the fog (the glow is the haze) and climbs to 20
degrees.

## The options

| | parts | it reads as |
|---|---|---|
| **A** | `wall_dark`, `glow`, `houses`, `tower` | the borough carrying on behind a block wall |
| **B** | `wall_dark`, `glow`, `trees` | a block wall with woods behind it |
| **C** | `wall_dark`, `glow` | the wall, with a town's glow beyond |
| **D** | `fence`, `glow`, `trees` | a fenced lot at the edge of the woods |
| **E** | `fence`, `glow`, `houses`, `tower` | a fenced lot backing onto houses |
| **F** | `fence`, `glow`, `trees`, houses from 38 m out, `tower` | D, with houses behind the trees |

Sheets, one a station, each laying out all seven frames:
- `menu_north_road1.png`, up the side road;
- `menu_north_lot.png`, across the open lot;
- `menu_east_end.png` and `menu_west_end.png`, down the main road.

## In the frames

- **The dark wall alone (C) removes the brightest thing in the frame.** The
  glow above it says the world goes on. From the open lot, the wall is
  still plainly the edge.
- **Trees (B, D) read at once at night, with the least geometry.** They are
  dark crowns over the glow, and through the fence (D) their trunks show
  too. Of the six, this reads least like a set.
- **Houses (A, E) read as buildings by their lit windows, and only by
  those.** At this fidelity, flat-roofed blocks, the near row seen whole
  through the fence (E) is a dark wall of windows. Seen from the east end,
  A's row was a flat grey slab until the blocks were darkened to 0.06 to
  0.12. They need a real kit: rooflines, cornices, chimneys and porches.
- **F's far houses barely show through the trees.** F is D with a water
  tower, at the houses' price.
- **The water tower** shows over the buildings from the side road and the
  open lot, its red lamp the one cue that reads as a landmark.

## The price

`price_edge.py` ran Level Factory's fixed-station harness
(`perf_stations_run.py`, windowed, this machine) once per option. That is
53 headings at the level's 14 gameplay stations, bracketed by two runs with
nothing built. Each option is set against the two controls' mean, heading by
heading (`price.txt`; the runs' own lines are in `price_runs.log`):

| | draw calls a heading, mean | the worst heading | p95 frame time, median |
|---|---|---|---|
| control 1 | +3.0 | +80 | -0.07 ms |
| **C** | +6.0 | +82 | -0.17 ms |
| **B** | +10.3 | +168 | +0.07 ms |
| **D** | +1.6 | +12 | -0.43 ms |
| **A** | +16.1 | +169 | -0.18 ms |
| **F** | +13.0 | +78 | -0.12 ms |
| control 2 | -3.0 | 0 | +0.07 ms |

- **No option moves frame time by more than the instrument can see.** The
  two controls' own p95 differs by a median 0.65 ms a heading, and every
  option lies inside that.
- **Draw calls rise by a handful a heading,** on a mean of about 1,150.
  - The controls differ by up to 80 at one heading, so the worst-heading
    column is mostly that noise. The mean is the number.
  - D is the cheapest of the rich options: hiding the wall's 78 lightmapped
    tiles pays for the fence that replaces them.
  - A is the dearest: up to 16 house MultiMeshes and the tower's 7 meshes.
- **These stations face into the level,** where the gameplay is, so an
  edge-facing view sees more of the backdrop than they do. The ceiling is
  every object in view at once: A, 25; F, 32 plus its fence; B, 10; D, 9
  plus its fence; C, 2.
- **In a tool, the fence would be one long run a side, 8 draws,** where this
  mockup tiles 42 modules.
- **Not this menu's cost, and worth knowing:** the level's own worst
  heading, `player_start_19` at 90 degrees, is 2,974 draws with nothing
  built. The harness's provisional budget is 2,000.

## What each part would be in the tools

| part | owner | what it is |
|---|---|---|
| dark wall | Lot, with a Pixelcoat pack | `PERIM_COLOR` becomes a concrete-block material, plus a cap; the same draws as now |
| fence | Lot, Zoo | `site_fences` at the plate's edge; Zoo builds one long run a side, 2 draws each, so 8, where this mockup tiles 42 modules |
| glow | Lux | a horizon glow in the time-of-day presets: sodium at night, haze by day |
| trees | Lot, Zoo | a belt planned beyond the plate; a backdrop tree from Zoo, one MultiMesh a side |
| houses | Lot, Zoo | bands beyond the plate; a backdrop rowhome kit from Zoo, one MultiMesh a side and band; the most work |
| tower | Zoo, Lux | a landmark species, and its beacon |

## Recommendation, the walker's call

- **D first: the chain-link fence, the tree belt and the glow.**
  - It reads most like a real place at night, with the least geometry.
  - The walker already liked a fence at the edge of play.
  - It is the cheapest of the rich options in draws, and frame time does
    not move.
- **C as the floor** wherever D does not suit: the dark wall alone removes
  the brightest thing in the frame.
- **Houses (A, E, F) later,** with a real backdrop kit. At this fidelity
  they read as blocks with windows, and behind a tree belt (F) they barely
  show.
- **The glow is in every option.** It can land first and alone: in Lux, per
  time of day.

## Instruments

- **`edge_proto.gd`:** builds the parts at run time from `EDGE_OPTION`.
  Installed in a copy of a walk copy as a node under `mission.tscn`'s root.
  Empty, it builds nothing, so the copy is its own control. A headless run
  prints what it built: `[edge_proto] built <parts> {counts}`.
- **`edge_shots.sh`:** the five stations, given in Godot metres, through
  `tools/look_shots.py`.
- **`sheet.py`:** lays frames out as a captioned sheet.
