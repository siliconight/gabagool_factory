"""Lot 0.109.0: the yards, the parkland and the roadside (roadmap 228). See
`lot_backdrop_2/CHANGELOG_0.109.0.md`.

Whole files from `lot_backdrop_2/`, each replaced file pinned by the hash its content had when
this patch was written, with its line endings made LF:
  replaced  site_backdrop.py    the three recipes, `_piece(..., z)`, `summary` by species
  replaced  lot.py              `write_site_slots` lifts a slot by its piece's `z`;
                                COVER_MATERIALS knows the tree and the warehouse
  new       tests/test_site_backdrop_2.py
CHANGELOG and VERSION from `CHANGELOG_0.109.0.md`. Nothing is written until every pin matched.

    python patch_lot_backdrop_2.py [--suite-pending]
    python patch_lot_backdrop_2.py --fill            fill the suite's result from result_suite.txt
    LOT_ROOT=<copy> python patch_lot_backdrop_2.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LOT = pathlib.Path(os.environ.get("LOT_ROOT") or HERE.parent / "lot")
SRC = HERE / "lot_backdrop_2"
DRAFT = "--draft" in sys.argv
SUITE_PENDING = "--suite-pending" in sys.argv
FILL = "--fill" in sys.argv

REPLACED = {"site_backdrop.py": ("site_backdrop.py", "6bb735141f9dfdc9"),
            "lot.py": ("lot.py", "c630ae1b6012ef32"),
            # 0.108.0's tests move with the change: the modules count the tower, and
            # parkland lays its trees without a finding now that its kit exists
            "tests/test_site_backdrop.py": ("test_site_backdrop.py", "2c6fa84122e1f5c6")}
NEW = {"tests/test_site_backdrop_2.py": "test_site_backdrop_2.py"}
CHANGELOG_HEAD = "## 0.108.0 - the backdrop beyond the plate's edge, by recipe\n"
VERSION_WAS, VERSION = b"Lot 0.108.0", b"Lot 0.109.0"


def _src(name):
    return (SRC / name).read_bytes().replace(b"\r\n", b"\n")


def _sha(raw):
    return hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def fill():
    assert (LOT / "VERSION").read_bytes().strip() == VERSION, (LOT / "VERSION").read_bytes()
    value = (SRC / "result_suite.txt").read_text(encoding="utf-8").strip()
    assert value and "RESULT_" not in value, value
    for path, rel in ((LOT / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.109.0.md", "the entry")):
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        assert text.count("RESULT_SUITE") == 1, (rel, text.count("RESULT_SUITE"))
        path.write_bytes(text.replace("RESULT_SUITE", value).encode("utf-8").replace(b"\n", eol))
    print("Lot 0.109.0: the suite's result filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("LOT_ROOT"):
        sys.exit("refusing: --draft is for a LOT_ROOT copy, never the repo")
    assert (LOT / "VERSION").read_bytes().strip() == VERSION_WAS, (LOT / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.109.0.md").decode("utf-8")
    assert entry.startswith("## 0.109.0 - "), entry[:40]
    if not DRAFT:
        left = entry.replace("RESULT_SUITE", "") if SUITE_PENDING else entry
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    writes = {}
    for rel, (name, sha) in REPLACED.items():
        raw = (LOT / rel).read_bytes()
        assert _sha(raw) == sha, (rel, "is not the file this patch read", _sha(raw))
        writes[LOT / rel] = _src(name).replace(b"\n", _eol(raw, rel))
    for rel, name in NEW.items():
        assert not (LOT / rel).exists(), (rel, "already exists")
        writes[LOT / rel] = _src(name)
    cl = LOT / "CHANGELOG.md"
    raw = cl.read_bytes()
    eol = _eol(raw, "CHANGELOG.md")
    text = raw.decode("utf-8").replace("\r\n", "\n")
    assert text.startswith(CHANGELOG_HEAD) and text.count(CHANGELOG_HEAD) == 1, text[:90]
    for p, data in writes.items():
        p.write_bytes(data)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + text).encode("utf-8").replace(b"\n", eol))
    (LOT / "VERSION").write_bytes(VERSION)
    print("Lot 0.108.0 -> 0.109.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
