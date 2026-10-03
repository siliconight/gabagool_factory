# Streetlights that do not light the lot: measured

The walker, 2026-10-03, walking `_runs/walk_export_moving` (9139's lot on
Zoo 1.56.0 / Lux 0.62.0 / Level Factory 0.130.0): "we still have quite a
few street lamps that aren't putting their light down", with a frame of a
lit lamp head over dark ground and another of a pole lighting a sidewalk
and a wall.

## What was measured (`patches/lf_wind/pole_cap_probe.gd`, the walk copy)

Every pole, read in the scene:

    17 poles; cone -Z points down (-1.00) on all; angle 55; range 14.0;
    energy 19.2 (5 cycling poles lower, mid-cycle); lenses bound on the
    cycling five.

The ground under each pole: the sidewalk tile its lamp stands over carries
1 to 3 lights (one carries 7), under the cap of 8. Those tiles ARE lit --
the walker's second frame.

The ground tiles each pole REACHES (its 14 m sphere against the tile's
box), and which of those carry more than 8 lights:

    site_lamp_1   39 tiles, 1 over cap   Ground_3/mesh_t0_5 (11)
    site_lamp_30  49 tiles, 1 over cap   Ground_6/mesh_t0_3 (9)
    site_lamp_34  75 tiles, 24 over cap  (the store's floors and ceilings
                                          through the walls, and the lot)
    the twelve others: 0 outdoor tiles over cap

The outdoor tiles over the cap, and who is on them:

    Ground_3/mesh_t0_5  7x6 m  11 lights: Spawned_fluorescent x4 (range 7),
        Spawned_sign (6), b0_ext_0_S_window_1 (4), b0_sales_floor_spill x3 (7),
        site_lamp_1 (14), site_lamp_34 (14)
    Ground_6/mesh_t0_3  8x8 m   9 lights: Spawned_fluorescent x3, wall_pack,
        window, spill x2, site_lamp_30, site_lamp_34
    path_0/mesh_t0_0    8x9 m  12 lights: fluorescents x5, pendants x2,
        wall_pack, windows x2, spill x2 -- no pole at all

## The cause

The store's INDOOR lights reach outdoors. A ceiling troffer's range is 7 m
from a ceiling at 3.2 m; its sphere crosses the wall and overlaps the lot
tiles outside. GL Compatibility assigns a light to a mesh by that overlap
and keeps at most 8 per mesh, in its own order. On the tiles where four
troffers, three spills, a sign and a window already sit, a pole is the
ninth and is dropped, while its lens -- an emissive face, not a light --
stays bright. The sidewalk strips are narrower and clear of the store's
spheres, so the same pole lights them.

A REFUTATION kept: the first read of the census ("47 meshes over the
cap") pointed at the per-mesh cap as such; the probe showed the sidewalk
under every pole is under the cap, and only the lot tiles beside the
store are over it. It is the leak, not the cap alone.

## A cap of 16, priced (`perf_cap8_a.json`, `perf_cap16.json`, `perf_cap8_a2.json`)

`rendering/limits/opengl/max_lights_per_object=16` on the same package,
the fixed-station harness, fresh copies, idle machine, the shipped cap
before and after as the control, one session:

| cap | mean median ms | mean p95 ms | mean GPU ms | mean draws |
|---|---|---|---|---|
| 8 | 5.88 | 7.08 | 2.45 | 1079.6 |
| 16 | 6.63 | 8.28 | 4.50 | 1086.8 |
| 8 again | 5.89 | 6.82 | 2.46 | 1079.6 |

    median ms, 16 minus 8 (second pass): mean +0.74, max |2.90|
    GPU ms,    16 minus 8:               mean +2.05; store-side views +2.36
    control, 8 minus 8:                  mean -0.01 (GPU -0.01)

The cap of 16 nearly doubles the GPU time of the whole level and the
control is flat, so the instrument sees it plainly. NOT SHIPPED. It is
the engine evaluating every assigned light per pixel on every lit mesh;
the lot gets its poles back at the price of every room.

## What would fix it, in the order to try

1. **Keep indoor light indoors.** A troffer's range is derived from its
   drop so its pool reaches the floor; nothing says it should cross a
   wall. A per-building clip -- the range capped at the room's reach, or
   the spawner given the building's footprint so an indoor light's sphere
   is trimmed to it -- removes the leak at its source. Lux owns the rule;
   Deli Counter knows the rooms.
2. **Bake the stable lights** (roadmap item 31, the probe the walker
   agreed to): baked troffers and spills leave the dynamic per-mesh count
   entirely. The right long-term answer; the probe comes first.
3. **Smaller lot tiles where lights are dense.** Lot's tiles are already
   light-budget-sized for the sidewalks; the lot plates near the store
   front could be cut finer. Costs draws; priced if 1 and 2 fall short.

Not a fix: the poles' own range (14 m) is not what crowds the tiles.

## RETRACTED as the cause of the dark poles (2026-10-03, later the same day)

Kept above as written. The leak and the cap are real on the tiles the
probe named, and they are not why the walker's poles were dark: at the
walker's second spot (-3, 1.6, 35) the tiles under the dark poles carried
1-4 lights, under the cap, and a fresh unshadowed spot on a dark pole's own
transform lit its foot (0.594) while the pole's own lamp did not (0.180)
with every other light in the level switched off. A survey over all 17
poles (`docs/findings/streetlight_shadow/NOTES.md`) found the 12 dark ones
were exactly the 12 the shadow budget had given shadow maps, and the caster
was the pole's own shaft cap, 5 mm under the lamp. Fixed in Lux 0.64.0 (the
lamp hangs 0.10 m below the lens point). The cap of 16 stays refused on its
own price; items 1-3 under "What would fix it" remain the answer to the
leak, which still crowds the lot tiles beside the store.
