# Cold run 9137 -- the whole store in one look

gas_block_001, 9135's brief and seed (9080), on Zoo 1.53.0, Level Factory
0.128.0, Pixelcoat 0.55.0. Zero interventions (journal 0, unattributed files
0), no observations. The same three buildings as 9135 and 9136.

Since 9136: Zoo 1.49.0 (the owner pass -- Aileron, Vegur and MFB Oldstyle
vendored by Pixelcoat 0.55.0, each typeface with an owner, the ATM's and the
poker's tubes in the pixel face), 1.50.0 (the candy rack), 1.51.0 (the
cooler wall), 1.52.0 (the frozen drink station), 1.53.0 (the roller grill).

## Seen in the level (`frames/`)

The 9136 probe, taught to find the cooler wall, the frozen drink station and
the roller grill by their materials. `till0_counter` is the one to look at:
the counter's candy rack, the tills and dispensers, the rack over them, the
cooler wall behind, the frozen drink station and the grill at the end, all
in one look. `slush_front`, `grill_*`, `cooler_*`, `rack_*`, `atm*`,
`poker0_*` are the parts.

What a frame still shows in the pixel look: the counter's laminate top and
the store's walls (both are Pixelcoat skins, not Zoo art), the cup tubes'
cups, the syrup bottles.

## Priced (`perf_9137.json`, `perf_9137_again.json`)

The fixed-station harness twice on a fresh copy, idle machine, against 9136.

| package | mean p95 ms | mean draws | views over 11 ms |
|---|---|---|---|
| 9136 | 5.32 | 1079.2 | 3 |
| 9137 | 4.19 | 1080.9 | 1 |
| 9137 again | 4.52 | 1080.9 | 2 |

**Draws**: 52 of 53 views identical to 9136. ONE VIEW IS NOT:
`attacker_spawn_1` at yaw 0 reads 1,169 draws where 9136 read 1,083, with
1,085 objects in view where there were 999 and 1.99 M primitives where
there were 1.35 M -- the same camera position to the millimetre, and the two
passes of this package agree with each other. NOT ATTRIBUTED. `site.tscn`,
`mission.tscn`, `occluders.tscn` and `occluders.json` are byte-identical
between the two packages; what differs is the props' GLBs and their
textures, and nothing in this release moved a vertex. The 86 objects have
not been named. It is one view of 53, and it is written here so the next
run on this brief can say whether it persists.

**Frame time**: this package reads 1.1 ms a view FASTER than 9136's did,
and its two passes differ from each other by 0.68 ms. The machine was not
in the same state for the two runs (9136's passes were the slower pair of
that day); the figure is not a change this release made.

**Texture memory**, the renderer's figure with `mission.tscn` loaded and
the warm-up finished:

| package | texture memory | shared textures compressed |
|---|---|---|
| 9136 | 333,443,842 B | 11 of 157 |
| 9137 | 333,056,888 B | 15 of 157 |

The cooler's, the counter's, the station's and the grill's larger images,
compressed, cost nothing against 9136's figure: 0.4 MB UNDER it.

## Findings

51, and the same count under every finding code as 9136.

## Open

* The 86 objects at `attacker_spawn_1` yaw 0.
* The candy rack's one-metre repeat; the coolers' glow strength (walker's
  calls, asked 2026-10-02).
* The store's walls and the counter's laminate top are Pixelcoat skins and
  still the pixel look; the real-look trial has not reached Pixelcoat.
* Next: the "alive" queue -- light that isn't perfectly steady.
