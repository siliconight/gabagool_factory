"""Zoo 1.89.0: the payphone lit (roadmap 210) -- the header's face and a hood
lamp's diffuser on a second, backlit atlas, and the hood lamp's marker.

Cold run 9212 stood Zoo 1.88.0's booth at a bus stop, and at midnight it read
as a silhouette: no light reached the card, the keys or the stickers. The
walker, 2026-10-09, on the proposal (a backlit header and a hood lamp, one
more draw a payphone): "yes light it".

- `core/payphone_forms.py`: the diffuser hangs under the roof just behind the
  header (a pedestal's roof edge), and `LuxEmit_payphone_hood` LAMP_EMIT under
  it, in free air; the header's face and the diffuser's go on a `glow` atlas;
  `plan` returns the lamp's marker -- name, point, payload (`lux_type`,
  `lux_drop`, its height above the ground).
- `recipes/payphone.py`: the ATM's two `build_art` calls, the lit one with
  `lit=(GLOW_EMISSION, GLOW_ALBEDO)` so its material is `_Face`; the marker as
  an attachment with its payload in `marker_props`.
- `bpylayer/markers.py` + `bpylayer/build.py`: `add_marker(..., props=)` sets
  custom properties, which the glTF export writes as the node's extras -- the
  path `LuxFixtureSpawner.marker_payload` reads. Both call sites pass a
  recipe's `marker_props`; a recipe that returns none is unchanged.
- The genome names the second part; `tests/test_payphone.py` holds the two
  atlases, the lamp in free air and its payload, and the built GLB.

`payphone_forms.py` and `tests/test_payphone.py` are CRLF in the working
tree and LF in git's index (1.88.0's patch copied them from CRLF sources);
this writes both LF, the index's form. Every other file keeps its endings.

Anchored edits (each anchor matches once; refuses on a miss; nothing is
written until every anchor and every replaced file's hash matched).
CHANGELOG and VERSION from `zoo_payphone_light/CHANGELOG_1.89.0.md`.

    python patch_zoo_payphone_light.py
    ZOO_ROOT=<copy> python patch_zoo_payphone_light.py [--draft]

`--draft` lets a changelog still carrying RESULT_ placeholders through, and
only against a ZOO_ROOT copy. `--suite-pending` lets exactly one through,
RESULT_SUITE, into the repo: the suite's count is only true of the repo's own
checkout (a copy has no `deli_counter/build` or `pixelcoat` beside it, and 27
more tests skip), so it is run after this writes and filled in by hand before
the commit, which a grep for RESULT_ guards.
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ZOO = pathlib.Path(os.environ.get("ZOO_ROOT") or HERE.parent / "zoo")
SRC = HERE / "zoo_payphone_light"
DRAFT = "--draft" in sys.argv
SUITE_PENDING = "--suite-pending" in sys.argv

CHANGELOG_HEAD = ("## [1.88.0] - the payphone, redrawn: a coin phone you can read, on its armoured cord, "
                  "in three enclosures\n")

#: Files this patch reads whole before editing, as the device had them.
SHA = {
    "zoo_keeper/core/payphone_forms.py": "5735a1f3b9351c61",
    "zoo_keeper/recipes/payphone.py": "6e3ea5636fce5d6b",
    "zoo_keeper/bpylayer/markers.py": "ea50eeb5e9965370",
    "zoo_keeper/genome/species/payphone.json": "f523e75bf6381d6c",
    "tests/test_payphone.py": "41012b3e75958d6e",
}
#: Written LF whatever the working tree held (see the docstring).
TO_LF = {"zoo_keeper/core/payphone_forms.py", "tests/test_payphone.py"}

FORMS_DOC_OLD = """ONE ATLAS, ONE MATERIAL, ONE DRAW. Every prim names a tile; the paint, the
steel, the black plastic and every word are pixels in one image
(`recipes/_card_atlas.build_art`). 1.87.0's payphone was three materials and
three draws of boxes.
"""
FORMS_DOC_NEW = """TWO ATLASES, TWO DRAWS (1.89.0; 1.88.0 drew one). Every prim names a tile;
the paint, the steel, the black plastic and every word are pixels in one image
(`recipes/_card_atlas.build_art`). 1.87.0's payphone was three materials and
three draws of boxes. The second atlas is the LIT one -- the header's face and
the hood's diffuser, their art their own light as well as paint -- and its
material is named `_Face`, so Lux's power cut takes it: the ATM's topper
(`atm_forms`).

