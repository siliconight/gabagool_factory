"""Where deli_a03's stair guards stand, in site space: every collider node whose name starts `stair` in the package's
`lot/deli_a03/site_base.glb`, with its box (node translation plus the accessor's min and max), moved by the site's
building offset. A probe: prints what it measured and stops.

    python stair_guards_a03.py <package dir> [x0,z0,x1,z1]

Frame: Godot metres, site space (glTF y up; the GLB's z is Godot's z; the site places deli_a03 at x -51, z -2.51,
unturned -- `site.tscn` node b0). Only translation is applied: a node with a rotation or scale is flagged, not
transformed. The optional rectangle keeps boxes that overlap it.
"""
import os
import sys

from pygltflib import GLTF2

pkg = os.path.abspath(sys.argv[1])
rect = [float(v) for v in sys.argv[2].split(",")] if len(sys.argv) > 2 else None
BX, BZ = -51.0, -2.51
g = GLTF2().load(os.path.join(pkg, "lot", "deli_a03", "site_base.glb"))
rows = []
for nd in g.nodes:
    if not nd.name or not nd.name.startswith("stair") or nd.mesh is None:
        continue
    t = nd.translation or [0.0, 0.0, 0.0]
    flag = "" if not (nd.rotation and nd.rotation != [0, 0, 0, 1]) and not (nd.scale and nd.scale != [1, 1, 1]) \
        else "  (ROTATED OR SCALED: box not transformed)"
    lo = [float("inf")] * 3
    hi = [float("-inf")] * 3
    for prim in g.meshes[nd.mesh].primitives:
        a = g.accessors[prim.attributes.POSITION]
        lo = [min(lo[i], a.min[i]) for i in range(3)]
        hi = [max(hi[i], a.max[i]) for i in range(3)]
    x0, x1 = lo[0] + t[0] + BX, hi[0] + t[0] + BX
    y0, y1 = lo[1] + t[1], hi[1] + t[1]
    z0, z1 = lo[2] + t[2] + BZ, hi[2] + t[2] + BZ
    if rect and (x1 < rect[0] or x0 > rect[2] or z1 < rect[1] or z0 > rect[3]):
        continue
    rows.append((nd.name, x0, x1, y0, y1, z0, z1, flag))
for r in sorted(rows):
    print("%-44s x %8.3f .. %8.3f   y %6.3f .. %6.3f   z %8.3f .. %8.3f%s" % r)
print("%d stair nodes" % len(rows))
