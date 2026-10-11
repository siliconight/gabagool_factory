"""Zoo 1.99.0: a container's roof is the dirty face it is from above (cold run 9226's pale slab).

Anchored edits in `zoo_keeper/recipes/cargo_container.py` (`_Wall.sheet` takes an optional fixed
shade; the roof sheet passes the valley shade) and a test appended to
`tests/test_cargo_container.py`; each file pinned by hash and each anchor asserted once, nothing
written on a miss; the files' own line endings kept. Applies on Zoo 1.98.0. CHANGELOG and VERSION
from `zoo_container_roof/CHANGELOG_1.99.0.md`; `--results-pending` leaves RESULT_SUITE and
RESULT_CENSUS to `--fill`.

    python patches/patch_zoo_container_roof.py --results-pending && cd zoo && python -m pytest -q
    python patches/patch_zoo_container_roof.py --fill
    ZOO_ROOT=<copy> python patches/patch_zoo_container_roof.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ZOO = pathlib.Path(os.environ.get("ZOO_ROOT") or HERE.parent / "zoo")
SRC = HERE / "zoo_container_roof"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_SUITE": "result_suite.txt", "RESULT_CENSUS": "result_census.txt"}
VERSION_WAS, VERSION = b"1.98.0", b"1.99.0"
CHANGELOG_HEAD = "## [1.98.0] - the dome a home's room hangs\n"
RECIPE = "zoo_keeper/recipes/cargo_container.py"
TESTS = "tests/test_cargo_container.py"
SHA = {RECIPE: "c3add958dd1d9ace", TESTS: "ede08e137a577cdb"}

SHEET_OLD = ("    def sheet(self, bm, v0, v1):\n"
             "        rows = [[bm.verts.new(self.base(u, v) + self.n * off)\n")
SHEET_NEW = ("    def sheet(self, bm, v0, v1, shade=None):\n"
             "        \"\"\"The sheet between ``v0`` and ``v1``, each face on its profile\n"
             "        segment's FORM_SHADE -- or on ``shade`` for every face when given\n"
             "        (1.99.0: the roof, see ROOF_SHADE).\"\"\"\n"
             "        rows = [[bm.verts.new(self.base(u, v) + self.n * off)\n")
FORM_OLD = "            f[form] = cf.FORM_SHADE[cf.segment_kind(self.pts, um)]\n"
FORM_NEW = ("            f[form] = (shade if shade is not None\n"
            "                       else cf.FORM_SHADE[cf.segment_kind(self.pts, um)])\n")
ROOF_OLD = ("    _Wall(lambda u, v: _v(v, u, zc), (0, 0, 1), roof_pts).sheet(\n"
            "        B[\"walls\"], -(W2 - TOP_RAIL_SIDE - TOP_RAIL_T + SHEET_BURY),\n"
            "        W2 - TOP_RAIL_SIDE - TOP_RAIL_T + SHEET_BURY)\n")
ROOF_NEW = ("    # THE ROOF IS THE DIRTY FACE (1.99.0). Cold run 9226 saw a container's top\n"
            "    # from the elevated west camera as a bright flat slab, (191, 191, 202) at\n"
            "    # 180 x 40 px, floating over a storefront: the roof took the walls' paint\n"
            "    # at full strength on its crests, and it is the one face square to the\n"
            "    # sky. A box that has sat in a yard wears its weather and its grime on\n"
            "    # top, so every roof face takes ROOF_SHADE -- the walls' own VALLEY shade,\n"
            "    # so it joins a surface the box already has and costs no draw; the ribs\n"
            "    # stop reading from above, where nobody stands close enough to see them.\n"
            "    _Wall(lambda u, v: _v(v, u, zc), (0, 0, 1), roof_pts).sheet(\n"
            "        B[\"walls\"], -(W2 - TOP_RAIL_SIDE - TOP_RAIL_T + SHEET_BURY),\n"
            "        W2 - TOP_RAIL_SIDE - TOP_RAIL_T + SHEET_BURY, shade=ROOF_SHADE)\n")
CONST_OLD = "ROOF_CREST = 0.030            # ROOF_PROFILE depth 0.020 -> valley at 0.050\n"
CONST_NEW = (CONST_OLD +
             "#: Every roof face's shade (1.99.0): the walls' valley, so the roof is the\n"
             "#: darkest face of the box from above and adds no surface to it.\n"
             "ROOF_SHADE = cf.FORM_SHADE[\"valley\"]\n")
TEST = '''

def test_the_roof_takes_the_valley_shade_and_adds_no_surface():
    """1.99.0, cold run 9226's pale slab from above: every roof face takes the
    walls' own valley shade -- the darkest the box has -- so the roof reads as
    the grimy top it is and joins a surface the box already carries."""
    src = open(_RECIPE, encoding="utf-8").read()
    tree = ast.parse(src)
    consts = {t.id: n.value for n in tree.body if isinstance(n, ast.Assign)
              for t in n.targets if isinstance(t, ast.Name)}
    assert "ROOF_SHADE" in consts
    assert ast.unparse(consts["ROOF_SHADE"]) == "cf.FORM_SHADE['valley']"
    assert cf.FORM_SHADE["valley"] == min(cf.FORM_SHADE.values())
    roof = src[src.index("roof_pts).sheet("):]
    roof = roof[:roof.index(")\\n") + 2]
    assert "shade=ROOF_SHADE" in roof, roof
    # the side walls and the end keep their per-rib shades
    assert src.count(".sheet(") == src.count("shade=ROOF_SHADE") + 3, src.count(".sheet(")
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
    assert got == SHA[rel], (rel, "is not the file this patch read", got)
    return p, _eol(raw, rel), raw.decode("utf-8").replace("\r\n", "\n")


def fill():
    assert (ZOO / "VERSION").read_bytes().strip() == VERSION, (ZOO / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value and not value.endswith("."), (name, value[-40:])
        results[key] = value
    targets = [(ZOO / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_1.99.0.md", "the entry")]
    writes = {}
    for path, rel in targets:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Zoo 1.99.0: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("ZOO_ROOT"):
        sys.exit("refusing: --draft is for a ZOO_ROOT copy, never the repo")
    assert (ZOO / "VERSION").read_bytes().strip() == VERSION_WAS, (ZOO / "VERSION").read_bytes()
    entry = _src("CHANGELOG_1.99.0.md")
    assert entry.startswith("## [1.99.0] - "), entry[:40]
    if not DRAFT:
        left = entry
        if PENDING:
            for key in RESULTS:
                left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"

    rp, r_eol, recipe = _read(RECIPE)
    assert "ROOF_SHADE" not in recipe, "already applied"
    recipe = _once(recipe, CONST_OLD, CONST_NEW, "ROOF_CREST")
    recipe = _once(recipe, SHEET_OLD, SHEET_NEW, "sheet def")
    recipe = _once(recipe, FORM_OLD, FORM_NEW, "sheet shade")
    recipe = _once(recipe, ROOF_OLD, ROOF_NEW, "the roof's sheet")
    tp, t_eol, tests = _read(TESTS)
    assert tests.endswith("\n")
    tests = tests.rstrip("\n") + "\n" + TEST

    cl = ZOO / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:120]
    # every anchor matched: now write
    rp.write_bytes(recipe.replace("\n", r_eol.decode()).encode("utf-8"))
    tp.write_bytes(tests.replace("\n", t_eol.decode()).encode("utf-8"))
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).replace("\n", cl_eol.decode()).encode("utf-8"))
    (ZOO / "VERSION").write_bytes(VERSION)
    print("Zoo 1.98.0 -> 1.99.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
