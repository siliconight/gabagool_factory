"""Level Factory 0.196.0: a rowhome's stoop merges with its front (factory roadmap 240; found pricing cold run
9271, Deli Counter 0.211.0's stoops: +22.7 draws a heading on the mean and +93 at the worst against 9270).

`merge_empties.gd` takes apart every slot child of an Empty whose name gives a side -- `ext_<storey>_<side>_*`,
`parapet_<side>_*`, `roof_*` -- and merges its surfaces one mesh a side per material. Deli Counter 0.211.0's
stoop slots, `stoop_landing` and `stoop_tread_<k>`, give none, so each stayed a module drawn on its own: three
an Empty, and 9271's merge report reads exactly as 9270's (95 meshes in, 86 colliders a rowhome). The stoop
stands at the front door, which Deli Counter puts on the S wall (`stoop.front_door` reads only `S`), so
`_side` gives a `stoop_*` slot the front's side.

Anchored edits, each asserted exactly once and every file's sha16 pinned, nothing written until all matched:
  assets/godot/merge_empties.gd     the header's list of sides; `_side` returns "S" for `stoop_*`
  tests/unit/test_merge_empties.py  `test_a_rowhome_s_stoop_merges_with_its_front` (the Godot half runs only
                                    inside Godot, as the file's docstring says; this pins its source, and a
                                    cold run's merge report measures it)
CHANGELOG and VERSION from `lf_merge_stoop/CHANGELOG_0.196.0.md`; `--results-pending` leaves the RESULT_
keys to `--fill`.

Read before it was written, in this session: `merge_empties.gd` (header, `_side`, the slot loop: colliders
copied out under `KitCollision`, mesh surfaces grouped by side, material and format), 9271's
`merge_empties.json`, Deli Counter 0.211.0's `_stoop` slot names and `stoop.front_door`, and
`test_merge_empties.py`. Every file LF; the GDScript tab-indented.

    python patches/patch_lf_merge_stoop.py --results-pending
    (python -m pytest -q in level_factory; exit 0 and the tally)
    python patches/patch_lf_merge_stoop.py --fill
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_merge_stoop"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_MERGE": "result_merge.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.195.0", b"0.196.0"
CHANGELOG_HEAD = "## [0.195.0] - An Empty's stoop stands in the terrace's frontage"
SHA = {"assets/godot/merge_empties.gd": "f5517ed68658feb6",
       "tests/unit/test_merge_empties.py": "420782f1c0f4b4db"}

EDITS = {
    "assets/godot/merge_empties.gd": [
        ("##     `parapet_<N|E|S|W>_*`, `roof_*` (side R) -- is taken apart.",
         "##     `parapet_<N|E|S|W>_*`, `roof_*` (side R), `stoop_*` (side S: a\n"
         "##     rowhome's stoop, at its front door, 0.196.0) -- is taken apart."),
        ("\tif slot_name.begins_with(\"ext_\") and parts.size() > 2 and parts[2] in [\"N\", \"E\", \"S\", \"W\"]:\n"
         "\t\treturn parts[2]\n"
         "\treturn \"\"\n",
         "\tif slot_name.begins_with(\"ext_\") and parts.size() > 2 and parts[2] in [\"N\", \"E\", \"S\", \"W\"]:\n"
         "\t\treturn parts[2]\n"
         "\t# A ROWHOME'S STOOP (0.196.0, Deli Counter 0.211.0): it stands at the front\n"
         "\t# door, which Deli Counter puts on the S wall (`stoop.front_door`), so its\n"
         "\t# pieces join the front's groups -- one mesh a material with the rest of that\n"
         "\t# side -- where each drew as a module of its own: three an Empty, +93 draws at\n"
         "\t# cold run 9271's worst heading.\n"
         "\tif slot_name.begins_with(\"stoop_\"):\n"
         "\t\treturn \"S\"\n"
         "\treturn \"\"\n"),
    ],
    "tests/unit/test_merge_empties.py": [
        ("def test_the_godot_half_ships_with_the_python_half():\n"
         "    assert M.MERGE_SCRIPT.is_file()\n"
         "    text = M.MERGE_SCRIPT.read_text(encoding=\"utf-8\")\n"
         "    assert re.search(r'^const SCHEMA := \"' + re.escape(M.SCHEMA) + '\"$', text, re.M)\n",
         "def test_the_godot_half_ships_with_the_python_half():\n"
         "    assert M.MERGE_SCRIPT.is_file()\n"
         "    text = M.MERGE_SCRIPT.read_text(encoding=\"utf-8\")\n"
         "    assert re.search(r'^const SCHEMA := \"' + re.escape(M.SCHEMA) + '\"$', text, re.M)\n"
         "\n"
         "\n"
         "def test_a_rowhome_s_stoop_merges_with_its_front():\n"
         "    \"\"\"0.196.0: Deli Counter 0.211.0's stoop slots (`stoop_landing`, `stoop_tread_<k>`)\n"
         "    give no side in their names, and each drew as a module of its own (cold run 9271:\n"
         "    +93 draws at its worst heading). `_side` gives them the front's, S, where Deli\n"
         "    Counter stands the stoop. The rule runs only inside Godot: this holds its source to\n"
         "    it, and a cold run's `merge_empties.json` measures it.\"\"\"\n"
         "    text = M.MERGE_SCRIPT.read_text(encoding=\"utf-8\")\n"
         "    side = text[text.index(\"func _side(\"):text.index(\"func _walk(\")]\n"
         "    rule = side.index('if slot_name.begins_with(\"stoop_\"):')\n"
         "    assert side[rule:].split(\"\\n\")[1].strip() == 'return \"S\"'\n"
         "    # before the catch-all: a stoop is never left without a side\n"
         "    assert rule < side.rindex('return \"\"')\n"),
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
    for path, rel in [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.196.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.196.0: results filled")


def main():
    if FILL:
        return fill()
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.196.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.196.0] - "), entry[:40]
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
    print("Level Factory 0.195.0 -> 0.196.0")


if __name__ == "__main__":
    main()
