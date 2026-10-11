"""What does the elevated west camera see where 9226 saw a "pale slab"?

    python docs/cold_runs/cold_9240/slab_ray.py

The camera is look_shots' `elev_W` as 9240's shots report records it: ORTHOGRAPHIC, eye
(-7.45, 3.758, 4.53) looking +X at the same height, an 8.1 m tall frame at 1600 x 900 (Godot
metres, Y up). It maps frame pixels to world rays, checks the mapping against the plate's own props
(their slot centres must land where the frame shows them), then casts the slab's rays -- the box
measured on the frame, pixels (70..290, 176..216) -- through every `site_backdrop` slot box of the
picked candidate (seed 9105, Blender Z-up: Godot (X, Y, Z) is Blender (X, -Z, Y)), and for the
warehouse they meet, reads which facade window each ray lands in and whether Zoo paints it lit
(`core.backdrop_forms.warehouse_openings` / `warehouse_lit`, keyed by the module's stem). It
prints what it measured and stops.
"""
import json
import math
import os
import sys

F = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(F, "zoo"))
from zoo_keeper.core import backdrop_forms as BF  # noqa: E402

SLOTS = os.path.join(F, "workspaces", "cold-9240-ws", ".level_factory", "jobs",
                     "warehouse_yard_001.lot_assemble.candidate.seed_9105", "out", "site.slots.json")
EYE, H_M, W_PX, H_PX = (-7.45, 3.758, 4.53), 8.1, 1600, 900
W_M = H_M * W_PX / H_PX


def ray(px, py):
    """The orthographic ray through a pixel: Blender (y, z) of a line along +X."""
    zg = EYE[2] + (px / W_PX - 0.5) * W_M
    yg = EYE[1] + (0.5 - py / H_PX) * H_M
    return -zg, yg


def frame_of(c, dims):
    zg = -c[1]
    return ((zg - EYE[2]) / W_M + 0.5) * W_PX, (0.5 - ((c[2] + dims[2] / 2) - EYE[1]) / H_M) * H_PX


slots = json.load(open(SLOTS, encoding="utf-8"))["slots"]
print("[slab] camera elev_W, orthographic, %.1f x %.1f m frame" % (W_M, H_M))
for s in slots:
    if s.get("species") in ("payphone", "mailbox", "bus_shelter"):
        px, top = frame_of(s["transform"]["translation"], s["fit"]["dims"])
        if 0 <= px <= W_PX:
            print("[slab] check: %-12s lands at frame x %.0f, top y %.0f" % (s["species"], px, top))

backdrop = [s for s in slots if s.get("source") == "site_backdrop"]
for px, py in ((80, 180), (180, 196), (280, 212)):
    yb, zb = ray(px, py)
    hits = []
    for s in backdrop:
        c = s["transform"]["translation"]
        w, d, h = s["fit"]["dims"]
        a = math.radians(s["transform"]["rot_y"])
        if abs(zb - c[2]) > h / 2:
            continue
        lo, hi, ok, dy = -1e9, 1e9, True, yb - c[1]
        for ku, kc, half in ((math.cos(a), math.sin(a) * dy, w / 2), (-math.sin(a), math.cos(a) * dy, d / 2)):
            if abs(ku) < 1e-9:
                ok = ok and abs(kc) <= half
                continue
            t1, t2 = (-half - kc) / ku + c[0], (half - kc) / ku + c[0]
            lo, hi = max(lo, min(t1, t2)), min(hi, max(t1, t2))
        # in front of the eye only: an orthographic camera draws nothing behind it
        if ok and lo <= hi and hi > EYE[0]:
            hits.append((max(lo, EYE[0]), s))
    hits.sort(key=lambda t: t[0])
    print("[slab] pixel (%d, %d): Blender y %.2f z %.2f, %d backdrop box(es) on the ray"
          % (px, py, yb, zb, len(hits)))
    for lo, s in hits[:1]:
        c, (w, d, h), rot = s["transform"]["translation"], s["fit"]["dims"], s["transform"]["rot_y"]
        print("[slab]   first: %s %s at x %.2f, centre %s, dims %s, rot %s"
              % (s["slot_id"], s["species"], lo, c, [w, d, h], rot))
        if s["species"] != "backdrop_warehouse" or rot != 270.0:
            continue
        # rot 270 about +Z takes local (x, y) to world (y, -x): the front (-Y) faces -X, and the
        # facade's left-to-right runs toward world -Y, so facade metres = w/2 + (cy - y)
        fx = w / 2.0 + (c[1] - yb)
        fz = zb - (c[2] - h / 2.0)
        stem = "prop_backdrop_warehouse_delco_1997_01_w%d_d%d_h%d" % (round(w * 100), round(d * 100), round(h * 100))
        wins = [o for o in BF.warehouse_openings(w, h - BF.MONITOR_H) if o[0] == "window"]
        lit = BF.warehouse_lit(stem, len(wins))
        for k, (_kind, x0, z0, x1, z1) in enumerate(wins):
            if x0 - 0.15 <= fx <= x1 + 0.15:
                print("[slab]   facade (%.2f, %.2f) m: high window %d of %d, (%.2f..%.2f) x (%.2f..%.2f) m, %s"
                      % (fx, fz, k, len(wins), x0, x1, z0, z1, "LIT " + lit[k] if lit[k] else "unlit"))
