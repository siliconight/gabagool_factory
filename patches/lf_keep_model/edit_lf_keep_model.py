"""Level Factory 0.234.1, applied to a CLONE (<repo>): a model its sidecar keeps is not one Godot imports, so the
import check does not wait for it and the export does not hold it through its passes. Cold run 9380 stopped at the
export on Deli Counter 0.259.0's `drawings/scout.glb`, kept on purpose. Anchored; refuses on a miss."""
import pathlib
import sys

R = pathlib.Path(sys.argv[1])


def edit(rel, pairs):
    p = R / rel
    b = p.read_bytes()
    crlf = b"\r\n" in b
    t = b.decode("utf-8").replace("\r\n", "\n")
    for o, n in pairs:
        assert t.count(o) == 1, (rel, o[:70])
        t = t.replace(o, n)
    p.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))


edit("packages/exporting/occluders.py", [
    ("""#: What the import check counts as a model: the scene formats a package
#: ships (0.163.1).
MODEL_SUFFIXES = (".glb", ".gltf")
""",
     """#: What the import check counts as a model: the scene formats a package
#: ships (0.163.1).
MODEL_SUFFIXES = (".glb", ".gltf")

#: A sidecar that keeps its file as the file it is: Godot imports nothing of
#: it, by design (0.234.1). Deli Counter 0.259.0 ships each building's scout
#: model so (`drawings/scout.glb`), for a game to read with `GLTFDocument`
#: when its screen opens rather than every level importing it; cold run 9380
#: stopped at the export, "the import pass left 3 of 537 model(s) unimported
#: ... first: lot/deli_a03/drawings/scout.glb", waiting for an import that was
#: never going to come. Matched on the importer line, as Godot reads it.
_KEEP = re.compile(r'^importer="keep"\\s*$', re.M)


def kept(model: Path) -> bool:
    \"\"\"Whether ``model``'s sidecar keeps it, unimported, as the file it is.\"\"\"
    try:
        text = Path(str(model) + ".import").read_text(encoding="utf-8")
    except OSError:
        return False
    return bool(_KEEP.search(text))
"""),
    ("""    \"\"\"Every model in the package, package-relative and sorted. `.godot/` is
    the cache, not the package; a folder holding `.gdignore` is one Godot
    never imports, and is skipped the way Godot skips it.\"\"\"""",
     """    \"\"\"Every model in the package, package-relative and sorted. `.godot/` is
    the cache, not the package; a folder holding `.gdignore` is one Godot
    never imports, and is skipped the way Godot skips it -- and so is a model
    its sidecar keeps (`kept`, 0.234.1).\"\"\""""),
    ("""        if rel.parts[0] == CACHE_DIR or any(d in p.parents for d in ignored):
            continue
        out.append(rel.as_posix())""",
     """        if rel.parts[0] == CACHE_DIR or any(d in p.parents for d in ignored):
            continue
        if kept(p):
            continue
        out.append(rel.as_posix())"""),
])

edit("packages/exporting/export.py", [
    ("""    models = [p for p in sorted(export_dir.rglob("*.glb")) if ".godot" not in p.parts]""",
     """    # a model its sidecar keeps is never imported, so it is never held (0.234.1, `occluders.kept`)
    from packages.exporting.occluders import kept
    models = [p for p in sorted(export_dir.rglob("*.glb")) if ".godot" not in p.parts and not kept(p)]"""),
])

edit("tests/unit/test_import_pass_verified.py", [
    ("""def test_a_folder_godot_ignores_is_ignored(tmp_path):""",
     """def test_a_model_its_sidecar_keeps_is_not_waited_for(tmp_path):
    \"\"\"0.234.1: cold run 9380 stopped at the export on Deli Counter 0.259.0's
    `drawings/scout.glb`, which its sidecar keeps -- `[remap]` and
    `importer="keep"`, the file a game reads with `GLTFDocument` -- and which
    Godot therefore never imports. It is no model of the import's; a sidecar
    that only mentions keep somewhere else is not a keep.\"\"\"
    from packages.exporting.occluders import kept, package_models
    pkg = _package(tmp_path, rels=("lot/a/art/wall.glb", "lot/a/drawings/scout.glb",
                                   "lot/b/art/odd.glb"))
    (pkg / "lot/a/drawings/scout.glb.import").write_text('[remap]\\n\\nimporter="keep"\\n',
                                                        encoding="utf-8")
    (pkg / "lot/b/art/odd.glb.import").write_text('[remap]\\n\\nimporter="scene"\\n; not "keep"\\n',
                                                  encoding="utf-8")
    _import_one(pkg, "lot/a/art/wall.glb")
    assert kept(pkg / "lot/a/drawings/scout.glb") and not kept(pkg / "lot/b/art/odd.glb")
    assert package_models(pkg) == ["lot/a/art/wall.glb", "lot/b/art/odd.glb"]
    assert unimported_models(pkg) == ["lot/b/art/odd.glb"]


def test_a_folder_godot_ignores_is_ignored(tmp_path):"""),
])

v = R / "VERSION"
assert v.read_bytes() == b"0.234.0", v.read_bytes()
v.write_bytes(b"0.234.1")
print("edited", R)
