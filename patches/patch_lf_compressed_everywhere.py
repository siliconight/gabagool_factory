"""Level Factory 0.190.0: compressed everywhere -- a package's textures import as an editor leaves
them (the walker's call of 2026-10-12; factory roadmap 239).

Anchored edits, each asserted once, nothing written until all of them matched:
  packages/exporting/export.py   `SHARED_TEX_PINS` the editor's decision (`export_shared_pins`);
                                 the filtered split replaced by `NORMAL_TEX_PINS`,
                                 `SURFACE_TEX_PINS` and `_normal_map_shared_textures`, `_glb_json`
                                 kept (`export_pins_block`, a region located by its two ends and
                                 its hash); the pin functions on one write rule, `_apply_pins`,
                                 with `_shared_pins_for` (`export_pin_functions`, likewise);
                                 `SKINS_DIR`; `_sign_pins` replaced by a note and
                                 `_pin_skin_texture_imports` (`export_skin_pins`); every sign map
                                 `SURFACE_TEX_PINS`; the read-back pins the skins and counts them
                                 (`export_print`); the sidecar step reads the normal maps where it
                                 read the samplers and pins the skins beside the signs; the
                                 sidecar step's docstring says the lossless pin was superseded
                                 (`export_docstring`)
  tests/unit/test_shared_texture_imports.py  replaced (its old text hashed first)
  tests/unit/test_sign_texture_imports.py    replaced
  tests/unit/test_models_import_once.py      replaced (made from the file by an anchored rewrite)
  tests/unit/test_compressed_everywhere.py   NEW
CHANGELOG and VERSION from `lf_compressed_everywhere/CHANGELOG_0.190.0.md`; `--results-pending`
leaves the RESULT_ keys to `--fill`.

Read before it was written: docs/findings/grader_speed/editor_texture_probe.py (what the bake's
editor writes on each kind of texture, key by key).

    python patches/patch_lf_compressed_everywhere.py --results-pending && cd level_factory && python -m pytest -q
    python patches/patch_lf_compressed_everywhere.py --fill
    LF_ROOT=<copy> python patches/patch_lf_compressed_everywhere.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_compressed_everywhere"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_AB": "result_ab.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.189.0", b"0.190.0"
CHANGELOG_HEAD = ("## [0.189.0] - Every model is imported once, with its final settings, in three "
                  "passes over three sets\n")
EXPORT = "packages/exporting/export.py"
T_SHARED = "tests/unit/test_shared_texture_imports.py"
T_SIGN = "tests/unit/test_sign_texture_imports.py"
T_ONCE = "tests/unit/test_models_import_once.py"
TEST = "tests/unit/test_compressed_everywhere.py"
SHA = {EXPORT: "546ed88e199c57c7", T_SHARED: "84076780c7689ee4", T_SIGN: "06833e4c0f3e6966",
       T_ONCE: "e92522da7c15098b"}

PINS_OLD = ('SHARED_TEX_PINS = {\n    "compress/mode": "0",\n    "process/fix_alpha_border": "false",\n'
            '    "mipmaps/generate": "true",\n}\n')
BLOCK_START, BLOCK_END, BLOCK_SHA = ("#: And on the ones every sampler FILTERS (0.128.0): VRAM compression. The\n",
                                     "def _pin_shared_texture_imports(", "ca79cc63150e3a0c")
FUNCS_START, FUNCS_END, FUNCS_SHA = ("def _pin_shared_texture_imports(", "def _repin_after_imports(",
                                     "97794109d7c93940")
SIGN_PINS_START, SIGN_PINS_END, SIGN_PINS_SHA = ("def _sign_pins(hints: dict) -> dict:\n",
                                                 "def _pin_sign_texture_imports(", "5d261f007cfb91f3")
REPIN_CALLS_OLD = ("    shared = _pin_shared_texture_imports(export_dir)\n"
                   "    sign = _pin_sign_texture_imports(export_dir)\n")
REPIN_CALLS_NEW = ("    shared = _pin_shared_texture_imports(export_dir)\n"
                   "    sign = _pin_sign_texture_imports(export_dir)\n"
                   "    skin = _pin_skin_texture_imports(export_dir)   # 0.190.0\n")
REPIN_RETURN_OLD = ('    return {"shared_repinned": shared, "sign_repinned": sign,\n'
                    '            "shared_sidecars": total}\n')
REPIN_RETURN_NEW = ('    return {"shared_repinned": shared, "sign_repinned": sign,\n'
                    '            "skin_repinned": skin, "shared_sidecars": total}\n')
REPIN_DOC_OLD = '    ``{"shared_repinned", "sign_repinned", "shared_sidecars"}``."""\n'
REPIN_DOC_NEW = ('    ``{"shared_repinned", "sign_repinned", "skin_repinned",\n'
                 '    "shared_sidecars"}`` -- the skins since 0.190.0."""\n')
