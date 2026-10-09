"""Level Factory 0.163.1: the import pass checks its own work.

Cold run 9214's export ran Godot's `--import` once, kept neither its exit code
nor its output, and went on: the pass had imported none of the package's 425
models, the occluder bake reported `ok` with 0 modules, and the Empties' merge
was the first step to refuse. The same package imported 425 of 425 in seven
fresh reruns.

Anchored edits, every anchor once, nothing written until all matched:
- `packages/exporting/occluders.py`: `MODEL_SUFFIXES`, `package_models` and
  `unimported_models` before `ensure_imported`; `ensure_imported` returns
  early only on a cache with every model imported, and refuses an import that
  leaves any behind;
- `packages/exporting/export.py`: `IMPORT_PASSES` after
  `OCCLUDERS_ENFORCED`; `ExportImportError` after `ExportOccluderError`;
  `_write_import_sidecars` checks each pass, repeats a short one, keeps every
  pass's output in `<package>.import.log` beside the package, and raises on a
  pass that never completes;
- `tests/fixtures/bin/godot.py`: the stub's `--import` writes each model's
  sidecar and its imported file, as the real one does. Its bare `.godot`
  had passed only because nothing checked.
New: `tests/unit/test_import_pass_verified.py`. CHANGELOG and VERSION from
`lf_import_pass_verified/CHANGELOG_0.163.1.md`.

    python patch_lf_import_pass_verified.py
    LF_ROOT=<copy> python patch_lf_import_pass_verified.py [--draft]
"""
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_import_pass_verified"
DRAFT = "--draft" in sys.argv
EX = "packages/exporting/"

OCC_HELPERS_OLD = (
    "def ensure_imported(export_dir: Path, godot_executable, *,\n"
    "                    timeout: int = 1200) -> bool:\n"
)
OCC_HELPERS_NEW = (
    "#: What the import check counts as a model: the scene formats a package\n"
    "#: ships (0.163.1).\n"
    "MODEL_SUFFIXES = (\".glb\", \".gltf\")\n"
    "\n"
    "\n"
    "def package_models(export_dir: Path) -> list:\n"
    "    \"\"\"Every model in the package, package-relative and sorted. `.godot/` is\n"
    "    the cache, not the package; a folder holding `.gdignore` is one Godot\n"
    "    never imports, and is skipped the way Godot skips it.\"\"\"\n"
    "    export_dir = Path(export_dir)\n"
    "    ignored = [g.parent for g in export_dir.rglob(\".gdignore\")]\n"
    "    out = []\n"
    "    for p in export_dir.rglob(\"*\"):\n"
    "        if p.suffix.lower() not in MODEL_SUFFIXES or not p.is_file():\n"
    "            continue\n"
    "        rel = p.relative_to(export_dir)\n"
    "        if rel.parts[0] == CACHE_DIR or any(d in p.parents for d in ignored):\n"
    "            continue\n"
    "        out.append(rel.as_posix())\n"
    "    return sorted(out)\n"
    "\n"
    "\n"
    "_DEST_FILES = re.compile(r\"^dest_files=\\[(.*)\\]\\s*$\", re.M)\n"
    "\n"
    "\n"
    "def unimported_models(export_dir: Path) -> list:\n"
    "    \"\"\"The package's models Godot has not imported HERE (0.163.1): no\n"
    "    `.import` sidecar, a sidecar naming no `dest_files` -- an unrecognised\n"
    "    shape is not evidence of an import -- or one whose files are not in the\n"
    "    cache. Read off a real sidecar, cold run 9214's\n"
    "    `doorway_delco_1997_01_w100_mbrick_orange_enavy_o3e3b2d.glb.import`,\n"
    "    Godot 4.7: `[deps]` carries `dest_files=[\"res://.godot/imported/\n"
    "    <name>-<hash>.scn\"]`.\n"
    "\n"
    "    COLD RUN 9214 IS WHY. Its export's first `--import` left sidecars on 140\n"
    "    of the package's 975 importable files -- SkyMint's, which arrive with\n"
    "    Lux's runtime -- and on none of its 425 models, and nothing looked: the\n"
    "    occluder bake loaded a scene whose every module was missing and said\n"
    "    `ok` with 0 modules, and the Empties' merge was the first step to\n"
    "    refuse. A shipped package, which keeps its sidecars and drops the cache,\n"
    "    lists every model here, and that is true: none is imported in it.\n"
    "    \"\"\"\n"
    "    export_dir = Path(export_dir)\n"
    "    out = []\n"
    "    for rel in package_models(export_dir):\n"
    "        try:\n"
    "            text = (export_dir / (rel + \".import\")).read_text(encoding=\"utf-8\")\n"
    "        except OSError:\n"
    "            out.append(rel)\n"
    "            continue\n"
    "        m = _DEST_FILES.search(text)\n"
    "        dests = re.findall(r'\"res://([^\"]+)\"', m.group(1)) if m else []\n"
    "        if not dests or not all((export_dir / d).is_file() for d in dests):\n"
    "            out.append(rel)\n"
    "    return out\n"
    "\n"
    "\n"
    + OCC_HELPERS_OLD
)

