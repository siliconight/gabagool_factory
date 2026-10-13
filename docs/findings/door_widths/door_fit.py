"""Do the doors fit, as built? (roadmap 197; Deli Counter 0.214.0's door widths)

    python docs/findings/door_widths/door_fit.py <deli_counter dir> [<spec> ...]

Reads each named shell's `build/<spec>.gameplay.json` -- every opening the builder cut, where it cut it (the
centre snapped to the building's grid) and how wide -- in the given Deli Counter directory (the repository, or a
scratch copy being tried). With no specs named, every built shell that is not an Empty. For each wall run (one
`wall` name on one storey) the openings are laid along the run's axis -- the one their centres vary along -- and
any two whose spans overlap are named; so is any walkable door narrower than the contract's
`min_door_width_m`. Prints what it found and stops; exit 1 when it found anything.
"""
import collections
import json
import pathlib
import sys

KEPT = {("primos_pizza", "kitchen_stairs")}   # left narrow, named in migrate_door_width.KEPT


def main():
    dc = pathlib.Path(sys.argv[1])
    need = float(json.loads((dc / "agent_contract.json").read_text(encoding="utf-8"))
                 ["clearances"]["min_door_width_m"])
    names = sys.argv[2:] or sorted(p.name[:-len(".gameplay.json")] for p in (dc / "build").glob("*.gameplay.json"))
    found = 0
    checked = 0
    for name in names:
        gp = dc / "build" / (name + ".gameplay.json")
        if not gp.exists():
            print("%s: NOT BUILT" % name)
            found += 1
            continue
        d = json.loads(gp.read_text(encoding="utf-8"))
        ops = d.get("openings") or []
        if not ops:
            continue
        checked += 1
        runs = collections.defaultdict(list)
        for o in ops:
            runs[(o.get("wall"), o.get("story"))].append(o)
            if (o.get("kind") == "door" and float(o["width"]) < need - 1e-9
                    and (name, o.get("tag")) not in KEPT):
                print("%s: door %s on %s storey %s is %.2f m" % (name, o.get("tag"), o.get("wall"),
                                                                 o.get("story"), float(o["width"])))
                found += 1
        for (wall, story), group in runs.items():
            if len(group) < 2:
                continue
            xs = {round(float(o["x"]), 3) for o in group}
            key = "y" if len(xs) == 1 else "x"
            spans = sorted((float(o[key]) - float(o["width"]) / 2, float(o[key]) + float(o["width"]) / 2,
                            o.get("kind"), o.get("tag")) for o in group)
            for a, b in zip(spans, spans[1:]):
                if b[0] < a[1] - 1e-6:
                    print("%s: on %s storey %s the %s %s (%.2f..%.2f) overlaps the %s %s (%.2f..%.2f)" % (
                        name, wall, story, a[2], a[3], a[0], a[1], b[2], b[3], b[0], b[1]))
                    found += 1
    print("%d shell(s) read, %d finding(s)" % (checked, found))
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
