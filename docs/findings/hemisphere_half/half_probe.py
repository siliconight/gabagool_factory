"""Which half does Zoo's geometry.add_hemisphere keep, and is every vertex it leaves scaled?

Run inside Blender, naming a Zoo root:

    blender -b --python docs/findings/hemisphere_half/half_probe.py -- <zoo root>

For each ring count it builds one hemisphere at the origin with radii (0.5, 0.5, 0.3) and prints,
in Blender's frame (Z up, metres): the z range of the vertices the helper RETURNS, the z range and
the largest horizontal radius of EVERY vertex left in the bmesh, how many vertices sit outside the
requested radii, and the mean face normal z. `segments` 14 asks for 7 rings, an odd count, so no
ring lies on the cut plane and the bisect makes new vertices there. It prints what it measured
and stops.
"""
import math
import sys

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
sys.path.insert(0, argv[0] if argv else ".")

import bmesh  # noqa: E402

from zoo_keeper.bpylayer import geometry  # noqa: E402

RX, RZ = 0.5, 0.3
print("[half] root %s" % (argv[0] if argv else "."))
for seg in (10, 12, 14, 20):
    bm = bmesh.new()
    ret = geometry.add_hemisphere(bm, (0.0, 0.0, 0.0), RX, RX, RZ, segments=seg)
    rz = [v.co.z for v in ret]
    az = [v.co.z for v in bm.verts]
    rad = [math.hypot(v.co.x, v.co.y) for v in bm.verts]
    out = sum(1 for v in bm.verts
              if math.hypot(v.co.x, v.co.y) > RX + 1e-6 or abs(v.co.z) > RZ + 1e-6)
    bm.normal_update()
    nz = sum(f.normal.z for f in bm.faces) / max(1, len(bm.faces))
    print("[half] segments %2d rings %2d: returned %3d verts z %+.4f .. %+.4f | bmesh %3d verts "
          "z %+.4f .. %+.4f, max radius %.4f, outside the radii %d | faces %3d, mean normal z %+.3f"
          % (seg, max(6, seg // 2), len(ret), min(rz), max(rz), len(az), min(az), max(az),
             max(rad), out, len(bm.faces), nz))
    bm.free()
