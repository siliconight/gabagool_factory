"""Zoo 1.69.0: an Empty's window fixtures -- a window air conditioner and bars
-- as geometry, and the pane stops painting the bars.

The walker's window photographs: "window air conditioners in nearly every
photograph", and bars proud of the frame on bolted straps. Patina (>= 0.26.0)
orders both from the slot Deli Counter (>= 0.181.0) marks. See
`zoo_window_fixtures/CHANGELOG_1.69.0.md`.

Anchored edits (every anchor once; refuses on a miss):
  zoo_keeper/core/dressing.py        AC_*, BAR*, STRAP*, IRON_*; ac_unit is
                                     painted metal; ac_parts, bar_parts
  zoo_keeper/recipes/dress_cover.py  builds them from the part lists
  zoo_keeper/core/window_panes.py    a barred pane paints only its room
Copies the test; CHANGELOG and VERSION.

    python patch_zoo_window_fixtures.py
"""
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve().parent
ZOO = HERE.parent / "zoo"
SRC = HERE / "zoo_window_fixtures"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


# --- core/dressing.py -------------------------------------------------------

METAL_OLD = '''METAL_COVERS = ("gutter_run", "downspout")
METAL_KIND = "metal_painted"
#: White aluminium -- the flat colour, used only with no skin library.
METAL_COLOR = (0.86, 0.86, 0.83)
'''
METAL_NEW = '''METAL_COVERS = ("gutter_run", "downspout", "ac_unit")
METAL_KIND = "metal_painted"
#: White aluminium. CORRECTED (1.69.0): this said "the flat colour, used only
#: with no skin library". It is also the TINT: `materials.make_material` tints
#: a tintable pack -- `metal_painted_neutral` is achromatic on purpose -- and
#: names the result for it, which is the `_dbdbd4` on every shipped gutter's
#: `M_Skin_metal_painted_delco_1997_dbdbd4`.
METAL_COLOR = (0.86, 0.86, 0.83)

#: AN EMPTY'S WINDOW AIR CONDITIONER (1.69.0). The walker's window
#: photographs: "window air conditioners in nearly every photograph", a white
#: or beige box in the lower sash, standing out of the wall. A 1990s
#: 6,000 BTU unit, 52 x 36 cm, standing 30 cm out of the wall and reaching back
#: through the reveal to the pane -- `_arch` sets the pane at the wall's centre
#: plane, 13 cm behind the face of a 0.3 m wall. Lifted 2 mm off the sill so
#: its underside is never coplanar with the reveal. White painted metal: the
#: gutters' material, so on a side that has gutters it merges into their mesh
#: at no extra draw. Sized from its opening and these, not from `_COVER`.
AC_W, AC_H = 0.52, 0.36
AC_OUT, AC_BACK = 0.30, 0.13
AC_LIFT = 0.002
#: AN EMPTY'S WINDOW BARS (1.69.0), "proud of the frame on bolted straps":
#: 18 mm square uprights about 12 cm apart standing 4 cm off the wall and
#: running 5 cm past the head and the sill; two flat straps behind them,
#: reaching 7 cm past each jamb onto the brick and bolted there on standoffs.
#: Every part stands 1 mm or more off the wall face, never in it or flush.
BAR = 0.018
BAR_PITCH = 0.12
BAR_PROUD = 0.04
BAR_REACH = 0.05
STRAP_W, STRAP_T = 0.04, 0.008
STRAP_REACH = 0.07
STRAP_IN = 0.14
#: Black painted iron: the same painted metal in a second colour, so ONE more
#: surface on a side that has bars, however many windows they cover.
IRON_COVERS = ("window_bars",)
IRON_COLOR = (0.07, 0.07, 0.07)
'''

PLAN_OLD = '''    if order.get("cover") in METAL_COVERS and METAL_KIND in genome["materials"]["options"]:
        material, color = METAL_KIND, [round(float(c), 4) for c in METAL_COLOR]
'''
PLAN_NEW = '''    if order.get("cover") in METAL_COVERS and METAL_KIND in genome["materials"]["options"]:
        material, color = METAL_KIND, [round(float(c), 4) for c in METAL_COLOR]
    # and an Empty's window bars are black painted iron (1.69.0)
    elif order.get("cover") in IRON_COVERS and METAL_KIND in genome["materials"]["options"]:
        material, color = METAL_KIND, [round(float(c), 4) for c in IRON_COLOR]
'''

