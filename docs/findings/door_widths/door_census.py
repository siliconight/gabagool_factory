"""Every door in Deli Counter's library against the contract's `min_door_width_m` (roadmap 197).

    python docs/findings/door_widths/door_census.py

Reads each library spec in `deli_counter/specs/` -- the `lf_*` workspace transients left out, as
`build.py --all` leaves them -- and each door opening on its exterior walls and partitions. A door with no
`width` is read off the built shell, `deli_counter/build/<spec>.gameplay.json`, which records each opening at
the width the builder gave it: the shell's door widths less the spec's authored ones are the rest's. A spec whose
shell does not account for its doors that way is named, and its width-less doors are not counted. Empties (`facade` true)
are counted apart: their doors are shut and nothing walks through them.

Prints the contract's number and the one its own formula gives at its own bake cell, then the doors by width,
and the buildings carrying a door under the contract's number. Prints what it measured and stops.
"""
import collections
import json
import math
import pathlib

F = pathlib.Path(__file__).resolve().parents[3]
DC = F / "deli_counter"


def _doors(spec):
    for wall in (spec.get("ext_walls") or []) + (spec.get("partitions") or []):
        for o in wall.get("openings") or []:
            if o.get("kind") == "door":
                yield o


def main():
    contract = json.loads((DC / "agent_contract.json").read_text(encoding="utf-8"))
    need = float(contract["clearances"]["min_door_width_m"])
    radius = float(contract["nav_bake"]["agent_radius_m"])
    cell = float(contract["nav_bake"]["cell_size_m"])
    # the contract's own formula, `clearances.derivation`: 2 x ceil(radius / cell) x cell + 2 x cell
    formula = 2 * math.ceil(round(radius / cell, 6)) * cell + 2 * cell
    print("contract: min_door_width_m %.2f; its formula at nav_bake.cell_size_m %.2f and agent_radius_m %.2f"
          " gives %.2f" % (need, cell, radius, formula))
    widths = collections.Counter()
    shut = collections.Counter()
    under = collections.Counter()
    unread = []
    specs = sorted(p for p in (DC / "specs").glob("*.json") if not p.stem.startswith("lf_"))
    for p in specs:
        s = json.loads(p.read_text(encoding="utf-8"))
        doors = list(_doors(s))
        sized = [round(float(o["width"]), 2) for o in doors if o.get("width") is not None]
        bare = len(doors) - len(sized)
        if bare:
            # A WIDTH-LESS DOOR is read off the built shell: its door widths, less the spec's authored ones,
            # are the widths the builder gave the rest. The counts must agree or the shell is not this spec.
            gp = DC / "build" / (p.stem + ".gameplay.json")
            built = (json.loads(gp.read_text(encoding="utf-8")).get("openings") or []) if gp.exists() else []
            rest = collections.Counter(round(float(b["width"]), 2) for b in built
                                       if b.get("kind") == "door" and "width" in b)
            rest.subtract(collections.Counter(sized))
            given = [w for w, c in rest.items() for _ in range(max(c, 0))]
            if len(given) != bare or any(c < 0 for c in rest.values()):
                unread.append(p.stem)
                given = []
            sized += given
        for w in sized:
            if s.get("facade"):
                shut[w] += 1
                continue
            widths[w] += 1
            if w < need:
                under[p.stem] += 1
    enterable = sum(1 for p in specs if not json.loads(p.read_text(encoding="utf-8")).get("facade"))
    print("library specs %d, %d enterable; doors in them %d, shut doors in Empties %d" % (
        len(specs), enterable, sum(widths.values()), sum(shut.values())))
    print("enterable doors by width (m: count):")
    for w in sorted(widths):
        print("  %.2f: %d%s" % (w, widths[w], "   under the contract's %.2f" % need if w < need else ""))
    print("enterable doors under %.2f: %d, in %d of %d buildings; at or over the formula's %.2f: %d" % (
        need, sum(under.values()), len(under), enterable, formula,
        sum(c for w, c in widths.items() if formula <= w < need)))
    for name, c in under.most_common():
        print("  %-44s %d" % (name, c))
    if unread:
        print("width-less doors left uncounted, the shell not accounting for them: %s"
              % ", ".join(sorted(set(unread))))


if __name__ == "__main__":
    main()
