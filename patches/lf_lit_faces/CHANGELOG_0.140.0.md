## [0.140.0] - A lit face keeps its own UVs on a kit module

Zoo 1.64.0 painted the Empties' window panes into one atlas, and the pane's
UVs choose its cell. Cold runs 9151 and 9152 showed every pane, from the
street, as flat frame-paint beige with no glow.

Two defects were behind that, measured one after the other:
- **9151:** the cell sat on the face pointing into the house
  (`patches/lf_empties/pane_face_probe.gd`). Zoo 1.66.0 painted both faces,
  and 9152's probe confirmed the street side then carried its cell.
- **9152:** the panes still looked the same, and the material showed why. Read
  headless on the walk copy (`patches/lf_empties/pane_census.gd`), it
  imported with `uv1_triplanar true, uv1_world_triplanar true, uv1_scale
  0.1856`. `_apply` world-projects every material on a kit module, so the
  atlas was sampled by world position, the mesh's UVs were ignored, and what
  showed was mostly frame paint.

`_apply` was right for every kit material until then -- each was a tiling
skin (brick, siding, drywall) -- and the pane is the first whose picture is
its UVs.

A material named with one of `LIT_FACE_SUFFIXES` -- `_Lens`, `_Diffuser`,
`_Face`, Lux's emissive-binder contract and the same list as
`lux_emissive_binder.gd` SUFFIXES -- is now never world-projected. The
report line counts it: "`N lit face(s) left on their own UVs`". A lit face is
artwork by definition, the binder already names them this way, and one list
read by two consumers cannot disagree about which materials are lit faces.

`tests/unit/test_worldskin_lit_faces.py` (real Godot import):
- a painted pane keeps its UVs while the brick beside it is still
  world-projected (fails on 0.139.0);
- the control: a module with no lit face is projected as before;
- the suffixes are Lux's binder's.

`glb_import_fixture.build_glb` gains `spread_uv`, opt-in: with every corner
on one UV, `_uv_density` read 0 and no fixture could reach the projection at
all.
