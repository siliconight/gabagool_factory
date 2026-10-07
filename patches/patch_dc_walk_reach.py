"""Deli Counter 0.194.0: L24, a room a body can only reach by breaching.

    python patch_dc_walk_reach.py

Anchored on layout_lint.py as read 2026-10-06 (`reachability_findings`
whole, and its line in `lint_spec`); refuses on any miss. Writes
walk_reach_baseline.json; refuses if it exists.

L12's search moves, unchanged, into `_reach_from_ext(spec, walk_only)`, so
L12 and L24 ask one search the same question with and without the ways in
that are not walking. L12's messages and verdicts do not change.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DC = ROOT / "deli_counter"
LINT = DC / "layout_lint.py"
BASELINE = DC / "walk_reach_baseline.json"

OLD_FN = '''def reachability_findings(spec):
    """L12 -- every room must have a path from an exterior entrance. Catches
    SEALED spaces (a stair landing in a closed box, a room with no door): a
    *missing* connection, which the coherence rules (dead openings) cannot see.
    Runs for every mode. Uses the same graph as the nav check, but treats a
    stair/ladder as serving every floor it passes through (real stairwell
    behaviour), and counts ramps + floor-hole/hatch drops as connections."""
    rooms = spec.get("rooms", [])
    if not rooms:
        return []
    edges, _ = graph(spec)
    by = _rooms_by_story(spec)

    def link(a, b):
        edges.setdefault(a, set()).add((b, "vert"))
        edges.setdefault(b, set()).add((a, "vert"))

    # outdoor / site rooms (bounds extend beyond the building footprint -- a
    # forecourt, yard, dock, parking) are contiguous with the exterior, so they
    # are reachable from outside by definition.
    hx, hy = spec["footprint_x"] / 2, spec["footprint_y"] / 2
    tol = 0.5
    for r in rooms:
        x0, y0, x1, y1 = r["bounds"]
        if x0 < -hx - tol or x1 > hx + tol or y0 < -hy - tol or y1 > hy + tol:
            link(r["id"], "EXT")

    # stairs/ladders connect every floor they pass through, not just endpoints
    for st in list(spec.get("stairs", [])) + list(spec.get("ladders", [])):
        a, b = st.get("from_story"), st.get("to_story")
        if a is None or b is None:
            continue
        chain = []
        for fl in range(min(a, b), max(a, b) + 1):
            r = _room_at(by.get(fl, []), st.get("x", 0), st.get("y", 0))
            if r:
                chain.append(r["id"])
        for i in range(len(chain) - 1):
            link(chain[i], chain[i + 1])
    # ramps
    for rp in spec.get("ramps", []):
        a = _room_at(by.get(rp.get("from_story", 0), []), rp.get("x", 0), rp.get("y", 0))
        b = _room_at(by.get(rp.get("to_story", 0), []), rp.get("x", 0), rp.get("y", 0))
        if a and b:
            link(a["id"], b["id"])
    # floor holes / hatches (vertical drops) connect the two stacked rooms
    for vl in spec.get("vertical_links", []):
        if vl.get("kind") in ("floor_hole", "hatch") and vl.get("x") is not None:
            s = vl.get("story", 0)
            a = _room_at(by.get(s, []), vl["x"], vl["y"])
            b = _room_at(by.get(s - 1, []), vl["x"], vl["y"])
            if a and b:
                link(a["id"], b["id"])

    seen = {"EXT"}
    stk = ["EXT"]
    while stk:
        u = stk.pop()
        for v, k in edges.get(u, ()):
            if v not in seen:
                seen.add(v)
                stk.append(v)
    fails = []
    for r in rooms:
        if r["id"] not in seen:
            fails.append(f"L12 unreachable room: '{r['id']}' (story {r.get('story')}) "
                         f"has no path from an exterior entrance -- sealed space or "
                         f"missing door/stair connection")
    return fails
'''

NEW_FN = '''# The ways through a wall a body WALKS (L24): a doorway, a garage, a vault
# door. `graph()` labels a vaultable window "vault" as well, so the filter
# acts on the raw opening kind, before graph() ever sees it.
WALK_KINDS = ("door", "garage", "vault")


def _reach_from_ext(spec, walk_only=False):
    """Room ids with a path from an exterior entrance, plus "EXT".

    Uses the same graph as the nav check, but treats a stair/ladder as
    serving every floor it passes through (real stairwell behaviour), and
    counts ramps + floor-hole/hatch drops as connections. That is L12's
    search. ``walk_only`` (L24) keeps only `WALK_KINDS` among the openings
    and drops the floor-hole/hatch links: what a body reaches without
    breaching a panel, vaulting a window or dropping through a hole. The
    caller's spec is never changed; a filtered copy goes to `graph()`."""
    rooms = spec.get("rooms", [])
    if walk_only:
        spec = dict(spec)
        for key in ("partitions", "ext_walls"):
            spec[key] = [dict(w, openings=[o for o in w.get("openings", [])
                                           if o.get("kind", "door") in WALK_KINDS])
                         for w in spec.get(key, [])]
    edges, _ = graph(spec)
    by = _rooms_by_story(spec)

    def link(a, b):
        edges.setdefault(a, set()).add((b, "vert"))
        edges.setdefault(b, set()).add((a, "vert"))

    # outdoor / site rooms (bounds extend beyond the building footprint -- a
    # forecourt, yard, dock, parking) are contiguous with the exterior, so they
    # are reachable from outside by definition.
    hx, hy = spec["footprint_x"] / 2, spec["footprint_y"] / 2
    tol = 0.5
    for r in rooms:
        x0, y0, x1, y1 = r["bounds"]
        if x0 < -hx - tol or x1 > hx + tol or y0 < -hy - tol or y1 > hy + tol:
            link(r["id"], "EXT")

    # stairs/ladders connect every floor they pass through, not just endpoints
    for st in list(spec.get("stairs", [])) + list(spec.get("ladders", [])):
        a, b = st.get("from_story"), st.get("to_story")
        if a is None or b is None:
            continue
        chain = []
        for fl in range(min(a, b), max(a, b) + 1):
            r = _room_at(by.get(fl, []), st.get("x", 0), st.get("y", 0))
            if r:
                chain.append(r["id"])
        for i in range(len(chain) - 1):
            link(chain[i], chain[i + 1])
    # ramps
    for rp in spec.get("ramps", []):
        a = _room_at(by.get(rp.get("from_story", 0), []), rp.get("x", 0), rp.get("y", 0))
        b = _room_at(by.get(rp.get("to_story", 0), []), rp.get("x", 0), rp.get("y", 0))
        if a and b:
            link(a["id"], b["id"])
    # floor holes / hatches (vertical drops) connect the two stacked rooms;
    # a drop goes one way, down, so a walk does not count it
    for vl in ([] if walk_only else spec.get("vertical_links", [])):
        if vl.get("kind") in ("floor_hole", "hatch") and vl.get("x") is not None:
            s = vl.get("story", 0)
            a = _room_at(by.get(s, []), vl["x"], vl["y"])
            b = _room_at(by.get(s - 1, []), vl["x"], vl["y"])
            if a and b:
                link(a["id"], b["id"])

    seen = {"EXT"}
    stk = ["EXT"]
    while stk:
        u = stk.pop()
        for v, k in edges.get(u, ()):
            if v not in seen:
                seen.add(v)
                stk.append(v)
    return seen


