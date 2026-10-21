"""Read-only GLB census: parses the JSON chunk of every .glb under a root.

Reports per folder group: materials with doubleSided true / false / absent,
alphaMode, mesh/primitive counts, attribute sets, triangle counts from the
index accessors, how many nodes reference each mesh (reuse), extensions used.
Writes nothing except stdout (and an optional JSON dump path in argv[2]).
"""
import json
import os
import struct
import sys
from collections import Counter, defaultdict

ROOT = sys.argv[1]
DUMP = sys.argv[2] if len(sys.argv) > 2 else None


def read_glb_json(path):
    with open(path, "rb") as f:
        head = f.read(12)
        magic, version, length = struct.unpack("<4sII", head)
        if magic != b"glTF":
            raise ValueError("not a GLB: %r" % magic)
        clen, ctype = struct.unpack("<II", f.read(8))
        if ctype != 0x4E4F534A:
            raise ValueError("first chunk not JSON")
        return json.loads(f.read(clen).decode("utf-8")), length


def group_of(rel):
    parts = rel.replace("\\", "/").split("/")
    if parts[0] == "lot":
        if len(parts) >= 4 and parts[2] == "art":
            return "lot/*/art/" + parts[3]
        return "lot/*/(building glb)"
    return parts[0] if len(parts) > 1 else "(root)"


groups = defaultdict(lambda: {
    "files": 0, "bytes": 0,
    "mat_total": 0, "ds_true": 0, "ds_false": 0, "ds_absent": 0,
    "alpha": Counter(), "ds_true_by_alpha": Counter(),
    "meshes": 0, "prims": 0, "nodes_with_mesh": 0, "tris": 0,
    "attrsets": Counter(), "ext_used": Counter(), "generators": Counter(),
    "mesh_ref_hist": Counter(), "prims_per_mesh": Counter(),
    "ds_true_names": Counter(), "ds_absent_names": Counter(),
    "mat_names": Counter(), "files_list": [],
})
per_file = []

for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d != ".godot"]
    for fn in filenames:
        if not fn.lower().endswith(".glb"):
            continue
        path = os.path.join(dirpath, fn)
        rel = os.path.relpath(path, ROOT)
        g = group_of(rel)
        try:
            gj, length = read_glb_json(path)
        except Exception as e:  # noqa
            print("UNREADABLE", rel, e)
            continue
        G = groups[g]
        G["files"] += 1
        G["bytes"] += os.path.getsize(path)
        G["files_list"].append(rel)
        G["generators"][gj.get("asset", {}).get("generator", "?")] += 1
        for e in gj.get("extensionsUsed", []):
            G["ext_used"][e] += 1
        mats = gj.get("materials", [])
        fd = {"rel": rel, "group": g, "materials": len(mats), "ds_true": 0,
              "ds_false": 0, "ds_absent": 0, "meshes": len(gj.get("meshes", [])),
              "prims": 0, "tris": 0, "nodes_with_mesh": 0, "max_mesh_refs": 0,
              "alpha": Counter(), "mats": []}
        for m in mats:
            G["mat_total"] += 1
            am = m.get("alphaMode", "OPAQUE")
            G["alpha"][am] += 1
            fd["alpha"][am] += 1
            nm = m.get("name", "?")
            G["mat_names"][nm] += 1
            if "doubleSided" not in m:
                G["ds_absent"] += 1
                fd["ds_absent"] += 1
                G["ds_absent_names"][nm] += 1
                ds = None
            elif m["doubleSided"]:
                G["ds_true"] += 1
                fd["ds_true"] += 1
                G["ds_true_by_alpha"][am] += 1
                G["ds_true_names"][nm] += 1
                ds = True
            else:
                G["ds_false"] += 1
                fd["ds_false"] += 1
                ds = False
            fd["mats"].append((nm, ds, am))
        accessors = gj.get("accessors", [])
        for mesh in gj.get("meshes", []):
            G["meshes"] += 1
            prims = mesh.get("primitives", [])
            G["prims_per_mesh"][len(prims)] += 1
            for p in prims:
                G["prims"] += 1
                fd["prims"] += 1
                G["attrsets"][",".join(sorted(p.get("attributes", {}).keys()))] += 1
                mode = p.get("mode", 4)
                if "indices" in p:
                    n = accessors[p["indices"]]["count"]
                else:
                    n = accessors[p["attributes"]["POSITION"]]["count"]
                if mode == 4:
                    G["tris"] += n // 3
                    fd["tris"] += n // 3
        refs = Counter()
        for node in gj.get("nodes", []):
            if "mesh" in node:
                refs[node["mesh"]] += 1
                G["nodes_with_mesh"] += 1
                fd["nodes_with_mesh"] += 1
        for mi, c in refs.items():
            G["mesh_ref_hist"][c] += 1
        fd["max_mesh_refs"] = max(refs.values()) if refs else 0
        per_file.append(fd)

print("ROOT", ROOT)
tot = Counter()
for g in sorted(groups):
    G = groups[g]
    print("\n== %s  files=%d  bytes=%d" % (g, G["files"], G["bytes"]))
    print("  materials=%d  doubleSided true=%d false=%d absent=%d" % (
        G["mat_total"], G["ds_true"], G["ds_false"], G["ds_absent"]))
    print("  alphaMode:", dict(G["alpha"]), " ds_true by alpha:", dict(G["ds_true_by_alpha"]))
    print("  meshes=%d prims=%d nodes_with_mesh=%d tris(index/3)=%d" % (
        G["meshes"], G["prims"], G["nodes_with_mesh"], G["tris"]))
    print("  prims_per_mesh hist:", dict(sorted(G["prims_per_mesh"].items())))
    print("  nodes-per-mesh hist (within file):", dict(sorted(G["mesh_ref_hist"].items())))
    print("  attribute sets:", dict(G["attrsets"].most_common(8)))
    print("  extensionsUsed:", dict(G["ext_used"]))
    print("  generators:", dict(G["generators"]))
    print("  ds_true material names (top 12):", G["ds_true_names"].most_common(12))
    print("  ds_absent material names (top 12):", G["ds_absent_names"].most_common(12))
    for k in ("mat_total", "ds_true", "ds_false", "ds_absent", "meshes", "prims", "tris", "files"):
        tot[k] += G[k]
print("\nTOTAL", dict(tot))

if DUMP:
    with open(DUMP, "w", encoding="utf-8") as f:
        json.dump({"per_file": [dict(d, alpha=dict(d["alpha"])) for d in per_file]}, f, indent=1)
