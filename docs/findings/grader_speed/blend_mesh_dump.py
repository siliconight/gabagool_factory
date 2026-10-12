"""Dump meshes from a .blend, face by face, to compare two builds where a GLB comparison only says
"the same rows in another order". Run in Blender:

    blender --background <file.blend> --python blend_mesh_dump.py -- <name prefix> <out.json>

For every mesh object whose name starts with the prefix: its vertices (rounded to 1e-6), and for
each polygon in storage order its vertex indices from its first corner, its smooth flag, and its
loop start; the sharp edges by their vertex pairs. Measures and writes; names no cause.
"""
import json
import sys

import bpy

argv = sys.argv[sys.argv.index("--") + 1:]
prefix, out = argv[0], argv[1]
dump = {}
for obj in bpy.data.objects:
    if obj.type != "MESH" or not obj.name.startswith(prefix):
        continue
    me = obj.data
    sharp = me.attributes.get("sharp_edge")
    sharp_pairs = []
    if sharp is not None:
        for i, e in enumerate(me.edges):
            if sharp.data[i].value:
                sharp_pairs.append(sorted(e.vertices))
    smooth = [not p.use_smooth for p in me.polygons]
    dump[obj.name] = {
        "verts": [[round(c, 6) for c in v.co] for v in me.vertices],
        "polys": [list(p.vertices) for p in me.polygons],
        "loop_start": [p.loop_start for p in me.polygons],
        "flat": smooth,
        "sharp_edges": sorted(sharp_pairs),
    }
with open(out, "w", encoding="utf-8") as fh:
    json.dump(dump, fh)
print("BLEND_DUMP %d meshes -> %s" % (len(dump), out))