OCC_ENSURE_OLD = (
    "    cache before the package ships; `drop_cache` below is that.\n"
    "    \"\"\"\n"
    "    export_dir = Path(export_dir)\n"
    "    if (export_dir / CACHE_DIR).is_dir():\n"
    "        return False\n"
    "    if not godot_executable:\n"
    "        raise OccluderError(\"no Godot executable: occluders cannot be measured\")\n"
    "    try:\n"
    "        subprocess.run(\n"
    "            [str(godot_executable), \"--headless\", \"--path\", str(export_dir),\n"
    "             \"--import\"],\n"
    "            capture_output=True, text=True, timeout=timeout)\n"
    "    except (OSError, subprocess.SubprocessError) as exc:\n"
    "        raise OccluderError(f\"import pass did not run: {exc}\") from exc\n"
    "    if not (export_dir / CACHE_DIR).is_dir():\n"
    "        raise OccluderError(\n"
    "            \"import pass left no %s cache: the bake cannot load anything\"\n"
    "            % CACHE_DIR)\n"
    "    return True\n"
)
OCC_ENSURE_NEW = (
    "    cache before the package ships; `drop_cache` below is that.\n"
    "\n"
    "    A CACHE FOLDER IS NOT AN IMPORT (0.163.1). This returned on `is_dir()`,\n"
    "    and cold run 9214's export reached it with a `.godot` its first pass had\n"
    "    made and left without a single model in it. It returns early only when\n"
    "    `unimported_models` is empty too, and refuses an import that leaves any\n"
    "    model behind.\n"
    "    \"\"\"\n"
    "    export_dir = Path(export_dir)\n"
    "    if (export_dir / CACHE_DIR).is_dir() and not unimported_models(export_dir):\n"
    "        return False\n"
    "    if not godot_executable:\n"
    "        raise OccluderError(\"no Godot executable: occluders cannot be measured\")\n"
    "    try:\n"
    "        subprocess.run(\n"
    "            [str(godot_executable), \"--headless\", \"--path\", str(export_dir),\n"
    "             \"--import\"],\n"
    "            capture_output=True, text=True, timeout=timeout)\n"
    "    except (OSError, subprocess.SubprocessError) as exc:\n"
    "        raise OccluderError(f\"import pass did not run: {exc}\") from exc\n"
    "    if not (export_dir / CACHE_DIR).is_dir():\n"
    "        raise OccluderError(\n"
    "            \"import pass left no %s cache: the bake cannot load anything\"\n"
    "            % CACHE_DIR)\n"
    "    left = unimported_models(export_dir)\n"
    "    if left:\n"
    "        raise OccluderError(\n"
    "            \"import pass left %d model(s) unimported, first %s: the bake \"\n"
    "            \"cannot load them\" % (len(left), left[0]))\n"
    "    return True\n"
)

