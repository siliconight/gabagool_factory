"""arena_a02's four barrier slots, as Deli Counter 0.242.0 is to write them: Deli Counter 0.241.0's own built slots
(`deli_counter/build/arena_a02.slots.json`) with the two fields 0.242.0 changes: `species`, which the word
`barrier` sets to `crowd_barrier`, and `material`, the species' own kind `metal_bare` where the spec wrote `metal` (the
dartboard's rule in `level_design._PROP_MATERIALS`: a slot in its species' own kind carries no `_m` in Zoo's stem, and
the genome's galvanised grey shows). The input for `zoo_cli --build-kit`, which builds what Zoo would ship for them.

    python patches/zoo_crowd_barrier/make_kit_slots.py <out.slots.json>

CORRECTED, kept: these slots keep 0.241.0's `style`, 4. Deli Counter 0.242.0 as it shipped also DECLARES `metal_bare`,
tenth in arena_a02's palette, and a slot's style is its material's place in the palette, so the slots it writes carry
style 10 and the stem is `prop_crowd_barrier_delco_1997_10_w300_d80_h120`, not this run's `_04_`. Built from the real
rebuilt slots (`patches/dc_crowd_barrier/kit_real_slots.log`, `kit_real_slots_glb_facts.out.txt`): the same module --
476 tris, one material `M_CrowdBarrier_metal_bare`, the same bounds -- under that name.
"""
import json
import pathlib
import sys

F = pathlib.Path(__file__).resolve().parents[2]
src = json.loads((F / "deli_counter" / "build" / "arena_a02.slots.json").read_text(encoding="utf-8"))
slots = [s for s in src["slots"] if s.get("slot_id", "").startswith("barrier_")]
assert [s["slot_id"] for s in slots] == ["barrier_0", "barrier_1", "barrier_2", "barrier_3"], slots
for s in slots:
    assert s["species"] is None and s["material"] == "metal" and s["fit"]["dims"] == [3.0, 0.8, 1.2], s
    s["species"] = "crowd_barrier"
    s["material"] = "metal_bare"
out = dict(src)
out["building_id"] = "arena_a02_barriers"
out["slots"] = slots
pathlib.Path(sys.argv[1]).write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
print("wrote %d slots to %s" % (len(slots), sys.argv[1]))
