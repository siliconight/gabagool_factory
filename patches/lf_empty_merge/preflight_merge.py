"""Pre-flight for the Empties' merge, before a cold run spends 33 minutes.

    python preflight_merge.py <level_factory dir> <source dir> <work dir>

Copies <source dir> -- a cold run's walk copy, which is its package plus the
walk scene the frame script needs -- to <work dir> (its import cache too), then
runs, from the Level Factory at <level_factory dir> (a patched scratch copy is
the point), the export's own two late steps in their order:
  1. `merge_empties.merge` -- prints its checked report, or why it refused;
  2. `light_bake.bake` -- re-bakes with the merged meshes as users, and
     prints its report beside the source's own `light_bake.json`, so a bake
     that took the merged meshes is told from one that fell back unbaked.
Prints what it measured and stops.
"""
import json
import pathlib
import shutil
import sys

lf, src, work = (pathlib.Path(a).resolve() for a in sys.argv[1:4])
sys.path.insert(0, str(lf))
from packages.exporting import light_bake, merge_empties  # noqa: E402

assert pathlib.Path(merge_empties.__file__).resolve().is_relative_to(lf), merge_empties.__file__
godot = r"C:\Godot\4.7\Godot_v4.7-stable_win64_console.exe"
if work.exists():
    shutil.rmtree(work)
shutil.copytree(src, work)
before = json.loads((src / "light_bake.json").read_text(encoding="utf-8")) \
    if (src / "light_bake.json").exists() else {}
print("source bake: ok %s, users %s" % (before.get("ok"), (before.get("result") or {}).get("users")))
try:
    rep = merge_empties.merge(work, godot)
except merge_empties.MergeError as exc:
    print("MERGE REFUSED:", exc)
    sys.exit(1)
for r in rep["scenes"]:
    print("  %s: %d meshes / %d surfaces -> %d merged, %d unwrapped, %d colliders, %d doors dropped"
          % (r["scene"], r["meshes_in"], r["surfaces_in"], r["merged"], r["unwrapped"],
             r["colliders"], r["doors_dropped"]))
merged = sorted(work.glob("lot/*/merged/*.res"))
print("merged meshes on disk: %d" % len(merged))
bk = light_bake.bake(work, godot, log=print)
print("re-bake: ok %s, users %s, reason %s"
      % (bk.get("ok"), (bk.get("result") or {}).get("users"), bk.get("reason")))
