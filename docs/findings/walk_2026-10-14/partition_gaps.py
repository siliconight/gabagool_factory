"""Partitions that stop short of where the rooms they divide meet (the walk's finding 5, 2026-10-14).

    python docs/findings/walk_2026-10-14/partition_gaps.py [--min 1.0]

For every Deli Counter spec under `deli_counter/specs/`, and every partition in it: the partition is a wall along
its `axis` at `pos`, from `start` to `end`, on its `story` (spec metres, the building's frame). Two rooms on that
story MEET along that line where one's bound is the line's `pos` on one side and the other's on the other, and
their spans along the axis overlap. Wherever such a meeting runs past either end of the partition by more than
`--min` metres, that stretch has no wall -- an opening the spec never names as one. Other partitions on the same
line are counted as wall, so a run split into two pieces is not reported.

Prints each gap (spec, story, axis, pos, the partition's span, the open stretch, the two rooms, its length) and a
count per spec, and stops. Names no cause: whether a gap is designed is for the reader.
"""
import argparse
import json
import pathlib

F = pathlib.Path(__file__).resolve().parents[3]
SPECS = F / "deli_counter" / "specs"
EPS = 1e-6


def _story(item):
    return int(item.get("story", 0))


def _room_side(room, axis, pos):
    """'lo' when the room's far bound is `pos` (it lies below the line), 'hi' when its near bound is, else None;
    and its span along the line. A room's bounds are [x0, y0, x1, y1]."""
    x0, y0, x1, y1 = room["bounds"]
    if axis == "X":      # a wall along X at y = pos
        if abs(y1 - pos) < EPS:
            return "lo", (min(x0, x1), max(x0, x1))
        if abs(y0 - pos) < EPS:
            return "hi", (min(x0, x1), max(x0, x1))
    else:                # a wall along Y at x = pos
        if abs(x1 - pos) < EPS:
            return "lo", (min(y0, y1), max(y0, y1))
        if abs(x0 - pos) < EPS:
            return "hi", (min(y0, y1), max(y0, y1))
    return None, None


def _minus(span, cover):
    """The parts of `span` that no interval in `cover` covers."""
    out = [span]
    for a, b in cover:
        nxt = []
        for s, e in out:
            if b <= s or a >= e:
                nxt.append((s, e))
                continue
            if a > s:
                nxt.append((s, a))
            if b < e:
                nxt.append((b, e))
        out = nxt
    return out


def main(min_gap):
    total, specs_with = 0, 0
    for path in sorted(SPECS.glob("*.json")):
        try:
            spec = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            print("UNREADABLE %s: %s" % (path.name, exc))
            continue
        parts = spec.get("partitions") or []
        rooms = [r for r in spec.get("rooms") or [] if isinstance(r.get("bounds"), list) and len(r["bounds"]) == 4]
        found = []
        lines = sorted({(_story(p), p.get("axis"), float(p.get("pos", 0.0))) for p in parts})
        for story, axis, pos in lines:
            walls = [(min(p["start"], p["end"]), max(p["start"], p["end"])) for p in parts
                     if _story(p) == story and p.get("axis") == axis and abs(float(p.get("pos", 0.0)) - pos) < EPS]
            lo, hi = [], []
            for r in rooms:
                if _story(r) != story:
                    continue
                side, span = _room_side(r, axis, pos)
                if side == "lo":
                    lo.append((r["id"], span))
                elif side == "hi":
                    hi.append((r["id"], span))
            for a_id, (a0, a1) in lo:
                for b_id, (b0, b1) in hi:
                    meet = (max(a0, b0), min(a1, b1))
                    if meet[1] - meet[0] <= EPS:
                        continue
                    for s, e in _minus(meet, walls):
                        if e - s > min_gap:
                            found.append((story, axis, pos, walls, (s, e), a_id, b_id))
        if found:
            specs_with += 1
            for story, axis, pos, walls, (s, e), a_id, b_id in found:
                total += 1
                print("%-28s story %2d  wall along %s at %6.2f  built %-22s open %7.2f..%7.2f (%5.2f m)  %s | %s"
                      % (path.stem, story, axis, pos, ",".join("%g..%g" % w for w in walls) or "none", s, e, e - s,
                         a_id, b_id))
    print("%d open stretches over %.2f m, in %d of %d specs" % (total, min_gap, specs_with,
                                                                 len(list(SPECS.glob("*.json")))))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--min", type=float, default=1.0, help="report open stretches longer than this, metres")
    main(ap.parse_args().min)
