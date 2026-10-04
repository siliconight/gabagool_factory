"""Level Factory 0.139.0: two geometries under one module name block the run.

Zoo 1.62.0 writes `stem_collisions` into the kit index and exits 2; this
adapter reads exit 2 as a usable kit (a failed module falls back to its
base). A collision has no fallback, so it is read off the index as a blocking
`ZOO_STEM_COLLISION`. See `lf_stem_collision/CHANGELOG_0.139.0.md`.

Anchored edits (every anchor once; refuses on a miss):
  adapters/zoo/__init__.py  the finding, beside ZOO_PARTIAL_BUILD
Copies the test; CHANGELOG and VERSION.

    python patch_lf_stem_collision.py
"""
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve().parent
LF = HERE.parent / "level_factory"
SRC = HERE / "lf_stem_collision"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


OLD = '''                    "message": (f"{n_fail} module(s) failed to build; the resolver "
                                f"falls back to base for those. Kit is usable — "
                                f"review skins/theme coverage."),
                    "blocking": False, "raw_source_path": str(p),
                })
'''
NEW = '''                    "message": (f"{n_fail} module(s) failed to build; the resolver "
                                f"falls back to base for those. Kit is usable — "
                                f"review skins/theme coverage."),
                    "blocking": False, "raw_source_path": str(p),
                })
            # TWO GEOMETRIES UNDER ONE NAME (0.139.0, Zoo >= 1.62.0 writes
            # them). Not a partial build: nothing falls back -- whichever
            # module built last stands in every slot of both. Cold run 9148
            # stood its Empties' 2.8 m walls in 3.1 m slots with Zoo's warning
            # in six kit logs and exit 2 read here as "usable". So it blocks.
            # An index from before 1.62.0 has no key, and absence is silent.
            coll = man.get("stem_collisions")
            if isinstance(coll, list) and coll:
                issues.append({
                    "code": "ZOO_STEM_COLLISION",
                    "severity": "blocker", "category": "art_coverage",
                    "message": (f"{len(coll)} module name(s) planned for two "
                                f"geometries each: "
                                f"{', '.join(str(c.get('stem')) for c in coll)}; "
                                f"the last built stands in every slot of both"),
                    "suggested_fix": ("Deli Counter marks a name that covers two "
                                      "heights (`fit.key_height`, 0.176.0); a "
                                      "collision on another axis needs that axis "
                                      "in the name, on both sides "
                                      "(`kit.module_stem` / `themed_tscn.module_stem`)"),
                    "blocking": True, "raw_source_path": str(p),
                })
'''


def main():
    assert (LF / "VERSION").read_text(encoding="utf-8").strip() == "0.138.1"
    _edit(LF / "adapters" / "zoo" / "__init__.py", [(OLD, NEW)])
    shutil.copyfile(SRC / "test_zoo_stem_collision.py",
                    LF / "tests" / "unit" / "test_zoo_stem_collision.py")
    ch = LF / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    ch.write_text((SRC / "CHANGELOG_0.139.0.md").read_text(encoding="utf-8").rstrip("\n") + "\n\n" + s,
                  encoding="utf-8", newline="\n")
    (LF / "VERSION").write_text("0.139.0", encoding="utf-8", newline="\n")
    print("applied Level Factory 0.139.0")


if __name__ == "__main__":
    main()
