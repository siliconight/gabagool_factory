"""Deli Counter 0.182.0: an Empty's front door -- a painted finish per house and,
on two, a black iron security door -- authored on the spec, carried on the
front door's slot, and named into its module as `_e<finish>`. See
`dc_front_doors/CHANGELOG_0.182.0.md`.

Anchored edits (every anchor once; refuses on a miss):
  empty_panes.py           DOOR_FINISHES, door()
  deli_counter.py          the hole carries its opening's tag; a facade
                           doorway's slot takes door()
  themed_tscn.py           module_stem's `_e<door>`, as Zoo 1.72.0 writes it
  spec_types.py            door_finish, security_door
  schema/level.schema.json the same two
  presets.py               empty_rowhome(door_finish=, security_door=); the family
Rewrites the six rowhome specs from the preset; copies the test; CHANGELOG and
VERSION. Rebuild after: `python build.py --all`.

    python patch_dc_front_doors.py
"""
import importlib
import json
import pathlib
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
DC = HERE.parent / "deli_counter"
SRC = HERE / "dc_front_doors"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


PANES_OLD = '''    rate = AC_GROUND if int(story or 0) <= 0 else AC_UPPER
    if _crc("ac:%s:%s:%s" % (building, seed, slot_id)) % 100 < rate:
        return {"ac": True}
    return {}
'''
PANES_NEW = '''    rate = AC_GROUND if int(story or 0) <= 0 else AC_UPPER
    if _crc("ac:%s:%s:%s" % (building, seed, slot_id)) % 100 < rate:
        return {"ac": True}
    return {}


#: AN EMPTY'S FRONT DOOR (0.182.0): the finishes Zoo (>= 1.72.0) paints a
#: facade leaf in, in Zoo's order (`zoo_keeper.core.doors.FINISHES`, pinned by
#: `test_front_doors.py`). The comp's row paints its doors house by house;
#: `stained` is the wood every Empty door wore before this.
DOOR_FINISHES = ("navy", "oxblood", "green", "black", "white", "stained")


def door(tag, finish=None, security=False):
    """What an Empty's doorway carries, as slot fields.

    On the FRONT door (the opening the preset tagged ``front_door``) the
    house's authored finish and its iron security door; on the back door, or
    a house that authored neither, nothing -- it keeps the leaf every Empty
    door had. AUTHORED, NOT DRAWN, as `vacant` is: a seeded draw over the six
    rowhomes gave three finishes, two of them twice, and no iron door. A
    finish outside `DOOR_FINISHES` is refused rather than dropped."""
    if tag != "front_door":
        return {}
    out = {}
    if finish is not None:
        if finish not in DOOR_FINISHES:
            raise ValueError("door finish %r is not one of %s" % (finish, DOOR_FINISHES))
        out["door"] = finish
    if security:
        out["security_door"] = True
    return out
'''

HOLE_OLD = '''        hole = dict(u=u, v=v, w=r["width"], h=r["height"], kind=op.kind,
                    sill=r["sill"], face=getattr(op, "face", None),
                    interactive=self._machine_for(op, wall_name, story))
'''
HOLE_NEW = '''        hole = dict(u=u, v=v, w=r["width"], h=r["height"], kind=op.kind,
                    sill=r["sill"], face=getattr(op, "face", None),
                    interactive=self._machine_for(op, wall_name, story),
                    # which opening this is (0.182.0): an Empty's front door
                    # is the one its preset tagged `front_door`
                    tag=getattr(op, "tag", None))
'''

SLOT_OLD = '''                slot.update(empty_panes.fixtures(
                    slot["pane"], self.s.name, self.s.seed, vb, story))
        self.slots.append(slot)
'''
SLOT_NEW = '''                slot.update(empty_panes.fixtures(
                    slot["pane"], self.s.name, self.s.seed, vb, story))
            # AND ITS FRONT DOOR (0.182.0): the house's painted finish and its
            # iron security door, authored on the spec. Zoo (>= 1.72.0) paints
            # the leaf; Patina (>= 0.28.0) orders the security door.
            elif role == "doorway":
                slot.update(empty_panes.door(
                    h.get("tag"), getattr(self.s, "door_finish", None),
                    getattr(self.s, "security_door", False)))
        self.slots.append(slot)
'''

