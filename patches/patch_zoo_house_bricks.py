"""Zoo 1.73.0: `brick_brown` and `brick_orange` are known kinds, so a slot asking
for a house's own brick keeps it. See `zoo_house_bricks/CHANGELOG_1.73.0.md`.

Anchored edits (every anchor once; refuses on a miss):
  zoo_keeper/core/skins.py         KNOWN_KINDS
  zoo_keeper/bpylayer/materials.py ROUGHNESS: a brick's 0.90 for both
                                   (`test_kind_vocabulary` holds the two
                                   tables to the same keys)
Copies the test; CHANGELOG and VERSION.

    python patch_zoo_house_bricks.py
"""
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve().parent
ZOO = HERE.parent / "zoo"
SRC = HERE / "zoo_house_bricks"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


KINDS_OLD = '''               "stone", "siding", "shingle",
'''
KINDS_NEW = '''               "stone", "siding", "shingle",
               # A HOUSE'S OWN BRICK (1.73.0, Pixelcoat 0.57.0): the comp's row
               # is brown, red and orange, one brick a house, and a theme holds
               # one grammar per kind
               "brick_brown", "brick_orange",
'''


ROUGH_OLD = '''             "brick": 0.90, "tile": 0.35, "drywall": 0.90, "ceiling_tile": 0.92,
'''
ROUGH_NEW = '''             "brick": 0.90, "tile": 0.35, "drywall": 0.90, "ceiling_tile": 0.92,
             # a house's own brick (1.73.0): the same fired clay, another colour
             "brick_brown": 0.90, "brick_orange": 0.90,
'''


def main():
    assert (ZOO / "VERSION").read_text(encoding="utf-8").strip() == "1.72.0"
    _edit(ZOO / "zoo_keeper" / "core" / "skins.py", [(KINDS_OLD, KINDS_NEW)])
    _edit(ZOO / "zoo_keeper" / "bpylayer" / "materials.py", [(ROUGH_OLD, ROUGH_NEW)])
    shutil.copyfile(SRC / "test_house_bricks.py", ZOO / "tests" / "test_house_bricks.py")
    ch = ZOO / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    ch.write_text((SRC / "CHANGELOG_1.73.0.md").read_text(encoding="utf-8").rstrip("\n") + "\n\n" + s,
                  encoding="utf-8", newline="\n")
    (ZOO / "VERSION").write_text("1.73.0", encoding="utf-8", newline="\n")
    print("applied Zoo 1.73.0")


if __name__ == "__main__":
    main()
