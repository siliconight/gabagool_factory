"""Deli Counter 0.269.0 on a CLONE (<repo>, at 0.268.0): a switchback's seam wall draws as a raking rail (the walker's
walk of cold run 9386, finding 6 -- the block they circled). The seam's collider stays exactly where it is, unseen; a
visual-only `stoop_railing` flight slot -- no greybox box, no collider -- follows the upper flight's inner edge. Anchored; refuses on a miss.

    python edit_dc_stair_rake.py <repo>
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


edit("stairwell.py", [
    ("""def _seam_pieces(st, H, s, sid, travel, pos, span):""",
     """def _seam_pieces(st, H, s, sid, travel, pos, span, rises_hi=True):"""),
    ("""    z_lo = s * H + agent_contract.body_height()
    return [{"stair": sid, "story": s, "kind": "side", "axis": travel,
             "pos": pos, "lo": span[0], "hi": span[1], "z_lo": round(z_lo, 4)}]""",
     """    z_lo = s * H + agent_contract.body_height()
    # `rises_hi` (0.269.0): whether the leg climbs toward ``hi`` -- the raking
    # rail the builder draws along it points its high end that way
    return [{"stair": sid, "story": s, "kind": "side", "axis": travel,
             "pos": pos, "lo": span[0], "hi": span[1], "z_lo": round(z_lo, 4),
             "rises_hi": bool(rises_hi)}]"""),
    ("""                    raw += _seam_pieces(st, H, s, sid, travel, pos_side,
                                        s_span)""",
     """                    raw += _seam_pieces(st, H, s, sid, travel, pos_side,
                                        s_span, rises_hi=arrive_hi)"""),
])

edit("deli_counter.py", [
    ("""            if "z_lo" in g:
                lift = max(0.0, float(g["z_lo"]) - z0)""",
     """            seam = "z_lo" in g
            seam_z0 = z0
            if "z_lo" in g:
                lift = max(0.0, float(g["z_lo"]) - z0)"""),
    ("""                size_y=round(sy, 4), size_z=round(h, 4), collision="convex",
                material=mat, form=("level" if g["kind"] == "rail" else None)))""",
     """                size_y=round(sy, 4), size_z=round(h, 4), collision="convex",
                material=mat, form=("level" if g["kind"] == "rail" else None),
                visual=not seam))
            # A SEAM DRAWS AS A RAKING RAIL (0.269.0). The walker, walking cold
            # run 9386, circled the block a switchback's upper flight carries
            # over the lower one's edge: "the walling/railing doesn't loook
            # natural yet"; their pick, the compact U, a rail between the
            # flights. The block stays a collider, unseen -- its underside a
            # body's height up so the lower flight keeps its headroom
            # (`stairwell._seam_pieces`), which a rail's collider following the
            # upper flight down to its treads would not -- and a visual-only
            # `stoop_railing` flight (Zoo >= 1.129.0) follows the upper flight's
            # inner edge, from its foot on the storey's floor to RAIL_H over its
            # head. Zoo draws the high end at +X; the volume's long-side turn
            # sends +X along -Y for a Y run, so a rail rising toward +Y turns a
            # further 180, and an X run rising toward -X turns 180
            # (`stoop.RAIL_ROT_Y`'s measured convention).
            if seam:
                hr = H + stoop.RAIL_H
                rises_hi = bool(g.get("rises_hi", True))
                # Zoo draws the high end at +X; the composer turns +X by rot_y to plan +X (0), -Y (90), -X (180)
                # or +Y (270) (`stoop.RAIL_ROT_Y`'s measured convention)
                if g["axis"] == "Y":
                    rot = 270.0 if rises_hi else 90.0
                else:
                    rot = 0.0 if rises_hi else 180.0
                # A SLOT WITH NO GREYBOX BOX, deliberately: a greybox visual box is navigation data to Lot's walk
                # bake (the factory's memory `greybox-is-in-the-walk-navmesh`, cold run 9340), and this one would
                # stand a thin wall from the storey's floor at the seam -- the floor-height seam 0.225.0 measured
                # cutting the lower flight. With no greybox node the composer places the module by the slot's own
                # transform and turn (`themed_tscn`: no extent to fit), and the bake sees the seam's collider alone.
                rmat = next((m for m in ("metal_painted", "wood") if m in have), None) or self.s.default_material
                self.slots.append({
                    "slot_id": f"stair_guard_rake_{k}", "role": "prop", "size_mod": "full",
                    "style": skin_style.style_for(rmat, self._mat_style, self.s.default_material),
                    "material": rmat, "species": "stoop_railing", "stock": None, "variant": 0,
                    "form": "flight", "current_ref": "prop_greybox_01", "kit_axis": "material",
                    "wall": None, "story": None, "facing": None,
                    "transform": {"translation": [round(x, 4), round(y, 4), round(seam_z0 + hr / 2.0, 4)],
                                  "rot_y": rot, "scale": [1.0, 1.0, 1.0]},
                    "fit": {"dims": [round(along, 4), self.RAKE_THICK_M, round(hr, 4)],
                            "pivot": "center", "openings": [], "collision": "none"},
                })"""),
    ("""    def _stair_guards(self):""",
     """    #: a seam's raking rail's depth across (0.269.0): the top rail's width, inside Zoo's genome's 0.03..0.12
    RAKE_THICK_M = 0.05

    def _stair_guards(self):"""),
])

TEST = '''"""A switchback's seam draws as a raking rail (0.269.0): its collider kept where it was, unseen; a visual-only
`stoop_railing` flight along the upper flight, its high end up the flight. The walker, walking cold run 9386, of the
block over the office switchback's upper flight: "the walling/railing doesn't loook natural yet". FAILS ON 0.268.0."""
import importlib
import json
import os
import sys
import types

