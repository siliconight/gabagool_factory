"""Top-down plan of one room of a spec, as a PNG: the room's bounds, every standing volume whose centre is in it on its
storey (furnish's in colour by stem, authored in grey, outlined), the doorways on its bounds (`room_openings`, red),
and its front (`room_front`, a blue bar). Measurements drawn, nothing judged.

    python room_plan.py <deli_counter dir> <spec.json> <room id> <out.png>
"""
import json
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, sys.argv[1])
import level_design as L  # noqa: E402

spec = json.load(open(sys.argv[2], encoding="utf-8"))
room = next(r for r in spec["rooms"] if r["id"] == sys.argv[3])
x0, y0, x1, y1 = room["bounds"]
S, M = 24, 30          # pixels a metre, margin
W, H = int((x1 - x0) * S) + 2 * M, int((y1 - y0) * S) + 2 * M
im = Image.new("RGB", (W, H), (245, 243, 238))
dr = ImageDraw.Draw(im)


def px(x, y):
    return M + (x - x0) * S, M + (y1 - y) * S        # north up


dr.rectangle([px(x0, y1), px(x1, y0)], outline=(40, 40, 40), width=3)
sh = spec.get("story_height", 3.6)
floor = room.get("story", 0) * sh
tag = "_%s_" % L._room_tag(room)
COL = {"pew": (150, 95, 50), "table_work": (60, 120, 200), "counter_service": (120, 60, 160),
       "cabinet_file": (110, 110, 110), "display_case": (40, 160, 150), "shelf_run": (200, 150, 40)}
for v in spec.get("volumes", []):
    vx, vy = float(v.get("x", 0)), float(v.get("y", 0))
    if not (x0 <= vx <= x1 and y0 <= vy <= y1):
        continue
    if abs(float(v.get("z", 0)) - float(v.get("size_z", 0)) / 2.0 - floor) > 0.3:
        continue
    sx, sy = float(v.get("size_x", 0)), float(v.get("size_y", 0))
    stem = v["name"].split(tag)[0] if tag in v["name"] else None
    fill = COL.get(stem, (230, 120, 120)) if stem else (190, 190, 190)
    dr.rectangle([px(vx - sx / 2, vy + sy / 2), px(vx + sx / 2, vy - sy / 2)], fill=fill, outline=(20, 20, 20))
for ox, oy, ow in L.room_openings(spec, room):
    cx, cy = px(ox, oy)
    dr.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(220, 30, 30))
along_x, sign = L.room_front(spec, room)
if along_x:
    fx = x1 if sign > 0 else x0
    dr.line([px(fx, y0), px(fx, y1)], fill=(30, 80, 230), width=6)
else:
    fy = y1 if sign > 0 else y0
    dr.line([px(x0, fy), px(x1, fy)], fill=(30, 80, 230), width=6)
dr.text((6, 6), "%s / %s  %s  front: %s %s  share %.2f" % (spec.get("name"), room["id"], L._room_kind(room, spec.get("name")),
                                                         "x" if along_x else "y", "+" if sign > 0 else "-",
                                                         L.room_floor_share(spec, room)), fill=(0, 0, 0))
im.save(sys.argv[4])
print(sys.argv[4], im.size)
