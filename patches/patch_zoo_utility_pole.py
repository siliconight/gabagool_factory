"""Zoo 1.104.0: a wooden utility pole (factory roadmap 240, the pole line's first build).

New files, each refused if it exists:
  zoo_keeper/core/utility_pole_forms.py      the pole in numbers, pure (`utility_pole_forms.py.txt`)
  zoo_keeper/recipes/utility_pole.py         the recipe (`utility_pole.py.txt`)
  zoo_keeper/genome/species/utility_pole.json   the genome (`utility_pole.json.txt`)
  tests/test_utility_pole.py                 seventeen tests (`test_utility_pole.py.txt`)
Anchored edits, each asserted once, nothing written until all of them matched:
  zoo_keeper/genome/minted.json     "utility_pole" between "traffic_signal" and "water_barrel"
  tests/test_coincident_faces.py    CENSUS_BUILDS 387 -> 390, the census line above it
CHANGELOG and VERSION from `zoo_utility_pole/CHANGELOG_1.104.0.md`; `--results-pending` leaves the
RESULT_ keys to `--fill`.

Read before it was written: tools/new_species.py's scaffold of the species in a copy of the repo;
`tools/coplanar_census.py --species utility_pole` and a `zoo_cli --build-kit` of both forms in that
copy, Blender 5.1.1.

    python patches/patch_zoo_utility_pole.py --results-pending && cd zoo && python -m pytest -q
    python patches/patch_zoo_utility_pole.py --fill
    ZOO_ROOT=<copy> python patches/patch_zoo_utility_pole.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ZOO = pathlib.Path(os.environ.get("ZOO_ROOT") or HERE.parent / "zoo")
SRC = HERE / "zoo_utility_pole"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_FAIL_FIRST": "result_fail_first.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"1.103.0", b"1.104.0"
CHANGELOG_HEAD = "## [1.103.0] - a mesh leaves with its faces in one order, the same every build\n"
NEW = {"zoo_keeper/core/utility_pole_forms.py": "utility_pole_forms.py.txt",
       "zoo_keeper/recipes/utility_pole.py": "utility_pole.py.txt",
       "zoo_keeper/genome/species/utility_pole.json": "utility_pole.json.txt",
       "tests/test_utility_pole.py": "test_utility_pole.py.txt"}
MINTED = "zoo_keeper/genome/minted.json"
CENSUS = "tests/test_coincident_faces.py"
SHA = {MINTED: "cb5fa78d6c526152", CENSUS: "c1e7e94c670b0ee9"}

MINTED_OLD = ' "traffic_signal",\n "water_barrel"\n'
MINTED_NEW = ' "traffic_signal",\n "utility_pole",\n "water_barrel"\n'
CENSUS_OLD = "CENSUS_BUILDS = 387\n"
CENSUS_NEW = (
    "#: 1.104.0: `utility_pole`, three builds more, same tool, Blender 5.1.1 --\n"
    "#: `blender -b --python tools/coplanar_census.py -- --species utility_pole`:\n"
    "#: \"3 builds, 0 with coincident pairs, 0 that did not build\", 496 / 496 /\n"
    "#: 496 tris. Every part that meets another is sunk 10 mm into it\n"
    "#: (`utility_pole_forms.SINK`) and the lens hangs 4 mm under its head, so\n"
    "#: `prims.coincident_pairs` reads 0 on both forms before Blender does.\n"
    "CENSUS_BUILDS = 390\n")


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def _src(name):
    return (SRC / name).read_bytes().decode("utf-8").replace("\r\n", "\n")


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def _read(rel):
    p = ZOO / rel
    raw = p.read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA[rel], (rel, "is not the file this patch read", got)
    return p, _eol(raw, rel), raw.decode("utf-8").replace("\r\n", "\n")


def _write(p, eol, text):
    p.write_bytes(text.replace("\n", eol.decode()).encode("utf-8"))


def fill():
    assert (ZOO / "VERSION").read_bytes().strip() == VERSION, (ZOO / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value and not value.endswith("."), (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(ZOO / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_1.104.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Zoo 1.104.0: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("ZOO_ROOT"):
        sys.exit("refusing: --draft is for a ZOO_ROOT copy, never the repo")
    assert (ZOO / "VERSION").read_bytes().strip() == VERSION_WAS, (ZOO / "VERSION").read_bytes()
    entry = _src("CHANGELOG_1.104.0.md")
    assert entry.startswith("## [1.104.0] - "), entry[:40]
    if not DRAFT:
        left = entry
        if PENDING:
            for key in RESULTS:
                left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    for rel in NEW:
        assert not (ZOO / rel).exists(), (rel, "already exists")
    new_text = {rel: _src(name) for rel, name in NEW.items()}
    mp, m_eol, minted = _read(MINTED)
    minted = _once(minted, MINTED_OLD, MINTED_NEW, "minted.json's tail")
    cp, c_eol, census = _read(CENSUS)
    census = _once(census, CENSUS_OLD, CENSUS_NEW, "CENSUS_BUILDS")
    cl = ZOO / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:160]
    # every anchor matched: now write
    for rel, text in new_text.items():
        (ZOO / rel).write_bytes(text.encode("utf-8"))
    _write(mp, m_eol, minted)
    _write(cp, c_eol, census)
    _write(cl, cl_eol, entry.rstrip("\n") + "\n\n" + cl_text)
    (ZOO / "VERSION").write_bytes(VERSION)
    print("Zoo 1.103.0 -> 1.104.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
