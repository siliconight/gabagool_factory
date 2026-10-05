"""Deli Counter 0.185.0: an Empty's TV antenna and satellite dish -- authored per
house on the spec, carried on the roof slot with the facing of the house's
front. See `dc_roof_fixtures/CHANGELOG_0.185.0.md`.

Anchored edits (every anchor once; refuses on a miss):
  roofs.py                 front_facing, roof_fixtures; the footprint roof
                           slot takes them
  spec_types.py            roof_antenna, roof_dish
  schema/level.schema.json the same two
  presets.py               empty_rowhome(antenna=, dish=); the family's rows
Rewrites the twelve rowhome specs from the preset; copies the test; CHANGELOG
and VERSION. Rebuild after: `python build.py --all` (presets.py and roofs.py
are geometry sources, so every shell goes stale).

    python patch_dc_roof_fixtures.py
"""
import importlib
import json
import pathlib
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
DC = HERE.parent / "deli_counter"
SRC = HERE / "dc_roof_fixtures"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


FUNCS_ANCHOR = '''

def roof_slots(spec, story, cz, ft):
'''
FUNCS_NEW = '''

def front_facing(spec):
    """The facing of the exterior wall that holds the spec's `front_door`
    opening (`presets.empty_rowhome` tags it), or None."""
    for w in getattr(spec, "ext_walls", None) or []:
        if any(getattr(o, "tag", None) == "front_door" for o in w.openings):
            return w.wall
    return None


def roof_fixtures(spec) -> dict:
    """AN EMPTY'S ROOF FIXTURES (0.185.0): ``antenna`` / ``dish`` for its roof
    slot, with ``front`` -- the facing of the wall holding its front door --
    which Patina (>= 0.29.0) sets them back from and Zoo (>= 1.74.0) builds.
    Authored per house (`roof_antenna`, `roof_dish`), as its door is.

    Empty for a spec that asks for neither, so every other roof slot is
    unchanged. Asked for on a spec that is not a facade, or on one with no
    front door, it RAISES: an Empty's roof is never reached, and an antenna a
    body walked through on a real rooftop would lie about it; with no front
    there is nothing to set it back from. A fixture that quietly did not
    appear is a check that cannot fail.
    """
    out = {}
    if getattr(spec, "roof_antenna", False):
        out["antenna"] = True
    if getattr(spec, "roof_dish", False):
        out["dish"] = True
    if not out:
        return out
    name = getattr(spec, "name", "?")
    if not getattr(spec, "facade", False):
        raise ValueError("%s: roof fixtures %s are an Empty's, and this spec is not a facade"
                         % (name, sorted(out)))
    front = front_facing(spec)
    if front is None:
        raise ValueError("%s: roof fixtures %s and no front_door opening to set them back from"
                         % (name, sorted(out)))
    out["front"] = front
    return out


def roof_slots(spec, story, cz, ft):
'''

SLOT_OLD = '''    _rx0, _ry0, _rx1, _ry1 = _sb.slab_extent(spec, story)
    return [_slot("roof_footprint", story, (_rx0 + _rx1) / 2.0,
                  (_ry0 + _ry1) / 2.0, cz,
                  _rx1 - _rx0, _ry1 - _ry0, ft,
                  style=style, material=mat,
                  voids=room_voids(spec, None, story, 0.0, 0.0,
                                   _rx1 - _rx0, _ry1 - _ry0))]
'''
SLOT_NEW = '''    _rx0, _ry0, _rx1, _ry1 = _sb.slab_extent(spec, story)
    slot = _slot("roof_footprint", story, (_rx0 + _rx1) / 2.0,
                 (_ry0 + _ry1) / 2.0, cz,
                 _rx1 - _rx0, _ry1 - _ry0, ft,
                 style=style, material=mat,
                 voids=room_voids(spec, None, story, 0.0, 0.0,
                                  _rx1 - _rx0, _ry1 - _ry0))
    # an Empty's TV antenna and satellite dish ride on its roof (0.185.0)
    slot.update(roof_fixtures(spec))
    return [slot]
'''

SPEC_OLD = '''    # hangs in front of it. Authored per house like `vacant`: a drawn mix left
    # the six rowhomes three finishes and no iron door.
    door_finish: Optional[str] = None
    security_door: bool = False
'''
SPEC_NEW = '''    # hangs in front of it. Authored per house like `vacant`: a drawn mix left
    # the six rowhomes three finishes and no iron door.
    door_finish: Optional[str] = None
    security_door: bool = False
    # AN EMPTY'S ROOF (0.185.0): a TV antenna, and the odd satellite dish,
    # authored per house as its door is. `roofs.roof_fixtures` puts them on
    # the roof slot with the facing of its front.
    roof_antenna: bool = False
    roof_dish: bool = False
'''

SCHEMA_OLD = '''    "security_door": {
      "type": "boolean",
      "description": "a black iron security door in front of an Empty's front door (0.182.0)"
    },
'''
SCHEMA_NEW = '''    "security_door": {
      "type": "boolean",
      "description": "a black iron security door in front of an Empty's front door (0.182.0)"
    },
    "roof_antenna": {
      "type": "boolean",
      "description": "a TV antenna on an Empty's roof (roofs.roof_fixtures, 0.185.0)"
    },
    "roof_dish": {
      "type": "boolean",
      "description": "a satellite dish on an Empty's roof (roofs.roof_fixtures, 0.185.0)"
    },
'''