THE HOOD LAMP (1.89.0). Cold run 9212 stood a booth at a bus stop, and at
midnight it was a silhouette: no light reached the card, the keys or the
stickers. A real booth's tube sits in its canopy right behind the header,
backlighting the sign and lighting the instrument below it. So the diffuser
hangs under the roof just behind the header (in a pedestal, which has none,
just behind the roof's front edge), and `LAMP` hangs LAMP_EMIT under its
face, in free air -- a lamp inside closed hardware bakes to nothing (Lux
0.65.0's pole, 0.67.0's bulbs) -- carrying `lux_drop`, its height above the
ground, from which Lux's `payphone_hood` row (Lux >= 0.70.0) solves the
lamp's range and energy. Where it hangs was measured, not chosen: with a lamp
stood live in cold run 9212's package (`docs/findings/payphone_light/`),
behind the header the card takes 0.42 per unit of the lamp's energy and the
back panel's top 5.9, against 0.27 and 11.4 with the lamp mid-hood -- the
hot spot halved and the card lit half again.
"""

EDITS = {
    "zoo_keeper/core/payphone_forms.py": [
        (FORMS_DOC_OLD, FORMS_DOC_NEW),
        ("""BINDER_RING = 0.008       # its rings' radius
""",
         """BINDER_RING = 0.008       # its rings' radius

# --- the hood lamp (1.89.0) ------------------------------------------------------------
LENS_D = 0.070            # the diffuser, front to back
LENS_T = 0.014            # how far it hangs under the roof
LENS_GAP = 0.010          # its front behind the header's back face (a pedestal's roof edge)
LENS_END = 0.030          # each end in from a side panel's inner face
LAMP_EMIT = 0.030         # the lamp's marker under the diffuser's face
#: The marker `LuxFixtureSpawner` stands the lamp at; it reads the type from
#: `lux_type`, and from the name when that is absent.
LAMP = "LuxEmit_payphone_hood"
LAMP_TYPE = "payphone_hood"
#: The lit atlas's tiles, and its emission and diffuse copy (the ATM's,
#: `atm_forms.GLOW_EMISSION` and `GLOW_ALBEDO`).
GLOW_TILES = ("header", "lens")
GLOW_EMISSION = 1.0
GLOW_ALBEDO = 0.6
"""),
        ("""RED = (176, 32, 30)
""",
         """RED = (176, 32, 30)
LENS_WHITE = (232, 240, 234)     # a lit diffuser, with the tube's faint green
LENS_TUBE = (252, 253, 248)      # the tube's line through it
"""),
        ("""    shelf_x0 = max(x for x, _y, _z in path) + CORD_R + SHELF_CLEAR
    return {"form": form, "w": w, "d": d, "h": h, "y_back": y_back, "y_bp0": y_bp0, "y_bp1": y_bp1,
            "y_face": y_face, "top": top, "z_enc0": z_enc0, "inst": (ix0, ix1, y_face, y_bp0 + INSET,
                                                                       inst_z0, inst_z0 + ih),
            "cradle_z": (cradle_z0, cradle_z1), "grip": (gx, gy, grip_z0, grip_z1),
            "ear_z": ear_z, "mouth_z": mouth_z, "cord": path, "shelf_x0": shelf_x0}
""",
         """    shelf_x0 = max(x for x, _y, _z in path) + CORD_R + SHELF_CLEAR
    # the hood lamp (1.89.0): the diffuser just behind the header's back face
    # (a pedestal has no header: just behind the roof's front edge), between
    # the side panels, its top INSET into the roof; the lamp's marker
    # LAMP_EMIT under its face, in free air
    sxi = w / 2.0 - INSET - T_SIDE
    ly0 = -d / 2.0 + 2.0 * INSET + (T_HEADER if form != "pedestal" else 0.0) + LENS_GAP
    lz1 = top - T_ROOF
    lens = (-(sxi - LENS_END), sxi - LENS_END, ly0, ly0 + LENS_D, lz1 - LENS_T, lz1)
    lamp = (0.0, ly0 + LENS_D / 2.0, lz1 - LENS_T - LAMP_EMIT)
    return {"form": form, "w": w, "d": d, "h": h, "y_back": y_back, "y_bp0": y_bp0, "y_bp1": y_bp1,
            "y_face": y_face, "top": top, "z_enc0": z_enc0, "inst": (ix0, ix1, y_face, y_bp0 + INSET,
                                                                       inst_z0, inst_z0 + ih),
            "cradle_z": (cradle_z0, cradle_z1), "grip": (gx, gy, grip_z0, grip_z1),
            "ear_z": ear_z, "mouth_z": mouth_z, "cord": path, "shelf_x0": shelf_x0,
            "lens": lens, "lamp": lamp}
"""),
        ("""    if form != "wall":
        # the post, under the back panel and into it, its back face set in from the panel's
""",
         """    # the hood lamp's diffuser (1.89.0): a lit face under a painted rim, its
    # top INSET into the roof
    lx0, lx1, ly0, ly1, lz0, lz1 = L["lens"]
    prims += _box("Payphone_Lens", {"*": "lens_rim", "under": "lens"},
                  (lx0, ly0, lz0), (lx1, ly1, lz1 + INSET), skip=("top",))
    if form != "wall":
        # the post, under the back panel and into it, its back face set in from the panel's
"""),
        ('''    """``{"prims", "tiles", "collision", "facts"}``: every prim on the one
    atlas, ``paint``. ``rgb`` is the shroud's linear paint (the genome's
    style colour), lettered and worn in the tiles."""
    L = layout(form, w, d, h)
    prims = []
    _enclosure(L, prims)
    _instrument(L, prims)
    paint = tuple(_srgb8(c) for c in rgb[:3])
''',
         '''    """``{"prims", "tiles", "collision", "layout", "lamp", "facts"}``: every
    prim on one of two atlases, ``paint`` or ``glow`` (`GLOW_TILES`, 1.89.0),
    and ``lamp`` the hood lamp's marker -- its name, where it hangs, and the
    payload it carries. ``rgb`` is the shroud's linear paint (the genome's
    style colour), lettered and worn in the tiles."""
    L = layout(form, w, d, h)
    prims = []
    _enclosure(L, prims)
    _instrument(L, prims)
    # the lit atlas (1.89.0): the header's face and the diffuser's
    for p in prims:
        if p.get("tile") in GLOW_TILES:
            p["mat"] = "glow"
    paint = tuple(_srgb8(c) for c in rgb[:3])
'''),
        ("""    def spec(kind, w_m, h_m, **more):
        return ("paint", dict({"kind": kind, "w_m": w_m, "h_m": h_m, "paint": paint, "form": L["form"]}, **more))
