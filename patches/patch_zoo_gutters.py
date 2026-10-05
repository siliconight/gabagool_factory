"""Zoo 1.67.0: a gutter that reads as a gutter, a downspout, painted metal.

The walker, 2026-10-04: "also we need rain gutters". Zoo built every
`gutter_run` as one solid box, 10 cm proud by 14 cm tall, centred ON the wall
face -- half of it inside the wall -- in the concrete every cover wears; from
the street, a bar. Patina 0.25.0 also orders `downspout`s, which nothing
built. See `zoo_gutters/CHANGELOG_1.67.0.md`.

Anchored edits (every anchor once; refuses on a miss):
  zoo_keeper/core/dressing.py                 `downspout` size, the metal covers,
                                              `gutter_parts`, `downspout_parts`
  zoo_keeper/recipes/dress_cover.py           builds them from the part lists
  zoo_keeper/genome/species/dress_cover.json  offers `metal_painted`
Copies the test; CHANGELOG and VERSION.

    python patch_zoo_gutters.py
"""
import json
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve().parent
ZOO = HERE.parent / "zoo"
SRC = HERE / "zoo_gutters"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


COVER_OLD = '''    "gutter_run":  {"proud": 0.10, "cross": 0.14, "span": 2.0},
'''
COVER_NEW = '''    "gutter_run":  {"proud": 0.10, "cross": 0.14, "span": 2.0},
    # 1.67.0 (Patina >= 0.25.0): the pipe from the gutter to the ground. A
    # 3-inch leader on straps; `span` is a placeholder -- `size` is the length.
    "downspout":   {"proud": 0.07, "cross": 0.076, "span": 2.5},
'''

CONSTS_OLD = '''    "frame":       {"proud": 0.05, "cross": 0.12, "span": 1.0},
}
'''
CONSTS_NEW = '''    "frame":       {"proud": 0.05, "cross": 0.12, "span": 1.0},
}

#: COVERS THAT ARE PAINTED METAL (1.67.0), whatever trim the style names: a
#: gutter and its downspout are aluminium on a 1990s rowhouse, and in the
#: concrete every other cover wears they read as one more ledge.
METAL_COVERS = ("gutter_run", "downspout")
METAL_KIND = "metal_painted"
#: White aluminium -- the flat colour, used only with no skin library.
METAL_COLOR = (0.86, 0.86, 0.83)

#: The gutter's sheet, drawn thicker than aluminium so it holds at street
#: distance; its front stands a little lower than its back, as a hung gutter's
#: does; and a rolled bead runs along the top of the front.
GUTTER_SHEET = 0.008
GUTTER_FRONT = 0.85
#: The downspout: a 3 x 2 inch leader held off the wall on straps, ending in a
#: cast boot at the ground, where a Philadelphia rowhouse's leader goes into
#: the sewer. A boot also means no elbow kicking out across the sidewalk:
#: non-collision geometry in walkable space is what panel fields were removed
#: for.
DOWNSPOUT_STANDOFF = 0.02
DOWNSPOUT_DEPTH = 0.05
BOOT_H, BOOT_W, BOOT_D = 0.35, 0.12, 0.10
'''

SIZE_OLD = '''    if cover == "conduit_run":
'''
SIZE_NEW = '''    if cover in ("conduit_run", "downspout"):
'''

PLAN_OLD = '''    material = style.get("material") or genome["materials"]["default"]
    if material not in genome["materials"]["options"]:
        material = genome["materials"]["default"]
'''
PLAN_NEW = '''    material = style.get("material") or genome["materials"]["default"]
    if material not in genome["materials"]["options"]:
        material = genome["materials"]["default"]
    color = [round(float(c), 4) for c in style.get("color", [0.6, 0.6, 0.6])]
    # a gutter and its downspout are painted metal (1.67.0) -- when the
    # genome offers it, so a genome that does not is never handed a kind it
    # cannot build
    if order.get("cover") in METAL_COVERS and METAL_KIND in genome["materials"]["options"]:
        material, color = METAL_KIND, [round(float(c), 4) for c in METAL_COLOR]
'''

COLOR_OLD = '''        "color": [round(float(c), 4) for c in style.get("color", [0.6, 0.6, 0.6])],
'''
COLOR_NEW = '''        "color": color,
'''

