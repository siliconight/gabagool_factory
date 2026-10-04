"""Level Factory 0.133.0: the service pad wears the theme's concrete. Lot
0.93.0 draws a `yard` slab under each dumpster and skins it from the spec's
`ground_skins["yard"]`; this names that pack. Anchored edits (every anchor
once; refuses on a miss): `apps/cli/commands/__init__.py`
(`GROUND_SKIN_KINDS`), `tests/unit/test_ground_skins_in_site_spec.py`.

    python patch_lf_yard_skin.py
"""
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
LF = HERE.parent / "level_factory"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:60])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


ENTRY = """## [0.133.0] - the service pad wears the theme's concrete

Lot 0.93.0 draws a concrete pad (`yard`) under each dumpster -- step 4 of
`docs/proposals/LAND_USE_DESIGN.md`, open land given a role -- and skins it
from the site spec's `ground_skins["yard"]`. `GROUND_SKIN_KINDS` names that
pack: `yard -> concrete`, the kind a courtyard already wears, which every
theme that skins a courtyard already builds (`concrete_delco_1997` is in
cold run 9140's Pixelcoat output). A theme without it is said by Lot
(`LOT_GROUND_SKIN_MISSING`) and the pad ships in its greybox colour.

`tests/unit/test_ground_skins_in_site_spec.py`: the constructed directories
include the yard's.

"""


def main():
    v = (LF / "VERSION").read_text(encoding="utf-8").strip()
    assert v == "0.132.0", v
    _edit(LF / "apps" / "cli" / "commands" / "__init__.py", [
        ('                     # the markings\' decal: road paint, cutout where worn\n'
         '                     "paint": "road_paint"}\n',
         '                     # the markings\' decal: road paint, cutout where worn\n'
         '                     "paint": "road_paint",\n'
         '                     # the service pad under a dumpster (Lot 0.93.0)\n'
         '                     "yard": "concrete"}\n'),
    ])
    _edit(LF / "tests" / "unit" / "test_ground_skins_in_site_spec.py", [
        ('        "paint": str(Path("/px/out") / "road_paint_delco_1997"),\n    }\n',
         '        "paint": str(Path("/px/out") / "road_paint_delco_1997"),\n'
         '        "yard": str(Path("/px/out") / "concrete_delco_1997"),\n    }\n'),
        ('{"ground", "path", "courtyard", "road", "sidewalk", "paint"}\n',
         '{"ground", "path", "courtyard", "road", "sidewalk", "paint",\n'
         '                                           "yard"}\n'),
    ])
    ch = LF / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    assert s.startswith("## [0.132.0]"), "changelog head"
    ch.write_text(ENTRY + s, encoding="utf-8", newline="\n")
    (LF / "VERSION").write_text("0.133.0", encoding="utf-8", newline="\n")
    print("Level Factory 0.133.0 applied")


if __name__ == "__main__":
    main()
