"""Where a shipped site scene's submissions come from: its meshes, materials and scene instances by owner.

    python tools/draw_census.py <package dir or site.tscn> [...]

Reads each package's `site.tscn` (the level's own ground, streets and furniture; the buildings'
scenes are instanced into it) and counts, by the owner its sub-resource ids name, the BoxMesh and
other mesh resources (`BoxMesh_mark_*` a marking, `BoxMesh_road_*` a slab, `BoxMesh_sidewalk_*`,
`BoxMesh_Ground_*`, `BoxMesh_frontage_*`, `BoxMesh_path_*`), the materials the same way, the
MeshInstance3D and MultiMeshInstance3D nodes, and the scene instances by name prefix (`cover`,
`blocker`, `hung`, `b`). A mesh node is one submission a frame when it is in view, so these
counts are the pool a heading draws from, not a heading's draws (the perf harness measures
those). Several packages print side by side so a street form or a tool release can be attributed.
It prints what it counted and stops.
"""
import collections
import os
import re
import sys


def census(path):
    text = open(path, encoding="utf-8").read()
    out = {"meshes": collections.Counter(), "materials": collections.Counter(),
           "nodes": collections.Counter(), "instances": collections.Counter()}
    for typ, rid in re.findall(r'^\[sub_resource type="([A-Za-z0-9]+)" id="([^"]+)"', text, re.M):
        owner = re.sub(r"[_-]?\d+.*$", "", rid.split("_", 1)[1] if "_" in rid else rid)
        if typ.endswith("Mesh"):
            out["meshes"][(typ, owner)] += 1
        elif typ.endswith("Material3D"):
            out["materials"][(typ, owner)] += 1
    for name, typ, instance in re.findall(
            r'^\[node name="([^"]+)"(?: type="([^"]+)")?[^\n]*?(instance=ExtResource)?', text, re.M):
        if typ in ("MeshInstance3D", "MultiMeshInstance3D"):
            out["nodes"][typ] += 1
        elif instance:
            out["instances"][re.sub(r"[_-]?\d+$", "", name)] += 1
    return out


def main(argv):
    paths = [p if p.endswith(".tscn") else os.path.join(p, "site.tscn") for p in argv]
    results = [(os.path.basename(os.path.dirname(os.path.abspath(p))) if p.endswith("site.tscn") else p,
                census(p)) for p in paths]
    for section in ("meshes", "materials", "nodes", "instances"):
        keys = sorted(set(k for _n, r in results for k in r[section]),
                      key=lambda k: -max(r[section].get(k, 0) for _n, r in results))
        print("== %s" % section)
        head = "%-42s" % "owner" + "".join("%12s" % n[-12:] for n, _r in results)
        print(head)
        for k in keys:
            label = " ".join(k) if isinstance(k, tuple) else k
            print("%-42s" % label[:42] + "".join("%12d" % r[section].get(k, 0) for _n, r in results))
        print("%-42s" % "total" + "".join("%12d" % sum(r[section].values()) for _n, r in results))


if __name__ == "__main__":
    main(sys.argv[1:])
