"""Level Factory 0.178.3: the walk keeps the bake, and its shot bot tells animation from fighting
(install test 5's two findings, roadmap 202).

Anchored edits in `apps/cli/main.py` (the walk subparser takes `--bake-lights`, defaulting to
`BAKE_LIGHTS_CLI_DEFAULT`), `apps/cli/commands/__init__.py` (`cmd_walk` hands the bake to the
export it calls, and says why), `assets/godot/shot_bot.gd` (two still frames beside the moved one;
`_jitter_diff` judges only pixels the still frames agree on, and reports `animated_pct`) and
`packages/preview/walk_bot.py` (the summary line says what animated); two tests appended to
`tests/unit/test_shotbot_fights.py` and a new `tests/unit/test_walk_keeps_the_bake.py`; each file
pinned by hash and each anchor asserted once, nothing written on a miss; the files' own line
endings kept. Applies on 0.178.2. CHANGELOG and VERSION from
`lf_walk_bake_and_still/CHANGELOG_0.178.3.md`; `--results-pending` leaves RESULT_CONTROL and
RESULT_SUITE to `--fill`.

    python patches/patch_lf_walk_bake_and_still.py --results-pending && cd level_factory && python -m pytest -q > out.txt 2>&1; echo exit=$?
    python patches/patch_lf_walk_bake_and_still.py --fill
    LF_ROOT=<copy> python patches/patch_lf_walk_bake_and_still.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_walk_bake_and_still"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_CONTROL": "result_control.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.178.2", b"0.178.3"
CHANGELOG_HEAD = "## [0.178.2] - Re-grounded to the set factory 1.37.0 certifies\n"
SHA = {"apps/cli/main.py": "60c2719028517663",
       "apps/cli/commands/__init__.py": "d4d195ae70e84b7d",
       "assets/godot/shot_bot.gd": "8ffd0533a8e83796",
       "packages/preview/walk_bot.py": "6cb495e0d918a43c",
       "tests/unit/test_shotbot_fights.py": "a312848ff4dbc19f"}
NEW_TEST = "tests/unit/test_walk_keeps_the_bake.py"

MAIN_OLD = ('    sp.add_argument("--no-shots", action="store_true",\n'
            '                    help="run the traversal check but skip the visual pass "\n'
            '                         "(the visual pass needs a display)")\n'
            '    sp.set_defaults(func=cmd_walk)\n')
MAIN_NEW = ('    sp.add_argument("--no-shots", action="store_true",\n'
            '                    help="run the traversal check but skip the visual pass "\n'
            '                         "(the visual pass needs a display)")\n'
            '    # THE WALK BAKES WHAT IT RE-EXPORTS (0.178.3). It exports into the folder\n'
            '    # `make` shipped, so an unbaked walk replaced a baked package -- install\n'
            '    # test 5 found the stranger\'s level without its bake after `walk`.\n'
            '    sp.add_argument("--bake-lights", action=argparse.BooleanOptionalAction,\n'
            '                    default=BAKE_LIGHTS_CLI_DEFAULT,\n'
            '                    help="the walk re-exports the package it wraps and bakes it as "\n'
            '                         "`export` does, so the package `make` shipped stays baked "\n'
            '                         "and the walk shows what ships; --no-bake-lights for a "\n'
            '                         "quicker look, which leaves the package unbaked")\n'
            '    sp.set_defaults(func=cmd_walk)\n')

CMD_OLD = ("    export_args.include_walk = False\n"
           "    code = cmd_export(export_args)\n")
CMD_NEW = ("    export_args.include_walk = False\n"
           "    # AND IT BAKES (0.178.3). `export_args` was the walk's own arguments, which\n"
           "    # carried no bake, so every walk since 0.144.0 re-exported the package\n"
           "    # UNBAKED into the folder `make` had shipped it to: install test 5 measured\n"
           "    # the stranger's package after `walk` at 2,526 files with no `bake.exr`\n"
           "    # and no `light_bake.json`, where `make` had left 3,008 and a bake. The\n"
           "    # walk's parser now carries `--bake-lights` at the export's own default;\n"
           "    # a caller building its own arguments says what it wants, as for export.\n"
           "    export_args.bake_lights = bool(getattr(args, \"bake_lights\", False))\n"
           "    code = cmd_export(export_args)\n")

SHOOT_OLD = ("\tvar a: Image = await _frame(eye, look)\n"
             "\tvar b: Image = await _frame(eye + Vector3(JITTER, JITTER, JITTER), look)\n"
             "\tif a == null or b == null:\n"
             "\t\tst[\"error\"] = \"no frame captured\"\n"
             "\t\treturn st\n")
SHOOT_NEW = ("\tvar a: Image = await _frame(eye, look)\n"
             "\t# THE STILL CONTROL (0.178.3). Two more frames with the camera where it was,\n"
             "\t# one before the move and one after it. A pixel that changes between them\n"
             "\t# changed with the camera at rest -- a failing tube's flicker, a turning\n"
             "\t# roller, a screen -- and is not the camera's to judge. Install test 5's\n"
             "\t# Ladder_ladder_0_base read 1.39% fighting with the camera moved and 1.27%\n"
             "\t# with it STILL, twice each (a bad tube in the room, Lux 0.74.0), where the\n"
             "\t# same station in 1.36.0's install test read 0.12%; every other station read\n"
             "\t# 0.00% still.\n"
             "\tvar a2: Image = await _frame(eye, look)\n"
             "\tvar b: Image = await _frame(eye + Vector3(JITTER, JITTER, JITTER), look)\n"
             "\tvar a3: Image = await _frame(eye, look)\n"
             "\tif a == null or a2 == null or b == null or a3 == null:\n"
             "\t\tst[\"error\"] = \"no frame captured\"\n"
             "\t\treturn st\n")
JD_OLD = ("\tvar jd: Dictionary = _jitter_diff(a, b)\n"
          "\tst[\"jitter_pct\"] = snappedf(float(jd[\"pct\"]) * 100.0, 0.01)\n"
          "\tst[\"fight_pct\"] = snappedf(float(jd[\"fight_pct\"]) * 100.0, 0.01)\n")
JD_NEW = ("\tvar jd: Dictionary = _jitter_diff(a, b, [a2, a3])\n"
          "\tst[\"jitter_pct\"] = snappedf(float(jd[\"pct\"]) * 100.0, 0.01)\n"
          "\tst[\"fight_pct\"] = snappedf(float(jd[\"fight_pct\"]) * 100.0, 0.01)\n"
          "\tst[\"animated_pct\"] = snappedf(float(jd[\"animated_pct\"]) * 100.0, 0.01)\n")
DIFF_OLD = (
    "func _jitter_diff(a: Image, b: Image) -> Dictionary:\n"
    "\tvar w: int = mini(a.get_width(), b.get_width())\n"
    "\tvar h: int = mini(a.get_height(), b.get_height())\n"
    "\tvar changed := 0\n"
    "\tvar fights := 0\n"
    "\tvar total := 0\n"
    "\tvar worst := [-1, -1]\n"
    "\tvar worst_d := 0\n"
    "\tvar y := 0\n"
    "\twhile y < h:\n"
    "\t\tvar x := 0\n"
    "\t\twhile x < w:\n"
    "\t\t\tvar pa: Color = a.get_pixel(x, y)\n"
    "\t\t\tvar pb: Color = b.get_pixel(x, y)\n"
    "\t\t\tvar d: int = int(maxf(maxf(absf(pa.r - pb.r), absf(pa.g - pb.g)),\n"
    "\t\t\t\t\t\t\t\t  absf(pa.b - pb.b)) * 255.0)\n"
    "\t\t\tif d > DIFF_TOL:\n"
    "\t\t\t\tchanged += 1\n"
    "\t\t\t\tif d > FIGHT_DELTA:\n"
    "\t\t\t\t\tfights += 1\n"
    "\t\t\t\tif d > worst_d:\n"
    "\t\t\t\t\tworst_d = d\n"
    "\t\t\t\t\tworst = [x, y]\n"
    "\t\t\ttotal += 1\n"
    "\t\t\tx += 2\n"
    "\t\ty += 2\n"
    "\treturn {\"pct\": float(changed) / float(maxi(total, 1)), \"worst\": worst,\n"
    "\t\t\t\"fight_pct\": float(fights) / float(maxi(total, 1))}\n")
DIFF_NEW = (
    "## Every sampled pixel's change between frame `a` and the moved frame `b`, judged\n"
    "## only where the STILL frames agree with `a` (0.178.3): a pixel that changed\n"
    "## with the camera at rest is animating, and its share is `animated_pct`,\n"
    "## reported and judged nowhere. `total` is every sampled pixel, so a fight's\n"
    "## share stays a share of the frame, as FIGHT_FAIL_PCT was calibrated.\n"
    "func _jitter_diff(a: Image, b: Image, stills: Array = []) -> Dictionary:\n"
    "\tvar w: int = mini(a.get_width(), b.get_width())\n"
    "\tvar h: int = mini(a.get_height(), b.get_height())\n"
    "\tvar changed := 0\n"
    "\tvar fights := 0\n"
    "\tvar animated := 0\n"
    "\tvar total := 0\n"
    "\tvar worst := [-1, -1]\n"
    "\tvar worst_d := 0\n"
    "\tvar y := 0\n"
    "\twhile y < h:\n"
    "\t\tvar x := 0\n"
    "\t\twhile x < w:\n"
    "\t\t\tvar pa: Color = a.get_pixel(x, y)\n"
    "\t\t\tvar moving := false\n"
    "\t\t\tfor s in stills:\n"
    "\t\t\t\tvar img: Image = s as Image\n"
    "\t\t\t\tif img != null and _delta(pa, img.get_pixel(x, y)) > DIFF_TOL:\n"
    "\t\t\t\t\tmoving = true\n"
    "\t\t\t\t\tbreak\n"
    "\t\t\tif moving:\n"
    "\t\t\t\tanimated += 1\n"
    "\t\t\telse:\n"
    "\t\t\t\tvar d: int = _delta(pa, b.get_pixel(x, y))\n"
    "\t\t\t\tif d > DIFF_TOL:\n"
    "\t\t\t\t\tchanged += 1\n"
    "\t\t\t\t\tif d > FIGHT_DELTA:\n"
    "\t\t\t\t\t\tfights += 1\n"
    "\t\t\t\t\tif d > worst_d:\n"
    "\t\t\t\t\t\tworst_d = d\n"
    "\t\t\t\t\t\tworst = [x, y]\n"
    "\t\t\ttotal += 1\n"
    "\t\t\tx += 2\n"
    "\t\ty += 2\n"
    "\treturn {\"pct\": float(changed) / float(maxi(total, 1)), \"worst\": worst,\n"
    "\t\t\t\"fight_pct\": float(fights) / float(maxi(total, 1)),\n"
    "\t\t\t\"animated_pct\": float(animated) / float(maxi(total, 1))}\n"
    "\n"
    "\n"
    "## The largest per-channel difference between two colours, on 0-255.\n"
    "func _delta(pa: Color, pb: Color) -> int:\n"
    "\treturn int(maxf(maxf(absf(pa.r - pb.r), absf(pa.g - pb.g)), absf(pa.b - pb.b)) * 255.0)\n")

SUM_OLD = ("                fight = st.get(\"fight_pct\")\n"
           "                lines.append(\n"
           "                    f\"  shot bot [{tag}] {name}: jitter {st.get('jitter_pct')}%\"\n"
           "                    + (f\", fighting {fight}%\" if fight is not None else \"\")\n"
           "                    + f\", void {st.get('void_pct')}%\"\n")
SUM_NEW = ("                fight = st.get(\"fight_pct\")\n"
           "                # animated (0.178.3): pixels that changed with the camera at\n"
           "                # rest -- a failing tube, a moving part -- reported, not judged\n"
           "                anim = st.get(\"animated_pct\")\n"
           "                lines.append(\n"
           "                    f\"  shot bot [{tag}] {name}: jitter {st.get('jitter_pct')}%\"\n"
           "                    + (f\", fighting {fight}%\" if fight is not None else \"\")\n"
           "                    + f\", void {st.get('void_pct')}%\"\n"
           "                    + (f\", animated {anim}% (changed with the camera still; not judged)\"\n"
           "                       if anim else \"\")\n")


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


def fill():
    """Put the control's and the suite's results where the entry left them, in LF's CHANGELOG and
    in this patch's own copy of the entry, so the record and the release say the same thing."""
    assert (LF / "VERSION").read_bytes().strip() == VERSION, (LF / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value and not value.endswith("."), (name, value[-40:])
        results[key] = value
    targets = [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.178.3.md", "the entry")]
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
    print("Level Factory 0.178.3: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("LF_ROOT"):
        sys.exit("refusing: --draft is for an LF_ROOT copy, never the repo")
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.178.3.md")
    assert entry.startswith("## [0.178.3] - "), entry[:40]
    if not DRAFT:
        left = entry
        if PENDING:
            for key in RESULTS:
                left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    assert not (LF / NEW_TEST).exists(), f"{NEW_TEST} already exists"

    mp, m_eol, mn = _read("apps/cli/main.py")
    assert "THE WALK BAKES" not in mn, "already applied"
    mn = _once(mn, MAIN_OLD, MAIN_NEW, "walk subparser")
    cp, c_eol, cmds = _read("apps/cli/commands/__init__.py")
    cmds = _once(cmds, CMD_OLD, CMD_NEW, "cmd_walk's export")
    sp, s_eol, shot = _read("assets/godot/shot_bot.gd")
    shot = _once(shot, SHOOT_OLD, SHOOT_NEW, "_shoot's frames")
    shot = _once(shot, JD_OLD, JD_NEW, "_shoot's diff")
    shot = _once(shot, DIFF_OLD, DIFF_NEW, "_jitter_diff")
    wp, w_eol, walk = _read("packages/preview/walk_bot.py")
    walk = _once(walk, SUM_OLD, SUM_NEW, "summary line")
    tp, t_eol, tests = _read("tests/unit/test_shotbot_fights.py")
    assert tests.endswith("\n")
    tests = tests.rstrip("\n") + "\n" + _src("test_shotbot_still.py.txt")

    cl = LF / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:120]
    new_test = _src("test_walk_keeps_the_bake.py.txt")
    # Every pin and anchor matched: now write.
    mp.write_bytes(mn.replace("\n", m_eol.decode()).encode("utf-8"))
    cp.write_bytes(cmds.replace("\n", c_eol.decode()).encode("utf-8"))
    sp.write_bytes(shot.replace("\n", s_eol.decode()).encode("utf-8"))
    wp.write_bytes(walk.replace("\n", w_eol.decode()).encode("utf-8"))
    tp.write_bytes(tests.replace("\n", t_eol.decode()).encode("utf-8"))
    (LF / NEW_TEST).write_bytes(new_test.replace("\n", t_eol.decode()).encode("utf-8"))
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).replace("\n", cl_eol.decode()).encode("utf-8"))
    (LF / "VERSION").write_bytes(VERSION)
    print("Level Factory 0.178.2 -> 0.178.3" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
