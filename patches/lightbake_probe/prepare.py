"""Roadmap item 31, the light-bake probe, step 1: can this package's
geometry get a second UV set at all?

    python prepare.py <walk copy> <probe dir>

Copies the walk copy to <probe dir> (without its import cache) and changes
two things, reporting both:

  * every model's `.glb.import`: `meshes/light_baking` 1 -> 2 (Static
    Lightmaps, which makes Godot unwrap a second UV set on import), EXCEPT a
    model that already carries TEXCOORD_1 -- those are the moving and
    flickering props (turn pivots, slush churn, crown sway, screen shutter
    schedules), whose second UV set is data a shader reads, and which a
    lightmap must not overwrite;
  * every inline primitive mesh in a `.tscn` (the ground, roads, walks,
    kerbs as `BoxMesh`, a few `QuadMesh`): `add_uv2 = true`, which is how a
    PrimitiveMesh makes its own lightmap UVs.

Writes `prepare.json` beside the copy: what it changed and what it left.
Prints what it did; nothing else.
"""
import json
import os
import re
import shutil
import struct
import sys


def has_uv2(glb):
    raw = open(glb, "rb").read()
    n = struct.unpack("<I", raw[12:16])[0]
    doc = json.loads(raw[20:20 + n])
    return any("TEXCOORD_1" in p.get("attributes", {})
               for m in doc.get("meshes", []) for p in m.get("primitives", []))


def main():
    src, dst = sys.argv[1], sys.argv[2]
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns(".godot"))
    report = {"glb_baked": [], "glb_kept_dynamic": [], "glb_already_2": [], "primitives": {}}
    for root, _dirs, files in os.walk(dst):
        for f in files:
            p = os.path.join(root, f)
            rel = os.path.relpath(p, dst).replace("\\", "/")
            if f.endswith(".glb.import"):
                glb = p[:-len(".import")]
                text = open(p, encoding="utf-8").read()
                if has_uv2(glb):
                    report["glb_kept_dynamic"].append(rel[:-len(".import")])
                    continue
                if "meshes/light_baking=2" in text:
                    report["glb_already_2"].append(rel[:-len(".import")])
                    continue
                new, k = re.subn(r"^meshes/light_baking=\d+$", "meshes/light_baking=2", text, flags=re.M)
                if k != 1:
                    raise SystemExit(f"{rel}: {k} light_baking lines, wanted 1")
                open(p, "w", encoding="utf-8", newline="\n").write(new)
                report["glb_baked"].append(rel[:-len(".import")])
            elif f.endswith(".tscn"):
                text = open(p, encoding="utf-8").read()
                count = 0

                def add(m):
                    nonlocal count
                    count += 1
                    return m.group(0) + "\nadd_uv2 = true"
                new = re.sub(r'^\[sub_resource type="(?:BoxMesh|QuadMesh|PlaneMesh|CylinderMesh|PrismMesh)" id="[^"]*"\]$',
                             add, text, flags=re.M)
                if count:
                    open(p, "w", encoding="utf-8", newline="\n").write(new)
                    report["primitives"][rel] = count
    json.dump(report, open(os.path.join(dst, "prepare.json"), "w", encoding="utf-8"), indent=1)
    print("PREPARE models set to static lightmaps:", len(report["glb_baked"]))
    print("PREPARE models kept dynamic (already carry TEXCOORD_1):", len(report["glb_kept_dynamic"]))
    for g in report["glb_kept_dynamic"]:
        print("PREPARE   ", g)
    print("PREPARE primitive meshes given add_uv2:", sum(report["primitives"].values()),
          "in", len(report["primitives"]), "scene(s)")


if __name__ == "__main__":
    main()
