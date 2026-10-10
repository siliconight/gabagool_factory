"""Pixelcoat 0.62.0: a business's sign in Blue Highway, smooth, at its band's shape (roadmap 223).
See `pixelcoat_smooth_signs/CHANGELOG_0.62.0.md`.

Whole files from `pixelcoat_smooth_signs/`, each replaced file pinned by the hash its content had
when this patch was written, with its line endings made LF:
  new       pixelcoat/core/smooth_type.py, pixelcoat/core/smooth_faces/__init__.py,
            tools/mint_smooth_type.py, tests/test_smooth_signs.py
  replaced  pixelcoat/core/signage.py   `face`, `_place_smooth`, the pack's sampling and mips
            pixelcoat/cli/main.py       `theme-signs` at 6:1 and smooth; `paint_matte`
            pixelcoat/version.py        _FALLBACK 0.62.0
  minted    pixelcoat/core/smooth_faces/highway_cond.py, by the mint tool this writes, and
            checked against the hash it had when this patch was written (and Zoo's table)
CHANGELOG and VERSION from `CHANGELOG_0.62.0.md`. Nothing is written until every pin matched;
the mint runs last, and a table that is not the expected bytes is said and stops the patch.

    python patch_pixelcoat_smooth_signs.py [--suite-pending]
    PIXELCOAT_ROOT=<copy> python patch_pixelcoat_smooth_signs.py --draft
"""
import hashlib
import os
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
PC = pathlib.Path(os.environ.get("PIXELCOAT_ROOT") or HERE.parent / "pixelcoat")
SRC = HERE / "pixelcoat_smooth_signs"
DRAFT = "--draft" in sys.argv
SUITE_PENDING = "--suite-pending" in sys.argv

NEW = {"pixelcoat/core/smooth_type.py": "smooth_type.py",
       "pixelcoat/core/smooth_faces/__init__.py": "smooth_faces_init.py",
       "tools/mint_smooth_type.py": "mint_smooth_type.py",
       "tests/test_smooth_signs.py": "test_smooth_signs.py"}
REPLACED = {
    "pixelcoat/core/signage.py": ("signage.py", "27d0a0663c67a94f"),
    "pixelcoat/cli/main.py": ("cli_main.py", "ec74d846645c5fe2"),
    "pixelcoat/version.py": ("version.py", "f33c62964dafc22c"),
}
TABLE = "pixelcoat/core/smooth_faces/highway_cond.py"
#: sha256[:16] of the table the mint tool gave on 2026-10-10 (PIL 12.3.0, FreeType 2.14.3), and
#: of Zoo's `smooth_faces/highway_cond.py`, byte for byte
TABLE_SHA = "36cc08e57d9d0c52"
CHANGELOG_HEAD = "## [0.61.0] - one name list: a band is dealt the names Zoo paints over the door\n"


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
    if DRAFT and not os.environ.get("PIXELCOAT_ROOT"):
        sys.exit("refusing: --draft is for a PIXELCOAT_ROOT copy, never the repo")
    assert (PC / "VERSION").read_bytes().strip() == b"Pixelcoat 0.61.0", (PC / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.62.0.md").decode("utf-8")
    assert entry.startswith("## [0.62.0] - "), entry[:40]
    if not DRAFT:
        left = entry.replace("RESULT_SUITE", "") if SUITE_PENDING else entry
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    writes = {}
    for rel, name in NEW.items():
        assert not (PC / rel).exists(), (rel, "already exists")
        writes[PC / rel] = _src(name)
    assert not (PC / TABLE).exists(), (TABLE, "already exists")
    for rel, (name, sha) in REPLACED.items():
        raw = (PC / rel).read_bytes()
        assert _sha(raw) == sha, (rel, "is not the file this patch read", _sha(raw))
        writes[PC / rel] = _src(name).replace(b"\n", _eol(raw, rel))
    cl = PC / "CHANGELOG.md"
    raw = cl.read_bytes()
    eol = _eol(raw, "CHANGELOG.md")
    text = raw.decode("utf-8").replace("\r\n", "\n")
    assert text.count(CHANGELOG_HEAD) == 1, "CHANGELOG head"
    new_cl = text.replace(CHANGELOG_HEAD, entry.rstrip("\n") + "\n\n" + CHANGELOG_HEAD)
    # every pin matched: now write
    for p, data in writes.items():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
    cl.write_bytes(new_cl.encode("utf-8").replace(b"\n", eol))
    (PC / "VERSION").write_bytes(b"Pixelcoat 0.62.0")
    # the table, minted from the vendored font by the tool just written
    rc = subprocess.run([sys.executable, str(PC / "tools" / "mint_smooth_type.py"), "--all"],
                        capture_output=True, text=True)
    assert rc.returncode == 0, rc.stdout + rc.stderr
    got = _sha((PC / TABLE).read_bytes())
    if got != TABLE_SHA:
        sys.exit(f"STOPPED: the minted {TABLE} is {got}, not {TABLE_SHA}: this FreeType draws the "
                 "face differently from the one the table was checked against; the other files "
                 "are written, the table is not what Zoo has")
    print("Pixelcoat 0.61.0 -> 0.62.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
