"""Level Factory 0.187.0: the light bake's lightmap requests ride the export's second import pass
(factory roadmap 239, the export).

Anchored edits, each asserted once, nothing written until all of them matched:
  packages/exporting/export.py      `_write_import_sidecars(..., bake_spawned=None)` applies
                                    `light_bake.mark_imports` after the pins and before the second
                                    pass; `export_mission` passes the bake's own spawned list when
                                    it bakes, nothing when it does not
  packages/exporting/light_bake.py  the bake's own import, kept, says why it now finds nothing
  tests/unit/test_bake_marks_second_pass.py   NEW, from `lf_bake_marks_second_pass/`
CHANGELOG and VERSION from `lf_bake_marks_second_pass/CHANGELOG_0.187.0.md`; `--results-pending`
leaves the RESULT_ keys to `--fill`.

Measured before it was written: docs/findings/grader_speed/uv_second_pass_probe.py (the same
change made in-process, against the same export as it was, on cold run 9252's workspace).

    python patches/patch_lf_bake_marks_second_pass.py --results-pending && cd level_factory && python -m pytest -q
    python patches/patch_lf_bake_marks_second_pass.py --fill
    LF_ROOT=<copy> python patches/patch_lf_bake_marks_second_pass.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_bake_marks_second_pass"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_AB": "result_ab.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.186.0", b"0.187.0"
CHANGELOG_HEAD = ("## [0.186.0] - A job's independent commands run side by side, and job.log "
                  "keeps every command\n")
EXPORT = "packages/exporting/export.py"
BAKE = "packages/exporting/light_bake.py"
TEST = "tests/unit/test_bake_marks_second_pass.py"
SHA = {EXPORT: "dde99794ebd0c3d5", BAKE: "9a306665d0fbf1aa"}

E_SIG_OLD = "def _write_import_sidecars(export_dir: Path, godot_executable) -> int:\n"
E_SIG_NEW = ("def _write_import_sidecars(export_dir: Path, godot_executable, *,\n"
             "                           bake_spawned=None) -> int:\n")
E_MARK_OLD = ("    rewrote += _pin_shared_texture_imports(export_dir)\n"
              "    rewrote += _pin_sign_texture_imports(export_dir)\n"
              "\n"
              "    if rewrote:\n")
E_MARK_NEW = (
    "    rewrote += _pin_shared_texture_imports(export_dir)\n"
    "    rewrote += _pin_sign_texture_imports(export_dir)\n"
    "\n"
    "    # THE LIGHT BAKE'S MARKS RIDE THE SECOND PASS (0.187.0). The bake asks\n"
    "    # every model for a lightmap UV (`light_bake.mark_imports`) and used to\n"
    "    # import the package again for it: every model's third import, 55.0 s of\n"
    "    # a 277.6 s re-export of cold run 9252, the shared textures re-imported\n"
    "    # with them (1,843 times for 476 models in 9248's), and the pass that\n"
    "    # loses their pins (`_repin_after_imports`). Marked here, before a pass\n"
    "    # that imports everything anyway, the bake's import finds nothing left\n"
    "    # to do: 5.0 s, the export 238.4 s, no pin lost where the control lost 74.\n"
    "    #\n"
    "    # NOT BEFORE THE FIRST PASS, which is the refuted plan (the factory's\n"
    "    # `patches/patch_lf_import_once.py`). The worldskin skins a building's\n"
    "    # slabs by `load()`ing one of its floor modules, and on a model's first\n"
    "    # import that module may not be imported yet: cold run 9251's import\n"
    "    # log, pass one left 105 slab meshes greybox and took two reveals from\n"
    "    # roof modules; pass two, its sidecars present, skinned every slab from\n"
    "    # a floor module. This pass is not a first import.\n"
    "    #\n"
    "    # WHAT IT CHANGES (the factory's\n"
    "    # `docs/findings/grader_speed/uv_second_pass_probe.py`): the Empties'\n"
    "    # merge sees models carrying their lightmap UV and makes one mesh a side\n"
    "    # per material, as it was written to -- 236 merged meshes became 148 for\n"
    "    # the same 1,061 meshes in, the bake's users 3,491 -> 3,320 (every one of\n"
    "    # the 171 a merged mesh of an Empty), the lightmap 16 slices -> 15. The\n"
    "    # greybox census, the occluders and the closure verdict identical.\n"
    "    if bake_spawned is not None:\n"
    "        from packages.exporting.light_bake import mark_imports\n"
    "        marks = mark_imports(export_dir, bake_spawned)\n"
    "        rewrote += len(marks[\"baked\"]) + len(marks[\"spawned\"])\n"
    "\n"
    "    if rewrote:\n")
E_CALL_OLD = "    _write_import_sidecars(export_dir, godot_executable)\n"
E_CALL_NEW = ("    # The light bake's marks go on before the second import pass, so the bake\n"
              "    # does not import every model a third time (0.187.0).\n"
              "    _write_import_sidecars(\n"
              "        export_dir, godot_executable,\n"
              "        bake_spawned=(responder_vehicle_scenes(themed_site_dir)\n"
              "                      if profile.bake_lights else None))\n")
L_IMPORT_OLD = ("        if not _import(export_dir, godot_executable):\n"
                "            raise RuntimeError(\"the UV2 import pass did not run\")\n")
L_IMPORT_NEW = ("        # Since 0.187.0 the export writes these marks before its second import\n"
                "        # pass, so this one finds nothing left to import (5.0 s where it took\n"
                "        # 55.0, cold run 9252's package re-exported). It stays: the net for a\n"
                "        # caller that did not, and for any sidecar changed above.\n"
                "        if not _import(export_dir, godot_executable):\n"
                "            raise RuntimeError(\"the UV2 import pass did not run\")\n")


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
    for path, rel in [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.187.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.187.0: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("LF_ROOT"):
        sys.exit("refusing: --draft is for an LF_ROOT copy, never the repo")
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.187.0.md")
    assert entry.startswith("## [0.187.0] - "), entry[:40]
    if not DRAFT:
        left = entry
        if PENDING:
            for key in RESULTS:
                left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    test_text = _src("test_bake_marks_second_pass.py.txt")
    assert not (LF / TEST).exists(), "already applied"
    ep, e_eol, exp = _read(EXPORT)
    assert "bake_spawned" not in exp, "already applied"
    exp = _once(exp, E_SIG_OLD, E_SIG_NEW, "_write_import_sidecars's signature")
    exp = _once(exp, E_MARK_OLD, E_MARK_NEW, "the pins before the second pass")
    exp = _once(exp, E_CALL_OLD, E_CALL_NEW, "export_mission's call")
    bp, b_eol, bake = _read(BAKE)
    bake = _once(bake, L_IMPORT_OLD, L_IMPORT_NEW, "the bake's own import")
    cl = LF / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:160]
    # every anchor matched: now write
    _write(ep, e_eol, exp)
    _write(bp, b_eol, bake)
    (LF / TEST).write_bytes(test_text.encode("utf-8"))
    _write(cl, cl_eol, entry.rstrip("\n") + "\n\n" + cl_text)
    (LF / "VERSION").write_bytes(VERSION)
    print("Level Factory 0.186.0 -> 0.187.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
