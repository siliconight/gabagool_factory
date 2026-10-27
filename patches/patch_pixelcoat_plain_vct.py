"""Pixelcoat 0.63.0: a store's vinyl tile is one pale colour, polished (the walker on seed 9205's supermarket).
See `pixelcoat_plain_vct/CHANGELOG_0.63.0.md`.

Whole files from `pixelcoat_plain_vct/`, each replaced file pinned by the hash its content had when this patch was
written, with its line endings made LF:
  new       tests/test_plain_vct.py
  replaced  profiles/materials/vct_floor_beige.json   12-inch off-white tiles, faint joints, roughness 0.12
            tools/art_standard_baseline.json          `vct_floor_beige`'s row only (the changelog says why)
            pixelcoat/version.py                      _FALLBACK 0.63.0
CHANGELOG and VERSION from `CHANGELOG_0.63.0.md`. Nothing is written until every pin matched.

    python patch_pixelcoat_plain_vct.py
    PIXELCOAT_ROOT=<copy> python patch_pixelcoat_plain_vct.py
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
PC = pathlib.Path(os.environ.get("PIXELCOAT_ROOT") or HERE.parent / "pixelcoat")
SRC = HERE / "pixelcoat_plain_vct"

NEW = {"tests/test_plain_vct.py": "test_plain_vct.py"}
REPLACED = {
    "profiles/materials/vct_floor_beige.json": ("vct_floor_beige.json", "77483414450b5b35"),
    "tools/art_standard_baseline.json": ("art_standard_baseline.json", "79b51fe7a068d635"),
    "pixelcoat/version.py": ("version.py", "21909f180228458d"),
}
CHANGELOG_HEAD = "## [0.62.0] - a business's sign in Blue Highway, smooth, at its band's shape\n"


def _src(name):
    return (SRC / name).read_bytes().replace(b"\r\n", b"\n")


def _sha(raw):
    return hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]


def _eol(raw, rel):
    """The file's own line ending. A file with both refuses: there is no one ending to restore."""
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    if crlf not in (0, lf):
        sys.exit(f"REFUSED: {rel} has mixed line endings ({crlf} CRLF of {lf}); nothing written")
    return b"\r\n" if crlf else b"\n"


def main():
    if (PC / "VERSION").read_bytes().strip() != b"Pixelcoat 0.62.0":
        sys.exit("REFUSED: VERSION reads %r, not Pixelcoat 0.62.0; nothing written" % (PC / "VERSION").read_bytes())
    entry = _src("CHANGELOG_0.63.0.md").decode("utf-8")
    assert entry.startswith("## [0.63.0] - "), entry[:40]
    writes = {}
    for rel, name in NEW.items():
        if (PC / rel).exists():
            sys.exit(f"REFUSED: {rel} exists already; nothing written")
        writes[PC / rel] = _src(name)
    for rel, (name, sha) in REPLACED.items():
        raw = (PC / rel).read_bytes()
        if _sha(raw) != sha:
            sys.exit(f"REFUSED: {rel} is {_sha(raw)}, not the {sha} this patch read; nothing written")
        writes[PC / rel] = _src(name).replace(b"\n", _eol(raw, rel))
    cl = PC / "CHANGELOG.md"
    raw = cl.read_bytes()
    eol = _eol(raw, "CHANGELOG.md")
    text = raw.decode("utf-8").replace("\r\n", "\n")
    if text.count(CHANGELOG_HEAD) != 1:
        sys.exit("REFUSED: CHANGELOG.md does not open on 0.62.0; nothing written")
    new_cl = text.replace(CHANGELOG_HEAD, entry.rstrip("\n") + "\n\n" + CHANGELOG_HEAD)
    # every pin matched: now write
    for p, data in writes.items():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
    cl.write_bytes(new_cl.encode("utf-8").replace(b"\n", eol))
    (PC / "VERSION").write_bytes(b"Pixelcoat 0.63.0")
    print("Pixelcoat 0.62.0 -> 0.63.0: %d files written, CHANGELOG, VERSION" % len(writes))


if __name__ == "__main__":
    main()
