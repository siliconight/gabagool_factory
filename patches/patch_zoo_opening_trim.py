"""Zoo 1.71.0: an Empty's stone lintels and sills, from Patina (>= 0.27.0)'s
`lintel` and `window_sill` orders. The walker's South Philly photograph:
"white stone lintels and sills over and under every window". See
`zoo_opening_trim/CHANGELOG_1.71.0.md`.

Anchored edits (every anchor once; refuses on a miss):
  zoo_keeper/core/dressing.py        LINTEL_*, SILL_*, STONE_TRIM_*; plaster
                                     for both; lintel_parts, sill_parts
  zoo_keeper/recipes/dress_cover.py  builds them from the part lists
Copies the test; CHANGELOG and VERSION.

    python patch_zoo_opening_trim.py
"""
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve().parent
ZOO = HERE.parent / "zoo"
SRC = HERE / "zoo_opening_trim"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


CONST_OLD = '''IRON_COVERS = ("window_bars",)
IRON_COLOR = (0.07, 0.07, 0.07)
'''
CONST_NEW = '''IRON_COVERS = ("window_bars",)
IRON_COLOR = (0.07, 0.07, 0.07)

#: AN EMPTY'S STONE LINTELS AND SILLS (1.71.0). The walker's South Philly
#: photograph: "white stone lintels and sills over and under every window".
#: A lintel stands on the opening's HEAD, 20 cm tall, bearing 10 cm into the
#: brick past each jamb and 2.8 cm proud -- behind the bars, whose uprights
#: run up past the head 3.1 cm off the wall. A sill hangs below the SILL
#: line, 7 cm deep, 6 cm proud so it reads as a ledge, 5 cm past each jamb.
#: Both stand 1 mm off the wall face.
LINTEL_H, LINTEL_PROUD, LINTEL_BEAR = 0.20, 0.028, 0.10
SILL_H, SILL_PROUD, SILL_BEAR = 0.07, 0.06, 0.05
#: In `plaster` -- Pixelcoat's `plaster_delco`, cream and matte, the nearest
#: skin to the photograph's white stone that a cover already offers. One more
#: material, so one more surface on a side that has openings. The colour is
#: the flat fallback; the pack is not tintable.
STONE_TRIM_COVERS = ("lintel", "window_sill")
STONE_TRIM_KIND = "plaster"
STONE_TRIM_COLOR = (0.80, 0.76, 0.68)
'''

PLAN_OLD = '''    # and an Empty's window bars are black painted iron (1.69.0)
    elif order.get("cover") in IRON_COVERS and METAL_KIND in genome["materials"]["options"]:
        material, color = METAL_KIND, [round(float(c), 4) for c in IRON_COLOR]
'''
PLAN_NEW = '''    # and an Empty's window bars are black painted iron (1.69.0)
    elif order.get("cover") in IRON_COVERS and METAL_KIND in genome["materials"]["options"]:
        material, color = METAL_KIND, [round(float(c), 4) for c in IRON_COLOR]
    # and its lintels and sills are stone-coloured plaster (1.71.0)
    elif order.get("cover") in STONE_TRIM_COVERS and STONE_TRIM_KIND in genome["materials"]["options"]:
        material, color = STONE_TRIM_KIND, [round(float(c), 4) for c in STONE_TRIM_COLOR]
'''

