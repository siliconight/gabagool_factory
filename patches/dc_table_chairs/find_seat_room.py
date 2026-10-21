"""In a Deli Counter checkout (argv[1]): rooms with seated hosts where furnishing the spec from bare with seats on and
with every seated piece's seats off places the same non-chair pieces (names and positions) -- what 0.252.0's
decoupling test needs -- and how many seated hosts each such room stands. Prints the first few."""
import copy
import json
import os
import re
import sys

dc = sys.argv[1]
sys.path.insert(0, dc)
import level_design as L  # noqa: E402

assert os.path.samefile(L.__file__, os.path.join(dc, "level_design.py"))
SEATED = [k for k, p in L._PIECES.items() if p.get("seats")]
CHAIR = re.compile(r"_r[0-9a-f]{8}_\d+_\d+$")


def pieces(d, tag):
    return sorted((v["name"], v["x"], v["y"]) for v in d["volumes"]
                  if "_" + tag + "_" in v["name"] and not CHAIR.search(v["name"]))


found = 0
for name in ("deli_a01", "primos_pizza", "restaurant_row_a01", "diner_a01", "country_club_a01", "brewery_a01",
             "casino_a01", "office", "courthouse_a02", "apartment_walkup_a01"):
    p = os.path.join(dc, "specs", name + ".json")
    if not os.path.exists(p):
        continue
    d0 = L.unfurnished(json.load(open(p, encoding="utf-8")))
    on = copy.deepcopy(d0)
    L.furnish(on)
    saved = {k: L._PIECES[k]["seats"] for k in SEATED}
    try:
        for k in SEATED:
            L._PIECES[k]["seats"] = None
        off = copy.deepcopy(d0)
        L.furnish(off)
    finally:
        for k, v in saved.items():
            L._PIECES[k]["seats"] = v
    for room in d0["rooms"]:
        tag = L._room_tag(room)
        hosts = [v for v in on["volumes"] if "_" + tag + "_" in v["name"]
                 and any(v["name"].startswith(k + "_") for k in SEATED) and not CHAIR.search(v["name"])]
        if len(hosts) >= 2 and pieces(on, tag) == pieces(off, tag):
            print("%s / %s: %d seated hosts, %d pieces the same with seats on and off"
                  % (name, room["id"], len(hosts), len(pieces(on, tag))))
            found += 1
print("found", found)
