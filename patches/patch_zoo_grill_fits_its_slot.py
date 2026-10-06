"""Zoo 1.80.0: the flat-top grill fits its slot -- the knobs end on the front
face instead of standing 35 mm past it.

Cold runs 9132, 9179 and 9185 each logged `ZOO_PARTIAL_BUILD`. The one
module that failed was `prop_flat_top_grill_delco_1997_04_w120_d90_h105_mmetal`:
`fit_depth` measured 0.935 m against the exact 0.900 m slot. Every other check
passed, and the resolver fell back to base -- a grey stand-in in every deli
kitchen that draws it, deli_a01's included.

The recipe built the cabinet at the full slot depth and hung the knobs off
its front: 0.03 m cylinders centred 0.02 m before the face, so they stood
0.035 m proud. That is 0.900 + 0.035 = 0.935, exactly what was measured.

Now the layout lives in `core/flat_top_grill_forms.py`, as the fence's and the
roller grill's do: one place, no bpy, testable.
- The cabinet and everything on it are built `KNOB_PROUD` shallower and
  pushed back by half of it, so the knobs end on the slot's front face.
- The module's extents are exactly (width, depth, height) at any genome
  dimension.

    python patch_zoo_grill_fits_its_slot.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ZOO = ROOT / "zoo"
FORMS = ZOO / "zoo_keeper" / "core" / "flat_top_grill_forms.py"
RECIPE = ZOO / "zoo_keeper" / "recipes" / "flat_top_grill.py"
TEST = ZOO / "tests" / "test_flat_top_grill_forms.py"

FORMS_BODY = '''"""What a flat-top grill is, in numbers: ONE place, no bpy.

A heavy steel cabinet on four legs, a flat cooktop plate at counter height,
splash guards up the back and both ends, a grease trap along the front lip,
and a row of control knobs on the front face. Origin at floor centre; the
controls face -Y.

