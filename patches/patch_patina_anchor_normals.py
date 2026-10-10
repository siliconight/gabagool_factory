"""Patina 0.30.0: a wall's anchors face out and stand on its face (roadmap 221). See
`patina_anchor_normals/CHANGELOG_0.30.0.md`.

Whole files from `patina_anchor_normals/`, each replaced file pinned by the hash its content had
when this patch was written, with its line endings made LF:
  replaced  patina/anchors.py         the normal's sign in a mirrored view, `_buried`, the
                                      conduit on its wall
            tests/test_anchors.py     the stand-in for `_wall_segments` takes the new keyword
            tests/test_sign_conduit.py  its wall's normal outward; its stub on the wall's plane
  new       tests/test_anchor_normals.py
  edited    patina/version.py         0.29.2 -> 0.30.0
CHANGELOG and VERSION from `CHANGELOG_0.30.0.md`. Nothing is written until every pin and anchor
matched.

    python patch_patina_anchor_normals.py [--suite-pending]
    PATINA_ROOT=<copy> python patch_patina_anchor_normals.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
PA = pathlib.Path(os.environ.get("PATINA_ROOT") or HERE.parent / "patina")
SRC = HERE / "patina_anchor_normals"
DRAFT = "--draft" in sys.argv
SUITE_PENDING = "--suite-pending" in sys.argv

REPLACED = {
    "patina/anchors.py": ("anchors.py", "b6c11a3f94defd6d"),
    "tests/test_anchors.py": ("test_anchors.py", "f97011f4ef27b4eb"),
    "tests/test_sign_conduit.py": ("test_sign_conduit.py", "f28a0b860fcaa6f5"),
}
NEW = {"tests/test_anchor_normals.py": "test_anchor_normals.py"}
VERSION_PY = "patina/version.py"
VERSION_PY_SHA = "f0d56864d7819264"
VER_OLD = '__version__ = "0.29.2"\n'
VER_NEW = '__version__ = "0.30.0"\n'
CHANGELOG_HEAD = "## [0.29.2] - no conduit to a sign's face\n"


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
    if DRAFT and not os.environ.get("PATINA_ROOT"):
        sys.exit("refusing: --draft is for a PATINA_ROOT copy, never the repo")
    assert (PA / "VERSION").read_bytes().strip() == b"Patina 0.29.2", (PA / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.30.0.md").decode("utf-8")
    assert entry.startswith("## [0.30.0] - "), entry[:40]
    if not DRAFT:
        left = entry.replace("RESULT_SUITE", "") if SUITE_PENDING else entry
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    writes = {}
    for rel, (name, sha) in REPLACED.items():
        raw = (PA / rel).read_bytes()
        assert _sha(raw) == sha, (rel, "is not the file this patch read", _sha(raw))
        writes[PA / rel] = _src(name).replace(b"\n", _eol(raw, rel))
    for rel, name in NEW.items():
        assert not (PA / rel).exists(), (rel, "already exists")
        writes[PA / rel] = _src(name)
    vp = PA / VERSION_PY
    raw = vp.read_bytes()
    assert _sha(raw) == VERSION_PY_SHA, (VERSION_PY, "is not the file this patch read", _sha(raw))
    eol = _eol(raw, VERSION_PY)
    text = raw.decode("utf-8").replace("\r\n", "\n")
    assert text.count(VER_OLD) == 1, VERSION_PY
    writes[vp] = text.replace(VER_OLD, VER_NEW).encode("utf-8").replace(b"\n", eol)
    cl = PA / "CHANGELOG.md"
    raw = cl.read_bytes()
    eol = _eol(raw, "CHANGELOG.md")
    text = raw.decode("utf-8").replace("\r\n", "\n")
    assert text.count(CHANGELOG_HEAD) == 1, "CHANGELOG head"
    new_cl = text.replace(CHANGELOG_HEAD, entry.rstrip("\n") + "\n\n" + CHANGELOG_HEAD)
    # every pin and anchor matched: now write
    for p, data in writes.items():
        p.write_bytes(data)
    cl.write_bytes(new_cl.encode("utf-8").replace(b"\n", eol))
    (PA / "VERSION").write_bytes(b"Patina 0.30.0")
    print("Patina 0.29.2 -> 0.30.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
