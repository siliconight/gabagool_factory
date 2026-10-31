"""The sodium pools at midnight: a walk copy re-baked under the night preset and shot from the street.

    python docs/findings/sodium_pools/night.py <walk project> <tag> [--preset delco_night]

0.75 x REFERENCE_POOL was judged at midnight and Lux 0.82.0 raised it 2.5 x for Blue Hour; the same level lights
every preset that keeps its street lamps lit. This re-bakes a copy (`tools/lux_rebake.py --preset`) and shoots the
slice's street stations, so a pre-0.82.0 walk copy and a 0.82.0 one can be compared at night. Prints each frame's
mean, median and its share of near-clipped pixels (any channel >= 250); the frames are the evidence.
"""
import argparse
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import look_shots  # noqa: E402

ST = ["ave_east:-120.0,1.7,30.6,60.0,4.0,30.6",
      "sidewalk_east:-45.0,1.7,25.5,40.0,2.0,23.5",
      "bank_oblique:8.0,1.7,32.0,-18.0,5.0,18.0",
      "road_down:-35.0,1.7,31.5,-70.0,0.0,31.5"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("tag")
    ap.add_argument("--preset", default="delco_night")
    a = ap.parse_args()
    base = ROOT / "_scratch" / "sodium_night"
    dst = base / a.tag
    if dst.exists():
        print(f"REFUSED: {dst} exists")
        return 1
    base.mkdir(parents=True, exist_ok=True)
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "lux_rebake.py"), a.project, str(dst),
                        "--preset", a.preset])
    if r.returncode != 0:
        print(f"rebake exit {r.returncode}")
        return 1
    out = base / ("frames_" + a.tag)
    got = look_shots.shoot(str(dst), str(out), stations=ST, timeout=1200)
    for sh in got.get("shots", []):
        name = sh["name"]
        if name not in [x.split(":")[0] for x in ST]:
            continue
        px = np.asarray(Image.open(out / (name + ".png")).convert("RGB"))
        clip = float((px.max(axis=2) >= 250).mean())
        print(a.tag, name, round(sh["mean"], 1), sh["p50"], "clip %.3f" % clip)
    return 0


if __name__ == "__main__":
    sys.exit(main())
