"""Deli Counter 0.268.0 on a CLONE (<repo>): a stair hole's rail is a balustrade -- Zoo's `stoop_railing`, level form,
painted iron where the palette has it -- not a solid wood box (the walker's walk of cold run 9386, finding 6). The
collider is unchanged: the rail's own `_col` box, as before. Anchored; refuses on a miss.

    python edit_dc_stair_balustrade.py <repo>
"""
import pathlib
import sys

R = pathlib.Path(sys.argv[1])


def edit(rel, pairs):
    p = R / rel
    b = p.read_bytes()
    crlf = b"\r\n" in b
    t = b.decode("utf-8").replace("\r\n", "\n")
    for o, n in pairs:
        assert t.count(o) == 1, (rel, o[:70])
        t = t.replace(o, n)
    p.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))


edit("prop_species.py", [
    ("""PROP_SPECIES = (
""", """PROP_SPECIES = (
    # A STAIR'S RAIL IS A BALUSTRADE (0.268.0). The walker, walking cold run
    # 9386, of the office stair's hole ringed by solid wood guard boxes: "the
    # walling/railing doesn't loook natural yet". `_stair_guards` names each
    # rail `stair_guard_rail_<k>`, a stair's or a ramp's; Zoo's `stoop_railing`
    # (>= 1.128.0, 8 m long and 0.12 m deep) draws it as its LEVEL form, posts
    # at least every 2.0 m and pickets between. No other row's keyword is in
    # those names, and no authored volume carries one, so first is as good as
    # anywhere; first, so a later row can never claim them.
    (("stair_guard_rail",), "stoop_railing"),
"""),
])

edit("deli_counter.py", [
    ("""                h = stairwell.GUARD_HEIGHT
                # a piece may name its own (0.241.0: a ramp's rail is steel)
                mat = g.get("material") or ("wood" if "wood" in have else None)""",
     """                h = stairwell.GUARD_HEIGHT
                # a piece may name its own (0.241.0: a ramp's rail is steel);
                # a stair's is painted iron where the palette has it, else wood
                # (0.268.0, `prop_species`'s balustrade row)
                mat = g.get("material") or next(
                    (m for m in ("metal_painted", "wood") if m in have), None)"""),
    ("""                size_y=round(sy, 4), size_z=round(h, 4), collision="convex",
                material=mat))""",
     """                size_y=round(sy, 4), size_z=round(h, 4), collision="convex",
                material=mat, form=("level" if g["kind"] == "rail" else None)))"""),
])

edit("tests/test_ramp_cut.py", [
    ("""    assert 'mat = g.get("material") or ("wood" if "wood" in have else None)' in src""",
     """    # the piece's own material first, still (0.268.0 made the default painted iron, then wood)
    assert 'mat = g.get("material") or next(' in src"""),
])

TEST = '''"""A stair hole's rail is a balustrade (0.268.0): Zoo's `stoop_railing`, its level form, painted iron where the palette
has it, the rail's own collider kept. The walker, walking cold run 9386, of the office stair's solid wood guard boxes:
"the walling/railing doesn't loook natural yet". FAILS ON 0.267.0 (no species, wood)."""
import importlib
import json
import os
import sys
import types

import pytest

import prop_species

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_a_stairs_rail_names_the_balustrade_and_nothing_else_does():
    for name in ("stair_guard_rail_0", "stair_guard_rail_11"):
        assert prop_species.species_for_name(name) == "stoop_railing", name
    for name in ("stair_guard_side_0", "stair_guard_back_10"):
        assert prop_species.species_for_name(name) is None, name
    assert not prop_species.owns_collision("stoop_railing")


@pytest.fixture
def dc(monkeypatch):
    """deli_counter against stub bpy/bmesh, as test_depth_long does."""
    for name in ("bpy", "bmesh"):
        try:
            importlib.import_module(name)
        except ImportError:
            monkeypatch.setitem(sys.modules, name, types.ModuleType(name))
    monkeypatch.delitem(sys.modules, "deli_counter", raising=False)
    mod = importlib.import_module("deli_counter")
    yield mod
    sys.modules.pop("deli_counter", None)


def test_the_offices_rails_are_iron_balustrades_and_keep_their_colliders(dc):
    import skin_style
    from spec_loader import spec_from_dict
    spec = spec_from_dict(json.load(open(os.path.join(HERE, "specs", "office.json"), encoding="utf-8")))
    b = dc._Builder(spec)
    b.slots = []
    b._mat_style = skin_style.material_styles([m.id for m in spec.materials])
    cols = []
    b._box = lambda *a, **k: None
    b._col_box = lambda name, *a, **k: cols.append(name)
    b._record_surface = lambda *a, **k: None
    b._stair_guards()
    b._volumes()
    rails = [s for s in b.slots if s["slot_id"].startswith("stair_guard_rail_")]
    assert len(rails) == 6, [s["slot_id"] for s in rails]
    for s in rails:
        assert (s["species"], s["form"], s["material"]) == ("stoop_railing", "level", "metal_painted"), s
        assert s["slot_id"] + "_col" in cols, s["slot_id"]
    walls = [s for s in b.slots if s["slot_id"].startswith(("stair_guard_side_", "stair_guard_back_"))]
    assert walls and all(s["species"] is None and s["form"] is None for s in walls)
'''
(R / "tests" / "test_stair_balustrade.py").write_text(TEST, encoding="utf-8", newline="\n")
print("prop_species balustrade row, _stair_guards iron rails in the level form; tests/test_stair_balustrade.py")
