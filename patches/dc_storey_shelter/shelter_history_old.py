"""When did each library room the shelter pass fills -- and whose 0.248.0 test already read it shelterless -- lose what
sheltered it? Read-only: `git log` / `git show` on the real deli_counter (argv[1]); run from the dc_storey clone, whose
level_design supplies 0.249.0's storey test. For each room, walk its spec's commits newest to oldest and print, at each
commit that changed either answer, two lists: the pieces on the room's own storey at least `_COVER_HIGH_Z` tall and
the cover_high markers on that storey, by 0.249.0's test ("what stood there"); and what 0.248.0's `_room_has_shelter`
test accepted -- the float window on a volume, no storey on a marker -- with each piece's foot ("what the old test let
in"). A first version printed only the first list, and could not tell a room the leak covered from one nothing ever
did."""
import json
import os
import subprocess
import sys

real = sys.argv[1]
sys.path.insert(0, os.getcwd())
import level_design as L  # noqa: E402

ROOMS = [("cbp_town_finale_midbalanced_schemafixed", "main_concourse"),
         ("cbp_town_finale_midbalanced_schemafixed", "club_ring_overlook"),
         ("freight_terminal_a02", "gantry_control"),
         ("parking_garage_a02", "attendant_booth"),
         ("primos_pizza", "rear_hall"),
         ("rail_station_a02", "vault_approach"),
         ("rowhouse_raid", "basement_vault"),
         ("warehouse_a01", "back_corridor")]


def git(*a):
    return subprocess.run(["git", "-C", real] + list(a), capture_output=True, text=True, encoding="utf-8").stdout


def shelter_in(d, room_id):
    room = next((r for r in d.get("rooms", []) if r["id"] == room_id), None)
    if room is None:
        return None
    x0, y0, x1, y1 = room["bounds"]
    sh = L._story_height(d)
    floor = room.get("story", 0) * sh
    out = []
    for v in d.get("volumes", []):
        h = float(v.get("size_z", 0))
        if h < L._COVER_HIGH_Z or min(v.get("size_x", 0), v.get("size_y", 0)) < 0.3:
            continue
        if x0 <= v["x"] <= x1 and y0 <= v["y"] <= y1 and L.stands_on_storey(float(v.get("z", 0)), h, floor, sh):
            out.append("%s(%.2f)" % (v["name"], h))
    for m in d.get("markers", []):
        if m.get("type") == "cover_high" and x0 <= m.get("x", 1e9) <= x1 and y0 <= m.get("y", 1e9) <= y1 \
                and L.marker_on_storey(m, floor, sh):
            out.append("marker:%s" % m.get("id"))
    return sorted(out)


def old_answer(d, room_id):
    """0.248.0's `_room_has_shelter` test, verbatim in shape: the float window on a volume, no storey on a marker."""
    room = next((r for r in d.get("rooms", []) if r["id"] == room_id), None)
    if room is None:
        return None
    if not room.get("combat_range"):
        return "NO COMBAT_RANGE"
    x0, y0, x1, y1 = room["bounds"]
    if (x1 - x0) * (y1 - y0) < L._SEED_MIN_AREA:
        return "UNDER _SEED_MIN_AREA"
    sh = L._story_height(d)
    floor = room.get("story", 0) * sh
    out = []
    for v in d.get("volumes", []):
        h = float(v.get("size_z", 0))
        if h < L._COVER_HIGH_Z or min(v.get("size_x", 0), v.get("size_y", 0)) < 0.3:
            continue
        if x0 <= v["x"] <= x1 and y0 <= v["y"] <= y1 and abs(float(v.get("z", 0)) - (floor + h / 2)) < sh:
            out.append("%s(%.2f@%.2f)" % (v["name"], h, float(v.get("z", 0)) - h / 2))
    for m in d.get("markers", []):
        if m.get("type") == "cover_high" and x0 <= m.get("x", 1e9) <= x1 and y0 <= m.get("y", 1e9) <= y1:
            out.append("marker:%s@%s" % (m.get("id"), m.get("z")))
    return sorted(out)


for spec, room_id in ROOMS:
    path = "specs/%s.json" % spec
    revs = git("log", "--format=%h %s", "--", path).splitlines()
    print("== %s / %s: %d commits touch the spec" % (spec, room_id, len(revs)))
    prev = None
    for line in revs:
        h, subj = line.split(" ", 1)
        try:
            d = json.loads(git("show", "%s:%s" % (h, path)))
        except ValueError:
            continue
        s = (shelter_in(d, room_id), old_answer(d, room_id))
        if s != prev:
            print("   %s %-50.50s -> own storey %s | 0.248.0's test %s" % (h, subj, s[0] if s[0] else "none", s[1] if s[1] else "none"))
            prev = s
