## [1.66.0] - a painted pane shows its picture on both faces

Cold run 9151 shipped the painted windows (1.64.0, 1.65.0). They import
with emission and bind to Lux. But from the street every pane read as flat
beige and none glowed.

Measured by the factory root's `patches/lf_empties/pane_face_probe.gd` on
9151's walk copy, on the Empty at x 1.55:
- the face carrying the atlas cell has world normal (0, 0, +1), into the
  house;
- the face toward the street carries the frame point.

`_arch.build_slab` mapped the cell onto the pane's local +Y face on the
assumption "+Y is outdoors". That holds for a wall module through its
placement; for these windows as placed it does not.

Both big faces now carry the cell, so the answer no longer depends on how a
module is turned. Each face reads unmirrored from its own side: looking
along ``d`` with up +Z the viewer's right is ``d x up`` -- -X from the +Y
side, +X from the -Y side -- and ``u`` runs toward it on both. The thin
edges take frame paint.

The mapping is a pure function, `window_panes.face_uv`, with `frame_uv`, so
it is tested without Blender; `_arch` calls it per corner. The material, the
atlas, the states and the module names are unchanged.

`tests/test_window_panes.py`:
- both big faces carry the cell and the edges take frame paint, which is
  painted where the frame UV points (fails on 1.65.0: no `face_uv`; the
  behaviour it pins is the defect 9151 measured);
- each face reads unmirrored from its own side, and up is up on both.
