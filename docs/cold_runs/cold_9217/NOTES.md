# Cold run 9217 -- 0 interventions, 0 retries; roadmap 219's six fixes together on the walked level

club_block_014, seed 9181 at night: the level the walker walked on
2026-10-09 (cold run 9213), staged from 9213's batch and brief. It proves six
of their twelve notes together:

| note | fix |
|---|---|
| 6, the news racks | Lot 0.102.1 |
| 4, the meters | Lot 0.102.2 |
| 3, the antennas | Deli Counter 0.204.1 |
| 10, the sign fonts | Zoo 1.90.0 |
| 9, the signals | Level Factory 0.165.0 |
| 2, the den windows | Zoo 1.91.0 and Deli Counter 0.205.0 |

Tool versions hashed at `--begin` (`_runs/cold/cold_9217/before.json`):
Deli Counter 0.205.0, Dispatch 0.5.2, Laser Tag 0.25.0, Level Factory
0.165.0, Lot 0.102.2, Lux 0.71.0, Patina 0.29.1, Pipeline 0.6.0, Pixelcoat
0.61.0, Zoo 1.91.0.

**`INTERVENTIONS: 0`** (journal 0, unattributed files 0), **retries 0.**

**Picked: seed_9181,** given to the driver as 9213 picked it. It carries
strip_club_a01, funeral_home_a03, airport_terminal_a02 and the 12 empty
rowhomes. All three candidates were distinct.

## What each fix shows here

Frames are `tools/look_shots.py` on the walk copy at midnight, at given
stations (`--station`, Godot metres). strip_club_a01 stands at (-62, 0, 2),
unturned.

- **The sign, note 10** (`club_sign_street.png`, eye (-67, 1.7, 23)): MOM
  THINKS I'M AT BINGO in Blue Highway Condensed, lit, outlined, one line,
  over the club's door. The same frame shows the meters.
- **The meters, note 4:** each meter's face looks across the kerb at the
  camera.
- **The signal, note 9** (`signal_close.png`, eye (27.0, 2.0, 18.4)):
  - both heads show green alone, with red and amber dark;
  - the import log, `LF_club_block_014.portable-godot.import.log`, reads
    `[worldskin] prop_traffic_signal_delco_1997_01_w800_d62_h650.glb  3
    signal lens surface(s) given the junction's clock` on both import
    passes;
  - the pole, `cover_89`, is at (34.45, 3.35, 15.75), its heads facing -X.
- **The drape, note 2:** strip_club_a01's `site.tscn` places
  `window_drape_s0_1` (`prop_window_drape_delco_1997_14_w150_d16_h155.glb`)
  at local (12.0, 2.475, 11.74), turned 180. The club's lights carry no
  `window` anchor.
  - **Not seen in a frame.** From inside, the club at midnight is nearly black
    (`club_drape_inside`: mean 2.1, p50 0): that is note 1, still open.
  - **From the street,** the window falls in a tree's shadow: black even
    brightened threefold.
  - At night a drawn drape in a dark room and clear glass onto one look
    alike. The piece's own frames are `docs/findings/den_drapes/`.
- **The news racks, note 6:** measured on the site's slots
  (`club_block_014.lot_assemble.candidate.seed_9181/1/out/site.slots.json`,
  spec frame, Z up). The plan gaps between boxes:

  | rack | nearest piece | gap |
  |---|---|---|
  | `cover_97` | the mailbox | 0.89 m |
  | `cover_98` | the payphone | 0.715 m |

  The bus shelter is 5.79 and 6.89 m off. In 9213 one rack stood 0.11 m
  from the flag post and another over the shelter's end.
  - *First measured in the wrong frame, kept:* the check read the
    translation as (x, up, depth). That put every piece on a line of
    heights, and all ten pairs it found overlapped. The file says "spec/
    Blender Z-up raw coords"; asked in that frame, none overlap.
- **The antennas, note 3:** the level places 26 rowhomes, two or three of
  each archetype (`presentation/lux.applied.tscn`).
  - The dressed archetypes, a and g with an antenna and k with the dish,
    stand twice each.
  - So 6 of the 26 roofs carry a fixture, where 0.204.0's dressing put one
    on 19.

## Found here, and older than any of this: a bar on the door sign

`sign_bar_9213_9217.png`. A thin, light vertical bar crosses the door sign at
its centre, from about mid-text to the bottom rule:
- **In 9217,** over Zoo 1.90.0's lettering;
- **in 9213,** over 1.89.0's pixel lettering, in the same place.

So no release in this run made it. What it is not:
- **Not the texture.** The package's `SignBox_Face_608x216_2573fba6_
  4af3fd0b.png` is clean.
- **Not a thing standing off the face.** Shot head-on and from 1.8 m to the
  side, it keeps its place between the letters, as a thing on the face's
  plane would.
- **Not Lux's emissive preview quad.** Both of Lux's paths turn it off
  (`lux_fixture_spawner.gd` 106, `lux_light_loader.gd` 1396).

The cause is not established. It is on the one door sign framed in each
run, and it is filed for its own block.

## What held

- **The shell leg:** 0 blockers of 51 findings. **The art leg:** 0 blockers
  of 71.
- **The export:**
  - 433 models and 1,528 primitive meshes lightmapped;
  - 7 kept dynamic, and 1 spawned set dynamic;
  - 78 steady rigs baked, 13 failing and 2 cycling left live;
  - 172 room fills, 3,890 users, 91.6 s in the editor.
- **Findings: 72 to 71 against 9213.** `LT_MAP_PLAYER_STUCK` went from 3 to
  2, and nothing else moved.
