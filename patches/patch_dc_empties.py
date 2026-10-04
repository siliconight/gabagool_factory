"""Deli Counter 0.174.0: Empties with real fronts -- the rowhome family.

Roadmap 106. The walker, 2026-10-04, shown this repo's two Empties (sealed
boxes, no openings) standing in a row: "that just looks like a continuous
concrete wall". Comps and the agreed families: the factory root's
`docs/reference/EMPTIES_COMPS.md` (1990s Delco/Philly).

Anchored edits (every anchor once; refuses on a miss):
  deli_counter.py  an Empty's doors do not carve its wall; an Empty records
                   no gameplay from its openings
  presets.py       `empty_rowhome`, `EMPTY_ROWHOMES`, the registry entry
Writes `specs/gs_empty_rowhome_[a-f].json` from the preset, copies
`dc_empties/test_empties.py`. CHANGELOG and VERSION from
`dc_empties/CHANGELOG_0.174.0.md`. The library build of the six specs is a
separate step (`python build.py specs/<name>.json`).

    python patch_dc_empties.py
"""
import importlib
import json
import pathlib
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
DC = HERE.parent / "deli_counter"
SRC = HERE / "dc_empties"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


PRESET = '''

# ---------------------------------------------------------------------------
# EMPTIES (0.174.0) -- non-enterable shells with real fronts (roadmap 106)
# ---------------------------------------------------------------------------
#
# The walker, 2026-10-04, shown `facade_rowhome` and `facade_storefront` (no
# openings, every slot a wall) standing in a row: "that just looks like a
# continuous concrete wall". The comps are read off in the factory root's
# `docs/reference/EMPTIES_COMPS.md`: a Philadelphia rowhouse street, and
# industrial lofts, all in their 1990s state. A terrace reads as houses
# because EACH HOUSE DIFFERS -- width, storeys, wall, cornice height, which
# side the door is on -- so the family below is a table of houses, not one
# house built six times.

def empty_rowhome(name: str = "empty_rowhome", width: float = 6.0,
                  floors: int = 3, wall: str = "brick", door_side: str = "W",
                  cornice: float = 0.8, seed: int = 1911,
                  scale_ref: bool = False) -> dict:
    """A Philadelphia / Delco rowhouse Empty. Two window bays wide; a door in
    one bay and a window in the other at street level, two windows on every
    storey above, stacked on the same bays; a back door and windows behind.
    The side walls are left unlisted, so `auto_exterior` seals them: they are
    party walls. Non-enterable: its door does not carve its wall and its
    openings carry no gameplay (deli_counter.py, 0.174.0)."""
    sh = 3.1
    depth = 12.0
    s = _facade(name, float(width), depth, int(floors), sh, wall, [
        {"id": wall, "acoustic": "Concrete", "absorption": 0.7, "damping": 0.6},
        {"id": "glass", "acoustic": "Glass", "absorption": 0.1, "damping": 0.1},
        {"id": "wood", "acoustic": "Wood", "absorption": 0.5, "damping": 0.45},
    ], parapet_h=float(cornice), seed=int(seed))
    bay = 0.22 if width >= 6.0 else 0.2
    door = -bay if door_side == "W" else bay
    win = {"kind": "window", "width": 0.95, "height": 1.6, "sill": 0.85,
           "material": "glass"}
    ext = []
    for st in range(int(floors)):
        if st == 0:
            front = [{"kind": "door", "pos": door, "width": 1.0, "height": 2.3,
                      "tag": "front_door", "material": "wood"},
                     dict(win, pos=-door)]
            back = [{"kind": "door", "pos": door, "width": 0.95, "height": 2.2,
                     "tag": "back_door", "material": "wood"}]
        else:
            front = [dict(win, pos=-bay), dict(win, pos=bay)]
            back = [dict(win, pos=-door)]
        ext.append({"wall": "S", "story": st, "material": wall, "openings": front})
        ext.append({"wall": "N", "story": st, "material": wall, "openings": back})
    s["ext_walls"] = ext
    s["scale_ref"] = bool(scale_ref)
    return s


#: The rowhome Empties built into the library, one row a house: width (m),
#: storeys, wall, door side, cornice height (m), seed. Brick dominates as it
#: does on the comp's street; siding and Formstone (`stone_ext`) are the
#: 1990s covering one house in a row would wear; painted block is the
#: painted front. Widths 5.5-6.5 m are the comp's 18-21 ft houses.
EMPTY_ROWHOMES = {
    "gs_empty_rowhome_a": dict(width=6.0, floors=3, wall="brick", door_side="W", cornice=0.8, seed=1911),
    "gs_empty_rowhome_b": dict(width=5.5, floors=3, wall="siding", door_side="E", cornice=0.6, seed=1912),
    "gs_empty_rowhome_c": dict(width=6.5, floors=3, wall="brick", door_side="E", cornice=1.0, seed=1913),
    "gs_empty_rowhome_d": dict(width=6.0, floors=2, wall="stone_ext", door_side="W", cornice=0.6, seed=1914),
    "gs_empty_rowhome_e": dict(width=5.5, floors=3, wall="paint_block", door_side="W", cornice=0.9, seed=1915),
    "gs_empty_rowhome_f": dict(width=6.0, floors=3, wall="brick", door_side="E", cornice=0.7, seed=1916),
}
'''