""",
         """    def spec(kind, w_m, h_m, atlas="paint", **more):
        return (atlas, dict({"kind": kind, "w_m": w_m, "h_m": h_m, "paint": paint, "form": L["form"]}, **more))
"""),
        ("""        "cord": spec("payphone_cord", 0.02, 0.16),
    }
    if L["form"] != "pedestal":
        hw = 2.0 * (w / 2.0 - INSET - T_SIDE + INSET)
        tiles["header"] = spec("payphone_header", hw, HEADER_H, line=hw >= HEADER_LINE_W)
""",
         """        "cord": spec("payphone_cord", 0.02, 0.16),
        "lens_rim": spec("payphone_lens_rim", 0.10, 0.03),
        "lens": spec("payphone_lens", L["lens"][1] - L["lens"][0], LENS_D, atlas="glow"),
    }
    if L["form"] != "pedestal":
        hw = 2.0 * (w / 2.0 - INSET - T_SIDE + INSET)
        tiles["header"] = spec("payphone_header", hw, HEADER_H, atlas="glow", line=hw >= HEADER_LINE_W)
"""),
        ("""    return {"prims": prims, "tiles": tiles, "collision": collision, "layout": L,
            "facts": {"form": L["form"], "company": COMPANY, "tris": P.tri_count(prims), "materials": 1}}