def reachability_findings(spec):
    """L12 -- every room must have a path from an exterior entrance. Catches
    SEALED spaces (a stair landing in a closed box, a room with no door): a
    *missing* connection, which the coherence rules (dead openings) cannot see.
    Runs for every mode. The search is `_reach_from_ext`, which counts every
    way through a wall, breach panels and windows included."""
    rooms = spec.get("rooms", [])
    if not rooms:
        return []
    seen = _reach_from_ext(spec)
    fails = []
    for r in rooms:
        if r["id"] not in seen:
            fails.append(f"L12 unreachable room: '{r['id']}' (story {r.get('story')}) "
                         f"has no path from an exterior entrance -- sealed space or "
                         f"missing door/stair connection")
    return fails


def walk_unreachable(spec):
    """The rooms L12 reaches that a body cannot walk to (L24): every way in
    is a breach panel, a window or a drop. Room dicts, in spec order."""
    rooms = spec.get("rooms", [])
    if not rooms:
        return []
    full = _reach_from_ext(spec)
    walk = _reach_from_ext(spec, walk_only=True)
    return [r for r in rooms if r["id"] in full and r["id"] not in walk]


def walk_reach_findings(spec):
    """L24 (WARN, 0.194.0): a room reached only by breaching, vaulting a
    window or dropping through a hole.

    L12 counts every way through a wall, so a room behind breach panels
    passes it. deli_a01's server room was one (186 m2, two soft-wall breaches,
    no door), and cold run 9188's site bake made it its own navmesh island.
    A warning, not a failure: an objective behind breach walls can be the
    design. `walk_reach_baseline.json` freezes the ones awaiting the walker's
    call, and test_walk_reach fails on a new one."""
    return [f"L24 reachable only by breaching: '{r['id']}' (story {r.get('story')}) "
            f"-- every way in is a breach panel, a window or a drop; no door, "
            f"stair or ladder reaches it"
            for r in walk_unreachable(spec)]
