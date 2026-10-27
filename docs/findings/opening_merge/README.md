# An opening's surround, merged with its wall: the walker's seams (L5-L7)

The walker, walking seed 9205 on 2026-10-26 (`docs/findings/walk_2026-10-26_panel/`):
- L5: "lot of seams visible on these doors in the supermarket" (supermarket_a01, `int_0_0_open1`);
- L6: "highly visible seams and pieces here...breach?" (deli_a01, breach panels);
- L7: "not consistent: textures" (deli_a01, a window).

Level Factory's buildings merge (`assets/godot/merge_buildings.gd`) merges a building's static modules per room cell
and material. Until 0.258.0 it left every `*_open<n>` slot whole, because "a window's pane may be glass, which Godot
sorts per mesh". So each opening module kept its own mesh, its own lightmap chart and its own shade beside a merged
wall.

The change, on the clone `_scratch/lf_openmerge` (Level Factory 0.258.0, not yet shipped):
- an opening merges with its unit;
- its transparent surfaces go into one mesh of their own where they stood (`GlassR_<n>`);
- a slot carrying `interactive_id` still stays whole.

## What it merged on the walker's level (`merge_buildings.json`, both arms)

The arms are the pricing workspace `_scratch/price_sm/ws_subject` (Level Factory 0.257.0) and its copy `ws_merge`
(the clone).

| building | slots merged | glass surfaces -> own meshes | `*_open` slots merged |
|---|---|---|---|
| deli_a01 | 523 -> 531 | 10 -> 10 | ext_0_E_open0, ext_0_E_open1, ext_0_N_open0, ext_0_S_open1, ext_1_E_open0, ext_1_N_open0, ext_1_S_open0, ext_1_S_open1 |
| parking_garage | 191 -> 199 | 8 -> 8 | eight storey-1 windows |
| supermarket_a01 | 154 -> 156 | 5 -> 5 | ext_0_E_open0, ext_0_S_open1 |

## What it fixes, and what it does not

- **L7, the window, is fixed** (`01_deli_window_before_after.png`, shot at the walker's position -49.7, 1.6, -6.7,
  looking east).
  - Before: the window's wall panel is a lighter rectangle on the wall.
  - After: the same shade as the wall, a faint edge left.
- **L5 and L6 are not touched.** Every opening the walker flagged carries `interactive_id`, so it is kept whole:
  - the supermarket's `int_0_0_open1`;
  - the deli's `int_0_0_open1` (a breach panel, `breach_delco_1997_02_w140_mdrywall`);
  - its `ext_0_N_open1`, `ext_0_S_open2` and `ext_0_W_open0`.

  A door that opens, a panel that breaks and a window that breaks swap states, and the merge cannot carry a swap.
- **Refuted: "an interactive module is left out of the light bake."** `light_bake.json`'s `imports.baked` lists
  every `breach_*`, `*_breached` and `doorway_*` GLB of the three buildings; its `dynamic` list is two trees, two
  ATMs and two video-poker machines. The door and the panel are baked like the wall.
- **MEASURED: an unmerged module bakes at about twice the merged wall's lightmap density**
  (`lightmap_density_probe.gd`, `lightmap_density.out.txt`, on `ws_merge`'s walk copy). Each mesh's
  `lightmap_size_hint` was set against its own surface area:
  - the deli's breach panel `int_0_0_open1` (`Wall_drywall`): 12.2 texels/m;
  - the supermarket's door `int_0_0_open1` (`Doorway_drywall`): 16.1 texels/m;
  - the merged walls round them: 5.8-8.3 texels/m. The large merged meshes come out lowest, and some small merged
    pieces are denser.

  A surface lit at twice its neighbour's resolution, with its own chart edges, reads as a different surface. This
  is the lead for L5 and L6 and is not yet a fix.
- **Superseded by the measurement above: the shade difference of an unmerged module.** The level bakes into ONE 1024 x 1024 lightmap
  for 2,817 users (`light_bake.json` `result`). A small module's chart may pack at a different effective texel
  density from the merged wall's, a merged surface being unwrapped at `TEXEL_M` 0.2 by the merge. That would
  explain why sharing the wall's mesh fixes the window, and it is the next thing to measure for L5 and L6.

## L5 and L6: what they are not, and what is left (2026-10-26)

- **REFUTED: lightmap density.** `texel_arm.py` re-imported all 27 `breach_*` and `doorway_*` GLBs at
  `meshes/lightmap_texel_size` 0.45 (about the merged walls' density) and re-baked (`texel_arm_t045.out.txt`). At the
  walker's door and breach views the frames do not change: means 93.6 -> 93.9, 90.8 -> 90.3, 84.2 -> 84.7, and by
  eye the same seams. The density difference is real and is not the seam.
- **REFUTED: the texture restarting at the module.** `lightmap_density_probe.gd`'s material read: the breach panel,
  the doorway and the wall round them all wear `M_Skin_drywall_delco_1997`, `uv1_triplanar` and
  `uv1_world_triplanar` true, at one scale. The texture runs on across the joint in world space.
- **What is left is Zoo 1.126.0's own finding and its fix.**
  - The finding: a door or panel that changes state keeps its own mesh, lit from its own rect of the lightmap, and
    the two bakes disagree across the joint by -12 % / +13 % (Zoo's CHANGELOG, 1.126.0).
  - The fix: a CASING, a 0.09 m strip of the wall's own material standing 0.015 m proud at each end, full height.
    In the walker's frames those strips are the "seams" (the walk's L5 note: "full-height strips either side of the
    opening ... read as pilasters with their own lines").
  - So the joint is covered, and the cover reads as a line of its own.
- **Choices, for the walker:**
  - (a) Make the casing a real door and panel trim: a painted trim colour around the opening, a frame that reads
    as one on purpose.
  - (b) Bake the intact state with the wall: merge a panel's intact geometry with the wall and swap only on breach,
    which the merge cannot carry today.
  - (c) Remove the casing and accept the bake's 12 % step at the joint.

## The price

`price.py`, `price.out.txt`, `compare.out.txt`, `perf_*.json`: the control (`ws_subject`'s package) twice and the
subject (`ws_merge`'s) once, in one session, 53 headings at 14 stations.

| | draws, subject - controls' mean | p95 ms, subject - controls' mean |
|---|---|---|
| median | -1.0 | -0.015 |
| mean | -2.8 | -0.029 |
| range | -23 to 0 | -0.347 to +0.353 |
| the controls' own a - b | 0 everywhere | median -0.027, largest 0.690 |

- Worst heading: 2,209 draws in both controls -> 2,186; p95 10.92 / 10.92 -> 10.58 ms.
- The merge takes 18 opening surrounds into their walls' meshes and gives their 23 glass surfaces 23 meshes of their
  own: a few draws saved where a surround's mesh used to stand, frame time within the controls' spread, nothing
  added.
