"""Level Factory 0.182.0: the shared textures' import pins, re-applied after the last import and read
back off the files that ship (`docs/findings/texture_pins/`).

Anchored edits in `packages/exporting/export.py`, each asserted once, nothing written until all of
them matched: `_shared_texture_pins_missing` and `_repin_after_imports` after
`_pin_shared_texture_imports`, and the export calls the second between the cache drop and the
closure verdict, printing what it re-pinned; a new `tests/unit/test_texture_pins_survive_the_bake.py`
from `lf_texture_repin/`. CHANGELOG and VERSION from `lf_texture_repin/CHANGELOG_0.182.0.md`;
`--results-pending` leaves the RESULT_ keys to `--fill`.

    python patches/patch_lf_texture_repin.py --results-pending && cd level_factory && python -m pytest -q
    python patches/patch_lf_texture_repin.py --fill
    LF_ROOT=<copy> python patches/patch_lf_texture_repin.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_texture_repin"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_AB": "result_ab.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.181.0", b"0.182.0"
CHANGELOG_HEAD = ("## [0.181.0] - The greybox census reads the bake's import cache instead of "
                  "importing the package again\n")
EXPORT = "packages/exporting/export.py"
TEST = "tests/unit/test_texture_pins_survive_the_bake.py"
SHA = {EXPORT: "0e88a956aa09d182"}

H_OLD = ("            changed += 1\n"
         "    return changed\n"
         "\n"
         "\n"
         "#: The folder Lot copies a dealt business's sign maps into, beside its scene\n")
H_NEW = (
    "            changed += 1\n"
    "    return changed\n"
    "\n"
    "\n"
    "def _shared_texture_pins_missing(export_dir: Path) -> list:\n"
    "    \"\"\"Every `SHARED_TEX_DIR` sidecar not carrying its pins, as ``(path, key,\n"
    "    value found)`` with the first key that is off or absent -- what the\n"
    "    package would ship wrong. The cache is not the package and is skipped.\"\"\"\n"
    "    filtered = _filtered_shared_textures(export_dir)\n"
    "    out = []\n"
    "    for sidecar in sorted(export_dir.rglob(\"*.png.import\")):\n"
    "        if sidecar.parent.name != SHARED_TEX_DIR or \".godot\" in sidecar.parts:\n"
    "            continue\n"
    "        pins = dict(SHARED_TEX_PINS)\n"
    "        if sidecar.with_name(sidecar.name[:-len(\".import\")]).resolve() in filtered:\n"
    "            pins.update(FILTERED_TEX_PINS)\n"
    "        have = {}\n"
    "        for ln in sidecar.read_text(encoding=\"utf-8\").splitlines():\n"
    "            key, eq, value = ln.partition(\"=\")\n"
    "            if eq:\n"
    "                have.setdefault(key, value)\n"
    "        for key, want in pins.items():\n"
    "            if have.get(key) != want:\n"
    "                out.append((sidecar.relative_to(export_dir).as_posix(), key, have.get(key)))\n"
    "                break\n"
    "    return out\n"
    "\n"
    "\n"
    "def _repin_after_imports(export_dir: Path) -> dict:\n"
    "    \"\"\"THE PINS AGAIN, AFTER THE LAST IMPORT, AND READ BACK (0.182.0).\n"
    "\n"
    "    The pins are written once, between the sidecar step's two passes, and\n"
    "    every import after that runs over them. One of those undoes some:\n"
    "    measured (factory `docs/findings/texture_pins/`), the light bake's first\n"
    "    `--import` -- re-importing every model `mark_imports` moved to static\n"
    "    lightmaps -- imported the shared textures 1,843 times for 476 models, the\n"
    "    same file again and again with several in flight, and 62 to 86 of 415\n"
    "    sidecars came out with Godot's DEFAULTS, which ones varying between runs;\n"
    "    nothing before it moved one, nothing after it put one back. Cold run\n"
    "    9248 shipped 65 of them so. Pinning `detect_3d/compress_to=0` changed\n"
    "    nothing (62, and the same 1,843), so the cause is the engine's import of\n"
    "    a scene's textures and not a setting this owns. This is the backstop:\n"
    "    the shared and the sign pins applied again over the files that ship,\n"
    "    then every shared sidecar read back, and a package that still carries\n"
    "    a wrong or a missing pin REFUSED -- a key a sidecar does not carry is\n"
    "    not one this writes (`_pin_shared_texture_imports`' rule), so it fails\n"
    "    here rather than shipping on the engine's default.\n"
    "\n"
    "    The cache, gone by the time this runs, was built with the pins the race\n"
    "    left; the light bake read those few textures without their mip chain or\n"
    "    with the alpha border filled, and nothing it bakes depends on either.\n"
    "    ``{\"shared_repinned\", \"sign_repinned\", \"shared_sidecars\"}``.\"\"\"\n"
    "    shared = _pin_shared_texture_imports(export_dir)\n"
    "    sign = _pin_sign_texture_imports(export_dir)\n"
    "    missing = _shared_texture_pins_missing(export_dir)\n"
    "    if missing:\n"
    "        raise ExportImportError(\n"
    "            \"%d shared-texture sidecar(s) do not carry their import pins after \"\n"
    "            \"they were applied again; first: %s (%s=%s)\"\n"
    "            % (len(missing), missing[0][0], missing[0][1], missing[0][2]))\n"
    "    total = sum(1 for s in export_dir.rglob(\"*.png.import\")\n"
    "                if s.parent.name == SHARED_TEX_DIR and \".godot\" not in s.parts)\n"
    "    return {\"shared_repinned\": shared, \"sign_repinned\": sign,\n"
    "            \"shared_sidecars\": total}\n"
    "\n"
    "\n"
    "#: The folder Lot copies a dealt business's sign maps into, beside its scene\n")
C_OLD = ("    if drop_cache(export_dir):\n"
         "        print(\"[export] import cache removed; the package ships sidecars, \"\n"
         "              \"not %s\" % \".godot\")\n"
         "\n"
         "    # 4.9 Resource-closure VERDICT -- see `_closure_verdict`. LAST, after\n")
C_NEW = ("    if drop_cache(export_dir):\n"
         "        print(\"[export] import cache removed; the package ships sidecars, \"\n"
         "              \"not %s\" % \".godot\")\n"
         "\n"
         "    # THE IMPORT PINS, READ BACK OFF THE FILES THAT SHIP (0.182.0): after the\n"
         "    # last import and the cache, before the verdict and the manifest describe\n"
         "    # the package. `_repin_after_imports` says why it has to be here.\n"
         "    pins = _repin_after_imports(export_dir)\n"
         "    print(\"[export] import pins: %d of %d shared-texture sidecar(s) carry their \"\n"
         "          \"pins; %d re-pinned after an import reset them, %d sign sidecar(s) \"\n"
         "          \"re-pinned\"\n"
         "          % (pins[\"shared_sidecars\"], pins[\"shared_sidecars\"],\n"
         "             pins[\"shared_repinned\"], pins[\"sign_repinned\"]))\n"
         "\n"
         "    # 4.9 Resource-closure VERDICT -- see `_closure_verdict`. LAST, after\n")


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
    for path, rel in [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.182.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.182.0: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("LF_ROOT"):
        sys.exit("refusing: --draft is for an LF_ROOT copy, never the repo")
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.182.0.md")
    assert entry.startswith("## [0.182.0] - "), entry[:40]
    if not DRAFT:
        left = entry
        if PENDING:
            for key in RESULTS:
                left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    test_text = _src("test_texture_pins_survive_the_bake.py.txt")
    assert not (LF / TEST).exists(), "already applied"
    ep, e_eol, export = _read(EXPORT)
    assert "def _repin_after_imports" not in export, "already applied"
    export = _once(export, H_OLD, H_NEW, "after _pin_shared_texture_imports")
    export = _once(export, C_OLD, C_NEW, "between the cache drop and the verdict")
    cl = LF / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:160]
    # every anchor matched: now write
    _write(ep, e_eol, export)
    (LF / TEST).write_bytes(test_text.encode("utf-8"))
    _write(cl, cl_eol, entry.rstrip("\n") + "\n\n" + cl_text)
    (LF / "VERSION").write_bytes(VERSION)
    print("Level Factory 0.181.0 -> 0.182.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
