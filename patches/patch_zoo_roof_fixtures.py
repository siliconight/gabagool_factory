"""Zoo 1.74.0: an Empty's TV antenna and satellite dish, two roof covers in the
gutters' white aluminium. Deli Counter (>= 0.185.0) authors which houses have
them; Patina (>= 0.29.0) orders them. See `zoo_roof_fixtures/CHANGELOG_1.74.0.md`.

Anchored edits (every anchor once; refuses on a miss):
  zoo_keeper/core/dressing.py        METAL_COVERS names both; antenna_parts,
                                     dish_parts and their constants
  zoo_keeper/recipes/dress_cover.py  the contract's list; builds both (the
                                     dish's head tilted about its bowl)
Copies the test; CHANGELOG and VERSION.

    python patch_zoo_roof_fixtures.py
"""
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve().parent
ZOO = HERE.parent / "zoo"
SRC = HERE / "zoo_roof_fixtures"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


METAL_OLD = '''#: COVERS THAT ARE PAINTED METAL (1.67.0), whatever trim the style names: a
#: gutter and its downspout are aluminium on a 1990s rowhouse, and in the
#: concrete every other cover wears they read as one more ledge.
METAL_COVERS = ("gutter_run", "downspout", "ac_unit")
'''
METAL_NEW = '''#: COVERS THAT ARE PAINTED METAL (1.67.0), whatever trim the style names: a
#: gutter and its downspout are aluminium on a 1990s rowhouse, and in the
#: concrete every other cover wears they read as one more ledge. So are an
#: Empty's air conditioners (1.69.0) and its roof's TV antenna and satellite
#: dish (1.74.0): on a side that has a gutter, each merges into its mesh.
METAL_COVERS = ("gutter_run", "downspout", "ac_unit", "tv_antenna", "sat_dish")
'''

PARTS_OLD = '''    parts.append(((inner / 2.0 - 0.05, SEC_Y1 + 0.0115, zb + SEC_LOCK_Z + 0.07), (0.07, 0.024, 0.14)))
    return parts


def frame_strips('''
PARTS_NEW = '''    parts.append(((inner / 2.0 - 0.05, SEC_Y1 + 0.0115, zb + SEC_LOCK_Z + 0.07), (0.07, 0.024, 0.14)))
    return parts


#: AN EMPTY'S TV ANTENNA (1.74.0). The comps' rowhome: "a TV antenna on the
#: roof" -- a 1990s VHF/UHF aerial on a mast, from before cable reached most
#: of the city. A plate on the roof and the mast up from it; a boom across
#: the mast's top; elements across the boom, longest at the back (the
#: reflector) and shortening toward the end that points at the transmitter,
#: which is local +x -- Patina (>= 0.29.0) gives that bearing as the order's
#: tangent. Drawn about twice real thickness, as the gutter's sheet is, so a
#: 2 cm tube holds at street distance rather than breaking into dashes.
ANT_MAST, ANT_BOOM, ANT_ELEMENT = 0.05, 0.04, 0.03
ANT_PLATE, ANT_PLATE_T = 0.36, 0.02
ANT_TOP = 0.15                    # the mast stands this far above the boom
ANT_PITCH = 0.20                  # between elements, along the boom
ANT_LONG, ANT_SHORT = 1.6, 0.36   # the reflector, the last director
ANT_BACK = 0.4                    # the share of the boom behind the mast


def antenna_parts(boom: float, mast: float):
    """A rooftop TV antenna's parts (1.74.0), as (center, size) boxes in
    cover-local space: z up from the ROOF'S TOP SURFACE, where Patina orders
    it, and x along the boom toward the transmitter. The plate 1 mm off the
    roof; the mast from 1 mm inside the plate to `mast`; the boom `ANT_TOP`
    under the mast's top, `ANT_BACK` of it behind the mast; and an element
    about every `ANT_PITCH` along it, the first and last 5 cm in from its
    ends, tapering from `ANT_LONG` at the back to `ANT_SHORT` at the front."""
    L, H = float(boom), float(mast)
    z0 = 0.001 + ANT_PLATE_T
    parts = [((0.0, 0.0, 0.001 + ANT_PLATE_T / 2.0), (ANT_PLATE, ANT_PLATE, ANT_PLATE_T)),
             ((0.0, 0.0, (z0 - 0.001 + H) / 2.0), (ANT_MAST, ANT_MAST, H - z0 + 0.001))]
    zb = H - ANT_TOP
    x0, x1 = -ANT_BACK * L, (1.0 - ANT_BACK) * L
    parts.append((((x0 + x1) / 2.0, 0.0, zb), (L, ANT_BOOM, ANT_BOOM)))
    n = max(3, int(round(L / ANT_PITCH)))
    for k in range(n):
        f = k / (n - 1.0)
        parts.append(((x0 + 0.05 + f * (L - 0.10), 0.0, zb),
                      (ANT_ELEMENT, ANT_LONG + f * (ANT_SHORT - ANT_LONG), ANT_ELEMENT)))
    return parts


#: AN EMPTY'S SATELLITE DISH (1.74.0), the comps' "odd early satellite dish":
#: an 18-inch DSS dish (1994 on), an oval 46 x 50 cm, on a pole on a roof
#: plate. Its bowl looks along local +x -- Patina gives the satellite's
#: bearing as the tangent -- tilted up `DISH_TILT`, Philadelphia's elevation
#: to the DSS satellites at 101 W; a feed arm runs out from below the bowl's
#: centre to the LNB. The head -- bowl, arm, LNB -- is built level, looking
#: along +x, and the recipe tilts it about the bowl's centre.
DISH_R = (0.045, 0.23, 0.25)      # the bowl's half-depth, half-width, half-height
DISH_TILT = 41.0
DISH_POLE = 0.045
DISH_REACH = 0.12                 # the bowl's centre in front of the pole
DISH_FOCUS = 0.30                 # the LNB, along the bowl's axis


def dish_parts(centre_h: float):
    """A satellite dish's parts (1.74.0), in cover-local space with z up from
    the roof's top surface. Returns ``(mount, head, bowl_center)``: `mount`,
    the plate, pole and bracket, standing level, as (center, size) boxes;
    `head`, the feed arm and LNB, as boxes in the head's own frame -- centred
    on the bowl, looking along +x -- for the recipe to tilt by `DISH_TILT`
    about `bowl_center` together with the bowl, an ellipsoid of `DISH_R`."""
    Hc = float(centre_h)
    z0 = 0.001 + ANT_PLATE_T
    top = Hc - 0.12
    mount = [((0.0, 0.0, 0.001 + ANT_PLATE_T / 2.0), (0.30, 0.30, ANT_PLATE_T)),
             ((0.0, 0.0, (z0 - 0.001 + top) / 2.0), (DISH_POLE, DISH_POLE, top - z0 + 0.001)),
             ((DISH_REACH / 2.0, 0.0, top), (DISH_REACH + 0.002, 0.03, 0.03))]
    head = [(((0.02 + DISH_FOCUS) / 2.0, 0.0, -0.17), (DISH_FOCUS - 0.02, 0.02, 0.02)),
            ((DISH_FOCUS, 0.0, -0.11), (0.07, 0.06, 0.11))]
    return mount, head, (DISH_REACH, 0.0, Hc)


def frame_strips('''

