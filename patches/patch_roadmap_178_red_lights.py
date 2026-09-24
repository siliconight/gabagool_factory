"""Roadmap item 178: the instruments report and nothing blocks.

WHY THIS IS ONE ITEM AND NOT FOUR. Each instance below was found separately and
looked like a small oversight -- a test with a bad duty cycle, a gate nobody
wired up, a warning nobody reads. Four of them inside one week, found while
looking for other things, is not four oversights. It is the standing state of
the second gate.

Item 18 says every gate measures whether a level WORKS and none measures
whether it is GOOD. That framing is half right and it is the half that has
been quoted. The other half is worse: several instruments that DO measure
whether a level is good already exist, already run, already print a number --
and not one of them can stop anything. The gap is not measurement. It is that
measurement was never connected to a decision.

Anchored on the file's final paragraph, which must match exactly once.
"""
from pathlib import Path

TARGET = Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

ANCHOR = """should run on its own cadence, and worth noting that the regression surfaced as
a side effect of an unrelated release rather than by being looked for.
"""

BODY = """should run on its own cadence, and worth noting that the regression surfaced as
a side effect of an unrelated release rather than by being looked for.

*STATUS: OPEN 2026-09-24 -- FOUR INSTRUMENTS, ALL REPORTING, NONE BLOCKING,
found inside one week while looking for other things. The z-fight gate has
printed FAIL and the word ERROR on five consecutive cold runs reported as
zeros; Lot's isolation warning fires on 65 of 79 generated sites; Lot's
objective-approach count reads 0 on 38 of 79 and has never exceeded 2;
`test_navgate_population` fires only after a library rebuild and hid a stair
regression for five weeks. Item 18 says the second gate does not exist. It
does exist -- it is wired to nothing.*

**178. The instruments report and nothing blocks, and that is one defect
rather than four.** Raised by the walker, 2026-09-24: "individually each is a
small oversight. Together it's the thing standing between measured and gated."

**THE FOUR, with the figures that make them comparable.**

    instrument                  fires            blocks   who reads it
    z-fight gate                every run        no       nobody
    Lot isolation warning       65 of 79 sites   no       nobody
    Lot objective_approaches    every site       no       nobody
    test_navgate_population     on rebuild only  YES      a rebuild, rarely

  * **The z-fight gate.** `presentation_compose` exits 3 with
    `z-fight gate [FAIL]` and `ERROR: coplanar surfaces detected -- the package
    would flicker`: 9072 (107 pairs / 363 solids), 9073 (72/283), 9075
    (44/300), 9076 (130/594), 9077 (79/525). Every one of those runs was
    reported as a zero-intervention success, by me. Tracked as item 177.
  * **Lot's isolation warning.** `site_tactical.analyze` emits "buildings with
    no declared path-route from 'b0'" on **65 of 79** site specs on disk, 20 of
    them naming two buildings. Cold run 9077's shipped package -- a genuine
    zero -- carries `isolated_buildings: ['b2']`.
  * **Lot's `objective_approaches`.** Intel, never gated: 0 on 38 specs, 1 on
    37, 2 on 4, never 3. `site_layout_lint` S5 lints the angular spread of
    those approaches against `SPREAD_MIN` 90 deg and also only warns.
  * **`test_navgate_population`.** It DOES block -- and only on a machine that
    has just rebuilt the shell library, which happens when a release needs it.
    Duty cycle rather than wiring, and the interval that hid 0.143.0's stair
    regression was five weeks (item 176).

**THE THREE SHAPES ARE DIFFERENT AND NEED DIFFERENT ANSWERS**, which is the
reason this is worth one item rather than four bug reports:

  1. **Fires always, blocks nothing** (z-fight, isolation, approaches). The
     number exists and no threshold was ever chosen. Choosing one is a taste
     call a tool cannot make -- `repetition_census.py` says so explicitly --
     so these are waiting on a person, not on code.
  2. **Blocks, but rarely runs** (`test_navgate_population`). The threshold
     exists and the cadence does not.
  3. **Deliberately non-blocking, and says so** (`navgate_baseline.json`'s
     UNJUDGED set: "the exit code is deliberately unchanged, so the set can
     grow silently. This freezes it."). This is the CONSIDERED version of the
     same shape, and it is the model for the others: a number that does not
     block is fine when something freezes it and fails on a new entrant.

**WHAT THIS IS NOT.** It is not an argument for making every warning fatal.
Three of the four have never had a threshold examined, and an approach count
turned into a gate today would fail one hundred percent of levels for a reason
that is not real -- `build_graph` counts building-to-building paths only, so
the graph does not model the street the buildings actually connect along. A
gate over a wrong graph is worse than a warning over one.

**THE DECISION OWED, PER INSTRUMENT**: block, freeze-and-fail-on-new-entrants
(the baseline pattern), or delete. Leaving one as it is teaches every future
reader that FAIL means nothing here, which is worse than not having it -- and
that reading is already earned, because five runs printed ERROR and were called
clean.

**WHY IT MATTERS MORE THAN ANY ONE FIX.** The deliverable is
interventions-per-level, and that number now reads zero on 72 of 73 completed
runs. A zero means nobody touched the machine; it does not mean the level is
good. Every instrument above is evidence about the second question, already
being collected, already being discarded. Connecting them is cheaper than
building anything new and is the difference between a pipeline that produces
levels and one that produces levels somebody would ship.
"""


def main() -> None:
    data = TARGET.read_bytes()
    if b"\r\n" in data:
        raise SystemExit("REFUSED: expected LF, found CRLF")
    text = data.decode("utf-8")
    before = len(data)
    if "**178." in text:
        raise SystemExit("REFUSED: item 178 already present")
    hits = text.count(ANCHOR)
    if hits != 1:
        raise SystemExit(f"REFUSED: anchor matched {hits} times")
    out = text.replace(ANCHOR, BODY).encode("utf-8")
    if b"\r\n" in out:
        raise SystemExit("REFUSED: would write CRLF")
    TARGET.write_bytes(out)
    print(f"{TARGET.name}: {before} -> {len(out)} bytes (+{len(out) - before})")


if __name__ == "__main__":
    main()
