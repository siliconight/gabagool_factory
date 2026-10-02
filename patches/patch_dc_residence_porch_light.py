"""Deli Counter 0.169.0: a home has a porch light over its door, not a lit sign.

Cold run 9121 put a name on every lit sign box (Zoo 1.37.0); a building of
no kind shows its street number, and a home is a building of no kind. The
walker was asked whether an apartment or a rowhouse should have a lit sign at
all and, 2026-10-02, left the call here. Decided: no. A lit cabinet over a
front door says BUSINESS; a home's door has a porch light.

  * `lights.is_residence(business)`: the building's identity
    (`level_design.club_building_id`) names a home -- apartment, walkup,
    rowhouse, twin, mansion, duplex, tenement, as whole words.
  * `derive_light_anchors(..., residence=False)`: a residence derives no
    storefront sign, so its front door falls to the loop that hangs a wall
    pack over every other exterior door. One anchor for one anchor: the
    light count does not move.
  * `build_light_manifest` passes `residence=is_residence(business)`.

Eight library buildings: apartment_walkup_a01-a03, mansion_a01-a03,
rowhouse_raid, twin_a01. 102 sign anchors -> 94.

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


CONST_OLD = '''_SIGN_H = 0.6           # sign height
_DOOR_KINDS = ("door", "garage")
'''
CONST_NEW = '''_SIGN_H = 0.6           # sign height
_DOOR_KINDS = ("door", "garage")

#: A HOME HAS NO LIT SIGN (0.169.0). Zoo 1.37.0 paints a business's name on
#: the sign box, and a building of no kind gets its street number -- which
#: on a home is a lit cabinet over a front door, and a lit cabinet says
#: BUSINESS. The walker left the call here (2026-10-02). A building whose
#: identity carries one of these words, whole, derives no storefront sign;
#: its front door takes the wall pack every other exterior door takes, so
#: the door is still lit and the light count does not move.
RESIDENCE_WORDS = frozenset(("apartment", "walkup", "rowhouse", "twin", "mansion", "duplex",
                             "tenement"))


def is_residence(business):
    """Does ``business`` (`level_design.club_building_id`) name a home?"""
    words = str(business or "").lower().replace("-", "_").replace(" ", "_").split("_")
    return bool(RESIDENCE_WORDS & set(words))
'''

SIG_OLD = '''                         report=None, volumes=None, club_rooms=None,
                         storefronts=None):
    """Derive default light anchors'''
SIG_NEW = '''                         report=None, volumes=None, club_rooms=None,
                         storefronts=None, residence=False):
    """Derive default light anchors'''

SIGN_OLD = '''    sign = _storefront_sign(openings, wall_thick)
    sign_door = None
'''
SIGN_NEW = '''    # a residence (0.169.0) derives none: its front door is one more exterior
    # door to the wall-pack loop below
    sign = None if residence else _storefront_sign(openings, wall_thick)
    sign_door = None
'''

CALL_OLD = '''                                   volumes=volumes, club_rooms=club_rooms,
                                   storefronts=storefronts)
    if authored:'''
CALL_NEW = '''                                   volumes=volumes, club_rooms=club_rooms,
                                   storefronts=storefronts,
                                   residence=is_residence(business))
    if authored:'''

SEEN_OLD = '''    assert seen >= 100, seen
'''
SEEN_NEW = '''    # 0.169.0: 102 -> 94, the eight homes' doors take a porch light instead
    assert seen >= 90, seen
'''

TEST = '''"""A home has a porch light over its door, not a lit sign (0.169.0).

Zoo 1.37.0 paints a name on every sign box and a building of no kind shows
its street number; on a home that is a lit cabinet over a front door. The
walker left the call here, 2026-10-02. Held: a residence derives no sign and
its front door takes a wall pack, in the same place a sign's door would have
gone without one; every other building is as it was; and the library's eight
homes built that way.
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import level_design  # noqa: E402
import lights  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))

ROOMS = [{"id": "front_hall", "story": 0, "bounds": [0, 0, 8, 6]}]
OPENINGS = [{"kind": "door", "wall": "ext_0_S", "x": 4.0, "y": 0.0, "width": 1.2,
             "height": 2.2, "sill": 0.0},
            {"kind": "window", "wall": "ext_0_S", "x": 1.5, "y": 0.0, "width": 1.6,
             "height": 1.2, "z": 1.5}]


def _anchors(business):
    man = lights.build_light_manifest("t", ROOMS, OPENINGS, 3.5, cap_thick=0.3, wall_thick=0.3,
                                      business=business)
    return man["anchors"]


def test_the_words_are_whole_words():
    for b in ("apartment_walkup_a01", "rowhouse_raid", "twin_a01", "mansion_a03",
              "lf_block_7 apartment_walkup"):
        assert lights.is_residence(b), b
    for b in ("corner_deli", "gas_station_a02", "strip_club_a01 strip_club", "twinkle_bar",
              "courthouse_a01", "funeral_home_a01", None, ""):
        assert not lights.is_residence(b), b


def test_a_home_takes_a_wall_pack_where_a_shop_takes_a_sign():
    shop, home = _anchors("corner_deli"), _anchors("rowhouse_raid")
    assert [a["type"] for a in shop].count("sign") == 1
    assert [a["type"] for a in shop].count("wall_pack") == 0
    assert [a["type"] for a in home].count("sign") == 0
    packs = [a for a in home if a["type"] == "wall_pack"]
    assert len(packs) == 1 and packs[0]["wall"] == "ext_0_S"
    assert abs(packs[0]["pos"][0] - 4.0) < 1e-6           # over the same door
    # one anchor for one anchor, and nothing else moved
    assert len(home) == len(shop)
    rest = lambda a: [x for x in a if x["type"] not in ("sign", "wall_pack")]   # noqa: E731
    assert rest(home) == rest(shop)


def test_the_library_homes_have_no_sign_and_every_other_storefront_keeps_its_own():
    homes = signs = 0
    for p in sorted(glob.glob(os.path.join(HERE, "specs", "*.json"))):
        if os.path.basename(p).startswith("lf_"):
            continue
        with open(p, encoding="utf-8") as f:
            spec = json.load(f)
        lp = os.path.join(HERE, "build", spec["name"] + ".lights.json")
        if not os.path.exists(lp):
            continue
        with open(lp, encoding="utf-8") as f:
            anchors = json.load(f)["anchors"]
        derived = [a for a in anchors if a["type"] == "sign" and a.get("source") == "derived"]
        if lights.is_residence(level_design.club_building_id(spec)):
            homes += 1
            assert derived == [], spec["name"]
            assert any(a["type"] == "wall_pack" for a in anchors), spec["name"]
        else:
            signs += len(derived)
    assert homes >= 8, homes
    assert signs >= 90, signs
'''


def main():
    t = DC / "test_residence_lights.py"
    assert not t.exists(), "already applied"
    _edit("lights.py", [(CONST_OLD, CONST_NEW), (SIG_OLD, SIG_NEW), (SIGN_OLD, SIGN_NEW),
                        (CALL_OLD, CALL_NEW)])
    _edit("test_sign_business.py", [(SEEN_OLD, SEEN_NEW)])
    t.write_bytes(TEST.encode("utf-8"))
    print("wrote test_residence_lights.py")


if __name__ == "__main__":
    main()