PARTS_OLD = '''        for sx in (-1.0, 1.0):
            parts.append(((sx * (ow / 2.0 + STRAP_REACH - 0.02), 0.001 + (back - 0.001) / 2.0, z),
                          (0.03, back - 0.001, 0.03)))
    return parts
'''
PARTS_NEW = '''        for sx in (-1.0, 1.0):
            parts.append(((sx * (ow / 2.0 + STRAP_REACH - 0.02), 0.001 + (back - 0.001) / 2.0, z),
                          (0.03, back - 0.001, 0.03)))
    return parts


def lintel_parts(opening_w: float):
    """A stone lintel (1.71.0): one block standing on the opening's head --
    z from 0 up, where Patina orders it -- bearing past both jambs, 1 mm off
    the wall face."""
    w = float(opening_w) + 2.0 * LINTEL_BEAR
    return [((0.0, 0.001 + LINTEL_PROUD / 2.0, LINTEL_H / 2.0), (w, LINTEL_PROUD, LINTEL_H))]


def sill_parts(opening_w: float):
    """A stone sill (1.71.0): one block hung below the sill line -- z from 0
    down, where Patina orders it -- projecting as a ledge, 1 mm off the wall
    face."""
    w = float(opening_w) + 2.0 * SILL_BEAR
    return [((0.0, 0.001 + SILL_PROUD / 2.0, -SILL_H / 2.0), (w, SILL_PROUD, SILL_H))]
'''

IMPORT_OLD = '''from ..core.dressing import (ac_parts, bar_parts, downspout_parts, frame_strips,
                             gutter_parts, strip_size, uv_offset)
'''
IMPORT_NEW = '''from ..core.dressing import (ac_parts, bar_parts, downspout_parts, frame_strips,
                             gutter_parts, lintel_parts, sill_parts, strip_size,
                             uv_offset)
'''

BRANCH_OLD = '''    elif cover in ("ac_unit", "window_bars"):
        # an Empty's window fixtures (1.69.0), sized from the opening Patina
        # passes as `size2` -- an air conditioner on the sill, or bars over it
        ow, oh = (order.get("size2") or [0.95, 1.6])[:2]
        parts = ac_parts(ow) if cover == "ac_unit" else bar_parts(ow, oh)
'''
BRANCH_NEW = '''    elif cover in ("ac_unit", "window_bars", "lintel", "window_sill"):
        # an Empty's window fixtures (1.69.0) and its stone lintels and sills
        # (1.71.0), each sized from the opening Patina passes as `size2`
        ow, oh = (order.get("size2") or [0.95, 1.6])[:2]
        if cover == "ac_unit":
            parts = ac_parts(ow)
        elif cover == "window_bars":
            parts = bar_parts(ow, oh)
        elif cover == "lintel":
            parts = lintel_parts(ow)
        else:
            parts = sill_parts(ow)
'''

DOC_OLD = '''* ``window_bars``  — an Empty's barred window: uprights on bolted straps
  (1.69.0; ``size2`` = the opening; ``core.dressing.bar_parts``).
'''
DOC_NEW = '''* ``window_bars``  — an Empty's barred window: uprights on bolted straps
  (1.69.0; ``size2`` = the opening; ``core.dressing.bar_parts``).
* ``lintel``       — an Empty's stone lintel standing on an opening's head
  (1.71.0; ``core.dressing.lintel_parts``).
* ``window_sill``  — an Empty's stone sill hung below a window's sill line
  (1.71.0; ``core.dressing.sill_parts``).
'''


def main():
    assert (ZOO / "VERSION").read_text(encoding="utf-8").strip() == "1.70.0"
    _edit(ZOO / "zoo_keeper" / "core" / "dressing.py",
          [(CONST_OLD, CONST_NEW), (PLAN_OLD, PLAN_NEW), (PARTS_OLD, PARTS_NEW)])
    _edit(ZOO / "zoo_keeper" / "recipes" / "dress_cover.py",
          [(IMPORT_OLD, IMPORT_NEW), (BRANCH_OLD, BRANCH_NEW), (DOC_OLD, DOC_NEW)])
    shutil.copyfile(SRC / "test_opening_trim.py", ZOO / "tests" / "test_opening_trim.py")
    ch = ZOO / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    ch.write_text((SRC / "CHANGELOG_1.71.0.md").read_text(encoding="utf-8").rstrip("\n") + "\n\n" + s,
                  encoding="utf-8", newline="\n")
    (ZOO / "VERSION").write_text("1.71.0", encoding="utf-8", newline="\n")
    print("applied Zoo 1.71.0")


if __name__ == "__main__":
    main()
