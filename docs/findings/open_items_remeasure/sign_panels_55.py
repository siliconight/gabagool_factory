"""Roadmap 55 re-measured on a package: the blank emitter cards and the unaddressable rigs.

55 (2026-08-18) found four 1.4 m `AreaPanel_Surface` quads at head height, blank, three of them under
engine-generated `@Node3D@<n>` names, in `presentation/lux.applied.tscn`. This reads that scene in a package and
prints: how many `AreaPanel_Surface` nodes stand; how many rig names the engine generated and how many the spawner
gave; every `QuadMesh` sub-resource with the node that uses it and that node's material -- its albedo and emission
textures, or none; and how many `panel_size = Vector2(...)` lines there are, which are rig PROPERTIES and not quads
(the first reading of this instrument counted them as seven quads). Measures and stops.

    python docs/findings/open_items_remeasure/sign_panels_55.py <package dir>
"""
import pathlib
import re
import sys


def main():
    pkg = pathlib.Path(sys.argv[1])
    scene = pkg / "presentation" / "lux.applied.tscn"
    if not scene.is_file():
        raise SystemExit("no presentation/lux.applied.tscn under %s" % pkg)
    text = scene.read_text(encoding="utf-8")
    names = re.findall(r'^\[node name="([^"]*)"', text, re.M)
    print("nodes %d; AreaPanel_Surface %d; engine names (@Node3D@) %d; spawner names (Spawned_*) %d; "
          "AreaPanel_Omni %d; AreaPanel_Spot %d; panel_size properties %d"
          % (len(names), sum(1 for n in names if n == "AreaPanel_Surface"),
             sum(1 for n in names if n.startswith("@Node3D@")), sum(1 for n in names if n.startswith("Spawned_")),
             sum(1 for n in names if n == "AreaPanel_Omni"), sum(1 for n in names if n == "AreaPanel_Spot"),
             len(re.findall(r"^panel_size = Vector2\(", text, re.M))))
    ext = {m.group(2): m.group(1) for m in re.finditer(r'^\[ext_resource type="Texture2D" path="([^"]*)" id="([^"]*)"\]', text, re.M)}
    subs = {}
    for m in re.finditer(r'^\[sub_resource type="([^"]*)" id="([^"]*)"\]\n((?:[^\[\n][^\n]*\n)*)', text, re.M):
        subs[m.group(2)] = (m.group(1), m.group(3))
    quads = [i for i, (t, _) in subs.items() if t == "QuadMesh"]
    print("QuadMesh sub-resources: %d" % len(quads))
    for q in quads:
        for m in re.finditer(r'^\[node name="([^"]*)"[^\n]*\n((?:[^\[\n][^\n]*\n)*)', text, re.M):
            body = m.group(2)
            if 'SubResource("%s")' % q not in body:
                continue
            mat = re.search(r'material_override = SubResource\("([^"]*)"\)', body)
            desc = "no material_override"
            if mat and mat.group(1) in subs:
                mbody = subs[mat.group(1)][1]
                alb = re.search(r'albedo_texture = ExtResource\("([^"]*)"\)', mbody)
                emi = re.search(r'emission_texture = ExtResource\("([^"]*)"\)', mbody)
                desc = "%s: albedo %s, emission %s" % (
                    mat.group(1), ext.get(alb.group(1), "?") if alb else "none",
                    ext.get(emi.group(1), "?") if emi else "none")
            print("  %-14s on node %-10s %s" % (q, m.group(1), desc))


if __name__ == "__main__":
    main()
