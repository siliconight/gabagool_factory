"""Zoo 1.105.0: a stoop's iron railing, `stoop_railing` (factory roadmap 240; the walker's calls of 2026-10-13,
"3 risers, concrete, railings both sides -- build the railings").

Anchored edits, each asserted exactly once and every file's sha16 pinned, nothing written until all of
them matched:
  zoo_keeper/core/stoop_railing_forms.py           NEW (`zoo_stoop_railing/stoop_railing_forms.py.txt`)
  zoo_keeper/recipes/stoop_railing.py              NEW (`zoo_stoop_railing/stoop_railing.py.txt`)
  zoo_keeper/genome/species/stoop_railing.json     NEW (`zoo_stoop_railing/stoop_railing.json.txt`)
  tests/test_stoop_railing.py                      NEW (`zoo_stoop_railing/test_stoop_railing.py.txt`)
  zoo_keeper/genome/minted.json                    the species, in its place (the file's own 1-space
                                                   indent kept, so one line moves)
  tests/test_coincident_faces.py                   CENSUS_BUILDS 390 -> 393 and the run that earned it
  tests/test_material_options_closed.py            the railing on PAINTED, with its reason
CHANGELOG and VERSION from `zoo_stoop_railing/CHANGELOG_1.105.0.md`; `--results-pending` leaves the
RESULT_ keys to `--fill`. The census's and the kit build's own logs are `zoo_stoop_railing/census.log`
and `kit.log`, run on a copy of Zoo 1.104.0 with these files in it.

Read before it was written, in this session: `core/prims.py` (box, mesh, fit_exact, bounds, tri_count,
coincident_pairs), `bpylayer/prim_mesh.py`, `core/chain_link_fence_forms.py` and its recipe and test,
`recipes/utility_pole.py` and its genome (`params.form`), `core/kit.py`'s `honour_dressing` (a form is
honoured only when the genome lists it) and the plan's slot material (`skins.KNOWN_KINDS`),
`tools/new_species.py`, `tools/coplanar_census.py`, `tools/zoo_cli.py --build-kit`,
`tests/test_coincident_faces.py` (`CENSUS_BUILDS` is three corners a genome) and
`tests/test_material_options_closed.py` (every species on a split metal kind is listed), and
`stair_rail` (unplaced, structural, left as it is). Every file LF.

    python patches/patch_zoo_stoop_railing.py --results-pending
    (python -m pytest -q in zoo)
    python patches/patch_zoo_stoop_railing.py --fill
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ZOO = pathlib.Path(os.environ.get("ZOO_ROOT") or HERE.parent / "zoo")
SRC = HERE / "zoo_stoop_railing"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"1.104.0", b"1.105.0"
CHANGELOG_HEAD = "## [1.104.0] - a wooden utility pole: the cobra-head"
SHA = {"zoo_keeper/genome/minted.json": "56401b664ef636fd",
       "tests/test_coincident_faces.py": "d135169b76c80f44",
       "tests/test_material_options_closed.py": "e3c55af466f29092"}
NEW = {"zoo_keeper/core/stoop_railing_forms.py": "stoop_railing_forms.py.txt",
       "zoo_keeper/recipes/stoop_railing.py": "stoop_railing.py.txt",
       "zoo_keeper/genome/species/stoop_railing.json": "stoop_railing.json.txt",
       "tests/test_stoop_railing.py": "test_stoop_railing.py.txt"}

EDITS = {
    "zoo_keeper/genome/minted.json": [
        (' "sign_post",\n "stop_sign",\n',
         ' "sign_post",\n "stoop_railing",\n "stop_sign",\n'),
    ],
    "tests/test_coincident_faces.py": [
        ("#: `prims.coincident_pairs` reads 0 on both forms before Blender does.\n"
         "CENSUS_BUILDS = 390\n",
         "#: `prims.coincident_pairs` reads 0 on both forms before Blender does.\n"
         "#: 1.105.0: `stoop_railing`, three builds more, same tool, Blender 5.1.1 --\n"
         "#: `blender -b --python tools/coplanar_census.py -- --species stoop_railing\n"
         "#: bollard`, the bollard the control that the census can see a pair (its known\n"
         "#: 2 / 2 / 1, as its RESIDUE row sums them): \"6 builds, 3 with coincident pairs, 0\n"
         "#: that did not build\", the railing's three corners 72 / 132 / 240 tris and 0\n"
         "#: pairs, first run. A rail's end stops `SINK` inside its post, a picket's ends\n"
         "#: lie on the rails' centre lines and each member nests `NEST` a side inside the\n"
         "#: one it runs into (`stoop_railing_forms`), so `prims.coincident_pairs` reads 0\n"
         "#: on both forms over 60 sizes before Blender does. 240 is the genome's budget.\n"
         "CENSUS_BUILDS = 393\n"),
    ],
    "tests/test_material_options_closed.py": [
        ('           "dress_cover")\n'
         'BARE = ("gold_bar", "flat_top_grill",\n',
         '           "dress_cover",\n'
         "           # a stoop's railing is wrought iron painted black (1.105.0)\n"
         '           "stoop_railing")\n'
         'BARE = ("gold_bar", "flat_top_grill",\n'),
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
        assert value and "RESULT_" not in value and not value.endswith("."), (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(ZOO / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_1.105.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Zoo 1.105.0: results filled")


def main():
    if FILL:
        return fill()
    assert (ZOO / "VERSION").read_bytes().strip() == VERSION_WAS, (ZOO / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_1.105.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [1.105.0] - "), entry[:40]
    left = entry
    for key in RESULTS if PENDING else ():
        left = left.replace(key, "")
    assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    for rel in NEW:
        assert not (ZOO / rel).exists(), ("already applied", rel)
    writes = {}
    for rel, pairs in EDITS.items():
        p = ZOO / rel
        raw = p.read_bytes()
        got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
        assert got == SHA[rel], (rel, "is not the file this patch read", got)
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for old, new in pairs:
            assert text.count(old) == 1, (rel, "anchor", text.count(old), old[:80])
            text = text.replace(old, new)
        writes[p] = text.encode("utf-8").replace(b"\n", eol)
    news = {rel: (SRC / src).read_bytes().replace(b"\r\n", b"\n") for rel, src in NEW.items()}
    cl = ZOO / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD), cl_text[:120]
    # every anchor matched: now write
    for p, data in writes.items():
        p.write_bytes(data)
    for rel, data in news.items():
        (ZOO / rel).write_bytes(data)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).encode("utf-8").replace(b"\n", cl_eol))
    (ZOO / "VERSION").write_bytes(VERSION)
    print("Zoo 1.104.0 -> 1.105.0")


if __name__ == "__main__":
    main()
