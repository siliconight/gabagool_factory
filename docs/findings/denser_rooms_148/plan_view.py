"""Plan view of one room in two Deli Counter checkouts, side by side: every standing volume on the room's storey as a
box, the storey's partitions and door openings, the room's bounds, and the floor share `room_floor_share` measures
(asked of the AFTER checkout's code, which has it). Each checkout's specs are read as they stand. Writes a PNG (PIL).

    python plan_view.py <before deli_counter> <after deli_counter> <spec> <room id> <out.png>

The roadmap 148 frames: before a 0.245.0 checkout, after 0.247.0 (the gondolas laid by furnish in red, a room's own
authored aisles in orange).
"""
import json
import os
import sys
from PIL import Image, ImageDraw

BEFORE, AFTER, name, rid, out = sys.argv[1:6]
S = 22  # px a metre
PAD = 3.0


def load(root):
    with open(os.path.join(root, "specs", name + ".json"), encoding="utf-8") as f:
        return json.load(f)


def panel(d, share, title):
    room = [r for r in d["rooms"] if r["id"] == rid][0]
    x0, y0, x1, y1 = room["bounds"]
    W, H = int((x1 - x0 + 2 * PAD) * S), int((y1 - y0 + 2 * PAD) * S) + 30
    im = Image.new("RGB", (W, H), "white")
    g = ImageDraw.Draw(im)
    def P(x, y):
        return ((x - x0 + PAD) * S, (y1 + PAD - y) * S + 30)
    def box(cx, cy, sx, sy, fill, outline=None):
        a, b = P(cx - sx / 2, cy + sy / 2), P(cx + sx / 2, cy - sy / 2)
        g.rectangle([a, b], fill=fill, outline=outline)
    st = room.get("story", 0)
    sh = float(d.get("story_height", 3.6) or 3.6)   # level_design._story_height's default
    t = float(d.get("wall_thick", 0.3))
    hx, hy = d.get("footprint_x", 20) / 2, d.get("footprint_y", 20) / 2
    for p in d.get("partitions", []):
        if p.get("story", 0) != st: continue
        s, e = p["start"], p["end"]
        if p["axis"] == "Y":
            box(p["pos"], (s + e) / 2, t, e - s, (70, 70, 70))
        else:
            box((s + e) / 2, p["pos"], e - s, t, (70, 70, 70))
        for op in p.get("openings", []):
            u = s + (op.get("pos", 0.0) + 0.5) * abs(e - s)
            ox, oy = (p["pos"], u) if p["axis"] == "Y" else (u, p["pos"])
            w = float(op.get("width", 1.25))
            box(ox, oy, t + 0.2 if p["axis"] == "Y" else w, w if p["axis"] == "Y" else t + 0.2, (40, 200, 40))
    for wl in d.get("ext_walls", []):
        if wl.get("story", 0) != st: continue
        runl = d.get("footprint_x", 20) if wl["wall"] in ("N", "S") else d.get("footprint_y", 20)
        for op in wl.get("openings", []):
            u = op.get("pos", 0.0) * runl
            ox, oy = {"N": (u, hy), "S": (u, -hy), "E": (hx, u), "W": (-hx, u)}[wl["wall"]]
            w = float(op.get("width", 1.25))
            door = "door" in str(op.get("kind", op.get("type", ""))).lower()
            box(ox, oy, w if wl["wall"] in ("N", "S") else t + 0.2, t + 0.2 if wl["wall"] in ("N", "S") else w,
                (40, 200, 40) if door else (80, 200, 230))
    floor = st * sh
    for v in d["volumes"]:
        vz, vh = v.get("z", 0), v.get("size_z", 0)
        if v.get("visual") is False: continue
        if not (floor - 0.5 <= vz - vh / 2 < floor + sh - 0.5): continue
        vx, vy, sx, sy = v["x"], v["y"], v["size_x"], v["size_y"]
        if not (x0 - PAD < vx < x1 + PAD and y0 - PAD < vy < y1 + PAD) or sx * sy > 60: continue
        n = v["name"]
        col = ((215, 40, 40) if n.startswith("gondola_aisle_r") else (240, 150, 30) if ("aisle" in n or "gondola" in n) else
               (190, 190, 190) if v.get("collision") == "none" else (60, 110, 200))
        box(vx, vy, sx, sy, col, (0, 0, 0))
    a, b = P(x0, y1), P(x1, y0)
    g.rectangle([a, b], outline=(0, 0, 0), width=2)
    g.text((6, 6), "%s  share %.1f%%" % (title, 100 * share), fill=(0, 0, 0))
    return im


sys.path.insert(0, AFTER)
import level_design as L  # noqa: E402  (the after checkout's: it has room_floor_share)

d0, d1 = load(BEFORE), load(AFTER)
r0 = [r for r in d0["rooms"] if r["id"] == rid][0]
r1 = [r for r in d1["rooms"] if r["id"] == rid][0]
a = panel(d0, L.room_floor_share(d0, r0), "%s/%s, before" % (name, rid))
b = panel(d1, L.room_floor_share(d1, r1), "after")
im = Image.new("RGB", (a.width + b.width + 20, max(a.height, b.height) + 24), "white")
im.paste(a, (0, 0))
im.paste(b, (a.width + 20, 0))
ImageDraw.Draw(im).text((6, im.height - 18), "red: rows' gondolas  orange: a room's own aisles  blue: other standing  "
                        "grey: no collision  green: doors  cyan: windows", fill=(0, 0, 0))
im.save(out)
print("wrote", out, im.size)
