"""Re-bake a copy of a walk project with a given Lux loader in its place, then measure and frame it.

    python loader_trial.py <walk project> <work dir> <lux_light_loader.gd> [--keep]

The trials beside this file edit the copy's loader by anchored swaps, which tests the IDEA. This
tests the CODE: the loader a release ships, vendored into the copy the way Level Factory vendors
it (the same text, CRLF), so what is measured is the release and not a re-statement of it.

Copies the walk project to <work>/src, puts the given loader at
`runtime/lux/runtime/lux_light_loader.gd`, re-bakes to <work>/baked with tools/lux_rebake.py (Level
Factory's own bake), runs tools/light_check.py at the level's own slot and look_shots at the
club's three stations. Prints the bake's fill line, every DEN row and each station's frame and
centre figures with the share of its pixels under luma 10. The baked copy is deleted unless
--keep; the shots stay. Nothing outside <work> is written.

FRAME AND UNITS: Godot metres, Y up. Luma 0-255 after the grade, Rec.709.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

FACTORY = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
STATIONS = ["club_main:-72.2,1.6,7.0,-51.8,1.0,7.0", "club_vip:-74.2,1.6,-5.0,-59.8,1.0,-5.0",
            "club_bar:-60.0,1.6,2.0,-62.0,1.2,13.0"]

ap = argparse.ArgumentParser()
ap.add_argument("walk")
ap.add_argument("work")
ap.add_argument("loader")
ap.add_argument("--keep", action="store_true")
args = ap.parse_args()

src, baked = os.path.join(args.work, "src"), os.path.join(args.work, "baked")
for d in (src, baked):
    if os.path.exists(d):
        shutil.rmtree(d)
shutil.copytree(args.walk, src)
dest = os.path.join(src, "runtime", "lux", "runtime", "lux_light_loader.gd")
old = open(dest, "rb").read()
assert old.count(b"\r\n") == old.count(b"\n"), "the package's loader is not CRLF throughout"
new = open(args.loader, "rb").read().replace(b"\r\n", b"\n")
open(dest, "wb").write(new.replace(b"\n", b"\r\n"))
print("trial: %s vendored (%d bytes, was %d)" % (args.loader, len(new.replace(b"\n", b"\r\n")), len(old)))

r = subprocess.run([sys.executable, os.path.join(FACTORY, "tools", "lux_rebake.py"), src, baked],
                   capture_output=True, text=True)
print("rebake exit", r.returncode)
for ln in (r.stdout + r.stderr).splitlines():
    if "room fill" in ln:
        print("  rebake:", ln.strip()[:240])
if r.returncode:
    print(r.stdout[-1500:], r.stderr[-1500:])
    sys.exit(2)
shutil.rmtree(src)

r = subprocess.run([sys.executable, os.path.join(FACTORY, "tools", "light_check.py"), baked,
                    "--slots", "own", "--out", os.path.join(args.work, "light")],
                   capture_output=True, text=True)
for ln in r.stdout.splitlines():
    if " DEN " in ln:
        print(ln)

shots = os.path.join(args.work, "shots")
cmd = [sys.executable, os.path.join(FACTORY, "tools", "look_shots.py"), baked, "--out", shots]
for s in STATIONS:
    cmd += ["--station", s]
r = subprocess.run(cmd, capture_output=True, text=True)
try:
    with open(shots + ".json", encoding="utf-8") as fh:
        man = json.load(fh)
except (OSError, ValueError):
    print(r.stdout[-1500:], r.stderr[-1500:])
    sys.exit("look_shots wrote no manifest")
if "error" in man or not man.get("shots"):
    sys.exit("look_shots: %s" % man.get("error", "no shots"))


def under(png, limit=10):
    """Share of the frame's pixels with Rec.709 luma under `limit`, from the PNG as shot."""
    from PIL import Image
    im = Image.open(png).convert("RGB")
    px = im.get_flattened_data() if hasattr(im, "get_flattened_data") else im.getdata()
    n = lo = 0
    for rr, gg, bb in px:
        n += 1
        if 0.2126 * rr + 0.7152 * gg + 0.0722 * bb < limit:
            lo += 1
    return 100.0 * lo / n


for s in man["shots"]:
    if s["name"].startswith("club_"):
        c = s["centre"]
        print("  %-10s frame mean %6.2f p50 %3d, %4.1f%% under 10 | centre mean %6.2f p50 %3d"
              % (s["name"], s["mean"], s["p50"], under(s["png"]), c["mean"], c["p50"]))
if not args.keep:
    shutil.rmtree(baked)