DOC_OLD = '''* ``security_door`` — an Empty's black iron security door in its doorway's
  reveal (1.72.0; ``core.dressing.security_door_parts``).
'''
DOC_NEW = '''* ``security_door`` — an Empty's black iron security door in its doorway's
  reveal (1.72.0; ``core.dressing.security_door_parts``).
* ``tv_antenna``   — an Empty's rooftop TV antenna: a mast, and a boom toward
  the transmitter with its elements (1.74.0; ``size2`` = [boom, mast];
  ``core.dressing.antenna_parts``).
* ``sat_dish``     — an Empty's satellite dish on a roof pole, its bowl tilted
  up toward the satellite (1.74.0; ``size2`` = [width, the bowl's height];
  ``core.dressing.dish_parts``).
'''

IMPORT_OLD = '''from ..core.dressing import (ac_parts, bar_parts, downspout_parts, frame_strips,
                             gutter_parts, lintel_parts, security_door_parts,
                             sill_parts, strip_size, uv_offset)
'''
IMPORT_NEW = '''from ..core.dressing import (DISH_R, DISH_TILT, ac_parts, antenna_parts, bar_parts,
                             dish_parts, downspout_parts, frame_strips,
                             gutter_parts, lintel_parts, security_door_parts,
                             sill_parts, strip_size, uv_offset)
'''

BRANCH_OLD = '''        for center, size in parts:
            geometry.add_box(bm, center, size)
    else:
'''
BRANCH_NEW = '''        for center, size in parts:
            geometry.add_box(bm, center, size)
    elif cover == "tv_antenna":
        # an Empty's rooftop TV antenna (1.74.0); `size2` is [boom, mast]
        boom, mast = (order.get("size2") or [2.0, 2.8])[:2]
        for center, size in antenna_parts(boom, mast):
            geometry.add_box(bm, center, size)
    elif cover == "sat_dish":
        # and its satellite dish (1.74.0); `size2` is [width, the bowl's
        # height above the roof]. The head is built level and tilted up to
        # the satellite about the bowl's centre.
        import math

        import bmesh
        from mathutils import Matrix, Vector
        _w, centre_h = (order.get("size2") or [0.5, 1.2])[:2]
        mount, head, bc = dish_parts(centre_h)
        for center, size in mount:
            geometry.add_box(bm, center, size)
        verts = list(geometry.add_ellipsoid(bm, bc, DISH_R, u_seg=12, v_seg=6))
        for (hx, hy, hz), size in head:
            verts += list(geometry.add_box(bm, (bc[0] + hx, bc[1] + hy, bc[2] + hz), size))
        bmesh.ops.rotate(bm, verts=verts, cent=Vector(bc),
                         matrix=Matrix.Rotation(math.radians(-DISH_TILT), 3, "Y"))
    else:
'''


def main():
    assert (ZOO / "VERSION").read_text(encoding="utf-8").strip() == "1.73.0"
    _edit(ZOO / "zoo_keeper" / "core" / "dressing.py", [(METAL_OLD, METAL_NEW), (PARTS_OLD, PARTS_NEW)])
    _edit(ZOO / "zoo_keeper" / "recipes" / "dress_cover.py",
          [(DOC_OLD, DOC_NEW), (IMPORT_OLD, IMPORT_NEW), (BRANCH_OLD, BRANCH_NEW)])
    shutil.copyfile(SRC / "test_roof_fixtures.py", ZOO / "tests" / "test_roof_fixtures.py")
    ch = ZOO / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    ch.write_text((SRC / "CHANGELOG_1.74.0.md").read_text(encoding="utf-8").rstrip("\n") + "\n\n" + s,
                  encoding="utf-8", newline="\n")
    (ZOO / "VERSION").write_text("1.74.0", encoding="utf-8", newline="\n")
    print("applied Zoo 1.74.0")


if __name__ == "__main__":
    main()
