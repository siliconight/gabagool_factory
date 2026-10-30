"""Level Factory 0.270.0: a civic building's pilasters merge with their side.

`merge_buildings.gd`'s `_unit` puts `pilaster_<side>_*` (Deli Counter >= 0.294.0) in the ground storey's side unit,
`ext 0 <side>`, before the room fallback: a pier outside its wall stands in no room and fell to a cell of its own.

Proven: tests/unit/test_merge_buildings.py's pilaster case fails on 0.269.0 (fails_on_old.out.txt); the clone's suite,
exit 0, 2,776 passed (suite_clone.out.txt); the slice rebuilt and priced (the factory's docs/findings/slice_look/,
slice 14: 5 fewer merged meshes on the bank, draws median +0, largest +2, as much as -6).
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT / 'level_factory'
PINS = {'CHANGELOG.md': 'f1c3f0cad0a71742', 'VERSION': 'b317526e27d3ae6c', 'assets/godot/merge_buildings.gd': '0a61c2c17d3187f3', 'tests/unit/test_merge_buildings.py': 'afaee8394d6225a5'}
EDITS = {'CHANGELOG.md': [('lines 1-1', "## [0.269.0] - a heading's draws are what the scene holds, not its stray frame\n", "## [0.270.0] - a civic building's pilasters merge with their side\n\nThe factory's roadmap 324. Deli Counter 0.294.0 stands a civic building's pilasters as `pilaster_<side>_<n>` slots\noutside its walls; `merge_buildings.gd`'s `_unit` knew `ext_`, `int_`, `parapet_` and `roof` and put anything else in\nthe room it stands in -- and a pier on the outside of a wall stands in none, so each fell to a cell of its own: one\nmesh and one draw a pier. Priced on the vertical slice (the factory's `docs/findings/slice_look/`, slice 11): draws\nmedian +2, largest +34, the bank's eight piers drawn one by one. `pilaster_<side>_*` now joins the ground storey's\nside, `ext 0 <side>`, before the room fallback -- the unit that enters view and leaves it with the pier -- and merges\nthere by material, so a side's piers are one mesh. On the slice (slice 14): the bank's scene 238 -> 233 merged\nmeshes and no pier left on its own; draws median +0, largest +2, as much as -6 (highest_vantage yaw 90). It does\nNOT give back what the pilasters cost at extraction_12 yaw 90 (1,457 -> 1,491 with them, 1,489 merged): that view's\n+34 is not per-pier submission, and what it is was not attributed. Tests: tests/unit/test_merge_buildings.py.\n\n## [0.269.0] - a heading's draws are what the scene holds, not its stray frame\n")], 'VERSION': [('lines 1-1', '0.269.0', '0.270.0')], 'assets/godot/merge_buildings.gd': [('lines 27-28', '##   * `ext_<storey>_<side>_*` -- one side of one storey; `parapet_<side>_*` -- one side of the parapet; `roof*`;\n##   * `int_<storey>_<k>_*` -- one partition run;\n', "##   * `ext_<storey>_<side>_*` -- one side of one storey; `parapet_<side>_*` -- one side of the parapet; `roof*`;\n##   * `pilaster_<side>_*` -- a civic building's pier, full height: the ground storey's side (0.270.0);\n##   * `int_<storey>_<k>_*` -- one partition run;\n"), ('lines 167-168', '\t\treturn "roof %s" % parts[1]\n\tif name.begins_with("roof"):\n', '\t\treturn "roof %s" % parts[1]\n\t# A CIVIC BUILDING\'S PILASTERS (0.270.0, Deli Counter >= 0.294.0): `pilaster_<side>_<n>` stands outside the\n\t# wall, in no room, so it fell to a cell of its own -- one mesh and one draw a pier; the slice\'s bank has eight.\n\t# Its side of the building is the unit that enters view and leaves it with it.\n\tif name.begins_with("pilaster_") and parts.size() > 1:\n\t\treturn "ext 0 %s" % parts[1]\n\tif name.begins_with("roof"):\n')], 'tests/unit/test_merge_buildings.py': [('lines 298-298', '    assert \'return "room %s %s" % [rid, _cell(origin.x, -origin.z)]\' in unit\n', '    assert \'return "room %s %s" % [rid, _cell(origin.x, -origin.z)]\' in unit\n\n\ndef test_a_civic_buildings_pilasters_merge_with_their_side():\n    """FAILS ON 0.269.0: a pilaster (Deli Counter >= 0.294.0, `pilaster_<side>_<n>`) stands outside the wall and in no\n    room, so it fell to a cell of its own -- a mesh and a draw a pier; the vertical slice\'s bank priced +34 draws at\n    one heading. It joins the ground storey\'s side, before the room fallback."""\n    text = M.MERGE_SCRIPT.read_text(encoding="utf-8")\n    unit = _func(text, "_unit")\n    rule = \'if name.begins_with("pilaster_") and parts.size() > 1:\\n\\t\\treturn "ext 0 %s" % parts[1]\'\n    assert rule in unit\n    assert unit.index(rule) < unit.index("return _room_unit(origin, rooms)")\n')]}
WHOLE = {}
NEW_FILES = {}


def _sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _read(name):
    """The file's LF text and whether it is CRLF on disk; refuses mixed endings and a file that is not the pinned one."""
    raw = (REPO / name).read_bytes()
    crlf, lf = raw.count(b"\r\n"), raw.count(b"\n")
    if crlf not in (0, lf):
        raise SystemExit("REFUSED: %s/%s has mixed line endings; nothing written" % (REPO.name, name))
    text = raw.decode("utf-8").replace("\r\n", "\n")
    if _sha(text) != PINS[name]:
        raise SystemExit("REFUSED: %s/%s is %s, not the %s this patch was written against; nothing written"
                         % (REPO.name, name, _sha(text), PINS[name]))
    return text, crlf > 0


def main():
    out = {}
    for name, edits in EDITS.items():
        text, crlf = _read(name)
        for what, old, new in edits:
            if text.count(old) != 1:
                raise SystemExit("REFUSED: %s/%s: the anchor at %s is there %d times; nothing written"
                                 % (REPO.name, name, what, text.count(old)))
            text = text.replace(old, new)
        out[name] = text.replace("\n", "\r\n") if crlf else text
    for name, text in WHOLE.items():
        _old, crlf = _read(name)
        out[name] = text.replace("\n", "\r\n") if crlf else text
    for name in NEW_FILES:
        if (REPO / name).exists():
            raise SystemExit("REFUSED: %s/%s exists already; nothing written" % (REPO.name, name))
    for name, text in out.items():
        (REPO / name).write_bytes(text.encode("utf-8"))
    for name, text in NEW_FILES.items():
        (REPO / name).parent.mkdir(parents=True, exist_ok=True)
        (REPO / name).write_bytes(text.encode("utf-8"))
    print("%s: %d files edited, %d written" % (REPO.name, len(out), len(NEW_FILES)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
