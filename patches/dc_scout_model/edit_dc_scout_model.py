"""Deli Counter 0.259.0, the scout model (the factory's roadmap 295), applied to a CLONE (<repo>) that already holds
the new `scout_model.py`: the package's `drawings/scout.glb`, the tests, VERSION. Anchored; refuses on a miss."""
import pathlib
import sys

R = pathlib.Path(sys.argv[1])
assert (R / "scout_model.py").is_file(), "scout_model.py first"


def edit(rel, pairs):
    p = R / rel
    b = p.read_bytes()
    crlf = b"\r\n" in b
    t = b.decode("utf-8").replace("\r\n", "\n")
    for o, n in pairs:
        assert t.count(o) == 1, (rel, o[:70])
        t = t.replace(o, n)
    p.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))


edit("portable_building.py", [
    ("""    signals needed") -- each with a ``.import`` that keeps it as the file it is (`KEEP_IMPORT`), and
    ``drawings.json`` naming them.""",
     """    signals needed") -- and since 0.259.0 its scout model, ``scout.glb`` (`scout_model.build_glb`: those signals
    as a model a player turns all the way round, one mesh a storey; the factory's roadmap 295) -- each with a
    ``.import`` that keeps it as the file it is (`KEEP_IMPORT`: a game reads the model with `GLTFDocument` when its
    screen opens, so no level pays to import it), and ``drawings.json`` naming them."""),
    ("""    import axonometric
    import floorplan
    import spec_loader
    spec = spec_loader.load_spec(spec_path)""",
     """    import axonometric
    import floorplan
    import scout_model
    import spec_loader
    spec = spec_loader.load_spec(spec_path)"""),
    ("""    record = {"schema": "deli_counter.drawings.v1", "spec": spec.name, "axonometric": None, "scout": None,
              "plans": []}
    files = {}""",
     """    record = {"schema": "deli_counter.drawings.v1", "spec": spec.name, "axonometric": None, "scout": None,
              "scout_model": None, "plans": []}
    files = {}
    blobs = {}"""),
    ("""        files["scout.svg"] = axonometric.render_axonometric(spec, scout=True)
        record["scout"] = "scout.svg"
""",
     """        files["scout.svg"] = axonometric.render_axonometric(spec, scout=True)
        record["scout"] = "scout.svg"
        blobs["scout.glb"] = scout_model.build_glb(spec)
        record["scout_model"] = "scout.glb"
"""),
    ("""    for name, text in files.items():
        with open(os.path.join(ddir, name), "w", encoding="utf-8", newline="\\n") as f:
            f.write(text)
        with open(os.path.join(ddir, name + ".import"), "w", encoding="utf-8", newline="\\n") as f:
            f.write(KEEP_IMPORT)""",
     """    for name, text in files.items():
        with open(os.path.join(ddir, name), "w", encoding="utf-8", newline="\\n") as f:
            f.write(text)
    for name, data in blobs.items():
        with open(os.path.join(ddir, name), "wb") as f:
            f.write(data)
    for name in list(files) + list(blobs):
        with open(os.path.join(ddir, name + ".import"), "w", encoding="utf-8", newline="\\n") as f:
            f.write(KEEP_IMPORT)"""),
])

edit("test_package_drawings.py", [
    ("""    assert rec["spec"] == spec.name and rec["axonometric"] == "axonometric.svg" and rec["scout"] == "scout.svg"
""",
     """    assert rec["spec"] == spec.name and rec["axonometric"] == "axonometric.svg" and rec["scout"] == "scout.svg"
    assert rec["scout_model"] == "scout.glb"
    import scout_model as SM
    assert (d / "scout.glb").read_bytes() == SM.build_glb(spec)
    assert (d / "scout.glb.import").read_text(encoding="utf-8") == PB.KEEP_IMPORT
"""),
    ("""    assert rec["axonometric"] is None and rec["scout"] is None and rec["plans"] == []""",
     """    assert rec["axonometric"] is None and rec["scout"] is None and rec["scout_model"] is None and rec["plans"] == []"""),
    ("""    assert not list(d.glob("*.svg")) and not list(d.glob("*.import"))""",
     """    assert not list(d.glob("*.svg")) and not list(d.glob("*.glb")) and not list(d.glob("*.import"))"""),
])