""",
         """    return {"prims": prims, "tiles": tiles, "collision": collision, "layout": L,
            "lamp": {"name": LAMP, "at": L["lamp"],
                     "props": {"lux_type": LAMP_TYPE, "lux_drop": L["lamp"][2]}},
            "facts": {"form": L["form"], "company": COMPANY, "tris": P.tri_count(prims), "materials": 2}}
"""),
        ("""    if kind == "payphone_binder_edge":
        w, h = _px(spec["w_m"], 200), _px(spec["h_m"], 200)
        im = PT.Img(w, h, (26, 26, 30))
        return im.to_canvas()
    raise ValueError(f"no payphone tile {kind!r}")
""",
         """    if kind == "payphone_binder_edge":
        w, h = _px(spec["w_m"], 200), _px(spec["h_m"], 200)
        im = PT.Img(w, h, (26, 26, 30))
        return im.to_canvas()
    if kind == "payphone_lens":
        # the diffuser a tube shines through (1.89.0), on the lit atlas: its
        # art is its own light. The tube's line runs its length, a little
        # brighter; the prismatic panel's ribs cross it, faint
        w, h = _px(spec["w_m"], 400), _px(spec["h_m"], 400)
        im = PT.Img(w, h, LENS_WHITE)
        im.rect((0, int(h * 0.36), w, int(h * 0.64)), LENS_TUBE, 0.8)
        for k in range(0, w, 4):
            im.rect((k, 0, k + 1, h), _lift(LENS_WHITE, -14), 0.35)
        im.edge_dark((0, 0, w, h), max(2, h * 0.08), 0.20)
        return im.to_canvas()
    if kind == "payphone_lens_rim":
        # the diffuser's frame, the canopy's own metal, darker
        w, h = _px(spec["w_m"], 400), _px(spec["h_m"], 400)
        im = PT.Img(w, h, _lift(body, -40))
        im.grain((0, 0, w, h), 2.0, 47)
        return im.to_canvas()
    raise ValueError(f"no payphone tile {kind!r}")
"""),
    ],
    "zoo_keeper/bpylayer/build.py": [
        ("""    for name, loc in result.get("attachments", {}).items():
        markers.add_marker(name, loc, coll)
    if opts["lods"]:
""",
         """    for name, loc in result.get("attachments", {}).items():
        markers.add_marker(name, loc, coll, props=result.get("marker_props", {}).get(name))
    if opts["lods"]:
