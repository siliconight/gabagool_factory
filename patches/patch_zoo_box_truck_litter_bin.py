"""Zoo 1.92.0: the box truck and the litter bin, drawn (roadmap 219 note 5). See
`zoo_box_truck_litter_bin/CHANGELOG_1.92.0.md`.

The last two placeholder silhouettes in the library. Whole files from `zoo_box_truck_litter_bin/`,
each replaced file pinned by the hash it had when this patch was written, and one anchored edit:
  new       zoo_keeper/core/box_truck_forms.py, zoo_keeper/core/litter_bin_forms.py
  replaced  zoo_keeper/recipes/box_truck.py, zoo_keeper/recipes/litter_bin.py,
            zoo_keeper/genome/species/box_truck.json, zoo_keeper/genome/species/litter_bin.json,
            tests/test_box_truck.py, tests/test_litter_bin.py
  edited    zoo_keeper/core/card_art.py: `paint` sends the `litter_` tiles to litter_bin_forms
CHANGELOG and VERSION from `CHANGELOG_1.92.0.md`. Nothing is written until every pin and anchor
matched.

    python patch_zoo_box_truck_litter_bin.py [--suite-pending]
    ZOO_ROOT=<copy> python patch_zoo_box_truck_litter_bin.py --draft

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
SRC = HERE / "zoo_box_truck_litter_bin"
DRAFT = "--draft" in sys.argv
SUITE_PENDING = "--suite-pending" in sys.argv

NEW = {"zoo_keeper/core/box_truck_forms.py": "box_truck_forms.py",
       "zoo_keeper/core/litter_bin_forms.py": "litter_bin_forms.py"}
#: repo path -> (source file, sha256[:16] of the CONTENT it replaces, its line endings made LF,
#: as read 2026-10-10). Content, not bytes: git's autocrlf rewrote litter_bin.py's endings on a
#: checkout with nothing else changed, and a byte pin refused the file this patch had read.
REPLACED = {
    "zoo_keeper/recipes/box_truck.py": ("recipe_box_truck.py", "67c13e78c0df1e05"),
    "zoo_keeper/recipes/litter_bin.py": ("recipe_litter_bin.py", "ac5d4d965919d4ab"),
    "zoo_keeper/genome/species/box_truck.json": ("box_truck.json", "ecbfe7cc9ba8e8df"),
    "zoo_keeper/genome/species/litter_bin.json": ("litter_bin.json", "25dc557a425058b0"),
    "tests/test_box_truck.py": ("test_box_truck.py", "cbf4536f23770df5"),
    "tests/test_litter_bin.py": ("test_litter_bin.py", "e149b47b8cfff2cf"),
}
CARD_ART = "zoo_keeper/core/card_art.py"
CARD_ART_SHA = "c72fb1d29c04e359"
DISPATCH_OLD = ("    if kind.startswith(\"dumpster_\"):\n"
                "        from . import dumpster_forms as DF\n"
                "        return DF.paint(spec)\n")
DISPATCH_NEW = DISPATCH_OLD + ("    # THE LITTER BIN (1.92.0): its slats, placard, lid and bag are\n"
                               "    # `litter_bin_forms`' tiles\n"
                               "    if kind.startswith(\"litter_\"):\n"
                               "        from . import litter_bin_forms as LB\n"
                               "        return LB.paint(spec)\n")
CHANGELOG_HEAD = "## [1.91.0] - window_drape: two velvet panels drawn shut across a den's window\n"


def _src(name):
    return (SRC / name).read_bytes().replace(b"\r\n", b"\n")


def _sha(path):
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()[:16]


def main():
    if DRAFT and not os.environ.get("ZOO_ROOT"):
        sys.exit("refusing: --draft is for a ZOO_ROOT copy, never the repo")
    assert (ZOO / "VERSION").read_bytes().strip() == b"1.91.0", (ZOO / "VERSION").read_bytes()
    entry = _src("CHANGELOG_1.92.0.md").decode("utf-8")
    assert entry.startswith("## [1.92.0] - "), entry[:40]
    if not DRAFT:
        left = entry.replace("RESULT_SUITE", "") if SUITE_PENDING else entry
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    writes = {}
    for rel, name in NEW.items():
        assert not (ZOO / rel).exists(), (rel, "already exists")
        writes[ZOO / rel] = _src(name)
    for rel, (name, sha) in REPLACED.items():
        got = _sha(ZOO / rel)
        assert got == sha, (rel, "is not the file this patch read", got)
        writes[ZOO / rel] = _src(name)
    ca = ZOO / CARD_ART
    assert _sha(ca) == CARD_ART_SHA, (CARD_ART, "is not the file this patch read", _sha(ca))
    t = ca.read_bytes().decode("utf-8")
    assert "\r" not in t, (CARD_ART, "has CR")
    assert t.count(DISPATCH_OLD) == 1 and "litter_bin_forms" not in t, CARD_ART
    writes[ca] = t.replace(DISPATCH_OLD, DISPATCH_NEW).encode("utf-8")
    cl = ZOO / "CHANGELOG.md"
    text = cl.read_bytes().decode("utf-8")
    assert "\r" not in text, "CHANGELOG.md is not LF"
    assert text.startswith(CHANGELOG_HEAD) and text.count(CHANGELOG_HEAD) == 1, text[:90]
    # every pin and anchor matched: now write
    for p, raw in writes.items():
        p.write_bytes(raw)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + text).encode("utf-8"))
    (ZOO / "VERSION").write_bytes(b"1.92.0")
    print("Zoo 1.91.0 -> 1.92.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
