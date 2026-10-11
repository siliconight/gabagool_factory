"""Zoo 1.98.0: the dome a home's room hangs (roadmap 229's species step).

New files `zoo_keeper/genome/species/dome_fixture.json` and `zoo_keeper/recipes/dome_fixture.py`
(from `zoo_dome/`); anchored edits in `zoo_keeper/core/fixtures.py` (the `dome` row, mount
'hang'), `tests/test_genome.py` (the species in PROP_SPECIES), `tests/test_fixtures.py` (a dome
anchor gets hardware, hung), `tests/test_coincident_faces.py` (the census note and 3 builds more)
and `tests/test_theme_style_resolution.py` (102 hand-styled species); each file pinned by hash
and each anchor asserted once, nothing written on a miss; the
files' own line endings kept. Applies on Zoo 1.97.0. CHANGELOG and VERSION from
`zoo_dome/CHANGELOG_1.98.0.md`; `--suite-pending` leaves RESULT_SUITE to `--fill`.

    python patches/patch_zoo_dome.py --suite-pending && cd zoo && python -m pytest -q
    python patches/patch_zoo_dome.py --fill
    ZOO_ROOT=<copy> python patches/patch_zoo_dome.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ZOO = pathlib.Path(os.environ.get("ZOO_ROOT") or HERE.parent / "zoo")
SRC = HERE / "zoo_dome"
DRAFT = "--draft" in sys.argv
PENDING = "--suite-pending" in sys.argv
FILL = "--fill" in sys.argv
VERSION_WAS, VERSION = b"1.97.0", b"1.98.0"
CHANGELOG_HEAD = "## [1.97.0] - the backdrop tree with a silhouette\n"
SHA = {"zoo_keeper/core/fixtures.py": "bfbb0210e4816204",
       "tests/test_fixtures.py": "3a0abf246366c5e6",
       "tests/test_genome.py": "deb42b90a743ded2",
       "tests/test_coincident_faces.py": "7a83174a1e290f47",
       "tests/test_theme_style_resolution.py": "57c56182cf7be77b"}
STY_OLD = "    # `delco` row.\n    assert len(_genomes()) == 101 + len(_minted), len(_genomes())\n"
STY_NEW = ("    # `delco` row.\n"
           "    # 1.98.0: 102, + dome_fixture, a home's dome, with its own `delco` row.\n"
           "    assert len(_genomes()) == 102 + len(_minted), len(_genomes())\n")
NEW = {"zoo_keeper/genome/species/dome_fixture.json": "dome_fixture.json",
       "zoo_keeper/recipes/dome_fixture.py": "dome_fixture.py"}

ROW_OLD = '    "counter_accent": {"species": "pendant_fixture", "mount": "above"},\n'
ROW_NEW = (ROW_OLD +
           "    # 1.98.0, A HOME'S DOME (Deli Counter 0.208.0, roadmap 229): a home's room\n"
           "    # took the office troffer until its fixture had a species. Deli Counter\n"
           "    # writes the anchor at the ceiling plane, so the dome HANGS -- its top at\n"
           "    # the emitter, the glass below -- the way the club's cans do; Lux hangs\n"
           "    # the lamp under the glass (its DOME_LAMP_DROP_M).\n"
           '    "dome": {"species": "dome_fixture", "mount": "hang"},\n')
GEN_OLD = ('                # basements and objective rooms; roadmap 57\'s 90s palette)\n'
           '                "pendant_fixture",\n')
GEN_NEW = (GEN_OLD +
           "                # a home's flush-mount dome (1.98.0, roadmap 229's species)\n"
           '                "dome_fixture",\n')
CEN_OLD = "#: its roof from the start.\nCENSUS_BUILDS = 384\n"
CEN_NEW = ("#: its roof from the start.\n"
           "#: 1.98.0: `dome_fixture`, three builds more, same tool, Blender 5.1.1 --\n"
           "#: `blender -b --python tools/coplanar_census.py -- --species dome_fixture\n"
           "#: pendant_fixture`, the pendant run beside it as the control that the census\n"
           "#: can see a pair (its known one, cover 35.62 / 52.62 / 49.62 mm, as the\n"
           "#: RESIDUE row says) -- reported the dome's three corners at 292 / 292 / 292\n"
           "#: tris, 0 pairs, first run: the glass's rim is closed by the canopy's\n"
           "#: underside rather than laid on it, and the finial sinks half into the glass.\n"
           "#: 292 is where its genome budget came from.\n"
           "CENSUS_BUILDS = 387\n")
FIX_TEST = '''

# --------------------------------------------------------------------------- #
# 1.98.0: a home's room hangs a dome (roadmap 229's species step)
# --------------------------------------------------------------------------- #

def test_a_dome_anchor_gets_its_hardware_hung_from_the_ceiling():
    """Deli Counter 0.208.0 writes a home's room as `dome` anchors at the
    ceiling plane; a type with no row here is skipped, and a skipped anchor
    emits no marker -- a dark room. The dome hangs: top at the emitter."""
    p = fixtures.plan(_manifest([
        {"id": "bedroom_ceiling", "type": "dome", "pos": [0, 0, 2.9],
         "row": {"count": 2, "spacing": 7.0}, "drop": 2.9}]))
    assert not p["skipped"]
    assert len(p["placements"]) == 2
    for pl in p["placements"]:
        assert pl["species"] == "dome_fixture" and pl["mount"] == "hang"
        assert pl["drop"] == 2.9
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


def _fill():
    cl = ZOO / "CHANGELOG.md"
    raw = cl.read_bytes()
    eol = _eol(raw, "CHANGELOG.md")
    text = raw.decode("utf-8").replace("\r\n", "\n")
    value = (SRC / "result_suite.txt").read_bytes().decode("utf-8").replace("\r\n", "\n").strip()
    assert value and not value.endswith("."), "result_suite.txt must be one sentence without its final stop"
    text = _once(text, "RESULT_SUITE", value, "RESULT_SUITE")
    cl.write_bytes(text.replace("\n", eol.decode()).encode("utf-8"))
    print("Zoo 1.98.0's changelog filled")


def main():
    if DRAFT and not os.environ.get("ZOO_ROOT"):
        sys.exit("refusing: --draft is for a ZOO_ROOT copy, never the repo")
    if FILL:
        _fill()
        return
    assert (ZOO / "VERSION").read_bytes().strip() == VERSION_WAS, (ZOO / "VERSION").read_bytes()
    entry = _src("CHANGELOG_1.98.0.md")
    assert entry.startswith("## [1.98.0] - "), entry[:40]
    if not DRAFT and not PENDING:
        assert "RESULT_" not in entry, "the changelog still carries an unfilled result"
    for rel in NEW:
        assert not (ZOO / rel).exists(), f"{rel} already exists"

    fp, f_eol, fx = _read("zoo_keeper/core/fixtures.py")
    assert '"dome"' not in fx, "already applied"
    fx = _once(fx, ROW_OLD, ROW_NEW, "fixtures row")
    gp, g_eol, gen = _read("tests/test_genome.py")
    gen = _once(gen, GEN_OLD, GEN_NEW, "genome species")
    tp, t_eol, tfx = _read("tests/test_fixtures.py")
    assert tfx.endswith("\n")
    tfx = tfx.rstrip("\n") + "\n" + FIX_TEST
    cp, c_eol, cen = _read("tests/test_coincident_faces.py")
    cen = _once(cen, CEN_OLD, CEN_NEW, "census builds")
    sp, s_eol, sty = _read("tests/test_theme_style_resolution.py")
    sty = _once(sty, STY_OLD, STY_NEW, "styled species count")

    cl = ZOO / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:120]
    news = {rel: _src(name) for rel, name in NEW.items()}
    # Every pin and anchor matched: now write.
    fp.write_bytes(fx.replace("\n", f_eol.decode()).encode("utf-8"))
    gp.write_bytes(gen.replace("\n", g_eol.decode()).encode("utf-8"))
    tp.write_bytes(tfx.replace("\n", t_eol.decode()).encode("utf-8"))
    cp.write_bytes(cen.replace("\n", c_eol.decode()).encode("utf-8"))
    sp.write_bytes(sty.replace("\n", s_eol.decode()).encode("utf-8"))
    for rel, text in news.items():
        (ZOO / rel).write_bytes(text.replace("\n", f_eol.decode()).encode("utf-8"))
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).replace("\n", cl_eol.decode()).encode("utf-8"))
    (ZOO / "VERSION").write_bytes(VERSION)
    print("Zoo 1.97.0 -> 1.98.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
