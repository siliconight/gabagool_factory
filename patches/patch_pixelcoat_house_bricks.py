"""Pixelcoat 0.57.0: a house's own brick -- `brick_brown` and `brick_orange`
beside the red, mapped in both level themes. See
`pixelcoat_house_bricks/CHANGELOG_0.57.0.md`.

Anchored edits (every anchor once; refuses on a miss):
  profiles/themes/delco.json       the two kinds after `brick`
  profiles/themes/delco_1997.json  the same
  pixelcoat/cli/main.py            `_ZOO_KINDS` lists them (Zoo 1.73.0)
  pixelcoat/version.py             0.57.0
Adds the two grammars; copies the test; CHANGELOG and VERSION.

    python patch_pixelcoat_house_bricks.py
"""
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve().parent
PC = HERE.parent / "pixelcoat"
SRC = HERE / "pixelcoat_house_bricks"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


THEME_OLD = '''    "brick": "brick_delco",
'''
THEME_NEW = '''    "brick": "brick_delco",
    "brick_brown": "brick_brown_delco",
    "brick_orange": "brick_orange_delco",
'''

KINDS_OLD = '''              "wood_stained", "paint_block")
'''
KINDS_NEW = '''              "wood_stained", "paint_block",
              # a house's own brick (0.57.0, Zoo 1.73.0): the comp's row is
              # brown, red and orange, one brick a house
              "brick_brown", "brick_orange")
'''

VER_OLD = '''_FALLBACK = "0.56.0"
'''
VER_NEW = '''_FALLBACK = "0.57.0"
'''


def main():
    assert (PC / "VERSION").read_text(encoding="utf-8").strip() == "Pixelcoat 0.56.0"
    for pid in ("brick_brown_delco", "brick_orange_delco"):
        dst = PC / "profiles" / "materials" / f"{pid}.json"
        assert not dst.exists(), dst
        shutil.copyfile(SRC / f"{pid}.json", dst)
    _edit(PC / "profiles" / "themes" / "delco.json", [(THEME_OLD, THEME_NEW)])
    _edit(PC / "profiles" / "themes" / "delco_1997.json", [(THEME_OLD, THEME_NEW)])
    _edit(PC / "pixelcoat" / "cli" / "main.py", [(KINDS_OLD, KINDS_NEW)])
    _edit(PC / "pixelcoat" / "version.py", [(VER_OLD, VER_NEW)])
    shutil.copyfile(SRC / "test_house_bricks.py", PC / "tests" / "test_house_bricks.py")
    ch = PC / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    head = "## [0.56.0]"
    assert s.count(head) == 1
    ch.write_text(s.replace(head, (SRC / "CHANGELOG_0.57.0.md").read_text(encoding="utf-8").rstrip("\n")
                            + "\n\n" + head), encoding="utf-8", newline="\n")
    (PC / "VERSION").write_text("Pixelcoat 0.57.0", encoding="utf-8", newline="\n")
    print("applied Pixelcoat 0.57.0")


if __name__ == "__main__":
    main()
