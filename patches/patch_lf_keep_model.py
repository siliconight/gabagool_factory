"""Level Factory 0.234.1: a model its sidecar keeps is not waited for. Cold run 9380 stopped at the export on Deli
Counter 0.259.0's `drawings/scout.glb`, kept on purpose (`importer="keep"`): the import check counted it as a model
Godot must import. `occluders.kept` names such a model; `package_models` and the export's import passes skip it.

What this writes, every target pinned by its hash and refused on a mismatch, nothing written until every file has been
worked out: `packages/exporting/occluders.py`, `packages/exporting/export.py` and
`tests/unit/test_import_pass_verified.py` (anchored hunks); VERSION; the CHANGELOG entry, prepended. Generated from a
proven clone (`patches/lf_keep_model/gen_lf_keep_model.py`), dry-run on a fresh clone to the clone's every byte, a
second run refused (`patches/lf_keep_model/dry_run_*.out.txt`).

    python patches/patch_lf_keep_model.py
    cd level_factory && python -m pytest -q
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
LF = ROOT / "level_factory"
PINS = {'packages/exporting/occluders.py': '6353bf95a24ae77e', 'packages/exporting/export.py': '1c5e7d5a2e894e55', 'tests/unit/test_import_pass_verified.py': 'bd3ac8ddec72bc65'}
EDITS = {'packages/exporting/occluders.py': [('lines 129-132', 'MODEL_SUFFIXES = (".glb", ".gltf")\n\n\ndef package_models(export_dir: Path) -> list:\n', 'MODEL_SUFFIXES = (".glb", ".gltf")\n\n#: A sidecar that keeps its file as the file it is: Godot imports nothing of\n#: it, by design (0.234.1). Deli Counter 0.259.0 ships each building\'s scout\n#: model so (`drawings/scout.glb`), for a game to read with `GLTFDocument`\n#: when its screen opens rather than every level importing it; cold run 9380\n#: stopped at the export, "the import pass left 3 of 537 model(s) unimported\n#: ... first: lot/deli_a03/drawings/scout.glb", waiting for an import that was\n#: never going to come. Matched on the importer line, as Godot reads it.\n_KEEP = re.compile(r\'^importer="keep"\\s*$\', re.M)\n\n\ndef kept(model: Path) -> bool:\n    """Whether ``model``\'s sidecar keeps it, unimported, as the file it is."""\n    try:\n        text = Path(str(model) + ".import").read_text(encoding="utf-8")\n    except OSError:\n        return False\n    return bool(_KEEP.search(text))\n\n\ndef package_models(export_dir: Path) -> list:\n'), ('lines 135-135', '    never imports, and is skipped the way Godot skips it."""\n', '    never imports, and is skipped the way Godot skips it -- and so is a model\n    its sidecar keeps (`kept`, 0.234.1)."""\n'), ('lines 143-144', '        if rel.parts[0] == CACHE_DIR or any(d in p.parents for d in ignored):\n            continue\n', '        if rel.parts[0] == CACHE_DIR or any(d in p.parents for d in ignored):\n            continue\n        if kept(p):\n            continue\n')], 'packages/exporting/export.py': [('lines 1152-1152', '    models = [p for p in sorted(export_dir.rglob("*.glb")) if ".godot" not in p.parts]\n', '    # a model its sidecar keeps is never imported, so it is never held (0.234.1, `occluders.kept`)\n    from packages.exporting.occluders import kept\n    models = [p for p in sorted(export_dir.rglob("*.glb")) if ".godot" not in p.parts and not kept(p)]\n')], 'tests/unit/test_import_pass_verified.py': [('lines 89-92', '    _import_one(pkg, "lot/b/site_base.glb", dest_files=False)\n    assert unimported_models(pkg) == ["lot/b/site_base.glb"]\n\n\n', '    _import_one(pkg, "lot/b/site_base.glb", dest_files=False)\n    assert unimported_models(pkg) == ["lot/b/site_base.glb"]\n\n\ndef test_a_model_its_sidecar_keeps_is_not_waited_for(tmp_path):\n    """0.234.1: cold run 9380 stopped at the export on Deli Counter 0.259.0\'s\n    `drawings/scout.glb`, which its sidecar keeps -- `[remap]` and\n    `importer="keep"`, the file a game reads with `GLTFDocument` -- and which\n    Godot therefore never imports. It is no model of the import\'s; a sidecar\n    that only mentions keep somewhere else is not a keep."""\n    from packages.exporting.occluders import kept, package_models\n    pkg = _package(tmp_path, rels=("lot/a/art/wall.glb", "lot/a/drawings/scout.glb",\n                                   "lot/b/art/odd.glb"))\n    (pkg / "lot/a/drawings/scout.glb.import").write_text(\'[remap]\\n\\nimporter="keep"\\n\',\n                                                        encoding="utf-8")\n    (pkg / "lot/b/art/odd.glb.import").write_text(\'[remap]\\n\\nimporter="scene"\\n; not "keep"\\n\',\n                                                  encoding="utf-8")\n    _import_one(pkg, "lot/a/art/wall.glb")\n    assert kept(pkg / "lot/a/drawings/scout.glb") and not kept(pkg / "lot/b/art/odd.glb")\n    assert package_models(pkg) == ["lot/a/art/wall.glb", "lot/b/art/odd.glb"]\n    assert unimported_models(pkg) == ["lot/b/art/odd.glb"]\n\n\n')]}
NEW_FILES = {}
CHANGELOG = '## [0.234.1] - a model its sidecar keeps is not waited for\n\n**Cold run 9380 stopped at the export.** Deli Counter 0.259.0 ships each building\'s scout model as\n`drawings/scout.glb` beside a keep sidecar (`importer="keep"`): a game reads it with `GLTFDocument` when its screen\nopens, so no level pays to import it. The export\'s import check counts every `.glb` as a model Godot must import, and\nwaited for one that was never going to come: "the import pass left 3 of 537 model(s) unimported after 3 attempt(s)\n... first: lot/deli_a03/drawings/scout.glb". The level was not shipped.\n\n### Fixed\n- **`occluders.kept`**: a model whose sidecar keeps it -- its importer line `importer="keep"`, as Godot reads it -- is\n  not one Godot imports. `package_models` skips it, as it skips a folder holding `.gdignore`, so `unimported_models`\n  does not wait for it; and the export\'s three import passes neither hold it nor count it.\n\n### Tests\n- `test_import_pass_verified.py`: a kept model is not waited for, an imported one is not, an unimported one still is,\n  and a sidecar that only mentions keep somewhere else is no keep. On 0.234.0 it fails on the new name (`kept`).\n\n'
OLD_VERSION, NEW_VERSION = '0.234.0', '0.234.1'


