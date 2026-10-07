# Night interiors: the light bake lost two things

The walker, 2026-10-07: "i've noticed a lot of our interiors are quite dark
when the sun isn't up ... this can be intentional in dive bars, strip clubs,
and other 'dens of sin' but otherwise we should aim to give the humans enough
light to signify the surroundings".

**Frames and units.** Luminance is Rec.709 on the 8-bit frame, after Lux's
tonemap and post stack, 0-255 (`tools/look_shots.py`). GL Compatibility,
RTX 2060, 1600 x 900. Positions are Godot metres, y up, site frame unless
said otherwise.

## The instrument

`night_interior_census.py <walk copy> <shots dir>`. It takes one station per
room from Deli Counter's `build/<building>.gameplay.json`:
- the eye 1.6 m over the room's floor, 20% along its long axis;
- looking 80% along it at 1.0 m.

Each room is labelled with Deli Counter's own lighting rule (`lights.py`):
- **MOODY:** below grade, or an objective room that is not a public entrance.
  Bare-bulb pendants.
- **ROW:** everything else. A fluorescent row.

It prints mean, median and crushed share a room. It does not judge them.

**The level:** cold run 9190's restaurant row. Its draw is deli_a01, office
and rail_station_a02, 24 rooms; the preset is Blue Hour.

## Measured: baked against live

`before_9190`: the walk copy as shipped, baked. `unbaked_9190`: the same copy
with the entry pointed at the presentation scene, so every steady lamp lights
in real time.

| rooms | baked | live |
|---|---|---|
| 16 ROW | 15.5 | 24.3 |
| 8 MOODY | 3.8 | 17.5 |
| ROW rooms with half the frame under 10 | 14 | 6 |

**The bake was never compared indoors.** `docs/findings/light_bake/` priced
it and compared exterior frames only.

## Cause 1: the probes' ambient floor never reaches a baked surface

Lux 0.38.0 gives every room a ReflectionProbe whose flat ambient (0.04)
replaces the sky's. Its comment calls this "a floor under the fixtures so an
unlit corner is dark grey rather than a hole".

**Raised five-fold (0.04 -> 0.2) on all 24 probes in a baked copy, nothing
moved.** The customer floor went 12.7 -> 13.1; every other room was
identical to 0.1. A lightmapped surface takes its light from the lightmap
alone. The bake is baked with the environment off and two bounces, so a
corner no lamp reaches gets nothing.

The dial was confirmed live before it was called dead. The 0.4 the customer
floor moved is its unbaked props.

## Cause 2: every steady bare bulb sat inside its own glass

**The floor straight under the deli counter's centre bulb**
(`pool_pendant_counter`, eye (-71.3, 1.6, -2.3) -> (-71.5, 0, -2.51)): 0.9
baked against 40.4 live.

A pendant's anchor is the bulb point. Zoo's `pendant_fixture` mounts the bulb
'above' it: an ellipsoid centred one radius over the anchor, stretched 1.15x
upright, so the glass reaches 0.15 of a radius below the anchor (6-12 mm).
Lux hung the lamp at mount 0.0, inside closed glass. The lightmapper
ray-traces, and the lamp lit nothing. That is the defect the street poles had
(`docs/findings/light_bake/`, Lux 0.65.0).

**Re-baked** (`rebake_variant.py`) with Level Factory's own `light_bake.bake`.
The control is a plain re-bake, which reproduced the shipped level: every room
within 0.4, both kinds' means exact. The variant moves the 33 bulb lamps
(32 bare bulbs, 1 counter accent) 0.020 m down.

| | control | bulbs clear |
|---|---|---|
| 8 MOODY rooms | 3.8 | 9.6 |
| cold storage | 0.8 | 15.1 |
| deli counter | 6.6 | 12.4 |
| floor under the bulb | 0.9 | 20.3 (live 40.4) |
| 16 ROW rooms | 15.5 | 15.7 |

All of the ROW movement is the customer floor, 12.8 -> 15.1, whose register
has the counter accent. **Shipped as Lux 0.67.0** (`BULB_LAMP_DROP_M`,
0.022 m, derived).

## How much of a lamp the bake keeps

`fixture_control.py` builds a 20 x 12 m grey floor with nothing else on it,
and two downward spots with Lux's own fluorescent and bare-bulb numbers. It
bakes them with Level Factory's plugin and settings, then shoots
(`fixture_shoot.gd`) the floor under each lamp with the lightmap and without
it.

