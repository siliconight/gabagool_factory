"""Zoo 1.98.1: the dome's glass hangs, and the dome is two meshes (cold run 9239's findings).

Replaces `zoo_keeper/recipes/dome_fixture.py` with `zoo_dome_fix/dome_fixture.py` (the bowl laid by
its depth below the rim and closed inside the canopy; the canopy and finial one mesh) and edits
`zoo_keeper/genome/species/dome_fixture.json` (parts and budget), `tests/test_coincident_faces.py`
(the census note) and appends a test to `tests/test_fixtures.py`; each file pinned by hash and
each anchor asserted once, nothing written on a miss; the files' own line endings kept. Applies
on Zoo 1.98.0. CHANGELOG and VERSION from `zoo_dome_fix/CHANGELOG_1.98.1.md`; `--suite-pending`
leaves RESULT_SUITE to `--fill`.

    python patches/patch_zoo_dome_fix.py --suite-pending && cd zoo && python -m pytest -q
    python patches/patch_zoo_dome_fix.py --fill
    ZOO_ROOT=<copy> python patches/patch_zoo_dome_fix.py --draft
"""
import hashlib
import json
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ZOO = pathlib.Path(os.environ.get("ZOO_ROOT") or HERE.parent / "zoo")
SRC = HERE / "zoo_dome_fix"
DRAFT = "--draft" in sys.argv
PENDING = "--suite-pending" in sys.argv
FILL = "--fill" in sys.argv
VERSION_WAS, VERSION = b"1.98.0", b"1.98.1"
CHANGELOG_HEAD = "## [1.98.0] - the dome a home's room hangs\n"
RECIPE = "zoo_keeper/recipes/dome_fixture.py"
GENOME = "zoo_keeper/genome/species/dome_fixture.json"
CENSUS = "tests/test_coincident_faces.py"
FIXT = "tests/test_fixtures.py"
SHA = {RECIPE: "bb9a21e010a6eaa0", GENOME: "ce8a4bcd97b03db5", CENSUS: "51ae49cef4119612",
       FIXT: "77271cceca1ba99d"}

CEN_OLD = ("#: 292 is where its genome budget came from.\n"
           "CENSUS_BUILDS = 387\n")
CEN_NEW = ("#: 292 is where its genome budget came from.\n"
           "#: 1.98.1: the same three builds after the dome's fix (the bowl laid by its\n"
           "#: depth below the rim and closed 4 mm inside the canopy; the canopy and the\n"
           "#: finial one mesh): 310 / 310 / 310 tris -- the closed rim's 18 -- and 0\n"
           "#: pairs, so the budget is 310 and the clean count does not move.\n"
           "CENSUS_BUILDS = 387\n")
FIX_TEST = '''

def test_the_domes_glass_hangs_closed_and_the_dome_is_two_meshes():
    """1.98.1, cold run 9239: `geometry.add_hemisphere` keeps the LOWER half
    (Blender 5.1.1: z -1 .. 0 at unit radius) though its docstring says upper,
    so 1.98.0's mirror turned the bowl up into the ceiling; and the canopy and
    finial, one material, were two meshes -- three a dome where a troffer is
    two, +6 draws at 24 of 53 headings. Held here by reading the recipe: the
    built frame is measured in Blender, `docs/cold_runs/cold_9239/` in the
    factory."""
    import ast
    import os as _os
    src = open(_os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))),
                             "zoo_keeper", "recipes", "dome_fixture.py"), encoding="utf-8").read()
    assert "rim_z + BOWL_BURY - abs(v.co.z)" in src            # hangs whichever half
    assert "holes_fill" in src                                  # a closed shell
    assert "reverse_faces" not in src
    names = [n.value for n in ast.walk(ast.parse(src))
             if isinstance(n, ast.Constant) and isinstance(n.value, str) and n.value.startswith("Dome_")]
    assert sorted(set(names)) == ["Dome_Canopy", "Dome_Glass"], names
'''


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def _src(name):
    return (SRC / name).read_bytes().replace(b"\r\n", b"\n").decode("utf-8")


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def _read(rel):
    p = ZOO / rel
    raw = p.read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    if SHA.get(rel):
        assert got == SHA[rel], (rel, "is not the file this patch read", got)
    return p, _eol(raw, rel), raw.decode("utf-8").replace("\r\n", "\n")


def _fill():
    cl = ZOO / "CHANGELOG.md"
    raw = cl.read_bytes()
    eol = _eol(raw, "CHANGELOG.md")
    text = raw.decode("utf-8").replace("\r\n", "\n")
    value = (SRC / "result_suite.txt").read_bytes().decode("utf-8").replace("\r\n", "\n").strip()
    assert value and not value.endswith("."), "result_suite.txt must be one sentence without its final stop"
    text = _once(text, "RESULT_SUITE", value, "RESULT_SUITE")
    cl.write_bytes(text.replace("\n", eol.decode()).encode("utf-8"))
    print("Zoo 1.98.1's changelog filled")


def main():
    if DRAFT and not os.environ.get("ZOO_ROOT"):
        sys.exit("refusing: --draft is for a ZOO_ROOT copy, never the repo")
    if FILL:
        _fill()
        return
    assert (ZOO / "VERSION").read_bytes().strip() == VERSION_WAS, (ZOO / "VERSION").read_bytes()
    entry = _src("CHANGELOG_1.98.1.md")
    assert entry.startswith("## [1.98.1] - "), entry[:40]
    if not DRAFT and not PENDING:
        assert "RESULT_" not in entry, "the changelog still carries an unfilled result"

    rp, r_eol, _recipe = _read(RECIPE)
    recipe = _src("dome_fixture.py")
    assert "BOWL_BURY" in recipe and "BOWL_BURY" not in _recipe, "already applied"
    gp, g_eol, genome_text = _read(GENOME)
    genome = json.loads(genome_text)
    assert genome["parts"] == ["Dome_Canopy", "Dome_Glass", "Dome_Finial"], genome["parts"]
    assert genome["budgets"]["tris_lod0"] == 292, genome["budgets"]
    genome["parts"] = ["Dome_Canopy", "Dome_Glass"]
    genome["budgets"]["tris_lod0"] = 310
    cp, c_eol, census = _read(CENSUS)
    census = _once(census, CEN_OLD, CEN_NEW, "census note")
    fp, f_eol, fixt = _read(FIXT)
    assert fixt.endswith("\n") and "test_the_domes_glass_hangs_closed" not in fixt
    fixt = fixt.rstrip("\n") + "\n" + FIX_TEST

    cl = ZOO / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:120]
    # every pin and anchor matched: now write
    rp.write_bytes(recipe.replace("\n", r_eol.decode()).encode("utf-8"))
    gp.write_bytes((json.dumps(genome, indent=1) + "\n").replace("\n", g_eol.decode()).encode("utf-8"))
    cp.write_bytes(census.replace("\n", c_eol.decode()).encode("utf-8"))
    fp.write_bytes(fixt.replace("\n", f_eol.decode()).encode("utf-8"))
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).replace("\n", cl_eol.decode()).encode("utf-8"))
    (ZOO / "VERSION").write_bytes(VERSION)
    print("Zoo 1.98.0 -> 1.98.1" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
