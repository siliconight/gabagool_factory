"""Lot concatenates its buildings' LADDERS into the site, as it already does
their interactives.

COLD RUN 9075 FALSIFIED THE CLAIM Dispatch 0.5.0 made. That release carried a
ladder's off-mesh nav link into the package and was tested against a fixture
and a unit test -- never against a package containing a ladder. 9075 shipped
one: 23 `gb_ladder` surfaces, `market_hall_a01` carrying a ladder with a
`nav_link` in its shell, and `navigation_hints.json` reading

    schema dispatch.navigation_hints.v0.3   nodes 57   edges 55   LINKS 0

The brief's own falsifier, written before the run, said exactly that: "a
package whose buildings carry ladders and whose links[] is empty".

WHY. Dispatch's Deli Counter importer was the one patched. For a SITE mission
Dispatch runs the LOT importer instead -- `lot.gameplay.json` is its manifest --
and Lot concatenates its buildings' `interactives` into the site while dropping
their `ladders` entirely. Measured: that file's keys are `anchors,
interactives, license, props, schema, up_axis`. No ladders, so nothing
downstream could carry a link it never received.

EVERY POSITION MOVES, OR NONE SHOULD. A ladder record carries twelve
three-component points and a four-point plan rect, all in the building's own
frame:

    lower_anchor, upper_anchor
    route_nodes/{lower_approach, lower_mount, climb_start, climb_end,
                 upper_dismount, upper_route}
    traversal_component/climb_axis[0..1]
    nav_link/{start_position, end_position}
    geometry/climb_rect[0..3]                     (x, y plan pairs)

Transforming some and leaving others would ship a record that contradicts
itself -- a nav link in site space beside route nodes in building space -- which
is worse than shipping nothing. They are listed explicitly rather than found by
walking the record, and an unrecognised numeric triple REFUSES, so a field Deli
Counter adds later cannot be carried silently in the wrong frame.

Anchored: every anchor must match exactly once or this refuses to write.
"""
from pathlib import Path

TARGET = Path(__file__).resolve().parent.parent / "lot" / "lot.py"

# ---------------------------------------------------------------- anchor 1
A1 = '''        "interactives": [],
        "surfaces": [],
'''

N1 = '''        "interactives": [],
        # LADDERS, for the same reason interactives are here: Deli Counter
        # emits them per building and the site is what Dispatch reads. Without
        # this a package ships a climb marker and no off-mesh nav link, so a
        # player climbs a ladder an AI cannot path up (roadmap 172, falsified
        # on cold run 9075).
        "ladders": [],
        "surfaces": [],
'''

# ---------------------------------------------------------------- anchor 2
A2 = '''        # surfaces (acoustic) + surface_roles: namespace node names so the
        # site-wide maps stay unambiguous across buildings
'''

N2 = '''        # ladders: carried like interactives -- verbatim but for the frame.
        # Ids are already building-scoped, and every POSITION is moved into
        # site space by `_ladder_to_site`, which refuses rather than carrying
        # a field it does not recognise.
        for lad in gp.get("ladders", []) or []:
            wl = _ladder_to_site(lad, placement)
            wl["building"] = bid
            site["ladders"].append(wl)

        # surfaces (acoustic) + surface_roles: namespace node names so the
        # site-wide maps stay unambiguous across buildings
'''

# ---------------------------------------------------------------- anchor 3
A3 = '''# ---------------------------------------------------------------------------
# building geometry source: .tscn (preferred) or .glb
# ---------------------------------------------------------------------------
'''

