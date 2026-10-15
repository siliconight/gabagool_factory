"""Cold run 9313 against 9312: where the second UV set went, and what else moved (the factory's roadmap 251).

Level Factory 0.212.0 gives `add_uv2 = true` to the scenes the bake draws and no others, and its log counts
those. 9312 ran on 0.211.1 and 9313 on 0.212.0, the same toolchain otherwise, the same brief and seed. This
reads both packages and prints: the `add_uv2 = true` marks in every scene that carries any, the `primitives`
table each `light_bake.json` recorded, whether the lightmap and every GLB are the same bytes, and the files
that differ, by name. It measures and stops; what the differences are belongs in NOTES.md.

    python docs/cold_runs/cold_9313/uv2_marks.py [9312 9313]
"""
import hashlib
import json
import pathlib
import sys

F = pathlib.Path(__file__).resolve().parents[3]
PKG = "workspaces/cold-{n}-ws/.level_factory/exports/LF_urban_row_001.portable-godot"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    a, b = (sys.argv[1], sys.argv[2]) if len(sys.argv) == 3 else ("9312", "9313")
    pa, pb = F / PKG.format(n=a), F / PKG.format(n=b)
    for p in (pa, pb):
        if not (p / "light_bake.json").is_file() or not (p / "site_backdrop.tscn").is_file():
            raise SystemExit("no baked package with a backdrop at %s" % p)
    print("== add_uv2 = true marks, per scene (every .tscn carrying any, in either package)")
    marks = {}
    for name, p in ((a, pa), (b, pb)):
        for s in sorted(p.rglob("*.tscn")):
            if ".godot" in s.parts:
                continue
            n = s.read_text(encoding="utf-8").count("add_uv2 = true")
            if n:
                marks.setdefault(s.relative_to(p).as_posix(), {})[name] = n
    for rel in sorted(marks):
        print("  %-36s %s %4d   %s %4d" % (rel, a, marks[rel].get(a, 0), b, marks[rel].get(b, 0)))
    print("== light_bake.json")
    for name, p in ((a, pa), (b, pb)):
        d = json.loads((p / "light_bake.json").read_text(encoding="utf-8"))
        prim = d.get("primitives")
        if not isinstance(prim, dict):
            raise SystemExit("%s: light_bake.json has no primitives table" % name)
        print("  %s ok=%s primitives=%s sum=%d baked_models=%d users=%s attempts=%d"
              % (name, d.get("ok"), json.dumps(prim, sort_keys=True), sum(prim.values()),
                 len((d.get("imports") or {}).get("baked") or []), (d.get("result") or {}).get("users"),
                 len(d.get("attempts") or [])))
    print("== the lightmap and the GLBs")
    print("  bake.exr: %s" % ("the same bytes" if sha(pa / "bake.exr") == sha(pb / "bake.exr") else "DIFFER"))
    ga = {g.relative_to(pa).as_posix(): sha(g) for g in pa.rglob("*.glb")}
    gb = {g.relative_to(pb).as_posix(): sha(g) for g in pb.rglob("*.glb")}
    moved = sorted(k for k in ga if k in gb and ga[k] != gb[k])
    print("  GLBs: %d in %s, %d in %s, %d shared, %d differ%s"
          % (len(ga), a, len(gb), b, len(set(ga) & set(gb)), len(moved), (": " + ", ".join(moved)) if moved else ""))
    print("== every file, by name")
    fa = {f.relative_to(pa).as_posix(): f for f in pa.rglob("*") if f.is_file()}
    fb = {f.relative_to(pb).as_posix(): f for f in pb.rglob("*") if f.is_file()}
    differ = sorted(k for k in fa if k in fb and sha(fa[k]) != sha(fb[k]))
    print("  %d files in %s, %d in %s; only in %s: %s; only in %s: %s"
          % (len(fa), a, len(fb), b, a, sorted(set(fa) - set(fb)) or "none", b, sorted(set(fb) - set(fa)) or "none"))
    print("  %d differ:" % len(differ))
    for k in differ:
        print("    " + k)


if __name__ == "__main__":
    main()
