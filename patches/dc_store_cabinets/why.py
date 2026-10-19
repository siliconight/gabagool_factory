"""Replay `level_design._place_fixture`'s candidate loop for the store's video poker cabinet and say which test
rejects each held wall slot. A probe: prints and stops.

Measured for patch_dc_store_cabinets.py on Deli Counter 0.227.0's deli_a01 (709fee88), which the test's fixture
keeps: `tests_fixtures/store_cabinets/deli_a01.json`. A spec argument ending in .json is read as a path; anything
else names a library spec under specs/.

    python why.py <deli_counter dir> <spec name | spec.json> <room id>
"""
import json
import os
import random
import sys
from collections import Counter

dc = os.path.abspath(sys.argv[1])
if sys.argv[2].endswith(".json"):
    sys.argv[2] = os.path.abspath(sys.argv[2])
sys.path.insert(0, dc)
os.chdir(dc)
import level_design as L  # noqa: E402

KEY = "video_poker_store"
arg = sys.argv[2]
spec_path = arg if arg.endswith(".json") else os.path.join("specs", arg + ".json")
spec = json.load(open(spec_path, encoding="utf-8"))
room = [r for r in spec["rooms"] if r.get("id") == sys.argv[3]][0]
p = L._PIECES[KEY]
story = room.get("story", 0)
clear_h = L._clear_height(spec)
inner = L._nested_rects(spec, room)
rng = random.Random(f"{spec.get('seed', 0)}:{room['id']}:fixture:{KEY}:0")
sizes = list(L._palette(spec, KEY))
why = Counter()
spots = []
for _r in range(L._FIXTURE_ROUNDS):
    for size in sizes:
        for spot in L._wall_slots(spec, room, size[0], size[1], rng, with_front=True,
                                  over_openings=L._over_openings(spec, story, p, size[2]),
                                  off_glass=p["off_glass"], back_off=L.piece_back_off(p)):
            w, d, h = size
            qx, qy, sx, sy, _rot, front = spot
            half = max(w, d) / 2.0
            if h is not None and h > clear_h:
                why["taller than the room"] += 1
                continue
            if L._over_rects(inner, qx, qy, half, half):
                why["over a nested room"] += 1
                continue
            if not L._seed_clear(spec, room, qx, qy, [], half=half):
                # which part of the clearance: re-ask with each named neighbour removed is too invasive here; say
                # where the spot is and what stands nearest it ON THIS STOREY, by `_seed_clear`'s own storey test
                # (a volume carries no storey, only its centre z). The first version filtered on a `story` key no
                # volume has and then `or True`, so it named a basement rack beside a ground-floor spot. Nearest
                # is a measurement, not the blocker: the distance is |dx| + |dy| between centres.
                sh = L._story_height(spec)
                near = sorted(((abs(v["x"] - qx) + abs(v["y"] - qy), v["name"]) for v in spec.get("volumes") or []
                               if L._on_storey(float(v.get("z", 0.0)), float(v.get("size_z", 0.0)),
                                               story * sh, sh)))[:2]
                why["_seed_clear refuses"] += 1
                spots.append(((round(qx, 2), round(qy, 2)), near))
                continue
            why["passes the loop's tests"] += 1
print(sys.argv[2], room["id"], "bounds", room["bounds"], "clear_h", clear_h, "sizes", sizes)
print("rejections:", dict(why))
for s in spots[:10]:
    print("   refused at", s[0], "nearest:", [(round(d, 2), n) for d, n in s[1]])
