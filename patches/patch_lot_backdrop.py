"""Lot 0.108.0: the backdrop beyond the plate's edge, by recipe (roadmap 228, step D). See
`lot_backdrop/CHANGELOG_0.108.0.md`.

Whole files from `lot_backdrop/`, each replaced file pinned by the hash its content had when this
patch was written, with its line endings made LF:
  replaced  lot.py              COVER_MATERIALS knows the two species; `write_site_slots` gives
                                each backdrop piece a slot with no collision; `assemble` plans the
                                backdrop after the perimeter fence and says LOT_BACKDROP_PLACED
  new       site_backdrop.py    the recipes, `plan`, `summary`
  new       tests/test_site_backdrop.py
CHANGELOG and VERSION from `CHANGELOG_0.108.0.md`. Nothing is written until every pin matched.

    python patch_lot_backdrop.py [--suite-pending]
    python patch_lot_backdrop.py --fill            fill the suite's result from result_suite.txt
    LOT_ROOT=<copy> python patch_lot_backdrop.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LOT = pathlib.Path(os.environ.get("LOT_ROOT") or HERE.parent / "lot")
SRC = HERE / "lot_backdrop"
DRAFT = "--draft" in sys.argv
SUITE_PENDING = "--suite-pending" in sys.argv
FILL = "--fill" in sys.argv

REPLACED = {"lot.py": ("lot.py", "08e70f295907d56d"),
            # the example compound's manifest now carries the backdrop beside its cover and fences
            "tests/test_site_cover_slots.py": ("test_site_cover_slots.py", "183201c8a1fef3bc")}
NEW = {"site_backdrop.py": "site_backdrop.py",
       "tests/test_site_backdrop.py": "test_site_backdrop.py"}
CHANGELOG_HEAD = "## 0.107.0 - the fence at the plate's edge\n"
VERSION_WAS, VERSION = b"Lot 0.107.0", b"Lot 0.108.0"


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
    for path, rel in ((LOT / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.108.0.md", "the entry")):
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        assert text.count("RESULT_SUITE") == 1, (rel, text.count("RESULT_SUITE"))
        path.write_bytes(text.replace("RESULT_SUITE", value).encode("utf-8").replace(b"\n", eol))
    print("Lot 0.108.0: the suite's result filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("LOT_ROOT"):
        sys.exit("refusing: --draft is for a LOT_ROOT copy, never the repo")
    assert (LOT / "VERSION").read_bytes().strip() == VERSION_WAS, (LOT / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.108.0.md").decode("utf-8")
    assert entry.startswith("## 0.108.0 - "), entry[:40]
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
    print("Lot 0.107.0 -> 0.108.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
