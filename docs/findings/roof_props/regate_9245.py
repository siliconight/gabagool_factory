"""Re-gate cold run 9245's composed buildings with the Deli Counter checked out beside this factory:
the circulation gate's three arms (shell, dressing, roofprops), per building, counted. Run once on
0.209.0 (eight roof conflicts, all stair columns) and once on 0.209.1 (the column bounded to the
floors the stair serves): the difference is what the fix owns, and the dressing and shell arms must
not move. Prints what it measured and stops.

    python docs/findings/roof_props/regate_9245.py [cold-9245-ws]
"""
import json
import os
import sys

F = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
WS = sys.argv[1] if len(sys.argv) > 1 else "cold-9245-ws"
sys.path.insert(0, os.path.join(F, "deli_counter"))
import circulation  # noqa: E402  (the checkout's own, whatever version it is)

JOBS = os.path.join(F, "workspaces", WS, ".level_factory", "jobs")
COMPOSE = os.path.join(JOBS, "restaurant_row_001.presentation_compose", "1", "out", "presentation", "lot")
version = open(os.path.join(F, "deli_counter", "VERSION"), encoding="utf-8").read().strip()
print("gate:", version, "| workspace:", WS)
total = {"shell": 0, "dressing": 0, "roofprops": 0}
for bid in sorted(os.listdir(COMPOSE)):
    out = os.path.join(COMPOSE, bid)
    man_p = os.path.join(out, "portable_resource_manifest.json")
    if not os.path.isfile(man_p):
        continue
    man = json.load(open(man_p, encoding="utf-8"))
    layers = man.get("content_layers") or {}
    # the slots and gameplay this building was composed from: the library's, by id
    slots_p = os.path.join(F, "deli_counter", "build", bid + ".slots.json")
    game_p = os.path.join(F, "deli_counter", "build", bid + ".gameplay.json")
    if not os.path.isfile(slots_p):
        print(f"  {bid:22s} no library slots for it (the mission shell?) -- skipped")
        continue
    slots = json.load(open(slots_p, encoding="utf-8"))
    gameplay = json.load(open(game_p, encoding="utf-8")) if os.path.isfile(game_p) else {}
    row = []
    greybox = os.path.join(F, "deli_counter", "build", bid + ".glb")
    if os.path.isfile(greybox):
        r = circulation.check_shell(greybox, slots, gameplay)
        row.append(("shell", len(r.get("conflicts") or []), r.get("volumes")))
        total["shell"] += len(r.get("conflicts") or [])
    for sub in ("dressing", "roofprops"):
        if layers.get(sub):
            r = circulation.check_dressing(os.path.join(out, "art", sub, layers[sub]), slots, gameplay)
            cs = r.get("conflicts") or []
            row.append((sub, len(cs), r.get("volumes")))
            total[sub] += len(cs)
            for c in cs:
                row.append(("   ", f"{c.get('prop')} {c.get('penetration')} m into {c.get('volume')}", ""))
    print(f"  {bid:22s} " + "; ".join(f"{a} {b}" + (f" ({c} vol)" if c != "" else "") for a, b, c in row))
print("conflicts by arm:", total)
