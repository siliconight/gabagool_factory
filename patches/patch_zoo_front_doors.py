"""Zoo 1.72.0: an Empty's front door -- the leaf painted in the house's finish,
named into the module as `_e<finish>` -- and its black iron security door.
Deli Counter (>= 0.182.0) authors the finish; Patina (>= 0.28.0) orders the
security door. See `zoo_front_doors/CHANGELOG_1.72.0.md`.

Anchored edits (every anchor once; refuses on a miss):
  zoo_keeper/core/kit.py             module_stem's `_e<door>`; plan_kit reads it
  zoo_keeper/core/dna.py             the plan carries it to the recipe
  zoo_keeper/recipes/_arch.py        the leaf in its finish (`doors`)
  zoo_keeper/core/dressing.py        security_door_parts, in the bars' iron
  zoo_keeper/recipes/dress_cover.py  builds it
Adds zoo_keeper/core/doors.py; copies the test; CHANGELOG and VERSION.

    python patch_zoo_front_doors.py
"""
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve().parent
ZOO = HERE.parent / "zoo"
SRC = HERE / "zoo_front_doors"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


# --- core/kit.py ------------------------------------------------------------

K_SIG_OLD = '''                material_in: str = None, pane: str = None) -> str:
    """The exact filename stem Deli Counter's resolver looks for:'''
K_SIG_NEW = '''                material_in: str = None, pane: str = None,
                door: str = None) -> str:
    """The exact filename stem Deli Counter's resolver looks for:'''

K_STEM_OLD = '''    if pane:
        base += f"_p{pane}"
'''
K_STEM_NEW = '''    if pane:
        base += f"_p{pane}"
    # AN EMPTY FRONT DOOR'S FINISH (1.72.0): `_e<finish>`, after the pane --
    # `_d` is the depth's. Two facade doorways of one size in different paints
    # are different modules. Deli Counter's `themed_tscn.module_stem` mirrors it.
    if door:
        base += f"_e{door}"
'''

K_PLAN_OLD = '''        pane = (str(s["pane"]) if typ == "window" and s.get("glazing") == "facade"
                and s.get("pane") in _panes.STATES else None)
'''
K_PLAN_NEW = '''        pane = (str(s["pane"]) if typ == "window" and s.get("glazing") == "facade"
                and s.get("pane") in _panes.STATES else None)
        # AN EMPTY FRONT DOOR'S FINISH (1.72.0, Deli Counter >= 0.182.0)
        from zoo_keeper.core import doors as _doors
        door = (str(s["door"]) if typ == "doorway" and s.get("glazing") == "facade"
                and s.get("door") in _doors.FINISHES else None)
'''

K_CALL_OLD = '''                               budget_tiles=budget, material_in=inner, pane=pane,
'''
K_CALL_NEW = '''                               budget_tiles=budget, material_in=inner, pane=pane,
                               door=door,
'''

K_KEY_OLD = '''                   _opening_key(fit.get("openings")), budget, inner, pane)
'''
K_KEY_NEW = '''                   _opening_key(fit.get("openings")), budget, inner, pane, door)
'''

K_DICT_OLD = '''                    "pane": pane,
'''
K_DICT_NEW = '''                    "pane": pane,
                    "door": door,
'''

# --- core/dna.py ------------------------------------------------------------

DNA_OLD = '''    if module.get("pane"):
        plan["pane"] = str(module["pane"])
'''
DNA_NEW = '''    if module.get("pane"):
        plan["pane"] = str(module["pane"])
    # An Empty front door's finish (1.72.0): `_arch.build_slab` paints the leaf
    if module.get("door"):
        plan["door"] = str(module["door"])
'''

# --- recipes/_arch.py -------------------------------------------------------

A_IMPORT_OLD = '''from ..core import arch, partnames, window_panes
'''
A_IMPORT_NEW = '''from ..core import arch, doors, partnames, window_panes
'''

