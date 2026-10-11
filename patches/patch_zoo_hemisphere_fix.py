"""Zoo 1.99.1: `geometry.add_hemisphere` keeps the upper half it names, every vertex scaled (roadmap 232).

Anchored edits: in `zoo_keeper/bpylayer/geometry.py` the whole `add_hemisphere` function, located
by its own `def` and the next one's and pinned by the block's hash (its old body carries line
continuations, so it is not quoted here); in `zoo_keeper/recipes/bollard.py` the cap built inside
the height; in `zoo_keeper/recipes/dome_fixture.py` one docstring paragraph; in
`tests/test_coincident_faces.py` the two rows and the total the census reads differently once the
caps stand up; and a new `tests/test_hemisphere.py`. Each file pinned by hash and each anchor asserted once, nothing written
on a miss; the files' own line endings kept. Applies on Zoo 1.99.0. CHANGELOG and VERSION from
`zoo_hemisphere_fix/CHANGELOG_1.99.1.md`; `--results-pending` leaves the RESULT_ keys to `--fill`.

    python patches/patch_zoo_hemisphere_fix.py --results-pending && cd zoo && python -m pytest -q
    python patches/patch_zoo_hemisphere_fix.py --fill
    ZOO_ROOT=<copy> python patches/patch_zoo_hemisphere_fix.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ZOO = pathlib.Path(os.environ.get("ZOO_ROOT") or HERE.parent / "zoo")
SRC = HERE / "zoo_hemisphere_fix"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_SUITE": "result_suite.txt", "RESULT_BPY": "result_bpy.txt",
           "RESULT_CENSUS": "result_census.txt"}
VERSION_WAS, VERSION = b"1.99.0", b"1.99.1"
CHANGELOG_HEAD = "## [1.99.0] - a container's roof is the dirty face it is from above\n"
GEOMETRY = "zoo_keeper/bpylayer/geometry.py"
BOLLARD = "zoo_keeper/recipes/bollard.py"
DOME = "zoo_keeper/recipes/dome_fixture.py"
TEST = "tests/test_hemisphere.py"
CENSUS = "tests/test_coincident_faces.py"
SHA = {GEOMETRY: "24a00fd24dfc22bc", BOLLARD: "c57891e2f5368bb0", DOME: "f70b54c39a294ca1",
       CENSUS: "57127f1676ecdf2f"}
HEMI_START, HEMI_END, HEMI_SHA = "def add_hemisphere(", "\n\n\ndef add_ellipsoid(", "05e30dababf34075"

HEMI_NEW = '''def add_hemisphere(bm, center, radius_x, radius_y, radius_z, segments=20):
    """Upper hemisphere shell (open bottom), squashed to per-axis radii: the
    rim at ``center``, the crown ``radius_z`` above it. Returns every vertex
    it leaves, each one transformed.

    1.99.1. Until then the bisect's normal pointed down, and ``clear_inner``
    clears the side behind the normal, so it kept the LOWER half and every
    caller's cap hung inside its own body: the bollard's under its pipe's flat
    top, the exhaust fan's around its drum, the soda cup's under its lid, the
    helmet's whole shell below its rim. And at an odd ring count --
    ``segments`` 14, 18, 22 ... -- no ring lies on the cut, the bisect makes
    the rim's vertices new, and only the sphere's own were transformed: 14
    vertices left at radius 0.975 on a hemisphere asked for at 0.5. Measured
    in Blender 5.1.1, ``docs/findings/hemisphere_half/`` in the factory. The
    cut's vertices are transformed with the rest now, and a bisect that left
    nothing raises rather than falling back to every vertex in the bmesh,
    which other parts share.
    """
    ret = bmesh.ops.create_uvsphere(
        bm, u_segments=segments, v_segments=max(6, segments // 2),
        radius=1.0)
    verts = ret["verts"]
    geom = (verts + [e for v in verts for e in v.link_edges]
            + [f for v in verts for f in v.link_faces])
    cut = bmesh.ops.bisect_plane(
        bm, geom=list(set(geom)), dist=1e-5,
        plane_co=(0, 0, 0), plane_no=(0, 0, 1), clear_inner=True)
    mine = set(verts)
    mine.update(g for g in cut["geom_cut"] if isinstance(g, bmesh.types.BMVert))
    keep = [v for v in bm.verts if v.is_valid and v in mine]
    if not keep:
        raise ValueError("add_hemisphere: the bisect left no vertex")
    mat = Matrix.Translation(Vector(center)) @ Matrix.Diagonal(
        Vector((radius_x, radius_y, radius_z)).to_4d())
    bmesh.ops.transform(bm, matrix=mat, verts=keep)
    return keep'''

CONST_OLD = "FOOT_H = 0.05\nBAND_H = 0.12\n"
CONST_NEW = (CONST_OLD +
             "#: The domed cap's rise, as a share of the foot's radius.\n"
             "CAP_RISE = 0.42\n")
BODY_OLD = ("    pipe_h = h - FOOT_H\n"
            "    geometry.add_cylinder(bm, (0.0, 0.0, z0 + FOOT_H + pipe_h / 2.0),\n"
            "                          r * 0.72, pipe_h, segments=10)\n"
            "    geometry.add_hemisphere(bm, (0.0, 0.0, h / 2.0), r * 0.72, r * 0.72,\n"
            "                            r * 0.42, segments=10)\n")
BODY_NEW = ("    # THE CAP STANDS INSIDE THE HEIGHT (1.99.1). Until then the cap hung inside\n"
            "    # the pipe -- `add_hemisphere` kept its lower half -- and the bollard was\n"
            "    # flat-topped. The pipe stops short by the cap's rise, so the crown lands\n"
            "    # at h/2 and `fit_to` has nothing to scale; the bands keep their heights.\n"
            "    run = h - FOOT_H\n"
            "    cap_h = r * CAP_RISE\n"
            "    pipe_h = run - cap_h\n"
            "    geometry.add_cylinder(bm, (0.0, 0.0, z0 + FOOT_H + pipe_h / 2.0),\n"
            "                          r * 0.72, pipe_h, segments=10)\n"
            "    geometry.add_hemisphere(bm, (0.0, 0.0, h / 2.0 - cap_h), r * 0.72,\n"
            "                            r * 0.72, cap_h, segments=10)\n")
BANDS_OLD = "        geometry.add_cylinder(bm, (0.0, 0.0, z0 + FOOT_H + pipe_h * frac),\n"
BANDS_NEW = "        geometry.add_cylinder(bm, (0.0, 0.0, z0 + FOOT_H + run * frac),\n"
DOME_OLD = ("keeps. Its rim rises `BOWL_BURY` into the canopy and is closed there, so the\n"
            "glass is a closed shell -- the finisher recalculates every part's normals,\n"
            "and an open bowl leaves it no inside to face away from -- and the cap lies\n"
            "4 mm from the canopy's underside, clear of the coplanar probe's 2 mm.\n")
DOME_NEW = ("keeps; 1.99.1 made the helper keep the upper half it names, and the bowl\n"
            "builds the same either way. Its rim rises `BOWL_BURY` into the canopy and\n"
            "is closed there, so the glass is a closed shell -- the finisher\n"
            "recalculates every part's normals, and an open bowl leaves it no inside to\n"
            "face away from -- and the cap lies 4 mm from the canopy's underside, clear\n"
            "of the coplanar probe's 2 mm.\n")
# The coincident-face table: two rows the census reads differently once the caps stand up.
SODA_OLD = '    "soda_cup": (7, 3, 4, 0, 0.21, 84.0),\n'
SODA_NEW = ('    # "soda_cup" covered 0.21 mm until 1.99.1, and the cover was its lid dome:\n'
            '    # hanging inside the cup, the bowl passed 0.21 mm from the body and lip\'s\n'
            '    # pair. On its lid since, the nearest surface is the lid\'s underside.\n'
            '    "soda_cup": (7, 3, 4, 0, 2.0, 84.0),\n')
FAN_OLD = '    "exhaust_fan": (3, 0, 3, 0, 50.92, 3567.1),\n'
LIGHT_OLD = '    "streetlight": (4, 0, 4, 0, 60.0, 87.7),\n'
LIGHT_NEW = (LIGHT_OLD +
             '    # "exhaust_fan": (3, 0, 3, 0, 50.92, 3567.1) until 1.99.1 stood its hood on\n'
             '    # its drum. The census counts the one buried coincidence it had at the\n'
             '    # default corner -- the drum\'s foot on the curb, 1725.46 cm2 -- as two\n'
             '    # pairs since, 1150.31 and 575.15 cm2: the same parts and the same area.\n'
             '    "exhaust_fan": (4, 0, 4, 0, 120.0, 3567.1),\n')
TOTAL_DOC_OLD = '    1.88.0 redrew the payphone, and its 2 (both exposed) went: 2995."""\n'
TOTAL_DOC_NEW = ('    1.88.0 redrew the payphone, and its 2 (both exposed) went: 2995. 1.99.1\n'
                 '    stood the exhaust fan\'s hood on its drum, and the census counts the\n'
                 '    fan\'s one buried pair at the default corner as two: 2996, and no\n'
                 '    coincidence more."""\n')
