"""Deli Counter 0.165.0: every sign anchor carries the business it names.

Cold run 9120's FLAPPHAS walk found the box over the gas station's door lit
and blank. Zoo 1.37.0 (`patch_zoo_storefront_signs.py`) paints a sign's face
with the business's name; this hands it the business. `build_light_manifest`
takes the building's identity -- `level_design.club_building_id(spec)`, the
name and the recipe that made it, the string a club's `neon_sign` variant is
keyed on -- and stamps it on every `sign` anchor, derived or authored, that
does not carry its own. `deli_counter.py` passes it.

Every edit asserts its anchor once and refuses to write on a miss.
"""
from __future__ import annotations

import pathlib

DC = pathlib.Path(__file__).resolve().parents[1] / "deli_counter"


def _edit(rel, pairs):
    p = DC / rel
    raw = p.read_bytes()
    assert b"\r\n" not in raw, f"{rel}: CRLF in an LF file"
    s = raw.decode("utf-8")
    for old, new in pairs:
        n = s.count(old)
        assert n == 1, f"{rel}: anchor found {n} times: {old[:60]!r}"
        s = s.replace(old, new)
    p.write_bytes(s.encode("utf-8"))
    print("patched", rel)


SIG_OLD = '''def build_light_manifest(building_id, rooms, openings, story_height,
                         *, cap_thick, wall_thick, authored=None, theme=None,
                         ceiling_voids=None, partitions=None, report=None,
                         volumes=None, club_rooms=None, storefronts=None):
    """Full `<name>.lights.json` manifest. `authored` is an optional list of
    hand-placed anchors; an authored anchor replaces a derived one with the
    same id (auto defaults + spec overrides, like props). `volumes` and
    `club_rooms` are `derive_light_anchors`'s."""'''
SIG_NEW = '''def build_light_manifest(building_id, rooms, openings, story_height,
                         *, cap_thick, wall_thick, authored=None, theme=None,
                         ceiling_voids=None, partitions=None, report=None,
                         volumes=None, club_rooms=None, storefronts=None,
                         business=None):
    """Full `<name>.lights.json` manifest. `authored` is an optional list of
    hand-placed anchors; an authored anchor replaces a derived one with the
    same id (auto defaults + spec overrides, like props). `volumes` and
    `club_rooms` are `derive_light_anchors`'s.

    `business` (0.165.0) is the building's identity,
    `level_design.club_building_id(spec)`: every `sign` anchor that does not
    name its own carries it, and Zoo's `sign_box` paints the business's name
    from it (`storefront_names`) -- until Zoo 1.37.0 every derived sign in
    the library was a blank lit box (cold run 9120)."""'''

STAMP_OLD = '''        anchors = list(by_id.values())
    return {
        "light_manifest_version": LIGHT_MANIFEST_VERSION,'''
STAMP_NEW = '''        anchors = list(by_id.values())
    if business:
        for a in anchors:
            if a.get("type") == "sign" and not a.get("business"):
                a["business"] = str(business)
    return {
        "light_manifest_version": LIGHT_MANIFEST_VERSION,'''

CALL_OLD = '''        club_rooms=_club,
        storefronts=_fronts,
    )'''
CALL_NEW = '''        club_rooms=_club,
        storefronts=_fronts,
        # WHO IS INSIDE (0.165.0): the identity a club's neon is keyed on,
        # which the sign over the door names (Zoo 1.37.0)
        business=_ld.club_building_id(builder.s),
    )'''

TEST = '''"""Every sign over a door names its business (0.165.0).

Cold run 9120's FLAPPHAS walk: the lit box over the gas station's door was
blank, and so was every derived sign in the library -- Zoo painted a face
only from a sign pack, and no theme ships one. Zoo 1.37.0 paints the name
from the anchor's `business`; this holds that every sign anchor the library
builds carries it, and that it is the identity a club's neon is keyed on, so
the door and the neon name the same club.
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import level_design  # noqa: E402
import lights  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def test_every_library_sign_names_the_building_it_is_on():
    seen = 0
    for p in sorted(glob.glob(os.path.join(HERE, "specs", "*.json"))):
        if os.path.basename(p).startswith("lf_"):
            continue
        with open(p, encoding="utf-8") as f:
            spec = json.load(f)
        lp = os.path.join(HERE, "build", spec["name"] + ".lights.json")
        if not os.path.exists(lp):
            continue
        with open(lp, encoding="utf-8") as f:
            man = json.load(f)
        for a in man["anchors"]:
            if a["type"] == "sign":
                seen += 1
                assert a.get("business") == level_design.club_building_id(spec), (spec["name"], a)
    assert seen >= 100, seen


def test_the_stamp_reaches_authored_signs_and_keeps_their_own():
    rooms = [{"id": "shop", "story": 0, "bounds": [0, 0, 8, 6]}]
    openings = [{"kind": "door", "wall": "ext_0_S", "x": 4.0, "y": 0.0, "width": 1.2,
                 "height": 2.2, "sill": 0.0},
                {"kind": "window", "wall": "ext_0_S", "x": 1.5, "y": 0.0, "width": 1.6,
                 "height": 1.2, "z": 1.5}]
    authored = [{"id": "own_sign", "type": "sign", "pos": [1, 1, 3], "rot_y": 0.0,
                 "size": [2.0, 0.6], "business": "somebody_else"},
                {"id": "plain_sign", "type": "sign", "pos": [5, 1, 3], "rot_y": 0.0,
                 "size": [2.0, 0.6]}]
    man = lights.build_light_manifest("t", rooms, openings, 3.5, cap_thick=0.3, wall_thick=0.3,
                                      authored=authored, business="corner_deli")
    by = {a["id"]: a for a in man["anchors"] if a["type"] == "sign"}
    assert by["own_sign"]["business"] == "somebody_else"
    assert by["plain_sign"]["business"] == "corner_deli"
    derived = [a for a in by.values() if a.get("source") == "derived"]
    assert derived and all(a["business"] == "corner_deli" for a in derived)
    # and without a business nothing is stamped (the call sites that pass none)
    bare = lights.build_light_manifest("t", rooms, openings, 3.5, cap_thick=0.3, wall_thick=0.3)
    assert not any("business" in a for a in bare["anchors"])
'''


def main():
    t = DC / "test_sign_business.py"
    assert not t.exists(), "already applied"
    _edit("lights.py", [(SIG_OLD, SIG_NEW), (STAMP_OLD, STAMP_NEW)])
    _edit("deli_counter.py", [(CALL_OLD, CALL_NEW)])
    t.write_bytes(TEST.encode("utf-8"))
    print("wrote test_sign_business.py")


if __name__ == "__main__":
    main()
