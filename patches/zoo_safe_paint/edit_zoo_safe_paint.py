"""Zoo 1.125.0 on a CLONE (<repo>): a drop safe is painted steel (the walker's walk of cold run 9386, finding 3: "drop
safe looks like a brown box"). Anchored; refuses on a miss.

The genome offers `metal_painted` alone -- a species on the painted list offers no raw `metal`
(`tests/test_material_options_closed.py`, whose first run against this change's first draft, which kept `metal` as an
option, failed `test_nothing_else_moved`) -- and the recipe's dial and handle are `metal_bare`, a constant, as the
dartboard's chrome and the display case's frame are.

    python edit_zoo_safe_paint.py <repo>
"""
import json
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
    return t


NOTE = (" PAINTED STEEL (1.125.0): the walker, cold run 9386, of a drop safe: \"looks like a brown box\" -- `metal` "
        "is a theme's street metal (delco_1997's `metal_rusted_street`, averaging (115, 80, 53), next to its wood's "
        "(86, 60, 41)); a safe is painted steel in its style's colour, delco's (0.20, 0.21, 0.23), and its dial and "
        "handle bare steel, a constant in the recipe.")

gp = R / "zoo_keeper" / "genome" / "species" / "drop_safe.json"
g = json.loads(gp.read_bytes().decode("utf-8"))
assert g["materials"] == {"default": "metal", "options": ["metal"]}, g["materials"]
note_old = g["license"]["notes"]
t = edit("zoo_keeper/genome/species/drop_safe.json", [
    ('''"materials": {
    "default": "metal",
    "options": [
      "metal"
    ]
  },''', '''"materials": {
    "default": "metal_painted",
    "options": [
      "metal_painted"
    ]
  },'''),
    (json.dumps(note_old)[1:-1], json.dumps(note_old + NOTE)[1:-1]),
])
# every style names its own material; all five said `metal`
gb = gp.read_bytes()
gcrlf = b"\r\n" in gb
gt = gb.decode("utf-8").replace("\r\n", "\n")
assert gt.count('"material": "metal",') == 5, gt.count('"material": "metal",')
gt = gt.replace('"material": "metal",', '"material": "metal_painted",')
gp.write_bytes((gt.replace("\n", "\r\n") if gcrlf else gt).encode("utf-8"))
t = gt
g2 = json.loads(t)
assert all(s["material"] == "metal_painted" for s in g2["styles"].values()), g2["styles"]
assert g2["materials"] == {"default": "metal_painted", "options": ["metal_painted"]}, g2["materials"]
assert g2["license"]["notes"].endswith("a constant in the recipe.")

edit("zoo_keeper/recipes/drop_safe.py", [
    ('''    trim = materials.make_material("M_DropSafe_trim",
                                   _darker(plan["color"]), "metal")''',
     '''    # the dial and handle are bare steel, a constant (1.125.0): the body is
    # painted, and `metal` would be the theme's street rust on both
    trim = materials.make_material("M_DropSafe_trim",
                                   _darker(plan["color"]), "metal_bare")'''),
])

edit("tests/test_material_options_closed.py", [
    ('''           # the belt with them (1.119.0)
           "stanchion_run")''',
     '''           # the belt with them (1.119.0)
           "stanchion_run",
           # a drop safe is painted steel, its dial and handle bare steel as
           # a constant in the recipe (1.125.0)
           "drop_safe")'''),
])

TEST = '''"""A drop safe is painted steel (1.125.0). The walker, walking cold run 9386: "drop safe looks like a brown box" --
`metal` was its only kind, and a theme's `metal` is its street metal. Each test FAILS ON 1.124.0 but the
last, which passes there too (a slot naming a known kind builds it) and guards Deli Counter 0.267.0's safe
row, which asks for `metal_painted`."""
import os

import pytest

from zoo_keeper.core import dna, genome, kit

RECIPE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "zoo_keeper", "recipes",
                      "drop_safe.py")


def test_the_genome_paints_a_safe_and_offers_no_raw_metal():
    m = genome.load_species("drop_safe")["materials"]
    assert m == {"default": "metal_painted", "options": ["metal_painted"]}, m


def test_the_dial_and_handle_are_bare_steel_not_the_street_metal():
    src = open(RECIPE, encoding="utf-8").read()
    assert '"metal")' not in src
    assert '"metal_bare")' in src


def _resolved(**extra):
    """The plan a kit module's build executes: `kit.plan_kit`, then `dna.resolve_module_plan`, where a module's
    material is decided -- the style's, unless the slot names a known kind, which wins whatever the genome offers."""
    slot = {"slot_id": "s", "role": "prop", "size_mod": "full", "style": 1, "species": "drop_safe",
            "fit": {"dims": [0.9, 0.9, 1.0], "pivot": "center"}}
    slot.update(extra)
    module = kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco_1997", style=1)["modules"][0]
    return dna.resolve_module_plan(module, genome.load_species("drop_safe"), "delco_1997", 1, "test")


def test_a_safe_that_names_no_material_is_painted_steel():
    """Every style named `metal` for itself, so a slot asking nothing took the street metal."""
    assert _resolved()["material"] == "metal_painted"


def test_a_safe_asked_for_painted_steel_builds_painted_steel():
    assert _resolved(material="metal_painted")["material"] == "metal_painted"


def test_bpy_a_safe_naming_no_material_is_built_in_painted_steel(tmp_path):
    """Built in Blender: the body and door in the painted kind, the dial and handle the trim. Run inside Blender for
    this change: `blender -b --factory-startup --python-expr "import sys, pytest; sys.path.insert(0, '.');
    pytest.main(['-q', '-p', 'no:cacheprovider', 'tests/test_safe_paint.py'])"`."""
    pytest.importorskip("bpy")
    import bpy
    from zoo_keeper.bpylayer import build as B
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    slot = {"slot_id": "s", "role": "prop", "size_mod": "full", "style": 1, "species": "drop_safe",
            "fit": {"dims": [0.9, 0.9, 1.0], "pivot": "center"}}
    plan = kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco_1997", style=1)
    B.build_module(plan["modules"][0], str(tmp_path / "out"), theme="delco_1997", style=1,
                   options={"save_blend": False})
    mats = {o.name: o.data.materials[0].name for o in bpy.data.objects if o.type == "MESH" and o.data.materials}
    assert mats.get("DropSafe_Body") == "M_DropSafe_metal_painted", mats
    assert mats.get("DropSafe_Door") == "M_DropSafe_metal_painted", mats
    assert mats.get("DropSafe_Handle") == "M_DropSafe_trim", mats


# NOT TESTED, and why: a slot naming `metal` still builds `metal`. A module's slot override wins with any known kind
# (`dna.resolve_module_plan`), whatever the genome's options say -- so the library's stored safes, which name `metal`,
# are Deli Counter 0.267.0's migration to repaint, not this genome's. This file's first draft asserted the opposite,
# from `resolve_plan`'s fallback, which a kit module does not take.
'''
(R / "tests" / "test_safe_paint.py").write_text(TEST, encoding="utf-8", newline="\n")
print("drop_safe: metal_painted alone, dial and handle metal_bare; PAINTED list; tests/test_safe_paint.py")
