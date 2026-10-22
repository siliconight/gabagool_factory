"""Does Deli Counter's `room_necks` read what the factory's census reads? Over twelve specs 0.256.0 leaves alone --
every twelfth of the census's specs, the 17 it changes taken out -- each room's endpoints from both, and every pair's
furnished bottleneck from the census (`docs/findings/furnish_route_cost/route_cost.json`, 0.252.0's library, which
0.253.0 to 0.256.0 leave as it was for these specs) against `room_necks` on the spec as it stands. Prints the rooms and
pairs compared, every pair that differs by more than a millimetre, every endpoint list that differs, and the time;
writes census_agreement.out.txt beside this file.

    python patches/dc_desk_move/census_agreement.py
"""
import json
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
F = HERE.parents[1]
DC = F / "deli_counter"
sys.path.insert(0, str(DC))
import level_design as L  # noqa: E402

assert pathlib.Path(L.__file__).resolve().parent == DC.resolve()
CHANGED = {"airport_terminal_a03", "auto_shop_a01", "auto_shop_a02", "bank_branch_a02",
           "cbp_town_finale_midbalanced_schemafixed", "clinic_a02", "courthouse_a01", "courthouse_a03",
           "credit_union_a01", "gs_auto_shop", "landmark_hall_a01", "mansion_a03", "marina_a02", "museum_a01",
           "night_auto", "office", "train_yard_a03"}
rows = json.load(open(F / "docs" / "findings" / "furnish_route_cost" / "route_cost.json", encoding="utf-8"))
specs = sorted({r["spec"] for r in rows} - CHANGED)
pick = specs[::max(1, len(specs) // 12)][:12]
base = {(r["spec"], r["room"]): r for r in rows}
out = ["# room_necks (Deli Counter %s) against the factory's census, furnished arm, on specs this change leaves alone"
       % (DC / "VERSION").read_text(encoding="utf-8").split()[-1]]
checked = differ = rooms = 0
eps_differ = []
slowest = (0.0, None)
t0 = time.time()
for name in pick:
    d = json.load(open(DC / "specs" / (name + ".json"), encoding="utf-8"))
    for room in d["rooms"]:
        row = base.get((name, room["id"]))
        if not row:
            continue
        if [(e[0], str(e[1])) for e in row["endpoints"]] != [(k, str(lab)) for k, lab, _x, _y in
                                                             L.room_route_endpoints(d, room)]:
            eps_differ.append("%s/%s" % (name, room["id"]))
            continue
        t1 = time.time()
        ours = L.room_necks(d, room)
        dt = time.time() - t1
        if dt > slowest[0]:
            slowest = (dt, "%s/%s %.0f m2" % (name, room["id"], row["area"]))
        rooms += 1
        theirs = {tuple(int(x) for x in k.split("-")): v for k, v in row["arms"]["furnished"]["bottleneck"].items()}
        for q, v in sorted(theirs.items()):
            checked += 1
            got = ours.get(q)
            if got is None or abs(got - v) > 1e-3:
                differ += 1
                out.append("  differs: %s/%s %s census %.3f room_necks %s" % (name, room["id"], q, v, got))
        for q in sorted(set(ours) - set(theirs)):
            out.append("  only room_necks: %s/%s %s %.3f" % (name, room["id"], q, ours[q]))
out.append("specs: %s" % ", ".join(pick))
out.append("rooms %d, pairs %d, differing by more than a millimetre %d; endpoint lists differing %d %s"
           % (rooms, checked, differ, len(eps_differ), eps_differ))
out.append("%.1f s in all; slowest room %.2f s, %s" % (time.time() - t0, slowest[0], slowest[1]))
txt = "\n".join(out) + "\n"
(HERE / "census_agreement.out.txt").write_text(txt, encoding="utf-8", newline="\n")
print(txt)
