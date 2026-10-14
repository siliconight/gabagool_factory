"""Level Factory 0.210.0: the kit modules only merged slots instanced, out of the package (factory roadmap 249, found
attributing cold run 9304's package).

`merge_empties` folds an Empty's sided slots into `lot/<id>/merged/<side>_<n>.res` and removes the slot children
that instanced `lot/<id>/art/zoo/*.glb`. The modules stayed in the package, and the light bake's `mark_imports`, which
walks every `*.glb.import`, set each to Static Lightmaps and unwrapped it at import. Measured on 9304's package
(`docs/findings/fire_escape/unreferenced_glbs.py`): 289 of 612 GLBs named by no scene, 286 of them modules under the
Empties' `art/zoo/` -- windows 191, walls 39, doorways 20, roofs 10, wall ends 10, props 17 -- and 315 of the bake's
632 model imports files no scene named. A merged mesh names no module: its materials are duplicates pointing at
`art/zoo/_tex/*.png` (read off gs_midrise_c's thirteen `merged/*.res`, no `.glb` in any).

`drop_merged_modules(export_dir, report)` removes, for each Empty the report merged, every `art/zoo/*.glb` that no
file of the package names by its file name -- a scene, resource, script, manifest or config, the import cache and
the package's two lists of its own files aside -- with its `.import` and `.unwrap_cache`. The export calls it after
the merge and before the light bake; the closure verdict (4.9) and the resource manifest (4.96) are written after
both, so they see the folder as shipped.

Anchored edits, each asserted exactly once and every file's sha16 pinned, nothing written until all matched:
  packages/exporting/merge_empties.py  the docstring's WHAT GOES AFTER IT; `NAMING_SUFFIXES`, `FILE_LISTS`,
                                       `drop_merged_modules`, at the end
  packages/exporting/export.py         the call and its line, after the merge's own line
  tests/unit/test_merged_modules_dropped.py   new, from `lf_drop_merged_modules/test_merged_modules_dropped.py.txt`
CHANGELOG and VERSION from `lf_drop_merged_modules/CHANGELOG_0.210.0.md`; `--results-pending` leaves the RESULT_
keys to `--fill`.

Read before it was written, in this session: `merge_empties.py` whole; `export.py` from the occluder bake through
the light bake (2255-2340) and the closure verdict, resource manifest and `_WRITTEN_AFTER_VERDICT` (1225-1260,
2509-2560); `light_bake.mark_imports`; 9305's package (an Empty's files, `occluders.json`'s `modules`, the root
JSONs, every `.gd`, `.cfg` and `.tres` for module names, `merged/*.res` for references). Every file LF.

    python patches/patch_lf_drop_merged_modules.py --results-pending
    (python -m pytest -q in level_factory; docs/findings/merged_modules/mirror.sh)
    python patches/patch_lf_drop_merged_modules.py --fill
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_drop_merged_modules"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_MIRROR": "result_mirror.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.209.0", b"0.210.0"
CHANGELOG_HEAD = "## [0.209.0] - A walk-up's fire escape merges with its front"
NEW_TEST = ("tests/unit/test_merged_modules_dropped.py", "test_merged_modules_dropped.py.txt")
SHA = {"packages/exporting/merge_empties.py": "c36a68b1cdce9bfd",
       "packages/exporting/export.py": "40693bd52b158cf6"}

DROP = '''

#: What can name a file in a package: a scene or a resource by `path="res://..."`, a script, a manifest or a config
#: by its path or its bare file name (0.210.0).
NAMING_SUFFIXES = (".tscn", ".tres", ".gd", ".json", ".cfg", ".godot")
#: The package's own lists of every file it carries: they name a module and never load one.
FILE_LISTS = frozenset({"portable_resource_manifest.json", "light_bake.json"})


def drop_merged_modules(export_dir: Path, report: dict) -> dict:
    """The kit modules only merged slots instanced, out of the package (0.210.0, factory roadmap 249).

    `merge` folds an Empty's sided slots into `lot/<id>/merged/<side>_<n>.res` and removes the slot children
    that instanced `lot/<id>/art/zoo/*.glb`. The modules stayed, and the light bake set each to Static Lightmaps
    and unwrapped it at import. Measured on cold run 9304's package: 286 module GLBs in its Empties named by no
    scene, and 315 of the bake's 632 model imports files no scene named (the factory's
    `docs/findings/fire_escape/unreferenced_glbs.py`). A merged mesh names no module: its materials are
    duplicates pointing at the textures under `art/zoo/_tex/`, which stay.

    For each Empty the report merged, an `art/zoo/*.glb` that no file of the package names by its file name --
    a scene, resource, script, manifest or config (`NAMING_SUFFIXES`; the import cache and `FILE_LISTS` aside)
    -- is removed with its `.import` and `.unwrap_cache`. A bare name is matched, not a path, so a module that
    shares its name with one another lot's scene instances is kept: the rule errs toward shipping a file.
    Nothing outside a merged Empty's `art/zoo/` is touched -- the responders' car under `cover/` is loaded by
    path. Returns `{"dropped": [package-relative paths], "bytes": n, "kept": n}`."""
    export_dir = Path(export_dir)
    lots = set()
    for row in (report or {}).get("scenes") or []:
        m = re.fullmatch(r"res://(lot/[^/]+)/site\\.tscn", str(row.get("scene", "")))
        if m and row.get("error") is None and int(row.get("merged") or 0) > 0:
            lots.add(m.group(1))
    out = {"dropped": [], "bytes": 0, "kept": 0}
    if not lots:
        return out
    texts = []
    for p in sorted(export_dir.rglob("*")):
        if (p.suffix in NAMING_SUFFIXES and p.name not in FILE_LISTS
                and ".godot" not in p.relative_to(export_dir).parts and p.is_file()):
            texts.append(p.read_text(encoding="utf-8", errors="replace"))
    named = "\\n".join(texts)
    for lot in sorted(lots):
        for glb in sorted((export_dir / lot / "art" / "zoo").glob("*.glb")):
            if glb.name in named:
                out["kept"] += 1
                continue
            for f in (glb, glb.with_name(glb.name + ".import"), glb.with_name(glb.name + ".unwrap_cache")):
                if f.is_file():
                    out["bytes"] += f.stat().st_size
                    f.unlink()
            out["dropped"].append(glb.relative_to(export_dir).as_posix())
    return out
'''

EDITS = {
    "packages/exporting/merge_empties.py": [
        ("The Godot half (`assets/godot/merge_empties.gd`) does what only Godot can;\n",
         "WHAT GOES AFTER IT (0.210.0, roadmap 249): a merged Empty's kit modules that\n"
         "no file of the package names any longer, with their sidecars --\n"
         "`drop_merged_modules`, which the export calls before the light bake imports\n"
         "every model it finds.\n"
         "\n"
         "The Godot half (`assets/godot/merge_empties.gd`) does what only Godot can;\n"),
        ("    except (OSError, ValueError) as exc:\n"
         "        raise MergeError(f\"report unreadable: {exc}\") from exc\n"
         "    return check(report, asked)\n",
         "    except (OSError, ValueError) as exc:\n"
         "        raise MergeError(f\"report unreadable: {exc}\") from exc\n"
         "    return check(report, asked)\n" + DROP),
    ],
    "packages/exporting/export.py": [
        ("        rows = mreport.get(\"scenes\") or []\n"
         "        if rows:\n"
         "            print(\"[export] Empties merged: %d scene(s), %d mesh(es) of %d surface(s) \"\n"
         "                  \"-> %d merged mesh(es), %d collider(s) kept\"\n"
         "                  % (len(rows), sum(r[\"meshes_in\"] for r in rows),\n"
         "                     sum(r[\"surfaces_in\"] for r in rows),\n"
         "                     sum(r[\"merged\"] for r in rows), sum(r[\"colliders\"] for r in rows)))\n",
         "        rows = mreport.get(\"scenes\") or []\n"
         "        if rows:\n"
         "            print(\"[export] Empties merged: %d scene(s), %d mesh(es) of %d surface(s) \"\n"
         "                  \"-> %d merged mesh(es), %d collider(s) kept\"\n"
         "                  % (len(rows), sum(r[\"meshes_in\"] for r in rows),\n"
         "                     sum(r[\"surfaces_in\"] for r in rows),\n"
         "                     sum(r[\"merged\"] for r in rows), sum(r[\"colliders\"] for r in rows)))\n"
         "            # THE MODULES ONLY MERGED SLOTS INSTANCED (0.210.0, roadmap 249) go\n"
         "            # before the light bake, which imports every model it finds for a\n"
         "            # lightmap; the closure verdict and the resource manifest, written\n"
         "            # after both, see the folder as it ships.\n"
         "            from packages.exporting.merge_empties import drop_merged_modules\n"
         "            dropped = drop_merged_modules(export_dir, mreport)\n"
         "            print(\"[export] merged Empties' modules no file names: %d removed (%.1f MB), \"\n"
         "                  \"%d named and kept\" % (len(dropped[\"dropped\"]), dropped[\"bytes\"] / 1e6,\n"
         "                                         dropped[\"kept\"]))\n"),
    ],
}


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def fill():
    assert (LF / "VERSION").read_bytes().strip() == VERSION, (LF / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value and not value.endswith("."), (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.210.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.210.0: results filled")


def main():
    if FILL:
        return fill()
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.210.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.210.0] - "), entry[:40]
    left = entry
    for key in RESULTS if PENDING else ():
        left = left.replace(key, "")
    assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    test_dst = LF / NEW_TEST[0]
    assert not test_dst.exists(), (test_dst, "already exists")
    test_src = (SRC / NEW_TEST[1]).read_bytes().replace(b"\r\n", b"\n")
    writes = {}
    for rel, pairs in EDITS.items():
        p = LF / rel
        raw = p.read_bytes()
        got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
        assert got == SHA[rel], (rel, "is not the file this patch read", got)
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for old, new in pairs:
            assert text.count(old) == 1, (rel, "anchor", text.count(old), old[:80])
            text = text.replace(old, new)
        writes[p] = text.encode("utf-8").replace(b"\n", eol)
    cl = LF / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD), cl_text[:120]
    # every anchor matched: now write
    for p, data in writes.items():
        p.write_bytes(data)
    test_dst.write_bytes(test_src)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).encode("utf-8").replace(b"\n", cl_eol))
    (LF / "VERSION").write_bytes(VERSION)
    print("Level Factory 0.209.0 -> 0.210.0")


if __name__ == "__main__":
    main()
