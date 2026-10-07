"""Deli Counter 0.197.0: open floor is a way in -- one rule, asked by tactical and lint.

    python patch_dc_open_plan.py

Anchored on tactical.py (38,491 bytes, LF) and layout_lint.py as read
2026-10-06, and on walk_reach_baseline.json as 0.194.0 wrote it; every anchor
must match exactly once or nothing is written.

WHY. L24 asked L12's graph, which joins rooms through openings, stairs and
ladders only. deli_a01's basement partition along y = 1 stops at x 12, so the
utility room's north edge from x 12 to 19 is open floor; cold run 9189's bake
walks across it on the street's island, and L24 named the room "reachable
only by breaching". 9 of the 15 rooms 0.194.0 froze were open floor.
`tactical.build_graph` has modelled open floor all along, as a closure;
lifted unchanged to `tactical.shared_open_edge`, it is now the one rule both
ask. `build_graph`'s adjacency is compared on all 128 room-bearing library
specs before and after: it must be identical.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DC = ROOT / "deli_counter"
TACT = DC / "tactical.py"
LINT = DC / "layout_lint.py"
BASE = DC / "walk_reach_baseline.json"

OLD_CLOSURE = '''    # open-plan adjacency: two same-story rooms whose rects share an edge
    # with NO partition covering it are one continuous space (a lobby flowing
    # into a bullpen). Without this, open floor plans read as disconnected
    # and open-plan rooms false-flag as dead ends. Additive only.
    def _shared_open_edge(ra, rb):
        ax0, ay0, ax1, ay1 = ra.bounds
        bx0, by0, bx1, by1 = rb.bounds
        # vertical shared edge (ra right == rb left or vice versa)
        for x_edge, lo, hi in ((ax1, max(ay0, by0), min(ay1, by1))
                               if abs(ax1 - bx0) < 0.05 else (None, 0, 0),
                               (bx1, max(ay0, by0), min(ay1, by1))
                               if abs(bx1 - ax0) < 0.05 else (None, 0, 0)):
            if x_edge is not None and hi - lo >= 1.2:
                covered = 0.0
                for p in spec.partitions:
                    if p.story != ra.story or p.axis != "Y":
                        continue
                    if abs(p.pos - x_edge) < 0.05:
                        covered += max(0.0, min(p.end, hi) - max(p.start, lo))
                if (hi - lo) - covered >= 1.2:
                    return True
        # horizontal shared edge
        for y_edge, lo, hi in ((ay1, max(ax0, bx0), min(ax1, bx1))
                               if abs(ay1 - by0) < 0.05 else (None, 0, 0),
                               (by1, max(ax0, bx0), min(ax1, bx1))
                               if abs(by1 - ay0) < 0.05 else (None, 0, 0)):
            if y_edge is not None and hi - lo >= 1.2:
                covered = 0.0
                for p in spec.partitions:
                    if p.story != ra.story or p.axis != "X":
                        continue
                    if abs(p.pos - y_edge) < 0.05:
                        covered += max(0.0, min(p.end, hi) - max(p.start, lo))
                if (hi - lo) - covered >= 1.2:
                    return True
        return False
'''

NEW_CLOSURE = '''    # open-plan adjacency: two same-story rooms whose rects share an edge
    # with NO partition covering it are one continuous space (a lobby flowing
    # into a bullpen). Without this, open floor plans read as disconnected
    # and open-plan rooms false-flag as dead ends. Additive only. The rule is
    # `shared_open_edge`, which layout_lint's L12 and L24 ask too (0.197.0).
    def _shared_open_edge(ra, rb):
        return shared_open_edge(ra.bounds, rb.bounds,
                                [(p.axis, p.pos, p.start, p.end)
                                 for p in spec.partitions if p.story == ra.story])
'''

OLD_BUILD = "def build_graph(spec):\n"
NEW_BUILD = '''def shared_open_edge(a, b, parts):
    """Do two same-storey room rects touch along an edge no partition covers
    for at least 1.2 m? Then they are one continuous floor.

    ``a`` and ``b`` are ``[min_x, min_y, max_x, max_y]``; ``parts`` is the
    storey's partitions as ``(axis, pos, start, end)``. Two rects touch when
    an edge of one lies within 0.05 m of the other's; the shared length, less
    every same-axis partition lying on that line, must leave 1.2 m.

    ONE RULE, TWO ASKERS (0.197.0): `build_graph` below, for open floor plans
    in the tactical graph, and `layout_lint._reach_from_ext`, for L12 and L24.
    L24 shipped without it and named nine rooms reachable only by breaching
    that open floor already joined -- deli_a01's basement utility room among
    them, whose north edge cold run 9189's bake walks across where its
    partition stops at x 12. Lifted from `build_graph`'s closure unchanged."""
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    # vertical shared edge (a's right == b's left or vice versa)
    for x_edge, lo, hi in ((ax1, max(ay0, by0), min(ay1, by1))
                           if abs(ax1 - bx0) < 0.05 else (None, 0, 0),
                           (bx1, max(ay0, by0), min(ay1, by1))
                           if abs(bx1 - ax0) < 0.05 else (None, 0, 0)):
        if x_edge is not None and hi - lo >= 1.2:
            covered = 0.0
            for axis, pos, start, end in parts:
                if axis != "Y":
                    continue
                if abs(pos - x_edge) < 0.05:
                    covered += max(0.0, min(end, hi) - max(start, lo))
            if (hi - lo) - covered >= 1.2:
                return True
    # horizontal shared edge
    for y_edge, lo, hi in ((ay1, max(ax0, bx0), min(ax1, bx1))
                           if abs(ay1 - by0) < 0.05 else (None, 0, 0),
                           (by1, max(ax0, bx0), min(ax1, bx1))
                           if abs(by1 - ay0) < 0.05 else (None, 0, 0)):
        if y_edge is not None and hi - lo >= 1.2:
            covered = 0.0
            for axis, pos, start, end in parts:
                if axis != "X":
                    continue
                if abs(pos - y_edge) < 0.05:
                    covered += max(0.0, min(end, hi) - max(start, lo))
            if (hi - lo) - covered >= 1.2:
                return True
    return False


