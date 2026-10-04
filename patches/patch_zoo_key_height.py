"""Zoo 1.60.0: a slot marked `fit.key_height` names its height.

Cold run 9148: an Empty's walls are 3.1 m below its roof storey and 2.8 m
under the roof (Deli Counter 0.175.2); both built as one name and the 2.8 m
module won, so every 3.1 m slot got a 2.8 m panel. Deli Counter 0.176.0
marks each slot whose name covers more than one height. See
`zoo_key_height/CHANGELOG_1.60.0.md`.

Anchored edits (every anchor once; refuses on a miss):
  zoo_keeper/core/kit.py  `height_cm` also when the slot is marked
Copies the test; CHANGELOG and VERSION.

    python patch_zoo_key_height.py
"""
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve().parent
ZOO = HERE.parent / "zoo"
SRC = HERE / "zoo_key_height"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


KIT_OLD = '''        height_cm = (int(round(dims[2] * 100))
                     if exact and typ in VOLUME_ROLES + CORNER_ROLES else None)
        vtag = void_tag(fit.get("voids")) if typ in PLATE_ROLES else None
        otag = (opening_tag(fit.get("openings"))
'''
KIT_NEW = '''        # `fit.key_height` (1.60.0): Deli Counter (>= 0.176.0) marks a slot
        # whose name would otherwise cover two heights in one building -- an
        # Empty's 3.1 m walls and its 2.8 m walls under the roof were one
        # name, and the later build overwrote the earlier. Unmarked, every
        # name is unchanged. `themed_tscn.resolve_themed_stem` is the mirror.
        height_cm = (int(round(dims[2] * 100))
                     if exact and (typ in VOLUME_ROLES + CORNER_ROLES
                                   or fit.get("key_height")) else None)
        vtag = void_tag(fit.get("voids")) if typ in PLATE_ROLES else None
        otag = (opening_tag(fit.get("openings"))
'''


def main():
    assert (ZOO / "VERSION").read_text(encoding="utf-8").strip() == "1.59.0"
    _edit(ZOO / "zoo_keeper" / "core" / "kit.py", [(KIT_OLD, KIT_NEW)])
    shutil.copyfile(SRC / "test_key_height.py", ZOO / "tests" / "test_key_height.py")
    ch = ZOO / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    ch.write_text((SRC / "CHANGELOG_1.60.0.md").read_text(encoding="utf-8").rstrip("\n") + "\n\n" + s,
                  encoding="utf-8", newline="\n")
    (ZOO / "VERSION").write_text("1.60.0", encoding="utf-8", newline="\n")
    print("applied Zoo 1.60.0")


if __name__ == "__main__":
    main()
