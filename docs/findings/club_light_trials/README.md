# The strip club's light: first trials (roadmap 219 note 1, not yet fixed)

**Question.** The walker, 2026-10-09: "strip club is still a tad too dark...
still be dark and moody, but lit enough for a player to see and experience
it". Their comps measured at a median luma of 15 to 39, with 19 to 40% of
each frame under 10 (memory note `walk-feedback-2026-10-09`). Which lever
moves a club room toward that?

**Frame and units.**
- `tools/light_check.py`'s room stations: eye 1.6 m over the floor, 20% along
  the room's long axis, looking 80% along it.
- Luma 0 to 255 after the grade, reported as the frame's mean and its
  median (p50).
- Measured on cold run 9217's walk copy, club_block_014 at night (Delco
  Night), strip_club_a01.

**The instrument.** `den_fill_trial.py` copies the walk project and edits
the copy only. It then re-bakes the copy with `tools/lux_rebake.py`, which
reproduces a shipped bake exactly, and measures it with `light_check`. The
repo's Lux is not touched.

## Results (mean / p50)

| variant | main floor | VIP wing | cash office | objective |
|---|---|---|---|---|
| as shipped | 3.7 / 1 | 2.2 / 0 | 2.6 / 1 | 1.2 / 0 |
| den fill, share 0 (control: 30 fills laid at zero energy) | 3.7 / 1 | 2.2 / 0 | 2.6 / 1 | 1.2 / 0 |
| den fill 0.5, tinted in the room's own colour | 4.6 / 2 | 2.7 / 1 | 6.7 / 3 | 4.7 / 2 |
| den fill 0.5, white | 7.5 / 3 | 4.6 / 1 | 6.7 / 3 | 4.7 / 2 |
| the stored club washes' energy x 3, no fill | 4.9 / 1 | 2.4 / 0 | 2.6 / 1 | 1.3 / 0 |

- **The control laid its 30 den fills** (202 room fills against the shipped
  172) at zero energy, and came back identical: the trial machinery
  reproduces the shipped numbers.
- **A den fill at half share,** the bulb rooms' share, reaches a median of
  3 at most. The tint costs about half of it, since a saturated colour
  carries less luma than white at one energy.
- **Tripling the washes** brightens their pools, and the room stations
  barely see them: main floor mean +1.2, median unchanged.

## A knob that was not the dial (kept)

The first wash trial set the copy's loader constant `CLUB_WASH_LEVEL` to 36
(from 12), and the club came back unchanged to the decimal. Lux computes
each wash's energy when it composes the presentation, and stores it in
`presentation/lux.applied.tscn` (`rig_name = &"Club Wash (baked)"`, for
example `energy = 7.05`, `light_range = 5.52`). A re-bake never reads the
constant. The trial now scales the stored energies, and that is the x 3
row above.

## What it says, and what it does not

- **Neither lever alone comes near a median of 15.** The club is lit in
  pools with black between them, and a room station looks mostly at the
  black.
- **The comps' format** is coloured washes on the walls, backlit shelves,
  glow strips and a floor that reads. That is broader light than either
  lever gives at these settings.
- **Not tried:**
  - a den fill at a full share or more, which risks flattening the mood the
    walker wants kept;
  - washes that light the walls rather than pools on the floor;
  - any frame looked at by eye. These are histograms only.
