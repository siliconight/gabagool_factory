# Pieces through walls

Found 2026-10-06, sizing the deli case for roadmap item 186's "deli detail".
Shipped as Deli Counter 0.199.0 (layout_lint L25, `migrate_wall_crossing`).

**Frames and units.** The spec's frame: metres, the footprint centred on 0,
x east, y north, z up from the storey-0 floor. Godot's frame, where a package
is quoted: x the same, y up, z = -(spec y).

## How it was seen

In cold run 9189's composed deli_a01 (the `presentation_compose` job's
`out/presentation/lot/deli_a01/site.tscn`, the shipped level's building):
- `deli_case_cover`, the deli's case, stands at x -10.5, 7.0 m long:
  x -14.0 to -7.0.
- Partition `int_0_0`'s segment `int_0_0_seg6` stands at x -8.0, across the
  same z.
- So the last 0.825 m of the case comes out of the far face of the wall into
  the market aisles.

`presets.corner_deli` authors the case that way, so all six library delis
carry it, and so does every deli the recipe generates.

## What was measured

Every authored piece against every wall the builder stands, over the 146
non-LF specs. A piece CROSSES a wall when its plan reaches past both faces of
the wall's band, on a stretch of the wall that is built, on a storey its
height reaches: matter on both sides.

**19 pieces in 15 specs at 0.198.0** (`census_0198.txt`). Two shapes:

| shape | pieces | which | past the far face |
|---|---|---|---|
| THROUGH: the centre stands off the wall | 7 | each deli's `deli_case_cover` (6) | 0.825 m |
| | | `warehouse`'s 16 m `shelving_run` | 3.85 m |
| ALONG: centred on the wall's line | 12 | `rack_long_b`, `forklift_bay` on y -3.0 (setback_demo, warehouse_a02) | 0.45, 0.85 m |
| | | cbp_town_finale's two vomitory covers on x -18 and 18, its rollgate across a 2.2 m door | 0.45, 0.20 m |
| | | bank_branch_a04's `VAULT_DOOR`, no opening under it | 0.10 m |
| | | four garage columns, 0.5 m square on 0.35 m walls | 0.075 m |

None stands at an opening. With every opening cut out of the walls the count
is 19; with every opening left solid it is the same 19.

**The recipes**, each through `presets.REGISTRY` in both modes before
0.199.0:
- `corner_deli` generates the case through its wall;
- `hospital` generates its `waiting_seats` 0.35 m through the partition at
  x -8.0;
- `casino_tower` stands its basement `vault_block` centred on the partition
  at x 0;
- `parking_garage` stands its first column on a wall.

The library hospitals do not carry the seats through a wall. The one-building
briefs Level Factory 0.145.0 leaves generated (county_hospital_001) do.

**No gate saw any of them.** Every rule asked a piece where it stands, and
none asked whether a wall stands in it.

## What shipped (Deli Counter 0.199.0)

- **L25 (WARN):** `layout_lint.wall_crossings` names every piece through a
  built wall and its shape.
- **The trim:** `migrate_wall_crossing.trim` cuts a piece THROUGH a wall back
  to the side its centre stands on, its far end at that face less
  `level_design._WALL_PIECE_AIR` (0.01 m).
  - It refuses a piece along a wall, a turned piece, a cut past half the
    piece, and a cut from under a marker. Each refusal says why.
  - `presets.make` runs it on every recipe before any pass places round it.
  - The migration ran it over the library: 7 trimmed, the case to
    x -14.0..-8.185 and the shelving to x -4.0..7.84.
- **The twelve ALONG a wall** are frozen in
  `deli_counter/wall_crossing_baseline.json`. A new one fails.

**After: 12 pieces in 8 specs** (`census_0199.txt`), the twelve frozen.

## Refuted, kept

- **The first instrument cut each opening at `pos * run` unsnapped.** The
  builder cuts it at `snap(pos * run)` (`Builder._opening_to_hole`).
  Snapped, the count did not move.
- **It modelled only the exterior walls `ext_walls` lists.** Under
  `auto_exterior` (the default) the builder stands all four sides on every
  storey. Modelled so, no exterior wall is crossed.
- **It skipped 465 turned pieces as unmeasured.** The second instrument
  measures each by its box and by its art turned: none crosses.
- **The first instrument printed "specs read (no lf_*): 427".** That counted
  every JSON. It read 146.
- **The tests patch first said `test_the_baseline_has_not_gone_stale`
  "passes either side".** It cannot run without the rule. Corrected in
  `patches/patch_dc_wall_crossing_tests.py`.

## Not established

- **Whether each ALONG piece is by design.** A column on a wall line may be
  structure. A rack centred on a partition is not. Each needs a look.
- **The trimmed case and shelving in a level frame.** That is the next cold
  run's to show.

## Instruments

- `wall_cross_census.py [--specs DIR] [--list]`, the first: authored runs,
  openings cut, listed exterior walls, turned pieces skipped.
- `wall_cross_census2.py [--specs DIR] [--list]`, the second: the walls the
  builder stands, asked of its own helpers (`partition_bounds`, `setbacks`,
  `stairwell.wall_voids`), and turned pieces measured. Layout_lint L25 is
  this instrument, lifted.
