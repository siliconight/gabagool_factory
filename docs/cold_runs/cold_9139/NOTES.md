# Cold run 9139 -- the first package with failing fixtures

gas_block_001, 9135's brief and seed (9080), on Lux 0.62.0, Zoo 1.54.0,
Level Factory 0.128.0, Pixelcoat 0.55.0. Zero interventions (journal 0,
unattributed files 0), no observations. The same three buildings as 9135,
9136 and 9137 (bank_tower_a02, freight_terminal_a01, gas_station_a03).

Cold run 9138 was a false start on this same batch: its `batch.json` was
written without the `briefs/` folder that stands beside every batch, the
batch created 0 missions, and the run was ended with that one note in its
journal. Nothing was generated under 9138.

Since 9137: Lux 0.62.0 (one failing fixture an anchor -- a fluorescent
stutters, a pendant wavers -- every third streetlight cycles, and the old
12 % / 9 Hz hum on every row is gone; a failing fixture's lens moves with
its lamp) and Zoo 1.54.0 (one price faces the customer on the till).

## What the package carries (`presentation/lux.applied.tscn`)

The export runs the fixture spawner headlessly and packs the rigs with their
resources, so the choice ships in the file:

    failing_kind = 1 (stutter)   9 rigs
    failing_kind = 2 (cycling)   5 rigs   (the loader's every-third pole)
    failing_kind = 3 (waver)     3 rigs
    flicker_amount               0 lines  (9137's file carried 47)

## Seen in the level (`frames/`)

A scratch probe (`failing_level_probe.gd`) on the walk copy, loaded as it
is -- nothing respawned, nothing made by hand -- after the warm-up:

    rigs=84 failing=17 kinds={1: 9, 3: 3, 2: 5}
    lenses bound by kind={1: 9, 3: 3, 2: 5}   rigs still humming=0
    tube Spawned_fluorescent_001: base energy 6.0, min 3.65, 8 drops in 30 s
    pole site_lamp_1: rig energy 19.2, seen 0.0 .. 19.2 in 80 s;
         frames lit, dark and restrike all caught; lens 1

Every failing rig bound exactly one lens. The concern raised before the run
-- that a packed rig's `owner` would be the Lux subtree and the lens search
from it would find no mesh -- did not bite: the owner is `Site`, which holds
the fixture GLBs.

`failing_tube_full` / `failing_tube_drop`: the tube at full and at the
first drop. In a still the drop is subtle -- at 61 % the diffuser is still
white -- so it reads in motion as a flicker, not in a frame as a dim.
`failing_pole_lit` / `_dark` / `_restrike`: the lamp head bright, black, and
dim on the restrike; that one reads plainly in a still.

## Priced

The fixed-station harness on fresh copies, idle machine. Two passes of this
package, and 9137's package once more IN THIS SESSION, because 9137's saved
reports (`cold_9137/perf_9137*.json`) were taken in an earlier session and
this session's own pass of those same bytes read 0.3-0.5 ms slower than
they did. A cross-session difference is the instrument's, not the package's.

| package | mean median ms | mean p95 ms | mean draws | views over 11 ms |
|---|---|---|---|---|
| 9137, same session | 4.37 | 4.87 | 1079.2 | 1 |
| 9139 | 4.52 | 5.34 | 1079.2 | 1 |
| 9139 again | 4.58 | 5.33 | 1079.2 | 2 |

    median ms, 9139 minus 9137 (same session):  mean +0.15, max |1.44|
    median ms, 9139 again minus 9137:           mean +0.22, max |4.00|
    median ms, 9139 again minus 9139 (control): mean +0.06, max |3.99|

**Draws**: identical in all 53 views to 9137's same-session pass.
**Frame time**: 0.15-0.22 ms a view over 9137, against a same-bytes control
of 0.06 ms this session and 0.68 ms earlier today (`cold_9137`'s A/B in
`docs/findings/failing_fixtures/NOTES.md` read -0.01 ms for the same Lux on
9137's own lot). The failing fixtures tick 17 scripts a frame where 84
ticked before; if there is a cost here it is at the instrument's floor, and
it is written down rather than rounded to zero.

**The 86 objects at `attacker_spawn_1` yaw 0** (open since 9137): 9137's
package read 1,169 draws there in its earlier session and 1,083 in this
one, on the same bytes; 9139 reads 1,083 in both passes. The view flips on
the same package between sessions, so it is the instrument (or the
renderer's culling at that station), not either package. Closed as such.

**Texture memory**, the renderer's figure with `mission.tscn` loaded and
the warm-up finished, both packages probed in this session:

| package | texture memory |
|---|---|
| 9137 | 333,056,888 B |
| 9139 | 333,041,944 B |

## Findings

51, and the same count under every finding code as 9137.

## Open

* The tube's drop in a still: if the walker wants it to read in a frame
  too, the floor (60-75 %) or the lens's emission base would move; priced
  by the same probe.
* The candy rack's one-metre repeat; the coolers' glow strength (walker's
  calls, asked 2026-10-02).
* The store's walls and the counter's laminate top are Pixelcoat skins and
  still the pixel look.
* Next in the "alive" queue: small things that move; a world that changes
  on its own. Designs shown first.