| lamp | baked | live |
|---|---|---|
| fluorescent, centre | 54.1 | 66.1 |
| bare bulb, centre | 42.9 | 53.6 |

**The bake keeps about 0.8 of a lamp's live luma, about 0.65 in linear
light.** That is with no hardware, no walls, and only the floor to bounce off.

**Refuted, kept:** the first run of this control read 0.00 live and a faint
rim baked, for both lamps alike. `fixture_shoot.gd` placed each camera from
the lamp's `global_position` in `_initialize`, before the tree ran. Godot
answered "!is_inside_tree()" with the identity, so every camera stood at x 0,
between the pools.

**An `editor_only` light does not bake.** The control with one added
(`fixture_control_editor_only.py`) read 0.00 under it both ways. A fill that
exists only in the bake has to be a real light while the bake runs, and gone
before the level ships.

## The floor, put back in the bake

Bake-only omnis per room: present while the lightmapper runs, stripped from
the shipped `bake.tscn`, so they cost nothing at runtime. Untinted probes
only. A tinted probe is a club room, dark by design.

**v1: one fill at the room's centre, a quarter of its height above the middle,
0.08 a room.**

| | bulbs clear | + fill v1 |
|---|---|---|
| 16 ROW rooms | 15.7 | 32.9 |
| ROW rooms, half the frame under 10 | 14 | 4 |
| 8 MOODY rooms | 9.6 | 19.4 |

The exterior barely moves: the overview is unchanged at 74.9 and the
elevations move 0 to +5.6. The west elevation's difference image is all
interior, seen through the section cut.

**Refuted, kept: v1's placement.** In a 3.2 m storey, a quarter of the height
above the middle is 2.3 m, where a bare bulb hangs. The room's centre is where
a row's middle bulb hangs. deli_a01's deli counter fill stood at
(-71.5, 2.3, -2.51), exactly its centre bulb's anchor, inside the glass. The
four deli basement rooms came out unchanged, and the deli counter moved 1.8.

**Four layouts, the same level, the bulbs clear.** Mean luma of 16 ROW and 8
MOODY rooms; the last column is the bake's time in the editor.

| layout | ROW | MOODY | bake |
|---|---|---|---|
| no floor | 15.7 | 9.6 | 85 s |
| v1: 1 fill a room, centre, 2.3 m, 0.08 | 32.9 | 19.4 | 86 s |
| v2: 6 m cells, 1.7 m, 0.08 a room split, each reaching the room | 32.0 | 28.1 | 172 s |
| v3: v2 on 8 m cells, bulb rooms half | 32.0 | 18.7 | 132 s |
| **v4: 6 m cells, 1.7 m, 0.025 each, reach 9 m, bulb rooms half** | **39.1** | **22.8** | **94 s** |
| the level lit live, before the bake | 24.3 | 17.5 | |

- **v2 put the floor back everywhere v1 missed:** the deli counter 14.2 ->
  41.7, the basement corridor 16.4 -> 40.3. It also took the mood out of the
  bulb-lit rooms (28.1 against 32.0). The walker's standing call,
  2026-09-28, is "keep pendants moody".
- **v2 and v3 left big rooms dark.** A floor point is lit by the fills near
  it, so a room's energy split n ways falls as 1/size: the office lobby,
  34 x 12 m, read 10.0.
- **v4 gives each fill a fixed energy and a local reach.** That lights a floor
  the same whatever the room's size: about 1.3x under a fill against the point
  between four. The local reach also cut the bake back to 94 s.
- **A bulb-lit room** is one whose probe box holds a Bare Bulb rig.
  `rebake_variant.py`'s `bulb_points` found exactly the census's eight MOODY
  rooms from the rigs alone.
- **The exterior barely moves** in any layout: the overview is unchanged, and
  the elevations move +0 to +5.6.

**What is left dark is not light.** The office lobby (13.4 with v4) and the
rail concourse (16.5) are the darkest ROW rooms. In the lobby, v4 lifted the
ceiling by 16 codes and the near floor by only 2.4: a dark red carpet.

**Shipped as Lux 0.68.0** (`add_bake_fills`, `LuxPreset.bake_room_fill`
0.025) and **Level Factory 0.151.0** (the bake plugin lays the fill, bakes,
and frees it before the save).

## Refuted, kept: the unowned fill

Lux 0.68.0 left the fill's container unowned, "so even a save that forgot to
free it cannot keep it".

