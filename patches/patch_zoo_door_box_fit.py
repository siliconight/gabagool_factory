"""Zoo 1.94.0: a door box wears its business's band as the pack asks, at the art's own shape
(roadmap 223). See `zoo_door_box_fit/CHANGELOG_1.94.0.md`.

Whole files from `zoo_door_box_fit/`, each replaced file pinned by the hash its content had when
this patch was written, with its line endings made LF:
  replaced  zoo_keeper/core/skins.py          `png_aspect`, `fit_uv`; `load_pack` returns the
                                              pack's `interpolation` and `art_aspect`
            zoo_keeper/bpylayer/materials.py  the sign material samples as the pack asks
            zoo_keeper/recipes/sign_box.py    the face's UVs keep the art's shape
  new       tests/test_door_box_fits_its_art.py
CHANGELOG and VERSION from `CHANGELOG_1.94.0.md`. Nothing is written until every pin matched.

    python patch_zoo_door_box_fit.py [--suite-pending]
    ZOO_ROOT=<copy> python patch_zoo_door_box_fit.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ZOO = pathlib.Path(os.environ.get("ZOO_ROOT") or HERE.parent / "zoo")
SRC = HERE / "zoo_door_box_fit"
DRAFT = "--draft" in sys.argv
SUITE_PENDING = "--suite-pending" in sys.argv

REPLACED = {
    "zoo_keeper/core/skins.py": ("skins.py", "8e7364fd16e0cc8f"),
    "zoo_keeper/bpylayer/materials.py": ("materials.py", "2b3bb8c06e8b0004"),
    "zoo_keeper/recipes/sign_box.py": ("sign_box.py", "db730277ddc00110"),
}
NEW = {"tests/test_door_box_fits_its_art.py": "test_door_box_fits_its_art.py"}
CHANGELOG_HEAD = "## [1.93.0] - trash_bags: a heap of filled garbage bags\n"


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
    if DRAFT and not os.environ.get("ZOO_ROOT"):
        sys.exit("refusing: --draft is for a ZOO_ROOT copy, never the repo")
    assert (ZOO / "VERSION").read_bytes().strip() == b"1.93.0", (ZOO / "VERSION").read_bytes()
    entry = _src("CHANGELOG_1.94.0.md").decode("utf-8")
    assert entry.startswith("## [1.94.0] - "), entry[:40]
    if not DRAFT:
        left = entry.replace("RESULT_SUITE", "") if SUITE_PENDING else entry
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    writes = {}
    for rel, (name, sha) in REPLACED.items():
        raw = (ZOO / rel).read_bytes()
        assert _sha(raw) == sha, (rel, "is not the file this patch read", _sha(raw))
        writes[ZOO / rel] = _src(name).replace(b"\n", _eol(raw, rel))
    for rel, name in NEW.items():
        assert not (ZOO / rel).exists(), (rel, "already exists")
        writes[ZOO / rel] = _src(name)
    cl = ZOO / "CHANGELOG.md"
    raw = cl.read_bytes()
    eol = _eol(raw, "CHANGELOG.md")
    text = raw.decode("utf-8").replace("\r\n", "\n")
    assert text.startswith(CHANGELOG_HEAD) and text.count(CHANGELOG_HEAD) == 1, text[:90]
    # every pin matched: now write
    for p, data in writes.items():
        p.write_bytes(data)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + text).replace("\n", "\r\n" if eol == b"\r\n"
                                                                else "\n").encode("utf-8"))
    (ZOO / "VERSION").write_bytes(b"1.94.0")
    print("Zoo 1.93.0 -> 1.94.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
