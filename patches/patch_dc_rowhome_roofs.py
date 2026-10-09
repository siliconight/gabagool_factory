"""Deli Counter 0.204.1: a quarter of the rowhome roofs carry an antenna or a dish.

Roadmap 219, the walker's note 3: "far too many Sattelite/Attena that makes the rowhomes look
a little too uniform and computer generated. perhaps 30% as many?" The source is
`presets.EMPTY_ROWHOMES` (0.185.0: antennas on a, b, d, e, g, i, j and l, dishes on b and k);
the specs are its output (`test_empties.test_the_variants_are_the_preset_s_own_output`). Three
stay: antennas on a and g, the dish on k.

*First attempt, refused by the suite and kept here:* the six specs were edited by hand, and
`test_roof_fixtures` and `test_empties` both failed -- the presets still asked for the fixtures
the built roofs no longer carried. The presets are the source; the specs follow them.

Anchored edits, every anchor once, nothing written until all matched:
- `presets.py`: the roof note, and six rows (b, d, e, i, j, l) lose `antenna` / `dish`;
- `specs/gs_empty_rowhome_{b,d,e,i,j,l}.json`: their last keys, as the presets now generate;
- `test_roof_fixtures.py`: the family test pins 2 antennas, 1 dish, 9 bare.
CHANGELOG and VERSION from `dc_rowhome_roofs/CHANGELOG_0.204.1.md`. The six shells are rebuilt
after, by `build.py`.

    python patch_dc_rowhome_roofs.py
"""
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
DC = HERE.parent / "deli_counter"
SRC = HERE / "dc_rowhome_roofs"

ROW = '    "gs_empty_rowhome_%s": dict('
PRESET_EDITS = [
    ("    # and its roof (0.185.0): a TV antenna on eight of the twelve, as a 1990s\n"
     "    # Philadelphia street has -- cable came late to the city -- and the odd\n"
     "    # satellite dish on two; c, f and h have neither\n",
     "    # and its roof (0.185.0): a TV antenna, and the odd satellite dish. Eight\n"
     "    # antennas and two dishes, as a 1990s Philadelphia street had them -- cable\n"
     "    # came late to the city -- read as uniform and computer generated: the\n"
     "    # walker, 2026-10-09, \"perhaps 30% as many?\" (0.204.1). So three:\n"
     "    # antennas on a and g, the dish on k; the other nine have neither.\n"),
    ('                               door_finish="white", antenna=True, dish=True),\n',
     '                               door_finish="white"),\n'),
    (ROW % "d" + 'width=6.0, floors=2, wall="stone_ext", door_side="W", cornice=0.6, seed=1914,\n'
     '                               door_finish="green", antenna=True),\n',
     ROW % "d" + 'width=6.0, floors=2, wall="stone_ext", door_side="W", cornice=0.6, seed=1914,\n'
     '                               door_finish="green"),\n'),
    ('                               vacant=True, door_finish="black", security_door=True, antenna=True),\n',
     '                               vacant=True, door_finish="black", security_door=True),\n'),
    ('                               door_finish="oxblood", antenna=True),\n',
     '                               door_finish="oxblood"),\n'),
    ('                               door_finish="black", antenna=True),\n',
     '                               door_finish="black"),\n'),
    ('                               door_finish="stained", security_door=True, antenna=True),\n',
     '                               door_finish="stained", security_door=True),\n'),
]

SPEC_EDITS = {
    "b": ('  "door_finish": "white",\n  "roof_antenna": true,\n  "roof_dish": true\n}',
          '  "door_finish": "white"\n}'),
    "d": ('  "door_finish": "green",\n  "roof_antenna": true\n}',
          '  "door_finish": "green"\n}'),
    "e": ('  "security_door": true,\n  "roof_antenna": true\n}',
          '  "security_door": true\n}'),
    "i": ('  "door_finish": "oxblood",\n  "roof_antenna": true\n}',
          '  "door_finish": "oxblood"\n}'),
    "j": ('  "door_finish": "black",\n  "roof_antenna": true\n}',
          '  "door_finish": "black"\n}'),
    "l": ('  "security_door": true,\n  "roof_antenna": true\n}',
          '  "security_door": true\n}'),
}

TEST_OLD = (
    "def test_the_family_has_antennas_on_eight_and_dishes_on_two():\n"
    "    rows = list(presets.EMPTY_ROWHOMES.values())\n"
    "    assert sum(1 for a in rows if a.get(\"antenna\")) == 8\n"
    "    assert sum(1 for a in rows if a.get(\"dish\")) == 2\n"
    "    assert sum(1 for a in rows if not (a.get(\"antenna\") or a.get(\"dish\"))) == 3\n"
)
TEST_NEW = (
    "def test_the_family_has_antennas_on_two_and_a_dish_on_one():\n"
    "    \"\"\"FAILS ON 0.204.0. The walker, 2026-10-09: \"far too many Sattelite/Attena\n"
    "    that makes the rowhomes look a little too uniform and computer generated.\n"
    "    perhaps 30% as many?\" 0.185.0's eight antennas and two dishes, cut to\n"
    "    three (0.204.1).\"\"\"\n"
    "    rows = list(presets.EMPTY_ROWHOMES.values())\n"
    "    assert sum(1 for a in rows if a.get(\"antenna\")) == 2\n"
    "    assert sum(1 for a in rows if a.get(\"dish\")) == 1\n"
    "    assert sum(1 for a in rows if not (a.get(\"antenna\") or a.get(\"dish\"))) == 9\n"
)


def _edit(path, pairs):
    d = path.read_bytes()
    assert b"\r\n" not in d, (path, "has CRLF")
    t = d.decode("utf-8")
    for old, new in pairs:
        assert t.count(old) == 1, (path.name, t.count(old), old[:70])
        t = t.replace(old, new)
    return t.encode("utf-8")


def main():
    v = (DC / "VERSION").read_text(encoding="utf-8").strip()
    assert v == "Deli Counter 0.204.0", v
    entry = (SRC / "CHANGELOG_0.204.1.md").read_text(encoding="utf-8")
    staged = {DC / "presets.py": _edit(DC / "presets.py", PRESET_EDITS),
              DC / "test_roof_fixtures.py": _edit(DC / "test_roof_fixtures.py", [(TEST_OLD, TEST_NEW)])}
    for house, (old, new) in SPEC_EDITS.items():
        p = DC / "specs" / ("gs_empty_rowhome_%s.json" % house)
        t = p.read_bytes().decode("utf-8")
        tail = t.rstrip("\n")
        assert tail.endswith(old) and t.count(old) == 1, (house, old)
        staged[p] = (tail[: -len(old)] + new + t[len(tail):]).encode("utf-8")
    cl = DC / "CHANGELOG.md"
    d = cl.read_bytes()
    assert b"## [0.204.1]" not in d and d.startswith(b"## [0.204.0]")
    for p, raw in staged.items():
        p.write_bytes(raw)
    cl.write_bytes(entry.encode("utf-8").replace(b"\r\n", b"\n") + b"\n" + d)
    (DC / "VERSION").write_bytes(b"Deli Counter 0.204.1")
    print("Deli Counter 0.204.0 -> 0.204.1; presets, specs", ", ".join(sorted(SPEC_EDITS)), "and the family test")


if __name__ == "__main__":
    main()
