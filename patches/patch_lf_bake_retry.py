"""Level Factory 0.178.6: a light bake that fails is tried once more on a fresh copy (cold run 9243).

See `lf_bake_retry/CHANGELOG_0.178.6.md`. Anchored edits, each asserted once, nothing written until
all of them matched:
  packages/exporting/light_bake.py   `BAKE_ATTEMPTS` = 2; the editor's run in a loop over a fresh
                                     work copy each time, every attempt's editor log kept
                                     (`.lightbake.log`, `.lightbake.2.log`), the report's
                                     `attempts`, and the export log saying when it took two
  tests/unit/test_light_bake.py      0.178.5's log test reads both attempts; two tests
CHANGELOG and VERSION from `lf_bake_retry/CHANGELOG_0.178.6.md`.

    python patches/patch_lf_bake_retry.py --results-pending && cd level_factory && python -m pytest -q
    python patches/patch_lf_bake_retry.py --fill
    LF_ROOT=<copy> python patches/patch_lf_bake_retry.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_bake_retry"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.178.5", b"0.178.6"
CHANGELOG_HEAD = "## [0.178.5] - The light bake keeps its editor awake and asks for the scene until it opens\n"

RUNNER = "packages/exporting/light_bake.py"
TESTS = "tests/unit/test_light_bake.py"
SHA = {RUNNER: "ce852e88a84ab797", TESTS: "f94ff0cf72b1a94d"}

C_OLD = "EDITOR_TIMEOUT_S = 900\nIMPORT_TIMEOUT_S = 1800\n"
C_NEW = (C_OLD +
         "#: Tries at the bake, each on a fresh work copy (0.178.6). Cold run 9243's bake opened the\n"
         "#: scene, baked, and read its lightmap image back EMPTY (`src_image_len == 0`, \"Failed\n"
         "#: creating lightmap images\"); the same package baked on the next try. Driving an editor's\n"
         "#: GUI is not deterministic, and one more try costs one more editor minute on a failure.\n"
         "BAKE_ATTEMPTS = 2\n")
LOOP_OLD = (
    "        if work.exists():\n"
    "            shutil.rmtree(work)\n"
    "        shutil.copytree(export_dir, work)\n"
    "        _forward_plus(work / \"project.godot\")\n"
    "        plugin = work / PLUGIN_DIR\n"
    "        plugin.mkdir(parents=True, exist_ok=True)\n"
    "        shutil.copy(PLUGIN_SCRIPT, plugin / \"light_bake_plugin.gd\")\n"
    "        (plugin / \"plugin.cfg\").write_text(\n"
    "            '[plugin]\\n\\nname=\"lf_light_bake\"\\ndescription=\"Bakes bake.tscn and quits.\"\\n'\n"
    "            'author=\"level_factory\"\\nversion=\"1\"\\nscript=\"light_bake_plugin.gd\"\\n',\n"
    "            encoding=\"utf-8\", newline=\"\\n\")\n"
    "        # the editor's output, kept beside the package (0.178.5), never inside it\n"
    "        editor_log = export_dir.parent / (export_dir.name + \".lightbake.log\")\n"
    "        code, took = _run([str(godot_executable), \"--editor\", \"--path\", str(work),\n"
    "                           \"--resolution\", \"1280x720\"], EDITOR_TIMEOUT_S,\n"
    "                          log_path=editor_log)\n"
    "        report[\"editor_s\"] = round(took, 1)\n"
    "        report[\"editor_log\"] = str(editor_log)\n"
    "        result_p = work / RESULT\n"
    "        result = json.loads(result_p.read_text(encoding=\"utf-8\")) if result_p.exists() else None\n"
    "        report[\"result\"] = result\n")
LOOP_NEW = (
    "        # 0.178.6: up to BAKE_ATTEMPTS tries, each on a fresh copy, each editor's log kept\n"
    "        attempts = []\n"
    "        for attempt in range(1, BAKE_ATTEMPTS + 1):\n"
    "            if work.exists():\n"
    "                shutil.rmtree(work)\n"
    "            shutil.copytree(export_dir, work)\n"
    "            _forward_plus(work / \"project.godot\")\n"
    "            plugin = work / PLUGIN_DIR\n"
    "            plugin.mkdir(parents=True, exist_ok=True)\n"
    "            shutil.copy(PLUGIN_SCRIPT, plugin / \"light_bake_plugin.gd\")\n"
    "            (plugin / \"plugin.cfg\").write_text(\n"
    "                '[plugin]\\n\\nname=\"lf_light_bake\"\\ndescription=\"Bakes bake.tscn and quits.\"\\n'\n"
    "                'author=\"level_factory\"\\nversion=\"1\"\\nscript=\"light_bake_plugin.gd\"\\n',\n"
    "                encoding=\"utf-8\", newline=\"\\n\")\n"
    "            # the editor's output, kept beside the package (0.178.5), never inside it\n"
    "            editor_log = export_dir.parent / (export_dir.name + (\n"
    "                \".lightbake.log\" if attempt == 1 else \".lightbake.%d.log\" % attempt))\n"
    "            code, took = _run([str(godot_executable), \"--editor\", \"--path\", str(work),\n"
    "                               \"--resolution\", \"1280x720\"], EDITOR_TIMEOUT_S,\n"
    "                              log_path=editor_log)\n"
    "            result_p = work / RESULT\n"
    "            result = json.loads(result_p.read_text(encoding=\"utf-8\")) if result_p.exists() else None\n"
    "            attempts.append({\"attempt\": attempt, \"editor_s\": round(took, 1),\n"
    "                             \"editor_log\": str(editor_log), \"timed_out\": code is None,\n"
    "                             \"result\": result})\n"
    "            if code is not None and result and result.get(\"ok\"):\n"
    "                break\n"
    "        report[\"attempts\"] = attempts\n"
    "        report[\"editor_s\"] = attempts[-1][\"editor_s\"]\n"
    "        report[\"editor_log\"] = attempts[-1][\"editor_log\"]\n"
    "        report[\"result\"] = result\n")
LOG_OLD = ("               result.get(\"users\"), report[\"editor_s\"]))\n")
LOG_NEW = ("               result.get(\"users\"), report[\"editor_s\"]))\n"
           "        if len(attempts) > 1:\n"
           "            log(\"[export] light bake: baked on attempt %d of %d; the first failed: %s\"\n"
           "                % (len(attempts), BAKE_ATTEMPTS,\n"
           "                   (attempts[0][\"result\"] or {}).get(\"error\") or \"no result written\"))\n")

T_OLD = ("    seen = {}\n"
         "\n"
         "    def fake_editor(cmd, timeout, log_path=None):\n"
         "        seen[\"log\"] = log_path\n"
         "        return None, float(timeout)\n"
         "    monkeypatch.setattr(LB, \"_run\", fake_editor)\n"
         "    r = LB.bake(pkg, \"godot.exe\", log=lambda *a: None)\n"
         "    assert seen[\"log\"] == tmp_path / \"LF_t.portable-godot.lightbake.log\"\n"
         "    assert r[\"editor_log\"] == str(seen[\"log\"])\n"
         "    assert not str(seen[\"log\"]).startswith(str(pkg) + os.sep), \"the log is not shipped\"\n")
T_NEW = ("    seen = []\n"
         "\n"
         "    def fake_editor(cmd, timeout, log_path=None):\n"
         "        seen.append(log_path)\n"
         "        return None, float(timeout)\n"
         "    monkeypatch.setattr(LB, \"_run\", fake_editor)\n"
         "    r = LB.bake(pkg, \"godot.exe\", log=lambda *a: None)\n"
         "    # 0.178.6: a failed bake is tried once more, and each try keeps its own log\n"
         "    assert seen == [tmp_path / \"LF_t.portable-godot.lightbake.log\",\n"
         "                    tmp_path / \"LF_t.portable-godot.lightbake.2.log\"]\n"
         "    assert r[\"editor_log\"] == str(seen[-1])\n"
         "    assert not any(str(s).startswith(str(pkg) + os.sep) for s in seen), \"no log is shipped\"\n")
TESTS_ADD = '''

def _baked_editor(work, users=12):
    (work / LB.RESULT).write_text(json.dumps({"ok": True, "users": users}), encoding="utf-8")
    (work / "bake.tscn").write_text("[gd_scene format=3]\\n", encoding="utf-8")
    for f in ("bake.lmbake", "bake.exr", "bake.exr.import"):
        (work / f).write_text("x", encoding="utf-8")


def test_a_bake_that_fails_once_is_tried_once_more_on_a_fresh_copy(tmp_path, monkeypatch):
    """0.178.6, cold run 9243: the bake read its lightmap image back empty and raised a dialog;
    the same package baked on the next try."""
    pkg = _package(tmp_path)
    monkeypatch.setattr(LB, "_import", lambda d, g: True)
    calls = []

    def flaky_editor(cmd, timeout, log_path=None):
        work = Path(cmd[cmd.index("--path") + 1])
        calls.append(log_path)
        assert not (work / LB.RESULT).exists(), "each try starts from a fresh copy"
        if len(calls) == 1:
            (work / LB.RESULT).write_text(json.dumps({"ok": False, "error": "the bake raised a dialog"}),
                                          encoding="utf-8")
        else:
            _baked_editor(work)
        return 0, 3.0
    monkeypatch.setattr(LB, "_run", flaky_editor)
    said = []
    r = LB.bake(pkg, "godot.exe", log=said.append)
    assert r["ok"] is True, r
    assert [a["attempt"] for a in r["attempts"]] == [1, 2]
    assert r["attempts"][0]["result"]["error"] == "the bake raised a dialog"
    assert any("baked on attempt 2 of 2" in s for s in said), said
    assert all((pkg / f).exists() for f in LB.BAKE_FILES)


def test_a_bake_that_works_first_time_is_not_tried_again(tmp_path, monkeypatch):
    pkg = _package(tmp_path)
    monkeypatch.setattr(LB, "_import", lambda d, g: True)
    calls = []

    def good_editor(cmd, timeout, log_path=None):
        calls.append(log_path)
        _baked_editor(Path(cmd[cmd.index("--path") + 1]))
        return 0, 3.0
    monkeypatch.setattr(LB, "_run", good_editor)
    r = LB.bake(pkg, "godot.exe", log=lambda *a: None)
    assert r["ok"] is True and len(calls) == 1 and len(r["attempts"]) == 1
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
    for path, rel in [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.178.6.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.178.6: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("LF_ROOT"):
        sys.exit("refusing: --draft is for an LF_ROOT copy, never the repo")
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.178.6.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.178.6] - "), entry[:40]
    if not DRAFT:
        left = entry
        if PENDING:
            for key in RESULTS:
                left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"

    rp, r_eol, run = _read(RUNNER)
    assert "BAKE_ATTEMPTS" not in run, "already applied"
    run = _once(run, C_OLD, C_NEW, "the constants")
    run = _once(run, LOOP_OLD, LOOP_NEW, "the editor's run")
    run = _once(run, LOG_OLD, LOG_NEW, "the success line")

    tp, t_eol, tests = _read(TESTS)
    tests = _once(tests, T_OLD, T_NEW, "0.178.5's log test")
    tests = tests.rstrip("\n") + "\n" + TESTS_ADD

    cl = LF / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:90]
    # every anchor matched: now write
    _write(rp, r_eol, run)
    _write(tp, t_eol, tests)
    _write(cl, cl_eol, entry.rstrip("\n") + "\n\n" + cl_text)
    (LF / "VERSION").write_bytes(VERSION)
    print("Level Factory 0.178.5 -> 0.178.6" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