N3 = '''#: Every position in a Deli Counter ladder record, by path. Listed rather than
#: discovered, because a blind walk over the record would also rewrite anything
#: that merely looks like a point, and because an explicit list is auditable
#: against `ladder.py`. `_ladder_to_site` REFUSES on a numeric triple it does
#: not find here, so a field added upstream cannot ride into site space
#: untransformed -- the failure would be a nav link and a route node
#: disagreeing about where the same ladder is.
_LADDER_POINTS_3 = (
    ("lower_anchor",),
    ("upper_anchor",),
    ("route_nodes", "lower_approach"),
    ("route_nodes", "lower_mount"),
    ("route_nodes", "climb_start"),
    ("route_nodes", "climb_end"),
    ("route_nodes", "upper_dismount"),
    ("route_nodes", "upper_route"),
    ("nav_link", "start_position"),
    ("nav_link", "end_position"),
)
#: Lists OF points rather than single points.
_LADDER_POINT_LISTS_3 = (
    ("traversal_component", "climb_axis"),
)
#: Plan polygons: (x, y) pairs, no height.
_LADDER_POINT_LISTS_2 = (
    ("geometry", "climb_rect"),
)


def _dig(rec, path):
    """The container holding `path`'s last key, and that key -- or (None, None)
    when the path is absent. Absent is fine: a ladder without a nav link is a
    ladder, and `ladder.py` omits blocks it has nothing to say about."""
    cur = rec
    for key in path[:-1]:
        if not isinstance(cur, dict) or key not in cur:
            return None, None
        cur = cur[key]
    if not isinstance(cur, dict) or path[-1] not in cur:
        return None, None
    return cur, path[-1]


def _ladder_to_site(lad, placement):
    """A ladder record with every position moved into site space.

    Deep-copied, so the building's own gameplay.json is untouched -- it is read
    again by other passes and a shared nested dict would put site coordinates
    into the building's file.
    """
    import copy as _copy

    out = _copy.deepcopy(lad)
    seen = set()
    for path in _LADDER_POINTS_3:
        owner, key = _dig(out, path)
        if owner is None:
            continue
        p = owner[key]
        if isinstance(p, (list, tuple)) and len(p) == 3:
            owner[key] = _place_point(p[0], p[1], p[2], placement)
            seen.add("/".join(path))
    for path in _LADDER_POINT_LISTS_3:
        owner, key = _dig(out, path)
        if owner is None:
            continue
        pts = owner[key]
        if isinstance(pts, list):
            owner[key] = [_place_point(p[0], p[1], p[2], placement)
                          if isinstance(p, (list, tuple)) and len(p) == 3
                          else p for p in pts]
            seen.add("/".join(path))
    for path in _LADDER_POINT_LISTS_2:
        owner, key = _dig(out, path)
        if owner is None:
            continue
        pts = owner[key]
        if isinstance(pts, list):
            owner[key] = [list(_rotate_xy(p[0], p[1], placement["rot"]))
                          if isinstance(p, (list, tuple)) and len(p) == 2
                          else p for p in pts]
            # translate after rotating, same order as `_place_point`
            owner[key] = [[p[0] + placement["at"][0], p[1] + placement["at"][1]]
                          if isinstance(p, (list, tuple)) and len(p) == 2
                          else p for p in owner[key]]
            seen.add("/".join(path))

    # AN UNRECOGNISED POSITION IS A REFUSAL, not a shrug. Anything that looks
    # like a point and was not transformed above would reach the site still in
    # building coordinates, and the only symptom would be an AI pathing to the
    # wrong place in one building out of several.
    missed = []

    def _scan(node, path):
        if isinstance(node, dict):
            for k, v in node.items():
                _scan(v, path + "/" + str(k))
        elif isinstance(node, list):
            if node and all(isinstance(x, (int, float)) for x in node) \\
                    and len(node) in (2, 3):
                stem = path.rsplit("[", 1)[0]
                if not any(stem.endswith(s) for s in seen):
                    missed.append(path)
            else:
                for i, v in enumerate(node):
                    _scan(v, "%s[%d]" % (path, i))

    _scan(out, "")
    if missed:
        raise ValueError(
            "lot: ladder %r carries position(s) this pass does not know how to "
            "move into site space: %s -- add them to _LADDER_POINTS_* rather "
            "than shipping them in building coordinates"
            % (lad.get("id", "?"), ", ".join(sorted(missed))))
    return out


# ---------------------------------------------------------------------------
# building geometry source: .tscn (preferred) or .glb
# ---------------------------------------------------------------------------
'''

EDITS = ((A1, N1), (A2, N2), (A3, N3))


def main() -> None:
    data = TARGET.read_bytes()
    if b"\r\n" in data:
        raise SystemExit("REFUSED: expected LF, found CRLF")
    text = data.decode("utf-8")
    before = len(data)
    for i, (old, new) in enumerate(EDITS, 1):
        hits = text.count(old)
        if hits != 1:
            raise SystemExit(f"REFUSED: anchor {i} matched {hits} times")
        text = text.replace(old, new)
    out = text.encode("utf-8")
    if b"\r\n" in out:
        raise SystemExit("REFUSED: would write CRLF")
    TARGET.write_bytes(out)
    print(f"{TARGET.name}: {before} -> {len(out)} bytes (+{len(out) - before})")


if __name__ == "__main__":
    main()
