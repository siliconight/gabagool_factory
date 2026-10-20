"""What Zoo plans for the slots Deli Counter 0.240.0 re-routed: its own `kit.plan_kit` (pure Python, no Blender) over
just those slots of the rebuilt library, the theme the levels build in. A slot whose species Zoo cannot build at its dims
comes back in `species_fallbacks` and builds as the box; this prints every planned stem and every fallback, and exits 1
when a re-routed slot does not plan as its species.

    python patches/dc_one_word_species/zoo_plan_check.py
"""
import json
import pathlib
import sys

F = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(F / "zoo"))
from zoo_keeper.core import kit  # noqa: E402

WANT = {("bank", "roof_ac"): "hvac_unit", ("foundry_heist_vertical", "roof_ac_block_a"): "hvac_unit",
        ("foundry_heist_vertical", "roof_ac_block_b"): "hvac_unit", ("primos_pizza", "club_bar"): "counter",
        ("strip_retail_a01", "club_bar"): "counter"}
bad = 0
for spec in sorted({s for s, _n in WANT}):
    d = json.load(open(F / "deli_counter" / "build" / (spec + ".slots.json"), encoding="utf-8"))
    slots = [s for s in d["slots"] if (spec, s["slot_id"]) in WANT]
    for s in slots:
        if s.get("species") != WANT[(spec, s["slot_id"])]:
            print("NOT RE-ROUTED: %s %s carries species %r" % (spec, s["slot_id"], s.get("species")))
            bad += 1
    plan = kit.plan_kit({"building_id": spec, "slots": slots}, theme="delco_1997", style=1)
    for m in plan["modules"]:
        print("%-24s %s" % (spec, m["stem"]))
    for fb in plan.get("species_fallbacks") or []:
        print("FALLBACK %s: %s" % (spec, fb))
        bad += 1
print("re-routed slots planned: %d; problems: %d" % (len(WANT), bad))
sys.exit(1 if bad else 0)