PARTS_ANCHOR = '''    return [pipe, boot] + straps
'''
PARTS_NEW = '''    return [pipe, boot] + straps


def ac_parts(opening_w: float):
    """A window air conditioner's parts (1.69.0), as (center, size) boxes in
    cover-local space: x along the wall, y out from the wall FACE, z up from
    the SILL, where Patina orders the unit.

    The cabinet, from the pane (``-AC_BACK``) to ``AC_OUT`` out of the wall;
    five fins across its back -- the side the street sees, the condenser
    grille; louvres down each flank, outside the wall; the accordion panels
    that close the sash out to the jambs, at the window plane, each with three
    pleats; and two L brackets under the overhang, their legs flat on the wall
    below the sill. Touching parts overlap by a millimetre rather than sharing
    a face. A narrow opening takes a narrower unit, 20 cm short of it.
    """
    ow = float(opening_w)
    w = min(AC_W, max(0.30, ow - 0.20))
    h = AC_H
    y0, y1 = -AC_BACK, AC_OUT
    z0 = AC_LIFT
    parts = [((0.0, (y0 + y1) / 2.0, z0 + h / 2.0), (w, y1 - y0, h))]       # cabinet
    for k in range(5):                                                     # grille fins
        parts.append(((0.0, y1 + 0.004, z0 + h * (0.2 + 0.15 * k)), (w - 0.08, 0.01, 0.02)))
    for sx in (-1.0, 1.0):                                                 # flank louvres
        for k in range(3):
            parts.append(((sx * (w / 2.0 + 0.003), y1 * 0.55, z0 + h * (0.3 + 0.2 * k)),
                          (0.008, y1 * 0.6, 0.025)))
    side = ow / 2.0 - w / 2.0 - 0.01
    if side > 0.02:                                                        # accordion panels
        for sx in (-1.0, 1.0):
            cx = sx * (w / 2.0 + side / 2.0)
            parts.append(((cx, y0 + 0.01, z0 + h / 2.0), (side, 0.012, h * 0.95)))
            for j in (-1, 0, 1):
                parts.append(((cx + j * side / 4.0, y0 + 0.021, z0 + h / 2.0),
                              (0.008, 0.012, h * 0.95)))
    arm = y1 - 0.04                                                        # brackets
    for sx in (-1.0, 1.0):
        x = sx * (w / 2.0 - 0.06)
        parts.append(((x, 0.001 + arm / 2.0, -0.013), (0.025, arm, 0.024)))
        parts.append(((x, 0.013, -0.15), (0.025, 0.024, 0.28)))
    return parts


def bar_parts(opening_w: float, opening_h: float):
    """A barred window's parts (1.69.0), in the same cover-local space with z
    about the opening's centre, where Patina orders them: square uprights
    across the opening running past its head and sill, two flat straps behind
    them reaching past the jambs onto the brick, and a bolted standoff at each
    strap end. Everything stands at least 1 mm off the wall face."""
    ow, oh = float(opening_w), float(opening_h)
    n = max(2, int(round(ow / BAR_PITCH)) - 1)
    pitch = ow / (n + 1)
    parts = [((-ow / 2.0 + j * pitch, BAR_PROUD, 0.0), (BAR, BAR, oh + 2 * BAR_REACH))
             for j in range(1, n + 1)]
    back = BAR_PROUD - BAR / 2.0                    # the uprights' back face
    for z in (-oh / 2.0 + STRAP_IN, oh / 2.0 - STRAP_IN):
        parts.append(((0.0, back - STRAP_T / 2.0 + 0.001, z),
                      (ow + 2 * STRAP_REACH, STRAP_T, STRAP_W)))
        for sx in (-1.0, 1.0):
            parts.append(((sx * (ow / 2.0 + STRAP_REACH - 0.02), 0.001 + (back - 0.001) / 2.0, z),
                          (0.03, back - 0.001, 0.03)))
    return parts
'''

# --- recipes/dress_cover.py -------------------------------------------------

IMPORT_OLD = '''from ..core.dressing import (downspout_parts, frame_strips, gutter_parts,
                             strip_size, uv_offset)
'''
IMPORT_NEW = '''from ..core.dressing import (ac_parts, bar_parts, downspout_parts, frame_strips,
                             gutter_parts, strip_size, uv_offset)
'''

