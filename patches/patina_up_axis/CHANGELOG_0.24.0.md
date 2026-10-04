## [0.24.0] - which way is up is read off the file

### Fixed
- **A building taller than it is wide was dressed on its side.**
  `slots.detect_up_axis` took the axis with the smallest extent as up,
  reasoning that "a building is wide and shallow". Deli Counter 0.174.0's
  rowhome Empties are 6.3 m wide, 6.8-10.1 m tall and 12.3 m deep, so up
  read as **X** for all six. The three real buildings in the same level
  read Y.

  Every height-dependent pass then ran on the wrong axis: grime, banding and
  the anchors. In cold run 9147 every `ground_edge` and `wall_base` anchor
  on an Empty stood on its centre line (x = 0) at heights from 0 to 10 m, and
  `roofline` ran up a side wall. Built, that was curbs, base courses and
  gutters standing out of the walls at storey lines and diagonals -- the
  walker saw it in the frames and asked about the axes. Cold run 9146 (the
  0.174.0 shells) shows the same scatter, so it predates any change to the
  Empties since.

- **The rule now reads provenance first.** Blender's glTF exporter writes +Y
  up unless `export_yup=False`, and Deli Counter exports with the default
  (`deli_counter.py`, `bpy.ops.export_scene.gltf`).
  - `gltf_io.load_glb` sets `Scene.up_axis_hint`:
    - from `asset.extras.patina_up_axis` when Patina wrote the file;
    - else Y when `asset.generator` names `Khronos glTF Blender I/O`;
    - else None.
  - `save_glb` writes the hint into its output's `asset.extras`, because
    Patina replaces the generator string and would otherwise erase the
    evidence it read.
  - `detect_up_axis` returns the hint when there is one, and guesses from
    extents only when the file says nothing (the legacy `DeliCounter-fixture`
    shell, `tests/make_fixture.py`).
  - The run result names which it was: `up_axis_source`.

- **`version.py` said 0.22.0 through all of 0.23.0**, so 0.23.0's output was
  stamped `Patina 0.22.0`. It now matches `VERSION`.

`tests/test_up_axis_declared.py`. Against the real Empty shell (skipped
without a Deli Counter build beside this repo):
- it reads Y;
- the control: with the declaration stripped, the guess answers X;
- Patina's own output carries Y forward;
- end to end, the command Level Factory runs for an Empty puts every ground
  and wall-base anchor at the foot of a wall and spread along it.

And against the legacy fixture: a file that says nothing is still guessed,
Z.
