"""Diff of the ceiling rows two Deli Counter trees derive for the same furnished library.

    python docs/findings/fixture_rows/aisle_rows_diff.py <before root> <after root>

Loads every library spec of the BEFORE tree (`build._spec_paths()`), furnishes it once with that
tree's `level_design.furnish`, and derives the light anchors with each tree's `lights.py`
(`derive_light_anchors`, the same arguments: the rooms, no openings, the story height, a 0.3 m
cap, a 0.3 m wall, the furnished volumes, the building's residence flag from its business id).
Prints, over the fluorescent anchors keyed by room: rooms identical, rooms changed, rows moved
(a row whose line differs), rows added and removed, lamps before and after, and the rooms the
after tree reports laid over their aisles (`rows_over_aisles`). It prints what it counted and
stops; the rooms with no shelving are the byte-identity claim and the rest is the change.
"""
import importlib
import json
import os
import sys


_ROOTS = []


def _load(root, names):
    """Import `names` from `root`, forgetting every module a previous root
    loaded: the trees import each other's modules lazily (`lights` asks
    `level_design`, which asks `layout_lint`), so the root stays on
    `sys.path` while its tree is in use and the previous one comes off."""
    root = os.path.abspath(root)
    for k, m in list(sys.modules.items()):
        f = os.path.abspath(getattr(m, "__file__", None) or "")
        if k in names or any(f.startswith(r + os.sep) for r in _ROOTS):
            del sys.modules[k]
    for r in _ROOTS:
        while r in sys.path:
            sys.path.remove(r)
    _ROOTS.append(root)
    sys.path.insert(0, root)
    return {n: importlib.import_module(n) for n in names}


def _rooms(spec):
    sh = float(spec.get("story_height", 3.0))
    out = []
    for r in spec.get("rooms", []):
        if not r.get("bounds"):
            continue
        b = r["bounds"]
        out.append({"id": r["id"], "story": r.get("story", 0), "bounds": b, "role": r.get("role"),
                    "objective": r.get("objective"),
                    "center": [(b[0] + b[2]) / 2.0, (b[1] + b[3]) / 2.0, float(r.get("story", 0)) * sh]})
    return out, sh


def _rows(lights, level_design, spec, rooms, sh):
    rep = {}
    business = level_design.club_building_id(spec) if hasattr(level_design, "club_building_id") else None
    anchors = lights.derive_light_anchors(rooms, [], sh, cap_thick=0.3, wall_thick=0.3,
                                          volumes=spec.get("volumes", []), report=rep,
                                          residence=lights.is_residence(business))
    by_room = {}
    for a in anchors:
        if a.get("type") == "fluorescent":
            by_room.setdefault(a.get("room"), []).append((a["id"], tuple(a["pos"]), a["rot_y"],
                                                          a["row"]["count"], a["row"]["spacing"]))
    return by_room, rep.get("rows_over_aisles", 0)


def main():
    before_root, after_root = sys.argv[1], sys.argv[2]
    before = _load(before_root, ("build", "level_design", "lights", "agent_contract"))
    specs = []
    for p in before["build"]._spec_paths():
        if p.endswith(".json"):
            spec = json.load(open(p, encoding="utf-8"))
            before["level_design"].furnish(spec)
            specs.append((os.path.basename(p), spec))
    rows_b = {}
    for name, spec in specs:
        rooms, sh = _rooms(spec)
        rows_b[name] = _rows(before["lights"], before["level_design"], spec, rooms, sh)[0]
    after = _load(after_root, ("build", "level_design", "lights", "agent_contract"))
    same = changed = moved = added = removed = over = fewer = 0
    lamps_b = lamps_a = 0
    examples = []
    for name, spec in specs:
        rooms, sh = _rooms(spec)
        got, n_over = _rows(after["lights"], after["level_design"], spec, rooms, sh)
        over += n_over
        for room in set(rows_b[name]) | set(got):
            b, a = rows_b[name].get(room, []), got.get(room, [])
            lamps_b += sum(x[3] for x in b)
            lamps_a += sum(x[3] for x in a)
            if b == a:
                same += 1
                continue
            changed += 1
            lb, la = {x[1][:2] for x in b}, {x[1][:2] for x in a}
            moved += len(lb - la)
            added += max(0, len(a) - len(b))
            removed += max(0, len(b) - len(a))
            # fewer rows and more lamps a row: the long hall's trade, not an aisle
            if len(a) < len(b) and a and b and a[0][3] > b[0][3]:
                fewer += 1
            if len(examples) < 10:
                examples.append((name, room, [x[1][:2] for x in b], [x[1][:2] for x in a]))
    print("specs: %d; rooms identical: %d; rooms changed: %d (rows moved %d, added %d, removed %d)"
          % (len(specs), same, changed, moved, added, removed))
    print("lamps: %d before, %d after; rooms the after tree laid over their aisles: %d; "
          "rooms with fewer rows and more lamps a row (the long hall's trade): %d"
          % (lamps_b, lamps_a, over, fewer))
    print("examples (spec, room, before lines, after lines):")
    for e in examples:
        print("  ", e)


if __name__ == "__main__":
    main()
