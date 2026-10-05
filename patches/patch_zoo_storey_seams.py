"""Zoo 1.70.0: a run module's top and bottom are joints too -- no V-groove at a
storey seam.

Cold runs 9153-9155's frames: short pale-then-dark dashes at regular spacing
along the storey line of the stone Empty's end wall. Measured on 9155's own
module GLB (`wall_delco_1997_01_w200_h310_mstone_idrywall.glb`): the panel's
ends are square (0.81.1's butt planes), but its top and bottom edges carry the
style's 3 mm x 3 mm chamfer -- vertices at +-1.547 against the face's +-1.550.
An Empty stacks storey on storey (Deli Counter 0.175.2: 0.0-3.1 then 3.1-5.9
on gs_empty_rowhome_d), so two chamfers meet as a V 6 mm wide and 3 mm deep
along the whole seam. The frames' 65-degree camera at 1152 x 648 puts 18-26 mm
in a pixel 10-15 m away, the groove a quarter to a third of one, and a sub-pixel
line at a slight slope aliases into regular dashes;
the up-facing facet catches the fill light, the down-facing one does not. See
`zoo_storey_seams/CHANGELOG_1.70.0.md`.

Anchored edits (every anchor once; refuses on a miss):
  zoo_keeper/core/arch.py         butt_planes(species, w, h): ends, top, bottom
  zoo_keeper/recipes/_arch.py     passes the module's height
  tests/test_butt_joints.py       the pins move with the decision; they fail
                                  on 1.69.0 (the planes test and the top edge)
CHANGELOG and VERSION.

    python patch_zoo_storey_seams.py
"""
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
ZOO = HERE.parent / "zoo"
SRC = HERE / "zoo_storey_seams"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


ARCH_OLD = '''def butt_planes(species: str, w: float):
    """The planes where this module MEETS ITS NEIGHBOUR, as ``(axis, coord)``.
'''
ARCH_NEW = '''def butt_planes(species: str, w: float, h: float):
    """The planes where this module MEETS ITS NEIGHBOUR, as ``(axis, coord)``.
'''

ARCH_DOC_OLD = '''    It is the plate-tile groove again (``recipes/_arch.py``), which was fixed
    for plates on the grounds that walls' chamfers "sit on real corners". A
    wall's END edges do not: they sit on the plane its neighbour shares. The
    corners a person can see -- a jamb's reveal, a sill, a header's underside,
    the top and bottom of the face -- are not on these planes and keep their
    chamfer.
'''
ARCH_DOC_NEW = '''    It is the plate-tile groove again (``recipes/_arch.py``), which was fixed
    for plates on the grounds that walls' chamfers "sit on real corners". A
    wall's END edges do not: they sit on the plane its neighbour shares. The
    corners a person can see -- a jamb's reveal, a sill, a header's underside
    -- are not on these planes and keep their chamfer.

    AND ITS TOP AND BOTTOM (1.70.0), ``z = -h/2`` and ``z = +h/2``. This said
    "the top and bottom of the face" were real corners too. They are not: in
    Deli Counter's model a run module's top and bottom always meet something
    -- the next storey's module, flush, on an Empty (0.175.2 stacks them:
    gs_empty_rowhome_d's end wall is 0.0-3.1 then 3.1-5.9), or the slab's
    edge on an enterable building (bank_tower_a02: 0.0-4.3, slab, 4.6-8.9).
    Cold runs 9153-9155 drew the groove on the stone Empty's end wall: a V
    6 mm wide and 3 mm deep along the storey seam, a quarter to a third of a
    pixel in those frames, aliased into a row of pale-then-dark dashes.
'''

ARCH_RET_OLD = '''    if species not in RUN_SPECIES:
        return ()
    hw = w / 2.0
    return ((0, -hw), (0, hw))
'''
ARCH_RET_NEW = '''    if species not in RUN_SPECIES:
        return ()
    hw, hh = w / 2.0, h / 2.0
    return ((0, -hw), (0, hw), (2, -hh), (2, hh))
'''

EDGE_DOC_OLD = '''    """True when edge ``a``-``b`` lies IN one of ``planes``: both ends on the
    SAME plane. A full-width edge has one end on each butt plane and lies in
    neither -- the top of a wall face, which keeps its chamfer."""
'''
EDGE_DOC_NEW = '''    """True when edge ``a``-``b`` lies IN one of ``planes``: both ends on the
    SAME plane. An edge with one end on each of two planes lies in neither;
    the top edge of a wall face lies in its top plane (1.70.0), so it is a
    butt edge now, and a jamb's reveal lies in none."""
'''

RECIPE_OLD = '''    butts = arch.butt_planes(species, w)
'''
RECIPE_NEW = '''    butts = arch.butt_planes(species, w, h)
'''

