"""Zoo 1.86.0: the responders' cruiser (roadmap 212). The walker, 2026-10-08:
"I would think a classic 1990s Crown Victoria", and "Delco County Police
Dept. as a start?". A new species, `cruiser`: `simple_car`'s sedan at a
Crown Victoria's proportions, a 1990s patrol car's kit, and a department's
livery on one image -- five meshes, one a material.

New files copied from `zoo_cruiser/`: `core/cruiser_forms.py`,
`recipes/cruiser.py`, `genome/species/cruiser.json`, `tests/test_cruiser.py`.
Anchored edits (every anchor once; refuses on a miss):
- `core/car_forms.py`: the `cruiser` row, `SEDANS`, `STREET_STYLES`.
- `recipes/simple_car.py`: a caller's `form`, sedan details by `SEDANS`, and
  the door, moulding and cabin values it built, returned. Its own cars are
  unchanged: 200 meshes hashed against 1.85.0, 0 differ (the CHANGELOG).
- The registries a new species joins: `tests/test_genome.py`,
  `tests/test_material_options_closed.py`, and the two audits that count by
  a literal on purpose (`tests/test_coincident_faces.py`,
  `tests/test_theme_style_resolution.py`); and `tests/test_car_forms.py`,
  whose style sets are `simple_car`'s own.
CHANGELOG and VERSION from `zoo_cruiser/CHANGELOG_1.86.0.md`.

    python patch_zoo_cruiser.py
    ZOO_ROOT=<copy> python patch_zoo_cruiser.py
"""
import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
ZOO = pathlib.Path(os.environ.get("ZOO_ROOT") or HERE.parent / "zoo")
SRC = HERE / "zoo_cruiser"


#: path -> [its text with LF endings, whether it was CRLF]. Nothing is written
#: until every anchor in every file has matched (docs/SHIPPING_A_CHANGE.md,
#: step 3), so a miss leaves the tree as it was.
_STAGED = {}


def _edit(path, old, new):
    """Stage one anchored replacement; refuse unless ``old`` occurs once."""
    if path not in _STAGED:
        d = path.read_bytes()
        crlf = d.count(b"\r\n")
        assert crlf in (0, d.count(b"\n")), (path.name, "mixed line endings")
        _STAGED[path] = [d.decode("utf-8").replace("\r\n", "\n"), bool(crlf)]
    s = _STAGED[path][0]
    assert s.count(old) == 1, (path.name, s.count(old), old[:60])
    _STAGED[path][0] = s.replace(old, new)


CRUISER_ROW = '''#: THE CRUISER (Zoo 1.86.0, roadmap 212): the responders' 1990s Ford Crown
#: Victoria police sedan, `species/cruiser.json` and `recipes/cruiser.py`. Read
#: off the 1998-2002 car's published sizes -- 5.385 m long, 1.986 m wide at
#: the body, 1.443 m tall, a 2.913 m wheelbase (0.541), about 0.99 m of front
#: overhang (0.184), P225/60R16 tyres (r 0.338 m, 0.234 of the height) -- and
#: off the walker's comps for the rest: a long hood, a near-vertical C-pillar
#: with a quarter glass, a long trunk (backlight base 0.785). Only reachable by
#: name: `auto` never parks a police car.
CRUISER = {
    "natural": {"depth": (5.2, 5.6), "height": (1.38, 1.50)},
    "doors": ((4, 1.0),),
    "wheel_r": 0.234, "clearance": 0.11, "belt": 0.67,
    "fascia": 0.53, "hood": 0.58, "deck": 0.685, "tail": 0.62,
    "wheelbase": 0.541, "front_overhang": 0.184,
    "ws_base": 0.345, "roof_front": 0.475, "roof_rear": 0.68,
    "bl_base": 0.785, "roof_w": 0.80,
    "tyre_w": 0.18, "mirror_out": 0.105,
    "pinch_front": 0.05, "pinch_rear": 0.03, "trough": "backlight",
    "quarter_glass": 1.0, "rack": 0.0, "two_tone": 0.0,
    "wheels": (("steel", 1.0),),
    "bumpers": (("body", 1.0),),
    "moulding": 1.0,
    "palette": (("black", 1),),
}
FORMS["cruiser"] = CRUISER

'''

