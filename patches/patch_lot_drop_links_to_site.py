"""Lot 0.125.0: a declared drop's nav link reaches the site in site space (factory roadmap 173, step 3).

Deli Counter 0.226.0 files a one-way off-mesh `nav_link` on every `floor_hole` / `hatch` vertical link
(`ladder.drop_nav_link`). Lot carried `vertical_links` through verbatim with a building tag ("positions are
descriptive"), which was true while the record held only a spec-frame point; a nav link's two positions and the
cut's rect are what an AI and a gate act on, and in building coordinates they would point at the wrong place in
every building but the one at the site's origin. The same seam cold run 9075 found for ladders.

What it changes (anchored; refuses on a miss; CRLF-safe):
  * lot.py `_ladder_to_site` takes the point tables and a label (defaults: the ladder's, byte for byte), so one
    transform and one refusal serve both records; `_VLINK_POINTS_3` / `_VLINK_POINT_LISTS_2` name a drop link's
    positions and its `hole` corners.
  * the `vertical_links` carry-through moves a record that carries a `nav_link` with it.
  * tests/test_drop_links_reach_the_site.py (pins deli_a01, which declares a floor hole and a hatch), VERSION
    0.125.0, CHANGELOG.

    python patches/patch_lot_drop_links_to_site.py --tests   # the test file only
    python patches/patch_lot_drop_links_to_site.py           # everything
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOT = ROOT / "lot"


def _apply(path, old, new, count=1):
    raw = path.read_bytes()
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n") - crlf
    assert crlf == 0 or lf == 0, f"{path.name}: mixed endings ({crlf} CRLF, {lf} LF)"
    eol = "\r\n" if crlf else "\n"
    text = raw.decode("utf-8")
    o, n = old.replace("\n", eol), new.replace("\n", eol)
    assert text.count(o) == count, f"{path.name}: anchor found {text.count(o)} times, wanted {count}: {old[:70]!r}"
    path.write_bytes(text.replace(o, n).encode("utf-8"))


TABLES_OLD = '''_LADDER_POINT_LISTS_2 = (
    ("geometry", "climb_rect"),
)
'''
TABLES_NEW = '''_LADDER_POINT_LISTS_2 = (
    ("geometry", "climb_rect"),
)
#: Every position in a Deli Counter DECLARED DROP (a `floor_hole` / `hatch`
#: vertical link carrying `ladder.drop_nav_link`, 0.226.0): the link's two
#: points, and the cut's rect as two corners. Listed for the same reason as the
#: ladder's tables, and moved by the same pass.
_VLINK_POINTS_3 = (
    ("nav_link", "start_position"),
    ("nav_link", "end_position"),
)
_VLINK_POINT_LISTS_2 = (
    ("nav_link", "hole"),
)
'''

SIG_OLD = '''def _ladder_to_site(lad, placement):
    """A ladder record with every position moved into site space.