def build_graph(spec):
'''

OLD_STAIRS = "    # stairs/ladders connect every floor they pass through, not just endpoints\n"
NEW_STAIRS = '''    # open floor (0.197.0): two rooms on one storey whose shared edge no
    # partition covers for 1.2 m are one floor -- tactical's rule, asked here
    # too (`tactical.shared_open_edge`). Without it L24 named nine rooms
    # reachable only by breaching that open floor already joined. A partition
    # with no start or end runs the footprint, as `_opening_xy` reads it.
    import tactical
    for st, rs in by.items():
        parts = []
        for p in spec.get("partitions", []):
            if p.get("story", 0) != st:
                continue
            lo, hi = (-hy, hy) if p["axis"] == "Y" else (-hx, hx)
            parts.append((p["axis"], p["pos"],
                          lo if p.get("start") is None else p["start"],
                          hi if p.get("end") is None else p["end"]))
        for i, ra in enumerate(rs):
            for rb in rs[i + 1:]:
                if tactical.shared_open_edge(ra["bounds"], rb["bounds"], parts):
                    link(ra["id"], rb["id"])

    # stairs/ladders connect every floor they pass through, not just endpoints
'''

OLD_MSG = '''            f"-- every way in is a breach panel, a window or a drop; no door, "
            f"stair or ladder reaches it"
'''
NEW_MSG = '''            f"-- every way in is a breach panel, a window or a drop; no door, "
            f"stair, ladder or open floor reaches it"
'''

OLD_FROZEN = {
    "apartment_walkup_a01": ["bedroom", "kitchen", "office"],
    "corner_deli_heist_01": ["utility_room"],
    "cr_deli": ["server_room", "utility_room"],
    "deli_a01": ["utility_room"],
    "deli_a02": ["server_room", "utility_room"],
    "deli_a03": ["server_room", "utility_room"],
    "night_deli": ["server_room", "utility_room"],
    "rowhouse_raid": ["basement_vault", "kitchen"],
}
NEW_FROZEN = {
    "apartment_walkup_a01": ["bedroom", "office"],
    "cr_deli": ["server_room"],
    "deli_a02": ["server_room"],
    "deli_a03": ["server_room"],
    "night_deli": ["server_room"],
}
NEW_REASON = (
    "Rooms a body can only reach by breaching a panel, vaulting a window or dropping "
    "through a hole (layout_lint L24). KEPT BY DESIGN, the walker's call (2026-10-06): the "
    "server room where it is the OBJECTIVE -- cr_deli, deli_a02, night_deli -- an objective "
    "you breach into. PENDING the walker: deli_a03's server room (fortifiable, on deli_a01's "
    "layout, whose server room got a door in 0.194.0) and apartment_walkup_a01's bedroom and "
    "office. REFUTED, kept: 0.194.0 froze 15 here, and 9 of them -- the deli family's six "
    "basement utility rooms, apartment_walkup_a01's kitchen, rowhouse_raid's kitchen and "
    "basement vault -- were open floor L24's graph did not model (0.197.0 asks "
    "tactical.shared_open_edge); deli_a01's utility room is walked into by cold run 9189's "
    "bake. A room given a door must leave this list (test_walk_baseline_has_not_gone_stale); "
    "a new one fails (test_no_new_room_only_a_breach_reaches).")


def _edit(path, edits, size=None):
    data = path.read_bytes()
    assert b"\r\n" not in data, "CRLF in %s; refusing" % path.name
    if size is not None:
        assert len(data) == size, "%s is %d bytes, not the %d read; refusing" % (path.name, len(data), size)
    text = data.decode("utf-8")
    for old, _new in edits:
        n = text.count(old)
        assert n == 1, "%s: anchor found %d times, not once: %r" % (path.name, n, old[:70])
    for old, new in edits:
        text = text.replace(old, new)
    return text.encode("utf-8")


def main():
    tact = _edit(TACT, [(OLD_CLOSURE, NEW_CLOSURE), (OLD_BUILD, NEW_BUILD)], size=38491)
    lint = _edit(LINT, [(OLD_STAIRS, NEW_STAIRS), (OLD_MSG, NEW_MSG)])
    b = BASE.read_bytes()
    d = json.loads(b.decode("utf-8"))
    assert json.dumps(d, indent=2) + "\n" == b.decode("utf-8"), "baseline does not round-trip"
    assert d["walk_unreachable"] == OLD_FROZEN, "baseline is not 0.194.0's; refusing"
    d["walk_unreachable"] = NEW_FROZEN
    d["reason"] = NEW_REASON
    d["counts"] = {"rooms": sum(len(v) for v in NEW_FROZEN.values()), "shells": len(NEW_FROZEN)}
    TACT.write_bytes(tact)
    LINT.write_bytes(lint)
    BASE.write_bytes((json.dumps(d, indent=2) + "\n").encode("utf-8"))
    print("tactical.py: shared_open_edge lifted; layout_lint.py: open floor in _reach_from_ext; "
          "baseline: %(rooms)d rooms in %(shells)d shells" % d["counts"])


if __name__ == "__main__":
    main()