SIG_OLD = '''                material_in: str = None, pane: str = None) -> str:
    """``<type>[_<species>]'''
SIG_NEW = '''                material_in: str = None, pane: str = None,
                door: str = None) -> str:
    """``<type>[_<species>]'''

STEM_OLD = '''    # A painted pane's state (0.179.0), as `kit.module_stem` writes it
    if pane:
        base += f"_p{pane}"
'''
STEM_NEW = '''    # A painted pane's state (0.179.0), as `kit.module_stem` writes it
    if pane:
        base += f"_p{pane}"
    # An Empty front door's finish (0.182.0), as `kit.module_stem` writes it
    # (Zoo 1.72.0): `_e`, because `_d` is the depth's
    if door:
        base += f"_e{door}"
'''

RESOLVE_OLD = '''    pane = (slot.get("pane") if typ == "window" and slot.get("glazing") == "facade"
            and slot.get("pane") in empty_panes.STATES else None)
    stem = module_stem(typ, theme, eff_style, width_cm,
                       state if state else _default_stem_state(slot),
                       depth_cm, vtag, otag, height_cm, species=species,
                       material=material, glazing=glazing, budget_tiles=budget,
                       material_in=inner, pane=pane, **dress)
'''
RESOLVE_NEW = '''    pane = (slot.get("pane") if typ == "window" and slot.get("glazing") == "facade"
            and slot.get("pane") in empty_panes.STATES else None)
    door = (slot.get("door") if typ == "doorway" and slot.get("glazing") == "facade"
            and slot.get("door") in empty_panes.DOOR_FINISHES else None)
    stem = module_stem(typ, theme, eff_style, width_cm,
                       state if state else _default_stem_state(slot),
                       depth_cm, vtag, otag, height_cm, species=species,
                       material=material, glazing=glazing, budget_tiles=budget,
                       material_in=inner, pane=pane, door=door, **dress)
'''

SPEC_OLD = '''    # wall material -- not drawn, so a street is not left without one.
    vacant: bool = False
'''
SPEC_NEW = '''    # wall material -- not drawn, so a street is not left without one.
    vacant: bool = False
    # AN EMPTY'S FRONT DOOR (0.182.0): its painted finish (one of
    # `empty_panes.DOOR_FINISHES`) and whether a black iron security door
    # hangs in front of it. Authored per house like `vacant`: a drawn mix left
    # the six rowhomes three finishes and no iron door.
    door_finish: Optional[str] = None
    security_door: bool = False
'''

SCHEMA_OLD = '''    "vacant": {
      "type": "boolean",
      "description": "a vacant facade shell: every window painted boarded (empty_panes, 0.179.0)"
    },
'''
SCHEMA_NEW = '''    "vacant": {
      "type": "boolean",
      "description": "a vacant facade shell: every window painted boarded (empty_panes, 0.179.0)"
    },
    "door_finish": {
      "type": "string",
      "enum": ["navy", "oxblood", "green", "black", "white", "stained"],
      "description": "an Empty's front-door finish (empty_panes.DOOR_FINISHES, 0.182.0)"
    },
    "security_door": {
      "type": "boolean",
      "description": "a black iron security door in front of an Empty's front door (0.182.0)"
    },
'''

