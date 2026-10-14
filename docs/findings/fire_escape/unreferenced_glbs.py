"""The GLBs a package carries that no scene or resource of it names (roadmap 249, found with cold run 9304).

    python docs/findings/fire_escape/unreferenced_glbs.py <package> > <out.txt>

Reads every `.tscn` and `.tres` in the package for `path="..."` references to a `.glb`, then lists the `.glb` files
none of them names, by `lot/<id>` or top directory, with the bytes of each file and of its `.import` and
`.unwrap_cache` beside it; and how many of `light_bake.json`'s `imports.baked` -- the model imports the light bake
sets to Static Lightmaps, each unwrapped at import -- are files no scene names.

NAMED BY NO SCENE IS NOT UNUSED. A script or the game may load a file by path at runtime: the responder cruiser
under `cover/` is shipped for the gameplay layer to spawn, by design. What this prints is where to look, not what
to delete. Prints what it measured and stops; a `light_bake.json` without `imports.baked` stops it.
"""
import json
import re
import sys
from pathlib import Path

P = Path(sys.argv[1])
text = "".join(t.read_text(encoding="utf-8", errors="replace") for t in list(P.rglob("*.tscn")) + list(P.rglob("*.tres")))
refs = set(re.findall(r'path="(?:res://)?([^"]+\.glb)"', text))
glbs = sorted(p.relative_to(P).as_posix() for p in P.rglob("*.glb"))
lb = json.loads((P / "light_bake.json").read_text(encoding="utf-8"))
baked = (lb.get("imports") or {}).get("baked")
if not isinstance(baked, list):
    raise SystemExit("UNKNOWN SHAPE: light_bake.json has no imports.baked list")
print("package", P.as_posix())
print("every .glb in the package: %d; named by a .tscn or .tres path: %d" % (len(glbs), sum(1 for g in glbs if g in refs)))
print("light_bake.json imports.baked: %d entries, of them named by no scene: %d"
      % (len(baked), sum(1 for x in baked if x.replace("res://", "") not in refs)))
by = {}
for g in glbs:
    if g in refs:
        continue
    top = "/".join(g.split("/")[:2]) if g.startswith("lot/") else g.split("/")[0]
    n, b = by.get(top, (0, 0))
    by[top] = (n + 1, b + (P / g).stat().st_size
               + sum(x.stat().st_size for x in (P / g).parent.glob(Path(g).name + ".*")))
print("named by no scene, by lot (files, bytes with their .import and .unwrap_cache):")
for k, (n, b) in sorted(by.items(), key=lambda kv: -kv[1][1]):
    print("  %-28s %4d  %10d" % (k, n, b))
print("total named by no scene: %d glb, %d bytes" % (sum(v[0] for v in by.values()), sum(v[1] for v in by.values())))
