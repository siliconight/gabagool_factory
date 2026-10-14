"""Level Factory 0.209.0: a walk-up's fire escape merges with its front (factory roadmaps 156 and 241; found
pricing cold run 9303, Zoo 1.110.0's `fire_escape` stood by Deli Counter 0.220.0, against 9302).

`merge_empties.gd` takes apart every slot child of an Empty whose name gives a side -- `ext_<storey>_<side>_*`,
`parapet_<side>_*`, `roof_*`, `stoop_*` -- and merges its surfaces one mesh a side per material. Deli Counter
0.220.0's fire escape slots, `fire_escape_<storey>` and `fire_escape_drop`, give none, so each stayed a module
drawn on its own: four to six a walk-up, 28 on 9303's picked candidate (`lot/gs_midrise_a/site.tscn` in its
package: five `fire_escape_*` instances beside the merged sides). The stack stands on the front wall, S --
`fire_escape_stack.plan` refuses any other side, and Deli Counter's schema enum is `["front", null]` -- and
every storey and the drop wear one material, `M_Skin_metal_painted_delco_1997_0f0f11` (the four GLBs'
glTF JSON, read). So `_side` gives a `fire_escape_*` slot the front's side, as 0.196.0 did the stoop.

Anchored edits, each asserted exactly once and every file's sha16 pinned, nothing written until all matched:
  assets/godot/merge_empties.gd     the header's list of sides; `_side` returns "S" for `fire_escape_*`
  tests/unit/test_merge_empties.py  `test_a_walk_up_s_fire_escape_merges_with_its_front` (pins the Godot
                                    half's source, as the stoop's test does) and
                                    `test_deli_counter_stands_a_fire_escape_only_on_the_front` (reads Deli
                                    Counter's schema through `tests.siblings`: a second side there fails it)
CHANGELOG and VERSION from `lf_merge_fire_escape/CHANGELOG_0.209.0.md`; `--results-pending` leaves the
RESULT_ keys to `--fill`.

Read before it was written, in this session: `merge_empties.gd` (header, `_side`, the slot loop, `_key`'s
grouping by side, material name, format and uv1 flags), `test_merge_empties.py` (imports, the stoop's test),
`tests/siblings.py` (`sibling_repo`, `not_found`), `test_sibling_locator.py`'s guard, Deli Counter's
`schema/level.schema.json` (`properties.fire_escape_stack`), and 9303's walk-up scenes and fire escape GLBs.
Every file LF; the GDScript tab-indented.

    python patches/patch_lf_merge_fire_escape.py --results-pending
    (python -m pytest -q in level_factory; exit 0 and the tally)
    python patches/patch_lf_merge_fire_escape.py --fill
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_merge_fire_escape"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_MERGE": "result_merge.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.208.0", b"0.209.0"
CHANGELOG_HEAD = "## [0.208.0] - Every animated Lux rig at rest before the applied scene is packed"
SHA = {"assets/godot/merge_empties.gd": "92bcc64885653e5f",
       "tests/unit/test_merge_empties.py": "2c2c3716be1ea066"}

EDITS = {
    "assets/godot/merge_empties.gd": [
        ("##     `parapet_<N|E|S|W>_*`, `roof_*` (side R), `stoop_*` (side S: a\n"
         "##     rowhome's stoop, at its front door, 0.196.0) -- is taken apart. Its\n",
         "##     `parapet_<N|E|S|W>_*`, `roof_*` (side R), `stoop_*` (side S: a\n"
         "##     rowhome's stoop, at its front door, 0.196.0), `fire_escape_*` (side S:\n"
         "##     a walk-up's fire escape, on its front, 0.209.0) -- is taken apart. Its\n"),
        ("\tif slot_name.begins_with(\"stoop_\"):\n"
         "\t\treturn \"S\"\n"
         "\treturn \"\"\n",
         "\tif slot_name.begins_with(\"stoop_\"):\n"
         "\t\treturn \"S\"\n"
         "\t# A WALK-UP'S FIRE ESCAPE (0.209.0, Deli Counter 0.220.0): Deli Counter stands\n"
         "\t# it on the front, the S wall -- `fire_escape_stack.plan` knows no other side --\n"
         "\t# so its storeys and its drop join the front's groups, one mesh with the rest of\n"
         "\t# that side's painted steel, where each drew as a module of its own: four to six\n"
         "\t# a walk-up, 28 on cold run 9303's picked candidate.\n"
         "\tif slot_name.begins_with(\"fire_escape_\"):\n"
         "\t\treturn \"S\"\n"
         "\treturn \"\"\n"),
    ],
    "tests/unit/test_merge_empties.py": [
        ("from packages.exporting import merge_empties as M  # noqa: E402\n",
         "from packages.exporting import merge_empties as M  # noqa: E402\n"
         "from tests.siblings import not_found, sibling_repo  # noqa: E402\n"),
        ("    rule = side.index('if slot_name.begins_with(\"stoop_\"):')\n"
         "    assert side[rule:].split(\"\\n\")[1].strip() == 'return \"S\"'\n"
         "    # before the catch-all: a stoop is never left without a side\n"
         "    assert rule < side.rindex('return \"\"')\n",
         "    rule = side.index('if slot_name.begins_with(\"stoop_\"):')\n"
         "    assert side[rule:].split(\"\\n\")[1].strip() == 'return \"S\"'\n"
         "    # before the catch-all: a stoop is never left without a side\n"
         "    assert rule < side.rindex('return \"\"')\n"
         "\n"
         "\n"
         "def test_a_walk_up_s_fire_escape_merges_with_its_front():\n"
         "    \"\"\"0.209.0: Deli Counter 0.220.0's fire escape slots (`fire_escape_<storey>`,\n"
         "    `fire_escape_drop`) give no side in their names, and each drew as a module of its\n"
         "    own: four to six a walk-up, 28 on cold run 9303's picked candidate. `_side` gives\n"
         "    them the front's, S, where Deli Counter stands the stack. The rule runs only inside\n"
         "    Godot: this holds its source to it, and a cold run's `merge_empties.json` measures\n"
         "    it.\"\"\"\n"
         "    text = M.MERGE_SCRIPT.read_text(encoding=\"utf-8\")\n"
         "    side = text[text.index(\"func _side(\"):text.index(\"func _walk(\")]\n"
         "    rule = side.index('if slot_name.begins_with(\"fire_escape_\"):')\n"
         "    assert side[rule:].split(\"\\n\")[1].strip() == 'return \"S\"'\n"
         "    # before the catch-all: no storey of it is left without a side\n"
         "    assert rule < side.rindex('return \"\"')\n"
         "\n"
         "\n"
         "_DC_SCHEMA = \"schema/level.schema.json\"\n"
         "\n"
         "\n"
         "def test_deli_counter_stands_a_fire_escape_only_on_the_front():\n"
         "    \"\"\"The rule above is right only while the front is the one side Deli Counter\n"
         "    stands a fire escape on, which its schema's `fire_escape_stack` enum says. A second\n"
         "    side there means the merge must learn to tell the two apart -- a back stack given\n"
         "    S would be merged into the front's mesh -- and this fails first. Skipped where\n"
         "    Deli Counter cannot be found; a schema without the field fails, since it is not\n"
         "    the Deli Counter this rule was written against (0.220.0).\"\"\"\n"
         "    dc = sibling_repo(\"deli_counter\", marker=_DC_SCHEMA)\n"
         "    if dc is None:\n"
         "        pytest.skip(not_found(\"deli_counter\", marker=_DC_SCHEMA))\n"
         "    props = json.loads((dc / _DC_SCHEMA).read_text(encoding=\"utf-8\")).get(\"properties\") or {}\n"
         "    assert \"fire_escape_stack\" in props, \"no fire_escape_stack in %s\" % (dc / _DC_SCHEMA)\n"
         "    assert props[\"fire_escape_stack\"].get(\"enum\") == [\"front\", None], props[\"fire_escape_stack\"]\n"),
    ],
}


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def fill():
    assert (LF / "VERSION").read_bytes().strip() == VERSION, (LF / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value and not value.endswith("."), (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.209.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.209.0: results filled")


def main():
    if FILL:
        return fill()
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.209.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.209.0] - "), entry[:40]
    left = entry
    for key in RESULTS if PENDING else ():
        left = left.replace(key, "")
    assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    writes = {}
    for rel, pairs in EDITS.items():
        p = LF / rel
        raw = p.read_bytes()
        got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
        assert got == SHA[rel], (rel, "is not the file this patch read", got)
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for old, new in pairs:
            assert text.count(old) == 1, (rel, "anchor", text.count(old), old[:80])
            text = text.replace(old, new)
        writes[p] = text.encode("utf-8").replace(b"\n", eol)
    cl = LF / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD), cl_text[:120]
    # every anchor matched: now write
    for p, data in writes.items():
        p.write_bytes(data)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).encode("utf-8").replace(b"\n", cl_eol))
    (LF / "VERSION").write_bytes(VERSION)
    print("Level Factory 0.208.0 -> 0.209.0")


if __name__ == "__main__":
    main()
