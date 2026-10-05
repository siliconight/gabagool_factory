## [0.143.0] - The Empties, merged one mesh a side per material

Roadmap 182. The walker, 2026-10-04: finish the Empties, "then optimise them
for runtime".

An Empty reaches the package as one kit module instance per Deli Counter
slot: about 88 for a three-storey house, 95 MeshInstance3D and 161
surfaces, in 8 materials.
- **The ceiling:** hiding all 25 of cold run 9161's Empties saved 816
  draws and 1.87 ms at the median view, up to 3,951 and 11.6 ms.
- **The prototype** (`patches/lf_empties/merge_empties_proto.gd`) merged each
  one's modules one mesh a side per material. It saved 686 draws and
  0.88 ms on 9162's level, against controls that agreed to 0.03 ms.

**`packages/exporting/merge_empties.py` and `assets/godot/merge_empties.gd`**
do that in the export.
- **Which scenes:** `empty_scenes` names every `res://lot/<id>/site.tscn`
  that a `blocker_<n>` node of the site instances. A blocker instancing
  anything else refuses rather than being merged on a guess.
- **The Godot half,** on each of those scenes:
  - takes every slot child that names a side (`ext_<storey>_<facing>_*`,
    `parapet_<facing>_*`, `roof_*`) apart;
  - copies its colliders out whole;
  - appends every surface, in the scene's frame, to one group per (side,
    material name, uv1 flags, surface format).
  - Each group becomes one ArrayMesh wearing a duplicate of its material,
    unwrapped for its lightmap at Godot's 0.2 m import default, and saved
    as `lot/<id>/merged/<side>_<n>.res`.
  - The collision base and the covers are left as they are.
- **The Python half** believes the report, not the exit code. It needs the
  right schema and `ok`, a row for every scene asked, at least one merged
  mesh and fewer than the surfaces in, every merged mesh unwrapped, and a
  collider kept. Anything else raises `ExportMergeError` and the export
  fails.
- **Where:** after the occluder bake and before the light bake.
  - The occluders are measured on the modules and placed world-space in
    their own scene, so they stay true of the merged geometry.
  - The light bake's users are node paths, so the merged meshes must exist
    first.
  - Without Godot, the package keeps its per-module Empties: consistent,
    and merely slower.
- **The unit is one side of one Empty**, the largest thing that enters and
  leaves view as one. Never across Empties.
