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
