"""Zoo 1.124.0 on a CLONE (<repo>): an Empty's shut front door has panels and a knob (the walker's walk of cold run
9386, finding 13: "many of the rowhome doors dont have doorknobs?"). Anchored; refuses on a miss.

    python edit_zoo_door_hardware.py <repo>
"""
import pathlib
import sys

R = pathlib.Path(sys.argv[1])
DOORS_BLOCK = '\n\n#: A DOOR HAS HARDWARE (1.124.0). The walker, walking cold run 9386, at a\n#: rowhome\'s stoop: "many of the rowhome doors dont have doorknobs?" -- the\n#: leaf was one flat box in its paint. A painted panel door: two raised panels\n#: on its street face, in the leaf\'s own material (they merge with it, no draw),\n#: and a knob on an escutcheon plate at the latch edge at handle height, in one\n#: shared brass (`HARDWARE`: one material for every door in a build, so the\n#: Empties\' per-side merge carries it as one more mesh a front at most). Each\n#: piece sinks `SINK` into the leaf, so no face of it lies on the leaf\'s face\n#: (`tests/test_coincident_faces.py`\'s rule). Sizes: a residential knob about\n#: 2 1/4 in across on its rose, 2 3/8 in back from the latch edge, about 38 in\n#: to its centre; the plate rounded to what reads at play distance. Built by\n#: `recipes/_arch.py`.\nKNOB_D = 0.06\nKNOB_PROUD = 0.06\nKNOB_Z = 0.95\nKNOB_FROM_EDGE = 0.07\nPLATE = (0.065, 0.012, 0.20)\nPANEL_INSET = 0.11\nPANEL_PROUD = 0.012\nPANEL_GAP = 0.12\nSINK = 0.001\nHARDWARE = ("M_Door_hardware_brass", (0.71, 0.55, 0.24), "metal_painted")\n'


def edit(rel, pairs):
    p = R / rel
    b = p.read_bytes()
    crlf = b"\r\n" in b
    t = b.decode("utf-8").replace("\r\n", "\n")
    for o, n in pairs:
        assert t.count(o) == 1, (rel, o[:70])
        t = t.replace(o, n)
    p.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))


dp = R / "zoo_keeper" / "core" / "doors.py"
raw = dp.read_bytes()
assert b"\r\n" not in raw and b"KNOB_D" not in raw
dp.write_bytes(raw.rstrip(b"\n") + b"\n" + DOORS_BLOCK.encode("utf-8"))

edit("zoo_keeper/recipes/_arch.py", [
    ('''        name, colour, kind = doors.leaf_material(
            plan.get("door"), plan.get("door_color", FACADE_DOOR_COLOR))
        materials.assign([leaf], materials.make_material(name, colour, kind))
        objs.append(leaf)''',
     '''        name, colour, kind = doors.leaf_material(
            plan.get("door"), plan.get("door_color", FACADE_DOOR_COLOR))
        leaf_mat = materials.make_material(name, colour, kind)
        materials.assign([leaf], leaf_mat)
        objs.append(leaf)
        # ITS PANELS AND ITS KNOB (1.124.0, `doors`' A DOOR HAS HARDWARE): on the
        # street face, +Y, each sunk doors.SINK into the leaf
        face_y = d / 2.0 - FACADE_DOOR_SETBACK
        cx = (void["x0"] + void["x1"]) / 2.0
        bm = geometry.new_bm()
        pw = lw - 2.0 * doors.PANEL_INSET
        ph = (lh - 2.0 * doors.PANEL_INSET - doors.PANEL_GAP) / 2.0
        if pw > 0.1 and ph > 0.1:
            for k in (0, 1):
                pz = void["z0"] + doors.PANEL_INSET + ph / 2.0 + k * (ph + doors.PANEL_GAP)
                geometry.add_box(bm, (cx, face_y + (doors.PANEL_PROUD - doors.SINK) / 2.0, pz),
                                 (pw, doors.PANEL_PROUD + doors.SINK, ph))
            panels = geometry.bm_to_object(bm, f"{root}_LeafPanels", collection, bevel=0.0,
                                           texel=1.0, rng=rng, wear=wear)
            materials.assign([panels], leaf_mat)
            objs.append(panels)
        kx = void["x1"] - doors.KNOB_FROM_EDGE
        kz = void["z0"] + doors.KNOB_Z
        bm = geometry.new_bm()
        geometry.add_box(bm, (kx, face_y + (doors.PLATE[1] - doors.SINK) / 2.0, kz),
                         (doors.PLATE[0], doors.PLATE[1] + doors.SINK, doors.PLATE[2]))
        geometry.add_cylinder(bm, (kx, face_y + doors.PLATE[1] + doors.KNOB_PROUD / 2.0 - doors.SINK, kz),
                              doors.KNOB_D / 2.0, doors.KNOB_PROUD, segments=8, axis="Y")
        knob = geometry.bm_to_object(bm, f"{root}_LeafHardware", collection, bevel=0.0,
                                     texel=1.0, rng=rng, wear=wear * 0.5)
        materials.assign([knob], materials.make_material(*doors.HARDWARE))
        objs.append(knob)'''),
])

