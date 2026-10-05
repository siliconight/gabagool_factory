"""Deli Counter 0.180.0: the window states follow Zoo 1.65.0's sixteen.

The walker: "color variation is key". Zoo 1.65.0 paints four room lights and
more coverings; `empty_panes` lists the same states in the same order (pinned
against Zoo by `test_empty_panes.py`) and spreads the mix across them -- still
mostly dark. See `dc_pane_colours/CHANGELOG_0.180.0.md`.

    python patch_dc_pane_colours.py
"""
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
DC = HERE.parent / "deli_counter"
SRC = HERE / "dc_pane_colours"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


OLD = '''STATES = ("lit", "lit_blind", "lit_curtain", "lit_bars",
          "dark", "dark_curtain", "dark_bars", "boarded")

#: (state, weight). Street level: bars on half, most dark -- 28 lit in 100.
GROUND = (("dark_bars", 36), ("lit_bars", 16), ("dark", 20),
          ("dark_curtain", 16), ("lit", 8), ("lit_blind", 4))
#: Upstairs: no bars, still more dark than lit -- 38 lit in 100.
UPPER = (("dark", 40), ("dark_curtain", 22), ("lit", 16),
         ("lit_blind", 12), ("lit_curtain", 10))
'''
NEW = '''STATES = ("lit", "lit_amber", "lit_cool", "lit_pink",
          "lit_blind", "lit_blind_cool", "lit_curtain", "lit_shade",
          "lit_bars", "dark", "dark_blind", "dark_shade",
          "dark_curtain", "dark_bars", "dark_fan", "boarded")

#: (state, weight), each table summing to 100. COLOUR VARIATION IS KEY (the
#: walker, 0.180.0): the lit share is spread across four room lights and the
#: coverings, so a street is not one warm yellow. Street level: bars on over a
#: third, most dark -- 32 lit in 100.
GROUND = (("dark_bars", 24), ("lit_bars", 12), ("dark", 12), ("dark_blind", 10),
          ("dark_curtain", 8), ("dark_shade", 8), ("dark_fan", 6), ("lit", 6),
          ("lit_amber", 4), ("lit_blind", 4), ("lit_curtain", 3), ("lit_shade", 3))
#: Upstairs: no bars, still more dark than lit -- 42 lit in 100.
UPPER = (("dark", 18), ("dark_blind", 12), ("dark_shade", 10), ("dark_curtain", 12),
         ("dark_fan", 6), ("lit", 8), ("lit_amber", 7), ("lit_cool", 6), ("lit_pink", 4),
         ("lit_blind", 6), ("lit_blind_cool", 4), ("lit_curtain", 4), ("lit_shade", 3))
'''


def main():
    assert (DC / "VERSION").read_text(encoding="utf-8").strip() == "Deli Counter 0.179.0"
    _edit(DC / "empty_panes.py", [(OLD, NEW)])
    ch = DC / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    ch.write_text((SRC / "CHANGELOG_0.180.0.md").read_text(encoding="utf-8").rstrip("\n") + "\n\n" + s,
                  encoding="utf-8", newline="\n")
    (DC / "VERSION").write_text("Deli Counter 0.180.0", encoding="utf-8", newline="\n")
    print("applied Deli Counter 0.180.0")


if __name__ == "__main__":
    main()