AUTO_POOL = '''#: What `auto` chooses between, and how often, before the slot's
#: proportions narrow it. The coupe is reachable by asking for it.
AUTO_POOL = (("sedan", 0.50), ("hatchback", 0.25), ("suv", 0.25))
'''

SEDANS = '''
#: THE THREE-BOX STYLES (1.86.0): built as a sedan wherever a style decides a
#: detail -- a small quarter glass, wide tail lamps, the plate low on the
#: tail. The cruiser is one; drawn as an SUV here, its first build carried a
#: hatchback's quarter glass (doors 1.45 m long on a Crown Victoria) and an
#: SUV's tall corner lamps.
SEDANS = ("sedan", "coupe", "cruiser")
#: THE STREET'S STYLES: what `simple_car`'s genome offers by name and its
#: prompt rules reach. The cruiser is not one -- it is the `cruiser`
#: species' alone, built with its kit and livery (1.86.0).
STREET_STYLES = ("sedan", "coupe", "hatchback", "suv")
'''

SIMPLE_CAR = [
    ('''def build(plan, streams, collection):
''',
     '''def build(plan, streams, collection, form=None):
    # ``form`` (1.86.0): a `car_forms.resolve` result the caller has already
    # drawn and pinned -- the cruiser's blue-grey interior, steel wheels and
    # body bumpers. Without it the car is drawn here, as it always was, from
    # the same streams in the same order.
'''),
    ('''    f = car_forms.resolve(plan, streams)
''',
     '''    f = form if form is not None else car_forms.resolve(plan, streams)
'''),
    ('''        if style in ("sedan", "coupe"):
            xa, xb = 0.24, hwt - 0.045
''',
     '''        if style in car_forms.SEDANS:
            xa, xb = 0.24, hwt - 0.045
'''),
    ('''        if style in ("sedan", "coupe"):
            ra, rb, rza, rzb = xa + 0.015, xa + 0.10, za + 0.015, zb_ - 0.015
''',
     '''        if style in car_forms.SEDANS:
            ra, rb, rza, rzb = xa + 0.015, xa + 0.10, za + 0.015, zb_ - 0.015
'''),
    ('''    plate_zc = (t_z0 + t_z1) / 2.0 - (0.05 if style in ("sedan", "coupe") else 0.0)
''',
     '''    plate_zc = (t_z0 + t_z1) / 2.0 - (0.05 if style in car_forms.SEDANS else 0.0)
'''),
    ('''    for sign in (-1.0, 1.0):
        for ye in door_edges:
''',
     '''    # the side moulding's centre line, one number for the strip and for a
    # recipe lettering the doors around it (1.86.0)
    zm_moulding = _lerp(clear + ROCKER_H, z2_at, 0.42)
    for sign in (-1.0, 1.0):
        for ye in door_edges:
'''),
    ('''            zm = _lerp(clear + ROCKER_H, z2_at, 0.42)
''',
     '''            zm = zm_moulding
'''),
    ('''    for sign in (-1.0, 1.0):
        x0, x1 = sign * (xi - 0.012), sign * (xi + 0.006)
''',
     '''    card_in = xi - 0.012                            # the door cards' inner face
    for sign in (-1.0, 1.0):
        x0, x1 = sign * card_in, sign * (xi + 0.006)
'''),
    ('''    _box(groups["interior"], (-(xtub - 0.01), y_ws + 0.05, floor_z - 0.01),
         (xtub - 0.01, y_te - 0.05, floor_z + 0.012))
''',
     '''    floor_top = floor_z + 0.012                     # the cabin floor's top face
    _box(groups["interior"], (-(xtub - 0.01), y_ws + 0.05, floor_z - 0.01),
         (xtub - 0.01, y_te - 0.05, floor_top))
'''),
    ('''    seat_w = min(0.48, xi * 0.9, 2.0 * (xtub - 0.015 - xd))
    for sx in (-1.0, 1.0):
''',
     '''    seat_w = min(0.48, xi * 0.9, 2.0 * (xtub - 0.015 - xd))
    back_rear = y_fs + 0.39                         # the seat back's and headrest's rear face
    for sx in (-1.0, 1.0):
'''),
    ('''            (xc + seat_w / 2.0 - 0.02, y_fs + 0.39, back_top), (xc - seat_w / 2.0 + 0.02, y_fs + 0.39, back_top)])
        _box(groups["interior"], (xc - 0.13, y_fs + 0.31, back_top - 0.03),
             (xc + 0.13, y_fs + 0.39, back_top + 0.15))
''',
     '''            (xc + seat_w / 2.0 - 0.02, back_rear, back_top), (xc - seat_w / 2.0 + 0.02, back_rear, back_top)])
        _box(groups["interior"], (xc - 0.13, y_fs + 0.31, back_top - 0.03),
             (xc + 0.13, back_rear, back_top + 0.15))
'''),
    ('''    y_rs = min(y_fs + 0.95, y_te - 0.42)
    if y_rs - 0.24 > y_fs + 0.40:
''',
     '''    y_rs = min(y_fs + 0.95, y_te - 0.42)
    rear_front = y_rs - 0.24 if y_rs - 0.24 > y_fs + 0.40 else None
    if rear_front is not None:
'''),
    ('''                            "ATT_trunk": (0.0, (y_bl + yt) / 2.0 if trunk else yt, deck)}}
''',
     '''                            "ATT_trunk": (0.0, (y_bl + yt) / 2.0 if trunk else yt, deck)},
            # where the door seams stand and the door skin runs (1.86.0): a
            # recipe that paints the doors (the cruiser's livery) paints
            # them where this car cut them, not where it guesses
            "door_edges": list(door_edges),
            "door_skin_z": (clear + ROCKER_H, z2_at),
            "moulding_z": zm_moulding if f["moulding"] else None,
            # the cabin floor's top, the front seat backs' rear face, the
            # rear seat's front (None without one) and the door cards' inner
            # face (1.86.0): what a recipe that fits a part inside stands it
            # on and keeps it between
            "interior": {"floor_top": floor_top, "back_rear": back_rear,
                         "rear_front": rear_front, "card_in": card_in}}
'''),
]

