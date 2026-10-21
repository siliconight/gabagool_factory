"""Read-only scan of Godot binary .res files for property-name strings.

A binary resource (RSRC) stores the names of NON-DEFAULT properties in its
string table, so the presence of b"cull_mode" means some embedded material set
cull_mode away from its default (CULL_BACK). Counts files containing each
token, and total occurrences. Prints only.
"""
import os
import sys
from collections import Counter

ROOT = sys.argv[1]
TOKENS = [b"RSRC", b"ArrayMesh", b"StandardMaterial3D", b"ORMMaterial3D",
          b"ShaderMaterial", b"cull_mode", b"lightmap_size_hint", b"shadow_mesh",
          b"lods", b"vertex_color_use_as_albedo", b"uv1_triplanar",
          b"transparency", b"ext_resource", b"res://", b"blend_shape",
          b"custom_aabb", b"surface_", b"albedo_texture"]
files = 0
has = Counter()
occ = Counter()
sizes = 0
examples = {}
for dp, dn, fns in os.walk(ROOT):
    dn[:] = [d for d in dn if d != ".godot"]
    for fn in fns:
        if not fn.endswith(".res"):
            continue
        p = os.path.join(dp, fn)
        b = open(p, "rb").read()
        files += 1
        sizes += len(b)
        for t in TOKENS:
            c = b.count(t)
            if c:
                has[t] += 1
                occ[t] += c
                examples.setdefault(t, os.path.relpath(p, ROOT))
print("files", files, "bytes", sizes)
for t in TOKENS:
    print("%-28s files_with=%5d  occurrences=%7d  e.g. %s" % (
        t.decode(), has[t], occ[t], examples.get(t, "")))