'''
SIG_NEW = '''def _ladder_to_site(lad, placement, points3=_LADDER_POINTS_3,
                    lists3=_LADDER_POINT_LISTS_3, lists2=_LADDER_POINT_LISTS_2,
                    what="ladder"):
    """A ladder record with every position moved into site space -- or, with
    its own tables, a declared drop's (`_VLINK_POINTS_3`, 0.125.0).
'''
LOOP3_OLD = "    for path in _LADDER_POINTS_3:\n"
LOOP3_NEW = "    for path in points3:\n"
LOOPL3_OLD = "    for path in _LADDER_POINT_LISTS_3:\n"
LOOPL3_NEW = "    for path in lists3:\n"
LOOPL2_OLD = "    for path in _LADDER_POINT_LISTS_2:\n"
LOOPL2_NEW = "    for path in lists2:\n"
ERR_OLD = '''        raise ValueError(
            "lot: ladder %r carries position(s) this pass does not know how to "
            "move into site space: %s -- add them to _LADDER_POINTS_* rather "
            "than shipping them in building coordinates"
            % (lad.get("id", "?"), ", ".join(sorted(missed))))
'''
ERR_NEW = '''        raise ValueError(
            "lot: %s %r carries position(s) this pass does not know how to "
            "move into site space: %s -- add them to the point tables rather "
            "than shipping them in building coordinates"
            % (what, lad.get("id", lad.get("kind", "?")),
               ", ".join(sorted(missed))))
'''

CARRY_OLD = '''        # vertical_links / openings: carry through, tag building (positions are
        # descriptive; markers already carry the authoritative world coords)
        for key in ("vertical_links", "openings"):
            for item in gp.get(key, []):
                wi = dict(item)
                wi["building"] = bid
                site[key].append(wi)
'''
CARRY_NEW = '''        # vertical_links / openings: carry through, tag building (positions are
        # descriptive; markers already carry the authoritative world coords)
        # -- EXCEPT a declared drop's nav link (Deli Counter 0.226.0), whose
        # two points and `hole` corners an AI and a gate act on: those move
        # into site space with the building, as a ladder's do (0.125.0).
        for key in ("vertical_links", "openings"):
            for item in gp.get(key, []):
                if key == "vertical_links" and item.get("nav_link"):
                    wi = _ladder_to_site(item, placement, _VLINK_POINTS_3, (),
                                         _VLINK_POINT_LISTS_2, "vertical link")
                else:
                    wi = dict(item)
                wi["building"] = bid
                site[key].append(wi)
'''

TEST = '''"""A building's declared drops reach the site, in site space (0.125.0, factory roadmap 173).

Deli Counter 0.226.0 files a one-way off-mesh `nav_link` on every `floor_hole` / `hatch` vertical link. Lot
carried `vertical_links` verbatim, which left those positions in building coordinates -- the seam cold run
9075 found for ladders. These run `merge_gameplay` against the real shell that declares both kinds.

Run:  python -m pytest tests/test_drop_links_reach_the_site.py -q
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import lot as L  # noqa: E402

#: deli_a01 declares a floor hole (story 1, 8, -4) and a hatch (story 1, -12, 8).
SHELL = "deli_a01"
BUILD = os.path.join(HERE, "..", "deli_counter", "build")


def _drops():
    p = os.path.join(BUILD, SHELL + ".gameplay.json")
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as fh:
        d = json.load(fh)
    return [v for v in (d.get("vertical_links") or []) if v.get("nav_link")]


def test_the_shell_this_pins_against_declares_drops_with_links():
    drops = _drops()
    assert drops is not None, "deli_counter/build/deli_a01.gameplay.json is missing: build the library"
    assert drops, "deli_a01's vertical links carry no nav_link: Deli Counter 0.226.0 not built yet"
    assert {v["kind"] for v in drops} == {"floor_hole", "hatch"}


def _merge(at, rot=0):
    """The site manifest for one placement of the pinned shell, as `merge_gameplay` builds it (the same
    fixture shape as tests/test_ladders_reach_the_site.py: `gameplay` is what it resolves the data from)."""
    site_spec = {"name": "t", "buildings": [
        {"id": "b0", "glb": SHELL + ".glb", "gameplay": SHELL + ".gameplay.json", "at": list(at), "rot": rot},
    ]}
    return L.merge_gameplay(site_spec, BUILD)


def _carried(site):
    return [v for v in site["vertical_links"] if v.get("nav_link")]


def test_a_drop_link_moves_with_the_building():
    """FAILS BEFORE THIS FIX: the link's points stayed in building coordinates."""
    at = (40.0, -10.0)
    site = _merge(at, 90)
    assert site["interactives"], "the fixture loaded no building data"
    carried = _carried(site)
    assert carried, site["vertical_links"][:2]
    local = {v["nav_link"]["id"]: v for v in _drops()}
    placement = {"at": list(at), "rot": 90}
    for v in carried:
        src = local[v["nav_link"]["id"]]
        for key in ("start_position", "end_position"):
            exp = L._place_point(*src["nav_link"][key], placement)
            assert v["nav_link"][key] == exp, (key, v["nav_link"][key], exp)
        for got, (hx, hy) in zip(v["nav_link"]["hole"], src["nav_link"]["hole"]):
            rx, ry = L._rotate_xy(hx, hy, 90)
            assert got == [rx + at[0], ry + at[1]], (got, hx, hy)
        assert v["building"] == "b0"