SIGNS_DIR_OLD = 'SIGNS_DIR = "signs"\n'
SIGNS_DIR_NEW = ('SIGNS_DIR = "signs"\n'
                 "#: The folder the export copies the site's skins into, beside the site scene\n"
                 "#: (`skins/<map>`): Pixelcoat's maps for the ground, the kerbs and the paint\n"
                 "#: (0.190.0).\n"
                 'SKINS_DIR = "skins"\n')
SIGN_DOC_OLD = "    \"\"\"Pin each sign map's import as its pack's manifest asks (0.166.0).\n"
SIGN_DOC_NEW = ("    \"\"\"Pin each sign map a pack's manifest names (0.166.0) as an editor leaves it,\n"
                "    whatever the pack asks (0.190.0, `SURFACE_TEX_PINS`).\n")
SIGN_CALL_OLD = ('        pins = _sign_pins(doc.get("import_hints") or {})\n'
                 '        if not pins:\n'
                 '            continue\n')
SIGN_CALL_NEW = '        pins = dict(SURFACE_TEX_PINS)   # whatever its import_hints ask (0.190.0)\n'
STEP_READ_OLD = "    filtered = _filtered_shared_textures(export_dir)   # off the models, while they are here\n"
STEP_READ_NEW = "    normals = _normal_map_shared_textures(export_dir)   # off the models, while they are here\n"
STEP_PINS_OLD = ("        _pin_shared_texture_imports(export_dir, filtered)\n"
                 "        _pin_sign_texture_imports(export_dir)\n")
STEP_PINS_NEW = ("        _pin_shared_texture_imports(export_dir, normals)\n"
                 "        _pin_sign_texture_imports(export_dir)\n"
                 "        _pin_skin_texture_imports(export_dir)\n")
STEP_BULLET_OLD = ("    #   * the filtered-texture set is read off the models' glTF, and read\n"
                   "    #     while they were held it was empty: 26 textures went lossless until\n"
                   "    #     the read-back after the last import. It is read before.\n")
STEP_BULLET_NEW = ("    #   * the filtered-texture set is read off the models' glTF, and read\n"
                   "    #     while they were held it was empty: 26 textures went lossless until\n"
                   "    #     the read-back after the last import. It is read before -- and\n"
                   "    #     since 0.190.0 the set read so is the normal maps.\n")
DOC_END = ("    other than desktop -- mode 2 imports S3TC here, and a platform without it\n"
           "    needs its own import flag before this pin means anything there.\n")
PRINT_OLD = ('    print("[export] import pins: %d of %d shared-texture sidecar(s) carry their "\n'
             '          "pins; %d re-pinned after an import reset them, %d sign sidecar(s) "\n'
             '          "re-pinned"\n'
             '          % (pins["shared_sidecars"], pins["shared_sidecars"],\n'
             '             pins["shared_repinned"], pins["sign_repinned"]))\n')


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


