"""Attribute every room roadmap 283's change touches. Run from the dc_storey clone (its level_design is 0.249.0's) with
the real deli_counter's path as argv[1] (its specs are 0.248.0's library). Writes nothing.

(1) For each library room the 0.249.0 shelter pass fills: what made 0.248.0's `_room_has_shelter` answer yes -- each
    volume or cover_high marker inside the room's plan that the OLD test accepted and `stands_on_storey` /
    `marker_on_storey` refuse, with its storey and height.
(2) For each COVER_ALL_LOW the 0.249.0 audit still reports after the pass: why the pass leaves the room -- its area
    against `_SEED_MIN_AREA`, a strip club room, or how many of its 36 candidates clear for each shelter choice.
Frame: spec coordinates, metres; a volume's z is its centre, a marker's z the floor it stands on."""
import json
import os
import random
import sys

real = sys.argv[1]
sys.path.insert(0, os.getcwd())
import level_design as L  # noqa: E402
import migrate_storey_shelter as MS  # noqa: E402
import combat_audit as CA  # noqa: E402
from spec_loader import spec_from_dict  # noqa: E402

SPECS = os.path.join(real, "specs")


def load(name):
    return json.load(open(os.path.join(SPECS, name + ".json"), encoding="utf-8"))


def storey_of(z_foot, sh):
    return int((z_foot + 0.05) // sh)


def old_shelter_witnesses(d, room):
    """What 0.248.0's `_room_has_shelter` accepted that 0.249.0's refuses."""
    x0, y0, x1, y1 = room["bounds"]
    sh = L._story_height(d)
    floor = room.get("story", 0) * sh
    out = []
    for v in d.get("volumes", []):
        h = float(v.get("size_z", 0))
        if h < L._COVER_HIGH_Z or min(v.get("size_x", 0), v.get("size_y", 0)) < 0.3:
            continue
        if not (x0 <= v["x"] <= x1 and y0 <= v["y"] <= y1):
            continue
        z = float(v.get("z", 0))
        old = abs(z - (floor + h / 2)) < sh
        new = L.stands_on_storey(z, h, floor, sh)
        if old and not new:
            out.append("volume %s h %.2f foot %.3f (storey %d)" % (v["name"], h, z - h / 2, storey_of(z - h / 2, sh)))
        elif old and new:
            out.append("ON ITS OWN STOREY: %s h %.2f" % (v["name"], h))
    for m in d.get("markers", []):
        if m.get("type") == "cover_high" and x0 <= m.get("x", 1e9) <= x1 and y0 <= m.get("y", 1e9) <= y1:
            if not L.marker_on_storey(m, floor, sh):
                out.append("marker %s z %s (storey %d)" % (m.get("id"), m.get("z"), storey_of(float(m["z"]), sh)))
            else:
                out.append("ON ITS OWN STOREY: marker %s" % m.get("id"))
    return out


def why_left(d, room_id):
    room = next(r for r in d["rooms"] if r["id"] == room_id)
    x0, y0, x1, y1 = room["bounds"]
    area = max(0.0, x1 - x0) * max(0.0, y1 - y0)
    if not room.get("combat_range"):
        return "no combat_range"
    if L.is_strip_club_room(room, L.club_building_id(d)):
        return "strip club room (the club recipe's)"
    if area < L._SEED_MIN_AREA:
        return "area %.1f m2 < _SEED_MIN_AREA %.1f" % (area, L._SEED_MIN_AREA)
    if L._room_has_shelter(d, room):
        return "the producer reads it sheltered (the audit does not): INSTRUMENTS DISAGREE"
    # the pass's own candidates, drawn as it draws them
    rng = random.Random(f"{d.get('seed', 0)}:{room['id']}:seed_cover")
    cands = []
    for i in range(6):
        for j in range(6):
            px = x0 + 1.2 + (i + rng.random() * 0.6) * (x1 - x0 - 2.4) / 6
            py = y0 + 1.2 + (j + rng.random() * 0.6) * (y1 - y0 - 2.4) / 6
            cands.append((px, py))
    choices = [L._seed_shelter(room)]
    if L._SEED_SHELTER_DEFAULT not in choices:
        choices.append(L._SEED_SHELTER_DEFAULT)
    parts = []
    for s_name, s_x, s_y in choices:
        n = sum(1 for (px, py) in cands
                if L._seed_clear(d, room, px, py, [], half=max(s_x, s_y) / 2.0, corridor=True))
        parts.append("%s %.1fx%.1f clears at %d/36" % (s_name, s_x, s_y, n))
    return "area %.1f m2, %s x %s m; " % (area, round(x1 - x0, 2), round(y1 - y0, 2)) + "; ".join(parts)


filled = []
left = []
for fn in sorted(os.listdir(SPECS)):
    if not fn.endswith(".json") or fn.startswith("lf_"):
        continue
    name = fn[:-5]
    d0 = load(name)
    if not d0.get("rooms"):
        continue
    d = json.loads(json.dumps(d0))
    added = MS.migrate(d)
    for a in added:
        room_id = next(r["id"] for r in d0["rooms"] if a.endswith("_" + r["id"] + "_shelter"))
        room = next(r for r in d0["rooms"] if r["id"] == room_id)
        filled.append((name, room_id, a, old_shelter_witnesses(d0, room)))
    res = CA.audit(spec_from_dict(d), name=name)
    for f in res["findings"]:
        if f[1] == "COVER_ALL_LOW":
            rid = f[2].split("'")[1]
            left.append((name, rid, why_left(d, rid)))

print("(1) rooms the 0.249.0 shelter pass fills: %d" % len(filled))
for name, rid, piece, wit in filled:
    print("  %s / %s  +%s" % (name, rid, piece))
    for w in wit or ["NOTHING ACCEPTED BY THE OLD TEST: the room read shelterless on 0.248.0 too"]:
        print("      0.248.0 counted: " + w)
print("(2) COVER_ALL_LOW the 0.249.0 audit still reports after the pass: %d" % len(left))
for name, rid, why in left:
    print("  %s / %s: %s" % (name, rid, why))
