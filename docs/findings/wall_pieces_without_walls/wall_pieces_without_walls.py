"""Furnished wall pieces with no wall behind them, across Deli Counter's specs.

    python wall_pieces_without_walls.py [--list]

Frame and units: the spec's frame, metres, footprint centred on 0.

A WALL PIECE is a volume `furnish` wrote (`migrate_furnish_recipes
.furnished_by_this_pass`) whose stem `level_design._PIECES` places on a wall
(`where == "wall"`, fixtures included). `_wall_slots` stands each one with its
back `wall_thick / 2 + _WALL_PIECE_AIR + back_off` off one of its ROOM'S
EDGES; the edge it was slotted against is the one nearest its box.

A WALL BEHIND IT is a built wall (`layout_lint.built_walls`: partition spans as
the builder cuts them, every exterior side) on the piece's storey whose
centreline lies within `TOL` of that edge and whose built span covers at
least `COVER` of the piece's run along it.

Prints what it measured. No cause.
"""
import collections
import glob
import json
import os
import sys

#: Deli Counter beside the factory root this folder sits under
DC = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "..", "..", "..", "deli_counter"))
sys.path.insert(0, DC)

import layout_lint  # noqa: E402
import level_design as L  # noqa: E402
import migrate_furnish_recipes as MF  # noqa: E402

TOL = 0.10
COVER = 0.5


def wall_stems():
    return {k for k, p in L._PIECES.items() if p.get("where") == "wall"}


def census(spec):
    stems = wall_stems()
    rooms = {L._room_tag(r): r for r in spec.get("rooms") or []}
    tags = set(rooms)
    walls = layout_lint.built_walls(spec)
    out = []
    for v in spec.get("volumes") or []:
        if not MF.furnished_by_this_pass(v, tags):
            continue
        m = MF._GENERATED.match(str(v.get("name")))
        stem, tag = m.group("stem"), m.group("tag")
        if stem not in stems:
            continue
        room = rooms[tag]
        story = int(room.get("story", 0) or 0)
        x0, y0, x1, y1 = room["bounds"]
        vx0, vx1 = v["x"] - v["size_x"] / 2.0, v["x"] + v["size_x"] / 2.0
        vy0, vy1 = v["y"] - v["size_y"] / 2.0, v["y"] + v["size_y"] / 2.0
        # the room edge the piece was slotted against: the nearest to its box
        edges = [("S", 1, y0, vy0 - y0, (vx0, vx1)), ("N", 1, y1, y1 - vy1, (vx0, vx1)),
                 ("W", 0, x0, vx0 - x0, (vy0, vy1)), ("E", 0, x1, x1 - vx1, (vy0, vy1))]
        side, n, line, gap, (a0, a1) = min(edges, key=lambda e: abs(e[3]))
        run = max(1e-9, a1 - a0)
        covered = 0.0
        for _label, wstory, wn, plane, half, spans in walls:
            if wstory != story or wn != n or abs(plane - line) > TOL:
                continue
            covered = max(covered, sum(max(0.0, min(a1, s1) - max(a0, s0)) for s0, s1 in spans) / run)
        if covered < COVER:
            out.append({"name": v["name"], "stem": stem, "room": room["id"], "edge": side,
                        "gap": round(gap, 3), "covered": round(covered, 2)})
    return out


def main(argv):
    root = os.path.join(DC, "specs")
    n_specs = n_pieces = 0
    by_stem = collections.Counter()
    shells = collections.Counter()
    total_wall_pieces = 0
    stems = wall_stems()
    for p in sorted(glob.glob(os.path.join(root, "*.json"))):
        name = os.path.basename(p)[:-5]
        if name.startswith("lf_"):
            continue
        n_specs += 1
        d = json.load(open(p, encoding="utf-8"))
        tags = {L._room_tag(r) for r in d.get("rooms") or []}
        total_wall_pieces += sum(1 for v in d.get("volumes") or []
                                 if MF.furnished_by_this_pass(v, tags)
                                 and MF._GENERATED.match(v["name"]).group("stem") in stems)
        rows = census(d)
        for r in rows:
            by_stem[r["stem"]] += 1
            shells[name] += 1
            n_pieces += 1
            if "--list" in argv:
                print("%-28s %-36s %-20s edge %s gap %.2f covered %.2f" % (
                    name, r["name"], r["room"], r["edge"], r["gap"], r["covered"]))
    print("specs read (no lf_*): %d; furnished wall pieces: %d; with no wall behind them: %d in %d shells"
          % (n_specs, total_wall_pieces, n_pieces, len(shells)))
    print("by stem:", dict(by_stem.most_common()))


if __name__ == "__main__":
    main(sys.argv[1:])