def _region(text, start, end, sha, new, what):
    assert text.count(start) == 1 and text.count(end) == 1, (what, "its ends")
    i = text.index(start)
    j = text.index(end, i)
    got = hashlib.sha256(text[i:j].encode("utf-8")).hexdigest()[:16]
    assert got == sha, (what, "is not the region this patch read", got)
    return text[:i] + new + text[j:]


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
    for path, rel in [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.190.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.190.0: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("LF_ROOT"):
        sys.exit("refusing: --draft is for an LF_ROOT copy, never the repo")
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.190.0.md")
    assert entry.startswith("## [0.190.0] - "), entry[:40]
    if not DRAFT:
        left = entry
        if PENDING:
            for key in RESULTS:
                left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    assert not (LF / TEST).exists(), "already applied"
    ep, e_eol, exp = _read(EXPORT)
    assert "SURFACE_TEX_PINS" not in exp, "already applied"
    exp = _once(exp, PINS_OLD, _src("export_shared_pins.py.txt"), "SHARED_TEX_PINS")
    exp = _region(exp, BLOCK_START, BLOCK_END, BLOCK_SHA, _src("export_pins_block.py.txt"),
                  "the filtered block")
    exp = _region(exp, FUNCS_START, FUNCS_END, FUNCS_SHA, _src("export_pin_functions.py.txt"),
                  "the pin functions")
    exp = _once(exp, REPIN_CALLS_OLD, REPIN_CALLS_NEW, "the read-back's pins")
    exp = _once(exp, REPIN_RETURN_OLD, REPIN_RETURN_NEW, "the read-back's report")
    exp = _once(exp, REPIN_DOC_OLD, REPIN_DOC_NEW, "the read-back's docstring")
    exp = _once(exp, SIGNS_DIR_OLD, SIGNS_DIR_NEW, "SIGNS_DIR")
    exp = _region(exp, SIGN_PINS_START, SIGN_PINS_END, SIGN_PINS_SHA, _src("export_skin_pins.py.txt"),
                  "_sign_pins")
    exp = _once(exp, SIGN_DOC_OLD, SIGN_DOC_NEW, "the sign pins' docstring")
    exp = _once(exp, SIGN_CALL_OLD, SIGN_CALL_NEW, "the sign pins' hints")
    exp = _once(exp, STEP_READ_OLD, STEP_READ_NEW, "the sidecar step's read")
    exp = _once(exp, STEP_PINS_OLD, STEP_PINS_NEW, "the sidecar step's pins")
    exp = _once(exp, STEP_BULLET_OLD, STEP_BULLET_NEW, "the sidecar step's comment")
    exp = _once(exp, DOC_END, DOC_END + _src("export_docstring.txt"), "the docstring's pins")
    exp = _once(exp, PRINT_OLD, _src("export_print.py.txt"), "the pins' line")
    for gone in ("FILTERED_TEX_PINS =", "def _filtered_shared_textures", "GLTF_LINEAR =",
                 "_filtered_shared_textures(", "def _sign_pins"):
        assert gone not in exp, ("still there", gone)
    sp, s_eol, _old_shared = _read(T_SHARED)
    gp, g_eol, _old_sign = _read(T_SIGN)
    op, o_eol, _old_once = _read(T_ONCE)
    new_shared = _src("test_shared_texture_imports.py.txt")
    new_sign = _src("test_sign_texture_imports.py.txt")
    new_once = _src("test_models_import_once.py.txt")
    new_test = _src("test_compressed_everywhere.py.txt")
    cl = LF / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:160]
    # every anchor matched: now write
    _write(ep, e_eol, exp)
    _write(sp, s_eol, new_shared)
    _write(gp, g_eol, new_sign)
    _write(op, o_eol, new_once)
    (LF / TEST).write_bytes(new_test.encode("utf-8"))
    _write(cl, cl_eol, entry.rstrip("\n") + "\n\n" + cl_text)
    (LF / "VERSION").write_bytes(VERSION)
    print("Level Factory 0.189.0 -> 0.190.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
