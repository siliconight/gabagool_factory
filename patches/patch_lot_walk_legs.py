"""Lot 0.89.0: a walk between two doors is drawn square to the buildings.
The walker, 2026-10-03, on 0.88.0's door-to-door building paths: "these look
goofy" -- an 8 m band laid diagonally across the lot from one side door to
the next. A building path whose two ends both found a door is now drawn as
legs at the sidewalk's width: out from each door along its own facing, and
one jog between them.

Anchored edits on `lot/site_paths.py` (every anchor once; refuses on a
miss, and refuses unless the file is 0.88.0's, byte for byte);
`tests/test_site_paths.py` replaced from `lot_walk_legs/`; CHANGELOG and
VERSION from `lot_walk_legs/CHANGELOG_0.89.0.md`.

    python patch_lot_walk_legs.py
    LOT_ROOT=<copy> python patch_lot_walk_legs.py
"""
import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
LOT = pathlib.Path(os.environ.get("LOT_ROOT") or HERE.parent / "lot")
SRC = HERE / "lot_walk_legs"

CONSTS = '''
#: The width a walk between two doors is drawn at when the site has no road
#: to take a sidewalk's width from, in metres. Level Factory's sidewalk
#: (`road_grammar.SIDEWALK_WIDTH`) is 3.0 and every site it writes carries
#: that on its roads, which is what `_walk_width` reads first.
WALK_WIDTH = 3.0

#: Two doors whose offset across the walk is within this are joined by one
#: straight leg down the middle, in metres: a jog a quarter of a metre deep
#: is a kink, not a corner.
ALIGNED_TOL = 0.25
'''

LEGS = '''

def _walk_width(site_spec, p):
    """The width a door-to-door walk is drawn at: the narrowest sidewalk the
    site's roads declare, never wider than the path was authored."""
    walks = [float(r.get("sidewalk") or 0.0) for r in site_spec.get("roads", []) or []]
    walks = [s for s in walks if s > 0.0]
    return min(float(p.get("width", WALK_WIDTH)), min(walks) if walks else WALK_WIDTH)


def _walk_legs(a, b, leaving, w):
    """The legs ``[(a, b, width)]`` of a walk from door point `a` to door
    point `b`, square to the axis `a`'s door faces along: out from each door
    and one jog between. None when the doors are closer along that axis
    than the walk is wide (no room to run out before turning).

    THE CORNERS BELONG TO THE LEGS THAT RUN OUT FROM THE DOORS. Each of those
    is drawn half a width past the jog's line, and the jog is drawn between
    them, so the three slabs tile the corner squares and no two lie coplanar
    over the same ground (which z-fights; `street_slabs` avoids it the same
    way at a junction's mouth)."""
    along_x = abs(leaving[0]) >= abs(leaving[1])
    (au, av), (bu, bv) = ((a[0], a[1]), (b[0], b[1])) if along_x else ((a[1], a[0]), (b[1], b[0]))

    def pt(u, v):
        return [u, v] if along_x else [v, u]

    du, dv = bu - au, bv - av
    if abs(du) < w:
        return None
    if abs(dv) <= ALIGNED_TOL:
        vm = (av + bv) / 2.0
        return [(pt(au, vm), pt(bu, vm), w)]
    if abs(dv) < w:
        # too shallow for a jog: one leg down the middle, wide enough to
        # reach both doors
        vm = (av + bv) / 2.0
        return [(pt(au, vm), pt(bu, vm), w + abs(dv))]
    su = 1.0 if du > 0 else -1.0
    sv = 1.0 if dv > 0 else -1.0
    um = (au + bu) / 2.0
    legs = [(pt(au, av), pt(um + su * w / 2.0, av), w),
            (pt(um, av + sv * w / 2.0), pt(um, bv - sv * w / 2.0), w),
            (pt(um - su * w / 2.0, bv), pt(bu, bv), w)]
    return [leg for leg in legs if math.dist(leg[0], leg[1]) > 1e-6]
'''


