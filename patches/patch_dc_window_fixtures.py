"""Deli Counter 0.181.0: what hangs in an Empty's window -- bars, an air
conditioner -- chosen per window and written on the slot beside its pane.

The walker's window photographs: "window air conditioners in nearly every
photograph", and bars proud of the frame. Patina (>= 0.26.0) orders them from
these fields and Zoo (>= 1.69.0) builds them. See
`dc_window_fixtures/CHANGELOG_0.181.0.md`.

Anchored edits (every anchor once; refuses on a miss):
  empty_panes.py    BAR_STATES, NO_AC, AC_GROUND / AC_UPPER, fixtures()
  deli_counter.py   the facade window's slot takes fixtures() beside its pane
Copies the test; CHANGELOG and VERSION. Rebuild after: `python build.py --all`.

    python patch_dc_window_fixtures.py
"""
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve().parent
DC = HERE.parent / "deli_counter"
SRC = HERE / "dc_window_fixtures"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


PANES_OLD = '''    if vacant:
        return "boarded"
    return _pick(GROUND if int(story or 0) <= 0 else UPPER,
                 "%s:%s:%s" % (building, seed, slot_id))
'''
PANES_NEW = '''    if vacant:
        return "boarded"
    return _pick(GROUND if int(story or 0) <= 0 else UPPER,
                 "%s:%s:%s" % (building, seed, slot_id))


#: THE PANES THAT CARRY BARS (0.181.0). They were painted into the pane; they
#: are geometry now -- Zoo (>= 1.69.0) builds them from the Patina (>= 0.26.0)
#: order this slot field asks for, and paints only the room behind.
BAR_STATES = ("lit_bars", "dark_bars")
#: Panes no air conditioner sits in: behind flat bars (they stand 3.5 cm off
#: the wall, a unit 30 cm out -- the bellied grille that takes one is not
#: built), a boarded window, and the box fan's, which has its own unit.
NO_AC = BAR_STATES + ("boarded", "dark_fan")
#: Units in 100 eligible windows. "Window air conditioners in nearly every
#: photograph" (EMPTIES_COMPS.md, "Window comps"): mostly upstairs, in the
#: bedrooms, fewer at the street, where a third of the front is barred.
AC_GROUND = 10
AC_UPPER = 30


def fixtures(pane, building, seed, slot_id, story):
    """What hangs in one window, as slot fields: ``{"bars": True}`` on a
    barred pane, ``{"ac": True}`` on a window drawn for an air conditioner,
    else ``{}``.

    The unit is drawn on its OWN key, not the pane's, so adding units or
    retuning their rate does not reshuffle which windows glow."""
    if pane in BAR_STATES:
        return {"bars": True}
    if pane in NO_AC or pane not in STATES:
        return {}
    rate = AC_GROUND if int(story or 0) <= 0 else AC_UPPER
    if _crc("ac:%s:%s:%s" % (building, seed, slot_id)) % 100 < rate:
        return {"ac": True}
    return {}
'''

SLOT_OLD = '''            if role == "window":
                slot["pane"] = empty_panes.choose(
                    self.s.name, self.s.seed, vb, story,
                    vacant=getattr(self.s, "vacant", False))
        self.slots.append(slot)
'''
SLOT_NEW = '''            if role == "window":
                slot["pane"] = empty_panes.choose(
                    self.s.name, self.s.seed, vb, story,
                    vacant=getattr(self.s, "vacant", False))
                # AND WHAT HANGS IN IT (0.181.0): bars on a barred pane, an
                # air conditioner in some others. Patina (>= 0.26.0) orders
                # them from these fields and Zoo (>= 1.69.0) builds them.
                slot.update(empty_panes.fixtures(
                    slot["pane"], self.s.name, self.s.seed, vb, story))
        self.slots.append(slot)
'''


def main():
    assert (DC / "VERSION").read_text(encoding="utf-8").strip() == "Deli Counter 0.180.0"
    _edit(DC / "empty_panes.py", [(PANES_OLD, PANES_NEW)])
    _edit(DC / "deli_counter.py", [(SLOT_OLD, SLOT_NEW)])
    shutil.copyfile(SRC / "test_window_fixtures.py", DC / "test_window_fixtures.py")
    ch = DC / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    ch.write_text((SRC / "CHANGELOG_0.181.0.md").read_text(encoding="utf-8").rstrip("\n") + "\n\n" + s,
                  encoding="utf-8", newline="\n")
    (DC / "VERSION").write_text("Deli Counter 0.181.0", encoding="utf-8", newline="\n")
    print("applied Deli Counter 0.181.0 -- now rebuild: python build.py --all")


if __name__ == "__main__":
    main()
