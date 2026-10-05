"""Level Factory 0.142.0: the Empties' terrace deals its houses from a shuffled
bag of every design instead of drawing each uniformly. See
`lf_terrace_deal/CHANGELOG_0.142.0.md`.

Cold run 9160: twelve rowhome designs, and its three candidates' rows used
10, 12 and 10 of them with one design up to 6 times.

Anchored edits (every anchor once; refuses on a miss):
  packages/pipeline/empties.py   _deal; terrace deals, and pops only a house
                                 it places
Copies the test; CHANGELOG and VERSION.

    python patch_lf_terrace_deal.py
"""
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve().parent
LF = HERE.parent / "level_factory"
SRC = HERE / "lf_terrace_deal"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


DEAL_ANCHOR = '''

def terrace(rows, extents, stream, roads, span_x):
'''
DEAL_NEW = '''

def _deal(usable, stream, avoid=None):
    """Every design once, in an order shuffled off ``stream`` (Fisher-Yates),
    dealt from the END of the list. If the first one dealt would be ``avoid``
    -- the house just placed -- it trades places with the next, so no two
    neighbours are the same house across two deals either.

    WHY A DEAL (0.142.0). The terrace drew each house uniformly and turned
    away only an immediate repeat. Cold run 9160 doubled the rowhomes to
    twelve expecting a row to show each about twice, and its three
    candidates' rows -- 25, 31 and 29 houses -- used 10, 12 and 10 of the
    designs with the most-repeated shown 5, 6 and 5 times. The library's size
    moved the mean; the spread is the draw's. Dealt, a row of n houses from k
    designs shows each floor(n/k) or one more times, and every design by the
    k-th house."""
    bag = list(usable)
    for i in range(len(bag) - 1, 0, -1):
        j = next(stream) % (i + 1)
        bag[i], bag[j] = bag[j], bag[i]
    if avoid is not None and len(bag) > 1 and bag[-1]["id"] == avoid:
        bag[-1], bag[-2] = bag[-2], bag[-1]
    return bag


def terrace(rows, extents, stream, roads, span_x):
'''

LOOP_OLD = '''    out, prev, in_run = [], None, 0
    run_len = RUN[0] + next(stream) % (RUN[1] - RUN[0] + 1)
    need = 0.0
    while True:
        pick = usable[next(stream) % len(usable)]
        if prev is not None and pick["id"] == prev and len(usable) > 1:
            pick = usable[(usable.index(pick) + 1) % len(usable)]
        tx0, tx1, ty0, ty1 = _turned(extents[pick["id"]], 180)
'''
LOOP_NEW = '''    out, prev, in_run = [], None, 0
    run_len = RUN[0] + next(stream) % (RUN[1] - RUN[0] + 1)
    need = 0.0
    bag: list = []
    while True:
        # A DEAL, NOT A DRAW (0.142.0): the next house off a shuffled bag of
        # every design, refilled when empty (`_deal`). A pick a road turns
        # away stays on the bag for the far side of it; only a house that is
        # placed is dealt.
        if not bag:
            bag = _deal(usable, stream, prev)
        pick = bag[-1]
        tx0, tx1, ty0, ty1 = _turned(extents[pick["id"]], 180)
'''

POP_OLD = '''        need = max(need, -(at_y + ty0))
        prev = pick["id"]
'''
POP_NEW = '''        need = max(need, -(at_y + ty0))
        bag.pop()
        prev = pick["id"]
'''


def main():
    assert (LF / "VERSION").read_text(encoding="utf-8").strip() == "0.141.0"
    _edit(LF / "packages" / "pipeline" / "empties.py",
          [(DEAL_ANCHOR, DEAL_NEW), (LOOP_OLD, LOOP_NEW), (POP_OLD, POP_NEW)])
    shutil.copyfile(SRC / "test_terrace_deal.py", LF / "tests" / "unit" / "test_terrace_deal.py")
    ch = LF / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    ch.write_text((SRC / "CHANGELOG_0.142.0.md").read_text(encoding="utf-8").rstrip("\n") + "\n\n" + s,
                  encoding="utf-8", newline="\n")
    (LF / "VERSION").write_text("0.142.0", encoding="utf-8", newline="\n")
    print("applied Level Factory 0.142.0")


if __name__ == "__main__":
    main()