SIG_OLD = '''                  door_finish: str = None, security_door: bool = False) -> dict:
'''
SIG_NEW = '''                  door_finish: str = None, security_door: bool = False,
                  antenna: bool = False, dish: bool = False) -> dict:
'''

BODY_OLD = '''    if security_door:
        s["security_door"] = True
    return s
'''
BODY_NEW = '''    if security_door:
        s["security_door"] = True
    # and its roof (0.185.0): a TV antenna, and the odd satellite dish, absent
    # unless asked as the door's are
    if antenna:
        s["roof_antenna"] = True
    if dish:
        s["roof_dish"] = True
    return s
'''

COMMENT_OLD = '''    # and its front door (0.182.0): a different paint on every house, as the
    # comp's row has, and a black iron security door on two
'''
COMMENT_NEW = '''    # and its front door (0.182.0): a different paint on every house, as the
    # comp's row has, and a black iron security door on two
    # and its roof (0.185.0): a TV antenna on eight of the twelve, as a 1990s
    # Philadelphia street has -- cable came late to the city -- and the odd
    # satellite dish on two; c, f and h have neither
'''

_ROW = '''    "gs_empty_rowhome_%s": dict(%s
                               %s),
'''
#: house -> (its first line's arguments, its second line's arguments, what it gains)
ROWS = {
    "a": ('width=6.0, floors=3, wall="brick_orange", door_side="W", cornice=0.8, seed=1911,',
          'door_finish="navy", security_door=True', 'antenna=True'),
    "b": ('width=5.5, floors=3, wall="siding", door_side="E", cornice=0.6, seed=1912,',
          'door_finish="white"', 'antenna=True, dish=True'),
    "d": ('width=6.0, floors=2, wall="stone_ext", door_side="W", cornice=0.6, seed=1914,',
          'door_finish="green"', 'antenna=True'),
    "e": ('width=5.5, floors=3, wall="paint_block", door_side="W", cornice=0.9, seed=1915,',
          'vacant=True, door_finish="black", security_door=True', 'antenna=True'),
    "g": ('width=5.8, floors=3, wall="brick_brown", door_side="W", cornice=0.9, seed=1917,',
          'door_finish="green"', 'antenna=True'),
    "i": ('width=6.1, floors=3, wall="siding", door_side="W", cornice=0.8, seed=1919,',
          'door_finish="oxblood"', 'antenna=True'),
    "j": ('width=6.2, floors=3, wall="brick", door_side="W", cornice=0.6, seed=1920,',
          'door_finish="black"', 'antenna=True'),
    "k": ('width=5.6, floors=3, wall="paint_block", door_side="E", cornice=1.0, seed=1921,',
          'door_finish="navy"', 'dish=True'),
    "l": ('width=6.4, floors=2, wall="stone_ext", door_side="E", cornice=0.8, seed=1922,',
          'door_finish="stained", security_door=True', 'antenna=True'),
}
ROW_EDITS = [(_ROW % (h, a, b), _ROW % (h, a, b + ", " + gain)) for h, (a, b, gain) in ROWS.items()]


def main():
    assert (DC / "VERSION").read_text(encoding="utf-8").strip() == "Deli Counter 0.184.0"
    _edit(DC / "roofs.py", [(FUNCS_ANCHOR, FUNCS_NEW), (SLOT_OLD, SLOT_NEW)])
    _edit(DC / "spec_types.py", [(SPEC_OLD, SPEC_NEW)])
    _edit(DC / "schema" / "level.schema.json", [(SCHEMA_OLD, SCHEMA_NEW)])
    json.loads((DC / "schema" / "level.schema.json").read_text(encoding="utf-8"))   # still JSON
    _edit(DC / "presets.py", [(SIG_OLD, SIG_NEW), (BODY_OLD, BODY_NEW), (COMMENT_OLD, COMMENT_NEW)]
          + ROW_EDITS)
    sys.path.insert(0, str(DC))
    presets = importlib.import_module("presets")
    assert len(presets.EMPTY_ROWHOMES) == 12
    assert sum(1 for a in presets.EMPTY_ROWHOMES.values() if a.get("antenna")) == 8
    for name, args in presets.EMPTY_ROWHOMES.items():
        with open(DC / "specs" / f"{name}.json", "w", encoding="utf-8", newline="\n") as f:
            json.dump(presets.empty_rowhome(name=name, **args), f, indent=2)
    shutil.copyfile(SRC / "test_roof_fixtures.py", DC / "test_roof_fixtures.py")
    ch = DC / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    ch.write_text((SRC / "CHANGELOG_0.185.0.md").read_text(encoding="utf-8").rstrip("\n") + "\n\n" + s,
                  encoding="utf-8", newline="\n")
    (DC / "VERSION").write_text("Deli Counter 0.185.0", encoding="utf-8", newline="\n")
    print("applied Deli Counter 0.185.0 -- now rebuild: python build.py --all")


if __name__ == "__main__":
    main()
