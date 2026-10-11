"""Lot 0.117.0: the walk test's navigation map updates on its own thread, so its clock need not wait
(factory roadmap 239).

Anchored edits in `godot/addons/lot/lot_navqa_setup.gd` (`_bake_nav` sets the world's map and the
site's region to iterate synchronously before it bakes) and `walktest.py` (`FIXED_FPS` 60, and
`run_one` launches the scene with `--fixed-fps 60`), and a new `tests/test_walktest_clock.py` from
`lot_walk_clock/test_walktest_clock.py.txt`; each file pinned by hash and each anchor asserted
once, nothing written on a miss; the files' own line endings kept. Applies on Lot 0.116.0.
CHANGELOG and VERSION from `lot_walk_clock/CHANGELOG_0.117.0.md`; `--results-pending` leaves the
RESULT_ keys to `--fill`.

    python patches/patch_lot_walk_clock.py --results-pending && cd lot && python -m pytest -q
    python patches/patch_lot_walk_clock.py --fill
    LOT_ROOT=<copy, or a staged walk test's project> python patches/patch_lot_walk_clock.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LOT = pathlib.Path(os.environ.get("LOT_ROOT") or HERE.parent / "lot")
SRC = HERE / "lot_walk_clock"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_AB": "result_ab.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"Lot 0.116.0", b"Lot 0.117.0"
CHANGELOG_HEAD = "## 0.116.0 - a lane lights its own length\n"
SETUP = "godot/addons/lot/lot_navqa_setup.gd"
WALK = "walktest.py"
NEW_TEST = "tests/test_walktest_clock.py"
SHA = {SETUP: "394b2fdc00812206", WALK: "0c7fe163cb62210c"}

S_OLD = ("\t\tNavigationServer3D.map_set_cell_height(map, nav.navigation_mesh.cell_height)\n"
         "\t\tnav.bake_navigation_mesh(false)\n")
S_NEW = ("\t\tNavigationServer3D.map_set_cell_height(map, nav.navigation_mesh.cell_height)\n"
         "\t\t# THE MAP AND THE REGION UPDATE ON THIS THREAD (0.117.0, factory roadmap\n"
         "\t\t# 239). Godot 4.7 iterates both on worker threads by default, so when\n"
         "\t\t# the bake's update lands is wall time: under walktest.py's `--fixed-fps`\n"
         "\t\t# clock the director's ten-second wait passed in milliseconds and read\n"
         "\t\t# the map EMPTY on every candidate of cold run 9247. Synchronous, the same\n"
         "\t\t# three walk tests read their jobs' reports field for field (the map's\n"
         "\t\t# iteration count aside, 2 -> 1) in 4 s against 2 to 2.5 minutes. Set\n"
         "\t\t# before the bake: the setters are server commands, applied in order at\n"
         "\t\t# the next sync, which the force_update below is.\n"
         "\t\tNavigationServer3D.map_set_use_async_iterations(map, false)\n"
         "\t\tNavigationServer3D.region_set_use_async_iterations(nav.get_rid(), false)\n"
         "\t\tnav.bake_navigation_mesh(false)\n")
W_CONST_OLD = "HERE = os.path.dirname(os.path.abspath(__file__))\n"
W_CONST_NEW = ("HERE = os.path.dirname(os.path.abspath(__file__))\n"
               "#: THE CLOCK (0.117.0, factory roadmap 239). The director simulates at Godot's\n"
               "#: default clock, which waits on real seconds: cold run 9247's walk tests took\n"
               "#: 2.1 to 2.6 minutes, their walkers' 475-480 m at 4 m/s about 120 s of it.\n"
               "#: `--fixed-fps` makes each frame one physics step (the project's 60 ticks)\n"
               "#: computed as fast as the processor allows; with `lot_navqa_setup.gd`'s map\n"
               "#: and region updating synchronously the report is the job's, field for field\n"
               "#: (the map's iteration count aside), in about 4 s. 0 restores the waiting\n"
               "#: clock.\n"
               "FIXED_FPS = 60\n")
W_CMD_OLD = '    cmd = [godot, "--headless", "--path", project_dir, f"res://{rel}"]\n'
W_CMD_NEW = ('    clock = ["--fixed-fps", str(int(FIXED_FPS))] if FIXED_FPS else []\n'
             '    cmd = [godot, "--headless", *clock, "--path", project_dir, f"res://{rel}"]\n')


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
    p = LOT / rel
    raw = p.read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA[rel], (rel, "is not the file this patch read", got)
    return p, _eol(raw, rel), raw.decode("utf-8").replace("\r\n", "\n")


def _write(p, eol, text):
    p.write_bytes(text.replace("\n", eol.decode()).encode("utf-8"))


def fill():
    assert (LOT / "VERSION").read_bytes().strip() == VERSION, (LOT / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value and not value.endswith("."), (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(LOT / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.117.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Lot 0.117.0: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("LOT_ROOT"):
        sys.exit("refusing: --draft is for a LOT_ROOT copy, never the repo")
    # A staged walk test's project carries the addon and no walktest.py: a draft there is the
    # setup's change alone, which is what an A/B on a staged level needs. The scene loads
    # `res://addons/lot/lot_navqa_setup.gd`; the copy at the project's root is not the one that
    # runs (REFUTED, KEPT: the first A/B patched that copy and measured the unpatched setup).
    staged = DRAFT and (LOT / "addons/lot/lot_navqa_setup.gd").exists() and not (LOT / WALK).exists()
    setup_rel = "addons/lot/lot_navqa_setup.gd" if staged else SETUP
    p = LOT / setup_rel
    raw = p.read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA[SETUP], (setup_rel, "is not the file this patch read", got)
    s_eol = _eol(raw, setup_rel)
    setup = raw.decode("utf-8").replace("\r\n", "\n")
    assert "map_set_use_async_iterations" not in setup, "already applied"
    setup = _once(setup, S_OLD, S_NEW, "_bake_nav's bake")
    if staged:
        _write(p, s_eol, setup)
        print("Lot 0.116.0 -> 0.117.0 (DRAFT, the setup script only, staged project)")
        return
    wp, w_eol, walk = _read(WALK)
    walk = _once(walk, W_CONST_OLD, W_CONST_NEW, "walktest.py's HERE")
    walk = _once(walk, W_CMD_OLD, W_CMD_NEW, "run_one's command")
    test_text = _src("test_walktest_clock.py.txt")
    assert not (LOT / NEW_TEST).exists(), "already applied"
    assert (LOT / "VERSION").read_bytes().strip() == VERSION_WAS, (LOT / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.117.0.md")
    assert entry.startswith("## 0.117.0 - "), entry[:40]
    if not DRAFT:
        left = entry
        if PENDING:
            for key in RESULTS:
                left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    cl = LOT / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:120]
    # every anchor matched: now write
    _write(p, s_eol, setup)
    _write(wp, w_eol, walk)
    (LOT / NEW_TEST).write_bytes(test_text.encode("utf-8"))
    _write(cl, cl_eol, entry.rstrip("\n") + "\n\n" + cl_text)
    (LOT / "VERSION").write_bytes(VERSION)
    print("Lot 0.116.0 -> 0.117.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
