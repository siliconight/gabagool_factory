"""Level Factory 0.179.0, the grounded table: deli_counter 0.208.0 -> 0.209.0 and zoo 1.100.0 ->
1.101.0, the two rows the real-tool smoke read DRIFT on against the installed tools after roadmap
181's releases (`LF_TOOLS_DIR=<factory> pytest tests/real_tools`: `test_grounded_matches_the_tools_
this_smoke_ran`, the smoke passing being what licenses a pin). Part of 0.179.0's commit, no VERSION
bump. Anchored edits in `packages/tools/contracts.py` (the two rows and a note above 0.178.4's) and
the two test stubs' VERSION files; each anchor asserted once, nothing written on a miss.

    python patches/patch_lf_reground_0_179_0.py
    cd level_factory && LF_TOOLS_DIR=<factory> python -m pytest -q tests/real_tools
"""
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
CONTRACTS = "packages/tools/contracts.py"
ROWS = [
    ('    "deli_counter": {"version": "0.208.0", "source": "VERSION"},\n',
     '    "deli_counter": {"version": "0.209.0", "source": "VERSION"},\n'),
    ('    "zoo":          {"version": "1.100.0", "source": "VERSION",\n',
     '    "zoo":          {"version": "1.101.0", "source": "VERSION",\n'),
]
NOTE_ANCHOR = "# RE-GROUNDED 2026-10-11 (0.178.4), FOUR ROWS, for factory 1.38.0: deli_counter\n"
NOTE = (
    "# RE-GROUNDED 2026-10-11 (0.179.0), TWO ROWS, for the set after factory 1.38.0:\n"
    "# deli_counter 0.208.0 -> 0.209.0 (a roof slot's landings, the roof-props layer)\n"
    "# and zoo 1.100.0 -> 1.101.0 (roof props off hatches and landings, yawed boxes,\n"
    "# the tank's height, one roof merged) -- roadmap 181, the stage this release\n"
    "# plans. Ahead of the install test that certifies that set, as the notes below\n"
    "# say; licensed by the real-tool smoke, which read exactly these two rows DRIFT\n"
    "# before and all green after.\n"
    "#\n"
)
STUBS = [
    ("tests/fixtures/repos/deli_counter/VERSION", b"Deli Counter 0.208.0\n", b"Deli Counter 0.209.0\n"),
    ("tests/fixtures/repos/zoo/VERSION", b"1.100.0\n", b"1.101.0\n"),
]


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def main():
    p = LF / CONTRACTS
    raw = p.read_bytes()
    eol = _eol(raw, CONTRACTS)
    text = raw.decode("utf-8").replace("\r\n", "\n")
    assert "(0.179.0), TWO ROWS" not in text, "already applied"
    for old, new in ROWS:
        assert text.count(old) == 1, (old.strip(), text.count(old))
        text = text.replace(old, new)
    assert text.count(NOTE_ANCHOR) == 1, "0.178.4's note not found once"
    text = text.replace(NOTE_ANCHOR, NOTE + NOTE_ANCHOR)
    stubs = []
    for rel, old, new in STUBS:
        sp = LF / rel
        got = sp.read_bytes()
        assert got.replace(b"\r\n", b"\n") == old, (rel, got)
        stubs.append((sp, new))
    # every anchor matched: now write
    p.write_bytes(text.encode("utf-8").replace(b"\n", eol))
    for sp, new in stubs:
        sp.write_bytes(new)
    print("Level Factory 0.179.0: deli_counter and zoo re-grounded (0.209.0, 1.101.0), two stubs moved")


if __name__ == "__main__":
    sys.exit(main())