EX_PASSES_OLD = (
    "#: that comes out of it is consistent, with the culler off.\n"
    "OCCLUDERS_ENFORCED = True\n"
)
EX_PASSES_NEW = (
    EX_PASSES_OLD
    + "\n"
    "\n"
    "#: How many times the export runs Godot's `--import` before it calls the\n"
    "#: import failed (0.163.1). CHOSEN, not derived: one short pass was seen in\n"
    "#: eight on cold run 9214's package, a pass costs about 40 s there, and 3\n"
    "#: bounds a bad export at about two minutes before it says so.\n"
    "IMPORT_PASSES = 3\n"
)

EX_ERROR_OLD = (
    "class ExportOccluderError(RuntimeError):\n"
    "    \"\"\"The package's occluders could not be measured, or the culling flag and\n"
    "    the occluders that shipped do not agree.\"\"\"\n"
)
EX_ERROR_NEW = (
    EX_ERROR_OLD
    + "\n"
    "\n"
    "class ExportImportError(RuntimeError):\n"
    "    \"\"\"Godot's `--import` was run `IMPORT_PASSES` times with a Godot present\n"
    "    and left models the package carries unimported (0.163.1, cold run 9214):\n"
    "    every step after it loads them.\"\"\"\n"
)

EX_PASS_OLD = (
    "    Best-effort. A missing Godot is a setup problem, not an export failure, and\n"
    "    HANDOFF.md tells the recipient what to do either way.\n"
    "    \"\"\"\n"
    "    if not godot_executable:\n"
    "        return 0\n"
    "    import shutil as _shutil\n"
    "    import subprocess as _subprocess\n"
    "\n"
    "    def _import_pass() -> bool:\n"
    "        try:\n"
    "            _subprocess.run(\n"
    "                [str(godot_executable), \"--headless\", \"--path\",\n"
    "                 str(export_dir), \"--import\"],\n"
    "                capture_output=True, text=True, timeout=1200)\n"
    "            return True\n"
    "        except (OSError, _subprocess.SubprocessError):\n"
    "            return False\n"
    "\n"
    "    if not _import_pass():\n"
    "        return 0\n"
)
EX_PASS_NEW = (
    "    Best-effort only where Godot is missing: that is a setup problem, not an\n"
    "    export failure, and HANDOFF.md tells the recipient what to do either way.\n"
    "\n"
    "    NOT BEST-EFFORT WHERE GODOT IS THERE (0.163.1), and cold run 9214 is why.\n"
    "    Its first pass left sidecars on 140 of the package's 975 importable files\n"
    "    -- SkyMint's, which arrive with Lux's runtime -- and on none of its 425\n"
    "    models. This threw the pass's exit code and output away and returned;\n"
    "    `ensure_imported` took the `.godot` folder for an import; the occluder\n"
    "    bake loaded a scene whose every module was missing and reported `ok`\n"
    "    with 0 modules; and the Empties' merge was the first step to refuse. The\n"
    "    same package imported 425 of 425 in seven fresh reruns, two of them from\n"
    "    the export's exact starting state, so the pass is a transient and the\n"
    "    cure is to look: every pass is checked by `occluders.unimported_models`\n"
    "    and repeated up to `IMPORT_PASSES` times, every pass's exit code and\n"
    "    output go to `<package>.import.log` beside the package -- not in it,\n"
    "    where the resource manifest would have to account for it -- and a pass\n"
    "    that never completes raises `ExportImportError`.\n"
    "    \"\"\"\n"
    "    if not godot_executable:\n"
    "        return 0\n"
    "    import shutil as _shutil\n"
    "    import subprocess as _subprocess\n"
    "\n"
    "    from packages.exporting.occluders import (package_models,\n"
    "                                              unimported_models)\n"
    "    log_path = export_dir.parent / (export_dir.name + \".import.log\")\n"
    "    log_path.unlink(missing_ok=True)  # this export's passes, not the last one's\n"
    "    passes: list = []\n"
    "\n"
    "    def _import_pass() -> None:\n"
    "        \"\"\"One `--import`, its exit code and output appended to the log.\"\"\"\n"
    "        try:\n"
    "            done = _subprocess.run(\n"
    "                [str(godot_executable), \"--headless\", \"--path\",\n"
    "                 str(export_dir), \"--import\"],\n"
    "                capture_output=True, timeout=1200)\n"
    "            code = getattr(done, \"returncode\", None)\n"
    "            out = ((getattr(done, \"stdout\", None) or b\"\")\n"
    "                   + (getattr(done, \"stderr\", None) or b\"\"))\n"
    "        except (OSError, _subprocess.SubprocessError) as exc:\n"
    "            code, out = None, (\"did not run: %s\\n\" % exc).encode(\"utf-8\", \"replace\")\n"
    "        passes.append(code)\n"
    "        with open(log_path, \"ab\") as fh:\n"
    "            fh.write((\"==== import pass %d: exit %s\\n\" % (len(passes), code))\n"
    "                     .encode(\"utf-8\"))\n"
    "            fh.write(out if isinstance(out, bytes)\n"
    "                     else str(out).encode(\"utf-8\", \"replace\"))\n"
    "\n"
    "    def _import_pass_verified() -> None:\n"
    "        \"\"\"Import until every model is, at most `IMPORT_PASSES` times.\"\"\"\n"
    "        for n in range(1, IMPORT_PASSES + 1):\n"
    "            _import_pass()\n"
    "            left = unimported_models(export_dir)\n"
    "            if not left:\n"
    "                if n > 1:\n"
    "                    print(\"[export] import: every model imported on attempt %d \"\n"
    "                          \"(%s)\" % (n, log_path))\n"
    "                return\n"
    "            print(\"[export] import pass %d left %d model(s) unimported, first \"\n"
    "                  \"%s\" % (len(passes), len(left), left[0]))\n"
    "        raise ExportImportError(\n"
    "            \"the import pass left %d of %d model(s) unimported after %d \"\n"
    "            \"attempt(s) and this build had a Godot to run it with; first: \"\n"
    "            \"%s\\n  Godot's output: %s\"\n"
    "            % (len(left), len(package_models(export_dir)), IMPORT_PASSES,\n"
    "               left[0], log_path))\n"
    "\n"
    "    _import_pass_verified()\n"
)

