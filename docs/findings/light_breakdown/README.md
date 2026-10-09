# What a night frame is made of: the light breakdown (club_block_014, cold run 9213, midnight)

**Question.** The walker, 2026-10-09: "Are you starting to get a better feel
of the lighting in general?", then "build that light breakdown instrument".
A frame at midnight is many sources at once, through the night grade:
- the bake;
- the live lamps;
- the moon;
- the environment's ambient;
- the rooms' probes;
- every glowing surface;
- the sky's own pixels;
- the fog.

Nothing in the repo said which of them a frame was made of. The open case
was cold run 9213: the airport terminal and the funeral home read near-black
around their payphones at midnight
(`docs/cold_runs/cold_9213/payphone_indoor_wall_units.png`). Either those
rooms have no lamps of their own, or they lose them somewhere, and nothing
could tell which.

**Subject.** Cold run 9213's walk copy (`_runs/walk_export_club_block_014`):
club_block_014, seed_9181, Lux's `Delco Night` preset, baked.

**Frame and units.** Rec.709 luma, 0 to 255, of the 8-bit frame after the
night grade and the tonemapper, as `tools/look_shots.py` reports it.
- "Frame" is the whole frame's mean, "centre" the middle third's.
- The drops do not add up to the whole: the grade is not linear. A drop is
  what a frame loses without that one source.

## The instrument

