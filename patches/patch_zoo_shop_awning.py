"""Zoo 1.108.0: a corner shop's canvas awning, `shop_awning` (factory roadmap 241, the corner shop).

The comps: "Corners carry the life. The corner building has the shop at grade (lit, awning), homes above"; the
Empties comps list the awning as Zoo's to build. Deli Counter 0.218.0's corner blocks have the shop and not the
awning.

Anchored edits, each asserted exactly once and every file's sha16 pinned, nothing written until all of them matched:
  zoo_keeper/core/shop_awning_forms.py           NEW (`zoo_shop_awning/shop_awning_forms.py.txt`)
  zoo_keeper/recipes/shop_awning.py              NEW (`zoo_shop_awning/shop_awning.py.txt`)
  zoo_keeper/genome/species/shop_awning.json     NEW (`zoo_shop_awning/shop_awning.json.txt`)
  tests/test_shop_awning.py                      NEW (`zoo_shop_awning/test_shop_awning.py.txt`)
  zoo_keeper/genome/minted.json                  the species, in its place (the file's own 1-space indent kept)
  tests/test_coincident_faces.py                 CENSUS_BUILDS 393 -> 396 and the run that earned it
CHANGELOG and VERSION from `zoo_shop_awning/CHANGELOG_1.108.0.md`; `--results-pending` leaves the RESULT_ keys to
`--fill`. The census's and the kit build's own logs are `zoo_shop_awning/census.log` and `kit.log`, run on a copy
of Zoo 1.107.0 with these files in it.

Read before it was written, in this session: `core/prims.py` (box, mesh, fit_exact, bounds, tri_count,
coincident_pairs), `bpylayer/prim_mesh.py`, `core/stoop_railing_forms.py`, its recipe, genome and test (the
pattern this follows), `core/kit.py`'s and Deli Counter's `VOLUME_ROLES` (a prop slot's `form` names its module),
`skins.KNOWN_KINDS` (`canvas`) and Pixelcoat's `canvas_neutral` (achromatic, so the colour is the tint),
`genome/minted.json` and `tools/new_species.py` (what reads it), `tests/test_coincident_faces.py` (`CENSUS_BUILDS`
is three corners a genome) and `tests/test_material_options_closed.py` (the metal split; a canvas species is not
on it). Every file LF.

    python patches/patch_zoo_shop_awning.py --results-pending
    (python -m pytest -q in zoo; the Blender check: the command in tests/test_shop_panes.py, on this file)
    python patches/patch_zoo_shop_awning.py --fill
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ZOO = pathlib.Path(os.environ.get("ZOO_ROOT") or HERE.parent / "zoo")
SRC = HERE / "zoo_shop_awning"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_SUITE": "result_suite.txt", "RESULT_BLENDER": "result_blender.txt"}
VERSION_WAS, VERSION = b"1.107.0", b"1.108.0"
CHANGELOG_HEAD = "## [1.107.0] - a corner shop's window, painted: its own atlas of storefront states\n"
SHA = {"zoo_keeper/genome/minted.json": "43769018ae27ec2c", "tests/test_coincident_faces.py": "67ff19f6d1e3016d"}
NEW = {"zoo_keeper/core/shop_awning_forms.py": "shop_awning_forms.py.txt",
       "zoo_keeper/recipes/shop_awning.py": "shop_awning.py.txt",
       "zoo_keeper/genome/species/shop_awning.json": "shop_awning.json.txt",
       "tests/test_shop_awning.py": "test_shop_awning.py.txt"}

EDITS = {
    "zoo_keeper/genome/minted.json": [
        (" \"red_maple\",\n \"sign_post\",\n",
         " \"red_maple\",\n \"shop_awning\",\n \"sign_post\",\n"),
    ],
    "tests/test_coincident_faces.py": [
        ("#: on both forms over 60 sizes before Blender does. 240 is the genome's budget.\n"
         "CENSUS_BUILDS = 393\n",
         "#: on both forms over 60 sizes before Blender does. 240 is the genome's budget.\n"
         "#: 1.108.0: `shop_awning`, three builds more, same tool, Blender 5.1.1 --\n"
         "#: `blender -b --python tools/coplanar_census.py -- --species shop_awning\n"
         "#: bollard`, the bollard the control (its known 2 / 2 / 1): \"6 builds, 3 with\n"
         "#: coincident pairs, 0 that did not build\", the awning's three corners 40 / 40 /\n"
         "#: 40 tris and 0 pairs, first run. The slope stops inside the valance and the\n"
         "#: cheeks, the cheeks stand off the wall plane and over the valance\n"
         "#: (`shop_awning_forms`), so `prims.coincident_pairs` reads 0 over 54 sizes\n"
         "#: before Blender does. 48 is the genome's budget.\n"
         "CENSUS_BUILDS = 396\n"),
    ],
}


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def fill():
    assert (ZOO / "VERSION").read_bytes().strip() == VERSION, (ZOO / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value, (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(ZOO / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_1.108.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Zoo 1.108.0: results filled")


def main():
    if FILL:
        return fill()
    assert (ZOO / "VERSION").read_bytes().strip() == VERSION_WAS, (ZOO / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_1.108.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [1.108.0] - "), entry[:40]
    left = entry
    for key in RESULTS if PENDING else ():
        left = left.replace(key, "")
    assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    for rel in NEW:
        assert not (ZOO / rel).exists(), ("already applied", rel)
    writes = {}
    for rel, edits in EDITS.items():
        raw = (ZOO / rel).read_bytes()
        got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
        assert got == SHA[rel], (rel, "is not the file this patch read", got)
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for old, new in edits:
            assert text.count(old) == 1, (rel, "anchor", text.count(old), old[:60])
            text = text.replace(old, new)
        if rel.endswith(".py"):
            compile(text, rel, "exec")
        writes[rel] = (text, eol)
    news = {r: (SRC / s).read_bytes().replace(b"\r\n", b"\n") for r, s in NEW.items()}
    for r, data in news.items():
        if r.endswith(".py"):
            compile(data.decode("utf-8"), r, "exec")
        else:
            import json
            json.loads(data.decode("utf-8"))
    cl = ZOO / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD), cl_text[:120]
    # every anchor matched: now write
    for rel, (text, eol) in writes.items():
        (ZOO / rel).write_bytes(text.encode("utf-8").replace(b"\n", eol))
    for r, data in news.items():
        (ZOO / r).write_bytes(data)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).encode("utf-8").replace(b"\n", cl_eol))
    (ZOO / "VERSION").write_bytes(VERSION)
    print("Zoo 1.107.0 -> 1.108.0")


if __name__ == "__main__":
    main()
