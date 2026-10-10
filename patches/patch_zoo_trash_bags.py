"""Zoo 1.93.0: trash_bags, a heap of filled garbage bags (roadmap 219 note 11). See
`zoo_trash_bags/CHANGELOG_1.93.0.md`.

The walker, 2026-10-09: "need filled black garbage bags stacked near the garbage bins". A new
species, whole files from `zoo_trash_bags/`, and three anchored edits to the counts a new
species moves, each edited file pinned by the hash its content had when this patch was written:
  new     zoo_keeper/core/trash_bag_forms.py, zoo_keeper/recipes/trash_bags.py,
          zoo_keeper/genome/species/trash_bags.json, tests/test_trash_bags.py
  edited  tests/test_genome.py: `trash_bags` joins PROP_SPECIES
          tests/test_coincident_faces.py: CENSUS_BUILDS 369 -> 372, with the census's own line
          tests/test_theme_style_resolution.py: 96 genomes -> 97
CHANGELOG and VERSION from `CHANGELOG_1.93.0.md`. Nothing is written until every pin and anchor
matched.

    python patch_zoo_trash_bags.py [--suite-pending]
    ZOO_ROOT=<copy> python patch_zoo_trash_bags.py --draft

`--draft` lets the changelog's RESULT_ placeholders through, against a ZOO_ROOT copy only.
`--suite-pending` lets exactly RESULT_SUITE through into the repo, filled in by hand after the
suite runs and before the commit.
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ZOO = pathlib.Path(os.environ.get("ZOO_ROOT") or HERE.parent / "zoo")
SRC = HERE / "zoo_trash_bags"
DRAFT = "--draft" in sys.argv
SUITE_PENDING = "--suite-pending" in sys.argv

NEW = {"zoo_keeper/core/trash_bag_forms.py": "trash_bag_forms.py",
       "zoo_keeper/recipes/trash_bags.py": "recipe_trash_bags.py",
       "zoo_keeper/genome/species/trash_bags.json": "trash_bags.json",
       "tests/test_trash_bags.py": "test_trash_bags.py"}

#: repo path -> (sha256[:16] of its content with line endings made LF, as read 2026-10-10,
#: the block it replaces, the block that replaces it). Content, not bytes: git's autocrlf can
#: rewrite a file's endings on a checkout with nothing else changed.
EDITS = {
    "tests/test_genome.py": (
        "3002b341a0145d1e",
        "                # a den's window drawn shut (1.91.0, roadmap 219 note 2):\n"
        "                # two velvet panels under a pelmet, the room side of the glass\n"
        "                \"window_drape\"}\n",
        "                # a den's window drawn shut (1.91.0, roadmap 219 note 2):\n"
        "                # two velvet panels under a pelmet, the room side of the glass\n"
        "                \"window_drape\",\n"
        "                # a heap of filled garbage bags beside a dumpster (1.93.0,\n"
        "                # roadmap 219 note 11)\n"
        "                \"trash_bags\"}\n"),
    "tests/test_coincident_faces.py": (
        "c2d1621d2e8b2a66",
        "#: 1.91.0: `window_drape`, three builds more, same tool, Blender 5.1.1:\n"
        "#: \"3 builds, 0 with coincident pairs, 0 that did not build\" (404 / 944\n"
        "#: / 1,844 tris), first run.\n"
        "CENSUS_BUILDS = 369\n",
        "#: 1.91.0: `window_drape`, three builds more, same tool, Blender 5.1.1:\n"
        "#: \"3 builds, 0 with coincident pairs, 0 that did not build\" (404 / 944\n"
        "#: / 1,844 tris), first run.\n"
        "#: 1.93.0: `trash_bags`, three builds more, same tool, Blender 5.1.1:\n"
        "#: \"3 builds, 0 with coincident pairs, 0 that did not build\" (1,536 /\n"
        "#: 1,536 / 2,304 tris). The probe's first heap found one pair: a bag's\n"
        "#: bottom clamped onto one plane folded two triangles back to back, and\n"
        "#: `trash_bag_forms.shape` squeezes it now rather than clamping it.\n"
        "CENSUS_BUILDS = 372\n"),
    "tests/test_theme_style_resolution.py": (
        "8b73ee1f2c3b0977",
        "    # 1.91.0: 96, + window_drape, with its own `delco` row.\n"
        "    assert len(_genomes()) == 96 + len(_minted), len(_genomes())\n",
        "    # 1.91.0: 96, + window_drape, with its own `delco` row.\n"
        "    # 1.93.0: 97, + trash_bags, with its own `delco` row.\n"
        "    assert len(_genomes()) == 97 + len(_minted), len(_genomes())\n"),
}
CHANGELOG_HEAD = "## [1.92.0] - the box truck and the litter bin, drawn\n"


def _src(name):
    return (SRC / name).read_bytes().replace(b"\r\n", b"\n")


def _eol(raw, rel):
    """The file's own line ending. A file with both refuses: there is no one ending to restore."""
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return "\r\n" if crlf else "\n"


def main():
    if DRAFT and not os.environ.get("ZOO_ROOT"):
        sys.exit("refusing: --draft is for a ZOO_ROOT copy, never the repo")
    assert (ZOO / "VERSION").read_bytes().strip() == b"1.92.0", (ZOO / "VERSION").read_bytes()
    entry = _src("CHANGELOG_1.93.0.md").decode("utf-8")
    assert entry.startswith("## [1.93.0] - "), entry[:40]
    if not DRAFT:
        left = entry.replace("RESULT_SUITE", "") if SUITE_PENDING else entry
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    writes = {}
    for rel, name in NEW.items():
        assert not (ZOO / rel).exists(), (rel, "already exists")
        writes[ZOO / rel] = _src(name)
    for rel, (sha, old, new) in EDITS.items():
        p = ZOO / rel
        raw = p.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        got = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
        assert got == sha, (rel, "is not the file this patch read", got)
        assert text.count(old) == 1, (rel, "anchor count", text.count(old))
        assert "trash_bags" not in text, (rel, "already names trash_bags")
        writes[p] = text.replace(old, new).replace("\n", eol).encode("utf-8")
    cl = ZOO / "CHANGELOG.md"
    raw = cl.read_bytes()
    eol = _eol(raw, "CHANGELOG.md")
    text = raw.decode("utf-8").replace("\r\n", "\n")
    assert text.startswith(CHANGELOG_HEAD) and text.count(CHANGELOG_HEAD) == 1, text[:90]
    # every pin and anchor matched: now write
    for p, data in writes.items():
        p.write_bytes(data)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + text).replace("\n", eol).encode("utf-8"))
    (ZOO / "VERSION").write_bytes(b"1.93.0")
    print("Zoo 1.92.0 -> 1.93.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
