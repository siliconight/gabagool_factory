"""The parked cars of one package: each car module's visual surfaces (glTF primitives off its collision mesh) and
materials, how many `cover_N` instances the site places of it, and the sum -- the cars' submissions with every car
in view. Prints what it counted and stops.

    python docs/findings/car_wear_44/car_surfaces.py <package dir>
"""
import json, re, struct, sys, os
pkg = sys.argv[1]
site = open(os.path.join(pkg, "site.tscn"), encoding="utf-8").read()
ids = {i: p for p, i in re.findall(r'\[ext_resource type="PackedScene" path="(cover/prop_simple_car_[^"]+\.glb)" id="([^"]+)"\]', site)}
counts = {}
for m in re.finditer(r'\[node name="cover_\d+" parent="\." instance=ExtResource\("([^"]+)"\)\]', site):
    if m.group(1) in ids:
        counts[ids[m.group(1)]] = counts.get(ids[m.group(1)], 0) + 1
total, rows = 0, []
for path in sorted(counts):
    raw = open(os.path.join(pkg, path), "rb").read()
    n = struct.unpack_from("<I", raw, 12)[0]
    g = json.loads(raw[20:20 + n])
    surf = sum(len(me["primitives"]) for me in g["meshes"] if not me.get("name", "").endswith("-colonly"))
    mats = sorted(m.get("name", "") for m in g.get("materials", []))
    total += surf * counts[path]
    rows.append((os.path.basename(path)[16:-4], counts[path], surf, ", ".join(x.replace("M_Car_", "").replace("M_Skin_", "") for x in mats)))
for r in rows:
    print("%-32s x%-2d %d surfaces  [%s]" % r)
print("instances %d, surfaces with every car in view %d" % (sum(counts.values()), total))
