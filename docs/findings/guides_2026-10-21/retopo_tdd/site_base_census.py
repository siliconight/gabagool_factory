"""Read-only: what a Deli Counter base GLB (site_base.glb) carries.

Per mesh-name family (prefix up to the first digit/underscore group): meshes,
meshes referenced by a node (drawn) vs orphans, triangles. For slab meshes:
triangle count per mesh -- an uncut box slab is 12 triangles, so >12 marks a
boolean-cut or tiled-and-cut slab. Collision nodes (-col / -colonly /
-convcolonly suffixes) are reported apart. Prints only.
"""
import json
import re
import struct
import sys
from collections import Counter, defaultdict

for path in sys.argv[1:]:
    data = open(path, "rb").read()
    clen = struct.unpack_from("<I", data, 12)[0]
    gj = json.loads(data[20:20 + clen].decode("utf-8"))
    acc = gj["accessors"]
    meshes = gj.get("meshes", [])
    nodes = gj.get("nodes", [])
    ref = Counter()
    col_ref = Counter()
    for n in nodes:
        if "mesh" in n:
            nm = n.get("name", "")
            if re.search(r"-(col|colonly|convcolonly)$", nm) or nm.endswith(("-col", "-colonly", "-convcolonly")):
                col_ref[n["mesh"]] += 1
            else:
                ref[n["mesh"]] += 1
    fam = defaultdict(lambda: [0, 0, 0, 0, 0])  # meshes, drawn, orphan, tris_drawn, col_only
    slab_tris = []
    for i, m in enumerate(meshes):
        name = m.get("name", "?")
        f = re.match(r"[A-Za-z]+", name)
        f = f.group(0) if f else "?"
        t = 0
        for p in m["primitives"]:
            t += acc[p["indices"]]["count"] // 3 if "indices" in p else acc[p["attributes"]["POSITION"]]["count"] // 3
        F = fam[f]
        F[0] += 1
        if ref[i]:
            F[1] += 1
            F[3] += t * ref[i]
        elif col_ref[i]:
            F[4] += 1
        else:
            F[2] += 1
        if name.startswith("slab_") and "col" not in name:
            slab_tris.append((t, name, ref[i]))
    print("==", path)
    print("  nodes %d  meshes %d" % (len(nodes), len(meshes)))
    for f in sorted(fam, key=lambda k: -fam[k][0]):
        a = fam[f]
        print("  %-14s meshes %4d  drawn %4d  orphan %4d  collision-only %4d  tris(drawn, x refs) %6d" % (f, a[0], a[1], a[2], a[4], a[3]))
    st = Counter(t for t, _, _ in slab_tris)
    print("  visual slab meshes by triangle count:", dict(sorted(st.items())))
    for t, n, r in sorted(slab_tris, reverse=True)[:6]:
        print("     %4d tris  %s  (node refs %d)" % (t, n, r))
