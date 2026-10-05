"""Zoo 1.65.0: colour variation in the painted windows -- sixteen states.

The walker sent window photographs and said "color variation is key": the
night ones show tungsten, deep orange, cool fluorescent and pink rooms, and
blinds, half-drawn shades, curtains, a box fan, where 1.64.0 painted one warm
light. `core/window_panes.py` is replaced whole by the sixteen-state painter
(same atlas machinery, same API), and only if the file is 1.64.0's to the
byte. See `zoo_pane_colours/CHANGELOG_1.65.0.md`.

    python patch_zoo_pane_colours.py
"""
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve().parent
ZOO = HERE.parent / "zoo"
SRC = HERE / "zoo_pane_colours"


def main():
    assert (ZOO / "VERSION").read_text(encoding="utf-8").strip() == "1.64.0"
    live = ZOO / "zoo_keeper" / "core" / "window_panes.py"
    assert live.read_bytes() == (HERE / "zoo_window_panes" / "window_panes.py").read_bytes(), \
        "window_panes.py is not 1.64.0's -- refusing to replace it"
    shutil.copyfile(SRC / "window_panes.py", live)
    t = ZOO / "tests" / "test_window_panes.py"
    s = t.read_text(encoding="utf-8")
    old = "def test_only_a_lit_window_glows():\n"
    new = ('def test_the_atlas_has_sixteen_states_and_five_room_lights():\n'
           '    """1.65.0, "color variation is key": more than one warm light."""\n'
           '    assert len(P.STATES) == P.COLS * P.ROWS == 16\n'
           '    lights = {P.ROOMS[s] for s in P.STATES if s.startswith("lit")}\n'
           '    assert len(lights) >= 4\n\n\n' + old)
    assert s.count(old) == 1
    t.write_text(s.replace(old, new), encoding="utf-8", newline="\n")
    shutil.copyfile(t, SRC / "test_window_panes.py")
    ch = ZOO / "CHANGELOG.md"
    c = ch.read_text(encoding="utf-8")
    ch.write_text((SRC / "CHANGELOG_1.65.0.md").read_text(encoding="utf-8").rstrip("\n") + "\n\n" + c,
                  encoding="utf-8", newline="\n")
    (ZOO / "VERSION").write_text("1.65.0", encoding="utf-8", newline="\n")
    print("applied Zoo 1.65.0")


if __name__ == "__main__":
    main()
