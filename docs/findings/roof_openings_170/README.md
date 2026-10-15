# Roof openings, roadmap 170: the split, measured

Roadmap 170 (the walker, 2026-09-23: "a building does not have an open hole in its roof") measured 58
`roof_access` ladders cutting the slab they arrive through and 74 `hatch` links doing the same, with no lid in
any tool. It also proposed the better answer for most of them -- a BULKHEAD, the little house a stair runs up
into, which turns a hole in a horizontal slab into a doorway in a vertical wall that Deli Counter already
builds -- and said the first thing to do was to split the population between a bulkhead (where a stair reaches
the roof) and a lid (where only a ladder does), measured rather than assumed. This folder is that split.

## Instrument

`census.py` reads every `deli_counter/specs/*.json` (446 on 2026-10-15) and, per spec, the stairs whose
`to_story` reaches the roof level (`n_stories`), the ladders that are roof access (`role`, `upper_surface`,
`transition` or `to_story`), and the `vertical_links` of kind `hatch` on the roof slab. Then the two
populations by what cuts the slab: a stair with `cut_slabs` leaves the hole at its head; a ladder leaves one
only where a hatch link sits at its own (x, y). Output: `census.out.txt`.

## What it reads

    specs                                       446
    stairs                                      511     to the roof   16
    ladders                                     124     roof access   69
    hatch links on the roof slab                 43     below it      37

    specs with a roof opening or a stair to the roof   73
      reached by a stair   (bulkhead)                   16
      reached by a ladder  (lid)                        57
      hatch link with neither                            0

The refinement that decides the build:

- **The 16 stairs are all switchbacks with `cut_slabs` true, in specs with no roof hatch link** -- so each
  leaves the roof slab open at its head, and nine of the sixteen are the mission buildings Level Factory writes
  today (`lf_deli_001_*`, `lf_restaurant_row_001_*`, `lf_urban_row_001_*`, three seeds each): every level
  made this week has a stair head open to the sky. Those are the bulkhead's population.
- **Of the 69 roof ladders, 43 have a hatch link at their foot and 26 do not.** The 43 cut the slab (42 of
  them `interior` with `roof_hatch_exit`); the 26 are exterior, parapet or platform ladders (`parapet_crossover_platform`,
  `side_step_off`, or older specs with no placement recorded) that cut nothing and need no lid. Those 43 are
  the lid's population. The item's "58 of 58" counted built output; this counts the contract, and the hatch link
  is what cuts.

So: **16 bulkheads, 43 lids, and 26 roof ladders that were never a hole.**

## What this decides

Build order, by population and by cost:

1. **The lid** (43 openings): one Zoo species, a hatch cover sized to the hole (`SlabHole` is 1.5 x 1.5 m by
   default), closed, with collision, standing on the roof slab over each `hatch` link whose story is the roof.
   Deli Counter places it where it already emits the `HATCH_<x>_<y>` marker; the ladder's `roof_hatch_exit`
   transition is unchanged (the cover is the thing the climber opens, which is the game's, as the doors are).
2. **The bulkhead** (16 openings): a Zoo species -- four short walls, a flat or mono-pitch roof, a doorway on
   one side -- stood by Deli Counter over the top landing of a stair that reaches the roof, its doorway cut and
   derived like any door, and the roof slab under it no longer cut.

Neither is started here. The look of both is the walker's reference (the tenement roofscape photo), and each
is a look change: frames before it ships.
