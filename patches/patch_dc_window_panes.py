"""Deli Counter 0.179.0: an Empty's windows carry a painted state.

Zoo 1.64.0 paints eight 1990s window states into one atlas; this chooses the
state of each Empty window (`empty_panes.choose`), writes it on the slot as
`pane`, and names the module `_p<state>` the way Zoo does. One rowhome in
the family is authored vacant, every window boarded. See
`dc_window_panes/CHANGELOG_0.179.0.md`.

Anchored edits (every anchor once; refuses on a miss):
  empty_panes.py                NEW: the states and the choice
  deli_counter.py               a facade window's slot carries `pane`
  themed_tscn.py                the mirror names `_p<state>`
  spec_types.py, schema         `vacant`
  presets.py                    `empty_rowhome(vacant=)`, one vacant house
  build_freshness.py            empty_panes.py is a source of the manifest
Rewrites the six rowhome specs from the preset; copies the test; CHANGELOG
and VERSION. `python build.py --all` follows.

    python patch_dc_window_panes.py
"""
import importlib
import json
import pathlib
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
DC = HERE.parent / "deli_counter"
SRC = HERE / "dc_window_panes"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


IMPORT_OLD = '''import roofs
import floors
'''
IMPORT_NEW = '''import roofs
import floors
import empty_panes
'''

TAG_OLD = '''        if role in ("window", "doorway") and getattr(self.s, "facade", False):
            slot["glazing"] = "facade"
        self.slots.append(slot)
'''
TAG_NEW = '''        if role in ("window", "doorway") and getattr(self.s, "facade", False):
            slot["glazing"] = "facade"
            # AND WHAT IT SHOWS (0.179.0): lit, dark, curtained, barred or
            # boarded, chosen per window -- which windows glow is a fact about
            # this building. Zoo (>= 1.64.0) paints the state.
            if role == "window":
                slot["pane"] = empty_panes.choose(
                    self.s.name, self.s.seed, vb, story,
                    vacant=getattr(self.s, "vacant", False))
        self.slots.append(slot)
'''

SIG_OLD = '''                material_in: str = None) -> str:
    """``<type>[_<species>]_<theme>_<style:02d>'''
SIG_NEW = '''                material_in: str = None, pane: str = None) -> str:
    """``<type>[_<species>]_<theme>_<style:02d>'''

STEM_OLD = '''    if material_in:
        base += f"_i{material_in}"
'''
STEM_NEW = '''    if material_in:
        base += f"_i{material_in}"
    # A painted pane's state (0.179.0), as `kit.module_stem` writes it
    if pane:
        base += f"_p{pane}"
'''

RESOLVE_OLD = '''    inner = slot.get("material_in") if typ in INNER_FACE_ROLES else None
    stem = module_stem(typ, theme, eff_style, width_cm,
                       state if state else _default_stem_state(slot),
                       depth_cm, vtag, otag, height_cm, species=species,
                       material=material, glazing=glazing, budget_tiles=budget,
                       material_in=inner, **dress)
'''
RESOLVE_NEW = '''    inner = slot.get("material_in") if typ in INNER_FACE_ROLES else None
    # the same test Zoo's `plan_kit` makes (1.64.0), so the names agree
    import empty_panes
    pane = (slot.get("pane") if typ == "window" and slot.get("glazing") == "facade"
            and slot.get("pane") in empty_panes.STATES else None)
    stem = module_stem(typ, theme, eff_style, width_cm,
                       state if state else _default_stem_state(slot),
                       depth_cm, vtag, otag, height_cm, species=species,
                       material=material, glazing=glazing, budget_tiles=budget,
                       material_in=inner, pane=pane, **dress)
'''

SPEC_OLD = '''    facade: bool = False

'''
SPEC_NEW = '''    facade: bool = False
    # A VACANT facade (0.179.0): every window boarded (`empty_panes`). The
    # 1990s vacancy the Empties' comps call for, authored per house like its
    # wall material -- not drawn, so a street is not left without one.
    vacant: bool = False

'''

