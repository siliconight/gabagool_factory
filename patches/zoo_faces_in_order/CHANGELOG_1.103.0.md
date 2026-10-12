## [1.103.0] - a mesh leaves with its faces in one order, the same every build

**Why.** Since Level Factory 0.192.0 two exports of one level bake the same
lightmap byte for byte, and two cold runs still did not: cold runs 9256 to
9259 packed the deli's lightmap three ways, each time because one dome glass
came out with a different chart in Godot's lightmap unwrap and 2,858 users
moved with it. Read down to the bytes, the deli's fixtures kit, built twice
from the same inputs, gave two GLBs whose every dome glass and pendant bulb
had the same vertices, normals, UVs and colours and its triangles in another
order, or some of them other triangles -- and the unwrap follows the
triangles. Three causes, each measured:

- **Blender's own operators lay faces in a process's order.** In four fresh
  Blender 5.1 processes, with no Zoo code, `bmesh.ops.create_uvsphere` laid
  its vertices in one order and its faces in two, and a sphere put through
  `bmesh.ops.bisect_plane` as `add_hemisphere` does came out with its faces
  in four orders -- the same faces every time, sorted (the factory's
  docs/findings/grader_speed/uvsphere_order_probe.py). The faces' order is
  what `bm.to_mesh` writes and the GLB's triangles follow.
- **An operator that makes a face starts it where it likes.** Across four
  builds of the kit, each dome's 20-cornered cap -- `holes_fill` closing the
  rim -- started at one of two neighbouring corners, dome by dome, with its
  rim given in one order or not (blend_mesh_dump.py on each build's .blend).
  A GLB triangulates a face from its first corner.
- **`add_hemisphere` handed its bisect a set.** `list(set(geom))`, BMesh
  elements, which iterate in the order of their addresses.

**What changed.**

- `in_one_order(bm, elems)`: BMesh elements sorted by kind, then by their
  vertices' indices. `add_hemisphere` hands its bisect its geometry so, the
  dome's rim and the fracture's cut are handed to their operators so.
- `start_at_lowest(bm, faces)`: each face remade to start at its
  lowest-index vertex, its winding and material kept; refused on a bmesh
  that already carries corner data, rather than lose it. The dome's cap,
  every face `fracture`'s `contextual_create` makes, and every face of a
  hemisphere after its bisect (a sphere's quads are flat, so only the order
  of its triangles changes) are started so.
- `bm_to_object` sorts the faces by their vertices before it writes the
  mesh: the vertices' order holds, so the faces leave in one order every
  build.

The faces, their corners and their windings are the ones the recipes made;
what changes is their order in the mesh, and where a filled or split face
starts. So
every Zoo model's bytes change once, and with them how Godot unwraps their
lightmap charts -- not their shapes.

**Measured:** cold run 9259's 38 Zoo jobs each replayed twice from its own command (the factory's docs/findings/grader_speed/zoo_repro_probe.py --jobs): on 1.102.0 seven built different bytes -- the deli's and the office's fixtures, the deli's and the pharmacy's roof props, a rowhome's dressing, the site kit's trash bags and the clutter's pebble (zoo_repro_probe.jobs_before.out.txt); on 1.103.0 all 38 built the same bytes both times, every output but the .blend (zoo_repro_probe.jobs_after.out.txt); the deli's fixtures built four times, one GLB (zoo_repro_probe.after.out.txt), where 1.102.0's two builds differed in every dome glass and pendant bulb (zoo_repro_probe.before.out.txt)

**Tests:** `tests/test_faces_in_order.py`, thirteen: the faces sorted after
`in_one_order` reads them and before the mesh is written; the hemisphere's
bisect given no set, and its faces started at the lowest vertex after it; the
dome's rim and the fracture's cut given in one order and their faces started
so; and in Blender every hemisphere face starting at its lowest vertex at an
odd and an even ring count, an ellipsoid and a hemisphere each leaving
`bm_to_object` with its faces sorted and with the faces it made, a face
remade to start at its lowest vertex with its winding and material, the
refusal with corner data present, and `in_one_order` one order whatever it is
given. Eleven fail on 1.102.0; the two faces-made tests are guards.
In Blender 5.1.1 the new file with tests/test_hemisphere.py, 24 passed; on 1.102.0 the new file's eleven failed and its two guards passed. 4,172 passed, 447 skipped, 1 xfailed in 5 min 43 s, where 1.102.0 passed 4,168 (the new file's four source tests run outside Blender, its nine Blender tests skip there)
