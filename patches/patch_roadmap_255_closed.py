"""Roadmap 255 CLOSED: Deli Counter 0.223.0, layout_lint L26. Replaces 255's status block (asserted once). The
index is NOT touched here: run `python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_255_closed.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUS_OLD_HEAD = ("*STATUS: OPEN 2026-10-14 -- FOUND TRACING THE WALK'S FINDING 5. A partition that stops short of "
                   "where the rooms it divides meet leaves an opening no spec names")
STATUS_NEW = (
    "*STATUS: CLOSED 2026-10-15 -- Deli Counter 0.223.0 (cdaefcd0): the advisory exists and the list is the walker's. "
    "`tactical.OPEN_FLOOR_M` (1.2 m) is the engine's open-floor threshold spelled once where it was spelled four "
    "times; `tactical.open_edge` returns the edge two rooms meet along and how much of it no partition covers, and "
    "`shared_open_edge` asks it (`build_graph`, L12 and L24 move nothing); a room's `open_to` (the schema admits it) "
    "says the floor between two rooms is meant; `layout_lint.open_floors` names every pair tactical joins that no "
    "`open_to` names, and L26 reports each as an advisory WARN in every mode, with where and how much. "
    "`open_floor_baseline.py` froze the built library's pairs in `open_floor_baseline.json` -- 49 open floors "
    "nobody named, in 26 of 159 built specs (the instrument's 32 stretches in 20 of 446 specs counted contiguous "
    "stretches over the whole specs folder; the lint counts pairs by the engine's total-uncovered rule over built "
    "specs) -- and `test_open_floor.py` fails on a new pair and on a stale one, as L24's does. Suite 1,549 passed; "
    "nothing built moves, and Level Factory's findings never carry a lint warning, so no cold run moves. What is "
    "left is not this item's: the walker sorts the 49, one pair at a time, saying each is meant (`open_to`) or "
    "walling it, and `open_floor_baseline.py` is re-run after each.*"
)


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    i = text.find(STATUS_OLD_HEAD)
    assert i >= 0 and text.count(STATUS_OLD_HEAD) == 1, "255's status block not found once"
    j = text.find("\n", i)
    old = text[i:j]
    assert old.endswith("*") and old.count("*STATUS:") == 1, old[-80:]
    text = text[:i] + STATUS_NEW + text[j:]
    head = "\n\n**255. A partition that stops short of where its rooms meet.**"
    k = text.find(STATUS_NEW)
    assert text[k + len(STATUS_NEW):].startswith(head), "255's status no longer adjoins its heading"
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 255: status replaced; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