import pytest

import stoop
import stairwell

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def dc(monkeypatch):
    for name in ("bpy", "bmesh"):
        try:
            importlib.import_module(name)
        except ImportError:
            monkeypatch.setitem(sys.modules, name, types.ModuleType(name))
    monkeypatch.delitem(sys.modules, "deli_counter", raising=False)
    mod = importlib.import_module("deli_counter")
    yield mod
    sys.modules.pop("deli_counter", None)


def _office(dc):
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
    return spec, b, cols


def test_the_seam_keeps_its_collider_unseen_and_gains_a_raking_rail(dc):
    spec, b, cols = _office(dc)
    seams = [(k, g) for k, g in enumerate(stairwell.stair_guards(spec)) if "z_lo" in g]
    assert len(seams) == 1, seams
    k, g = seams[0]
    side = "stair_guard_side_%d" % k
    assert side + "_col" in cols
    assert side not in {s["slot_id"] for s in b.slots}
    rake = [s for s in b.slots if s["slot_id"] == "stair_guard_rake_%d" % k]
    assert len(rake) == 1, [s["slot_id"] for s in b.slots if "rake" in s["slot_id"]]
    r = rake[0]
    assert (r["species"], r["form"], r["fit"]["collision"]) == ("stoop_railing", "flight", "none"), r
    along = round(g["hi"] - g["lo"], 4)
    assert r["fit"]["dims"] == [along, b.RAKE_THICK_M, round(spec.story_height + stoop.RAIL_H, 4)], r["fit"]
    want = 270.0 if g["rises_hi"] else 90.0
    if g["axis"] == "X":
        want = 0.0 if g["rises_hi"] else 180.0
    assert r["transform"]["rot_y"] == want, (r["transform"], g)
    assert "stair_guard_rake_%d_col" % k not in cols


def test_the_rake_draws_no_greybox_box(dc):
    """A greybox visual box is navigation data to Lot's walk bake; the rake has none."""
    import skin_style
    from spec_loader import spec_from_dict
    spec = spec_from_dict(json.load(open(os.path.join(HERE, "specs", "office.json"), encoding="utf-8")))
    b = dc._Builder(spec)
    b.slots = []
    b._mat_style = skin_style.material_styles([m.id for m in spec.materials])
    boxes = []
    b._box = lambda name, *a, **k: boxes.append(name)
    b._col_box = lambda *a, **k: None
    b._record_surface = lambda *a, **k: None
    b._stair_guards()
    b._volumes()
    assert not [n for n in boxes if "rake" in n], boxes
'''
(R / "tests" / "test_stair_rake.py").write_text(TEST, encoding="utf-8", newline="\n")
print("seam: collider unseen, stair_guard_rake flight rail; tests/test_stair_rake.py")
