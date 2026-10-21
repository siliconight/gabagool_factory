"""setback_demo's floor_cage and strip_retail_a01's rear_hall, newly COVER_ALL_LOW in the 0.252.0 clone: per checkout
(argv: 0.251.0, 0.252.0), the room's area and kind, whether the shelter pass would seed it and why not, and the
pieces standing on its storey with their heights, tallest first. Read-only; each checkout in its own process."""
import json
import os
import subprocess
import sys

PROBE = r'''
import json, os, sys
sys.path.insert(0, sys.argv[1])
import level_design as L
assert os.path.samefile(L.__file__, os.path.join(sys.argv[1], "level_design.py"))
for spec, rid in (("setback_demo", "floor_cage"), ("strip_retail_a01", "rear_hall")):
    d = json.load(open(os.path.join(sys.argv[1], "specs", spec + ".json"), encoding="utf-8"))
    room = next(r for r in d["rooms"] if r["id"] == rid)
    x0, y0, x1, y1 = room["bounds"]
    sh = L._story_height(d)
    floor = room.get("story", 0) * sh
    mine = sorted(((v["size_z"], v["name"]) for v in d["volumes"]
                   if x0 <= v["x"] <= x1 and y0 <= v["y"] <= y1 and v.get("collision") != "none"
                   and L.stands_on_storey(float(v.get("z", 0)), float(v.get("size_z", 0)), floor, sh)), reverse=True)
    print("%s/%s %.0f m2 kind %s combat %r has_shelter %r has_cover %r tallest: %s" % (
        spec, rid, (x1 - x0) * (y1 - y0), L._room_kind(room, L.club_building_id(d)), room.get("combat_range"),
        L._room_has_shelter(d, room), L._room_has_cover(d, room), mine[:5]))
'''
for dc in sys.argv[1:3]:
    r = subprocess.run([sys.executable, "-B", "-c", PROBE, dc], capture_output=True, text=True)
    print("==", dc)
    print(r.stdout.strip() or r.stderr[-1500:])
