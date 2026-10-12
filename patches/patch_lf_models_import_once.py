"""Level Factory 0.189.0: every model is imported once, with its final settings, in three passes
over three sets (factory roadmap 239, the export).

Anchored edits, each asserted once, nothing written until all of them matched:
  packages/exporting/export.py   `_pin_shared_texture_imports` takes the filtered set it is given;
                                 `HELD_SUFFIX`, `WORLDSKIN_BASE_PREFIX`, `MODEL_STATIC`,
                                 `_model_import_defaults` and `_own_light_baking_sidecars` before
                                 `_write_import_sidecars` (`lf_models_import_once/export_helpers`);
                                 its docstring says what replaced the two passes
                                 (`export_docstring.txt`); and the middle of the step, from the
                                 first pass to the second, replaced -- located by its two ends and
                                 its hash, since it is 3,320 characters (`export_region.py.txt`)
  tests/unit/test_import_pass_verified.py   the two tests that count calls: the models' first
                                 pass is the second call now
  tests/unit/test_bake_marks_second_pass.py  replaced: its pass-counting tests moved to the new
                                 file, the wiring test kept
  tests/unit/test_shared_texture_imports.py  the extract-cleanup test: there is no cleanup, and
                                 the step deletes no texture
  tests/unit/test_sign_texture_imports.py    the sign pins beside the shared ones, at their new
                                 lines
  tests/unit/test_models_import_once.py      NEW
CHANGELOG and VERSION from `lf_models_import_once/CHANGELOG_0.189.0.md`; `--results-pending`
leaves the RESULT_ keys to `--fill`.

Measured before it was written: docs/findings/grader_speed/sidecar_once_probe.py (arm G).

    python patches/patch_lf_models_import_once.py --results-pending && cd level_factory && python -m pytest -q
    python patches/patch_lf_models_import_once.py --fill
    LF_ROOT=<copy> python patches/patch_lf_models_import_once.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_models_import_once"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_AB": "result_ab.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.188.0", b"0.189.0"
CHANGELOG_HEAD = ("## [0.188.0] - The export keeps its import cache beside the package, for the walk "
                  "copy\n")
EXPORT = "packages/exporting/export.py"
T_PASS = "tests/unit/test_import_pass_verified.py"
T_MARKS = "tests/unit/test_bake_marks_second_pass.py"
T_TEX = "tests/unit/test_shared_texture_imports.py"
T_SIGN = "tests/unit/test_sign_texture_imports.py"
TEST = "tests/unit/test_models_import_once.py"
SHA = {EXPORT: "9cee15249f338236", T_PASS: "64addd4612de1d0d", T_MARKS: "afc4da27f2008bf6",
       T_TEX: "39b38f233c5848e5", T_SIGN: "1e2e94dd7dbdc443"}
T_SIGN_OLD = ("    shared = src.index(\"    rewrote += _pin_shared_texture_imports(export_dir)\\n\")\n"
              "    signs = src.index(\"    rewrote += _pin_sign_texture_imports(export_dir)\\n\")\n")
T_SIGN_NEW = ("    # 0.189.0 pins between the first and second import passes, the filtered\n"
              "    # set read before the models were held; the two calls stay side by side.\n"
              "    shared = src.index(\"        _pin_shared_texture_imports(export_dir, filtered)\\n\")\n"
              "    signs = src.index(\"        _pin_sign_texture_imports(export_dir)\\n\")\n")
REGION_START = '    _import_pass_verified()\n\n    KEY = "gltf/embedded_image_handling"\n'
REGION_END = ('        _shutil.rmtree(export_dir / ".godot", ignore_errors=True)\n'
              '        _import_pass_verified()\n')
REGION_SHA = "95f0e2913f4fa5f5"

E_PIN_SIG_OLD = "def _pin_shared_texture_imports(export_dir: Path) -> int:\n"
E_PIN_SIG_NEW = "def _pin_shared_texture_imports(export_dir: Path, filtered=None) -> int:\n"
E_PIN_BODY_OLD = "    changed = 0\n    filtered = _filtered_shared_textures(export_dir)\n"
E_PIN_BODY_NEW = ("    changed = 0\n"
                  "    if filtered is None:   # 0.189.0: the sidecar step reads it before it holds the models\n"
                  "        filtered = _filtered_shared_textures(export_dir)\n")
E_DEF = ("def _write_import_sidecars(export_dir: Path, godot_executable, *,\n"
         "                           bake_spawned=None) -> int:\n")
E_DOC_OLD = ("    that never completes raises `ExportImportError`.\n"
             "    \"\"\"\n"
             "    if not godot_executable:\n"
             "        return 0\n")

T_PASS_OLD = (
    "def test_a_pass_that_imports_no_model_is_run_again(tmp_path, monkeypatch):\n"
    "    \"\"\"FAILS ON 0.163.0: one pass, nothing checked, 425 models unimported.\"\"\"\n"
    "    from packages.exporting import export\n"
    "    pkg = _package(tmp_path)\n"
    "    godot = _Godot(short=1)\n"
    "    monkeypatch.setattr(subprocess, \"run\", godot)\n"
    "    export._write_import_sidecars(pkg, \"godot.exe\")\n"
    "    assert godot.calls == 2\n"
    "    assert unimported_models(pkg) == []\n"
    "    log = (pkg.parent / (pkg.name + \".import.log\")).read_text(encoding=\"utf-8\")\n"
    "    assert \"import pass 1\" in log and \"import pass 2\" in log, log\n"
    "\n"
    "\n"
    "def test_an_import_that_never_completes_stops_the_export(tmp_path, monkeypatch):\n"
    "    \"\"\"FAILS ON 0.163.0, which returned and let the occluder bake measure 0.\"\"\"\n"
    "    from packages.exporting import export\n"
    "    pkg = _package(tmp_path)\n"
    "    godot = _Godot(short=99)\n"
    "    monkeypatch.setattr(subprocess, \"run\", godot)\n"
    "    with pytest.raises(export.ExportImportError) as exc:\n"
    "        export._write_import_sidecars(pkg, \"godot.exe\")\n"
    "    assert godot.calls == export.IMPORT_PASSES\n"
    "    assert \"2 of 2 model(s)\" in str(exc.value)\n")
T_PASS_NEW = (
    "def test_a_pass_that_imports_no_model_is_run_again(tmp_path, monkeypatch):\n"
    "    \"\"\"FAILS ON 0.163.0: one pass, nothing checked, 425 models unimported.\n"
    "\n"
    "    0.189.0: the first pass holds every model, so the models' first pass is\n"
    "    the second call -- `short=2` makes it the one that imports nothing -- and\n"
    "    the base (`site_base.glb`) is imported by the pass after it.\n"
    "    \"\"\"\n"
    "    from packages.exporting import export\n"
    "    pkg = _package(tmp_path)\n"
    "    godot = _Godot(short=2)\n"
    "    monkeypatch.setattr(subprocess, \"run\", godot)\n"
    "    export._write_import_sidecars(pkg, \"godot.exe\")\n"
    "    assert godot.calls == 4\n"
    "    assert unimported_models(pkg) == []\n"
    "    log = (pkg.parent / (pkg.name + \".import.log\")).read_text(encoding=\"utf-8\")\n"
    "    assert \"import pass 2\" in log and \"import pass 3\" in log and \"import pass 4\" in log, log\n"
    "\n"
    "\n"
    "def test_an_import_that_never_completes_stops_the_export(tmp_path, monkeypatch):\n"
    "    \"\"\"FAILS ON 0.163.0, which returned and let the occluder bake measure 0.\n"
    "\n"
    "    0.189.0: the models' first pass is the one that never completes (the\n"
    "    first holds every model), and the base held for the pass after it is put\n"
    "    back.\n"
    "    \"\"\"\n"
    "    from packages.exporting import export\n"
    "    pkg = _package(tmp_path)\n"
    "    godot = _Godot(short=99)\n"
    "    monkeypatch.setattr(subprocess, \"run\", godot)\n"
    "    with pytest.raises(export.ExportImportError) as exc:\n"
    "        export._write_import_sidecars(pkg, \"godot.exe\")\n"
    "    assert godot.calls == 1 + export.IMPORT_PASSES\n"
    "    assert \"1 of 1 model(s)\" in str(exc.value)\n"
    "    assert (pkg / \"lot\" / \"b\" / \"site_base.glb\").exists() and not list(pkg.rglob(\"*.held\"))\n")

T_TEX_OLD = (
    "def test_the_extract_cleanup_spares_the_shared_textures():\n"
    "    \"\"\"The cleanup loop must skip `_tex/` by name, not by luck.\n"
    "\n"
    "    Those PNGs already survived because their folder holds no `.glb` to match\n"
    "    the loop's test. A later change that moved the textures next to the GLB,\n"
    "    or widened the glob, would have deleted a module's textures with no test\n"
    "    to notice.\n"
    "    \"\"\"\n"
    "    import inspect\n"
    "    src = inspect.getsource(export._write_import_sidecars)\n"
    "    cleanup = src.split(\"Drop what EXTRACT wrote\", 1)[1].split(\"_import_pass\")[0]\n"
    "    assert \"SHARED_TEX_DIR\" in cleanup\n")
T_TEX_NEW = (
    "def test_the_sidecar_step_deletes_no_texture():\n"
    "    \"\"\"No pass extracts, so nothing is cleaned up (0.189.0).\n"
    "\n"
    "    This held the step's cleanup loop -- what extract wrote beside each GLB,\n"
    "    deleted before the second pass -- to sparing `_tex/` by name, not by\n"
    "    luck. Every model now imports with its images embedded from its first\n"
    "    import, so there is no extract and no loop, and a texture the sidecar\n"
    "    step deleted would be a texture the package lost.\n"
    "    \"\"\"\n"
    "    import inspect\n"
    "    src = inspect.getsource(export._write_import_sidecars)\n"
    "    assert 'rglob(\"*.png\")' not in src and \"png.unlink\" not in src\n")


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
    for path, rel in [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.189.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.189.0: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("LF_ROOT"):
        sys.exit("refusing: --draft is for an LF_ROOT copy, never the repo")
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.189.0.md")
    assert entry.startswith("## [0.189.0] - "), entry[:40]
    if not DRAFT:
        left = entry
        if PENDING:
            for key in RESULTS:
                left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    assert not (LF / TEST).exists(), "already applied"
    ep, e_eol, exp = _read(EXPORT)
    assert "HELD_SUFFIX" not in exp, "already applied"
    exp = _once(exp, E_PIN_SIG_OLD, E_PIN_SIG_NEW, "_pin_shared_texture_imports' signature")
    exp = _once(exp, E_PIN_BODY_OLD, E_PIN_BODY_NEW, "its filtered set")
    exp = _once(exp, E_DEF, _src("export_helpers.py.txt") + E_DEF, "before _write_import_sidecars")
    doc = _src("export_docstring.txt")
    exp = _once(exp, E_DOC_OLD, E_DOC_OLD.replace("ExportImportError`.\n",
                                                  "ExportImportError`.\n" + doc, 1), "the docstring's end")
    assert exp.count(REGION_START) == 1 and exp.count(REGION_END) == 1, "the region's ends"
    i = exp.index(REGION_START)
    j = exp.index(REGION_END, i) + len(REGION_END)
    got = hashlib.sha256(exp[i:j].encode("utf-8")).hexdigest()[:16]
    assert got == REGION_SHA, ("the region is not the one this patch read", got)
    exp = exp[:i] + _src("export_region.py.txt") + exp[j:]
    pp, p_eol, pt = _read(T_PASS)
    pt = _once(pt, T_PASS_OLD, T_PASS_NEW, "the two call-counting tests")
    mp, m_eol, _mt = _read(T_MARKS)
    tp, t_eol, tt = _read(T_TEX)
    tt = _once(tt, T_TEX_OLD, T_TEX_NEW, "the extract-cleanup test")
    sp, s_eol, st = _read(T_SIGN)
    st = _once(st, T_SIGN_OLD, T_SIGN_NEW, "the sign pins' neighbour test")
    new_marks = _src("test_bake_marks_second_pass.py.txt")
    new_test = _src("test_models_import_once.py.txt")
    cl = LF / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:160]
    # every anchor matched: now write
    _write(ep, e_eol, exp)
    _write(pp, p_eol, pt)
    _write(mp, m_eol, new_marks)
    _write(tp, t_eol, tt)
    _write(sp, s_eol, st)
    (LF / TEST).write_bytes(new_test.encode("utf-8"))
    _write(cl, cl_eol, entry.rstrip("\n") + "\n\n" + cl_text)
    (LF / "VERSION").write_bytes(VERSION)
    print("Level Factory 0.188.0 -> 0.189.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
