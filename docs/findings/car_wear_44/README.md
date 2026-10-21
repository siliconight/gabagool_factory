# The parked cars' wear: sun, salt, the road, a repair and a sticker (roadmap 44)

**What it was for.** The walker's look review of 2026-10-19, on the parked cars: "Looks right", and "some of the cars
need some patina and wear...rusting....ect....bumper stickers....more lift". Roadmap 44's next step: wear per car as
seeded variation on the shared species, never a material per colour.

**What changed.**
- **Zoo 1.120.0** (0c51827; `patches/patch_zoo_car_wear.py`, `patches/zoo_car_wear/`): `core/car_wear.py` draws each car
  a history from its own stream -- kept, driven, beater -- so no car's style, paint or trim moves. The sun and the
  road ride the body's `Wear`. Rust over the arches and along a rocker, a primer patch on the kerb side's front door
  and a beater's lost clear coat are thin pieces of the car's one painted material. Bumper stickers come from one
  shared sheet (`core/car_stickers.py`, `sticker_sheet.png` here: twelve invented Delco stickers, a denylist test over
  every line). The cruiser never weathers; its GLB is 1.119.0's, byte for byte.
- **Zoo 1.120.1** (2ed0d79; `patches/patch_zoo_sticker_share.py`, `patches/zoo_sticker_share/`): stickers on about
  three cars in eight, drawn last so nothing else a car drew moves.

**REFUTED, kept.**
- *The sun as the van's bleach.* The first cut chalked every face that looks at the sky toward
  `van_forms.SUN_BLEACH`, a pale grey against the van's near-black and DARKER than a silver or a white car: the first
  silver beater's roof went grey, and its peel patches read darker than the paint around them. The sun now lifts a
  paint toward a pale, dull version of itself (`car_wear.chalk`).
- *The first look's pieces.* The rust lip was a near-black brown that read as the arch's own shadow; the primer was grey
  on a silver car and barely showed; the peel was 8-point rings in a column down the roof, every centre drawn from
  smooth noise, which crowds toward 0.5. Each is in `car_wear`'s comments with what replaced it.
- *Stickers on most cars.* 1.120.0 drew a kept car none or one and a driven car none to two; cold run 9365's street put
  them on 27 of its 35 cars, where the walker asked for "some". 1.120.1: seven.

## One level, three Zoos

Cold runs 9364, 9365 and 9366 made the same level -- bank_block_001 at seed 9082, the same brief and batch -- with
Zoo 1.119.0, 1.120.0 and 1.120.1, every other tool the same: 0 interventions each, findings 110 -> 110 -> 110. Its 35
parked cars are eight modules in the same bays (`car_surfaces.py`, `car_surfaces_9364_9365_9366.out.txt`):

| run | Zoo | cars with stickers | the cars' surfaces, every car in view |
|---|---|---|---|
| 9364 | 1.119.0 | 0 | 140 |
| 9365 | 1.120.0 | 27 | 167 |
| 9366 | 1.120.1 | 7 | 147 |

Every surface more is the sticker material: the rust, the primer and the peel pack into each car's painted mesh. The
export's light bake agrees -- 2,213, 2,240 and 2,220 users.

## What it costs: priced

`_runs/perf_inner/run.py`, Level Factory's fixed-station harness, GL Compatibility, windowed: 9364's package twice (the
control) and 9366's once, in one session, nothing else running -- 14 stations, 53 headings
(`price_9364_a.json`, `price_9364_a2.json`, `price_9366_b.json`; `price_headings.py`, `price_headings.out.txt`):

- **The instrument sees the change.** Draws differ between 9364 and 9366 at 20 of the 53 headings, by +1 to +3 (the
  stickered cars in view); the control's two runs differ at none. Mesh instances 2,274 -> 2,281.
- **Frame time does not move.** Where draws moved, 9366's median frame is +0.015 ms over the mean of 9364's two; where
  they did not, +0.014 ms; the control's own spread is -0.040 to +0.076 ms. The stations' mean p95: 2.926 and 2.930 ms
  for 9364, 2.921 for 9366.
- **Texture memory +155,824 bytes**: one sticker sheet, compressed with its mips -- every car references the same file.

So the stickers cost a draw a stickered car in view and nothing a frame can show at this level's seven; the rest of
the history costs triangles only (a beater 92 to 136 more, the car's budget 3,400 -> 3,500).

## Frames

`shots.sh` frames five stations in the site's own frame -- behind the silver beater (`cover_133`), along its kerb
side, over its roof, behind a tan SUV (`cover_2`), and down the parking lane -- in each run's walk copy;
`compose_columns.py` puts the three runs side by side.

- `cars_9364_9365_9366_inspect.jpg`, the inspection light: the clean silver sedan becomes the beater -- stickers on its
  rear bumper, rust blooming round both kerb-side arches and the driver's rear one, a red-oxide primer patch on the
  front door, three milky patches of lost clear coat on the roof. Behind the SUV, 1.120.0 had stuck a sticker on the
  white sedan beside it as well; 1.120.1 leaves that one clean.
- `cars_9364_9365_9366_lit.jpg`, the level's own light: a heavy-rain afternoon so dark the cars are near-silhouettes
  and only the roof's patches faintly read. The wear will show in a brighter level; in this one, the light hides it.

## The walker's calls

- **The look**, from the frames.
- **"more lift"** -- a lifted ride height (a jacked-up pickup or SUV), or "more life"? Not built.
- **The primer patch reads as a clean oval.** A sanded, feathered panel would read as a repair; an oval reads as a
  decal.
- **How many stickers, and their copy** (`sticker_sheet.png`).

## Files

- `shots.sh`, `compose_columns.py`: the frames; `cars_9364_9365_9366_inspect.jpg`, `cars_9364_9365_9366_lit.jpg`.
- `car_surfaces.py`, `car_surfaces_9364_9365_9366.out.txt`: the cars' surfaces in each package.
- `price_headings.py`, `price_headings.out.txt`, `price_9364_a.json`, `price_9364_a2.json`, `price_9366_b.json`: the
  price.
- `sticker_sheet.png`: the sheet as this suite's Python paints it. The shipped one is Blender's
  (`cover/_tex/Car_stickers_7010d0fd_7010d0fd.png` in 9366's package): the same sheet to within one level of 255 in
  any pixel, measured -- the two numpy builds round differently -- so its bytes and its name's hash differ.
