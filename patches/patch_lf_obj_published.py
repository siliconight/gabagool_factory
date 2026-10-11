"""Level Factory 0.177.2: the Lot adapter publishes the paint meshes (cold run 9234's stop).

One anchored edit in `adapters/lot/__init__.py` (`collect_outputs` publishes `.obj` beside
`.tscn/.json/.csv/.glb/.gd/.png`) and a new `tests/unit/test_lot_paint_published.py`; the file
pinned by hash and the anchor asserted once, nothing written on a miss; the file's own line
endings kept. Applies on 0.177.1. CHANGELOG and VERSION from `lf_obj_published/CHANGELOG_0.177.2.md`;
`--suite-pending` leaves RESULT_SUITE to `--fill`.

    python patches/patch_lf_obj_published.py --suite-pending && cd level_factory && python -m pytest -q > out.txt 2>&1; echo exit=$?
    python patches/patch_lf_obj_published.py --fill
    LF_ROOT=<copy> python patches/patch_lf_obj_published.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_obj_published"
DRAFT = "--draft" in sys.argv
PENDING = "--suite-pending" in sys.argv
FILL = "--fill" in sys.argv
VERSION_WAS, VERSION = b"0.177.1", b"0.177.2"
CHANGELOG_HEAD = "## [0.177.1] - The paint's OBJ meshes bake: the wavefront sidecar's lightmap UV\n"
SHA = {"adapters/lot/__init__.py": "848a3281de76f527"}
NEW_TEST = "tests/unit/test_lot_paint_published.py"

WANTED_OLD = (
    '        wanted = (".tscn", ".json", ".csv", ".glb", ".gd", ".png")\n'
    '        return sorted(p for p in work.rglob("*") if p.is_file() and p.suffix in wanted)\n')
WANTED_NEW = (
    '        # .obj joined on 2026-10-12 (0.177.2): Lot 0.114.0 writes the road paint\n'
    '        # as one wavefront mesh a colour beside its scene, declared as a Mesh\n'
    '        # ext_resource. Cold run 9234 published the scene without them and the\n'
    '        # export\'s closure gate refused the package -- two relative references\n'
    '        # resolving to nothing -- correctly, and three stages late. A published\n'
    '        # artifact has to be the whole artifact.\n'
    '        wanted = (".tscn", ".json", ".csv", ".glb", ".gd", ".png", ".obj")\n'
    '        return sorted(p for p in work.rglob("*") if p.is_file() and p.suffix in wanted)\n')


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
    p = LF / rel
    raw = p.read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA[rel], (rel, "is not the file this patch read", got)
    return p, _eol(raw, rel), raw.decode("utf-8").replace("\r\n", "\n")


def _fill():
    cl = LF / "CHANGELOG.md"
    raw = cl.read_bytes()
    eol = _eol(raw, "CHANGELOG.md")
    text = raw.decode("utf-8").replace("\r\n", "\n")
    value = (SRC / "result_suite.txt").read_bytes().decode("utf-8").replace("\r\n", "\n").strip()
    assert value and not value.endswith("."), "result_suite.txt must be one sentence without its final stop"
    text = _once(text, "RESULT_SUITE", value, "RESULT_SUITE")
    cl.write_bytes(text.replace("\n", eol.decode()).encode("utf-8"))
    print("Level Factory 0.177.2's changelog filled")


def main():
    if DRAFT and not os.environ.get("LF_ROOT"):
        sys.exit("refusing: --draft is for an LF_ROOT copy, never the repo")
    if FILL:
        _fill()
        return
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.177.2.md")
    assert entry.startswith("## [0.177.2] - "), entry[:40]
    if not DRAFT and not PENDING:
        assert "RESULT_" not in entry, "the changelog still carries an unfilled result"
    assert not (LF / NEW_TEST).exists(), f"{NEW_TEST} already exists"

    ap, a_eol, adapter = _read("adapters/lot/__init__.py")
    assert '".obj"' not in adapter, "already applied"
    adapter = _once(adapter, WANTED_OLD, WANTED_NEW, "collect_outputs wanted")

    cl = LF / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:120]
    test = _src("test_lot_paint_published.py.txt")
    # Every pin and anchor matched: now write.
    ap.write_bytes(adapter.replace("\n", a_eol.decode()).encode("utf-8"))
    (LF / NEW_TEST).write_bytes(test.replace("\n", a_eol.decode()).encode("utf-8"))
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).replace("\n", cl_eol.decode()).encode("utf-8"))
    (LF / "VERSION").write_bytes(VERSION)
    print("Level Factory 0.177.1 -> 0.177.2" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
