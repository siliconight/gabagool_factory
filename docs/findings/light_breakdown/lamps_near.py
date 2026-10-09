"""Every lamp and room probe a walk project carries near a point, by kind.

    python lamps_near.py <walk project> X,Y,Z [--within M]

Reads `presentation/lux.applied.tscn` -- the presentation scene `bake.tscn`
instances at the identity, so its numbers are Godot world metres, Y up -- and
lists each rig under `LuxFixtureLights` (the spawner's), `LuxLights` (the
manifest bake's), `LuxClub` and `LuxDaylight`, and each ReflectionProbe, whose
origin is within --within metres (default 12) of the point, nearest first:
name, kind, distance, and whether its rig resource is baked (`bake_mode = 1`)
or live. A rig's kind is its name with the container's prefixes taken off
(`Spawned_fluorescent_004` is a fluorescent). Nested rigs are not looked into:
a rig's lamps sit within a metre of its origin.

Godot writes a Transform3D's basis as rows and its origin last; only the
origin is read here. Prints what it measured and stops. A scene with none of
the four containers refuses.
"""
import argparse
import math
import pathlib
import re

SCENE = pathlib.Path("presentation") / "lux.applied.tscn"
CONTAINERS = ("LuxFixtureLights", "LuxLights", "LuxClub", "LuxDaylight")
NODE = re.compile(r'^\[node name="([^"]+)" type="([^"]+)" parent="([^"]*)"[^\]]*\]$', re.M)
NODE_ANY = re.compile(r'^\[node name="([^"]+)"(?: type="([^"]+)")? parent="([^"]*)"[^\]]*\]$', re.M)
XFORM = re.compile(r"^transform = Transform3D\(([^)]*)\)$", re.M)
SUBRES = re.compile(r'^rig = SubResource\("([^"]+)"\)$', re.M)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("point")
    ap.add_argument("--within", type=float, default=12.0)
    a = ap.parse_args()
    px, py, pz = (float(v) for v in a.point.split(","))
    text = (pathlib.Path(a.project) / SCENE).read_text(encoding="utf-8")
    marks = list(NODE_ANY.finditer(text))
    if not any(m.group(1) in CONTAINERS for m in marks):
        raise SystemExit("none of %s in %s" % (", ".join(CONTAINERS), SCENE))
    # which sub_resources are baked
    baked = {}
    for m in re.finditer(r'^\[sub_resource type="Resource" id="([^"]+)"\]$(.*?)(?=^\[)', text, re.M | re.S):
        bm = re.search(r"^bake_mode = (\d+)$", m.group(2), re.M)
        baked[m.group(1)] = int(bm.group(1)) if bm else 0
    found = []
    for i, m in enumerate(marks):
        name, typ, parent = m.group(1), m.group(2) or "", m.group(3)
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        body = text[m.end():end]
        top = parent.split("/")[-1] if parent else ""
        is_rig = top in CONTAINERS and "/" not in parent.replace(top, "", 1).strip("/")
        is_probe = typ == "ReflectionProbe"
        if not (is_rig or is_probe):
            continue
        x = XFORM.search(body)
        if not x:
            continue
        v = [float(s) for s in x.group(1).split(",")]
        ox, oy, oz = v[9], v[10], v[11]
        d = math.dist((ox, oy, oz), (px, py, pz))
        if d > a.within:
            continue
        sub = SUBRES.search(body)
        mode = baked.get(sub.group(1)) if sub else None
        kind = re.sub(r"^(Spawned_|b\d+_)", "", name)
        while re.search(r"(_dup\d+|_\d+)$", kind):          # pendant_001_dup2 -> pendant
            kind = re.sub(r"(_dup\d+|_\d+)$", "", kind)
        found.append((d, name, "probe" if is_probe else kind, top or parent,
                      "-" if mode is None else ("baked" if mode == 1 else "live")))
    found.sort()
    print("within %.1f m of (%.3f, %.3f, %.3f): %d" % (a.within, px, py, pz, len(found)))
    for d, name, kind, where, mode in found:
        print("  %6.2f m  %-34s %-18s %-17s %s" % (d, name, kind, where, mode))


if __name__ == "__main__":
    main()
