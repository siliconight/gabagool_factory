"""Zoo 1.103.0: a mesh leaves with its faces in one order, the same every build (factory roadmap
239, the Blender builds' reproducibility).

Anchored edits, each asserted once, nothing written on a miss: in
`zoo_keeper/bpylayer/geometry.py`, `in_one_order` before `add_hemisphere` (`in_one_order`);
`add_hemisphere` hands its bisect its geometry `in_one_order`, where it handed it
`list(set(geom))` (`hemisphere_old` -> `hemisphere_new`); the fracture's `contextual_create`
takes its cut `in_one_order` (`cut_old` -> `cut_new`); `bm_to_object` sorts the faces before it
writes the mesh (`to_mesh_old` -> `to_mesh_new`). In `zoo_keeper/recipes/dome_fixture.py`, the
rim `holes_fill` closes is taken `in_one_order` (`dome_rim_old` -> `dome_rim_new`).
`tests/test_faces_in_order.py` NEW. The file's own line endings kept. Applies on
Zoo 1.102.0. CHANGELOG and VERSION from `zoo_faces_in_order/CHANGELOG_1.103.0.md`;
`--results-pending` leaves the RESULT_ keys to `--fill`.

Read before it was written: docs/findings/grader_speed/uvsphere_order_probe.py (Blender's own
operators, four processes), zoo_repro_probe.py (the deli's fixtures kit built twice, with and
without the weighted normals and with one thread) and blend_mesh_dump.py (the bulbs' faces read
off the two builds' .blend).

    python patches/patch_zoo_faces_in_order.py --results-pending && cd zoo && python -m pytest -q
    python patches/patch_zoo_faces_in_order.py --fill
    ZOO_ROOT=<copy> python patches/patch_zoo_faces_in_order.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ZOO = pathlib.Path(os.environ.get("ZOO_ROOT") or HERE.parent / "zoo")
SRC = HERE / "zoo_faces_in_order"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_AB": "result_ab.txt", "RESULT_BPY": "result_bpy.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"1.102.0", b"1.103.0"
CHANGELOG_HEAD = "## [1.102.0] - what a roof carries follows what the building is, and fewer\n"
GEOMETRY = "zoo_keeper/bpylayer/geometry.py"
DOME = "zoo_keeper/recipes/dome_fixture.py"
TEST = "tests/test_faces_in_order.py"
SHA = {GEOMETRY: "8984f07adff59edb", DOME: "63d4b840e4d6a189"}
HEMI_DEF = "def add_hemisphere(bm, center, radius_x, radius_y, radius_z, segments=20):\n"


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
    for path, rel in [(ZOO / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_1.103.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Zoo 1.103.0: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("ZOO_ROOT"):
        sys.exit("refusing: --draft is for a ZOO_ROOT copy, never the repo")
    assert (ZOO / "VERSION").read_bytes().strip() == VERSION_WAS, (ZOO / "VERSION").read_bytes()
    entry = _src("CHANGELOG_1.103.0.md")
    assert entry.startswith("## [1.103.0] - "), entry[:40]
    if not DRAFT:
        left = entry
        if PENDING:
            for key in RESULTS:
                left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    assert not (ZOO / TEST).exists(), "already applied"
    gp, g_eol, geo = _read(GEOMETRY)
    assert "bm.faces.sort(" not in geo, "already applied"
    geo = _once(geo, HEMI_DEF, _src("in_one_order.txt") + HEMI_DEF, "add_hemisphere's definition")
    geo = _once(geo, _src("hemisphere_old.txt"), _src("hemisphere_new.txt"), "add_hemisphere's bisect")
    geo = _once(geo, _src("cut_old.txt"), _src("cut_new.txt"), "the cut's contextual_create")
    geo = _once(geo, _src("hemisphere_end_old.txt"), _src("hemisphere_end_new.txt"), "add_hemisphere's end")
    dp, d_eol, dome = _read(DOME)
    dome = _once(dome, _src("dome_rim_old.txt"), _src("dome_rim_new.txt"), "the dome's rim")
    geo = _once(geo, _src("to_mesh_old.txt"), _src("to_mesh_new.txt"), "bm_to_object's mesh")
    new_test = _src("test_faces_in_order.py.txt")
    cl = ZOO / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:160]
    # every anchor matched: now write
    _write(gp, g_eol, geo)
    _write(dp, d_eol, dome)
    (ZOO / TEST).write_bytes(new_test.encode("utf-8"))
    _write(cl, cl_eol, entry.rstrip("\n") + "\n\n" + cl_text)
    (ZOO / "VERSION").write_bytes(VERSION)
    print("Zoo 1.102.0 -> 1.103.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
