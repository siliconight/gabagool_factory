# The pole line (roadmap 240)

The walker's Philly comps (`docs/reference/PHILLY_STREET_COMPS.md`) put the
overhead network in two of three frames; the factory stood a steel lamp on
both kerbs every 25 m and not one pole. The walker's calls of 2026-10-12
(`docs/proposals/POLE_LINE_DESIGN.md`): one side of every street; the full
wire set without house drops; a transformer can every third or fourth pole; a
cobra-head on every pole.

Built in three steps, each its own release:

1. **Zoo 1.104.0, the pole** (`patches/patch_zoo_utility_pole.py`): a 40 ft
   wood pole, its crossarm and insulators, the cobra-head on a 6 ft arm, a
   `transformer` form; four materials, so four draws a pole (Blender 5.1.1:
   census 3 builds 0 coincident pairs; both forms PASS through the kit path).
2. **Lot 0.118.0, the line** (`patches/patch_lot_pole_line.py`): one kerb of
   every street, poles at the kerb no more than 36 m apart, every pole's light
   at its lens, a can every third or fourth pole by the buildings it serves.
3. **The wires**, between the poles -- next.

## The census (`pole_census.py`, `pole_census.out.txt`)

Each Lot checkout's planner on the four stored site fixtures of cold runs,
their cover dropped first:

    fixture                         0.117.0 lamps   0.118.0 poles / cans   lights      trees   hydrants
    bank_block_001 seed 9256        18              8 / 3                  18 -> 8     16      3
    club_block_014 seed 9080        20              9 / 3                  20 -> 9     21      3
    club_block_014 seed 9181        15              9 / 3                  15 -> 9     18      2
    restaurant_row_001 seed 9205    16              9 / 3                  16 -> 9     14      2

The street lights about halve, as the walker's option said they would (pools
with dark between); whether a street reads too dark is for frames, not this
table. The trees and hydrants did not move on these four. On Lot's kerb probe
they did: its first kerb now takes every corner hydrant the site's spacing
allows, its lamps having refused two of them (four across both kerbs became
three on one) -- the hydrant rule working alone, recorded rather than undone.

## Found on the way (Lot 0.118.0's drafts)

- **A lost station doubles a span.** The first draft stepped a pole only up to
  6 m and lost one inside the probe's 20 m footpath cut: a 75 m gap. A pole
  now also tries a cut's or a shop band's ends (`site_poles._steps`).
- **Along-only spacing is wrong across two lines.** `site_furniture._free`
  compares stations along the road, right for pieces on one line. The
  corner's bin and blade stand on the furniture line 1.9 m across the band
  from the pole line, and read along-only they refused both ends of that cut.
  The pole reads plan boxes instead (`site_poles._room`); a tree keeps its
  crown's spread and a signal 5 m.
- **A band on one kerb moves the whole line.** `pole_kerb` takes the kerb with
  less to dodge, so the band tests put a matching band behind both kerbs.
