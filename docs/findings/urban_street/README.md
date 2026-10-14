# The first urban street: a mid-rise wall across the street, seen and priced (roadmap 241)

The walker chose a new urban level type on 2026-10-11 (`docs/reference/URBAN_MIDRISE_COMPS.md`): mid-rise
blocks at the sidewalk line, touching, block after block. Then, 2026-10-13: "go ahead with the census, then
241".

## What shipped: Level Factory 0.200.0 (65cf5e7), steps 2 and 3, the first cut

- **The brief asks.** A brief asks with `streetscape: "urban"`. `models.streetscape_effective` decides what
  it gets: urban only where a terrace stands, and the functional signature carries it only then.
- **Every other brief is today's strip,** lock and terrace unchanged; the suite holds both.
- **An urban brief's far side** is a continuous wall of Deli Counter 0.213.0's mid-rise Empties
  (`building_library.empties_for_brief` draws `gs_midrise_*`; `empties.terrace(continuous=True)` drops the
  alley every five to eight houses). One fault found on the way: the adapter's preset list had not learned
  Deli Counter 0.213.0's `empty_midrise`, so `test_dc_preset_registry` had been red, unseen.

## Proven: cold run 9287 (`docs/cold_runs/cold_9287/`)

`urban_row_001` is restaurant_row_001's brief plus `streetscape: urban`. It ran at 0 interventions, and every
candidate's site stood 8 or 9 mid-rises across the street, themed. The near side's lots are 9285's buildings
exactly, so this folder's A/B isolates the far side:

    bash docs/findings/urban_street/ab_record.sh 9285 restaurant_row_001 9287 urban_row_001

**Seen** (`ab_sheet.png`, 9285 left, 9287 right):
- **The two road ends** look down the street, and the far side's three-storey rowhomes are now brick blocks
  that leave the frame's top.
- **From the south** (orthographic, `elev_S`), the wall's backs are dark, with lit windows.
- **From the north,** the wall stands taller than everything in front of it, at two heights.
- **The near side** is still the strip's one-to-three-storey row.

**Priced** (`price/price.txt`; Level Factory's fixed-station harness, 53 headings, control-subject-control):

    draws a heading     807 -> 736 on the mean (-71.6; -302 to +58)
    p95 frame time      -0.15 ms at the median (the controls' floor 0.03 ms)
    textures            76.0 -> 74.4 MiB
    buffers             47.9 -> 68.6 MiB
    video memory        123.9 -> 142.9 MiB

**What the price says.**
- **The wall is cheaper to draw than the terrace it replaced.** Eight or nine shells merged per side, against
  about two dozen rowhomes.
- **It costs about 19 MiB more resident memory, all of it buffers,** the geometry of five- to twelve-storey
  facades. Both controls read 47.9 MiB here. An earlier measurement (roadmap 238) saw buffers vary from 48.0
  to 56.1 MiB between runs of one package, and +20.7 is outside that.
- **The lightmap:** 3,037 users, against 3,392.

## What the walker is asked

- **The frames.** Is this the wall the comps meant, before the near side follows?
- **The near side, next.** The mission's own buildings among mid-rise Empties, with no plate between them.
  It meets what Lot lays after the roads (parking, pads, dumpsters), so it is its own cut.
- **Not drawn yet:**
  - heights by cause (taller away from the action);
  - the 2.0 m frontage, kept;
  - tree pits;
  - the corner shop at grade;
  - the dusk haze.

## Not attributed

- **Laser Tag's `LT_MAP_BLIND_MAP`** (moderate) is on all three candidates where 9285 had it on two: 52 to
  63% of positions never seen from an enemy spawn. A gapless, taller wall cutting sightlines is the obvious
  reading, and it is not measured. Enemy spawns are provisional until a gameplay layer owns them.
- **The bake's 60 fewer models** (566 -> 506) and 355 fewer users are read as the shell count, eight or
  nine shells where there were about two dozen. They have not been counted shell by shell.
