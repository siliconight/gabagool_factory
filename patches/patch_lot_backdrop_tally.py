"""Lot 0.109.1: the backdrop's summary line counts pieces by species, not rowhomes.

Cold run 9226's yards printed `0 rowhome(s) in 3 bands a side (N 41, ...)`: `summary["houses"]`
is the borough's rowhome count, and only the borough has three bands. One anchored edit to the
print in `lot.py`, pinned by hash, asserted once; CHANGELOG and VERSION from
`lot_backdrop_tally/CHANGELOG_0.109.1.md`. Nothing is written on a miss.

    python patches/patch_lot_backdrop_tally.py            # LOT_ROOT=<copy> ... --draft for a copy
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LOT = pathlib.Path(os.environ.get("LOT_ROOT") or HERE.parent / "lot")
SRC = HERE / "lot_backdrop_tally"
DRAFT = "--draft" in sys.argv
SHA_LOT_PY = "cdc33554b0aa52cb"      # lot.py as read on 2026-10-10, Lot 0.109.0
VERSION_WAS, VERSION = b"Lot 0.109.0", b"Lot 0.109.1"
CHANGELOG_HEAD = "## 0.109.0 - the yards, the parkland and the roadside\n"

OLD = (
    "        print(f\"[lot] LOT_BACKDROP_PLACED: recipe {merged['backdrop_plan']['recipe']}, \"\n"
    "              f\"{_bs['houses']} rowhome(s) in {len(site_backdrop.BANDS)} bands a side \"\n"
    "              f\"({', '.join(f'{k} {v}' for k, v in _bs['by_side'].items())}), \"\n"
    "              f\"{_bs['modules']} module(s), {_bs['towers']} water tower(s)\")\n")
NEW = (
    "        # pieces by species (0.109.1): `houses` is the borough's rowhome count and\n"
    "        # read 0 of the yards; the bands differ by recipe, so no count of them here\n"
    "        print(f\"[lot] LOT_BACKDROP_PLACED: recipe {merged['backdrop_plan']['recipe']}, \"\n"
    "              f\"{len(site_spec['backdrop'])} piece(s) (\"\n"
    "              f\"{', '.join(f'{k} {v}' for k, v in sorted(_bs['by_species'].items()))}) \"\n"
    "              f\"by side ({', '.join(f'{k} {v}' for k, v in _bs['by_side'].items())}), \"\n"
    "              f\"{_bs['modules']} module(s), {_bs['towers']} water tower(s)\")\n")


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def main():
    if DRAFT and not os.environ.get("LOT_ROOT"):
        sys.exit("refusing: --draft is for a LOT_ROOT copy, never the repo")
    assert (LOT / "VERSION").read_bytes().strip() == VERSION_WAS, (LOT / "VERSION").read_bytes()
    p = LOT / "lot.py"
    raw = p.read_bytes()
    got = hashlib.sha256(raw).hexdigest()[:16]
    assert got == SHA_LOT_PY, ("lot.py is not the file this patch read", got)
    eol = _eol(raw, "lot.py")
    text = raw.decode("utf-8").replace("\r\n", "\n")
    assert text.count(OLD) == 1, text.count(OLD)
    text = text.replace(OLD, NEW)
    entry = (SRC / "CHANGELOG_0.109.1.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## 0.109.1 - "), entry[:40]
    cl = LOT / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:90]
    # Every pin and anchor matched: now write.
    p.write_bytes(text.replace("\n", eol.decode()).encode("utf-8"))
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).replace("\n", cl_eol.decode()).encode("utf-8"))
    (LOT / "VERSION").write_bytes(VERSION)
    print("Lot 0.109.0 -> 0.109.1" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
