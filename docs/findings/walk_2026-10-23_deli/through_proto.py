"""Prototype: luma through an opening's rim, from a light_check run's frames. Prints measurements only, and
writes each frame with its rim drawn on it into the light check's out dir.

    python _scratch/through_proto.py <walk copy> <light_check out dir> <deli_counter>
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "tools"))
import light_check  # noqa: E402

walk, out, dc = sys.argv[1:4]
sys.path.insert(0, dc)
import ladder_geom  # noqa: E402
import lights  # noqa: E402
import spec_loader  # noqa: E402
import stairwell  # noqa: E402
import axonometric  # noqa: E402

FOV_V = 75.0


def project(eye, target, pts, w, h):
    e, t = np.array(eye, float), np.array(target, float)
    z = e - t
    z /= np.linalg.norm(z)
    x = np.cross([0.0, 1.0, 0.0], z)
    x /= np.linalg.norm(x)
    y = np.cross(z, x)
    f = 1.0 / math.tan(math.radians(FOV_V) / 2.0)
    uv = []
    for p in pts:
        d = np.array(p, float) - e
        cx, cy, cz = d @ x, d @ y, d @ z
        if cz >= 0:
            return None
        nx, ny = f * cx / (-cz) / (w / h), f * cy / (-cz)
        uv.append(((nx + 1) / 2 * w, (1 - ny) / 2 * h))
    return uv


def luma(png):
    a = np.asarray(Image.open(png).convert("RGB"), dtype=np.float64)
    return 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]


def mask(uv, w, h):
    from PIL import ImageDraw
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).polygon([(float(u), float(v)) for u, v in uv], fill=255)
    return np.asarray(m) > 0


ops, note = light_check.openings(walk, dc)
places = light_check.placements(walk)
shots = {s["name"]: s for s in json.load(open(os.path.join(out, "own.json"), encoding="utf-8"))["shots"]}
for o in ops:
    sh_ = shots.get(o["name"])
    if not sh_:
        print(o["name"], "no shot")
        continue
    spec = spec_loader.load_spec(os.path.join(dc, "specs", [b for b in json.load(open(os.path.join(walk, "buildings.json")))["buildings"] if b.get("node") == o["node"]][0]["spec"] + ".json"))
    sh = float(spec.story_height)
    s = o["story"]
    k = int(o["name"].rsplit("_", 1)[1])
    g = lights.opening_landings(spec)[k]
    rect, zt = None, None
    if g["kind"] == "stair":
        for st in spec.stairs:
            low = [x for x in stairwell.stair_endpoints(st) if x["end"] == "lower"]
            if low and min(st.from_story, st.to_story) == s and abs(low[0]["point"][0] - g["x"]) < .01 and abs(low[0]["point"][1] - g["y"]) < .01:
                rect, zt = stairwell.footprint_rect(st), max(st.from_story, st.to_story) * sh
    elif g["kind"] == "hole":
        for r, kind in axonometric._slab_holes(spec).get(s + 1, []):
            if kind != "stair" and r[0] <= g["x"] <= r[2] and r[1] <= g["y"] <= r[3]:
                rect, zt = r, (s + 1) * sh
                break
    else:
        for ld in spec.ladders:
            if abs(ld.x - g["x"]) < .01 and abs(ld.y - g["y"]) < .01:
                hx, hy, sx, sy = ladder_geom.through_hole(ld.x, ld.y, ld.width, ld.facing)
                rect, zt = (hx - sx / 2, hy - sy / 2, hx + sx / 2, hy + sy / 2), max(ld.from_story, ld.to_story) * sh
    place = places[o["node"]]
    rim = [light_check.to_site(place, (rect[0], rect[1], zt)), light_check.to_site(place, (rect[2], rect[1], zt)),
           light_check.to_site(place, (rect[2], rect[3], zt)), light_check.to_site(place, (rect[0], rect[3], zt))]
    L = luma(sh_["png"])
    h, w = L.shape
    uv = project(sh_["eye"], sh_["target"], rim, w, h)
    if uv is None:
        print(o["name"], "rim behind the camera")
        continue
    m = mask(uv, w, h)
    inside = L[m]
    print("%-28s frame p50 godot %3d png %5.1f | rim %5.1f%% of frame, through p50 %5.1f mean %5.1f p95 %5.1f | rect %s z %.2f"
          % (o["name"], sh_["p50"], np.percentile(L, 50), 100.0 * m.mean(),
             np.percentile(inside, 50) if inside.size else -1, inside.mean() if inside.size else -1,
             np.percentile(inside, 95) if inside.size else -1, [round(c, 2) for c in rect], zt))
    im = Image.open(sh_["png"]).convert("RGB")
    from PIL import ImageDraw
    ImageDraw.Draw(im).polygon([(float(u), float(v)) for u, v in uv], outline=(255, 0, 255))
    im.save(os.path.join(out, "through_" + o["name"] + ".png"))   # the rim drawn on the frame, beside the run