THE EXTENTS ARE EXACT (Zoo 1.80.0). The knobs stand KNOB_PROUD off the
cabinet's face, so the cabinet is that much shallower than the slot and set
back by half of it, and the knobs end on the slot's front face. Until 1.80.0
the cabinet took the whole depth and the knobs hung 35 mm past it: the module
measured 0.935 m against an exact 0.900 m slot, failed `fit_depth`, and fell
back to base in every kitchen that drew it (cold runs 9132, 9179, 9185).
"""
from __future__ import annotations

LEG_H = 0.12          # m
GUARD_H = 0.12        # m, splash guards above the cooking surface
PLATE_T = 0.03        # m, the cooktop plate
GUARD_T = 0.02        # m
KNOB_R = 0.022        # m
KNOB_LEN = 0.03       # m, along Y
KNOB_GAP = 0.005      # m, between the cabinet face and the knob
KNOB_PROUD = KNOB_GAP + KNOB_LEN   # how far the knobs stand off the face


def layout(w, d, h, n_knobs=3):
    """``[(name, shape, centre, size)]``. ``shape`` is ``"box"`` with ``size``
    ``(sx, sy, sz)``, or ``"cylinder"`` with ``size`` ``(radius, length,
    axis)``. Every part lies inside ``(-w/2..w/2, -d/2..d/2, 0..h)``, and
    together they reach every face of it."""
    surface_z = h - GUARD_H
    body_h = surface_z - PLATE_T - LEG_H
    cd = d - KNOB_PROUD               # the cabinet's depth
    cy = KNOB_PROUD / 2.0             # its centre, set back
    front = cy - cd / 2.0             # its face: -d/2 + KNOB_PROUD
    gz = surface_z + GUARD_H / 2.0
    parts = [
        ("Grill_Body", "box", (0.0, cy, LEG_H + body_h / 2.0), (w, cd, body_h)),
        ("Grill_Cooktop", "box", (0.0, cy, surface_z - PLATE_T / 2.0),
         (w * 0.98, cd * 0.98, PLATE_T)),
        ("Grill_SplashGuard_B", "box", (0.0, d / 2.0 - GUARD_T / 2.0, gz),
         (w, GUARD_T, GUARD_H)),
    ]
    for side, sx in (("L", -1), ("R", 1)):
        parts.append(("Grill_SplashGuard_%s" % side, "box",
                      (sx * (w / 2.0 - GUARD_T / 2.0), cy, gz),
                      (GUARD_T, cd, GUARD_H)))
    parts.append(("Grill_GreaseTrap", "box",
                  (0.0, front + 0.02, surface_z - PLATE_T - 0.015),
                  (w * 0.7, 0.03, 0.03)))
    for i in range(n_knobs):
        x = (i - (n_knobs - 1) / 2.0) * (w * 0.14)
        parts.append(("Grill_Knob_%d" % (i + 1), "cylinder",
                      (x, front - KNOB_GAP - KNOB_LEN / 2.0,
                       LEG_H + body_h * 0.6),
                      (KNOB_R, KNOB_LEN, "Y")))
    i = 0
    for sx in (-1, 1):
        for sy in (-1, 1):
            i += 1
            parts.append(("Grill_Leg_%d" % i, "box",
                          (sx * (w / 2.0 - 0.06), cy + sy * (cd / 2.0 - 0.06),
                           LEG_H / 2.0), (0.05, 0.05, LEG_H)))
    return parts


def bounds(parts):
    """``((x0, y0, z0), (x1, y1, z1))`` over every part."""
    lo, hi = [float("inf")] * 3, [float("-inf")] * 3
    for _name, shape, c, s in parts:
        if shape == "box":
            half = (s[0] / 2.0, s[1] / 2.0, s[2] / 2.0)
        else:
            r, length, axis = s
            half = [r, r, r]
            half["XYZ".index(axis)] = length / 2.0
        for k in range(3):
            lo[k] = min(lo[k], c[k] - half[k])
            hi[k] = max(hi[k], c[k] + half[k])
    return tuple(lo), tuple(hi)
'''

RECIPE_OLD = '''    leg_h = 0.12
    guard_h = 0.12
    surface_z = h - guard_h            # cooking surface (~counter height)
    body_h = surface_z - PLATE_T - leg_h

    # cabinet body
    bm = geometry.new_bm()
    geometry.add_box(bm, (0, 0, leg_h + body_h / 2), (w, d, body_h))
    part(bm, "Grill_Body")
    cboxes.append(((-w / 2, -d / 2, 0), (w / 2, d / 2, h)))

    # cooktop plate — top surface at counter height
    bm = geometry.new_bm()
    geometry.add_box(bm, (0, 0, surface_z - PLATE_T / 2),
                     (w * 0.98, d * 0.98, PLATE_T))
    part(bm, "Grill_Cooktop", texel=2.0)

    # splash guards rise from the surface to the overall height
    gz = surface_z + guard_h / 2
    bm = geometry.new_bm()
    geometry.add_box(bm, (0, d / 2 - GUARD_T / 2, gz), (w, GUARD_T, guard_h))
    part(bm, "Grill_SplashGuard_B")
    for side, sx in (("L", -1), ("R", 1)):
        bm = geometry.new_bm()
        geometry.add_box(bm, (sx * (w / 2 - GUARD_T / 2), 0, gz),
                         (GUARD_T, d, guard_h))
        part(bm, f"Grill_SplashGuard_{side}")

    # grease trap slot along the front lip
    bm = geometry.new_bm()
    geometry.add_box(bm, (0, -d / 2 + 0.02, surface_z - PLATE_T - 0.015),
                     (w * 0.7, 0.03, 0.03))
    part(bm, "Grill_GreaseTrap")

    # control knobs on the front
    for i in range(n_knobs):
        x = (i - (n_knobs - 1) / 2) * (w * 0.14)
        bm = geometry.new_bm()
        geometry.add_cylinder(bm, (x, -d / 2 - 0.02, leg_h + body_h * 0.6),
                              0.022, 0.03, segments=12, axis="Y")
        part(bm, f"Grill_Knob_{i + 1}")

    # legs
    i = 0
    for sx in (-1, 1):
        for sy in (-1, 1):
            i += 1
            bm = geometry.new_bm()
            geometry.add_box(bm, (sx * (w / 2 - 0.06), sy * (d / 2 - 0.06),
                                  leg_h / 2), (0.05, 0.05, leg_h))
            part(bm, f"Grill_Leg_{i}")
'''
RECIPE_NEW = '''    # The parts, from core.flat_top_grill_forms: the cabinet stands
    # KNOB_PROUD shallower than the slot and set back, so the knobs end on the
    # slot's front face and the module measures exactly (w, d, h) (1.80.0).
    for name, shape, centre, size in grill_forms.layout(w, d, h, n_knobs):
        bm = geometry.new_bm()
        if shape == "box":
            geometry.add_box(bm, centre, size)
        else:
            radius, length, axis = size
            geometry.add_cylinder(bm, centre, radius, length, segments=12,
                                  axis=axis)
        part(bm, name, texel=2.0 if name == "Grill_Cooktop" else 1.0)
    cboxes.append(((-w / 2, -d / 2, 0), (w / 2, d / 2, h)))
'''

IMPORT_OLD = '''from ..bpylayer import geometry, materials

PLATE_T = 0.03
GUARD_T = 0.02
'''
IMPORT_NEW = '''from ..bpylayer import geometry, materials
from ..core import flat_top_grill_forms as grill_forms
'''

TEST_BODY = '''"""The flat-top grill measures exactly its slot (Zoo 1.80.0).