T_PLANES_OLD = '''@pytest.mark.parametrize("species", ["wall", "wallEnd", "doorway", "window", "breach"])
def test_a_standing_module_meets_its_neighbours_at_its_two_ends(species):
    assert arch.butt_planes(species, 2.0) == ((0, -1.0), (0, 1.0))


@pytest.mark.parametrize("species", arch.PLATE_SPECIES)
def test_plates_declare_no_butt_planes(species):
    """Their tiles are unbevelled already; nothing to exempt."""
    assert arch.butt_planes(species, 12.0) == ()


def test_a_prop_stands_alone_and_keeps_every_chamfer():
    """`prop` shares the slab builder with walls; a desk's ends are corners."""
    assert arch.butt_planes("prop", 1.6) == ()
'''
T_PLANES_NEW = '''@pytest.mark.parametrize("species", ["wall", "wallEnd", "doorway", "window", "breach"])
def test_a_standing_module_meets_its_neighbours_at_its_ends_top_and_bottom(species):
    """1.70.0 added the top and bottom: the next storey, or the slab's edge."""
    assert arch.butt_planes(species, 2.0, 3.1) == ((0, -1.0), (0, 1.0), (2, -1.55), (2, 1.55))


@pytest.mark.parametrize("species", arch.PLATE_SPECIES)
def test_plates_declare_no_butt_planes(species):
    """Their tiles are unbevelled already; nothing to exempt."""
    assert arch.butt_planes(species, 12.0, 0.3) == ()


def test_a_prop_stands_alone_and_keeps_every_chamfer():
    """`prop` shares the slab builder with walls; a desk's ends are corners."""
    assert arch.butt_planes("prop", 1.6, 0.8) == ()
'''

T_HELPER_OLD = '''def _planes():
    return arch.butt_planes("wall", _W)
'''
T_HELPER_NEW = '''def _planes():
    return arch.butt_planes("wall", _W, _H)
'''

T_TOP_OLD = '''def test_the_top_edge_of_a_face_is_not_although_both_ends_touch_a_butt_plane():
    """One end on each plane lies in neither: the chamfer along the top stays."""
    a = (-1.0, -_D / 2, _H / 2)
    b = (1.0, -_D / 2, _H / 2)
    assert not arch.edge_on_butt_plane(a, b, _planes())
'''
T_TOP_NEW = '''def test_the_top_edge_of_a_face_is_a_butt_edge_now():
    """REVERSED in 1.70.0, kept so the old decision is findable: this pinned
    the top chamfer as kept ("one end on each plane lies in neither"). The
    top edge lies in the module's top plane, which the next storey or the
    slab's edge shares -- cold runs 9153-9155's storey-seam dashes."""
    a = (-1.0, -_D / 2, _H / 2)
    b = (1.0, -_D / 2, _H / 2)
    assert arch.edge_on_butt_plane(a, b, _planes())


def test_an_edge_from_one_plane_to_another_still_lies_in_neither():
    """A face's diagonal from the top plane to an end plane is in no plane."""
    a = (-0.5, -_D / 2, _H / 2)
    b = (1.0, -_D / 2, 0.0)
    assert not arch.edge_on_butt_plane(a, b, _planes())
'''

T_DOOR_OLD = '''    planes = arch.butt_planes("doorway", 1.25)
'''
T_DOOR_NEW = '''    planes = arch.butt_planes("doorway", 1.25, _H)
'''

T_BPY_OLD = '''def test_bpy_a_wall_has_no_chamfer_at_its_ends_and_keeps_its_top(tmp_path):
    pytest.importorskip("bpy")
    w, objs = _build(tmp_path, "wall", 200)
    xs = _xs(objs)
    assert xs[0] == pytest.approx(-w / 2) and xs[-1] == pytest.approx(w / 2)
    inside = [x for x in xs if w / 2 - 0.01 < abs(x) < w / 2 - 1e-4]
    assert not inside, inside
    zs = sorted({round(v.co.z, 4) for o in objs for v in o.data.vertices})
    assert any(0.0 < _H / 2 - z < 0.01 for z in zs), zs      # top chamfer kept
'''
T_BPY_NEW = '''def test_bpy_a_wall_has_no_chamfer_at_its_ends_top_or_bottom(tmp_path):
    """1.70.0: the top and bottom lost their chamfer as the ends did. This
    asserted the top chamfer KEPT until then."""
    pytest.importorskip("bpy")
    w, objs = _build(tmp_path, "wall", 200)
    xs = _xs(objs)
    assert xs[0] == pytest.approx(-w / 2) and xs[-1] == pytest.approx(w / 2)
    inside = [x for x in xs if w / 2 - 0.01 < abs(x) < w / 2 - 1e-4]
    assert not inside, inside
    zs = sorted({round(v.co.z, 4) for o in objs for v in o.data.vertices})
    assert not [z for z in zs if _H / 2 - 0.01 < abs(z) < _H / 2 - 1e-4], zs
'''


def main():
    assert (ZOO / "VERSION").read_text(encoding="utf-8").strip() == "1.69.0"
    _edit(ZOO / "zoo_keeper" / "core" / "arch.py",
          [(ARCH_OLD, ARCH_NEW), (ARCH_DOC_OLD, ARCH_DOC_NEW), (ARCH_RET_OLD, ARCH_RET_NEW),
           (EDGE_DOC_OLD, EDGE_DOC_NEW)])
    _edit(ZOO / "zoo_keeper" / "recipes" / "_arch.py", [(RECIPE_OLD, RECIPE_NEW)])
    _edit(ZOO / "tests" / "test_butt_joints.py",
          [(T_PLANES_OLD, T_PLANES_NEW), (T_HELPER_OLD, T_HELPER_NEW), (T_TOP_OLD, T_TOP_NEW),
           (T_DOOR_OLD, T_DOOR_NEW), (T_BPY_OLD, T_BPY_NEW)])
    ch = ZOO / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    ch.write_text((SRC / "CHANGELOG_1.70.0.md").read_text(encoding="utf-8").rstrip("\n") + "\n\n" + s,
                  encoding="utf-8", newline="\n")
    (ZOO / "VERSION").write_text("1.70.0", encoding="utf-8", newline="\n")
    print("applied Zoo 1.70.0")


if __name__ == "__main__":
    main()