CAR_FORMS_TEST = [
    ('''    assert set(g["params"]["body_style"][1:]) == set(car_forms.FORMS)
''',
     '''    assert set(g["params"]["body_style"][1:]) == set(car_forms.STREET_STYLES)
    # every form is a street style or the cruiser's, which is its species' alone (1.86.0)
    assert set(car_forms.FORMS) == set(car_forms.STREET_STYLES) | {"cruiser"}
'''),
    ('''    reached = {r["set"]["params.body_style"] for r in g["prompt_rules"]}
    assert reached == set(car_forms.FORMS)
''',
     '''    reached = {r["set"]["params.body_style"] for r in g["prompt_rules"]}
    assert reached == set(car_forms.STREET_STYLES)
'''),
    ('''    assert set(MEASURED["tris_max"]) == set(car_forms.FORMS)
''',
     '''    # simple_car's own styles; the cruiser row is its species', measured in
    # tests/test_cruiser.py against the cruiser genome's budget
    assert set(MEASURED["tris_max"]) == set(car_forms.STREET_STYLES)
'''),
]

CENSUS = '''#: 1.86.0: `cruiser`, three builds more, same tool, Blender 5.1.1: "3
#: builds, 0 with coincident pairs, 0 that did not build" (3,476 tris at
#: each corner), third run. The first found 8-9 pairs a build, all in the
#: kit, and the lowest corner refusing its livery; each fixed at its source.
#: The partition's posts stood 1-2 mm inside its rails' faces, the rails'
#: ends flush with its posts, its bottom rail in the cabin floor's bottom
#: plane, its middle posts 1.37 mm off the headrests' sides; the push bar's
#: lower brace touched its lower bar. Now `cruiser_forms.INSET` sets faces
#: back 4 mm, and the partition stands from the cabin `simple_car` returns.
#: The second run found the rail's underside 2 mm over the body's pan. The
#: species' own test checks the kit's faces at all 27 corners without
#: Blender, and a sweep of 51 sizes -- every centimetre of height at three
#: widths, both liveries -- found 0.
CENSUS_BUILDS = 366
'''