**`tools/light_breakdown.py`,** on look_shots' new `--switch-off`
(`tools/look_shots.gd`, `SWITCHES`). Each configuration is a fresh load of
the level, shot from look_shots' own cameras: the derived ones, `--interiors
4` rooms, and given stations. Each switch uses the level's own mechanism
where it has one:

| switch | what it does |
|---|---|
| `lightmap` | every LightmapGI's `light_data` to null, Lux's own power-cut switch, and every static lamp hidden |
| `live` | every lamp neither static nor directional hidden |
| `sun` | every DirectionalLight3D hidden: in `Delco Night`, the moon |
| `ambient` | each Environment's ambient and reflected light off |
| `probes` | every ReflectionProbe hidden |
| `emission` | the emission multiplier of every lit BaseMaterial3D to 0 |
| `sky` | each Environment's background to black |
| `fog` | each Environment's depth fog off |

**The configurations:**
- `all`, twice, as the control;
- each source alone off;
- `none`, everything off;
- combinations (`--also`);
- with `--fills`, two re-bakes by Level Factory's own `bake()`: the room
  fills on, as the control, and off.

**Every run's manifest says what each switch found.** A switch that finds
nothing reads as "nothing here", never as "no contribution".

**`lamps_near.py`** lists the lamps and probes a level carries near a point,
read off the presentation scene.

## What it measured

**The control:** `all` against `all_control`, frame means identical to 0.00
and centre means to 0.03. The renderer is deterministic, so every difference
below is the switch.

**What each switch found:**
- `lightmap`: 1 lightmap, 81 static lamps (the paired census's 81);
- `live`: 17 lamps;
- `sun`: 1, `LuxSun`, the preset's moon at energy 0.75;
- `ambient`: 1 environment, ambient from the sky at 0.55;
- `probes`: 11;
- `emission`: 97 of 1,221 materials;
- `sky` and `fog`: 1 environment each;
- **`none`: every camera reads 0.8,** the grade's black. The switches reach
  all of the light. The 7 ShaderMaterials no switch reaches show nothing.

| camera | all | -moon | the bake's own light | what is left |
|---|---|---|---|---|
| `elev_S`, a facade | 17.4 | 1.6 | 1.0 | |
| `elev_W`, a facade | 15.3 | 1.6 | 2.0 | |
| `extraction` | 29.2 | 2.7 | 9.4 | |
| `spawn` | 47.4 | 16.5 | 22.1 | |
| `booth_caller`, the street payphone | 45.5 | 37.2 | 33.0 | 5.9 a live lamp |
| `in_drywall`, a lit room | 26.0 | 26.0 | 22.8 | 2.4 the probes |
| `wall_a_room`, the airport terminal | 16.2 | 16.2 | 14.2 | |
| `wall_b_room`, the funeral home | 17.8 | 17.8 | 15.6 | |
| `in_concrete`, a room | 1.7 | 1.7 | 0.8 | |
| `in_concrete_2`, a room | 2.5 | 2.5 | 1.4 | |
| `in_wallpaper_club`, the club | 0.8 | 0.8 | 0.0 | |

"The bake's own light" is `-ambient+probes` less `-lightmap+ambient+probes`.

**RETRACTED, kept: "the bake's light is `all` less `-lightmap`".** The first
table read it that way, and two concrete rooms got BRIGHTER without the bake:
1.7 to 6.8 and 2.5 to 9.8. A lightmapped surface takes no ambient and no
probe light, so clearing the lightmap let both in, in real time. The
combinations isolate the bake.

## What it says

**Outdoors at midnight, the moon carries the level.** Without it the
facades fall from 15-17 to 1.6, and the extraction from 29 to 2.7. The
baked street lamps add 1-2 to a facade and 9-22 near the anchors they stand
by. That is the preset's design, in its own words: "a MOON to shape, and the
practicals -- streetlight sodium, canopy fluorescent, emissive sign faces --
to direct attention".

**The environment's ambient moves nothing while the bake is on:** 0.0 at
every camera.
- A lightmapped surface takes its light from the lightmap alone (Lux 0.68.0
  wrote this down).
- The sky's own pixels give 0.0 too.
- The fog takes up to 0.9 from a frame: it darkens.

**Indoors, the bake is everything.** A lit room's light is the bake: 22.8 of
the drywall room's 26.0.

**A room no lamp reaches is black.**
- The two concrete rooms take 0.8 and 1.4 from the bake.
- Their real-time ambient would have read 6.8 and 9.8. That is what they
  show with the lightmap cleared, when ambient and probes reach them.
- The bake runs with the environment off (Level Factory's
  `environment_mode = 0`). Lux 0.68.0 puts a room's floor back as bake-only
  fills over each untinted room probe. Whether these two rooms get any is
  the fill re-bake's question, below.

**The fills carry the lit rooms.** `--fills` re-baked two copies with Level
Factory's own `bake()`:
- the room fills on: 172 fills, the control, 84 s in the editor;
- the room fills off: 0 fills, 89 s.

**The re-bake is exact.** With the fills on it reproduces the shipped frames
to 0.0 at every camera. So the fills' own light is `rebake_fills_on` less
`rebake_fills_off`:

| camera | all | the fills |
|---|---|---|
| `in_drywall` | 26.0 | 25.2 |
| `wall_a_room`, the airport terminal | 16.2 | 9.7 |
| `wall_b_room`, the funeral home | 17.8 | 11.1 |
| `in_concrete` | 1.7 | 1.0 |
| `in_concrete_2` | 2.5 | 1.7 |
| every outdoor camera | | 0.0 to 1.3 |

- **The drywall room's light is the fills'.** Without them it is black, 0.8.
  Its own lamps light nothing this camera sees
  (`sheets/in_drywall_delco_1997.png`).
- **The concrete rooms take a sliver,** 1.0 and 1.7. They are black with the
  fills too.
- **What a night room reads by is mostly a flat fill,** laid at head height
  with no falloff, and not the lamps a player can see. That is Lux 0.68.0's
  design: the room's floor, put back for the bake. Whether a fill-lit room
  reads as lit by its lamps is a question for the eye.

**The payphone rooms have lamps.** `lamps_near.py` on the walk copy:
- **The airport terminal:** a baked fluorescent 5.9 m from the payphone,
  and pendants at 13 to 14 m.
- **The funeral home:** pendants at 3.9 and 7.5 m, and fluorescents at 6.6,
  8.4 (live) and 10.5 m.
- **Most of what the 3 m view shows is the payphone's own light:** the
  bake's 14 to 16 of the frame, and its centre 50 of 52.

- **The fills give these two rooms 9.7 and 11.1** of their 16.2 and 17.8.
  The rest is the payphone's lamp and the room's own, through the bake,
  plus 0.6 each from the probes and from the glowing surfaces.
- **So "near-black" was not "no lamps".** Both rooms have their own lamps.
  What the 3 m view of the payphone's wall shows is mostly a fill and a
  payphone: the fills give 9.7 of its frame's 16.2, and the bake gives 50 of
  its centre's 52. Where the rooms' own lamps put their light was not shot.

**The club room is black in every configuration,** 0.8, its switches moving
nothing. The dens of sin are kept dark (the walker's rule), and this camera
sees no lit surface.

## Records beside this README

- **Instruments:**
  - `tools/light_breakdown.py` and look_shots' `--switch-off`, at the root;
  - `lamps_near.py` here.
- **The run,** on cold run 9213's walk copy, 2026-10-09:
  - `breakdown.txt` (the tables), `breakdown.json` and `breakdown.log`;
  - the 15 configurations' look_shots manifests in `runs/`. Their PNG paths
    point into `_runs/`, which is not kept.
- **Sheets,** each camera's frames side by side, one per configuration; the
  six the sentences above cite: `in_drywall_delco_1997`,
  `in_concrete_delco_1997`, `wall_a_room`, `booth_caller`, `elev_N` and
  `spawn`.

The command, as run:

    python tools/light_breakdown.py _runs/walk_export_club_block_014 --out _runs/light_breakdown_9213
        --interiors 4 --station booth_caller:33.161,1.697,-2.035,34.561,1.347,-2.035
        --station wall_a_room:-20.70,1.70,3.44,-23.70,1.40,3.44
        --station wall_b_room:79.23,1.70,10.70,79.23,1.40,13.70
        --also ambient+probes --also lightmap+ambient+probes --fills
