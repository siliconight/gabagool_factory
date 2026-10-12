"""Lot 0.119.0: the pole line's wires -- the full set without house drops, along every line and
across each junction, with the art only (factory roadmap 240, build 3).

Anchored edits, each asserted once, nothing written until all of them matched:
  site_poles.py              the wires appended (`wires.py.txt`): SAG, WIRE_R, `spans`,
                             `wire_path`, `_tube`, `wire_meshes`
  lot.py                     `_outdoor_nodes` draws them after the paint, in a themed site only
  tests/test_site_wires.py   NEW
CHANGELOG and VERSION from `lot_pole_wires/CHANGELOG_0.119.0.md`; `--results-pending` leaves the
RESULT_ keys to `--fill`. Level Factory 0.194.0 keeps them out of the lightmap.

Read before it was written: `_marking_meshes` and `write_godot_scene` (every file `_outdoor_nodes`
returns is written beside the scene and declared a Mesh), Laser Tag's nav bake (static colliders
only) and Lot's walk navmeshes (`geometry_parsed_geometry_type = 2`, visual meshes too).

    python patches/patch_lot_pole_wires.py --results-pending && cd lot && python -m pytest -q
    python patches/patch_lot_pole_wires.py --fill
    LOT_ROOT=<copy> python patches/patch_lot_pole_wires.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LOT = pathlib.Path(os.environ.get("LOT_ROOT") or HERE.parent / "lot")
SRC = HERE / "lot_pole_wires"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_MEASURED": "result_measured.txt", "RESULT_TESTS": "result_tests.txt",
           "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"Lot 0.118.1", b"Lot 0.119.0"
CHANGELOG_HEAD = ("## 0.118.1 - a line starts clear of the kerb's own cut span, and a signal keeps its "
                  "arms' box: the corner pole stands\n")
POLES = "site_poles.py"
LOTPY = "lot.py"
TEST = "tests/test_site_wires.py"
SHA = {POLES: "de7379ca7bd5dea0", LOTPY: "6185cb5290a8757b"}

PAINT_OLD = ("    mb, ms, mf = _marking_meshes(marks, skins)\n"
             "    body += mb\n"
             "    sub += ms\n"
             "    if files is not None:\n"
             "        files.update(mf)\n")
PAINT_NEW = ("    mb, ms, mf = _marking_meshes(marks, skins)\n"
             "    body += mb\n"
             "    sub += ms\n"
             "    if files is not None:\n"
             "        files.update(mf)\n"
             "    # THE WIRES (0.119.0, `site_poles.wire_meshes`, factory roadmap 240):\n"
             "    # with the art only -- a themed site, whose cover stands as Zoo's\n"
             "    # modules. A candidate's greybox lot, which Laser Tag and the walk test\n"
             "    # grade, draws none: a wire is visual, Lot's walk navmeshes parse visual\n"
             "    # meshes (`geometry_parsed_geometry_type = 2`), and a grade on these lots\n"
             "    # moves with any change to what stands on them (roadmap 242).\n"
             "    if cover_refs:\n"
             "        import site_poles\n"
             "        wb, ws, wf = site_poles.wire_meshes(site_spec.get(\"cover\") or [], SIDEWALK_H)\n"
             "        body += wb\n"
             "        sub += ws\n"
             "        if files is not None:\n"
             "            files.update(wf)\n")


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def _src(name):
    return (SRC / name).read_bytes().decode("utf-8").replace("\r\n", "\n")


def _read(rel):
    p = LOT / rel
    raw = p.read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA[rel], (rel, "is not the file this patch read", got)
    return p, _eol(raw, rel), raw.decode("utf-8").replace("\r\n", "\n")


def fill():
    assert (LOT / "VERSION").read_bytes().strip() == VERSION, (LOT / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value and not value.endswith("."), (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(LOT / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.119.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Lot 0.119.0: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("LOT_ROOT"):
        sys.exit("refusing: --draft is for a LOT_ROOT copy, never the repo")
    assert (LOT / "VERSION").read_bytes().strip() == VERSION_WAS, (LOT / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.119.0.md")
    assert entry.startswith("## 0.119.0 - "), entry[:40]
    if not DRAFT:
        left = entry
        if PENDING:
            for key in RESULTS:
                left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    assert not (LOT / TEST).exists(), "already applied"
    pp, p_eol, poles = _read(POLES)
    assert "def wire_meshes" not in poles, "already applied"
    poles = poles.rstrip("\n") + "\n" + _src("wires.py.txt")
    lp, l_eol, lotpy = _read(LOTPY)
    assert lotpy.count(PAINT_OLD) == 1, lotpy.count(PAINT_OLD)
    lotpy = lotpy.replace(PAINT_OLD, PAINT_NEW)
    new_test = _src("test_site_wires.py.txt")
    cl = LOT / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:160]
    # every anchor matched: now write
    pp.write_bytes(poles.replace("\n", p_eol.decode()).encode("utf-8"))
    lp.write_bytes(lotpy.replace("\n", l_eol.decode()).encode("utf-8"))
    (LOT / TEST).write_bytes(new_test.encode("utf-8"))
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).replace("\n", cl_eol.decode()).encode("utf-8"))
    (LOT / "VERSION").write_bytes(VERSION)
    print("Lot 0.118.1 -> 0.119.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