def test_height_is_preserved_because_buildings_share_the_ground():
    site = _merge((7.0, 7.0))
    local = {v["nav_link"]["id"]: v for v in _drops()}
    for v in _carried(site):
        src = local[v["nav_link"]["id"]]
        assert v["nav_link"]["start_position"][2] == src["nav_link"]["start_position"][2]
        assert v["nav_link"]["end_position"][2] == src["nav_link"]["end_position"][2]


def test_the_buildings_own_record_is_not_rewritten():
    before = json.dumps(_drops(), sort_keys=True)
    _merge((12.0, 3.0))
    assert json.dumps(_drops(), sort_keys=True) == before


def test_a_record_without_a_link_still_rides_verbatim():
    site = _merge((5.0, 5.0))
    plain = [v for v in site["vertical_links"] if not v.get("nav_link")]
    assert plain, "deli_a01 declares a descriptive stair link; expected it carried verbatim"
    for v in plain:
        assert v["kind"] == "stair" and v["building"] == "b0"
'''

CHANGELOG = '''## 0.125.0 - a declared drop's nav link reaches the site in site space

**Factory roadmap 173, step 3.** Deli Counter 0.226.0 files a one-way off-mesh `nav_link` on every `floor_hole`
/ `hatch` vertical link (`ladder.drop_nav_link`). This repo carried `vertical_links` through verbatim with a
building tag -- "positions are descriptive; markers already carry the authoritative world coords" -- which was
true while the record held only a spec-frame point. A nav link's two positions and the cut's rect are what an AI
and a gate act on, and in building coordinates they would name the wrong place in every building but the one at
the site's origin: the seam cold run 9075 found for ladders, one record over.

### Changed
- `_ladder_to_site` takes its point tables and a label (defaults: the ladder's, byte for byte), so one transform
  and one refusal serve both records; `_VLINK_POINTS_3` / `_VLINK_POINT_LISTS_2` name a drop link's two points
  and its `hole` corners.
- The `vertical_links` carry-through moves a record that carries a `nav_link` with the building; a record
  without one (a descriptive `stair` link) rides verbatim as before.
- `tests/test_drop_links_reach_the_site.py` pins `deli_a01`, which declares a floor hole and a hatch, through
  `merge_gameplay`: the link's points land where `_place_point` puts them, the hole's corners translate, the
  building's own record is untouched.

'''


def write_tests():
    (LOT / "tests" / "test_drop_links_reach_the_site.py").write_text(TEST, encoding="utf-8")
    print("wrote lot/tests/test_drop_links_reach_the_site.py")


def main(argv):
    if "--tests" in argv:
        write_tests()
        return 0
    lp = LOT / "lot.py"
    _apply(lp, TABLES_OLD, TABLES_NEW)
    _apply(lp, SIG_OLD, SIG_NEW)
    _apply(lp, LOOP3_OLD, LOOP3_NEW)
    _apply(lp, LOOPL3_OLD, LOOPL3_NEW)
    _apply(lp, LOOPL2_OLD, LOOPL2_NEW)
    _apply(lp, ERR_OLD, ERR_NEW)
    _apply(lp, CARRY_OLD, CARRY_NEW)
    v = LOT / "VERSION"
    assert v.read_text(encoding="utf-8").strip() == "Lot 0.124.0", v.read_text(encoding="utf-8")
    v.write_text("Lot 0.125.0", encoding="utf-8")
    cl = LOT / "CHANGELOG.md"
    raw = cl.read_bytes()
    eol = "\r\n" if raw.count(b"\r\n") else "\n"
    text = raw.decode("utf-8")
    assert text.startswith("## 0.124.0"), text[:40]
    cl.write_bytes((CHANGELOG.replace("\n", eol) + text).encode("utf-8"))
    write_tests()
    print("Lot 0.125.0 applied: declared drops' nav links move into site space, test, VERSION, CHANGELOG")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
