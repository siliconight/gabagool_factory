"""Zoo 1.91.0: `window_drape` -- two velvet panels drawn shut across a den's window.

Roadmap 219, the walker's note 2, walking club_block_014 on 2026-10-09: "the windows in any 'den
of sin' building should have curtains or drapes or blinds So people outside can't see in, and you
keep the streetlight light out of the club", with a red drape as the comp. Zoo had no drape. This
is the species; Deli Counter (0.205.0) hangs one in every strip club's windows.

New files, each refused if it already exists:
- `zoo_keeper/core/window_drape_forms.py` -- the pure planner (`core/drape_forms.py` is
  `dust_sheet`'s, since 0.84.0: this patch refused to overwrite it, which is how the name
  was found taken);
- `zoo_keeper/recipes/window_drape.py` -- the recipe;
- `zoo_keeper/genome/species/window_drape.json` -- the genome;
- `tests/test_window_drape.py`.
Three anchored edits, each pinned by hash: `tests/test_genome.py`'s species set takes
`window_drape`; `tests/test_coincident_faces.py`'s census count takes its three builds (run in
Blender 5.1.1, recorded beside the count); `tests/test_theme_style_resolution.py`'s styled count
takes it, with its own `delco` row.
CHANGELOG and VERSION from `zoo_window_drape/CHANGELOG_1.91.0.md`.

    python patch_zoo_window_drape.py [--suite-pending]
    ZOO_ROOT=<copy> python patch_zoo_window_drape.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ZOO = pathlib.Path(os.environ.get("ZOO_ROOT") or HERE.parent / "zoo")
SRC = HERE / "zoo_window_drape"
DRAFT = "--draft" in sys.argv
SUITE_PENDING = "--suite-pending" in sys.argv

NEW = {
    "zoo_keeper/core/window_drape_forms.py": "window_drape_forms.py",
    "zoo_keeper/recipes/window_drape.py": "window_drape.py",
    "zoo_keeper/genome/species/window_drape.json": "window_drape.json",
    "tests/test_window_drape.py": "test_window_drape.py",
}
GENOME_TEST = "tests/test_genome.py"
#: the two guards that COUNT species, so a new one joins on purpose; the
#: suite's first run failed exactly these two
CENSUS_TEST = "tests/test_coincident_faces.py"
THEME_TEST = "tests/test_theme_style_resolution.py"
#: sha256[:16] of each file as read on 2026-10-09 for this patch
SHA = {GENOME_TEST: "d6626b0c75d84fdb", CENSUS_TEST: "3b1c34dda73908a3",
       THEME_TEST: "aea20923b543fda7"}
CENSUS_OLD = ("#: widths, both liveries -- found 0.\n"
              "CENSUS_BUILDS = 366\n")
CENSUS_NEW = ("#: widths, both liveries -- found 0.\n"
              "#: 1.91.0: `window_drape`, three builds more, same tool, Blender 5.1.1:\n"
              "#: \"3 builds, 0 with coincident pairs, 0 that did not build\" (404 / 944\n"
              "#: / 1,844 tris), first run.\n"
              "CENSUS_BUILDS = 369\n")
THEME_OLD = ("    # department's livery is in its image, not in a theme.\n"
             "    assert len(_genomes()) == 95 + len(_minted), len(_genomes())\n")
THEME_NEW = ("    # department's livery is in its image, not in a theme.\n"
             "    # 1.91.0: 96, + window_drape, with its own `delco` row.\n"
             "    assert len(_genomes()) == 96 + len(_minted), len(_genomes())\n")
SET_OLD = ("                # Crown Victoria lettered for the DELCO COUNTY POLICE\n"
           "                \"cruiser\"}\n")
SET_NEW = ("                # Crown Victoria lettered for the DELCO COUNTY POLICE\n"
           "                \"cruiser\",\n"
           "                # a den's window drawn shut (1.91.0, roadmap 219 note 2):\n"
           "                # two velvet panels under a pelmet, the room side of the glass\n"
           "                \"window_drape\"}\n")

CHANGELOG_HEAD = ("## [1.90.0] - the sign over a door in its owner's hand: Blue Highway for a shop, "
                  "painted smooth\n")


def _read(name):
    return (SRC / name).read_bytes().decode("utf-8").replace("\r\n", "\n")


def _stage():
    staged = {}
    for rel, src in NEW.items():
        p = ZOO / rel
        assert not p.exists(), (rel, "already exists")
        staged[p] = _read(src).encode("utf-8")
    for rel, old, new in ((GENOME_TEST, SET_OLD, SET_NEW), (CENSUS_TEST, CENSUS_OLD, CENSUS_NEW),
                          (THEME_TEST, THEME_OLD, THEME_NEW)):
        p = ZOO / rel
        d = p.read_bytes()
        got = hashlib.sha256(d).hexdigest()[:16]
        assert got == SHA[rel], (rel, "is not the file this patch read", got)
        assert b"\r" not in d, (rel, "has CR; this patch writes LF")
        t = d.decode("utf-8")
        assert t.count(old) == 1, (rel, t.count(old))
        staged[p] = t.replace(old, new).encode("utf-8")
    return staged


def main():
    if DRAFT and not os.environ.get("ZOO_ROOT"):
        sys.exit("refusing: --draft is for a ZOO_ROOT copy, never the repo")
    v = (ZOO / "VERSION").read_bytes()
    assert v == b"1.90.0", repr(v)
    staged = _stage()
    entry = _read("CHANGELOG_1.91.0.md")
    assert entry.startswith("## [1.91.0] - "), entry[:40]
    if not DRAFT:
        left = entry.replace("RESULT_SUITE", "") if SUITE_PENDING else entry
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    cl = ZOO / "CHANGELOG.md"
    data = cl.read_bytes()
    assert b"\r" not in data, "CHANGELOG.md is not LF"
    text = data.decode("utf-8")
    assert text.startswith(CHANGELOG_HEAD) and text.count(CHANGELOG_HEAD) == 1, text[:90]
    assert "## [1.91.0]" not in text, "already applied"
    # Every anchor and hash matched: now write.
    for p, raw in staged.items():
        p.write_bytes(raw)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + text).encode("utf-8"))
    (ZOO / "VERSION").write_bytes(b"1.91.0")
    print("Zoo 1.90.0 -> 1.91.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
