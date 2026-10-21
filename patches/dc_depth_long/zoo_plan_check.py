"""What Zoo plans for the slots Deli Counter 0.245.0 records for freight_terminal_a01's four containers: its own
`kit.plan_kit` (pure Python, no Blender) over the rebuilt library's container slots, at the theme the levels build in.
Copied from `patches/dc_teller_queue/zoo_plan_check.py`, its slots changed. A slot whose species Zoo cannot build at its
dims comes back in `species_fallbacks` and builds as the box; this prints each slot as recorded, every planned stem and
every fallback, and exits 1 when a re-routed slot is not recorded 2.4 wide, 6.0 deep and turned 90, does not plan as
its species, or carries a kind that tags its stem `_m`.

    python patches/dc_depth_long/zoo_plan_check.py
"""
import json
import pathlib
import sys

F = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(F / "zoo"))
from zoo_keeper.core import kit  # noqa: E402

SPEC = "freight_terminal_a01"
WANT = {"container_%d" % n: "cargo_container" for n in range(4)}
bad = 0
d = json.load(open(F / "deli_counter" / "build" / (SPEC + ".slots.json"), encoding="utf-8"))
slots = [s for s in d["slots"] if s["slot_id"] in WANT]
if len(slots) != len(WANT):
    print("MISSING: %s has %d of the re-routed slots" % (SPEC, len(slots)))
    bad += 1
for s in slots:
    dims, rot = s["fit"]["dims"], s["transform"]["rot_y"]
    print("%-12s species %r material %r style %r dims %r rot_y %r collision %r" % (
        s["slot_id"], s.get("species"), s.get("material"), s.get("style"), dims, rot, s["fit"].get("collision")))
    if s.get("species") != WANT[s["slot_id"]] or s.get("material") != "metal_painted":
        print("NOT RE-ROUTED: %s carries species %r in %r" % (s["slot_id"], s.get("species"), s.get("material")))
        bad += 1
    if dims != [2.4, 6.0, 2.6] or rot != 90.0:
        print("NOT DEPTH-LONG: %s is recorded %r at %r" % (s["slot_id"], dims, rot))
        bad += 1
plan = kit.plan_kit({"building_id": SPEC, "slots": slots}, theme="delco_1997", style=1)
for m in plan["modules"]:
    print("%-24s %s" % (SPEC, m["stem"]))
    if "_m" in m["stem"].rsplit("_h", 1)[-1]:
        print("TAGGED: %s's stem carries a kind" % m["stem"])
        bad += 1
for fb in plan.get("species_fallbacks") or []:
    print("FALLBACK %s: %s" % (SPEC, fb))
    bad += 1
print("re-routed slots planned: %d; problems: %d" % (len(WANT), bad))
sys.exit(1 if bad else 0)
