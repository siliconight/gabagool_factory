"""Level Factory 0.191.0: the light bake's editor is given the scene groups it would read first
(factory roadmap 239).

Anchored edits, each asserted once, nothing written until all of them matched:
  packages/exporting/light_bake.py   `SCENE_GROUPS_CACHE`, `scene_groups` and
                                     `write_scene_groups_cache` before `bake`
                                     (`light_bake_groups`); `bake` writes the cache after
                                     its import pass and before its work copy, and its
                                     report counts the scenes listed
  tests/unit/test_scene_groups_cache.py   NEW
CHANGELOG and VERSION from `lf_scene_groups_cache/CHANGELOG_0.191.0.md`; `--results-pending`
leaves the RESULT_ keys to `--fill`.

Read before it was written: docs/findings/grader_speed/bake_phases_probe.py and its three
outputs (the editor's timeline without the cache, with --verbose, and with an editor's cache in
the work copy); the editor's own `scene_groups_cache.cfg` from a bake's work copy, which the
test carries verbatim.

    python patches/patch_lf_scene_groups_cache.py --results-pending && cd level_factory && python -m pytest -q
    python patches/patch_lf_scene_groups_cache.py --fill
    LF_ROOT=<copy> python patches/patch_lf_scene_groups_cache.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_scene_groups_cache"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_AB": "result_ab.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.190.0", b"0.191.0"
CHANGELOG_HEAD = ("## [0.190.0] - Compressed everywhere: a package's textures import as an editor "
                  "leaves them\n")
LIGHT_BAKE = "packages/exporting/light_bake.py"
TEST = "tests/unit/test_scene_groups_cache.py"
SHA = {LIGHT_BAKE: "1b459030282e7f2c"}

BAKE_DEF = "def bake(export_dir, godot_executable, *, log=print, spawned=()) -> dict:\n"
CALL_OLD = ('        if not _import(export_dir, godot_executable):\n'
            '            raise RuntimeError("the UV2 import pass did not run")\n'
            '        # 0.178.6: up to BAKE_ATTEMPTS tries, each on a fresh copy, each editor\'s log kept\n')
CALL_NEW = ('        if not _import(export_dir, godot_executable):\n'
            '            raise RuntimeError("the UV2 import pass did not run")\n'
            '        # the groups the editor would load every scene to read before it could\n'
            '        # open one (0.191.0), written where the work copy takes them from\n'
            '        report["scene_groups_cached"] = write_scene_groups_cache(export_dir)\n'
            '        # 0.178.6: up to BAKE_ATTEMPTS tries, each on a fresh copy, each editor\'s log kept\n')


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
    p = LF / rel
    raw = p.read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA[rel], (rel, "is not the file this patch read", got)
    return p, _eol(raw, rel), raw.decode("utf-8").replace("\r\n", "\n")


def _write(p, eol, text):
    p.write_bytes(text.replace("\n", eol.decode()).encode("utf-8"))


def fill():
    assert (LF / "VERSION").read_bytes().strip() == VERSION, (LF / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value and not value.endswith("."), (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.191.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.191.0: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("LF_ROOT"):
        sys.exit("refusing: --draft is for an LF_ROOT copy, never the repo")
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.191.0.md")
    assert entry.startswith("## [0.191.0] - "), entry[:40]
    if not DRAFT:
        left = entry
        if PENDING:
            for key in RESULTS:
                left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    assert not (LF / TEST).exists(), "already applied"
    lp, l_eol, lb = _read(LIGHT_BAKE)
    assert "SCENE_GROUPS_CACHE" not in lb, "already applied"
    lb = _once(lb, "\n\n\n" + BAKE_DEF, "\n\n\n" + _src("light_bake_groups.py.txt") + BAKE_DEF,
               "bake's definition")
    lb = _once(lb, CALL_OLD, CALL_NEW, "the bake's import pass")
    new_test = _src("test_scene_groups_cache.py.txt")
    cl = LF / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:160]
    # every anchor matched: now write
    _write(lp, l_eol, lb)
    (LF / TEST).write_bytes(new_test.encode("utf-8"))
    _write(cl, cl_eol, entry.rstrip("\n") + "\n\n" + cl_text)
    (LF / "VERSION").write_bytes(VERSION)
    print("Level Factory 0.190.0 -> 0.191.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
