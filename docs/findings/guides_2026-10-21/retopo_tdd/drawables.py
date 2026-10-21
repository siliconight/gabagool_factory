"""Read-only: the drawable mesh nodes the mission tree would hold, by source.

Walks the scenes the entry reaches (bake.tscn -> presentation/lux.applied.tscn
-> lot/<b>/site.tscn; restaurant_row_001_dressing.tscn; site_backdrop.tscn),
and counts, per scene:
  * MeshInstance3D nodes whose mesh is a merged/extracted .res (no LODs, by
    rsrc decode), an .obj (Godot-imported), or inline (sub_resource);
  * GLB instances x the GLB's visual mesh nodes (each becomes one
    MeshInstance3D at import; import asks generate_lods=true);
  * MultiMeshInstance3D nodes.
Instanced .tscn are followed (one level per reference, recursively).
Static count from scene text; nothing is run. Prints only.
"""
import json
import os
import re
import struct
import sys
from collections import Counter

PKG = sys.argv[1]


def glb_visual_nodes(path):
    d = open(path, "rb").read()
    n = struct.unpack_from("<I", d, 12)[0]
    g = json.loads(d[20:20 + n])
    c = 0
    for node in g.get("nodes", []):
        if "mesh" in node and not re.search(r"-(col|colonly|convcolonly)$", node.get("name", "")):
            c += 1
    return c


total = Counter()


def scene(res_path, mult, depth=0):
    p = os.path.join(PKG, res_path.replace("res://", ""))
    t = open(p, encoding="utf-8").read()
    ext = {}
    for m in re.finditer(r'\[ext_resource type="([^"]+)"[^\]]*path="([^"]+)"[^\]]*id="([^"]+)"\]', t):
        ext[m.group(3)] = (m.group(1), m.group(2))
    blocks = re.split(r"\n(?=\[)", t)
    for b in blocks:
        h = b.split("\n", 1)[0]
        if not h.startswith("[node"):
            continue
        mi = re.search(r'instance=ExtResource\("([^"]+)"\)', h)
        if mi:
            typ, path = ext[mi.group(1)]
            if path.endswith(".glb"):
                total["glb_instance_mesh_nodes"] += mult * glb_visual_nodes(os.path.join(PKG, path.replace("res://", "")))
                total["glb_instances"] += mult
            elif path.endswith(".tscn"):
                scene(path, mult, depth + 1)
            else:
                total["other_instance:" + path.rsplit(".", 1)[-1]] += mult
            continue
        if 'type="MultiMeshInstance3D"' in h:
            total["multimesh_nodes"] += mult
            continue
        if 'type="MeshInstance3D"' in h:
            mm = re.search(r'\nmesh = (ExtResource|SubResource)\("([^"]+)"\)', b)
            if not mm:
                total["mesh_node_no_mesh"] += mult
            elif mm.group(1) == "SubResource":
                total["mesh_node_inline"] += mult
            else:
                path = ext[mm.group(2)][1]
                kind = "res" if path.endswith(".res") else path.rsplit(".", 1)[-1]
                total["mesh_node_" + kind] += mult


for entry in ("res://bake.tscn", "res://restaurant_row_001_dressing.tscn", "res://site_backdrop.tscn"):
    scene(entry, 1)
for k, v in sorted(total.items()):
    print("%-34s %6d" % (k, v))
