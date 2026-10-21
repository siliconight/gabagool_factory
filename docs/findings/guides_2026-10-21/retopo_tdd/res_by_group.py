"""Read-only: per package group, StandardMaterial3D vertex_color_use_as_albedo
and ArrayMesh surface-format flags (COLOR, TEX_UV2), via rsrc_read.load.
Godot 4 ArrayFormat: ARRAY_FORMAT_COLOR = 1 << 3, ARRAY_FORMAT_TEX_UV2 = 1 << 5.
"""
import collections
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rsrc_read as rr  # noqa: E402

root = sys.argv[1]
by = collections.defaultdict(collections.Counter)
names = collections.defaultdict(list)
for dp, dn, fns in os.walk(root):
    dn[:] = [d for d in dn if d != ".godot"]
    for fn in fns:
        if not fn.endswith(".res"):
            continue
        p = os.path.join(dp, fn)
        rel = os.path.relpath(p, root).replace(os.sep, "/")
        g = rel.split("/")[0] if not rel.startswith("lot/") else "lot/merged"
        info = rr.load(p)
        for t, pth, props in info["res"]:
            if t == "StandardMaterial3D":
                v = props.get("vertex_color_use_as_albedo", False)
                by[g]["vcol=%s" % v] += 1
                if g in ("backdrop", "dressing"):
                    names[g].append((fn, props.get("resource_name"), v))
            if t == "ArrayMesh":
                fmts = [s.get("format") or 0 for s in props.get("_surfaces", [])]
                by[g]["mesh_color=%s" % any(f & (1 << 3) for f in fmts)] += 1
                by[g]["mesh_uv2=%s" % any(f & (1 << 5) for f in fmts)] += 1
for g in sorted(by):
    print(g, dict(by[g]))
for g in names:
    for row in names[g]:
        print("  ", g, row)
