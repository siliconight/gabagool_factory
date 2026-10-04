# Cold run 9148 -- 0 interventions; both of 9147's fixes hold, a third defect found

gas_block_001, seed 9080, `empties: "across"`, `--bake-lights`.

**Stack:** Patina 0.24.0 and Deli Counter 0.175.2 (plus DC 0.175.1, LF
0.138.1). Every leg ran, and `INTERVENTIONS: 0`.

## What it verified

- **Patina's dressing stands right.** On `gs_empty_rowhome_f`:
  - `ground_edge` and `wall_base` at z 0.0, spread over 10 and 7 distinct x
    (9147: x = 0, z 0-10);
  - `roofline` at 9.0-10.0 m.

  In the frames, nothing sticks out of any wall.
- **The fronts close at every storey line.** The dark slot through the
  facades in 9147 is gone.

Frames: `docs/findings/empties_rowhome_9148/`, the same five views as 9147,
fill and night.

## What it found: 2.8 m panels in 3.1 m slots

The end house's alley side still showed a light strip and a dark line, at
about 3.1 m and 6.2 m. A headless census of the walk copy measured each side
wall's `Wall_Panel` at **2.80 m**, centred 1.55 and 4.65, in slots Deli
Counter now writes at 3.10 m. The `WallEnd_Panel` (unit-scaled) is 3.10.

**Why.** Zoo names a wall by width alone: "the storey height is fixed". The
Empty's walls became 3.1 m below the roof storey and stayed 2.8 m under it,
so both built as `wall_delco_1997_01_w200_mbrick_idrywall`. The kit index
listed it twice, and one file won. Windows too, for the same reason.

Across the library: 14 names, all in the 8 facade shells.

**Zoo saw it.** `STEM COLLISION ... one will overwrite the other` is in all
six Empty kit logs from this run. The kit exited 0, and Level Factory reads
Zoo's exit 2 as a usable kit anyway. The instrument fired and nothing
listened.

## Fixed

- **Deli Counter 0.176.0 / Zoo 1.60.0.** A name covering two heights is
  marked `fit.key_height` and takes `_h<cm>`; every other building keeps
  every name. A library-wide test now holds that no built name covers two
  geometries.
- **Zoo 1.62.0 / Level Factory 0.139.0.** A stem collision fails the kit
  (index plus exit 2) and blocks the run (`ZOO_STEM_COLLISION`). Proven on
  Zoo's real output: the marked rowhome builds clean, and the same manifest
  with its marks stripped is refused and blocks.

## Also fixed since, from the open list

- **Deli Counter 0.177.0: parapets are wall slots.** 9148 still shipped
  324 grey parapet surfaces (260 on Empties, 64 on two real buildings).
  1,680 parapet slots across the library. Two consequences surfaced on the
  way:
  - the name check moved to whole centimetres, since millimetre-snapped
    tiles of one run differ by 1 mm;
  - `themed_tscn.py` joined the build-freshness sources.
- **Deli Counter 0.178.0 / Zoo 1.61.0: an Empty's door is shut.** A
  `wood_panel` leaf, set back 8 cm, proven by a real kit build before and
  after.

## Not chased

`ZOO_KIT_DIMS_MISMATCH` compares built modules with the index's `dims`, and
9148's index carried `"dims": null` for walls. A second instrument that
could not fire on this defect. Whether it can fire on any wall is unread.