EX_SECOND_OLD = (
    "        _shutil.rmtree(export_dir / \".godot\", ignore_errors=True)\n"
    "        _import_pass()\n"
)
EX_SECOND_NEW = (
    "        _shutil.rmtree(export_dir / \".godot\", ignore_errors=True)\n"
    "        _import_pass_verified()\n"
)

STUB_OLD = (
    "    if \"--import\" in argv:\n"
    "        proj = Path(argv[argv.index(\"--path\") + 1]) if \"--path\" in argv else Path(\".\")\n"
    "        (proj / \".godot\" / \"imported\").mkdir(parents=True, exist_ok=True)\n"
    "        return 0\n"
)
STUB_NEW = (
    "    #\n"
    "    # AND IT IMPORTS THE MODELS (Level Factory 0.163.1), because the export\n"
    "    # now checks that the real one did. Every `.glb`/`.gltf` outside `.godot/`\n"
    "    # and any `.gdignore` folder gets the sidecar Godot 4.7 writes -- `[deps]`\n"
    "    # `dest_files` naming `res://.godot/imported/<name>-<md5 of its res://\n"
    "    # path>.scn` -- and that file. Cold run 9214's first pass imported none,\n"
    "    # and the export went on to measure an empty scene.\n"
    "    if \"--import\" in argv:\n"
    "        proj = Path(argv[argv.index(\"--path\") + 1]) if \"--path\" in argv else Path(\".\")\n"
    "        cache = proj / \".godot\" / \"imported\"\n"
    "        cache.mkdir(parents=True, exist_ok=True)\n"
    "        import hashlib\n"
    "        ignored = [g.parent for g in proj.rglob(\".gdignore\")]\n"
    "        for p in proj.rglob(\"*\"):\n"
    "            if p.suffix.lower() not in (\".glb\", \".gltf\") or not p.is_file():\n"
    "                continue\n"
    "            rel = p.relative_to(proj)\n"
    "            if rel.parts[0] == \".godot\" or any(d in p.parents for d in ignored):\n"
    "                continue\n"
    "            res = \"res://\" + rel.as_posix()\n"
    "            dest = \"%s-%s.scn\" % (p.name, hashlib.md5(res.encode(\"utf-8\")).hexdigest())\n"
    "            (cache / dest).write_bytes(b\"stub\")\n"
    "            Path(str(p) + \".import\").write_text(\n"
    "                '[remap]\\n\\nimporter=\"scene\"\\nimporter_version=1\\n'\n"
    "                'type=\"PackedScene\"\\npath=\"res://.godot/imported/%s\"\\n\\n'\n"
    "                '[deps]\\n\\nsource_file=\"%s\"\\n'\n"
    "                'dest_files=[\"res://.godot/imported/%s\"]\\n\\n[params]\\n\\n'\n"
    "                'nodes/root_type=\"\"\\n' % (dest, res, dest), encoding=\"utf-8\")\n"
    "        return 0\n"
)