def _sha(b):
    return hashlib.sha256(b).hexdigest()[:16]


def _read(name):
    """The file's LF text and whether it is CRLF on disk; refuses mixed endings and a file that is not the pinned one."""
    raw = (LF / name).read_bytes()
    crlf, lf = raw.count(b"\r\n"), raw.count(b"\n")
    if crlf not in (0, lf):
        raise SystemExit("REFUSED: level_factory/%s has mixed line endings (%d CRLF of %d); nothing written"
                         % (name, crlf, lf))
    text = raw.decode("utf-8").replace("\r\n", "\n")
    if _sha(text.encode("utf-8")) != PINS[name]:
        raise SystemExit("REFUSED: level_factory/%s is %s, not the %s this patch was written against; nothing "
                         "written" % (name, _sha(text.encode("utf-8")), PINS[name]))
    return text, crlf > 0


def main(argv):
    # every file worked out and checked before any is written
    out = {}
    for name, edits in EDITS.items():
        text, crlf = _read(name)
        for what, old, new in edits:
            if text.count(old) != 1:
                raise SystemExit("REFUSED: level_factory/%s: the anchor at %s is there %d times; nothing written"
                                 % (name, what, text.count(old)))
            text = text.replace(old, new)
        out[name] = text.replace("\n", "\r\n") if crlf else text
    for name in NEW_FILES:
        if (LF / name).exists():
            raise SystemExit("REFUSED: level_factory/%s exists already; nothing written" % name)
    v = LF / "VERSION"
    if v.read_bytes().decode("utf-8") != OLD_VERSION:
        raise SystemExit("REFUSED: VERSION reads %r, not %s; nothing written" % (v.read_text(), OLD_VERSION))
    cl = LF / "CHANGELOG.md"
    craw = cl.read_bytes()
    if b"\r\n" in craw or not craw.startswith(b"## [" + OLD_VERSION.encode() + b"]"):
        raise SystemExit("REFUSED: CHANGELOG.md is not LF opening on %s; nothing written" % OLD_VERSION)
    for name, text in out.items():
        (LF / name).write_bytes(text.encode("utf-8"))
    for name, text in NEW_FILES.items():
        (LF / name).write_bytes(text.encode("utf-8"))
    v.write_bytes(NEW_VERSION.encode("utf-8"))
    cl.write_bytes(CHANGELOG.encode("utf-8") + craw)
    print("Level Factory %s applied: %d files edited, %d written, VERSION, CHANGELOG. Now, in level_factory/: the "
          "suite" % (NEW_VERSION, len(out), len(NEW_FILES)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