- **The target itself is open.** `light_check` exempts DEN rooms ("dark by
  design"), and the walker's note asks for a floor: a DEN target such as
  p50 >= 15 with dark corners kept would be the walker's call.

## Second round, 2026-10-10: where the light goes, and walls that carry it

### Where the club's light lands (`light_breakdown`, two stations)

`tools/light_breakdown.py` on the same walk copy, at `club_main`
(eye -72.2, 1.6, 7.0, looking at -51.8, 1.0, 7.0) and `club_vip`
(-74.2, 1.6, -5.0 to -59.8, 1.0, -5.0). See
`breakdown_main_floor_x6.png`, shown at x6 for the eye only.

| main floor, frame mean | value |
|---|---|
| as shipped | 3.7 |
| with the bake off | 1.6 |
| live lights' share | 0.0 |
| emission's share | 0.2 |

- **The bright pools in the frame are on the CEILING,** and they are baked.
  Only switching the lightmap off removes them.
- **They come from the room's two low omnis:**
  - the stage lip's neon, an omni at 1.53 m;
  - the back bar's three omnis, at 1.71 m.
- **The washes are not the cause.** They are downlights at 89 degrees,
  0.25 m under the ceiling, and they light only the floor.
- **The surfaces explain the rest.** Linear albedo, from the package's
  textures:

| surface | albedo |
|---|---|
| `carpet_club` | 0.036 |
| office ceiling tile | 0.545 |
| `carpet_delco` | 0.057 |

  So the pools land on near-black carpet, and anything that throws light up
  makes the ceiling the brightest thing in the room.

### Wall washers and tinted fills (`den_wash_trial.py`)

`den_wash_trial.py` lays, in the copy's loader only, bake-only spot lights
along every wall of each tinted den room:
- every 3 m along the wall, 0.8 m in from it and 0.25 m under the ceiling;
- each aimed at the wall 1.0 m over the floor, a 50-degree cone, range 4 m;
- each in its nearest club wash's colour.

`--fill` adds a den fill: white, or with `--tint` in the room's own colour.

The control (no washers, no fill) reproduced the shipped figures to the
decimal: 3.7/1, 2.2/0, 2.6/1, 1.2/0.

**RETRACTED, kept: the trials' "wall level".** The script solved each
washer's energy with the cosine of incidence taken as the ray's VERTICAL
share (drop / d = 0.93). The wall's normal is horizontal, so the cosine is
inset / d = 0.36. Each trial's energies are exact as printed. The labels
overstated the light on the wall by 2.56x. The table gives the corrected
level: what one washer puts on the wall at its aim point, in units of Lux's
`REFERENCE_POOL` (0.684).

Mean / p50 at light_check's room stations. The last column is the share of
`club_main`'s frame under luma 10.

| washers (energy) | fill | main floor | VIP wing | cash office | objective | club_main < 10 |
|---|---|---|---|---|---|---|
| none | none | 3.7 / 1 | 2.2 / 0 | 2.6 / 1 | 1.2 / 0 | 95.0% |
| 1.56 (17.24) | none | 6.9 / 2 | 7.9 / 2 | 2.7 / 1 | 1.7 / 1 | 88.7% |
| 3.12 (34.47) | none | 9.4 / 3 | 12.6 / 4 | 2.8 / 1 | 2.2 / 1 | 83.2% |
| 1.56 | white 1 | 16.1 / 7 | 14.7 / 5 | 12.4 / 9 | 11.2 / 10 | 52.7% |
| 1.56 | white 2 | 24.9 / 11 | 21.3 / 8 | 23.1 / 20 | 21.4 / 22 | 48.2% |
| none | white 2 | 21.5 / 8 | 14.4 / 3 | 22.9 / 20 | 20.7 / 21 | 52.6% |
| 1.56 | tinted 2 | 13.2 / 7 | 10.5 / 5 | 23.0 / 20 | 21.2 / 21 | 53.1% |
| 2.34 (25.85) | tinted 2 | 14.5 / 8 | 13.0 / 7 | 23.1 / 20 | 21.5 / 22 | 51.3% |
| 2.34 | tinted 4 | 21.3 / 10 | 15.2 / 9 | 41.3 / 40 | 38.5 / 42 | 48.7% |

The trials' fill used one share for every den room. So the cash office and
the objective, both untinted, were filled white at that share.

**By eye.** See `tinted_against_white.png` and `shipped_fill2_fill4.png`.
- **Washers alone** give the comps' format: coloured scallops on every wall,
  the stage and the bar readable. But the floor stays black.
- **A white fill** reads the floor and the furniture. But it turns the
  office tile overhead into a grey grid, and the club reads as a hall.
- **A tinted fill** reads them as well, and the ceiling carries the room's
  colour instead: amber over the main floor, pink over the VIP wing. That
  is the one that keeps the mood.

**Chosen for Lux 0.72.0: washers 2.34 and a tinted fill at 2.** The den's
untinted back rooms take the bulb rooms' white 0.5, not the club floor's
share.
- At a full share, 0.68.0 made strip_club_a02's back rooms the brightest
  room in a level (52.3), and the walker kept dens dark after it.
- The fill at 4 is the brighter option, and it is the walker's call.

### The release's own loader, baked (`loader_trial.py`)

Lux 0.72.0's loader, vendored into a copy of the walk project and baked by
Level Factory's own bake. Mean / p50 at the room stations:

| room | 0.71.0 | 0.72.0 |
|---|---|---|
| main floor | 3.7 / 1 | 14.5 / 8 |
| VIP wing | 2.2 / 0 | 13.0 / 7 |
| cash office | 2.6 / 1 | 6.9 / 3 |
| objective | 1.2 / 0 | 5.7 / 3 |

- **The club floor matches its trial row to the decimal,** so the code is
  the trial.
- **The back rooms take the bulb rooms' white 0.5,** a little over the
  first round's 6.7 / 3 and 4.7 / 2, from the washers' spill.
- **The club stations' share under 10:** `club_main` 51.3%, `club_vip`
  60.4%, `club_bar` 50.4%.
- **The bake took 83.5 s,** against the shipped 82.3. It laid 256 room
  fills: the shipped 172, the den's 30 and 54 washers. Nothing of them
  ships.

### What is left, and whose it is

- **The ceiling is the office tile.** Deli Counter's `dress_club_rooms`
  sets a club's floor, partitions and outside walls, never its ceiling. So
  a club room takes its role's default, `ceiling_tile`. A dark club ceiling
  would let a fill read the floor without lighting a grid overhead.
- **The carpet is near-black** (0.036). It is Pixelcoat's `carpet_club`, and
  the walker has not judged it.
- **The washers have no hardware.** The scallops come from no visible
  fixture.
- **Still under the comps:** a median of 8 against their 15 to 39, with
  about half of each club frame under 10 against their 19 to 40%.