def main():
    v = (LOT / "VERSION").read_text(encoding="utf-8").strip()
    assert v == "Lot 0.88.0", v
    p = LOT / "site_paths.py"
    assert p.read_bytes() == (HERE / "lot_door_paths" / "site_paths.py").read_bytes(), \
        "lot/site_paths.py is not 0.88.0's"
    s = p.read_text(encoding="utf-8")
    pairs = [
        ('CATEGORY = "site_paths"\n', 'CATEGORY = "site_paths"\n' + CONSTS),
        ('    findings = []\n'
         '    for i, p in enumerate(site_spec.get("paths", []) or []):\n'
         '        a, b = endpoints_or_none(p, bld)\n'
         '        if a is None:\n'
         '            continue\n'
         '        snapped = {}\n',
         '    findings = []\n'
         '    extra = {}      # authored index -> the further legs of its walk\n'
         '    for i, p in enumerate(site_spec.get("paths", []) or []):\n'
         '        a, b = endpoints_or_none(p, bld)\n'
         '        if a is None:\n'
         '            continue\n'
         '        snapped = {}\n'
         '        normals = {}\n'),
        ('                p[key] = [ex + nx * DOOR_STANDOFF, ey + ny * DOOR_STANDOFF]\n'
         '                snapped[key] = wall\n',
         '                p[key] = [ex + nx * DOOR_STANDOFF, ey + ny * DOOR_STANDOFF]\n'
         '                snapped[key] = wall\n'
         '                normals[key] = (nx, ny)\n'),
        ('                    if key not in snapped:\n'
         '                        p[key] = [here[0], here[1]]\n',
         '                    if key not in snapped:\n'
         '                        p[key] = [here[0], here[1]]\n'
         '            # BOTH ENDS AT A DOOR: THE WALK IS DRAWN SQUARE (0.89.0). A band\n'
         '            # at the authored width laid door to door crossed the lot on a\n'
         '            # diagonal (the walker: "these look goofy"). It is drawn as legs\n'
         '            # at the sidewalk\'s width instead: out from each door along its\n'
         '            # facing and one jog between. The record keeps its ids and its\n'
         '            # authored width as `route_width`; the further legs follow it\n'
         '            # in the list as plain point paths naming the route in `leg_of`.\n'
         '            if len(snapped) == 2:\n'
         '                legs = _walk_legs(p["a"], p["b"], normals["a"], _walk_width(site_spec, p))\n'
         '                if legs:\n'
         '                    p["route_width"] = p.get("width")\n'
         '                    p["a"], p["b"], p["width"] = legs[0]\n'
         '                    extra[i] = [{"a": la, "b": lb, "width": lw,\n'
         '                                 "leg_of": [p["from"], p["to"]]}\n'
         '                                for la, lb, lw in legs[1:]]\n'),
        ('            p["snapped"] = snapped\n'
         '    return findings\n',
         '            p["snapped"] = snapped\n'
         '    if extra:\n'
         '        out = []\n'
         '        for i, p in enumerate(site_spec.get("paths", []) or []):\n'
         '            out.append(p)\n'
         '            out.extend(extra.get(i, []))\n'
         '        site_spec["paths"] = out\n'
         '    return findings\n'),
        ('    return best\n', '    return best\n' + LEGS),
    ]
    for old, new in pairs:
        assert s.count(old) == 1, old[:70]
        s = s.replace(old, new)
    p.write_text(s, encoding="utf-8", newline="\n")
    (LOT / "tests" / "test_site_paths.py").write_bytes((SRC / "test_site_paths.py").read_bytes())
    entry = (SRC / "CHANGELOG_0.89.0.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    cl = LOT / "CHANGELOG.md"
    d = cl.read_bytes()
    assert b"## 0.89.0" not in d and d.startswith(b"## 0.88.0")
    cl.write_bytes(entry.encode("utf-8") + d)
    (LOT / "VERSION").write_bytes(b"Lot 0.89.0")
    print("0.88.0 -> 0.89.0")


if __name__ == "__main__":
    main()
