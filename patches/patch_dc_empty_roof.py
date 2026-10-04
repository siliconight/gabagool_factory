"""Deli Counter 0.175.0: an Empty is exterior plus roof.

Cold run 9146's export was refused by Level Factory's greybox-skin gate:
588 slab surfaces in `gb_floor`, every one an Empty's (attributed per
archetype off the shipped `site_base.glb`s, 48+96+120+108+48+168). An Empty
recorded no floor or roof slot, so Zoo built no module whose material the
worldskin's slab pass could use. See `dc_empty_roof/CHANGELOG_0.175.0.md`.

Anchored edits (every anchor once; refuses on a miss):
  deli_counter.py  a facade keeps only its roof slab; the facade branch
                   records its roof slot when modular
  presets.py       `empty_rowhome` names `roof_material: "concrete"`
Rewrites `specs/gs_empty_rowhome_[a-f].json` from the preset, copies
`dc_empty_roof/test_empty_roof.py`, CHANGELOG and VERSION. The library
rebuild is a separate step (`python build.py --all`, which the pre-commit
freshness check requires after any deli_counter.py change).

    python patch_dc_empty_roof.py
"""
import importlib
import json
import pathlib
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
DC = HERE.parent / "deli_counter"
SRC = HERE / "dc_empty_roof"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


SLABS_OLD = '''        for s in range(base, top + 1):
            is_roof = (s == top)
'''
SLABS_NEW = '''        for s in range(base, top + 1):
            is_roof = (s == top)
            # AN EMPTY IS EXTERIOR PLUS ROOF (0.175.0). Its ground slab and the
            # floors between its storeys stand inside a sealed box behind
            # opaque glass: unseen, unreachable, and with no room to record a
            # floor slot from, no art pass can dress them -- cold run 9146
            # shipped 588 of them in the greybox material. The roof stays,
            # visual and collision, so a greybox level still has a top on it.
            if getattr(self.s, "facade", False) and not is_roof:
                continue
'''

FACADE_OLD = '''            self._slabs()
            self._exterior()
            self._parapets()
            self._materials()
'''
FACADE_NEW = '''            self._slabs()
            self._exterior()
            # The roof slot, as a building records it, so Zoo dresses the
            # roof the shell keeps (0.175.0). A building calls this after
            # `_slab_holes_cut`; an Empty cuts no hole -- it has no stair or
            # ladder -- so here is as late as it needs to be.
            if self._modular_on():
                self._record_roof_slots()
            self._parapets()
            self._materials()
'''

PRESET_OLD = '''    s["ext_walls"] = ext
    s["scale_ref"] = bool(scale_ref)
    return s
'''
PRESET_NEW = '''    s["ext_walls"] = ext
    # A 1990s rowhouse roof is flat tar, silver-coated -- never its brick.
    # Unnamed, the roof slot's style follows the walls (`roofs.roof_slots`).
    s["roof_material"] = "concrete"
    s["scale_ref"] = bool(scale_ref)
    return s
'''


def main():
    assert (DC / "VERSION").read_text(encoding="utf-8").strip() == "Deli Counter 0.174.0"
    _edit(DC / "deli_counter.py", [(SLABS_OLD, SLABS_NEW), (FACADE_OLD, FACADE_NEW)])
    _edit(DC / "presets.py", [(PRESET_OLD, PRESET_NEW)])

    sys.path.insert(0, str(DC))
    presets = importlib.import_module("presets")
    for name, args in presets.EMPTY_ROWHOMES.items():
        spec = presets.empty_rowhome(name=name, **args)
        with open(DC / "specs" / f"{name}.json", "w", encoding="utf-8", newline="\n") as f:
            json.dump(spec, f, indent=2)

    shutil.copyfile(SRC / "test_empty_roof.py", DC / "test_empty_roof.py")
    ch = DC / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    ch.write_text((SRC / "CHANGELOG_0.175.0.md").read_text(encoding="utf-8").rstrip("\n") + "\n\n" + s,
                  encoding="utf-8", newline="\n")
    (DC / "VERSION").write_text("Deli Counter 0.175.0", encoding="utf-8", newline="\n")
    print("applied Deli Counter 0.175.0")


if __name__ == "__main__":
    main()