**The first bake through the real plugin baked none of it.** On a copy of
this level with Lux 0.68.0 vendored in, Level Factory 0.151.0's plugin laid
267 fills (`light_bake.json`: `room_fills` 267), and the saved `bake.tscn`
held none. Every room read the control's number: ROW 15.5, MOODY 3.8.

**Why.** Godot's LightmapGI skips any child with no owner when it collects
lights ("maybe a helper"). The experiments had written their fills into the
bake scene's text, so those were owned, and lit.

The 104.6 s that bake took is not evidence either way: Level Factory's suite
was running beside it.

**Lux 0.68.1 owns the fills;** the bake frees them before it saves.

## Dens of sin are buildings, not rooms (Lux 0.68.2)

The walker, the same day: "the 'dens of sin' buildings that we can keep a bit
dark". The fill had skipped only a TINTED probe, a strip club's floor, and
filled the rest of the building.

On club_block_014 at night (Delco Night), re-baked through Level Factory
0.151.0, mean luma of 255:

| room | shipped | 0.68.1 | 0.68.2 |
|---|---|---|---|
| strip_club_a02 main floor | 2.8 | 2.8 | 2.8 |
| strip_club_a02 back rooms | 19.5 | 52.3 | 19.5 |
| strip_club_a02 cellar hall | 1.2 | 8.7 | 1.2 |
| strip_club_a02 count room | 1.0 | 7.0 | 1.0 |
| bank_tower_a02 teller band | 9.7 | 40.0 | 40.0 |
| freight_terminal_a01 cross dock | 1.1 | 11.1 | 11.1 |

A building with any tinted probe now keeps every room unfilled. Which
building a probe is in comes from Lot's ids: `<building>/<id>`, with "/" made
"_" in the probe's name. In `sheet_club_block_014_dens.jpg` the club is back
to its shipped dark, room for room, and the bank and the freight terminal
keep their floor.

## Proven in a level: cold run 9193

0 interventions; findings 64 -> 64; Laser Tag identical to 9192.
- **The fills:** 267 baked, none shipped.
- **The bulbs:** 33 hang at -0.022.
- **16 fluorescent rooms:** 15.5 -> 39.2.
- **8 bulb-lit rooms:** 3.8 -> 23.4.

Against 9190's shipped bake of the same draw
(`docs/cold_runs/cold_9193/NOTES.md`).

## Not established

- **The spawn shot is black (0.8) in every variant**, and no lighting change
  moves it. Its camera stands at (-13.97, 1.6, 4.09), 3 cm inside the office
  lobby's west edge. A frame no light can move says the camera is inside
  something; that is not looked at yet.
- **Other lamps that hang AT their anchor** were not checked for hardware
  around them: a club's neon, back bar and stage lights, a canopy wash, a
  sign. This level has none of them.
- **Daylight presets.** All of the restaurant row is Blue Hour, on one level.
- **Window light at midnight is small here.** Lux ships every window spot at
  3.0 whatever the preset: daylight through a window at midnight. On
  club_block_014 (Delco Night), baking without its 9 window-light nodes
  (`rebake_variant.py nowindows`) moved the banking hall 12.4 -> 12.3, the
  teller band 40.0 -> 39.5, the upper ring 46.7 -> 45.8; every other room
  was identical. A window spot reaches 3-4 m, and these stations look
  across a room's middle. It is a mismatch with the sky, not a cause of
  dark rooms.

## Instruments and outputs

| file | what it is |
|---|---|
| `night_interior_census.py` | one station a room from Deli Counter's gameplay rooms, frames and per-room luma |
| `rebake_variant.py` | re-bake a copy of a walk export with Level Factory's own bake, one variant at a time |
| `fixture_control.py`, `fixture_shoot.gd` | a bare floor and two lamps, baked and shot both ways |
| `fixture_control_editor_only.py` | the same, with an `editor_only` light added |
| `contact_sheet.py` | the four-stage sheet |
| `census_9190.txt` | every room under every variant above, each column's provenance at its head |
| `fixture_control_and_editor_only.json` | the control's frames, cameras over their lamps |
| `fixture_control_REFUTED_cameras_at_x0.json` | the first run, cameras between the pools; kept, not evidence |
| `sheet_9190_four_stages.jpg` | five rooms: the shipped bake, the bulbs fixed, the floor, live |
| `sheet_club_block_014_dens.jpg` | the club level: shipped, the room rule, the building rule |
