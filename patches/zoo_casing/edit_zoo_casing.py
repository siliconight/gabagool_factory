"""Zoo 1.126.0 on a CLONE (<repo>): a doorway or breach panel is cased at its ends (the walker's walk of cold run 9386,
finding 2: "textures have visible seams"; their call 2026-10-24: "Yes hide the seam for breaches"). Anchored; refuses
on a miss.

    python edit_zoo_casing.py <repo>
"""
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


ARCH_BLOCK = '''#: A CASED OPENING (1.126.0). The walker, walking cold run 9386: "textures have
#: visible seams" -- eight of their ten marks stood where an interactive
#: opening meets the wall it is set in (the factory's
#: `docs/findings/walk_2026-10-23_9386/`, finding 2). A door and a breach panel
#: change state, so Level Factory keeps each a mesh of its own, lit from its
#: own rect of the lightmap, and the two bakes disagree across the joint (-12 %
#: and +13 % at a breach panel's edges). A building covers that joint with a
#: casing, and so does this: a strip on each face at each end, standing across
#: the joint so it covers both sides' edge, in the module's own material, so it
#: packs into the module's mesh and costs no draw. AN OPEN SHELL, front and
#: two sides: its back lies on the wall's face and its ends on the floor and the
#: ceiling, where nothing sees them, so they are not built and nothing is left
#: to be coplanar -- this change's first draft sank a closed box 1 mm and Zoo's
#: coincident-face census counted 12 more pairs a build on doorways and breach
#: panels (`tests/test_coincident_faces.py`, 6 -> 42). No collider.
#: The walker, 2026-10-24, on framing a breach panel, which shows a player
#: where a wall will open: "Yes hide the seam for breaches".
CASED_TYPES = ("doorway", "breach")
CASING_W = 0.09
CASING_PROUD = 0.015
#: what a casing keeps clear of an opening's void, so it never narrows it
CASING_VOID_CLEAR = 0.005


def casing_parts(w: float, d: float, h: float, void: dict | None = None,
                 width: float = CASING_W, proud: float = CASING_PROUD):
    """The casing of a module ``w`` x ``d`` x ``h`` in the slab's centred frame:
    ``(name, (cx, cy, cz), (sx, sy, sz))`` boxes, one a face (+Y ``Out``, -Y
    ``In``) at each end (``L`` at ``x = -w/2``, ``R`` at ``+w/2``), full height.
    Each reaches ``width / 2`` past the end into the neighbour's span and as
    far into the module's own, stopping ``CASING_VOID_CLEAR`` short of the
    void. Its back lies on the face; the builder drops the back and the ends
    (``CASING_DROPPED``)."""
    hw, half = w / 2.0, width / 2.0
    out = []
    for side, sgn in (("L", -1.0), ("R", 1.0)):
        inner = half
        if void:
            gap = (void["x0"] + hw) if side == "L" else (hw - void["x1"])
            inner = min(half, max(0.0, gap - CASING_VOID_CLEAR))
        lo, hi = (-hw - half, -hw + inner) if side == "L" else (hw - inner, hw + half)
        for face, fs in (("Out", 1.0), ("In", -1.0)):
            cy = fs * (d / 2.0 + proud / 2.0)
            out.append((f"Casing_{side}_{face}",
                        (round((lo + hi) / 2.0, 6), round(cy, 6), 0.0),
                        (round(hi - lo, 6), round(proud, 6), round(h, 6))))
    return out


def casing_dropped(name: str, normal) -> bool:
    """Whether a face of casing box ``name`` with ``normal`` (x, y, z) is one
    nobody sees: its ends (floor and ceiling) or its back (on the wall's face,
    which points the face's way, so the back points the other)."""
    back = -1.0 if name.endswith("_Out") else 1.0
    return abs(normal[2]) > 0.9 or normal[1] * back > 0.9


def storefront_parts(w: float, d: float, h: float, void: dict | None = None,'''

edit("zoo_keeper/core/arch.py", [
    ("def storefront_parts(w: float, d: float, h: float, void: dict | None = None,", ARCH_BLOCK),
])

edit("zoo_keeper/recipes/_arch.py", [
    ('''        part(bm, f"{root}_{name}{mark}", bv=plate_bevel)
    if species not in arch.PLATE_SPECIES or species in arch.PLATE_COLLIDES:''',
     '''        part(bm, f"{root}_{name}{mark}", bv=plate_bevel)
    # A CASED OPENING (1.126.0, `arch.casing_parts`): a doorway's or breach
    # panel's ends, both states, by the slot's TYPE -- an intact breach panel is
    # built as a wall and is still a breach slot. Structure, so it takes the
    # wall's material and its room face; no collider (built after `slab`'s).
    if ((plan.get("module") or {}).get("type") in arch.CASED_TYPES
            and species not in arch.PLATE_SPECIES and not plan.get("storefront")):
        for name, center, size in arch.casing_parts(w, d, h, void):
            bm = geometry.new_bm()
            geometry.add_box(bm, center, size)
            geometry.drop_faces(bm, lambda n, nm=name: arch.casing_dropped(nm, n))
            part(bm, f"{root}_{name}", bv=0.0)
    if species not in arch.PLATE_SPECIES or species in arch.PLATE_COLLIDES:'''),
])