def main():
    v = (DC / "VERSION").read_text(encoding="utf-8").strip()
    assert v == "Deli Counter 0.173.0", v
    assert not (DC / "specs" / "gs_empty_rowhome_a.json").exists(), "already applied"
    _edit(DC / "deli_counter.py", [
        ('        carve = sorted((h for h in holes\n'
         '                        if h["kind"] in ("door", "garage", "breach", "vault")),\n'
         '                       key=lambda h: h["u"])\n',
         '        carve = sorted((h for h in holes\n'
         '                        if h["kind"] in ("door", "garage", "breach", "vault")),\n'
         '                       key=lambda h: h["u"])\n'
         '        # AN EMPTY\'S DOOR IS SOLID (0.174.0): it is drawn, and behind it\n'
         '        # there is no interior, no navmesh and nothing to reach, so the\n'
         '        # wall it stands in stays one box (roadmap 106).\n'
         '        if getattr(self.s, "facade", False):\n'
         '            carve = []\n'),
        ('        opening -- see interactives.py + docs/INTERACTIVES.md."""\n'
         '        H = self.s.story_height\n',
         '        opening -- see interactives.py + docs/INTERACTIVES.md."""\n'
         '        # AN EMPTY CARRIES NO GAMEPLAY (0.174.0): no opening record, no\n'
         '        # socket marker, no interactive -- its door opens onto nothing\n'
         '        # (roadmap 106).\n'
         '        if getattr(self.s, "facade", False):\n'
         '            return\n'
         '        H = self.s.story_height\n'),
    ])
    _edit(DC / "presets.py", [
        ('\n\n# ---------------------------------------------------------------------------\n'
         '# REGISTRY\n',
         PRESET + '\n\n# ---------------------------------------------------------------------------\n'
         '# REGISTRY\n'),
        ('    "facade_storefront": facade_storefront,\n',
         '    "facade_storefront": facade_storefront,\n'
         '    "empty_rowhome": empty_rowhome,\n'),
    ])
    sys.path.insert(0, str(DC))
    presets = importlib.import_module("presets")
    for name, args in presets.EMPTY_ROWHOMES.items():
        spec = presets.empty_rowhome(name=name, **args)
        with open(DC / "specs" / f"{name}.json", "w", encoding="utf-8", newline="\n") as f:
            json.dump(spec, f, indent=2)
    shutil.copyfile(SRC / "test_empties.py", DC / "test_empties.py")
    ch = DC / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    assert s.startswith("## [0.173.0]"), "changelog head"
    ch.write_text((SRC / "CHANGELOG_0.174.0.md").read_text(encoding="utf-8").rstrip("\n") + "\n\n" + s,
                  encoding="utf-8", newline="\n")
    (DC / "VERSION").write_text("Deli Counter 0.174.0", encoding="utf-8", newline="\n")
    print("Deli Counter 0.174.0 applied")


if __name__ == "__main__":
    main()
