"""What Zoo plans for the slots Deli Counter 0.243.0 lays: its own `kit.plan_kit` (pure Python, no Blender) over
arena_a02's four stanchion-run slots of the rebuilt library, at the theme the levels build in. Copied from
`patches/dc_crowd_barrier/zoo_plan_check.py`, its slots and kind changed. A slot whose species Zoo cannot build at its dims
comes back in `species_fallbacks` and builds as the box; this prints every planned stem and every fallback, and exits 1
when a re-routed slot does not plan as its species, or carries a kind that tags its stem `_m`.

    python patches/dc_ticket_queue/zoo_plan_check.py
"""
import json
import pathlib
import sys

F = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(F / "zoo"))
from zoo_keeper.core import kit  # noqa: E402

WANT = {("arena_a02", "stanchion_run_0_%d" % n): "stanchion_run" for n in range(4)}
bad = 0
for spec in sorted({s for s, _n in WANT}):
    d = json.load(open(F / "deli_counter" / "build" / (spec + ".slots.json"), encoding="utf-8"))
    slots = [s for s in d["slots"] if (spec, s["slot_id"]) in WANT]
    if len(slots) != len([k for k in WANT if k[0] == spec]):
        print("MISSING: %s has %d of the re-routed slots" % (spec, len(slots)))
        bad += 1
    for s in slots:
        if s.get("species") != WANT[(spec, s["slot_id"])] or s.get("material") != "metal_painted":
            print("NOT RE-ROUTED: %s %s carries species %r in %r" % (spec, s["slot_id"], s.get("species"),
                                                                      s.get("material")))
            bad += 1
    plan = kit.plan_kit({"building_id": spec, "slots": slots}, theme="delco_1997", style=1)
    for m in plan["modules"]:
        print("%-24s %s" % (spec, m["stem"]))
        if "_m" in m["stem"].rsplit("_h", 1)[-1]:
            print("TAGGED: %s's stem carries a kind" % m["stem"])
            bad += 1
    for fb in plan.get("species_fallbacks") or []:
        print("FALLBACK %s: %s" % (spec, fb))
        bad += 1
print("re-routed slots planned: %d; problems: %d" % (len(WANT), bad))
sys.exit(1 if bad else 0)
