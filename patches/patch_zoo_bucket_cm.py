"""Zoo 1.63.0: a module is grouped no finer than the name it is given.

Cold run 9149 stopped at art: the freight terminal's parapet tiles were
4.514 and 4.515 m, two `plan_kit` groups under one centimetre name, and
1.62.0 refused the collision. Deli Counter 0.177.0 had moved its own name
check to centimetres and Zoo's grouping stayed at 0.1 mm -- one number asked
at two resolutions. See `zoo_bucket_cm/CHANGELOG_1.63.0.md`.

Anchored edits (every anchor once; refuses on a miss):
  zoo_keeper/core/kit.py  `dims_key` in whole centimetres
Copies the test; CHANGELOG and VERSION.

    python patch_zoo_bucket_cm.py
"""
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve().parent
ZOO = HERE.parent / "zoo"
SRC = HERE / "zoo_bucket_cm"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


OLD = '''            dims_key = (tuple(round(float(v), 4) for v in dims[:3])
                        if exact else None)
'''
NEW = '''            #
            # IN WHOLE CENTIMETRES, the resolution the name carries (1.63.0).
            # Grouped to 0.1 mm, two slots a millimetre apart -- Deli
            # Counter's parapet tiles, cut at millimetre-snapped lines, 4.514
            # and 4.515 m on the freight terminal in cold run 9149 -- were two
            # modules under ONE name, and the collision refusal (1.62.0)
            # stopped the run. A group finer than its name is a collision by
            # construction; two slots that can only get one name are one
            # module, built to the first slot's dims.
            dims_key = (tuple(int(round(float(v) * 100)) for v in dims[:3])
                        if exact else None)
'''


def main():
    assert (ZOO / "VERSION").read_text(encoding="utf-8").strip() == "1.62.0"
    _edit(ZOO / "zoo_keeper" / "core" / "kit.py", [(OLD, NEW)])
    shutil.copyfile(SRC / "test_bucket_at_name_resolution.py",
                    ZOO / "tests" / "test_bucket_at_name_resolution.py")
    ch = ZOO / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    ch.write_text((SRC / "CHANGELOG_1.63.0.md").read_text(encoding="utf-8").rstrip("\n") + "\n\n" + s,
                  encoding="utf-8", newline="\n")
    (ZOO / "VERSION").write_text("1.63.0", encoding="utf-8", newline="\n")
    print("applied Zoo 1.63.0")


if __name__ == "__main__":
    main()
