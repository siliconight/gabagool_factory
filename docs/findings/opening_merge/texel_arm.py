"""Does an opening module baked at its wall's lightmap density lose the seam? A copy of a walk preview whose door and
breach module GLBs import at a coarser `meshes/lightmap_texel_size`, re-imported and re-baked with Level Factory's own
bake, shot beside the preview as it was at the walker's door and breach views.

    python docs/findings/opening_merge/texel_arm.py <walk copy> <texel size> <tag>

`lightmap_density.out.txt`: the deli's breach panel bakes at 12.2 texels/m and the supermarket's door at 16.1,
against 5.8-8.3 for the merged walls round them. Both import at 0.2 m; the small module's chart is mostly padding.
This arm sets every `breach_*` and `doorway_*` GLB's sidecar to <texel size> (0.45 m is about the walls' density),
removes their import cache, imports the copy headless and re-bakes it (`tools/lux_rebake.py`). Writes frames under
`_scratch/texel_<tag>/` and `texel_arm_<tag>.out.json` beside itself; draws no conclusion.
"""
import json
import pathlib
import re
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
F = HERE.parents[2]
GODOT = r"C:\Godot\4.7\Godot_v4.7-stable_win64_console.exe"
SRC, TEXEL, TAG = pathlib.Path(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
WORK = F / "_scratch" / ("texel_" + TAG)
#: the walker's views (docs/findings/walk_2026-10-26_panel/ L5, L6), each looking at the slot it flagged
STATIONS = ["l5_door:7.3,1.6,-13.5,7.5,1.8,-9.0", "l6_breach:-65.9,1.6,-9.7,-70.0,1.5,-9.5",
            "l6_deli:-54.1,1.6,-5.6,-60.0,1.5,-5.6"]

sys.path.insert(0, str(F / "tools"))
import look_shots  # noqa: E402

if WORK.exists():
    shutil.rmtree(WORK)
WORK.mkdir(parents=True)
staged = WORK / "staged"
shutil.copytree(SRC, staged)
n = 0
for imp in staged.glob("lot/*/art/zoo/*.glb.import"):
    if not re.match(r"(breach|doorway)_", imp.name):
        continue
    t = imp.read_text(encoding="utf-8")
    t2, k = re.subn(r"^meshes/lightmap_texel_size=.*$", "meshes/lightmap_texel_size=%s" % TEXEL, t, flags=re.M)
    assert k == 1, imp
    imp.write_text(t2, encoding="utf-8")
    n += 1
shutil.rmtree(staged / ".godot", ignore_errors=True)
r = subprocess.run([GODOT, "--headless", "--path", str(staged), "--import"], capture_output=True, text=True,
                   timeout=1800)
print("sidecars set", n, "import", r.returncode, flush=True)
baked = WORK / "baked"
r = subprocess.run([sys.executable, str(F / "tools" / "lux_rebake.py"), str(staged), str(baked)],
                   capture_output=True, text=True)
print("rebake", r.returncode, (r.stdout.strip().splitlines() or ["-"])[-1][:300], flush=True)
shutil.rmtree(staged, ignore_errors=True)
out = {}
for arm, proj in (("shipped", SRC), ("texel", baked)):
    got = look_shots.shoot(str(proj), str(WORK / ("shots_" + arm)), stations=STATIONS, timeout=900)
    out[arm] = {s["name"]: [round(s["mean"], 1), s["p50"], s.get("png")] for s in got.get("shots", [])
                if s["name"] in ("l5_door", "l6_breach", "l6_deli")}
    print(arm, {k: v[:2] for k, v in out[arm].items()}, flush=True)
shutil.rmtree(baked, ignore_errors=True)
(HERE / ("texel_arm_%s.out.json" % TAG)).write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
