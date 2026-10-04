# Cold run 9147 -- 0 interventions; two defects found in the frames

gas_block_001, seed 9080, `empties: "across"`, exported with `--bake-lights`.

**Stack:** Deli Counter 0.175.0 and Level Factory 0.138.0, the fix for 9146's
refused export.

**Result:** shell, art, export, findings and walk all ran. The driver reads
`INTERVENTIONS: 0`, and this time the package exists. The greybox gate
measured 0 slab surfaces (9146: 588), and each Empty carries a concrete
`roof_` module.

**The zero is traversal correctness only.** Two defects were found by looking
at the frames; no gate saw either one.

## Frames

`docs/findings/empties_rowhome_9147/`: five views, each shot twice --
`_fill` with the frame script's 0.6-energy directional fill, `_night` as a
player sees it.
- Script: `patches/lf_empties/make_empty_shots.py`, which places the cameras
  off the drawn spec's `blockers`.
- Shot from the walk copy. Its `glb_reference_scan.json` names
  `cold-9147-ws`.

## 1. Patina's dressing on the Empties stood on its side

The walker asked, looking at the frames: "i see some x, y, z axis mismatch
on some of the patina pieces? Do you see it?" Yes.

**The pieces.** A headless mesh census of the Empty at x 1.55
(`patches/lf_empties/empty_mesh_census.gd`) named them
`blocker_<n>/Dressing/Cover_curb`, `Cover_base_course` and
`Cover_gutter_run`. Each sat on the house's centre line, at heights from 0
to 10 m.

**At the source.** Patina's own orders for `gs_empty_rowhome_f`
(`space: spec/Blender Z-up raw coords`):
- `ground_edge` and `wall_base` at x = 0, z from 0.0 to 10.0;
- `roofline` running up a side wall.

On the same level's three real buildings, both kinds sit at z = 0.0 across
14-33 distinct x. Cold run 9146 (the 0.174.0 shells) shows the same scatter,
so this was not caused by 0.175.0.

**Cause, measured.** `slots.detect_up_axis`, run on the real files:
- **X** for all three rowhome Empties sampled (6.3 m wide, 6.8-10.1 m tall);
- **Y** for the gas station, the bank tower and the freight terminal.

The rule took the smallest extent as up ("a building is wide and
shallow").

**Fixed: Patina 0.24.0.** Up is read off the file:
- Patina's own declaration first, then Blender's exporter as the generator
  (+Y up);
- the guess only for a file that says nothing.

Re-running the gas station's dressing on 0.24.0 gives orders identical to
9147's (170 = 170), so real buildings did not move.

## 2. A dark band through every Empty at every storey line

This one was mine, from Deli Counter 0.175.0. It removed the Empties' floor
slabs, and `_cap_thick` still stopped each wall 0.3 m short of the storey
line.

**Measured on `gs_empty_rowhome_f.slots.json`:** walls 0-2.80, 3.10-5.90,
6.20-9.00. Nothing filled 2.80-3.10 or 5.90-6.20.

**Fixed: Deli Counter 0.175.2.** An Empty's walls run the full storey. The
rebuilt shell measures 0-3.10, 3.10-6.20 and 6.20-9.00, then the roof slab
9.00-9.30.

## Seen, not fixed

- **Parapets are skinned on no building.** 324 greybox surfaces remain,
  2,744.7 m² in `gb_wall`. All are `parapet_*`: 260 on the 26 Empties and
  64 on the bank tower and freight terminal.
  - The worldskin has no parapet pass.
  - The gate counts parapets and does not refuse them.
  - On a rowhome, the parapet is the cornice: a grey band along every top.
- **An Empty's doorway is an open frame** over solid collision (9146 notes).
  Visible in `empties_one_front_*`.

## Verified next

Cold run 9148 carries both fixes.