PRESET_SIG_OLD = '''                  scale_ref: bool = False, vacant: bool = False) -> dict:
'''
PRESET_SIG_NEW = '''                  scale_ref: bool = False, vacant: bool = False,
                  door_finish: str = None, security_door: bool = False) -> dict:
'''
PRESET_BODY_OLD = '''    if vacant:
        s["vacant"] = True
    return s
'''
PRESET_BODY_NEW = '''    if vacant:
        s["vacant"] = True
    # the front door (0.182.0): its finish and its iron security door, absent
    # unless asked, as `vacant` is. NAMED `door_finish`, not `door`: `door` is
    # this function's front-door POSITION, a few lines up, and a parameter of
    # that name was shadowed by it -- the first build of this patch wrote the
    # position, -0.22, as the finish, and `empty_panes.door` refused it.
    if door_finish:
        s["door_finish"] = door_finish
    if security_door:
        s["security_door"] = True
    return s
'''
FAMILY_OLD = '''EMPTY_ROWHOMES = {
    "gs_empty_rowhome_a": dict(width=6.0, floors=3, wall="brick", door_side="W", cornice=0.8, seed=1911),
    "gs_empty_rowhome_b": dict(width=5.5, floors=3, wall="siding", door_side="E", cornice=0.6, seed=1912),
    "gs_empty_rowhome_c": dict(width=6.5, floors=3, wall="brick", door_side="E", cornice=1.0, seed=1913),
    "gs_empty_rowhome_d": dict(width=6.0, floors=2, wall="stone_ext", door_side="W", cornice=0.6, seed=1914),
    # the vacant one (0.179.0): painted block, boarded -- the family's
    # "boarded variant", one in six as a 1990s Delco street has a few
    "gs_empty_rowhome_e": dict(width=5.5, floors=3, wall="paint_block", door_side="W", cornice=0.9, seed=1915,
                               vacant=True),
    "gs_empty_rowhome_f": dict(width=6.0, floors=3, wall="brick", door_side="E", cornice=0.7, seed=1916),
}
'''
FAMILY_NEW = '''EMPTY_ROWHOMES = {
    # and its front door (0.182.0): a different paint on every house, as the
    # comp's row has, and a black iron security door on two
    "gs_empty_rowhome_a": dict(width=6.0, floors=3, wall="brick", door_side="W", cornice=0.8, seed=1911,
                               door_finish="navy", security_door=True),
    "gs_empty_rowhome_b": dict(width=5.5, floors=3, wall="siding", door_side="E", cornice=0.6, seed=1912,
                               door_finish="white"),
    "gs_empty_rowhome_c": dict(width=6.5, floors=3, wall="brick", door_side="E", cornice=1.0, seed=1913,
                               door_finish="oxblood"),
    "gs_empty_rowhome_d": dict(width=6.0, floors=2, wall="stone_ext", door_side="W", cornice=0.6, seed=1914,
                               door_finish="green"),
    # the vacant one (0.179.0): painted block, boarded -- the family's
    # "boarded variant", one in six as a 1990s Delco street has a few; its
    # door black and secured
    "gs_empty_rowhome_e": dict(width=5.5, floors=3, wall="paint_block", door_side="W", cornice=0.9, seed=1915,
                               vacant=True, door_finish="black", security_door=True),
    "gs_empty_rowhome_f": dict(width=6.0, floors=3, wall="brick", door_side="E", cornice=0.7, seed=1916,
                               door_finish="stained"),
}
'''


def main():
    assert (DC / "VERSION").read_text(encoding="utf-8").strip() == "Deli Counter 0.181.0"
    _edit(DC / "empty_panes.py", [(PANES_OLD, PANES_NEW)])
    _edit(DC / "deli_counter.py", [(HOLE_OLD, HOLE_NEW), (SLOT_OLD, SLOT_NEW)])
    _edit(DC / "themed_tscn.py", [(SIG_OLD, SIG_NEW), (STEM_OLD, STEM_NEW), (RESOLVE_OLD, RESOLVE_NEW)])
    _edit(DC / "spec_types.py", [(SPEC_OLD, SPEC_NEW)])
    _edit(DC / "schema" / "level.schema.json", [(SCHEMA_OLD, SCHEMA_NEW)])
    _edit(DC / "presets.py", [(PRESET_SIG_OLD, PRESET_SIG_NEW), (PRESET_BODY_OLD, PRESET_BODY_NEW),
                              (FAMILY_OLD, FAMILY_NEW)])
    sys.path.insert(0, str(DC))
    presets = importlib.import_module("presets")
    for name, args in presets.EMPTY_ROWHOMES.items():
        with open(DC / "specs" / f"{name}.json", "w", encoding="utf-8", newline="\n") as f:
            json.dump(presets.empty_rowhome(name=name, **args), f, indent=2)
    shutil.copyfile(SRC / "test_front_doors.py", DC / "test_front_doors.py")
    ch = DC / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    ch.write_text((SRC / "CHANGELOG_0.182.0.md").read_text(encoding="utf-8").rstrip("\n") + "\n\n" + s,
                  encoding="utf-8", newline="\n")
    (DC / "VERSION").write_text("Deli Counter 0.182.0", encoding="utf-8", newline="\n")
    print("applied Deli Counter 0.182.0 -- now rebuild: python build.py --all")


if __name__ == "__main__":
    main()