EDITS = {
    EX + "occluders.py": [(OCC_HELPERS_OLD, OCC_HELPERS_NEW), (OCC_ENSURE_OLD, OCC_ENSURE_NEW)],
    EX + "export.py": [(EX_PASSES_OLD, EX_PASSES_NEW), (EX_ERROR_OLD, EX_ERROR_NEW),
                       (EX_PASS_OLD, EX_PASS_NEW), (EX_SECOND_OLD, EX_SECOND_NEW)],
    "tests/fixtures/bin/godot.py": [(STUB_OLD, STUB_NEW)],
}


def main():
    if DRAFT and not os.environ.get("LF_ROOT"):
        raise SystemExit("--draft writes a copy: set LF_ROOT")
    v = (LF / "VERSION").read_text(encoding="utf-8").strip()
    assert v == "0.163.0", v
    entry = (SRC / "CHANGELOG_0.163.1.md").read_text(encoding="utf-8")
    assert DRAFT or "RESULT_" not in entry, "the changelog still carries an unfilled result"
    staged = {}
    for rel, pairs in EDITS.items():
        p = LF / rel
        d = p.read_bytes()
        assert b"\r\n" not in d, (rel, "has CRLF; this patch writes LF files")
        t = d.decode("utf-8")
        assert ("unimported_models" not in t and "IMPORT_PASSES" not in t
                and "IT IMPORTS THE MODELS" not in t), (rel, "already applied")
        for old, new in pairs:
            n = t.count(old)
            assert n == 1, (rel, n, old[:70])
            t = t.replace(old, new)
        staged[p] = t.encode("utf-8")
    test = LF / "tests" / "unit" / "test_import_pass_verified.py"
    assert not test.exists(), test
    cl = LF / "CHANGELOG.md"
    d = cl.read_bytes()
    assert b"## [0.163.1]" not in d
    head = b"## [0.163.0]"
    assert d.startswith(head)
    for p, raw in staged.items():
        p.write_bytes(raw)
    test.write_bytes((SRC / "test_import_pass_verified.py").read_bytes().replace(b"\r\n", b"\n"))
    cl.write_bytes(entry.encode("utf-8").replace(b"\r\n", b"\n") + b"\n" + d)
    (LF / "VERSION").write_bytes(b"0.163.1")
    print("Level Factory 0.163.0 -> 0.163.1" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
