"""Zoo 1.62.0: a kit whose plan gives two geometries one name is refused.

`plan_kit` detected cold run 9148's colliding Empty walls and printed
"STEM COLLISION ... one will overwrite the other" into six job logs; the kit
build exited 0 and the wrong module shipped. See
`zoo_refuse_collision/CHANGELOG_1.62.0.md`.

Anchored edits (every anchor once; refuses on a miss):
  zoo_keeper/bpylayer/build.py  `stem_collisions` in the kit index and the result
  tools/zoo_cli.py              `kit_exit_code`: a collision fails the build
Copies the test; CHANGELOG and VERSION.

    python patch_zoo_refuse_collision.py
"""
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve().parent
ZOO = HERE.parent / "zoo"
SRC = HERE / "zoo_refuse_collision"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


INDEX_OLD = '''        "n_fail": n_fail,
        "n_missing": n_missing,
    }
    index_file = f"{building_id}_kit.built.json"
'''
INDEX_NEW = '''        "n_fail": n_fail,
        "n_missing": n_missing,
        # Two geometries planned under one name (1.62.0): one file overwrote
        # the other and the loser's slots got the winner's module. Printed
        # since `plan_kit` was written and read by nobody -- cold run 9148
        # shipped six Empties' 2.8 m walls into 3.1 m slots with the warning
        # in every log. In the index, and it fails the build (`zoo_cli`).
        "stem_collisions": plan.get("stem_collisions", []),
    }
    index_file = f"{building_id}_kit.built.json"
'''

RET_OLD = '''    return {"building_id": building_id, "out_dir": out_dir, "theme": theme,
            "style": int(style), "modules": modules, "n_fail": n_fail,
            "n_missing": n_missing,
'''
RET_NEW = '''    return {"building_id": building_id, "out_dir": out_dir, "theme": theme,
            "style": int(style), "modules": modules, "n_fail": n_fail,
            "n_missing": n_missing,
            "stem_collisions": plan.get("stem_collisions", []),
'''

CLI_OLD = '''    print("[zoo] copy these into your game's art/zoo/ so Deli Counter's "
          "resolver swaps them in.")
    return 0 if res["n_fail"] == 0 else 2


def dress_run(args):
'''
CLI_NEW = '''    print("[zoo] copy these into your game's art/zoo/ so Deli Counter's "
          "resolver swaps them in.")
    for c in res.get("stem_collisions", []):
        print("[zoo] REFUSED: STEM COLLISION %s -- %d geometries planned under "
              "one name; the kit is wrong whichever was written last"
              % (c.get("stem"), c.get("count", 0)))
    return kit_exit_code(res)


def kit_exit_code(res):
    """2 when the kit is wrong, else 0: a module failed to build, or two
    geometries were planned under one name (1.62.0) -- the second is a module
    in the wrong place as surely as the first is a missing one."""
    return 0 if res.get("n_fail", 0) == 0 and not res.get("stem_collisions") else 2


def dress_run(args):
'''


def main():
    assert (ZOO / "VERSION").read_text(encoding="utf-8").strip() == "1.61.0"
    _edit(ZOO / "zoo_keeper" / "bpylayer" / "build.py", [(INDEX_OLD, INDEX_NEW), (RET_OLD, RET_NEW)])
    _edit(ZOO / "tools" / "zoo_cli.py", [(CLI_OLD, CLI_NEW)])
    shutil.copyfile(SRC / "test_kit_refuses_collision.py",
                    ZOO / "tests" / "test_kit_refuses_collision.py")
    ch = ZOO / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    ch.write_text((SRC / "CHANGELOG_1.62.0.md").read_text(encoding="utf-8").rstrip("\n") + "\n\n" + s,
                  encoding="utf-8", newline="\n")
    (ZOO / "VERSION").write_text("1.62.0", encoding="utf-8", newline="\n")
    print("applied Zoo 1.62.0")


if __name__ == "__main__":
    main()
