# Cold run 9112 -- glass off the back rooms

The walker, 2026-09-29: "keep glass off the back rooms, use a room-name list".
Deli Counter 0.159.0: a storefront slot glazes only where the room behind it
is named in `SHOPFRONT_ROOMS` (`sales_floor`, `food_service`); a shell-walled
store's other rooms keep the building's default wall. Zero interventions; the
art leg read before export: 0 blockers, 64 findings.

    gas_station_a02, east facade (from its slots.json, the kit's input)
      y -9.85 .. 0.2    glass_facade   food_service behind it (centre y -5)
      y  2.2  .. 10.03  stone          walk_in_cooler behind it (centre y 6)

THE FINDINGS DO NOT COMPARE TO 9111, and not because of this change. Every
candidate drew different buildings:

    seed    9111                                  9112
    9181    deli_a01, gas_station_a02             airport_terminal_a02, gas_station_a02
    9080    brewery_a01, market_hall_a02          landmark_hall_a02, pvp_station_ref
    9282    credit_union_a02, museum_a02          casino_a02, funeral_home_a02
            (strip_club_a01/a02/a03 anchor each lot in both)

Attributed, not assumed: `building_library.pick_lot` replayed on today's
library with `stop_n_go` removed from the themed pool gives all nine 9111
picks exactly. Deli Counter 0.158.0 (the storefront on every store) made
`stop_n_go` modular, so its slot coverage stopped being empty and
`themed_fitness` passed it -- the 43rd fit family. `pick_lot` draws
`pool.pop(next(rng) % len(pool))`, so one more family moves every draw after
it. The comment on `REQUIRED` warns of exactly this for suffixes; a family
becoming fit does it too, and nothing says so when it happens.

So 58 -> 64 is a different lot's findings (the airport terminal alone adds
LUX_NO_ROOM_PROBES for its check-in hall and rooms beside it), not a
regression. The gas station is the one building both lots share.

ERRATUM (cold run 9113): the frames below were taken during Level Factory's
shader warm-up, at scaling_3d_scale 0.1 -- see cold_9113/NOTES.md. Re-shot
at full scale in `cooler_wall_9111_vs_9112_fullscale.png`: east wall 16 m
9.4 / 8.7, cooler run 8 m 16.6 / 7.4 (36.1% / 47.2% black), oblique 9.8 /
9.6. The conclusion stands; the figures move by under a code.

THE COOLER WALL AT NIGHT, 9111 vs 9112 (`cooler_wall_9111_vs_9112.png`,
left 9111, right 9112; rows: east wall at 16 m, the cooler's run at 8 m, an
oblique from the forecourt end). The gas station stands at x 70 in 9111's lot
and x 78 in 9112's, same rotation, so each station was placed from its own
lot's origin; 9111's walk copy was rebuilt from its package and its
`_walk.tscn` matched the original byte for byte. In 9111 the cooler's run was
lit glass with a spill pool on the pavement under it; in 9112 it is a dark
stone wall and the glass stops where food_service does.

    player's frame, night (mean / % crushed to black)
                          9111            9112
    east wall, 16 m       9.0 / 33.1      8.2 / 34.1
    cooler run, 8 m      16.1 / 35.5      7.0 / 47.4
    oblique               9.3 / 34.0      9.1 / 34.2

That is the change doing what it was asked to do, and it costs that facade
its light: the cooler's 8 m frame loses more than half its mean.

PRICED, and what the price can and cannot say. Both packages copied fresh
(`.godot` deleted, re-imported), `perf_stations_run.py` twice each,
alternating, one session:

                        9111 a / b          9112 a / b
    worst draws         2774 / 2774         2620 / 2620
    worst p95 ms        11.62 / 11.94       11.19 / 10.87
    mean p95 ms         7.71 / 7.62         6.97 / 6.67
    mean draws          1936 / 1944         1621 / 1623
    lights / meshes     156 / 4688          111 / 4415
    meshes over 8       58                  40

9112 is cheaper, and almost none of that is 0.159.0. The lots differ (an
airport terminal where 9111 had a deli), the stations are derived from each
package's own markers, and nine stations share a name but not a position --
per-station rows were computed and are NOT comparable. What 0.159.0 removed
on the one shared building is one spill lamp and the back-room glass on
gas_station_a02; the package-level drop in lights, meshes and draws belongs
to the draw change.

OPEN, reported not changed: a stable draw -- ranking families by a per-family
hash of (seed, family) instead of popping from a positional list -- would make
a new fit family displace only the picks it outranks, so a cold-run series
stays comparable across library growth. It re-draws every existing seed once
when it lands, which is the cost `REQUIRED` exists to avoid.
