"""Level Factory 0.193.0: the bake's editor stops drawing for the bake; its work copy is copied in
parallel and removed in the background (factory roadmap 239).

Anchored edits, each asserted once, nothing written until all of them matched:
  assets/godot/light_bake_plugin.gd   the header gains the 0.193.0 paragraph (`plugin_header`);
                                      `_stop_drawing` after `_done` (`plugin_stop_drawing`), called
                                      just before Bake is pressed
  packages/exporting/light_bake.py    os, threading and ThreadPoolExecutor imported;
                                      `COPY_WORKERS`, `_copy_project` and `_remove_later` before
                                      `_import` (`light_bake_copy`); `bake` copies with
                                      `_copy_project` and removes with `_remove_later`
  tests/unit/test_scene_groups_cache.py   its order test reads `_copy_project(export_dir, work)`
  tests/unit/test_bake_draws_nothing.py   NEW
CHANGELOG and VERSION from `lf_bake_draws_nothing/CHANGELOG_0.193.0.md`; `--results-pending`
leaves the RESULT_ keys to `--fill`.

Read before it was written: docs/findings/grader_speed/bake_phases_probe.py's --no-viewport (its
draft, which set a property a SubViewport does not have, and the run that set the right one) and
--no-viewport-at-bake, and their lightmaps by lightmap_compare.py --layout; the copy and removal
timed on 9258's walk copy.

    python patches/patch_lf_bake_draws_nothing.py --results-pending && cd level_factory && python -m pytest -q
    python patches/patch_lf_bake_draws_nothing.py --fill
    LF_ROOT=<copy> python patches/patch_lf_bake_draws_nothing.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_bake_draws_nothing"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_AB": "result_ab.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.192.0", b"0.193.0"
CHANGELOG_HEAD = ("## [0.192.0] - The light bake's editor stops its clock and looks for the scene at "
                  "once; the localizer skips class names a script does not contain\n")
PLUGIN = "assets/godot/light_bake_plugin.gd"
LIGHT_BAKE = "packages/exporting/light_bake.py"
T_GROUPS = "tests/unit/test_scene_groups_cache.py"
TEST = "tests/unit/test_bake_draws_nothing.py"
SHA = {PLUGIN: "5399e22b655013d4", LIGHT_BAKE: "9fd1ff562da117b2", T_GROUPS: "86e5cd89adfb7446"}

HEADER_END = "## floor is one frame now; an open that has not landed is still asked again.\n"
DONE_END = "\tOS.kill(OS.get_process_id())\n\n\n"
PRESS_OLD = "\t\t\t_busy = true\n\t\t\tb.pressed.emit()\n"
PRESS_NEW = "\t\t\t_busy = true\n\t\t\t_stop_drawing()\n\t\t\tb.pressed.emit()\n"
IMPORTS_OLD = ("import json\nimport re\nimport shutil\nimport struct\nimport subprocess\nimport sys\n"
               "import time\nfrom pathlib import Path\n")
IMPORTS_NEW = ("import json\nimport os\nimport re\nimport shutil\nimport struct\nimport subprocess\n"
               "import sys\nimport threading\nimport time\nfrom concurrent.futures import ThreadPoolExecutor\n"
               "from pathlib import Path\n")
IMPORT_DEF = "def _import(export_dir: Path, godot) -> bool:\n"
COPY_OLD = "            shutil.copytree(export_dir, work)\n"
COPY_NEW = "            _copy_project(export_dir, work)   # threads (0.193.0)\n"
REMOVE_OLD = ("    finally:\n"
              "        if work.exists():\n"
              "            shutil.rmtree(work, ignore_errors=True)\n")
REMOVE_NEW = ("    finally:\n"
              "        if work.exists():\n"
              "            _remove_later(work)   # while the export goes on (0.193.0)\n")
GROUPS_OLD = '    copy = code.find("shutil.copytree(export_dir, work)")\n'
GROUPS_NEW = '    copy = code.find("_copy_project(export_dir, work)")   # its copy since 0.193.0\n'


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
    for path, rel in [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.193.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.193.0: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("LF_ROOT"):
        sys.exit("refusing: --draft is for an LF_ROOT copy, never the repo")
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.193.0.md")
    assert entry.startswith("## [0.193.0] - "), entry[:40]
    if not DRAFT:
        left = entry
        if PENDING:
            for key in RESULTS:
                left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    assert not (LF / TEST).exists(), "already applied"
    pp, p_eol, plugin = _read(PLUGIN)
    assert "_stop_drawing" not in plugin, "already applied"
    plugin = _once(plugin, HEADER_END, HEADER_END + _src("plugin_header.txt"), "the header's last paragraph")
    plugin = _once(plugin, DONE_END, DONE_END + _src("plugin_stop_drawing.txt"), "_done's end")
    plugin = _once(plugin, PRESS_OLD, PRESS_NEW, "the press")
    lp, l_eol, lb = _read(LIGHT_BAKE)
    lb = _once(lb, IMPORTS_OLD, IMPORTS_NEW, "the imports")
    lb = _once(lb, IMPORT_DEF, _src("light_bake_copy.py.txt") + IMPORT_DEF, "_import's definition")
    lb = _once(lb, COPY_OLD, COPY_NEW, "the work copy")
    lb = _once(lb, REMOVE_OLD, REMOVE_NEW, "the work copy's removal")
    gp, g_eol, groups = _read(T_GROUPS)
    groups = _once(groups, GROUPS_OLD, GROUPS_NEW, "the groups test's copy")
    new_test = _src("test_bake_draws_nothing.py.txt")
    cl = LF / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:160]
    # every anchor matched: now write
    _write(pp, p_eol, plugin)
    _write(lp, l_eol, lb)
    _write(gp, g_eol, groups)
    (LF / TEST).write_bytes(new_test.encode("utf-8"))
    _write(cl, cl_eol, entry.rstrip("\n") + "\n\n" + cl_text)
    (LF / "VERSION").write_bytes(VERSION)
    print("Level Factory 0.192.0 -> 0.193.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
