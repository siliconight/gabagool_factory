"""Furnish's storey filter, `level_design._room_volume_count`'s `abs(z - (story * sh + h / 2)) < sh`, printed for every
volume under bank_branch_a03's upstairs `offices` (story 1, 3.6 m storeys) in a spec file: for a piece standing on the
floor below, the quantity is exactly the storey height in exact arithmetic, so the strict `<` is decided by float
rounding. Which ground-floor pieces the upper room counts is whatever rounding says.

    python patches/dc_teller_queue/storey_filter_floats.py <deli_counter dir> [<spec json>]

The spec defaults to the deli_counter's own specs/bank_branch_a03.json. Prints repr() of each quantity and stops.
"""
import json
import os
import sys

dc = os.path.abspath(sys.argv[1])
sys.path.insert(0, dc)
import level_design  # noqa: E402

path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(dc, "specs", "bank_branch_a03.json")
spec = json.load(open(path, encoding="utf-8"))
sh = level_design._story_height(spec)
room = [r for r in spec["rooms"] if r["id"] == "offices"][0]
x0, y0, x1, y1 = room["bounds"]
print("spec %s; story height %r; room %s, story %d, bounds %s" % (os.path.basename(path), sh, room["id"],
                                                                   room["story"], room["bounds"]))
counted_below = 0
for v in spec["volumes"]:
    if not (x0 <= v["x"] <= x1 and y0 <= v["y"] <= y1):
        continue
    d = abs(v["z"] - (room["story"] * sh + v["size_z"] / 2))
    below = v["z"] - v["size_z"] / 2 < room["story"] * sh - 1e-6
    counted_below += below and d < sh
    print("%-30s z %-7r h %-6r |z - (story*sh + h/2)| = %-20r counted %-5s %s" % (
        v["name"], v["z"], v["size_z"], d, d < sh, "(stands on a floor below)" if below else ""))
print("pieces standing on a floor below that the upper room counts: %d" % counted_below)
