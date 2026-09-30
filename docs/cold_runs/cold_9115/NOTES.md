# Cold run 9115 -- poster walls, seen at night

The walker, 2026-09-30: posters in strip club interiors, bar interiors, alley
walls and poles, and store windows and walls; "fix the arm and legs, add the
poses, then placement"; "do the cold run of club_block_014". Deli Counter
0.163.0 (poster runs hung as fixtures), Zoo 1.31.0-1.32.0 (the redrawn club
sheets: a figure in three poses, three layouts, monogram italic), Lot 0.83.0
(the enterability gate reads a build's wall labels). Same brief, same seed,
same lot (replayed before --begin: strip_club_a01, airport_terminal_a02,
gas_station_a02 from 43 fit families).

Zero interventions, one observation (the look below). The art leg read before
export: 0 blockers, 64 findings, identical to 9114 but one line --
PRESENTATION_TINT_MATERIALS, 694 -> 700 material entries (the six poster
modules). Exit status 1 on both legs is `EXIT_FINDINGS`, as in 9114. Export
closure clean: 257 GLBs, 1,140 references, 0 missing.

## What the frames show (full scale; `posters_4m.png`, `posters_2m.png`)

Stations from the specs through each building's lot transform (both turned
90 degrees: world = (origin.x - y, z, origin.z - x); club at (-69, 0, -5),
gas station at (78, 0, 10)), camera 4 m and 2 m off the wall on the room side,
at the eye. Every station found its run, so the mapping is right.

- strip_club_a01's main floor carries five runs (W, S, E walls; 3.2, 1.6 and
  2.4 m) and the VIP wing two. The sheets read as the Zoo 1.32.0 art -- the
  three poses, the marquee, the stepped diagonal, the gold strip -- and no
  run repeats in its room.
- gas_station_a02's sales floor carries two sale-poster runs on its stone W
  wall, off the glass: SCRATCH & WIN, PHONE CARDS, OPEN 24 HRS, LOTTO HERE.
- THE CLUB'S LIGHT TAKES THE POSTERS' WHITES AND BLACKS. Paper is lit by the
  room, and the club rooms are dim and coloured: at 4 m the frames average
  2.7-13.6 luma. Measured at 2 m on the poster band:

      station      band p5   p50    p95    max  | wall above mean
      club S         0.5     9.5   58.4  126.5  |  7.1
      club W         0.0     3.7   29.2   92.3  |  3.9
      club E         3.4    13.2   36.3   91.9  | 10.4
      store          8.9    33.3   69.6  104.8  | 28.5

  The painted near-whites (about 250) arrive at 92-127, and the median of
  the band sits a few levels over the wall. The shapes read at 2 m; the value
  range the walker asked for does not survive the club's light at 4 m.
  Not changed here -- it is a lighting question, not a poster one.

## An unrelated re-roll, and what it cost (`store_9114_vs_9115.png`)

22 of gas_station_a02's modules (floors, ceilings, cartons, a chair, a
counter) were renamed and rebuilt: their stems' style index moved +1. The
mechanism, read: a surface's skin style is its material's 1-based position in
the builder's material list (`skin_style.material_styles`), and the dressing
materials the builder appends -- concrete, wood, carpet, tile, ceiling_tile,
plaster -- come AFTER the spec's own list. Deli Counter 0.163.0 declared
`paper` in the spec, so every appended material moved down one place and every
module keyed on it got a new stem. It is older than the posters: any release
that declares a new material in a spec re-rolls those surfaces.

What it cost here, measured: frame means at 9114's six store stations move by
0.9 or less, and 0.0-0.6 % of pixels differ by 12 levels or more at the
cooler wall, the entrance and the counter. The rebuilt modules carry 2 fewer
mesh nodes than the ones they replace (62 against 64), which is why the
harness's mesh count rose by 7 for 9 posters.

## Cost

Fresh package copies of 9114 and 9115, imported headless, `perf_stations_run.py`
twice each, alternating, in one session:

    draws, heading by heading     60,671 -> 60,753 (+82) over 53 headings;
                                  21 identical, largest +11 (highest_vantage
                                  at 90), then +7, +7, +6, +6, +5
    control, 9114 a against b     identical on all 53
    frame median of medians       4.192 / 4.190 -> 4.210 / 4.267 ms
    worst p95                     11.37 / 11.03 -> 11.02 / 11.01 ms
    mesh instances                4,421 -> 4,428 (+9 posters, -2 re-rolled)
    nodes                         10,949 -> 10,974
    positional lights             112 both; meshes over 8 lights 43 both

A poster run is one draw, and the lot gained nine; +82 over 53 headings is
those runs seen from the stations that face them. The frame-time move is
inside what 9115's own pair spreads (0.057 ms) and is not resolved.

THE INSTRUMENT ACROSS SESSIONS: the same 9114 package measured 60,732 draws
on the same 53 headings in 9114's record and 60,671 here, with the harness
unchanged since 2026-09-27. Within a session it repeats exactly. So a draw
figure compares only to one measured beside it; the 61 is not explained.

## Findings to act on

1. The club's paper posters lose most of their value range in the club's
   light (above). Options, for the walker: leave it (it is a dark club); a
   blacklight/UV treatment on club sheets (emission in the same material --
   no new draw, a look the lewd guide's clubs would own); or a warmer wash
   on the poster walls (a light, priced against the 8-per-mesh cap).
2. Deli Counter's style index is positional, so declaring a material re-rolls
   unrelated surfaces. Harmless-looking here; a stable key (the material id)
   would stop it, and changing the key re-rolls everything once.
3. Lot 0.83.0's enterability change, read off the lot job's
   `site.site.gameplay.json` in both runs: entries counted 8/11/12 -> 4/6/4
   (the storey-0 exterior ones), all clear before and after, no building
   walled in, and the same one warning (b0, the strip club: no authored path
   to a clear entry) in both.

## After the run: the blacklight probe (Zoo 1.33.0)

The walker chose "blacklight treatment for the club posters" ("if it looks
bad, no light is also ok"). Probed before shipping, outside the clock: the six
club modules this run used were rebuilt under their exact stems with the
working tree's Zoo (a backlit `_Face` material, emission 0.6, same atlases),
swapped into a copy of this run's walk scene, re-imported, and shot at the same
stations (`blacklight_probe.png`, paper left, blacklight right). Poster band at
2 m: max 92-127 -> 237-247, p95 29-58 -> 131-192, p5 unchanged (0-5). It
shipped as Zoo 1.33.0; the next cold run is the first to carry it.