def main():
    v = (ZOO / "VERSION").read_text(encoding="utf-8").strip()
    assert v == "1.85.0", v
    zk = ZOO / "zoo_keeper"
    assert not (zk / "core" / "cruiser_forms.py").exists(), "already applied"
    new_files = {zk / "core" / "cruiser_forms.py": "cruiser_forms.py",
                 zk / "recipes" / "cruiser.py": "cruiser.py",
                 zk / "genome" / "species" / "cruiser.json": "cruiser.json",
                 ZOO / "tests" / "test_cruiser.py": "test_cruiser.py"}
    for dst in new_files:
        assert not dst.exists(), dst
    cf = zk / "core" / "car_forms.py"
    _edit(cf, AUTO_POOL, CRUISER_ROW + AUTO_POOL + SEDANS)
    _edit(cf, '''        out.append(("quarter", 0.42 if form["style"] in ("sedan", "coupe")
''', '''        out.append(("quarter", 0.42 if form["style"] in SEDANS
''')
    for old, new in SIMPLE_CAR:
        _edit(zk / "recipes" / "simple_car.py", old, new)
    for old, new in CAR_FORMS_TEST:
        _edit(ZOO / "tests" / "test_car_forms.py", old, new)
    _edit(ZOO / "tests" / "test_genome.py",
          '''                # the crew's getaway van (1.82.0, roadmap 206): a P30-style
                # step van, matte black gone chalky, parked at the spawn
                "step_van"}
''',
          '''                # the crew's getaway van (1.82.0, roadmap 206): a P30-style
                # step van, matte black gone chalky, parked at the spawn
                "step_van",
                # the responders' cruiser (1.86.0, roadmap 212): a 1990s
                # Crown Victoria lettered for the DELCO COUNTY POLICE
                "cruiser"}
''')
    _edit(ZOO / "tests" / "test_material_options_closed.py",
          '''           # (1.58.0)
           "dumpster",
''',
          '''           # (1.58.0)
           "dumpster",
           # a cruiser is simple_car's painted body under its livery's
           # image, its kit enamelled steel coloured in the vertex
           # (1.86.0)
           "cruiser",
''')
    # the two audits that count species by a literal on purpose
    _edit(ZOO / "tests" / "test_coincident_faces.py",
          'CENSUS_BUILDS = 363\n', CENSUS)
    _edit(ZOO / "tests" / "test_theme_style_resolution.py",
          '    assert len(_genomes()) == 94 + len(_minted), len(_genomes())\n',
          "    # 1.86.0: 95, + cruiser, its `delco` row a copy of its `default`: the\n"
          "    # department's livery is in its image, not in a theme.\n"
          '    assert len(_genomes()) == 95 + len(_minted), len(_genomes())\n')
    entry = (SRC / "CHANGELOG_1.86.0.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    assert "SUITE_PENDING" not in entry, "the CHANGELOG's suite line is not filled in"
    cl = ZOO / "CHANGELOG.md"
    d = cl.read_bytes()
    assert b"## [1.86.0]" not in d and d.startswith(b"## [1.85.0]")
    crlf = b"\r\n" in d
    changelog = (entry.replace("\n", "\r\n") if crlf else entry).encode("utf-8") + d
    # every anchor matched: write
    for dst, name in new_files.items():
        dst.write_bytes((SRC / name).read_bytes())
    for path, (s, was_crlf) in _STAGED.items():
        path.write_bytes((s.replace("\n", "\r\n") if was_crlf else s).encode("utf-8"))
    cl.write_bytes(changelog)
    (ZOO / "VERSION").write_bytes(b"1.86.0")
    print("1.85.0 -> 1.86.0: %d files new, %d edited" % (len(new_files), len(_STAGED)))


if __name__ == "__main__":
    main()
