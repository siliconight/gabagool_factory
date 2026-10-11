"""Level Factory 0.178.5: the light bake keeps its editor awake, asks for the scene until it opens, and
keeps the editor's output (cold run 9242). See `lf_bake_open/CHANGELOG_0.178.5.md`.

Anchored edits, each asserted once, nothing written until all of them matched:
  assets/godot/light_bake_plugin.gd   the editor's low-processor mode held off; the scene asked for
                                      once the file scan is idle, asked again every 300 frames until
                                      it opens, the wait judged on a clock (OPEN_LIMIT_MS) instead of
                                      3,000 frames; what it did printed
  packages/exporting/light_bake.py    `_run` writes the process's output to a log when given one;
                                      the bake keeps the editor's beside the package and names it
                                      in the report
  tests/unit/test_light_bake.py       the three editor fakes take the log; two tests
CHANGELOG and VERSION from `lf_bake_open/CHANGELOG_0.178.5.md`.

    python patches/patch_lf_bake_open.py --results-pending && cd level_factory && python -m pytest -q
    python patches/patch_lf_bake_open.py --fill
    LF_ROOT=<copy> python patches/patch_lf_bake_open.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_bake_open"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_SUITE": "result_suite.txt", "RESULT_BAKE": "result_bake.txt"}
VERSION_WAS, VERSION = b"0.178.4", b"0.178.5"
CHANGELOG_HEAD = "## [0.178.4] - Re-grounded to the set factory 1.38.0 certifies\n"

PLUGIN = "assets/godot/light_bake_plugin.gd"
RUNNER = "packages/exporting/light_bake.py"
TESTS = "tests/unit/test_light_bake.py"
SHA = {PLUGIN: "5619560b50d519bc", RUNNER: "ba3dbddd07cddb69", TESTS: "f41ca1f0336c72e9"}

# --- the plugin -------------------------------------------------------------------------------
P_DOC_OLD = ("## save, write `res://bake_result.json`, and quit. Every wait is counted in\n"
             "## frames and bounded; a failure writes what it saw and quits all the same.\n")
P_DOC_NEW = (P_DOC_OLD +
             "##\n"
             "## THE EDITOR STAYS AWAKE, AND THE SCENE IS ASKED FOR UNTIL IT OPENS (0.178.5).\n"
             "## Cold run 9242's bake wrote `bake.tscn did not open` after 83.7 s, and a\n"
             "## re-run of it 371.8 s: an editor whose window has no focus sleeps 100 ms a\n"
             "## frame (Godot's unfocused low-processor mode), so 3,180 counted frames came to\n"
             "## minutes while the editor's first open -- which re-imports every texture it\n"
             "## finds used in 3D -- crawled at the same pace. The same plugin with the mode\n"
             "## held off, the open asked once the file scan is idle and again until it\n"
             "## lands, and the wait judged on a clock, opened 9242's scene in 21 s and baked\n"
             "## it. The bake's own wait (BAKE_LIMIT_MS) was always a clock.\n")
P_VARS_OLD = "var _t0: int = 0\n"
P_VARS_NEW = ("var _t0: int = 0\n"
              "## When the scene was first asked for, and how long it may take to open (0.178.5).\n"
              "var _open_t0: int = 0\n"
              "const OPEN_LIMIT_MS := 300000\n")
P_ENTER_OLD = "func _enter_tree() -> void:\n\tset_process(true)\n"
P_ENTER_NEW = ("func _enter_tree() -> void:\n"
               "\t# An unfocused editor sleeps between frames; a bake on someone's desktop\n"
               "\t# rarely has the focus. Held off here and every frame (0.178.5).\n"
               "\tOS.low_processor_usage_mode = false\n"
               "\tset_process(true)\n")
P_PROC_OLD = "func _process(_delta: float) -> void:\n\tif _busy:\n\t\treturn\n\t_frames += 1\n"
P_PROC_NEW = ("func _process(_delta: float) -> void:\n"
              "\tOS.low_processor_usage_mode = false\n"
              "\tif _busy:\n\t\treturn\n\t_frames += 1\n")
P_OPEN_OLD = ("\t\t\tif _frames < 180:\n"
              "\t\t\t\treturn\n"
              "\t\t\tEditorInterface.open_scene_from_path(SCENE)\n"
              "\t\t\t_phase = 1\n")
P_OPEN_NEW = ("\t\t\tif _frames < 180 or EditorInterface.get_resource_filesystem().is_scanning():\n"
              "\t\t\t\treturn\n"
              "\t\t\tEditorInterface.open_scene_from_path(SCENE)\n"
              "\t\t\t_open_t0 = Time.get_ticks_msec()\n"
              "\t\t\tprint(\"BAKE asked to open the scene at frame \", _frames)\n"
              "\t\t\t_phase = 1\n")
P_WAIT_OLD = ("\t\t\t\tif _frames > 3000:\n"
              "\t\t\t\t\t_done({\"ok\": false, \"error\": \"bake.tscn did not open\"})\n"
              "\t\t\t\treturn\n")
P_WAIT_NEW = ("\t\t\t\t# asked again until it lands: an open asked during the editor's\n"
              "\t\t\t\t# first scan or re-import can be dropped\n"
              "\t\t\t\tif _frames % 300 == 0 and not EditorInterface.get_resource_filesystem().is_scanning():\n"
              "\t\t\t\t\tprint(\"BAKE asked again at frame \", _frames)\n"
              "\t\t\t\t\tEditorInterface.open_scene_from_path(SCENE)\n"
              "\t\t\t\tvar waited: int = Time.get_ticks_msec() - _open_t0\n"
              "\t\t\t\tif waited > OPEN_LIMIT_MS:\n"
              "\t\t\t\t\t_done({\"ok\": false, \"error\": \"bake.tscn did not open\",\n"
              "\t\t\t\t\t\t\"waited_ms\": waited, \"frames\": _frames})\n"
              "\t\t\t\treturn\n"
              "\t\t\tprint(\"BAKE the scene opened after \", Time.get_ticks_msec() - _open_t0, \" ms, frame \", _frames)\n")

# --- the runner -------------------------------------------------------------------------------
R_RUN_OLD = ("def _run(cmd, timeout):\n"
             "    \"\"\"Run, bounded; on the bound kill the process TREE (the console\n"
             "    launcher's engine is a grandchild). ``(returncode or None, seconds)``.\"\"\"\n"
             "    t0 = time.time()\n"
             "    p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)\n"
             "    try:\n"
             "        p.wait(timeout=timeout)\n"
             "        return p.returncode, time.time() - t0\n"
             "    except subprocess.TimeoutExpired:\n")
R_RUN_NEW = ("def _run(cmd, timeout, log_path=None):\n"
             "    \"\"\"Run, bounded; on the bound kill the process TREE (the console\n"
             "    launcher's engine is a grandchild). ``(returncode or None, seconds)``.\n"
             "\n"
             "    ``log_path`` keeps the process's output (0.178.5). Cold run 9242's bake\n"
             "    failed with this sending it to DEVNULL, and only a re-run that kept it\n"
             "    could say why.\"\"\"\n"
             "    t0 = time.time()\n"
             "    out = open(log_path, \"wb\") if log_path else subprocess.DEVNULL\n"
             "    try:\n"
             "        p = subprocess.Popen(cmd, stdout=out, stderr=subprocess.STDOUT if log_path\n"
             "                             else subprocess.DEVNULL)\n"
             "    except Exception:\n"
             "        if log_path:\n"
             "            out.close()\n"
             "        raise\n"
             "    try:\n"
             "        p.wait(timeout=timeout)\n"
             "        return p.returncode, time.time() - t0\n"
             "    except subprocess.TimeoutExpired:\n")
R_RUN_TAIL_OLD = ("            p.kill()\n"
                  "        return None, time.time() - t0\n")
R_RUN_TAIL_NEW = ("            p.kill()\n"
                  "        return None, time.time() - t0\n"
                  "    finally:\n"
                  "        if log_path:\n"
                  "            out.close()\n")
R_CALL_OLD = ("        code, took = _run([str(godot_executable), \"--editor\", \"--path\", str(work),\n"
              "                           \"--resolution\", \"1280x720\"], EDITOR_TIMEOUT_S)\n"
              "        report[\"editor_s\"] = round(took, 1)\n")
R_CALL_NEW = ("        # the editor's output, kept beside the package (0.178.5), never inside it\n"
              "        editor_log = export_dir.parent / (export_dir.name + \".lightbake.log\")\n"
              "        code, took = _run([str(godot_executable), \"--editor\", \"--path\", str(work),\n"
              "                           \"--resolution\", \"1280x720\"], EDITOR_TIMEOUT_S,\n"
              "                          log_path=editor_log)\n"
              "        report[\"editor_s\"] = round(took, 1)\n"
              "        report[\"editor_log\"] = str(editor_log)\n")

# --- the tests --------------------------------------------------------------------------------
T_FAIL_OLD = "    monkeypatch.setattr(LB, \"_run\", lambda cmd, timeout: (None, float(timeout)))\n"
T_FAIL_NEW = "    monkeypatch.setattr(LB, \"_run\", lambda cmd, timeout, log_path=None: (None, float(timeout)))\n"
T_FAKE_OLD = "    def fake_editor(cmd, timeout):\n"
T_FAKE_NEW = "    def fake_editor(cmd, timeout, log_path=None):\n"
TESTS_ADD = '''

def test_the_editor_stays_awake_and_the_scene_is_asked_for_until_it_opens():
    """0.178.5, cold run 9242: `bake.tscn did not open` after 83.7 s, and 371.8 s on a re-run.
    An unfocused editor sleeps between frames, and the open was asked once and waited on in
    frames. The same plugin with these three changes opened 9242's scene in 21 s and baked it."""
    src = LB.PLUGIN_SCRIPT.read_text(encoding="utf-8")
    assert src.count("OS.low_processor_usage_mode = false") == 2, "held off at start and every frame"
    assert "_frames > 3000" not in src, "the open's wait is a clock, not a frame count"
    assert "if waited > OPEN_LIMIT_MS:" in src
    assert src.count("EditorInterface.open_scene_from_path(SCENE)") == 2, "asked, then asked again"
    assert src.count("get_resource_filesystem().is_scanning()") == 2