"""),
        ("""    for name, loc in result.get("attachments", {}).items():
        markers.add_marker(name, loc, coll)

    fit_names = ([o.name for o in result["fit_objects"]]
""",
         """    for name, loc in result.get("attachments", {}).items():
        markers.add_marker(name, loc, coll, props=result.get("marker_props", {}).get(name))

    fit_names = ([o.name for o in result["fit_objects"]]
"""),
    ],
    "zoo_keeper/bpylayer/markers.py": [
        ('''"""Attachment markers: empties exported as glTF nodes for wearables,
mount points, and gameplay anchors (ATT_* naming)."""
''',
         '''"""Attachment markers: empties exported as glTF nodes for wearables,
mount points, and gameplay anchors (ATT_* naming), and Lux's emitter markers
(`LuxEmit_*`) where a recipe stands its own lamp."""
'''),
        ('''def add_marker(name, location, collection, size=0.08):
    empty = bpy.data.objects.new(name, None)
    empty.empty_display_type = "PLAIN_AXES"
    empty.empty_display_size = size
    empty.location = location
    collection.objects.link(empty)
''',
         '''def add_marker(name, location, collection, size=0.08, props=None):
    """An empty at ``location``. ``props`` (1.89.0) become its custom
    properties, which the glTF export writes as the node's ``extras``
    (`export._export_selection`, ``export_extras=True``) and Godot imports as
    its ``extras`` metadata -- where `LuxFixtureSpawner.marker_payload` reads a
    lamp's ``lux_type`` and ``lux_drop``. `build.build_fixtures` stamps its
    markers the same way."""
    empty = bpy.data.objects.new(name, None)
    empty.empty_display_type = "PLAIN_AXES"
    empty.empty_display_size = size
    empty.location = location
    for key, value in (props or {}).items():
        empty[key] = value
    collection.objects.link(empty)
'''),
    ],
    "zoo_keeper/recipes/payphone.py": [
        ('''"""payphone recipe: a 1990s coin payphone in one of three enclosures, one
atlas, one draw.
''',
         '''"""payphone recipe: a 1990s coin payphone in one of three enclosures, two
atlases, two draws.
'''),
        ("""stainless instrument with its keys, coin slot, coin-return recess, vault door,
card and cradle; the handset on its armoured cord. `recipes/_card_atlas.
build_art` builds every prim into one object on one painted image. See that
module for the reference, the forms and the company.
""",
         """stainless instrument with its keys, coin slot, coin-return recess, vault door,
card and cradle; the handset on its armoured cord. `recipes/_card_atlas.
build_art` builds the PAINT tiles into one object on one painted image, and
(1.89.0) the LIT tiles -- the header's face and the hood lamp's diffuser --
into one more, its backlit material named `_Face` so Lux's power cut takes
it: the ATM's two atlases (`recipes/atm.py`). See `core/payphone_forms.py`
for the reference, the forms, the company and the lamp.
"""),
        ("""draws: no keypad, no coin slot, no cord, nothing printed. The walker,
2026-10-09: it "doesn't have a phone or appropriate decals".
""",
         """draws: no keypad, no coin slot, no cord, nothing printed. The walker,
2026-10-09: it "doesn't have a phone or appropriate decals". 1.88.0 drew it in
one atlas; cold run 9212 found it a silhouette at midnight, and the walker,
on the lit proposal: "yes light it".
"""),
        ("""back. `ATT_hood` stays under the roof, where a light would go if a level lit
one. Origin on the ground under the middle (`build_module` re-centres it);
the caller at -Y.
""",
         """back. `ATT_hood` stays under the roof. The hood lamp's marker,
`LuxEmit_payphone_hood`, hangs under the diffuser with its payload --
`lux_type`, and `lux_drop`, its height above the ground -- as custom
properties, which the glTF export carries as the node's extras
(`bpylayer.markers.add_marker`). Origin on the ground under the middle
(`build_module` re-centres it); the caller at -Y.
"""),
        ("""    from ._card_atlas import build_art
    tiles = {k: spec for k, (_a, spec) in got["tiles"].items()}
    objs, _atlas = build_art(got["prims"], collection, dict(plan, _tiles=tiles), streams,
                             "Payphone", roughness=ROUGHNESS, smooth=True)
    f = got["facts"]
    print(f"[payphone] {w:.2f} x {d:.2f} x {h:.2f} form={f['form']} {f['tris']} tris, 1 material")
    return {"objects": objs, "collision_boxes": got["collision"],
            "attachments": {"ATT_hood": (0.0, 0.0, got["layout"]["top"] - PF.T_ROOF)},
            "payphone": {"form": f["form"], "company": f["company"]}}
""",
         """    from ._card_atlas import build_art
    objs = []
    for atlas_name, lit, name in (("paint", None, "Payphone"),
                                  ("glow", (PF.GLOW_EMISSION, PF.GLOW_ALBEDO), "PayphoneGlow")):
        tiles = {k: spec for k, (a, spec) in got["tiles"].items() if a == atlas_name}
        prims = [p for p in got["prims"] if p["mat"] == atlas_name]
        o, _atlas = build_art(prims, collection, dict(plan, _tiles=tiles), streams, name,
                              roughness=ROUGHNESS, lit=lit, smooth=True)
        objs += o
    f = got["facts"]
    lamp = got["lamp"]
    print(f"[payphone] {w:.2f} x {d:.2f} x {h:.2f} form={f['form']} {f['tris']} tris, "
          f"{f['materials']} materials, lamp drop {lamp['props']['lux_drop']:.3f}")
    return {"objects": objs, "collision_boxes": got["collision"],
            "attachments": {"ATT_hood": (0.0, 0.0, got["layout"]["top"] - PF.T_ROOF),
                            lamp["name"]: lamp["at"]},
            "marker_props": {lamp["name"]: dict(lamp["props"])},
            "payphone": {"form": f["form"], "company": f["company"]}}
"""),
    ],
    "zoo_keeper/genome/species/payphone.json": [
        ('''  "version": 2,
''', '''  "version": 3,
'''),
        ('''BUILT: one atlas, one material, 980 to 1,098 tris over its forms and the genome's corners, 1,046 as a booth at the default slot (2026-10-09); 308 tris and three materials before."''',
         '''BUILT: one atlas, one material, 980 to 1,098 tris over its forms and the genome's corners, 1,046 as a booth at the default slot (2026-10-09); 308 tris and three materials before. LIT (Zoo 1.89.0): the header's face and a hood lamp's diffuser on a second, backlit atlas, two materials and two draws, and the lamp's marker LuxEmit_payphone_hood carrying lux_type and lux_drop -- 990 to 1,108 tris over its forms and the genome's corners, 1,056 as a booth at the default slot, 4 of them lit (2026-10-09)."'''),
        ('''  "parts": [
    "Payphone_Art"
  ],
''',
         '''  "parts": [
    "Payphone_Art",
    "PayphoneGlow_Art"
  ],
'''),
    ],
    "tests/test_payphone.py": [
        ('''"""The 1990s coin payphone (Zoo 1.88.0, roadmap 210): three enclosures, one
atlas, one draw, an invented phone company, a real coin-return recess, and no
two faces on one plane at any size.
''',
         '''"""The 1990s coin payphone (Zoo 1.88.0, roadmap 210): three enclosures, an
invented phone company, a real coin-return recess, and no two faces on one
plane at any size. Since 1.89.0, two atlases and two draws: the header's face
and a hood lamp's diffuser are lit, and the lamp's marker hangs under the
diffuser in free air, carrying its height above the ground.
'''),
        ('''pinned it at 2 pairs (`test_coincident_faces.RESIDUE`). On 1.87.0 this file
fails at its import: there is no `core.payphone_forms`.
"""
''',
         '''pinned it at 2 pairs (`test_coincident_faces.RESIDUE`). On 1.87.0 this file
fails at its import: there is no `core.payphone_forms`. On 1.88.0 the lit
atlas, the lamp and the built GLB's second material fail: there is no
`PF.GLOW_TILES` and no layout `lamp`.
"""
'''),
        ('''    assert g["parts"] == ["Payphone_Art"]
''', '''    assert g["parts"] == ["Payphone_Art", "PayphoneGlow_Art"]
'''),
        ('''def test_one_atlas_one_material_and_every_tile_exists():
    for form in PF.FORMS:
        g = PF.plan(0.75, 0.5, 2.3, form)
        assert {p["mat"] for p in g["prims"]} == {"paint"}
        assert {a for a, _s in g["tiles"].values()} == {"paint"}
        assert {p["tile"] for p in g["prims"]} <= set(g["tiles"])
        assert g["facts"]["materials"] == 1
''',
         '''def test_two_atlases_and_the_lit_one_holds_the_header_and_the_diffuser():
    """The header's face and the diffuser are lit (1.89.0); everything else is
    paint. A tile on the wrong atlas is a sign that does not glow, or a shroud
    that does."""
    for form in PF.FORMS:
        g = PF.plan(0.75, 0.5, 2.3, form)
        assert {p["mat"] for p in g["prims"]} == {"paint", "glow"}
        for p in g["prims"]:
            assert (p["mat"] == "glow") == (p["tile"] in PF.GLOW_TILES), p["part"]
        for name, (atlas, _spec) in g["tiles"].items():
            assert atlas == ("glow" if name in PF.GLOW_TILES else "paint"), name
        assert {p["tile"] for p in g["prims"]} <= set(g["tiles"])
        lit = {p["tile"] for p in g["prims"] if p["mat"] == "glow"}
        assert lit == ({"lens"} if form == "pedestal" else {"header", "lens"}), (form, lit)
        assert g["facts"]["materials"] == 2
'''),
        ('''@pytest.mark.parametrize("form", PF.FORMS)
def test_bpy_a_payphone_is_one_object_one_material_and_fits(tmp_path, form):
    bpy = pytest.importorskip("bpy")
''',
         '''def _part_boxes(prims):
    """Each part's bounds, a part being its prims' name up to a box face's
    suffix; a part that is one prim is its own."""
    boxes = {}
    for p in prims:
        key = p["part"]
        if key.endswith(("_front", "_back", "_left", "_right", "_top", "_under")):
            key = key.rsplit("_", 1)[0]
        lo, hi = boxes.get(key, ((1e9,) * 3, (-1e9,) * 3))
        boxes[key] = (tuple(min(lo[k], min(v[k] for v in p["verts"])) for k in range(3)),
                      tuple(max(hi[k], max(v[k] for v in p["verts"])) for k in range(3)))
    return boxes


def test_the_hood_lamp_hangs_in_free_air_under_its_diffuser():
    """A lamp inside closed hardware bakes to nothing (Lux 0.65.0's pole,
    0.67.0's bulbs). The marker hangs LAMP_EMIT under the diffuser's face,
    behind the header, in front of the instrument and above it, inside no
    part, and carries its own height above the ground for Lux to solve
    from."""
    for form in PF.FORMS:
        for w, d, h in CORNERS:
            g = PF.plan(w, d, h, form)
            L = g["layout"]
            x0, x1, y0, y1, z0, z1 = L["lens"]
            lx, ly, lz = L["lamp"]
            assert x0 < lx < x1 and y0 < ly < y1, (form, w, d, h)
            assert lz == pytest.approx(z0 - PF.LAMP_EMIT)
            assert z1 == pytest.approx(h - PF.T_ROOF)
            assert lz > L["inst"][5], (form, w, d, h)
            assert ly < L["y_face"], (form, w, d, h)
            if form != "pedestal":
                hdr = next(p for p in g["prims"] if p["part"] == "Payphone_Header_front")
                assert y0 - max(v[1] for v in hdr["verts"]) > PF.T_HEADER, (form, w, d, h)
            for part, (lo, hi) in _part_boxes(g["prims"]).items():
                assert not all(lo[k] < c < hi[k] for k, c in enumerate((lx, ly, lz))), (form, w, d, h, part)
            assert g["lamp"]["name"] == "LuxEmit_payphone_hood"
            assert g["lamp"]["at"] == L["lamp"]
            assert g["lamp"]["props"] == {"lux_type": "payphone_hood", "lux_drop": lz}


def test_the_recipe_hands_the_lamp_and_its_payload_to_the_marker():
    """The marker is an attachment and its payload rides `marker_props`, which
    `bpylayer.build` passes to `markers.add_marker` at both call sites."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    recipe = open(os.path.join(root, "zoo_keeper", "recipes", "payphone.py"), encoding="utf-8").read()
    assert 'lamp["name"]: lamp["at"]' in recipe
    assert '"marker_props": {lamp["name"]: dict(lamp["props"])}' in recipe
    build_src = open(os.path.join(root, "zoo_keeper", "bpylayer", "build.py"), encoding="utf-8").read()
    call = 'markers.add_marker(name, loc, coll, props=result.get("marker_props", {}).get(name))'
    assert build_src.count(call) == 2
    assert "markers.add_marker(name, loc, coll)\\n" not in build_src


@pytest.mark.parametrize("form", PF.FORMS)
def test_bpy_a_payphone_is_two_objects_two_materials_and_its_lamp(tmp_path, form):
    """Built as a kit builds it and read back out of the GLB: the paint and the
    lit art, the lit material named `_Face` for Lux's power cut, and the lamp's
    marker with its payload in the node's extras, re-centred with the geometry
    (1.89.0)."""
    bpy = pytest.importorskip("bpy")
'''),
        ('''    assert res["report"]["status"] == "pass", res["report"]["checks"]
    objs = [o for o in bpy.context.scene.objects if o.type == "MESH" and not o.name.endswith(_COL_SUFFIXES)]
    assert len(objs) == 1
    raw = open(os.path.join(str(tmp_path), res["files"]["glb"]), "rb").read()
    ln, _kind = struct.unpack_from("<I4s", raw, 12)
    doc = json.loads(raw[20:20 + ln])
    assert len(doc["materials"]) == 1
''',
         '''    assert res["report"]["status"] == "pass", res["report"]["checks"]
    objs = sorted(o.name for o in bpy.context.scene.objects
                  if o.type == "MESH" and not o.name.endswith(_COL_SUFFIXES))
    assert objs == ["PayphoneGlow_Art", "Payphone_Art"], objs
    raw = open(os.path.join(str(tmp_path), res["files"]["glb"]), "rb").read()
    ln, _kind = struct.unpack_from("<I4s", raw, 12)
    doc = json.loads(raw[20:20 + ln])
    assert len(doc["materials"]) == 2
    assert [m["name"].endswith("_Face") for m in doc["materials"]].count(True) == 1, doc["materials"]
    lamps = [n for n in doc["nodes"] if n["name"].startswith("LuxEmit_payphone_hood")]
    assert len(lamps) == 1, [n["name"] for n in doc["nodes"]]
    want = PF.layout(form, 0.75, 0.5, 2.3)["lamp"]
    assert lamps[0]["extras"]["lux_type"] == "payphone_hood"
    assert lamps[0]["extras"]["lux_drop"] == pytest.approx(want[2])
    # glTF is Y up with the caller at +Z, and the module is re-centred on its slot
    assert lamps[0]["translation"] == pytest.approx([want[0], want[2] - 2.3 / 2.0, -want[1]], abs=1e-4)
'''),
    ],
}


def _stage(root, edits):
    """{path: bytes}: every file's new content, every anchor matched once,
    endings kept (or LF for `TO_LF`); raises before anything is written."""
    staged = {}
    for rel, pairs in edits.items():
        p = root / rel
        d = p.read_bytes()
        if rel in SHA:
            got = hashlib.sha256(d).hexdigest()[:16]
            assert got == SHA[rel], (rel, "is not the file this patch read", got)
        crlf, lf = d.count(b"\r\n"), d.count(b"\n")
        assert crlf in (0, lf), (rel, "mixed endings")
        t = d.decode("utf-8").replace("\r\n", "\n")
        for old, new in pairs:
            n = t.count(old)
            assert n == 1, (rel, n, old[:70])
            t = t.replace(old, new)
        keep_crlf = crlf and rel not in TO_LF
        staged[p] = (t.replace("\n", "\r\n") if keep_crlf else t).encode("utf-8")
    return staged


def main():
    if DRAFT and not os.environ.get("ZOO_ROOT"):
        sys.exit("refusing: --draft is for a ZOO_ROOT copy, never the repo")
    v = (ZOO / "VERSION").read_bytes().strip()
    assert v == b"1.88.0", repr(v)
    staged = _stage(ZOO, EDITS)
    entry = (SRC / "CHANGELOG_1.89.0.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    for p, raw in staged.items():
        if not DRAFT:
            assert b"RESULT_" not in raw, (p, "still carries an unfilled result")
    if not DRAFT:
        left = entry.replace("RESULT_SUITE", "") if SUITE_PENDING else entry
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    cl = ZOO / "CHANGELOG.md"
    data = cl.read_bytes()
    crlf, lf = data.count(b"\r\n"), data.count(b"\n")
    assert crlf in (0, lf), "CHANGELOG.md has mixed endings"
    text = data.decode("utf-8").replace("\r\n", "\n")
    assert text.startswith(CHANGELOG_HEAD) and text.count(CHANGELOG_HEAD) == 1, text[:90]
    # Every anchor and hash matched: now write.
    for p, raw in staged.items():
        p.write_bytes(raw)
    out = entry + text
    cl.write_bytes((out.replace("\n", "\r\n") if crlf else out).encode("utf-8"))
    vfile = ZOO / "VERSION"
    vfile.write_bytes(vfile.read_bytes().replace(b"1.88.0", b"1.89.0"))
    print("Zoo 1.88.0 -> 1.89.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
