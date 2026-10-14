"""Zoo 1.110.0: a steel fire escape, a storey a slot, `fire_escape` (factory roadmaps 156 and 241).

The walker's photo of a brick walk-up: "this is something i'd like to see in our toolset, fireescape stairs brick".
The factory's `docs/proposals/FIRE_ESCAPE.md`, step 1.

Anchored edits, each asserted exactly once and every edited file's sha16 pinned, nothing written until all matched:
  zoo_keeper/core/fire_escape_forms.py           NEW (`zoo_fire_escape/fire_escape_forms.py.txt`)
  zoo_keeper/recipes/fire_escape.py              NEW (`zoo_fire_escape/fire_escape.py.txt`)
  zoo_keeper/genome/species/fire_escape.json     NEW (`zoo_fire_escape/fire_escape.json.txt`)
  tests/test_fire_escape.py                      NEW (`zoo_fire_escape/test_fire_escape.py.txt`)
  zoo_keeper/genome/minted.json                  the species, in its place (the file's own 1-space indent kept)
  tests/test_coincident_faces.py                 CENSUS_BUILDS 396 -> 399 and the run that earned it
  tests/test_material_options_closed.py          `fire_escape` on the painted list
CHANGELOG and VERSION from `zoo_fire_escape/CHANGELOG_1.110.0.md`; `--results-pending` leaves the RESULT_ keys to
`--fill`. The census's own log is `zoo_fire_escape/census.log`, run on a copy of Zoo 1.109.0 with these files in it.

Read before it was written, in this session: `core/prims.py` (box, mesh, fit_exact, bounds, tri_count,
coincident_pairs and its 2 mm tolerance), `core/stoop_railing_forms.py` (`sheared`, `pickets`, the NEST and SINK
discipline), its recipe and genome, `core/shop_awning_forms.py`, its recipe, genome and test (the pattern this
follows), `bpylayer/prim_mesh.py`'s call, `recipes/__init__.get` (a recipe by the species' name), `core/dna.py`'s
`_resolve_params` (a list's first option is the default), `tools/coplanar_census.py` (three corners, no form),
`tests/test_coincident_faces.py` and `tests/test_material_options_closed.py` (a `metal_painted` species is listed),
and `genome/minted.json`. Every file LF.

    python patches/patch_zoo_fire_escape.py --results-pending
    (python -m pytest -q tests in zoo; inside Blender, tests/test_fire_escape.py)
    python patches/patch_zoo_fire_escape.py --fill
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ZOO = pathlib.Path(os.environ.get("ZOO_ROOT") or HERE.parent / "zoo")
SRC = HERE / "zoo_fire_escape"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_TESTS": "result_tests.txt", "RESULT_CENSUS": "result_census.txt",
           "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"1.109.0", b"1.110.0"
CHANGELOG_HEAD = ("## [1.109.0] - a bevelled mesh is one mesh every build: each face restarts at its lowest vertex "
                  "after the bevel\n")
MINTED = "zoo_keeper/genome/minted.json"
CENSUS = "tests/test_coincident_faces.py"
METALS = "tests/test_material_options_closed.py"
SHA = {MINTED: "dba73020c69fc237", CENSUS: "8bfcfc04641d506a", METALS: "e5769759c18a41e1"}
NEW = {"zoo_keeper/core/fire_escape_forms.py": "fire_escape_forms.py.txt",
       "zoo_keeper/recipes/fire_escape.py": "fire_escape.py.txt",
       "zoo_keeper/genome/species/fire_escape.json": "fire_escape.json.txt",
       "tests/test_fire_escape.py": "test_fire_escape.py.txt"}

EDITS = {
    MINTED: [(' "fire_hydrant",\n', ' "fire_escape",\n "fire_hydrant",\n')],
    CENSUS: [("#: before Blender does. 48 is the genome's budget.\nCENSUS_BUILDS = 396\n",
              "#: before Blender does. 48 is the genome's budget.\n"
              "#: 1.110.0: `fire_escape`, three builds more, same tool, Blender 5.1.1 --\n"
              "#: `blender -b --python tools/coplanar_census.py -- --species fire_escape\n"
              "#: bollard`, the bollard the control (its known 2 / 2 / 1): \"6 builds, 3 with\n"
              "#: coincident pairs, 0 that did not build\", the fire escape's three corners\n"
              "#: 48 / 1092 / 1464 tris and 0 pairs -- the min corner a drop ladder, the\n"
              "#: others a flight bay, `auto` drawing the form each box can be. The first\n"
              "#: run drew the min corner as a flight and it did not build: a list's first\n"
              "#: option is a plan's default, so the genome lists `auto` first. The deck\n"
              "#: nests in levels, a rail sinks deeper into its post than its section nests\n"
              "#: and the treads stop a step short of the stringers (`fire_escape_forms`),\n"
              "#: so `prims.coincident_pairs` reads 0 over 1,968 sizes before Blender does.\n"
              "#: 1,500 is the genome's budget.\n"
              "CENSUS_BUILDS = 399\n")],
    METALS: [('           # a stoop\'s railing is wrought iron painted black (1.105.0)\n'
              '           "stoop_railing")\n',
              '           # a stoop\'s railing is wrought iron painted black (1.105.0)\n'
              '           "stoop_railing",\n'
              '           # a fire escape is steel painted black (1.110.0)\n'
              '           "fire_escape")\n')],
}


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def fill():
    assert (ZOO / "VERSION").read_bytes().strip() == VERSION, (ZOO / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value, (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(ZOO / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_1.110.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Zoo 1.110.0: results filled")


def main():
    if FILL:
        return fill()
    assert (ZOO / "VERSION").read_bytes().strip() == VERSION_WAS, (ZOO / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_1.110.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [1.110.0] - "), entry[:40]
    left = entry
    for key in RESULTS if PENDING else ():
        left = left.replace(key, "")
    assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    for rel in NEW:
        assert not (ZOO / rel).exists(), ("already applied", rel)
    out = {}
    for rel, edits in EDITS.items():
        raw = (ZOO / rel).read_bytes()
        got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
        assert got == SHA[rel], (rel, "is not the file this patch read", got)
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for old, new in edits:
            assert text.count(old) == 1, (rel, "anchor", text.count(old), old[:60])
            text = text.replace(old, new)
        if rel.endswith(".py"):
            compile(text, rel, "exec")
        out[rel] = (text, eol)
    news = {r: (SRC / s).read_bytes().replace(b"\r\n", b"\n") for r, s in NEW.items()}
    for r, data in news.items():
        if r.endswith(".py"):
            compile(data.decode("utf-8"), r, "exec")
    cl = ZOO / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:160]
    # every anchor matched: now write
    for rel, (text, eol) in out.items():
        (ZOO / rel).write_bytes(text.encode("utf-8").replace(b"\n", eol))
    for r, data in news.items():
        (ZOO / r).write_bytes(data)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).encode("utf-8").replace(b"\n", cl_eol))
    (ZOO / "VERSION").write_bytes(VERSION)
    print("Zoo 1.109.0 -> 1.110.0")


if __name__ == "__main__":
    main()
