"""Read-only: per MultiMesh sub_resource in a .tscn, instance count, the
extent of instance ORIGINS (frame: the scene's local space, metres), and any
custom_aabb / use_colors / use_custom_data; per MultiMeshInstance3D node, its
cast_shadow / visibility_range / gi_mode / transform. Prints only.

Godot 4 MultiMesh TRANSFORM_3D buffer: 12 floats per instance, rows of a
3x4 matrix, origin at indices 3, 7, 11 (then colour 4 floats if use_colors,
custom data 4 floats if use_custom_data).
"""
import re
import sys

path = sys.argv[1]
text = open(path, encoding="utf-8").read()
blocks = re.split(r"\n(?=\[)", text)
mm = {}
nodes = []
for b in blocks:
    head = b.split("\n", 1)[0]
    m = re.match(r'\[sub_resource type="MultiMesh" id="([^"]+)"', head)
    if m:
        d = {"id": m.group(1)}
        for key in ("instance_count", "transform_format", "use_colors", "use_custom_data",
                    "custom_aabb", "visible_instance_count"):
            mm_ = re.search(r"^%s = (.*)$" % key, b, re.M)
            d[key] = mm_.group(1) if mm_ else None
        mesh = re.search(r"^mesh = (.*)$", b, re.M)
        d["mesh"] = mesh.group(1) if mesh else None
        buf = re.search(r"^buffer = PackedFloat32Array\((.*)\)$", b, re.M)
        if buf:
            vals = [float(x) for x in buf.group(1).split(",") if x.strip()]
            stride = 12 + (4 if d["use_colors"] == "true" else 0) + (4 if d["use_custom_data"] == "true" else 0)
            n = len(vals) // stride
            xs = [vals[i * stride + 3] for i in range(n)]
            ys = [vals[i * stride + 7] for i in range(n)]
            zs = [vals[i * stride + 11] for i in range(n)]
            d["n_from_buffer"] = n
            d["stride"] = stride
            d["extent_xyz"] = (round(max(xs) - min(xs), 1), round(max(ys) - min(ys), 1), round(max(zs) - min(zs), 1))
            d["min_xyz"] = (round(min(xs), 1), round(min(ys), 1), round(min(zs), 1))
        mm[d["id"]] = d
        continue
    m = re.match(r'\[node name="([^"]+)" type="(MultiMeshInstance3D|MeshInstance3D)"', head)
    if m:
        d = {"name": m.group(1), "type": m.group(2)}
        for key in ("multimesh", "mesh", "cast_shadow", "visibility_range_end", "visibility_range_begin",
                    "gi_mode", "transform", "lod_bias", "custom_aabb"):
            mm_ = re.search(r"^%s = (.*)$" % key, b, re.M)
            d[key] = mm_.group(1) if mm_ else None
        nodes.append(d)

print("MultiMesh resources:", len(mm))
for k, d in mm.items():
    print(" ", k, "count", d["instance_count"], "buf_n", d.get("n_from_buffer"), "stride", d.get("stride"),
          "origin extent xyz m", d.get("extent_xyz"), "min", d.get("min_xyz"),
          "custom_aabb", d["custom_aabb"], "colors", d["use_colors"], "custom", d["use_custom_data"],
          "mesh", d["mesh"])
print("Nodes:", len(nodes))
for d in nodes:
    print(" ", d["type"], d["name"], "cast_shadow", d["cast_shadow"], "vr_end", d["visibility_range_end"],
          "gi_mode", d["gi_mode"], "custom_aabb", d["custom_aabb"],
          "xf", (d["transform"] or "")[:60])
