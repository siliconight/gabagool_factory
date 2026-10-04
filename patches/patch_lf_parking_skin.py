"""Level Factory 0.134.0: the parking field wears the theme's asphalt. Lot
0.94.0 draws a `parking` slab per field and skins it from the site spec's
`ground_skins["parking"]`; this names that pack. Anchored edits (every
anchor once; refuses on a miss): `apps/cli/commands/__init__.py`
(`GROUND_SKIN_KINDS`), `tests/unit/test_ground_skins_in_site_spec.py`.

    python patch_lf_parking_skin.py
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


ENTRY = """## [0.134.0] - the parking field wears the theme's asphalt

Lot 0.94.0 draws a parking field in a gap between buildings -- step 4 of
`docs/proposals/LAND_USE_DESIGN.md`, its second use -- and skins its slab
from the site spec's `ground_skins["parking"]`. `GROUND_SKIN_KINDS` names
that pack: `parking -> asphalt`, the road's and the plate's own kind, so
the field reads as paving continuous with the road through its driveway,
and is told apart by its bay lines and its cars, not by its surface.

`tests/unit/test_ground_skins_in_site_spec.py`: the constructed directories
include the field's.

"""


def main():
    v = (LF / "VERSION").read_text(encoding="utf-8").strip()
    assert v == "0.133.0", v
    _edit(LF / "apps" / "cli" / "commands" / "__init__.py", [
        ('                     # the service pad under a dumpster (Lot 0.93.0)\n'
         '                     "yard": "concrete"}\n',
         '                     # the service pad under a dumpster (Lot 0.93.0)\n'
         '                     "yard": "concrete",\n'
         '                     # a parking field in a gap between buildings (Lot 0.94.0)\n'
         '                     "parking": "asphalt"}\n'),
    ])
    _edit(LF / "tests" / "unit" / "test_ground_skins_in_site_spec.py", [
        ('        "yard": str(Path("/px/out") / "concrete_delco_1997"),\n    }\n',
         '        "yard": str(Path("/px/out") / "concrete_delco_1997"),\n'
         '        "parking": str(Path("/px/out") / "asphalt_delco_1997"),\n    }\n'),
        ('{"ground", "path", "courtyard", "road", "sidewalk", "paint",\n'
         '                                           "yard"}\n',
         '{"ground", "path", "courtyard", "road", "sidewalk", "paint",\n'
         '                                           "yard", "parking"}\n'),
    ])
    ch = LF / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    assert s.startswith("## [0.133.0]"), "changelog head"
    ch.write_text(ENTRY + s, encoding="utf-8", newline="\n")
    (LF / "VERSION").write_text("0.134.0", encoding="utf-8", newline="\n")
    print("Level Factory 0.134.0 applied")


if __name__ == "__main__":
    main()