A_COMMENT_OLD = '''#: Navy, one of the rowhouse comp's three door colours
#: (`docs/reference/EMPTIES_COMPS.md`); per-house colour is instance data,
#: not a material per colour, when it comes.
'''
A_COMMENT_NEW = '''#: Navy, one of the rowhouse comp's three door colours
#: (`docs/reference/EMPTIES_COMPS.md`).
#:
#: CORRECTED (1.72.0): that navy never showed. It is the FLAT colour, and a
#: skinned `wood_panel` takes no tint, so every Empty door rendered brown. A
#: house's finish now rides in the module (`doors.FINISHES`, `_e<finish>`),
#: painted metal for the paints. It costs no draw: a doorway module is drawn
#: once per placement either way. This colour stays the unpainted leaf's.
'''

A_LEAF_OLD = '''        materials.assign([leaf], materials.make_material(
            "M_Door_wood_panel", plan.get("door_color", FACADE_DOOR_COLOR), "wood_panel"))
'''
A_LEAF_NEW = '''        # in its house's finish (1.72.0, Deli Counter >= 0.182.0); no finish
        # is the stained `wood_panel` leaf every Empty door had
        name, colour, kind = doors.leaf_material(
            plan.get("door"), plan.get("door_color", FACADE_DOOR_COLOR))
        materials.assign([leaf], materials.make_material(name, colour, kind))
'''

# --- core/dressing.py -------------------------------------------------------

D_IRON_OLD = '''IRON_COVERS = ("window_bars",)
'''
D_IRON_NEW = '''IRON_COVERS = ("window_bars", "security_door")
'''

D_PARTS_OLD = '''    return [((0.0, 0.001 + SILL_PROUD / 2.0, -SILL_H / 2.0), (w, SILL_PROUD, SILL_H))]
'''
D_PARTS_NEW = '''    return [((0.0, 0.001 + SILL_PROUD / 2.0, -SILL_H / 2.0), (w, SILL_PROUD, SILL_H))]


#: AN EMPTY'S IRON SECURITY DOOR (1.72.0). The walker's South Philly
#: photograph: "a black iron security door with a grille". Hung in the
#: doorway's reveal: from 6 cm to 2 cm behind the wall face, so 2 cm in front
#: of the leaf `_arch` sets back 8 cm. Two stiles and three rails -- top,
#: bottom and the lock rail at handle height -- with uprights between, and a
#: lock box on the lock rail. In the bars' black iron, so on a side with bars
#: it merges into their mesh.
SEC_Y0, SEC_Y1 = -0.06, -0.02
SEC_STILE = SEC_RAIL = 0.05
SEC_BAR = 0.016
SEC_PITCH = 0.11
SEC_LOCK_Z = 1.0


def security_door_parts(opening_w: float, opening_h: float):
    """An iron security door's parts (1.72.0), as (center, size) boxes in
    cover-local space with z about the opening's centre, where Patina orders
    it: 5 mm clear of the jambs and head, the threshold at the bottom."""
    ow, oh = float(opening_w), float(opening_h)
    w, h = ow - 0.01, oh - 0.01
    y, d = (SEC_Y0 + SEC_Y1) / 2.0, SEC_Y1 - SEC_Y0
    zb = -h / 2.0
    parts = [((sx * (w / 2.0 - SEC_STILE / 2.0), y, 0.0), (SEC_STILE, d, h))
             for sx in (-1.0, 1.0)]
    inner = w - 2.0 * SEC_STILE
    for z in (zb + SEC_RAIL / 2.0, zb + h - SEC_RAIL / 2.0, zb + SEC_LOCK_Z):
        parts.append(((0.0, y, z), (inner + 0.002, d, SEC_RAIL)))
    n = max(2, int(round(inner / SEC_PITCH)) - 1)
    pitch = inner / (n + 1)
    for j in range(1, n + 1):
        parts.append(((-inner / 2.0 + j * pitch, y, 0.0), (SEC_BAR, SEC_BAR, h - 2.0 * SEC_RAIL + 0.002)))
    parts.append(((inner / 2.0 - 0.05, SEC_Y1 + 0.0115, zb + SEC_LOCK_Z + 0.07), (0.07, 0.024, 0.14)))
    return parts
'''

