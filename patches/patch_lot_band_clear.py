"""Lot 0.106.0: a lamp or a tree keeps out of a shop band's span. See
`lot_band_clear/CHANGELOG_0.106.0.md`.

Whole files from `lot_band_clear/`, each replaced file pinned by the hash its content had when
this patch was written, with its line endings made LF:
  replaced  site_furniture.py   SIGN_CLEAR; `_nudged(..., avoid=)`; `_sign_spans`; `_nearest_road`;
                                `plan_furniture(..., sign_bands=)` and LOT_BAND_KEPT_CLEAR
  replaced  lot.py              `sign_bands`; the furniture planner is told where the bands hang
  new       tests/test_site_band_clear.py
CHANGELOG and VERSION from `CHANGELOG_0.106.0.md`. Nothing is written until every pin matched.

    python patch_lot_band_clear.py [--suite-pending]
    LOT_ROOT=<copy> python patch_lot_band_clear.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LOT = pathlib.Path(os.environ.get("LOT_ROOT") or HERE.parent / "lot")
SRC = HERE / "lot_band_clear"
DRAFT = "--draft" in sys.argv
SUITE_PENDING = "--suite-pending" in sys.argv

REPLACED = {
    "site_furniture.py": ("site_furniture.py", "5c149546a02443fb"),
    "lot.py": ("lot.py", "0f052b78245dc9fc"),
}
NEW = {"tests/test_site_band_clear.py": "test_site_band_clear.py"}
CHANGELOG_HEAD = "## 0.105.0 - a shop sign's pack manifest travels beside its maps\n"


def _src(name):
    return (SRC / name).read_bytes().replace(b"\r\n", b"\n")


def _sha(raw):
    return hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]


def _eol(raw, rel):
    """The file's own line ending. A file with both refuses: there is no one ending to restore."""
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def main():
    if DRAFT and not os.environ.get("LOT_ROOT"):
        sys.exit("refusing: --draft is for a LOT_ROOT copy, never the repo")
    assert (LOT / "VERSION").read_bytes().strip() == b"Lot 0.105.0", (LOT / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.106.0.md").decode("utf-8")
    assert entry.startswith("## 0.106.0 - "), entry[:40]
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
    # every pin matched: now write
    for p, data in writes.items():
        p.write_bytes(data)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + text).encode("utf-8").replace(b"\n", eol))
    (LOT / "VERSION").write_bytes(b"Lot 0.106.0")
    print("Lot 0.105.0 -> 0.106.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
