"""Level Factory 0.177.3: the export carries the paint meshes beside the assembly scene (cold run
9235's stop, one stage past 9234's).

One anchored edit in `packages/exporting/export.py` (step 2.5 copies every `*.obj` beside the
assembly's `site.tscn` to the package root, as it copies the scene and its `skins/`, `cover/`
and `signs/`) and a new `tests/unit/test_paint_meshes_in_package.py`; the file pinned by hash
and the anchor asserted once, nothing written on a miss; the file's own line endings kept.
Applies on 0.177.2. CHANGELOG and VERSION from `lf_obj_in_package/CHANGELOG_0.177.3.md`;
`--suite-pending` leaves RESULT_SUITE to `--fill`.

    python patches/patch_lf_obj_in_package.py --suite-pending && cd level_factory && python -m pytest -q > out.txt 2>&1; echo exit=$?
    python patches/patch_lf_obj_in_package.py --fill
    LF_ROOT=<copy> python patches/patch_lf_obj_in_package.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_obj_in_package"
DRAFT = "--draft" in sys.argv
PENDING = "--suite-pending" in sys.argv
FILL = "--fill" in sys.argv
VERSION_WAS, VERSION = b"0.177.2", b"0.177.3"
CHANGELOG_HEAD = "## [0.177.2] - The Lot adapter publishes the paint meshes\n"
SHA = {"packages/exporting/export.py": "863215629b169131"}
NEW_TEST = "tests/unit/test_paint_meshes_in_package.py"

SIB_OLD = (
    '        for sib in ("skins", "cover", "signs"):\n'
    '            src = Path(themed_site_dir) / sib\n'
    '            if src.is_dir():\n'
    '                shutil.copytree(str(src), str(export_dir / sib),\n'
    '                                dirs_exist_ok=True)\n')
SIB_NEW = SIB_OLD + (
    '        # ... and the road paint Lot 0.114.0 writes as one `site_marks_<colour>.obj`\n'
    '        # a paint colour beside its scene (roadmap 231), named "from ./" by the\n'
    '        # assembly and `res://site_marks_*.obj` by Lux\'s applied scene: sibling\n'
    '        # FILES, which the directory list above cannot carry. Cold run 9235\n'
    '        # shipped the scene without them -- 2 unresolved res://, 2 unresolved\n'
    '        # relative, and the bake\'s scene would not open -- one stage after 9234\n'
    '        # had shipped it without them for the adapter\'s reason (0.177.2). Same\n'
    '        # rule as the directories: a new sibling in Lot means a line here.\n'
    '        for obj in sorted(Path(themed_site_dir).glob("*.obj")):\n'
    '            shutil.copy2(str(obj), str(export_dir / obj.name))\n')


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
    print("Level Factory 0.177.3's changelog filled")


def main():
    if DRAFT and not os.environ.get("LF_ROOT"):
        sys.exit("refusing: --draft is for an LF_ROOT copy, never the repo")
    if FILL:
        _fill()
        return
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.177.3.md")
    assert entry.startswith("## [0.177.3] - "), entry[:40]
    if not DRAFT and not PENDING:
        assert "RESULT_" not in entry, "the changelog still carries an unfilled result"
    assert not (LF / NEW_TEST).exists(), f"{NEW_TEST} already exists"

    ep, e_eol, exp = _read("packages/exporting/export.py")
    assert 'glob("*.obj")' not in exp, "already applied"
    exp = _once(exp, SIB_OLD, SIB_NEW, "step 2.5 siblings")

    cl = LF / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:120]
    test = _src("test_paint_meshes_in_package.py.txt")
    # Every pin and anchor matched: now write.
    ep.write_bytes(exp.replace("\n", e_eol.decode()).encode("utf-8"))
    (LF / NEW_TEST).write_bytes(test.replace("\n", e_eol.decode()).encode("utf-8"))
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).replace("\n", cl_eol.decode()).encode("utf-8"))
    (LF / "VERSION").write_bytes(VERSION)
    print("Level Factory 0.177.2 -> 0.177.3" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
