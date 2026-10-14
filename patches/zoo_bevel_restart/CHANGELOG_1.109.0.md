## [1.109.0] - a bevelled mesh is one mesh every build: each face restarts at its lowest vertex after the bevel

**Factory roadmap 247.** Cold runs 9294 and 9296 shipped the pharmacy's roof props as one GLB and 9295 as another,
from the same command and seed. Traced in the factory's `docs/findings/roofprops_bytes/`:
- **Where.** Cold run 9298's own command, replayed six times (`zoo_repro_probe.py --jobs`), built the roof props
  four ways, every difference in `SatelliteDish_metal_delco_1997`, one of the four 9294's and 9296's bytes. Every
  other Zoo job of 9298 built the same bytes three times over (39 of 40).
- **Which step.** `stage_runs.py` digests the dish's parts after every step of the build, in six fresh processes:
  - the pole, the arm and the feed are one mesh at every step;
  - the bowl, an `add_ellipsoid`, leaves `create_uvsphere` with its faces in an order that changes from process to
    process, the same faces from the same corners;
  - it leaves the bevel with the same faces starting at other corners. `bm_to_object`'s sort (1.103.0) orders faces
    by their corners, so it cannot undo where a face starts;
  - the bowl left four ways: its triangles in other orders and from other corners, its normals within 0.0044
    degrees of each other paired vertex by vertex (`normal_shift.py`). Bytes, not shading. **Refuted and kept:** a
    first reading that one build's normals were "values apart, max 1.67" compared each array as rows sorted alone,
    where a 1e-4 wobble swaps two near-equal rows and pairs different vertices.
- **Why its input cannot be fixed.** `shuffle_bevel.py`, in one process, laid the bowl's faces in six orders.
  Bevelled as laid, they made four to six meshes; sorted back into `in_one_order`'s order first, six in each of two
  processes. The bevel's choice of a start moves with more than the faces' order.
- **What does.** Restarted at their lowest vertex just after the bevel, the six were one mesh, the same one in two
  processes.

**What changes:**
- **`bevel_edges` restarts every face it leaves** at its lowest vertex (`start_at_lowest`), after `bmesh.ops.bevel`.
  A mesh with nothing bevelled -- built with `bevel=0.0`, or with no edge sharp enough -- is not touched.
- **`start_at_lowest` carries a face's corner data with its corners.** Since 1.103.0 it refused a bmesh carrying any,
  rather than lose it. But a turning part reaches the bevel carrying its UVMap and Pivot layers (`prim_mesh`).
  - Every loop layer is carried, of every kind this Blender's BMesh has (`_corner_layers`, read off the API rather
    than listed).
  - Each layer's value is read before the face is remade and written back to the corner on the same vertex.
- **Every bevelled model's bytes move, once.** The same vertices and faces; a face's triangles come from another
  corner where it now starts at its lowest vertex. Measured on cold run 9298's 40 Zoo jobs (`churn.py`, each job's outputs as 9298 built them on 1.108.0, against one 1.109.0 replay): 1,138 of the 1,866 files both carry have other bytes, in every one of the 40 jobs, where a 1.108.0 replay against the same outputs, the control, read 1, the dish's. In those GLBs the positions, colours and UVs are the same rows in another order, the triangles are other, and the normals lie within 0.013 degrees of 1.108.0's, paired vertex by vertex over 797,941 vertices (`normal_shift.py`; the control, 0). Not measured: how far a quad split across its other diagonal moves a surface that is not flat.
- **`tests/test_bevelled_faces_in_order.py`:** fails on 1.108.0 on its four checks of the fix -- `bevel_edges` restarts nothing, `start_at_lowest` raises, the bowl bevelled from six face orders makes six meshes, and its corner data is refused (`ValueError: start_at_lowest: the bmesh carries uv corner data`) -- while its control passes there: Blender's own bevel, handed the bowl in six orders, starts its faces more than one way. All 5 pass on 1.109.0, with `test_faces_in_order.py`'s other 12, in Blender 5.1.1. `test_faces_in_order.py`'s test of the refusal is
  retired with the refusal.
- **The replays:** `zoo_repro_probe.py --jobs` over cold run 9298's 40 Zoo jobs, three replays each: on 1.108.0, 39 of 40 built the same bytes every time, the pharmacy's roof props not (`census_1108.out.txt`); on 1.109.0, 40 of 40 (`census_1109.out.txt`). The pharmacy's roof props alone, six replays: four GLBs on 1.108.0, one on 1.109.0 (`replay6_1108.out.txt`, `replay6_1109.out.txt`).
- **The suite:** `python -m pytest -q tests`: 4,970 passed, 460 skipped, 1 xfailed in 5 min 36 s, where 1.108.0 passed 4,968 and skipped 458 -- the new file's 2 source checks pass, and its 3 Blender checks skip where the retired one did. Inside Blender 5.1.1: the two face-order files and `test_roller_grill.py`, whose turning part carries its Pivot layer through the bevel, 63 passed; the 20 files of Blender checks on pivots and on one file every build, run on copies of 1.108.0 and 1.109.0, 1,398 passed on both with the same 5 failures on both, `test_club_bpy.py`'s golden digests, stale before this change and filed apart.