BRANCH_OLD = '''    elif cover == "downspout":
        # the leader, its straps and its boot (1.67.0)
        w, _d, h = strip_size(cover, order.get("size", 0.6), order.get("size2"))
        for center, size in downspout_parts(h, w):
            geometry.add_box(bm, center, size)
'''
BRANCH_NEW = '''    elif cover == "downspout":
        # the leader, its straps and its boot (1.67.0)
        w, _d, h = strip_size(cover, order.get("size", 0.6), order.get("size2"))
        for center, size in downspout_parts(h, w):
            geometry.add_box(bm, center, size)
    elif cover in ("ac_unit", "window_bars"):
        # an Empty's window fixtures (1.69.0), sized from the opening Patina
        # passes as `size2` -- an air conditioner on the sill, or bars over it
        ow, oh = (order.get("size2") or [0.95, 1.6])[:2]
        parts = ac_parts(ow) if cover == "ac_unit" else bar_parts(ow, oh)
        for center, size in parts:
            geometry.add_box(bm, center, size)
'''

DOC_OLD = '''* ``frame``        — four thin strips around a doorway/window opening
  (``size2`` = the exact opening rect from DC's ``fit.openings``;
  ``frame_width`` from the order).
'''
DOC_NEW = '''* ``frame``        — four thin strips around a doorway/window opening
  (``size2`` = the exact opening rect from DC's ``fit.openings``;
  ``frame_width`` from the order).
* ``ac_unit``      — an Empty's window air conditioner standing on the sill
  (1.69.0; ``size2`` = the opening; parts from ``core.dressing.ac_parts``).
* ``window_bars``  — an Empty's barred window: uprights on bolted straps
  (1.69.0; ``size2`` = the opening; ``core.dressing.bar_parts``).
'''

# --- core/window_panes.py ---------------------------------------------------

BAR_RGB_OLD = '''MUNTIN_RGB = (150, 144, 132)
BAR_RGB = (22, 22, 22)
'''
BAR_RGB_NEW = '''MUNTIN_RGB = (150, 144, 132)
'''

BARS_FN_OLD = '''def _bars(c, e, x0, y0, x1, y1):
    for j in range(1, 6):
        x = x0 + (x1 - x0) * j // 6
        c.rect(x - 1, y0, x + 1, y1, BAR_RGB)
        e.rect(x - 1, y0, x + 1, y1, (0, 0, 0))
    for y in (y0 + 4, y1 - 5):
        c.rect(x0, y, x1, y + 2, BAR_RGB)
        e.rect(x0, y, x1, y + 2, (0, 0, 0))


'''
BARS_FN_NEW = ''

BARS_CALL_OLD = '''    _sash(c, e, gx0, gy0, gx1, gy1)
    if state.endswith("_bars"):
        _bars(c, e, gx0, gy0, gx1, gy1)
    if state == "dark_fan":
'''
BARS_CALL_NEW = '''    _sash(c, e, gx0, gy0, gx1, gy1)
    # NO PAINTED BARS (1.69.0). A barred window's bars are geometry now --
    # `dressing.bar_parts`, ordered by Patina (>= 0.26.0) from the slot Deli
    # Counter (>= 0.181.0) marks -- standing 3.5 cm off the wall while this
    # pane sits 13 cm behind it. Painted as well, they drew a second grid that
    # slid against the real one as the eye moved. A barred pane paints its
    # room and nothing else.
    if state == "dark_fan":
'''


def main():
    assert (ZOO / "VERSION").read_text(encoding="utf-8").strip() == "1.68.0"
    _edit(ZOO / "zoo_keeper" / "core" / "dressing.py",
          [(METAL_OLD, METAL_NEW), (PLAN_OLD, PLAN_NEW), (PARTS_ANCHOR, PARTS_NEW)])
    _edit(ZOO / "zoo_keeper" / "recipes" / "dress_cover.py",
          [(IMPORT_OLD, IMPORT_NEW), (BRANCH_OLD, BRANCH_NEW), (DOC_OLD, DOC_NEW)])
    _edit(ZOO / "zoo_keeper" / "core" / "window_panes.py",
          [(BAR_RGB_OLD, BAR_RGB_NEW), (BARS_FN_OLD, BARS_FN_NEW), (BARS_CALL_OLD, BARS_CALL_NEW)])
    shutil.copyfile(SRC / "test_window_fixtures.py", ZOO / "tests" / "test_window_fixtures.py")
    ch = ZOO / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    ch.write_text((SRC / "CHANGELOG_1.69.0.md").read_text(encoding="utf-8").rstrip("\n") + "\n\n" + s,
                  encoding="utf-8", newline="\n")
    (ZOO / "VERSION").write_text("1.69.0", encoding="utf-8", newline="\n")
    print("applied Zoo 1.69.0")


if __name__ == "__main__":
    main()
