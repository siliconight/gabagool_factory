"""Level Factory 0.181.0: the greybox census reads the bake's import cache instead of importing the
package a fifth time (factory roadmap 239, the export now half a cold run's drive).

Anchored edits, each asserted once, nothing written until all of them matched:
  packages/exporting/export.py        the cache is dropped AFTER the greybox census and before the
                                      closure verdict, not straight after the bake
  packages/exporting/greybox_skin.py  `measure`'s comment says what it now finds
  tests/unit/test_census_reads_the_bake_cache.py   NEW, from `lf_census_cache/`
CHANGELOG and VERSION from `lf_census_cache/CHANGELOG_0.181.0.md`; `--results-pending` leaves the
RESULT_ keys to `--fill`.

    python patches/patch_lf_census_cache.py --results-pending && cd level_factory && python -m pytest -q
    python patches/patch_lf_census_cache.py --fill
    LF_ROOT=<copy> python patches/patch_lf_census_cache.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_census_cache"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_AB": "result_ab.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.180.1", b"0.181.0"
CHANGELOG_HEAD = "## [0.180.1] - Re-grounded to Lot 0.117.0: the walk test's clock no longer waits\n"
EXPORT = "packages/exporting/export.py"
GREYBOX = "packages/exporting/greybox_skin.py"
TEST = "tests/unit/test_census_reads_the_bake_cache.py"
SHA = {EXPORT: "fdd3625bc2a1e08e", GREYBOX: "78c43802752ccd77"}

E_DROP_OLD = (
    "    # Settle the flag against what shipped, then drop the cache the bake\n"
    "    # needed -- before `build_resource_manifest` walks the tree, so the\n"
    "    # manifest cannot list a cache entry and the package stays cache-free.\n"
    "    proj = export_dir / \"project.godot\"\n"
    "    proj.write_text(\n"
    "        set_occlusion_culling(proj.read_text(encoding=\"utf-8\"),\n"
    "                              occluder_count), encoding=\"utf-8\")\n"
    "    if drop_cache(export_dir):\n"
    "        print(\"[export] import cache removed; the package ships sidecars, \"\n"
    "              \"not %s\" % \".godot\")\n")
E_DROP_NEW = (
    "    # Settle the flag against what shipped. The cache the bake needed stays\n"
    "    # until the greybox census has read it, below (0.181.0).\n"
    "    proj = export_dir / \"project.godot\"\n"
    "    proj.write_text(\n"
    "        set_occlusion_culling(proj.read_text(encoding=\"utf-8\"),\n"
    "                              occluder_count), encoding=\"utf-8\")\n")
E_VERDICT_OLD = "    # 4.9 Resource-closure VERDICT -- see `_closure_verdict`. LAST, after\n"
E_VERDICT_NEW = (
    "    # THE CACHE GOES HERE, AFTER THE CENSUS (0.181.0, factory roadmap 239), and\n"
    "    # before the closure verdict and `build_resource_manifest` walk the tree,\n"
    "    # so neither can meet a cache entry and the package stays cache-free. It\n"
    "    # was dropped straight after the bake, and the census then imported the\n"
    "    # whole package again to read it: 100.4 of a 430.7 s export, profiled on\n"
    "    # cold run 9248's -- the fifth import of the same files in one export.\n"
    "    # Nothing between the bake and this line reads the cache's file types\n"
    "    # (`.scn`, `.mesh`, `.md5`, `.cfg`): the occlusion audit and the handoff\n"
    "    # walk read `*.tscn`, the GLB scan `*.glb`, the rest JSON.\n"
    "    if drop_cache(export_dir):\n"
    "        print(\"[export] import cache removed; the package ships sidecars, \"\n"
    "              \"not %s\" % \".godot\")\n"
    "\n"
    "    # 4.9 Resource-closure VERDICT -- see `_closure_verdict`. LAST, after\n")
G_OLD = (
    "    # LEAVE THE PACKAGE AS THIS FOUND IT, and the cost of not doing so is\n"
    "    # why this comment is long. Taking the census needs an import cache; the\n"
    "    # exporter has ALREADY removed one by this point (\"import cache removed;\n"
    "    # the package ships sidecars, not .godot\") and the closure verdict three\n"
    "    # steps below scans every file in the package.")
G_NEW = (
    "    # LEAVE THE PACKAGE AS THIS FOUND IT, and the cost of not doing so is\n"
    "    # why this comment is long. Taking the census needs an import cache. The\n"
    "    # exporter keeps the bake's until this has run (0.181.0), so in an export\n"
    "    # this finds one and imports nothing; called on a package without one it\n"
    "    # imports, and then it must remove what it made, because the closure\n"
    "    # verdict below it scans every file in the package.")


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
    for path, rel in [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.181.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.181.0: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("LF_ROOT"):
        sys.exit("refusing: --draft is for an LF_ROOT copy, never the repo")
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.181.0.md")
    assert entry.startswith("## [0.181.0] - "), entry[:40]
    if not DRAFT:
        left = entry
        if PENDING:
            for key in RESULTS:
                left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    test_text = _src("test_census_reads_the_bake_cache.py.txt")
    assert not (LF / TEST).exists(), "already applied"

    ep, e_eol, export = _read(EXPORT)
    assert "THE CACHE GOES HERE, AFTER THE CENSUS" not in export, "already applied"
    export = _once(export, E_DROP_OLD, E_DROP_NEW, "the drop after the bake")
    export = _once(export, E_VERDICT_OLD, E_VERDICT_NEW, "the closure verdict's heading")
    gp, g_eol, greybox = _read(GREYBOX)
    greybox = _once(greybox, G_OLD, G_NEW, "measure's comment")

    cl = LF / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:160]
    # every anchor matched: now write
    _write(ep, e_eol, export)
    _write(gp, g_eol, greybox)
    (LF / TEST).write_bytes(test_text.encode("utf-8"))
    _write(cl, cl_eol, entry.rstrip("\n") + "\n\n" + cl_text)
    (LF / "VERSION").write_bytes(VERSION)
    print("Level Factory 0.180.1 -> 0.181.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