edit("zoo_keeper/bpylayer/geometry.py", [
    ("""def add_box(bm, center, size):
    \"\"\"Axis-aligned box. center/size are (x, y, z) in meters.\"\"\"""",
     """def drop_faces(bm, pred):
    \"\"\"Delete the faces of ``bm`` whose normal ``pred`` accepts, returning how
    many (1.126.0): a part whose hidden sides would only lie coplanar with
    what hides them, as a casing's back lies on its wall.\"\"\"
    bm.normal_update()
    dead = [f for f in bm.faces if pred(tuple(f.normal))]
    if dead:
        bmesh.ops.delete(bm, geom=dead, context="FACES_ONLY")
    return len(dead)


def add_box(bm, center, size):
    \"\"\"Axis-aligned box. center/size are (x, y, z) in meters.\"\"\""""),
])

TEST = '''"""A doorway or breach panel is cased at its ends (1.126.0). The walker, walking cold run 9386: "textures have visible
seams" -- where an interactive opening, its own mesh and its own lightmap rect, meets the wall; and of framing a breach
panel: "Yes hide the seam for breaches". The pure half holds the geometry; the bpy half builds the modules. FAILS ON
1.125.0. Run inside Blender for this change:

    blender -b --factory-startup --python-expr "import sys, pytest; sys.path.insert(0, '.'); print('rc', int(pytest.main(['-q', '-p', 'no:cacheprovider', 'tests/test_casing.py'])))"
"""
from __future__ import annotations

import pytest

from zoo_keeper.core import arch


def _span(box):
    _n, (cx, _cy, _cz), (sx, _sy, _sz) = box
    return cx - sx / 2.0, cx + sx / 2.0


def test_each_end_has_a_casing_on_each_face_straddling_the_joint():
    w, d, h = 1.4, 0.3, 3.1
    parts = arch.casing_parts(w, d, h)
    assert sorted(p[0] for p in parts) == ["Casing_L_In", "Casing_L_Out", "Casing_R_In", "Casing_R_Out"]
    for p in parts:
        lo, hi = _span(p)
        joint = -w / 2.0 if "_L_" in p[0] else w / 2.0
        assert lo < joint < hi, p
        assert abs(p[2][2] - h) < 1e-9


def test_a_casing_sits_on_the_face_and_drops_only_what_nobody_sees():
    d = 0.3
    for name, (_cx, cy, _cz), (_sx, sy, _sz) in arch.casing_parts(1.4, d, 3.1):
        assert abs(cy) - sy / 2.0 == pytest.approx(d / 2.0), name
        assert abs(cy) + sy / 2.0 - d / 2.0 == pytest.approx(arch.CASING_PROUD), name
        out = 1.0 if name.endswith("_Out") else -1.0
        assert not arch.casing_dropped(name, (0.0, out, 0.0)), name          # its front
        assert not arch.casing_dropped(name, (1.0, 0.0, 0.0)), name          # its sides
        assert arch.casing_dropped(name, (0.0, -out, 0.0)), name             # its back
        assert arch.casing_dropped(name, (0.0, 0.0, 1.0)) and arch.casing_dropped(name, (0.0, 0.0, -1.0))


def test_a_casing_never_narrows_the_opening():
    void = {"x0": -0.5, "x1": 0.5, "z0": -1.55, "z1": 0.65}
    for p in arch.casing_parts(1.25, 0.3, 3.1, void):
        lo, hi = _span(p)
        assert hi <= void["x0"] - arch.CASING_VOID_CLEAR + 1e-9 or lo >= void["x1"] + arch.CASING_VOID_CLEAR - 1e-9, p


def _module(role, extra=None):
    from zoo_keeper.core import kit
    slot = {"slot_id": "s", "role": role, "size_mod": "full", "style": 1, "material": "concrete",
            "fit": {"dims": [1.4, 0.3, 3.1], "pivot": "center", "collision": "convex",
                    "openings": [{"kind": "door", "width": 1.0, "height": 2.2, "sill": 0.0}] if role == "doorway" else []}}
    slot.update(extra or {})
    return kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco_1997", style=1)["modules"]


def _built(module, tmp_path):
    import bpy
    from zoo_keeper.bpylayer import build as B
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    B.build_module(module, str(tmp_path / module["stem"]), theme="delco_1997", style=1, options={"save_blend": False})
    return sorted(o.name for o in bpy.data.objects if o.type == "MESH")


BREACH = {"interactive": {"id": "t:if:1", "kind": "breach_wall", "states": ["intact", "breached"],
                          "default": "intact", "state_geometry": {"intact": "wall", "breached": "breach"},
                          "collision_per_state": {"intact": True, "breached": False}}}


def test_bpy_a_doorway_and_both_states_of_a_breach_panel_are_cased_and_a_wall_is_not(tmp_path):
    pytest.importorskip("bpy")
    import bpy
    doorway = _module("doorway")[0]
    assert sum("_Casing_" in n for n in _built(doorway, tmp_path)) == 4
    assert all(len(o.data.polygons) == 3 for o in bpy.data.objects if "_Casing_" in o.name)
    breach = _module("breach", BREACH)
    assert {m.get("state") for m in breach} == {None, "breached"}
    for m in breach:
        assert sum("_Casing_" in n for n in _built(m, tmp_path)) == 4, m["stem"]
    wall = _module("wall")[0]
    assert not any("_Casing_" in n for n in _built(wall, tmp_path))
'''
(R / "tests" / "test_casing.py").write_text(TEST, encoding="utf-8", newline="\n")
print("arch.casing_parts, _arch cases doorways and breach panels; tests/test_casing.py")