# --- recipes/dress_cover.py -------------------------------------------------

R_IMPORT_OLD = '''from ..core.dressing import (ac_parts, bar_parts, downspout_parts, frame_strips,
                             gutter_parts, lintel_parts, sill_parts, strip_size,
                             uv_offset)
'''
R_IMPORT_NEW = '''from ..core.dressing import (ac_parts, bar_parts, downspout_parts, frame_strips,
                             gutter_parts, lintel_parts, security_door_parts,
                             sill_parts, strip_size, uv_offset)
'''

R_BRANCH_OLD = '''    elif cover in ("ac_unit", "window_bars", "lintel", "window_sill"):
'''
R_BRANCH_NEW = '''    elif cover in ("ac_unit", "window_bars", "lintel", "window_sill", "security_door"):
'''
R_ELSE_OLD = '''        elif cover == "lintel":
            parts = lintel_parts(ow)
        else:
            parts = sill_parts(ow)
'''
R_ELSE_NEW = '''        elif cover == "lintel":
            parts = lintel_parts(ow)
        elif cover == "security_door":
            parts = security_door_parts(ow, oh)
        else:
            parts = sill_parts(ow)
'''
R_DOC_OLD = '''* ``window_sill``  — an Empty's stone sill hung below a window's sill line
  (1.71.0; ``core.dressing.sill_parts``).
'''
R_DOC_NEW = '''* ``window_sill``  — an Empty's stone sill hung below a window's sill line
  (1.71.0; ``core.dressing.sill_parts``).
* ``security_door`` — an Empty's black iron security door in its doorway's
  reveal (1.72.0; ``core.dressing.security_door_parts``).
'''


def main():
    assert (ZOO / "VERSION").read_text(encoding="utf-8").strip() == "1.71.0"
    assert not (ZOO / "zoo_keeper" / "core" / "doors.py").exists()
    shutil.copyfile(SRC / "doors.py", ZOO / "zoo_keeper" / "core" / "doors.py")
    _edit(ZOO / "zoo_keeper" / "core" / "kit.py",
          [(K_SIG_OLD, K_SIG_NEW), (K_STEM_OLD, K_STEM_NEW), (K_PLAN_OLD, K_PLAN_NEW),
           (K_CALL_OLD, K_CALL_NEW), (K_KEY_OLD, K_KEY_NEW), (K_DICT_OLD, K_DICT_NEW)])
    _edit(ZOO / "zoo_keeper" / "core" / "dna.py", [(DNA_OLD, DNA_NEW)])
    _edit(ZOO / "zoo_keeper" / "recipes" / "_arch.py",
          [(A_IMPORT_OLD, A_IMPORT_NEW), (A_COMMENT_OLD, A_COMMENT_NEW), (A_LEAF_OLD, A_LEAF_NEW)])
    _edit(ZOO / "zoo_keeper" / "core" / "dressing.py", [(D_IRON_OLD, D_IRON_NEW), (D_PARTS_OLD, D_PARTS_NEW)])
    _edit(ZOO / "zoo_keeper" / "recipes" / "dress_cover.py",
          [(R_IMPORT_OLD, R_IMPORT_NEW), (R_BRANCH_OLD, R_BRANCH_NEW), (R_ELSE_OLD, R_ELSE_NEW),
           (R_DOC_OLD, R_DOC_NEW)])
    shutil.copyfile(SRC / "test_front_doors.py", ZOO / "tests" / "test_front_doors.py")
    ch = ZOO / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    ch.write_text((SRC / "CHANGELOG_1.72.0.md").read_text(encoding="utf-8").rstrip("\n") + "\n\n" + s,
                  encoding="utf-8", newline="\n")
    (ZOO / "VERSION").write_text("1.72.0", encoding="utf-8", newline="\n")
    print("applied Zoo 1.72.0")


if __name__ == "__main__":
    main()