(R / "test_scout_model.py").write_text('''"""The scout model: the scout view's signals as a model a player turns all the way round (0.259.0, the factory's
roadmap 295).

The walker, of the scout view: "make it look more polished and artistic so it could ship to players....They can scout
out the buildings and rotate the schemas in a 360 degree way". `scout_model.build_glb` builds a GLB, one mesh a
storey, one material, colour in the vertex data.

THE TEST THAT MATTERS IS `test_the_model_and_the_scout_drawing_agree_on_every_door_and_window`: the model reads the
layout the drawings read, and a player must not find a door in one that the other does not have.
"""
import json
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import axonometric as AX  # noqa: E402
import floorplan as FP  # noqa: E402
import scout_model as SM  # noqa: E402
import spec_loader  # noqa: E402

NAMES = ("deli_a03", "office", "pharmacy_a01")


def _load(name):
    return spec_loader.load_spec(os.path.join(HERE, "specs", name + ".json"))


def _gltf(data):
    magic, version, length = struct.unpack_from("<III", data, 0)
    assert (magic, version, length) == (0x46546C67, 2, len(data))
    jlen, jtype = struct.unpack_from("<II", data, 12)
    assert jtype == 0x4E4F534A
    blen, btype = struct.unpack_from("<II", data, 20 + jlen)
    assert btype == 0x004E4942 and 28 + jlen + blen == len(data)
    return json.loads(data[20:20 + jlen])


def test_a_node_and_a_mesh_a_storey_at_its_true_elevation_with_one_material():
    for name in NAMES:
        spec = _load(name)
        g = _gltf(SM.build_glb(spec))
        sh = FP._story_height(spec)
        stories = FP.stories_in(spec)
        assert [n["extras"]["storey"] for n in g["nodes"]] == stories, name
        for n in g["nodes"]:
            assert abs(n["translation"][1] - n["extras"]["storey"] * sh) < 1e-6, (name, n["name"])
        assert len(g["materials"]) == 1 and len(g["meshes"]) == len(stories), name
        for m in g["meshes"]:
            (prim,) = m["primitives"]
            col = g["accessors"][prim["attributes"]["COLOR_0"]]
            assert (col["componentType"], col["type"], col.get("normalized")) == (5121, "VEC4", True), name


def _openings_by_storey_in_the_drawing(spec):
    """{storey: (doors, windows)} as the scout drawing draws them: a door's threshold line, a window's glass box."""
    svg = AX.render_axonometric(spec, scout=True)
    heads = list(re.finditer(r'<g id="storey_[^"]+" data-storey="(-?\\d+)"', svg))
    ends = [h.start() for h in heads[1:]] + [svg.index('<g id="connections">')]
    out = {}
    for h, e in zip(heads, ends):
        part = svg[h.end():e]
        doors = len(re.findall(r'<line [^>]*data-opening=', part))
        windows = len(re.findall(r'<g data-opening=', part))
        out[int(h.group(1))] = (doors, windows)
    return out


def _openings_by_storey_in_the_model(spec):
    """{storey: (doors, windows)} counted off the model's own boxes: a door strip's top in the door or entry colour,
    a window's top in the glass colour."""
    pal = SM.PALETTES[SM.DEFAULT_PALETTE]

    def rgba(c):
        return tuple(int(round(SM._linear(v) * 255)) for v in c) + (255,)
    door, entry, glass = rgba(pal["door"]), rgba(pal["entry"]), rgba(pal["glass"])
    out = {}
    for s, m in SM._storeys(spec, pal).items():
        ups = [m.col[i] for i in range(0, len(m.pos), 4) if m.nrm[i] == (0.0, 1.0, 0.0)]
        out[s] = (sum(1 for c in ups if c in (door, entry)), sum(1 for c in ups if c == glass))
    return out


def test_the_model_and_the_scout_drawing_agree_on_every_door_and_window():
    seen = 0
    for name in NAMES + ("bank_branch_a02", "apartment_walkup_a01"):
        spec = _load(name)
        drawn, built = _openings_by_storey_in_the_drawing(spec), _openings_by_storey_in_the_model(spec)
        assert drawn == built, (name, drawn, built)
        seen += sum(d + w for d, w in drawn.values())
    assert seen > 40, seen    # the control: there are openings to agree about


def test_doors_in_from_outside_wear_the_entry_colour():
    """deli_a03 is entered from the street: its ground floor has doors in its exterior walls, and they, and only they,
    wear the entry colour."""
    spec = _load("deli_a03")
    pal = SM.PALETTES[SM.DEFAULT_PALETTE]
    entry = tuple(int(round(SM._linear(v) * 255)) for v in pal["entry"]) + (255,)
    tops = {s: [m.col[i] for i in range(0, len(m.pos), 4) if m.nrm[i] == (0.0, 1.0, 0.0)]
            for s, m in SM._storeys(spec, pal).items()}
    exterior_doors = 0
    for wall in FP.storey_walls(spec, 0):
        if str(wall["name"]).startswith("ext"):
            exterior_doors += sum(1 for op in wall["openings"] if float(op.resolved().get("sill") or 0.0) < 1e-6)
    assert exterior_doors > 0
    assert tops[0].count(entry) == exterior_doors


def test_the_model_is_deterministic_and_every_library_building_builds():
    """Every building with an inside builds; the largest is a REGRESSION DETECTOR, not a frame cost (CLAUDE.md: draw
    calls are the budget) -- a model that silently doubles trips it. Measured 2026-10-22: 132 buildings, the largest
    cbp_town_finale_midbalanced at 5,628 triangles."""
    import glob
    worst = 0
    for path in sorted(glob.glob(os.path.join(HERE, "specs", "*.json"))):
        if os.path.basename(path).startswith("lf_"):
            continue
        spec = spec_loader.load_spec(path)
        if getattr(spec, "facade", False):
            continue
        worst = max(worst, sum(SM.model_stats(spec).values()))
    assert 0 < worst <= 8000, worst
    spec = _load("office")
    assert SM.build_glb(spec) == SM.build_glb(spec)
    assert set(SM.PALETTES) >= {SM.DEFAULT_PALETTE}
''', encoding="utf-8", newline="\n")

v = R / "VERSION"
assert v.read_bytes().decode("utf-8") == "Deli Counter 0.258.0"
v.write_bytes(b"Deli Counter 0.259.0")
print("edited", R)
