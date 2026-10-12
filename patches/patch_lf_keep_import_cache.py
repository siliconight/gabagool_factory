"""Level Factory 0.188.0: the export keeps its import cache beside the package, for the walk copy
(factory roadmap 239).

Anchored edits, each asserted once, nothing written until all of them matched:
  packages/exporting/occluders.py   `KEPT_CACHE_SUFFIX`, `kept_cache_dir`, `keep_cache` (move the
                                    cache out of the package to sit beside it), after `drop_cache`
  packages/exporting/export.py      an export removes the last package's kept cache before it
                                    builds; the cache is kept, not dropped, where it was dropped
  tests/unit/test_census_reads_the_bake_cache.py   pins the order at the keep, where it pinned it
  tests/unit/test_texture_pins_survive_the_bake.py at the drop (both read the drop's line)
  tests/unit/test_kept_import_cache.py   NEW, from `lf_keep_import_cache/`
CHANGELOG and VERSION from `lf_keep_import_cache/CHANGELOG_0.188.0.md`; `--results-pending`
leaves the RESULT_ keys to `--fill`. The walk copy's half is the factory's own
`tools/walk_export.py`, which moves the kept cache in.

Measured before it was written: docs/findings/grader_speed/walk_cache_probe.py.

    python patches/patch_lf_keep_import_cache.py --results-pending && cd level_factory && python -m pytest -q
    python patches/patch_lf_keep_import_cache.py --fill
    LF_ROOT=<copy> python patches/patch_lf_keep_import_cache.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_keep_import_cache"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_AB": "result_ab.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.187.0", b"0.188.0"
CHANGELOG_HEAD = ("## [0.187.0] - The light bake's lightmap requests ride the export's second "
                  "import pass\n")
OCC = "packages/exporting/occluders.py"
EXPORT = "packages/exporting/export.py"
CENSUS_TEST = "tests/unit/test_census_reads_the_bake_cache.py"
PINS_TEST = "tests/unit/test_texture_pins_survive_the_bake.py"
TEST = "tests/unit/test_kept_import_cache.py"
SHA = {OCC: "541197c2b9fa8286", EXPORT: "b6ce974fea8a65bf", CENSUS_TEST: "5b471d79bd2e5c54",
       PINS_TEST: "be5f2066953fafa7"}

O_DROP_END_OLD = ("    cache = Path(export_dir) / CACHE_DIR\n"
                  "    if not cache.is_dir():\n"
                  "        return False\n"
                  "    shutil.rmtree(cache, ignore_errors=True)\n"
                  "    return True\n")
O_DROP_END_NEW = (
    "    cache = Path(export_dir) / CACHE_DIR\n"
    "    if not cache.is_dir():\n"
    "        return False\n"
    "    shutil.rmtree(cache, ignore_errors=True)\n"
    "    return True\n"
    "\n"
    "\n"
    "#: Where the export keeps its import cache once the package is done with it\n"
    "#: (0.188.0): beside the package, never in it, for a walk copy to start from\n"
    "#: (the factory's `tools/walk_export.py`, which moves it in).\n"
    "KEPT_CACHE_SUFFIX = \".import_cache\"\n"
    "\n"
    "\n"
    "def kept_cache_dir(export_dir) -> Path:\n"
    "    \"\"\"Where `keep_cache` puts a package's import cache: beside it, named\n"
    "    for it.\"\"\"\n"
    "    export_dir = Path(export_dir)\n"
    "    return export_dir.parent / (export_dir.name + KEPT_CACHE_SUFFIX)\n"
    "\n"
    "\n"
    "def keep_cache(export_dir) -> Path | None:\n"
    "    \"\"\"Move the import cache out of the package to sit beside it. Where it\n"
    "    went, or None if there was no cache.\n"
    "\n"
    "    The package leaves this as `drop_cache` leaves it: cache-free. The cache\n"
    "    is the export's own import of the files it ships, so a walk copy of the\n"
    "    package can start from it instead of importing everything again --\n"
    "    measured on cold run 9253's package re-exported (the factory's\n"
    "    `docs/findings/grader_speed/walk_cache_probe.py`): a walk copy importing\n"
    "    from scratch 85.6 and 86.2 s, one started from this cache 9.6 s; every\n"
    "    model it imports loading the same (501 of 501 by `import_digest.gd`,\n"
    "    whose digest a one-sidecar change moves), and the level the same (20,954\n"
    "    nodes, 3,380 meshes, none empty, 242 lights, 3,320 lightmap users).\n"
    "\n"
    "    A sidecar changed after the cache was made -- the pins read back after\n"
    "    it -- is imported again by the walk copy's own pass: that control, one\n"
    "    sidecar changed in a copy started from the cache, moved that model's\n"
    "    digest and no other's. A kept cache from an earlier export of the same\n"
    "    package is replaced, never merged.\n"
    "    \"\"\"\n"
    "    cache = Path(export_dir) / CACHE_DIR\n"
    "    if not cache.is_dir():\n"
    "        return None\n"
    "    kept = kept_cache_dir(export_dir)\n"
    "    if kept.exists():\n"
    "        shutil.rmtree(kept, ignore_errors=True)\n"
    "    shutil.move(str(cache), str(kept))\n"
    "    return kept\n")

E_START_OLD = ("    if export_dir.exists():\n"
               "        shutil.rmtree(export_dir)\n"
               "    export_dir.mkdir(parents=True, exist_ok=True)\n")
E_START_NEW = ("    if export_dir.exists():\n"
               "        shutil.rmtree(export_dir)\n"
               "    # A cache kept beside the last package was that package's import, not\n"
               "    # this one's (0.188.0, `occluders.keep_cache`): it goes with it, so an\n"
               "    # export that stops early leaves no walk copy a stranger's cache.\n"
               "    from packages.exporting.occluders import kept_cache_dir\n"
               "    shutil.rmtree(kept_cache_dir(export_dir), ignore_errors=True)\n"
               "    export_dir.mkdir(parents=True, exist_ok=True)\n")
E_IMPORT_OLD = ("    from packages.exporting.occluders import (OccluderDisagreement,\n"
                "                                              OccluderError, audit,\n"
                "                                              drop_cache, emit)\n")
E_IMPORT_NEW = ("    from packages.exporting.occluders import (OccluderDisagreement,\n"
                "                                              OccluderError, audit,\n"
                "                                              drop_cache, emit,\n"
                "                                              keep_cache)\n")
E_DROP_OLD = ("    if drop_cache(export_dir):\n"
              "        print(\"[export] import cache removed; the package ships sidecars, \"\n"
              "              \"not %s\" % \".godot\")\n")
E_DROP_NEW = ("    #\n"
              "    # KEPT BESIDE THE PACKAGE, NOT DELETED (0.188.0): the walk copy starts\n"
              "    # from it instead of importing every file again -- 9.6 s against 86 s,\n"
              "    # `occluders.keep_cache` says how that was measured. The package leaves\n"
              "    # this line as cache-free as it did.\n"
              "    kept = keep_cache(export_dir)\n"
              "    if kept is not None:\n"
              "        print(\"[export] import cache moved beside the package (%s); the \"\n"
              "              \"package ships sidecars, not %s\" % (kept.name, \".godot\"))\n")
C_OLD = "    drops = _calls(body, \"if drop_cache(export_dir):\")\n"
C_NEW = ("    # 0.188.0 keeps the cache beside the package instead of dropping it, for the\n"
         "    # walk copy (`occluders.keep_cache`): the line the package ships through\n"
         "    # moved; the order this pins did not.\n"
         "    drops = _calls(body, \"kept = keep_cache(export_dir)\")\n")
P_OLD = ("    for earlier in (\"_bake_lights(\", \"greybox_skin.measure(\", "
         "\"if drop_cache(export_dir):\"):\n")
P_NEW = ("    # 0.188.0 keeps the cache beside the package where it dropped it.\n"
         "    for earlier in (\"_bake_lights(\", \"greybox_skin.measure(\", "
         "\"kept = keep_cache(export_dir)\"):\n")


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
    for path, rel in [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.188.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.188.0: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("LF_ROOT"):
        sys.exit("refusing: --draft is for an LF_ROOT copy, never the repo")
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.188.0.md")
    assert entry.startswith("## [0.188.0] - "), entry[:40]
    if not DRAFT:
        left = entry
        if PENDING:
            for key in RESULTS:
                left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    test_text = _src("test_kept_import_cache.py.txt")
    assert not (LF / TEST).exists(), "already applied"
    op, o_eol, occ = _read(OCC)
    assert "def keep_cache" not in occ, "already applied"
    occ = _once(occ, O_DROP_END_OLD, O_DROP_END_NEW, "the end of drop_cache")
    ep, e_eol, exp = _read(EXPORT)
    exp = _once(exp, E_START_OLD, E_START_NEW, "the export's fresh directory")
    exp = _once(exp, E_IMPORT_OLD, E_IMPORT_NEW, "export_mission's occluder imports")
    exp = _once(exp, E_DROP_OLD, E_DROP_NEW, "the cache's last drop")
    cp, c_eol, ct = _read(CENSUS_TEST)
    ct = _once(ct, C_OLD, C_NEW, "the census test's anchor")
    pp, p_eol, pt = _read(PINS_TEST)
    pt = _once(pt, P_OLD, P_NEW, "the pins test's anchor")
    cl = LF / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:160]
    # every anchor matched: now write
    _write(op, o_eol, occ)
    _write(ep, e_eol, exp)
    _write(cp, c_eol, ct)
    _write(pp, p_eol, pt)
    (LF / TEST).write_bytes(test_text.encode("utf-8"))
    _write(cl, cl_eol, entry.rstrip("\n") + "\n\n" + cl_text)
    (LF / "VERSION").write_bytes(VERSION)
    print("Level Factory 0.187.0 -> 0.188.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