PARTS_ANCHOR = '''def frame_strips(w: float, h: float, frame_w: float, proud: float):
'''
PARTS_NEW = '''def gutter_parts(span: float, proud: float, cross: float):
    """A hung gutter's parts, as (center, size) boxes in cover-local space:
    x along the wall, y out from the wall FACE (y = 0 is the face, which is
    where Patina's ``pos`` sits), z up about the gutter's centre line.

    AN OPEN TROUGH, NOT A BAR (1.67.0). The box this replaces was centred on
    the face, so half of it stood inside the wall, and it had no mouth. Here:
    a back on the wall, a floor, a front a little lower than the back, and a
    rolled bead along the front's top -- with nothing across the mouth, so a
    street-level eye sees a lip and a shadow. Every part runs the full span,
    so sections butt at module seams as real gutter sections join.
    """
    t = GUTTER_SHEET
    front = cross * GUTTER_FRONT
    zb = -cross / 2.0
    return [
        ((0.0, t / 2.0, 0.0), (span, t, cross)),                          # back
        ((0.0, proud / 2.0, zb + t / 2.0), (span, proud, t)),             # floor
        ((0.0, proud - t / 2.0, zb + front / 2.0), (span, t, front)),     # front
        ((0.0, proud - 0.007, zb + front - 0.006), (span, 0.014, 0.012)),  # bead
    ]


def downspout_parts(length: float, cross: float):
    """A downspout's parts, in the same cover-local space (y out from the wall
    face, z about the run's middle): the leader on its standoff, a cast boot
    at the ground, two straps. Bottom at ``-length / 2`` -- the ground -- and
    top at ``+length / 2``, the gutter's underside (Patina 0.25.0 measures
    the run between the two).
    """
    L = float(length)
    zb = -L / 2.0
    y0 = DOWNSPOUT_STANDOFF
    pipe_z0 = zb + BOOT_H - 0.02                      # the leader enters the boot
    pipe = ((0.0, y0 + DOWNSPOUT_DEPTH / 2.0, (pipe_z0 + L / 2.0) / 2.0),
            (cross, DOWNSPOUT_DEPTH, L / 2.0 - pipe_z0))
    boot = ((0.0, BOOT_D / 2.0, zb + BOOT_H / 2.0), (BOOT_W, BOOT_D, BOOT_H))
    strap_d = y0 + DOWNSPOUT_DEPTH + 0.004
    straps = [((0.0, strap_d / 2.0, zb + L * f), (cross + 0.012, strap_d, 0.025))
              for f in (1.0 / 3.0, 2.0 / 3.0)]
    return [pipe, boot] + straps


def frame_strips(w: float, h: float, frame_w: float, proud: float):
'''

RECIPE_IMPORT_OLD = '''from ..core.dressing import frame_strips, strip_size, uv_offset
'''
RECIPE_IMPORT_NEW = '''from ..core.dressing import (downspout_parts, frame_strips, gutter_parts,
                             strip_size, uv_offset)
'''

RECIPE_OLD = '''    else:
        w, d, h = strip_size(cover, order.get("size", 0.6),
                             order.get("size2"))
        geometry.add_box(bm, (0.0, 0.0, 0.0), (w, d, h))
'''
RECIPE_NEW = '''    elif cover == "gutter_run":
        # an open trough off the wall face (1.67.0), not a bar through it
        w, d, h = strip_size(cover, order.get("size", 0.6), order.get("size2"))
        for center, size in gutter_parts(w, d, h):
            geometry.add_box(bm, center, size)
    elif cover == "downspout":
        # the leader, its straps and its boot (1.67.0)
        w, _d, h = strip_size(cover, order.get("size", 0.6), order.get("size2"))
        for center, size in downspout_parts(h, w):
            geometry.add_box(bm, center, size)
    else:
        w, d, h = strip_size(cover, order.get("size", 0.6),
                             order.get("size2"))
        geometry.add_box(bm, (0.0, 0.0, 0.0), (w, d, h))
'''


def main():
    assert (ZOO / "VERSION").read_text(encoding="utf-8").strip() == "1.66.0"
    core = ZOO / "zoo_keeper" / "core" / "dressing.py"
    _edit(core, [(COVER_OLD, COVER_NEW), (CONSTS_OLD, CONSTS_NEW), (SIZE_OLD, SIZE_NEW),
                 (PLAN_OLD, PLAN_NEW), (COLOR_OLD, COLOR_NEW), (PARTS_ANCHOR, PARTS_NEW)])
    _edit(ZOO / "zoo_keeper" / "recipes" / "dress_cover.py",
          [(RECIPE_IMPORT_OLD, RECIPE_IMPORT_NEW), (RECIPE_OLD, RECIPE_NEW)])
    # THE METAL SPLIT, FOR THIS SPECIES (`tests/test_material_options_closed`):
    # a species offering a split kind offers no raw `metal`, and no style
    # names it -- raw `metal` resolves the theme's own pack (delco_1997's is
    # rusted street metal) and ignores the genome colour. Gutters and
    # downspouts are painted aluminium; the two styles whose every cover was
    # raw `metal` (center_city, industrial_flats) move to `metal_painted`,
    # since a metal facade trim is painted flashing. The file round-trips
    # through json.dumps(indent=1) byte for byte, so the edit is structural.
    g = ZOO / "zoo_keeper" / "genome" / "species" / "dress_cover.json"
    raw = g.read_text(encoding="utf-8")
    d = json.loads(raw)
    assert json.dumps(d, indent=1, ensure_ascii=False) + "\n" == raw, "dress_cover.json does not round-trip"
    assert d["materials"]["options"] == ["concrete", "plaster", "metal"], d["materials"]["options"]
    d["materials"]["options"] = ["concrete", "plaster", "metal_painted"]
    moved = []
    for name, style in d["styles"].items():
        if style.get("material") == "metal":
            style["material"] = "metal_painted"
            moved.append(name)
    assert sorted(moved) == ["center_city", "industrial_flats"], moved
    g.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    t = ZOO / "tests" / "test_material_options_closed.py"
    _edit(t, [('''           "dumpster")
''', '''           "dumpster",
           # a cover's metal is painted flashing, and a gutter and its
           # downspout are painted aluminium (1.67.0): `metal_painted` is
           # what METAL_COVERS ask for, and the two styles whose every cover
           # was raw `metal` moved with them
           "dress_cover")
''')])
    shutil.copyfile(SRC / "test_gutters.py", ZOO / "tests" / "test_gutters.py")
    ch = ZOO / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    ch.write_text((SRC / "CHANGELOG_1.67.0.md").read_text(encoding="utf-8").rstrip("\n") + "\n\n" + s,
                  encoding="utf-8", newline="\n")
    (ZOO / "VERSION").write_text("1.67.0", encoding="utf-8", newline="\n")
    print("applied Zoo 1.67.0")


if __name__ == "__main__":
    main()
