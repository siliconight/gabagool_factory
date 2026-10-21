"""landmark_hall_a01's artifact_room through 0.252.0's refurnish, step by step (argv: the 0.252.0 clone, the 0.251.0
checkout): 0.251.0's library spec; after `migrate_furnish_recipes.migrate` with 0.252.0's furnish; after
`migrate_shelter.migrate`. At each step, the room's pieces (name, position, footprint) against 0.251.0's, and whether it
has shelter. Read-only (works on a copy, in memory)."""
import copy
import json
import os
import sys

clone, base = sys.argv[1], sys.argv[2]
sys.path.insert(0, clone)
import level_design as L  # noqa: E402
import migrate_furnish_recipes as M  # noqa: E402
import migrate_shelter as MS  # noqa: E402

assert os.path.samefile(L.__file__, os.path.join(clone, "level_design.py"))
d0 = json.load(open(os.path.join(base, "specs", "landmark_hall_a01.json"), encoding="utf-8"))
room = next(r for r in d0["rooms"] if r["id"] == "artifact_room")
x0, y0, x1, y1 = room["bounds"]


def pieces(d):
    return {v["name"]: (v["x"], v["y"], v["size_x"], v["size_y"]) for v in d["volumes"]
            if x0 <= v["x"] <= x1 and y0 <= v["y"] <= y1 and v.get("collision") != "none"}


ref = pieces(d0)
d = copy.deepcopy(d0)
for label, step in (("0.251.0's spec", None), ("after migrate_furnish_recipes", M.migrate),
                    ("after migrate_shelter", MS.migrate)):
    if step:
        step(d)
    now = pieces(d)
    diff = {n: (ref.get(n), now.get(n)) for n in set(ref) | set(now) if ref.get(n) != now.get(n)}
    print("== %s: has_shelter %s; differs from 0.251.0 in %d piece(s)" % (label, L._room_has_shelter(d, room),
                                                                          len(diff)))
    for n in sorted(diff):
        print("   %-40s %s -> %s" % (n, diff[n][0], diff[n][1]))