def test_the_editor_s_output_is_kept_beside_the_package(tmp_path, monkeypatch):
    """0.178.5: 9242's bake sent the editor's output to DEVNULL, so the failure said nothing."""
    log = tmp_path / "out.log"
    code, _took = LB._run([sys.executable, "-c", "print('BAKE hello from the editor')"], 60, log_path=log)
    assert code == 0
    assert "BAKE hello from the editor" in log.read_text(encoding="utf-8", errors="replace")
    pkg = _package(tmp_path)
    monkeypatch.setattr(LB, "_import", lambda d, g: True)
    seen = {}

    def fake_editor(cmd, timeout, log_path=None):
        seen["log"] = log_path
        return None, float(timeout)
    monkeypatch.setattr(LB, "_run", fake_editor)
    r = LB.bake(pkg, "godot.exe", log=lambda *a: None)
    assert seen["log"] == tmp_path / "LF_t.portable-godot.lightbake.log"
    assert r["editor_log"] == str(seen["log"])
    assert not str(seen["log"]).startswith(str(pkg) + os.sep), "the log is not shipped"
'''


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


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
    for path, rel in [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.178.5.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.178.5: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("LF_ROOT"):
        sys.exit("refusing: --draft is for an LF_ROOT copy, never the repo")
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.178.5.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.178.5] - "), entry[:40]
    if not DRAFT:
        left = entry
        if PENDING:
            for key in RESULTS:
                left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"

    pp, p_eol, plug = _read(PLUGIN)
    assert "OPEN_LIMIT_MS" not in plug, "already applied"
    plug = _once(plug, P_DOC_OLD, P_DOC_NEW, "the plugin's header")
    plug = _once(plug, P_VARS_OLD, P_VARS_NEW, "the plugin's clock")
    plug = _once(plug, P_ENTER_OLD, P_ENTER_NEW, "_enter_tree")
    plug = _once(plug, P_PROC_OLD, P_PROC_NEW, "_process")
    plug = _once(plug, P_OPEN_OLD, P_OPEN_NEW, "the open")
    plug = _once(plug, P_WAIT_OLD, P_WAIT_NEW, "the open's wait")

    rp, r_eol, run = _read(RUNNER)
    run = _once(run, R_RUN_OLD, R_RUN_NEW, "_run")
    run = _once(run, R_RUN_TAIL_OLD, R_RUN_TAIL_NEW, "_run's tail")
    run = _once(run, R_CALL_OLD, R_CALL_NEW, "the editor's call")

    tp, t_eol, tests = _read(TESTS)
    tests = _once(tests, T_FAIL_OLD, T_FAIL_NEW, "the failing fake")
    assert tests.count(T_FAKE_OLD) == 2, ("the two editor fakes", tests.count(T_FAKE_OLD))
    tests = tests.replace(T_FAKE_OLD, T_FAKE_NEW)
    tests = _once(tests, "import json\nfrom pathlib import Path\n",
                  "import json\nimport os\nimport sys\nfrom pathlib import Path\n", "the tests' imports")
    tests = tests.rstrip("\n") + "\n" + TESTS_ADD

    cl = LF / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:90]
    # every anchor matched: now write
    _write(pp, p_eol, plug)
    _write(rp, r_eol, run)
    _write(tp, t_eol, tests)
    _write(cl, cl_eol, entry.rstrip("\n") + "\n\n" + cl_text)
    (LF / "VERSION").write_bytes(VERSION)
    print("Level Factory 0.178.4 -> 0.178.5" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
