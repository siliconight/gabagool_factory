# Cold run 9220 -- 0 interventions, 0 retries; the garbage bags beside the dumpsters, on the walked level

club_block_014, seed 9181 at night: the level the walker walked on
2026-10-09 (cold run 9213). It is staged from 9219's batch and brief, and
proves roadmap 219 note 11, "need filled black garbage bags stacked near the
garbage bins":

| what | fix |
|---|---|
| `trash_bags`, a heap of filled garbage bags | Zoo 1.93.0 |
| one heap beside each dumpster, on its pad | Lot 0.104.0 |

Tool versions hashed at `--begin` (`_runs/cold/cold_9220/before.json`):
Deli Counter 0.205.0, Dispatch 0.5.2, Laser Tag 0.25.0, Level Factory
0.165.0, Lot 0.104.0, Lux 0.72.0, Patina 0.29.2, Pipeline 0.6.0, Pixelcoat
0.61.0, Zoo 1.93.0.

**`INTERVENTIONS: 0`** (journal 0, unattributed files 0), **retries 0.**
- **Picked: seed_9181,** as 9213 and 9217 to 9219 picked it.
- **The shell leg:** 0 blockers of 51. **The art leg:** 0 blockers of 71.
- **Findings 71 to 71.**

## What Lot placed

The seed-9181 assemble's own log, exactly as Lot 0.104.0's replay of 9218's
spec predicted before the run:

    LOT_BAGS_PLACED: TrashBags_b0 at (-76.07, 10.85) yaw 90.0 beside Dumpster_b0, heap 3, on its pad
    LOT_BAGS_PLACED: TrashBags_b1 at (27.07, 18.85) yaw 270.0 beside Dumpster_b1, heap 1, on its pad
    LOT_BAGS_PLACED: TrashBags_b2 at (56.93, 10.85) yaw 90.0 beside Dumpster_b2, heap 3, on its pad

- **Three dumpsters, three heaps, all on their pads.** Each heap stands
  beside its dumpster, toward the middle of the wall, turned so its row of
  bags lines the container's side.
- **They reach the package** as `cover_116` to `cover_118` in `site.tscn`
  (`prop_trash_bags_delco_1997_01_w140_d80_h75_n3` and `_n1`), at Lot's
  positions.
- **The bake:** 435 models against 9219's 433 (the two heaps' modules) and
  3,897 users against 3,894 (the three heaps), 91.3 s in the editor.

## The heaps

`bags_blender_1_93_0.png` is Blender's render of all four heaps from Zoo
1.93.0:
- filled black bags, slumped and knotted at the neck;
- heap 3, which this level ships twice, carries a green contractor bag.

**Measured, correcting 1.93.0's changelog, which gave variant 0 alone:**
- at the default 1.4 x 0.8 x 0.75 slot, heaps 0 and 2 are 1,536 triangles
  and heaps 1 and 3 are 1,920;
- at the largest slot, heap 0 is 2,304 and the odd heaps are 2,688, under
  the genome's 2,800.

## In the frames: present, and black

`tools/look_shots.py` on the walk copy at midnight, low along each wall
(`bags_at_night.png`). Means are of 255:
- **b0** (the strip club's dumpster): mean 9.3, median 1;
- **b2** (the funeral home's): mean 10.5, median 1;
- **b1** (the airport terminal's): mean 6.1. Its frame is filled by the
  building's dark wall and is not kept.

**The heaps are where Lot put them, and they read as black lumps.** Every
dumpster stands on a north wall, in the building's shadow from the moon. Bags
of albedo 0.020 lit by nothing but the bake's bounce are a lumpy silhouette
against the moonlit pad, still black at four times brightness. The dumpsters
beside them read by their paint and their hauler's sign.

**What would show them, not done:**
- **light on the service side.** A wall pack over the back door that serves
  the dumpster: real ones have one, and Deli Counter derives wall packs over
  doors already;
- **gloss.** The bake is not directional, so a baked surface gets no
  specular, and black plastic is mostly specular;
- **a less absolute black.** 0.020 is darker than black polyethylene's
  usual 0.04 to 0.05. That would lift black only to near black at night.

The first is the walker's call, with the rest of the night's look.
