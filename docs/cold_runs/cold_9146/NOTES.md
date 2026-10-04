# Cold run 9146 -- STOPPED AT EXPORT, not a zero

gas_block_001, seed 9080, `empties: "across"`: the first level to stand the
rowhome Empties (Deli Counter 0.174.0) across the street (Level Factory
0.137.0). Exported with `--bake-lights`.

**Result: the driver read `INTERVENTIONS: 0`, and that number describes a run
that produced no package.** The shell and art legs passed. Export exited 5
(`EXIT_INTERNAL`) and the driver stopped there. A zero counted on a run that
never shipped is not a zero; this run does not count toward
interventions-per-level.

## What stopped it

The driver's grep kept only `^exported|CLOSURE|light bake`, so the error line
was thrown away. Recovering it took a full re-export of the same workspace,
after `--end`, with the whole output kept:

    internal error: GREYBOX_SLAB_IN_A_THEMED_PACKAGE: 588 slab surface(s) still carry a greybox material

`greybox_skin_scan.json` lists only the worst 20, all under
`Bake/Site/blocker_<n>/GreyboxBase/slab_*`. The full 588 were attributed off
the shipped `lot/<aid>/site_base.glb`s: visual slab primitives per base,
times the base's instances in `site.tscn`.

| archetype | slabs a base | placed | total |
|---|---|---|---|
| gs_empty_rowhome_a | 24 | 2 | 48 |
| gs_empty_rowhome_b | 24 | 4 | 96 |
| gs_empty_rowhome_c | 24 | 5 | 120 |
| gs_empty_rowhome_d | 18 | 6 | 108 |
| gs_empty_rowhome_e | 24 | 2 | 48 |
| gs_empty_rowhome_f | 24 | 7 | 168 |
| **Empties** | | 26 | **588** -- the gate's figure exactly |
| bank_tower_a02, freight_terminal_a01, gas_station_a03 | | 3 | 193, skinned |

The first count printed `x0 placed` for every row: its regex expected
`res://lot/...` and the package writes `lot/...`. It was caught because a
zero could not be right, then fixed and rerun. Kept as the instance of
"read one real artefact before writing the reader".

## Why

- **No module to skin from.** The worldskin's slab pass dresses a slab from a
  `floor_` module in `art/zoo` beside the base. An Empty's art folder held
  only `doorway_`, `wall_`, `wallEnd_` and `window_` modules: Deli Counter
  recorded an Empty no floor, ceiling or roof slot (75 slots on rowhome_f,
  all walls, windows and doorways), because an Empty has no rooms.
- **Slabs nobody can see.** Deli Counter's facade branch was documented
  "exterior + roof + theme only. No interior" and called `_slabs()`, which
  emits every storey. So each Empty carried a ground slab and the floors
  between storeys, inside a sealed box behind opaque glass.

## Fixed in the tools

- **Deli Counter 0.175.0** (3107e6e4): an Empty keeps only its roof slab,
  visual and collision, and records a roof slot in `concrete`. A 1990s
  rowhouse roof is tar, never its brick.
  - Visual slabs per house: 24 or 18 → 6. On this site: 588 → 156 meshes,
    and 98 → 26 slab colliders.
  - The six Empties joined `navgate_baseline.json` as facade-only. 0.174.0
    slipped past that check: `check.py` runs its unit suites before
    `nav_gate --all` writes the files the test reads.
- **Level Factory 0.138.0** (de7a59d): `SLAB_REVEAL_FAMILY` is
  `["floor_", "roof_"]`. A real-import test passes; its control (a base with
  both modules still takes `floor_`) also passes.

## Seen, not fixed

- **An Empty's doorway is an open frame with no door leaf** (Zoo
  `doorway_*`: a frame and its trim, no leaf). Since 0.174.0 a solid
  collision wall stands behind it, so a player sees a doorway they cannot
  walk through. An Empty needs a closed door: a storm door over a painted
  door, 1990s.
- The driver now `tee`s the art and export legs to `art.log` and
  `export.log` beside the batch, so the next stop keeps its own reason.

The re-run is cold run 9147.
