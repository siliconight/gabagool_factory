"""Patina 0.23.0: a zone dresses only the ground it owns.

`zone_for` has said since it was written that the precedence rule travels in
the data and that "a placement counted against two budgets is counted
against neither" -- and the planner never called it. Each zone scattered
over its own bounding box, and Lot's `open_ground` box is the whole plate,
so open-ground clutter at MEDIUM density landed on the roads (low), the
sidewalks, the perimeter and the walks, on top of what those zones placed.
Measured on cold run 9141's shipped manifest: 2,436 of 5,232 placements
stand where the precedence rule gives the ground to another zone; across
families, open_ground on road_0 445, on the perimeter 238, on the sidewalks
265, on road_1 115, on walks 58, and every one of the 256 pieces on the
parking fields (0.29 a m2, the walker's "pebbles on the aisles").

Anchored edits (every anchor once; refuses on a miss):
`patina/surface_dressing.py` (`CODE_NOT_OWNER`, `zone_family`, the check in
the placement loop), `tests/test_surface_dressing.py`. CHANGELOG and VERSION
from `patina_zone_owner/CHANGELOG_0.23.0.md`.

    python patch_patina_zone_owner.py
"""
import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
PATINA = pathlib.Path(os.environ.get("PATINA_ROOT") or HERE.parent / "patina")
SRC = HERE / "patina_zone_owner"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


def main():
    vf = PATINA / "VERSION"
    v = vf.read_text(encoding="utf-8").strip()
    assert v == "Patina 0.22.0", v
    sd = PATINA / "patina" / "surface_dressing.py"
    _edit(sd, [
        ('CODE_STRADDLES_STEP = "DRESS_REFUSED_STRADDLES_STEP"\n',
         'CODE_STRADDLES_STEP = "DRESS_REFUSED_STRADDLES_STEP"\n'
         '#: 0.23.0: a candidate point whose ground the precedence rule\n'
         '#: (`zone_for`) gives to a zone of another family.\n'
         'CODE_NOT_OWNER = "DRESS_REFUSED_ANOTHER_ZONES_GROUND"\n'),
        ('def zone_for(point, zones):\n',
         'def zone_family(zone):\n'
         '    """A zone\'s family: Lot\'s `zone_family:<f>` tag, or its own id when it\n'
         '    carries none. A corridor is chopped into boxes that overlap at their\n'
         '    joins (`road_0_s00`, `road_0_s01`), and a point on a join is the same\n'
         '    ground whichever box placed it, so ownership is asked of the family."""\n'
         '    for t in zone.get("tags") or ():\n'
         '        if t.startswith("zone_family:"):\n'
         '            return t.split(":", 1)[1]\n'
         '    return zone["surface_zone_id"]\n'
         '\n'
         '\n'
         'def zone_for(point, zones):\n'),
        ('            radius = math.sqrt(fp / math.pi)\n'
         '            tags = excluded((x, y), exclusions, radius_m=radius)\n',
         '            # A ZONE DRESSES ONLY ITS OWN GROUND (0.23.0). Asked after the\n'
         '            # draws above, so a refusal here does not shift the asset, scale\n'
         '            # or yaw of the points after it.\n'
         '            owner = zone_for((x, y), zones)\n'
         '            if owner is None or zone_family(owner) != zone_family(zone):\n'
         '                keep_out.append({\n'
         '                    "code": CODE_NOT_OWNER, "surface_zone_id": zid,\n'
         '                    "asset_id": c["asset_id"],\n'
         '                    "why": ("the precedence rule gives this ground to "\n'
         '                            + (owner["surface_zone_id"] if owner else "no zone"))})\n'
         '                continue\n'
         '            radius = math.sqrt(fp / math.pi)\n'
         '            tags = excluded((x, y), exclusions, radius_m=radius)\n'),
    ])
    tests = PATINA / "tests" / "test_surface_dressing.py"
    s = tests.read_text(encoding="utf-8")
    assert "\r" not in s
    tests.write_text(s.rstrip("\n") + "\n" + (SRC / "tests_append.py").read_text(encoding="utf-8"),
                     encoding="utf-8", newline="\n")
    ch = PATINA / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    entry = (SRC / "CHANGELOG_0.23.0.md").read_text(encoding="utf-8").rstrip("\n") + "\n\n"
    anchor = "\n## "
    i = s.index(anchor) + 1
    ch.write_text(s[:i] + entry + s[i:], encoding="utf-8", newline="\n")
    vf.write_text("Patina 0.23.0", encoding="utf-8", newline="\n")
    print("Patina 0.23.0 applied")


if __name__ == "__main__":
    main()
