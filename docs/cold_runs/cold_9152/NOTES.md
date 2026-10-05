# Cold run 9152 -- 0 interventions; the pane faces fixed, and the panes still beige

gas_block_001, seed 9080, `empties: "across"`, `--bake-lights`.

**Stack:** Zoo 1.66.0, which paints each pane's picture on both faces.

**Result:** every leg ran, in 32.6 minutes, with `INTERVENTIONS: 0`. It was
the first run staged and driven by `tools/cold_drive/` -- batch id
`cold_9152`, correct this time. The repo copy of the sky wiring reported
its structural check.

## Measured

`patches/lf_empties/pane_face_probe.gd` on the walk copy, on the Empty at
x 1.55: the face toward the street, world normal (0, 0, -1), now carries the
atlas cell (9151: the frame point), and so does the face into the house.
The thin edges carry frame paint. Zoo 1.66.0 did what it said.

## And the frames did not change

From the street every pane still read as flat beige, with no glow at night --
the same as 9151. The probe and the frames disagreed, so one of them was
not measuring what was drawn.

`patches/lf_empties/pane_census.gd`, extended to read the material's
mapping, settled it. `M_Window_pane_Face` imported with
`uv1_triplanar true, uv1_world_triplanar true, uv1_scale 0.1856`:
- Level Factory's worldskin `_apply` world-projects every material on a kit
  module, and a window is a kit module;
- the atlas was sampled by world position and the mesh's UVs were ignored;
- the probe read UVs nothing used.

Both defects were real:
- the cell on the inward face, fixed by Zoo 1.66.0;
- the projection that discarded it either way, fixed by **Level Factory
  0.140.0**: a material named with a Lux lit-face suffix keeps its own UVs.

**Proven before a cold run:**
- A copy of this run's walk copy had its window modules re-imported with
  0.140.0's worldskin. All 36 reported "1 material(s) world-projected ...
  1 lit face(s) left on their own UVs".
- Its frames (`docs/findings/empties_windows_litfix/`) show the windows: lit
  in four colours behind sashes, blinds and shades, dark ones, bars, green
  shades.

That is a re-import, not a cold run; cold run 9153 carries 0.140.0.

## Seen while preparing the gutters, not fixed

`zoo_keeper/bpylayer/build.py` `build_dressing` leaves a building's covers
unmerged, citing Level Factory's `extract_meshes.gd` as merging them "per
visible chunk". It does not:
- `extract_meshes.gd` is the surface-clutter layer's (`dressing_layer.py`);
- the only Level Factory code that names `_dressing.glb` is the worldskin's
  tiling list;
- the 9147 census shows every `Dressing/Cover_*` as its own MeshInstance3D.

So each visible cover is a draw call. It bears on the gutters' price, and
on the queued per-material merge of the Empties.