SCHEMA_OLD = '''    "facade": {
      "type": "boolean",
      "description": "non-enterable facade shell: exterior+roof+collision only, no interior/gameplay"
    },
'''
SCHEMA_NEW = '''    "facade": {
      "type": "boolean",
      "description": "non-enterable facade shell: exterior+roof+collision only, no interior/gameplay"
    },
    "vacant": {
      "type": "boolean",
      "description": "a vacant facade shell: every window painted boarded (empty_panes, 0.179.0)"
    },
'''

PRESET_SIG_OLD = '''                  cornice: float = 0.8, seed: int = 1911,
                  scale_ref: bool = False) -> dict:
'''
PRESET_SIG_NEW = '''                  cornice: float = 0.8, seed: int = 1911,
                  scale_ref: bool = False, vacant: bool = False) -> dict:
'''
PRESET_BODY_OLD = '''    s["roof_material"] = "concrete"
    s["scale_ref"] = bool(scale_ref)
    return s
'''
PRESET_BODY_NEW = '''    s["roof_material"] = "concrete"
    s["scale_ref"] = bool(scale_ref)
    # boarded, every window (0.179.0); absent unless asked, so every other
    # house's spec is unchanged
    if vacant:
        s["vacant"] = True
    return s
'''
FAMILY_OLD = '''    "gs_empty_rowhome_e": dict(width=5.5, floors=3, wall="paint_block", door_side="W", cornice=0.9, seed=1915),
'''
FAMILY_NEW = '''    # the vacant one (0.179.0): painted block, boarded -- the family's
    # "boarded variant", one in six as a 1990s Delco street has a few
    "gs_empty_rowhome_e": dict(width=5.5, floors=3, wall="paint_block", door_side="W", cornice=0.9, seed=1915,
                               vacant=True),
'''

FRESH_OLD = '''    "themed_tscn.py",
)
'''
FRESH_NEW = '''    "themed_tscn.py",
    # which state an Empty's window is painted in rides on its slot (0.179.0)
    "empty_panes.py",
)
'''


def main():
    assert (DC / "VERSION").read_text(encoding="utf-8").strip() == "Deli Counter 0.178.0"
    assert not (DC / "empty_panes.py").exists()
    shutil.copyfile(SRC / "empty_panes.py", DC / "empty_panes.py")
    _edit(DC / "deli_counter.py", [(IMPORT_OLD, IMPORT_NEW), (TAG_OLD, TAG_NEW)])
    _edit(DC / "themed_tscn.py", [(SIG_OLD, SIG_NEW), (STEM_OLD, STEM_NEW), (RESOLVE_OLD, RESOLVE_NEW)])
    _edit(DC / "spec_types.py", [(SPEC_OLD, SPEC_NEW)])
    _edit(DC / "schema" / "level.schema.json", [(SCHEMA_OLD, SCHEMA_NEW)])
    _edit(DC / "presets.py", [(PRESET_SIG_OLD, PRESET_SIG_NEW), (PRESET_BODY_OLD, PRESET_BODY_NEW),
                              (FAMILY_OLD, FAMILY_NEW)])
    _edit(DC / "build_freshness.py", [(FRESH_OLD, FRESH_NEW)])
    sys.path.insert(0, str(DC))
    presets = importlib.import_module("presets")
    for name, args in presets.EMPTY_ROWHOMES.items():
        with open(DC / "specs" / f"{name}.json", "w", encoding="utf-8", newline="\n") as f:
            json.dump(presets.empty_rowhome(name=name, **args), f, indent=2)
    shutil.copyfile(SRC / "test_empty_panes.py", DC / "test_empty_panes.py")
    ch = DC / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    ch.write_text((SRC / "CHANGELOG_0.179.0.md").read_text(encoding="utf-8").rstrip("\n") + "\n\n" + s,
                  encoding="utf-8", newline="\n")
    (DC / "VERSION").write_text("Deli Counter 0.179.0", encoding="utf-8", newline="\n")
    print("applied Deli Counter 0.179.0")


if __name__ == "__main__":
    main()
