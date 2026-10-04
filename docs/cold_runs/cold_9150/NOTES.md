# Cold run 9150 -- 0 interventions; the Empties' open list closed in a level

gas_block_001, seed 9080, `empties: "across"`, `--bake-lights`.

**Stack:** Deli Counter 0.178.0, Zoo 1.63.0, Patina 0.24.0, Level Factory
0.139.0.

**Result:** every leg ran -- export, findings, walk -- with
`INTERVENTIONS: 0`, and the package exists. This is the re-run of 9149,
which stopped on millimetre-apart parapet tiles.

## Measured

- **Greybox surfaces: 0**, against 324 in 9148, all parapets. Parapets are
  dressed on every building, Empties and real.
- **No `STEM COLLISION`** in any job log.
- **The Empty's kit** (`gs_empty_rowhome_f`):
  - walls and windows `_h280` and `_h310`;
  - parapets `wall_..._w300_mbrick` and `w380_mbrick`;
  - both doorways carry `Doorway_Leaf`.
- **Side-wall panels, measured headless on the walk copy (9150's):** 3.10 m
  centred 1.55 and 4.65, and 2.80 m centred 7.60 -- 0 to 3.1 to 6.2 to 9.0
  with no gap. 9148 had 2.80 m panels in 3.10 m slots.

## Seen in the frames

`docs/findings/empties_rowhome_9150/`, the same five views, fill and night.

- **Fixed:**
  - the cornice reads as brick and stone, not a grey band;
  - the doors are shut;
  - the alley-side wall is continuous.
- **The doors are brown wood, not the navy `FACADE_DOOR_COLOR`.** With the
  theme's skin library loaded, `wood_panel` resolves to its pack texture and
  the fallback colour never applies. Per-house door colour therefore needs
  instance data over the skin, not a different constant.
- **At night the row is a dark mass** outside the streetlight pools: the
  windows are unlit recesses. That is the painted-pane item (lit, dark,
  blind, barred), still open.
