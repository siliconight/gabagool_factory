"""Deli Counter's circulation gate, as the installed `circulation.py` has it,
on every building cold run 9187 shipped: the export's dressing GLBs, and the
library's greybox, slots and gameplay. Measures; names no cause.

    python gate_on_9187.py [workspace]
"""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
DC = os.path.join(ROOT, "deli_counter")
sys.path.insert(0, DC)
import circulation  # noqa: E402

WS = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "workspaces", "cold-9187-ws")
LOT = os.path.join(WS, ".level_factory", "exports", "LF_restaurant_row_001.portable-godot", "lot")


def main():
    print("circulation.py has dressing_part_boxes:", hasattr(circulation, "dressing_part_boxes"))
    for b in sorted(os.listdir(LOT)):
        build = os.path.join(DC, "build")
        slots = json.load(open(os.path.join(build, b + ".slots.json"), encoding="utf-8"))
        gp = json.load(open(os.path.join(build, b + ".gameplay.json"), encoding="utf-8"))
        dressing = os.path.join(LOT, b, "art", "dressing", b + "_dressing.glb")
        d = circulation.check_dressing(dressing, slots, gp) if os.path.exists(dressing) else None
        s = circulation.check_shell(os.path.join(build, b + ".glb"), slots, gp)
        print("%-20s dressing %s | shell ok=%s props=%s conflicts=%s excused=%s" % (
            b,
            "none" if d is None else "ok=%s nodes=%s parts=%s conflicts=%d" % (
                d["ok"], d.get("nodes"), d["props"], len(d["conflicts"])),
            s["ok"], s["props"],
            [(c["prop"], c["volume"], c["penetration"]) for c in s["conflicts"]],
            [(c["prop"], c["volume"]) for c in s.get("excused", [])]))


if __name__ == "__main__":
    main()