TEST = '''"""An Empty's shut front door has panels and a knob (1.124.0). The walker, walking cold run 9386: "many of the
rowhome doors dont have doorknobs?" -- the leaf was one flat box.

The pure half holds the sizes; the bpy half builds a facade doorway and finds the hardware where a hand would reach
it. It skips without Blender and was run inside Blender 5.1.1 for this change, from the repo root:

    blender -b --factory-startup --python-expr "import sys, pytest; sys.path.insert(0, '.'); print('rc', int(pytest.main(['-q', '-p', 'no:cacheprovider', 'tests/test_door_hardware.py'])))"
"""
from __future__ import annotations

import pytest

from zoo_keeper.core import doors as A


def test_the_knob_is_where_a_hand_reaches_it():
    assert 0.85 <= A.KNOB_Z <= 1.05
    assert 0.05 <= A.KNOB_FROM_EDGE <= 0.09
    assert A.SINK > 0.0 and A.PANEL_PROUD > A.SINK
    name, colour, kind = A.HARDWARE
    assert name.startswith("M_Door_hardware") and kind == "metal_painted"


@pytest.mark.parametrize("finish", [None, "navy", "stained"])
def test_bpy_a_facade_door_has_panels_and_a_knob(finish, tmp_path):
    pytest.importorskip("bpy")
    import bpy
    from zoo_keeper.core import kit
    from zoo_keeper.bpylayer import build as B
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    slot = {"slot_id": "d", "role": "doorway", "size_mod": "full", "style": 1, "material": "brick",
            "glazing": "facade",
            "fit": {"dims": [2.0, 0.3, 3.3], "pivot": "center",
                    "openings": [{"kind": "door", "width": 1.0, "height": 2.2, "sill": 0.0}],
                    "collision": "convex"}}
    if finish:
        slot["door"] = finish
    plan = kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco_1997", style=1)
    B.build_module(plan["modules"][0], str(tmp_path / "out"), theme="delco_1997", style=1,
                   options={"save_blend": False})
    names = [o.name for o in bpy.data.objects if o.type == "MESH"]
    hw = [o for o in bpy.data.objects if o.type == "MESH" and o.name.endswith("_LeafHardware")]
    panels = [o for o in bpy.data.objects if o.type == "MESH" and o.name.endswith("_LeafPanels")]
    assert hw and panels, names
    assert hw[0].data.materials[0].name == A.HARDWARE[0]
'''
(R / "tests" / "test_door_hardware.py").write_text(TEST, encoding="utf-8", newline="\n")
print("_arch: a facade door's panels and knob; tests/test_door_hardware.py")
