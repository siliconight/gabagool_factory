"""Which half does zoo's geometry.add_hemisphere keep? Run inside Blender:

    blender -b --python docs/cold_runs/cold_9239/hemisphere_probe.py -- <zoo repo root>

Builds one hemisphere at the origin with radii (1, 1, 1) and prints the z range of the vertices it
returns and of every vertex left in the bmesh, and the mean face normal z. Its docstring says
"Upper hemisphere shell (open bottom)". It prints what it measured and stops.
"""
import sys

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
sys.path.insert(0, argv[0] if argv else ".")

import bmesh  # noqa: E402

from zoo_keeper.bpylayer import geometry  # noqa: E402

bm = bmesh.new()
ret = geometry.add_hemisphere(bm, (0.0, 0.0, 0.0), 1.0, 1.0, 1.0, segments=20)
zs = [v.co.z for v in ret]
allz = [v.co.z for v in bm.verts]
bm.normal_update()
nz = sum(f.normal.z for f in bm.faces) / max(1, len(bm.faces))
print("[hemi] returned verts %d, z %.4f .. %.4f" % (len(zs), min(zs), max(zs)))
print("[hemi] bmesh verts %d, z %.4f .. %.4f; faces %d, mean face normal z %+.4f"
      % (len(allz), min(allz), max(allz), len(bm.faces), nz))
bm.free()
