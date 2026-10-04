# Cold run 9149 -- STOPPED AT ART on the new collision guard; not a zero

gas_block_001, seed 9080, `empties: "across"`.

**Stack:**
- Deli Counter 0.178.0, with parapets as wall slots and the Empties' doors
  shut;
- Zoo 1.62.0, which refuses a stem collision;
- Level Factory 0.139.0, which blocks on one.

**Result:** the art leg stopped on one blocker,
`gas_block_001.zoo_kit_build.freight_terminal_a01`. The driver read
`INTERVENTIONS: 0` over a run with no package; this does not count as a
zero.

## What stopped it

Zoo's own refusal, in the job log:

    [zoo] REFUSED: STEM COLLISION wall_delco_1997_04_w451_mmetal -- 2 geometries planned under one name
    [zoo] REFUSED: STEM COLLISION wall_delco_1997_04_w491_mmetal -- ...

The kit index's `stem_collisions` dims were [4.514, 0.2, 1.0] against
[4.515, 0.2, 1.0], and 4.909 against 4.910. These are the freight terminal's
parapet tiles: wall slots since Deli Counter 0.177.0, cut by
`floors.slab_tiles` at millimetre-snapped lines.

## Why, and whose

**One number asked at two resolutions.** Deli Counter 0.177.0 moved its own
name check to whole centimetres for exactly these tiles. Zoo's `plan_kit`
kept grouping exact-fit slots at 0.1 mm while naming them in centimetres. A
group finer than its name is a collision by construction.

**My miss.** The guard was right. The defect was letting one side move
without the other, and starting a run without planning the library through
Zoo first.

That pre-flight, run afterwards (`plan_kit` over all 139 built manifests):
- Zoo 1.62.0: **42 buildings, 63 collisions**. Most levels would have
  stopped here.
- Zoo 1.63.0: **0**.

## Fixed

**Zoo 1.63.0** groups at whole centimetres. A millimetre apart is one module;
2.8 against 3.1 m unmarked still collides.

The guard (Zoo 1.62.0 plus Level Factory 0.139.0) is unchanged. It did what
it was built for: it stopped a run that would otherwise have shipped
whichever module built last.

Re-run: cold run 9150.
