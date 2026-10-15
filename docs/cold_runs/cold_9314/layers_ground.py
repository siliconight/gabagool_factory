"""Cold run 9314 against 9313: the three files Level Factory 0.213.0 and 0.215.0 move, and what else did.

0.213.0 spells `output_layers.json`'s label by the planner and writes HANDOFF.md's last paragraph on the layers;
0.215.0 writes `shading_mode = 0` on the backdrop ground's material. 9313 ran on 0.212.0 and 9314 on 0.215.0 (with
0.214.0, which changes nothing in a package), the same toolchain otherwise, the same brief and seed. This prints:
the two labels and the layer lists; HANDOFF.md's line counts and its last paragraph's first words; the ground
material's lines against the priced unshaded arm's (`docs/findings/walk_2026-10-14/ground_price.sh`); whether the
lightmap and every GLB are the same bytes; the `[export] layers:` line of 9314's export log; and every file that
differs, the 12 scenes Godot saves masked of their per-save ids as `cold_9313/masked_scenes.py` masks them. It
measures and stops.

    python docs/cold_runs/cold_9314/layers_ground.py [9313 9314]
"""
import hashlib
import json
import pathlib
import re
import sys

F = pathlib.Path(__file__).resolve().parents[3]
PKG = "workspaces/cold-{n}-ws/.level_factory/exports/LF_urban_row_001.portable-godot"
GODOT_SAVED = ["presentation/lux.applied.tscn", "bake.tscn"] + [
    "lot/%s/site.tscn" % e for e in ("gs_cornershop_c", "gs_cornershop_d", "gs_midrise_a", "gs_midrise_b",
                                      "gs_midrise_c", "gs_midrise_d", "gs_midrise_e", "gs_midrise_f",
                                      "gs_midrise_h", "gs_midrise_i")]
MASKS = [(re.compile(r'unique_id\s*=\s*-?\d+'), 'unique_id=#'),
         (re.compile(r'id="[^"]*"'), 'id="#"'),
         (re.compile(r'(Ext|Sub)Resource\("[^"]*"\)'), r'\1Resource("#")'),
         (re.compile(r'uid="uid://[^"]*"'), 'uid="#"')]
MAT = re.compile(r'\[sub_resource type="StandardMaterial3D" id="BackdropGround_mat"\]\n(.*?)\n\n', re.S)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def masked(line):
    for pat, rep in MASKS:
        line = pat.sub(rep, line)
    return line


def main():
    a, b = (sys.argv[1], sys.argv[2]) if len(sys.argv) == 3 else ("9313", "9314")
    pa, pb = F / PKG.format(n=a), F / PKG.format(n=b)
    for p in (pa, pb):
        for rel in ("output_layers.json", "HANDOFF.md", "site_backdrop.tscn", "bake.exr"):
            if not (p / rel).is_file():
                raise SystemExit("no %s at %s" % (rel, p))
    print("== output_layers.json")
    for name, p in ((a, pa), (b, pb)):
        d = json.loads((p / "output_layers.json").read_text(encoding="utf-8"))
        print("  %s  layers=%s  label=%r" % (name, d.get("layers"), d.get("label")))
    print("== HANDOFF.md")
    for name, p in ((a, pa), (b, pb)):
        t = (p / "HANDOFF.md").read_text(encoding="utf-8")
        last = [x for x in t.split("\n\n") if x.strip()][-1]
        print("  %s  %d lines, %d bytes; last paragraph: %r" % (name, t.count("\n"), len(t.encode("utf-8")), last[:120]))
    print("== the ground's material, against the priced unshaded arm's")
    priced = F / "_scratch/price_ground/unshaded/site_backdrop.tscn"
    for name, p in ((a, pa), (b, pb)):
        m = MAT.search((p / "site_backdrop.tscn").read_text(encoding="utf-8"))
        print("  %s  %s" % (name, m.group(1).split("\n") if m else "NO GROUND MATERIAL"))
    if priced.is_file():
        m = MAT.search(priced.read_text(encoding="utf-8"))
        print("  priced arm  %s" % (m.group(1).split("\n") if m else "NO GROUND MATERIAL"))
    else:
        print("  priced arm  (its copy is gone; the material lines are in docs/findings/walk_2026-10-14/ground_strip.py)")
    print("== the lightmap and the GLBs")
    print("  bake.exr: %s" % ("the same bytes" if sha(pa / "bake.exr") == sha(pb / "bake.exr") else "DIFFER"))
    ga = {g.relative_to(pa).as_posix(): sha(g) for g in pa.rglob("*.glb")}
    gb = {g.relative_to(pb).as_posix(): sha(g) for g in pb.rglob("*.glb")}
    moved = sorted(k for k in ga if k in gb and ga[k] != gb[k])
    print("  GLBs: %d in %s, %d in %s, %d differ%s" % (len(ga), a, len(gb), b, len(moved),
                                                        (": " + ", ".join(moved)) if moved else ""))
    print("== the export log's layers line")
    log = F / ("docs/cold_runs/cold_%s/export.log" % b)
    lines = [l for l in log.read_text(encoding="utf-8", errors="replace").splitlines() if "[export] layers:" in l] \
        if log.is_file() else []
    print("  " + (lines[0] if lines else "NONE in %s" % log))
    print("== every file, by name")
    fa = {f.relative_to(pa).as_posix(): f for f in pa.rglob("*") if f.is_file()}
    fb = {f.relative_to(pb).as_posix(): f for f in pb.rglob("*") if f.is_file()}
    differ = sorted(k for k in fa if k in fb and sha(fa[k]) != sha(fb[k]))
    print("  %d files in %s, %d in %s; only in %s: %s; only in %s: %s" % (
        len(fa), a, len(fb), b, a, sorted(set(fa) - set(fb)) or "none", b, sorted(set(fb) - set(fa)) or "none"))
    print("  %d differ:" % len(differ))
    for k in differ:
        note = ""
        if k in GODOT_SAVED:
            la = (pa / k).read_text(encoding="utf-8").split("\n")
            lb = (pb / k).read_text(encoding="utf-8").split("\n")
            if len(la) == len(lb):
                d = [i for i, (x, y) in enumerate(zip(la, lb)) if x != y]
                after = [i for i in d if masked(la[i]) != masked(lb[i])]
                note = "  (Godot-saved: %d lines differ, %d after the per-save-id mask)" % (len(d), len(after))
            else:
                note = "  (Godot-saved: %d -> %d lines)" % (len(la), len(lb))
        print("    " + k + note)


if __name__ == "__main__":
    main()