TOTAL_OLD = '    assert total == 2995, total\n'
TOTAL_NEW = '    assert total == 2996, total\n'
SUM_OLD = "    assert total + 18 + 6 + 6 + 2 == 3027      # 0.96.0's, the ATM's, sign_box's, the payphone's\n"
SUM_NEW = ("    # 0.96.0's, the ATM's, sign_box's and the payphone's went; the fan's split\n"
           "    assert total + 18 + 6 + 6 + 2 - 1 == 3027\n")


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
    for path, rel in [(ZOO / "CHANGELOG.md", "CHANGELOG.md"),
                      (SRC / "CHANGELOG_1.99.1.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Zoo 1.99.1: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("ZOO_ROOT"):
        sys.exit("refusing: --draft is for a ZOO_ROOT copy, never the repo")
    assert (ZOO / "VERSION").read_bytes().strip() == VERSION_WAS, (ZOO / "VERSION").read_bytes()
    entry = _src("CHANGELOG_1.99.1.md")
    assert entry.startswith("## [1.99.1] - "), entry[:40]
    if not DRAFT:
        left = entry
        if PENDING:
            for key in RESULTS:
                left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    test_text = _src("test_hemisphere.py.txt")
    assert not (ZOO / TEST).exists(), "already applied"

    gp, g_eol, geo = _read(GEOMETRY)
    assert geo.count(HEMI_START) == 1 and geo.count(HEMI_END) == 1, "the helper's bounds"
    a, b = geo.index(HEMI_START), geo.index(HEMI_END)
    got = hashlib.sha256(geo[a:b].encode("utf-8")).hexdigest()[:16]
    assert got == HEMI_SHA, ("add_hemisphere is not the block this patch read", got)
    geo = geo[:a] + HEMI_NEW + geo[b:]

    bp, b_eol, bol = _read(BOLLARD)
    assert "CAP_RISE" not in bol, "already applied"
    bol = _once(bol, CONST_OLD, CONST_NEW, "the bollard's constants")
    bol = _once(bol, BODY_OLD, BODY_NEW, "the pipe and its cap")
    bol = _once(bol, BANDS_OLD, BANDS_NEW, "the bands")

    dp, d_eol, dome = _read(DOME)
    dome = _once(dome, DOME_OLD, DOME_NEW, "the dome's paragraph")

    cp, c_eol, cen = _read(CENSUS)
    cen = _once(cen, SODA_OLD, SODA_NEW, "the soda cup's row")
    cen = _once(cen, FAN_OLD, "", "the exhaust fan's row")
    cen = _once(cen, LIGHT_OLD, LIGHT_NEW, "the streetlight's row")
    cen = _once(cen, TOTAL_DOC_OLD, TOTAL_DOC_NEW, "the total's history")
    cen = _once(cen, TOTAL_OLD, TOTAL_NEW, "the total")
    cen = _once(cen, SUM_OLD, SUM_NEW, "the sum")

    cl = ZOO / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:120]
    # every anchor matched: now write
    _write(gp, g_eol, geo)
    _write(bp, b_eol, bol)
    _write(dp, d_eol, dome)
    _write(cp, c_eol, cen)
    (ZOO / TEST).write_bytes(test_text.encode("utf-8"))
    _write(cl, cl_eol, entry.rstrip("\n") + "\n\n" + cl_text)
    (ZOO / "VERSION").write_bytes(VERSION)
    print("Zoo 1.99.0 -> 1.99.1" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
