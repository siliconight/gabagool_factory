"""What refurnishing arena_a02 moved once its barricades were off and its queue on: `migrate_furnish_recipes.migrate`
run on the spec as `migrate_ticket_queue` left it (kept here, `arena_a02_queued_before_refurnish.json`), every volume
that moved, appeared or went, by name; and the same pass run on 0.242.0's spec (`arena_a02_0242.json`), the control,
which the library's fixed point says moves nothing. Plan coordinates the building's, metres.

    python docs/findings/ticket_queue_267/refurnish_moves.py

Prints what it measured and stops.
"""
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DC = os.path.join(HERE, "..", "..", "..", "deli_counter")
sys.path.insert(0, DC)
os.chdir(DC)

import migrate_furnish_recipes  # noqa: E402

for label, name in (("queued, before the refurnish", "arena_a02_queued_before_refurnish.json"),
                    ("0.242.0, the control", "arena_a02_0242.json")):
    d = json.load(open(os.path.join(HERE, name), encoding="utf-8"))
    full = copy.deepcopy(d)
    removed, added = migrate_furnish_recipes.migrate(full)
    a = {v["name"]: v for v in d["volumes"]}
    b = {v["name"]: v for v in full["volumes"]}
    moved = [n for n in sorted(set(a) & set(b)) if a[n] != b[n]]
    print("== %s (%s): furnish stripped %d, placed %d; %d moved, %d appeared, %d went" % (
        label, name, removed, added, len(moved), len(set(b) - set(a)), len(set(a) - set(b))))
    for n in moved:
        print("   %s: (%.2f, %.2f) -> (%.2f, %.2f)" % (n, a[n]["x"], a[n]["y"], b[n]["x"], b[n]["y"]))
    others = [k for k in d if k != "volumes" and d[k] != full[k]]
    print("   other keys moved: %s" % (others or "none"))
