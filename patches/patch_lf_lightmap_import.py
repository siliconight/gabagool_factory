"""Level Factory 0.183.0: the editor's import of the lightmap is kept, not done again (factory roadmap
239, the export).

Anchored edits in `packages/exporting/light_bake.py`, each asserted once, nothing written until all
of them matched: `_copy_lightmap_import` (the work copy's cache entries for `bake.exr`, into the
package's cache) before `_import`, and `bake` calls it after copying `BAKE_FILES` back, recording
what it copied; a new `tests/unit/test_lightmap_import_is_kept.py` from `lf_lightmap_import/`.
CHANGELOG and VERSION from `lf_lightmap_import/CHANGELOG_0.183.0.md`; `--results-pending` leaves the
RESULT_ keys to `--fill`.

    python patches/patch_lf_lightmap_import.py --results-pending && cd level_factory && python -m pytest -q
    python patches/patch_lf_lightmap_import.py --fill
    LF_ROOT=<copy> python patches/patch_lf_lightmap_import.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_lightmap_import"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_AB": "result_ab.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.182.0", b"0.183.0"
CHANGELOG_HEAD = ("## [0.182.0] - The shared textures' import pins are applied again after the last "
                  "import, and read back off what ships\n")
BAKE = "packages/exporting/light_bake.py"
TEST = "tests/unit/test_lightmap_import_is_kept.py"
SHA = {BAKE: "5967b9d9577a8d8a"}

F_OLD = "def _import(export_dir: Path, godot) -> bool:\n"
F_NEW = (
    "def _copy_lightmap_import(work: Path, export_dir: Path) -> list:\n"
    "    \"\"\"THE EDITOR'S IMPORT OF THE LIGHTMAP, KEPT (0.183.0, factory roadmap 239).\n"
    "\n"
    "    The editor that bakes imports what it baked: `bake.exr`, a 1024 x 1024\n"
    "    texture array of 16 slices, VRAM-compressed (BPTC) as its sidecar says.\n"
    "    The package then imported the same bytes again, and measured on cold run\n"
    "    9248's export that second `--import` imported that one file and nothing\n"
    "    else, in 49.5 s. This copies the work copy's cache entries for it into the\n"
    "    package's cache beside the sidecar `BAKE_FILES` already copies, so the\n"
    "    import after finds them current: an entry is named for the file's\n"
    "    `res://` path and checked against its source's hash and its parameters,\n"
    "    all three the same files in both projects. Returns the names copied;\n"
    "    none when either cache is missing, and the import after does the work\n"
    "    as it always did.\"\"\"\n"
    "    src = Path(work) / \".godot\" / \"imported\"\n"
    "    dst = Path(export_dir) / \".godot\" / \"imported\"\n"
    "    if not src.is_dir() or not dst.is_dir():\n"
    "        return []\n"
    "    copied = []\n"
    "    for name in BAKE_FILES:\n"
    "        if not name.endswith(\".exr\"):\n"
    "            continue\n"
    "        for p in sorted(src.glob(name + \"-*\")):\n"
    "            shutil.copy2(p, dst / p.name)\n"
    "            copied.append(p.name)\n"
    "    return copied\n"
    "\n"
    "\n"
    "def _import(export_dir: Path, godot) -> bool:\n")
C_OLD = ("        for f in BAKE_FILES:\n"
         "            src = work / f\n"
         "            if not src.exists():\n"
         "                raise RuntimeError(f\"the bake wrote no {f}\")\n"
         "            shutil.copy(src, export_dir / f)\n")
C_NEW = ("        for f in BAKE_FILES:\n"
         "            src = work / f\n"
         "            if not src.exists():\n"
         "                raise RuntimeError(f\"the bake wrote no {f}\")\n"
         "            shutil.copy(src, export_dir / f)\n"
         "        # the editor's import of the lightmap, kept rather than done again (0.183.0)\n"
         "        report[\"lightmap_import_copied\"] = _copy_lightmap_import(work, export_dir)\n")


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
    for path, rel in [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.183.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.183.0: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("LF_ROOT"):
        sys.exit("refusing: --draft is for an LF_ROOT copy, never the repo")
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.183.0.md")
    assert entry.startswith("## [0.183.0] - "), entry[:40]
    if not DRAFT:
        left = entry
        if PENDING:
            for key in RESULTS:
                left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    test_text = _src("test_lightmap_import_is_kept.py.txt")
    assert not (LF / TEST).exists(), "already applied"
    bp, b_eol, bake = _read(BAKE)
    assert "def _copy_lightmap_import" not in bake, "already applied"
    bake = _once(bake, F_OLD, F_NEW, "before _import")
    bake = _once(bake, C_OLD, C_NEW, "the copy back")
    cl = LF / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:160]
    # every anchor matched: now write
    _write(bp, b_eol, bake)
    (LF / TEST).write_bytes(test_text.encode("utf-8"))
    _write(cl, cl_eol, entry.rstrip("\n") + "\n\n" + cl_text)
    (LF / "VERSION").write_bytes(VERSION)
    print("Level Factory 0.182.0 -> 0.183.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