'''

OLD_WIRE = "    fails += reachability_findings(spec)    # L12 sealed/unreachable rooms (all modes)\n"
NEW_WIRE = (OLD_WIRE +
            "    warns += walk_reach_findings(spec)      # L24 a room only a breach, window or drop reaches\n")

FROZEN = {
    "apartment_walkup_a01": ["bedroom", "kitchen", "office"],
    "corner_deli_heist_01": ["utility_room"],
    "cr_deli": ["server_room", "utility_room"],
    "deli_a01": ["utility_room"],
    "deli_a02": ["server_room", "utility_room"],
    "deli_a03": ["server_room", "utility_room"],
    "night_deli": ["server_room", "utility_room"],
    "rowhouse_raid": ["basement_vault", "kitchen"],
}
REASON = (
    "Rooms a body can only reach by breaching a panel, vaulting a window or dropping "
    "through a hole (layout_lint L24), left as authored by 0.194.0 because each is a "
    "design call: deli_a01's server room was the first, and the walker gave it a door "
    "(2026-10-06). The deli family repeats its layout: a server room on story 1 "
    "(fortifiable in deli_a01 and deli_a03, the OBJECTIVE in cr_deli, deli_a02 and "
    "night_deli, where breaching in may be the point) and a utility room in the "
    "basement whose role is 'connector', which a room with no door contradicts. "
    "apartment_walkup_a01's kitchen, bedroom and office and rowhouse_raid's kitchen "
    "and basement vault are the rest. A room given a door must leave this list "
    "(test_walk_baseline_has_not_gone_stale); a new one fails "
    "(test_no_new_room_only_a_breach_reaches).")


def _eol(data):
    crlf = data.count(b"\r\n")
    lf = data.count(b"\n") - crlf
    assert not (crlf and lf), "mixed line endings in %s; refusing" % LINT
    return "\r\n" if crlf else "\n"


def main():
    data = LINT.read_bytes()
    eol = _eol(data)
    text = data.decode("utf-8").replace(eol, "\n")
    a = text.find("def reachability_findings(spec):\n")
    # "    return fails\n\n\ndef gate": find() lands on the SECOND newline, so
    # text[a:b] ends at the function's own last newline (the first run sliced
    # to b + 1, took a blank line, and the anchor refused).
    b = text.find("\n\ndef gate(spec):")
    assert a > 0 and b > a, (a, b)
    block = text[a:b]
    assert block == OLD_FN, "reachability_findings is not the text read 2026-10-06; refusing"
    assert text.count(OLD_WIRE) == 1, "L12's lint_spec line not found exactly once"
    assert "def walk_reach_findings" not in text and "WALK_KINDS" not in text
    assert not BASELINE.exists(), "%s exists; refusing" % BASELINE
    text = text[:a] + NEW_FN + text[b:]
    text = text.replace(OLD_WIRE, NEW_WIRE)
    LINT.write_bytes(text.replace("\n", eol).encode("utf-8"))
    rooms = sum(len(v) for v in FROZEN.values())
    BASELINE.write_bytes((json.dumps({"walk_unreachable": FROZEN, "reason": REASON,
                                      "counts": {"rooms": rooms, "shells": len(FROZEN)}},
                                     indent=2) + "\n").encode("utf-8"))
    print("layout_lint.py: L12's search shared, L24 added and wired (%s endings)"
          % ("CRLF" if eol == "\r\n" else "LF"))
    print("walk_reach_baseline.json: %d rooms in %d shells" % (rooms, len(FROZEN)))


if __name__ == "__main__":
    main()
