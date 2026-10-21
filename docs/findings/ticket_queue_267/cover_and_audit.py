"""arena_a02's fight before and after Deli Counter 0.243.0: the combat audit as the build runs it (`--rules auto`, the
heist / cqb / flow packs for its pvp_heist mode) and the event floor's cover, for 0.242.0's spec (kept here,
`arena_a02_0242.json`) and the live one.

    python docs/findings/ticket_queue_267/cover_and_audit.py

Cover is read three ways: the pieces `level_design._looks_like_cover` tags, `_room_has_cover` and `_room_has_shelter`
(what `seed_cover` asks before it adds anything), and the pieces 1.0 m or taller standing more than 3 m off every wall
of the event floor -- the middle of the room, where the barricades stood. Units metres, plan coordinates the
building's. Prints what it measured and stops.
"""
import io
import json
import os
import sys
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
DC = os.path.join(HERE, "..", "..", "..", "deli_counter")
sys.path.insert(0, DC)
os.chdir(DC)

import combat_audit  # noqa: E402
import level_design  # noqa: E402

for name, path in (("0.242.0", os.path.join(HERE, "arena_a02_0242.json")),
                   ("0.243.0", os.path.join(DC, "specs", "arena_a02.json"))):
    print("==", name, os.path.relpath(path, os.path.join(HERE, "..", "..", "..")))
    buf = io.StringIO()
    with redirect_stdout(buf):
        combat_audit.main(["--rules", "auto", path])
    print("   audit: " + "\n   audit: ".join(ln for ln in buf.getvalue().splitlines()[1:] if ln.strip()))
    d = json.load(open(path, encoding="utf-8"))
    ev = [r for r in d["rooms"] if r["id"] == "event_floor"][0]
    x0, y0, x1, y1 = ev["bounds"]
    inroom = [v for v in d["volumes"] if x0 <= v["x"] <= x1 and y0 <= v["y"] <= y1]
    tagged = sorted(v["name"] for v in inroom if level_design._looks_like_cover(v))
    print("   event floor volumes %d; cover-like %d: %s" % (len(inroom), len(tagged), ", ".join(tagged)))
    print("   _room_has_cover %s, _room_has_shelter %s" % (level_design._room_has_cover(d, ev),
                                                         level_design._room_has_shelter(d, ev)))
    mid = sorted("%s %.2f m" % (v["name"], v["size_z"]) for v in inroom
                 if v["size_z"] >= 1.0 and x0 + 3 < v["x"] < x1 - 3 and y0 + 3 < v["y"] < y1 - 3)
    print("   standing 1.0 m or taller, mid-floor: %d: %s" % (len(mid), ", ".join(mid)))