Cold runs 9132, 9179 and 9185 each logged `ZOO_PARTIAL_BUILD` for this species:
`fit_depth` 0.935 m against an exact 0.900 m, because the knobs hung 35 mm past
a cabinet built at the full depth. The layout is pure, so it is tested here
without Blender, at the genome's default and at both ends of its ranges.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from zoo_keeper.core import flat_top_grill_forms as g  # noqa: E402

DIMS = [(1.2, 0.9, 1.05), (0.9, 0.7, 0.98), (1.6, 1.0, 1.15), (1.6, 0.7, 0.98)]


def test_the_extents_are_exactly_the_slot():
    for w, d, h in DIMS:
        for knobs in (2, 3, 4):
            lo, hi = g.bounds(g.layout(w, d, h, knobs))
            for got, want in zip(lo + hi, (-w / 2, -d / 2, 0.0, w / 2, d / 2, h)):
                assert abs(got - want) < 1e-9, ((w, d, h, knobs), lo, hi)


def test_the_knobs_end_on_the_front_face():
    w, d, h = 1.2, 0.9, 1.05
    parts = g.layout(w, d, h, 3)
    knobs = [p for p in parts if p[0].startswith("Grill_Knob_")]
    body = [p for p in parts if p[0] == "Grill_Body"][0]
    assert len(knobs) == 3
    for _n, _s, c, (r, length, axis) in knobs:
        assert axis == "Y"
        assert abs((c[1] - length / 2) - (-d / 2)) < 1e-9
    face = body[2][1] - body[3][1] / 2
    assert abs(face - (-d / 2 + g.KNOB_PROUD)) < 1e-9


def test_the_recipe_builds_from_the_layout():
    """Read as source: the Blender-bound recipe draws the parts the layout
    returns and carries no geometry of its own."""
    path = os.path.join(os.path.dirname(HERE), "zoo_keeper", "recipes",
                        "flat_top_grill.py")
    src = open(path, encoding="utf-8").read()
    assert "grill_forms.layout(w, d, h, n_knobs)" in src
    assert "-d / 2 - 0.02" not in src
'''


def main():
    # The test may already stand: `--tests` writes it first, to be seen failing.
    assert not FORMS.exists()
    data = RECIPE.read_bytes()
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    for old, new in ((IMPORT_OLD, IMPORT_NEW), (RECIPE_OLD, RECIPE_NEW)):
        n = text.count(old)
        assert n == 1, f"recipe anchor matched {n} times: {old[:60]!r}"
        text = text.replace(old, new)
    FORMS.write_bytes(FORMS_BODY.encode("utf-8"))
    RECIPE.write_bytes(text.encode("utf-8"))
    print("wrote", FORMS.relative_to(ROOT), "and patched", RECIPE.relative_to(ROOT))


def tests_only():
    assert not TEST.exists()
    TEST.write_bytes(TEST_BODY.encode("utf-8"))
    print("wrote", TEST.relative_to(ROOT))


if __name__ == "__main__":
    import sys
    tests_only() if "--tests" in sys.argv else main()
