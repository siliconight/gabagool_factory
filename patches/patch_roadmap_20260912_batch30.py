"""Roadmap batch 30, 2026-09-12: item 149's status told what cold run 9008
found -- the 0.73.0 anchor reached one of three call sites and the guard
fired -- and 0.73.1. REPLACE; old kept verbatim. Asserts once.
"""
import io
import sys

P = "PIPELINE_ROADMAP.md"

OLD = """*STATUS: NARROWED 2026-09-12 -- FOUND BY COLD RUN 9007, FIXED IN LEVEL
FACTORY 0.73.0 THE SAME HOUR, NOT YET RUN*"""

NEW = """*STATUS: NARROWED 2026-09-12 -- 0.73.0 ANCHORED ONE OF THREE DRAWS AND COLD
RUN 9008 CAUGHT IT; 0.73.1 MAKES THE LOT ONE RULE READ OFF THE BRIEF; 9009
RUNNING. 9008 (same bank brief, seeds 9008/9109/9210): the planner's lot
had a bank and the compose spec's and the site spec's did not -- their
greybox lots were marina_a02 / pawn_shop_a02 / strip_club_a02 and the
like -- and the planner's own guard refused the art layer in one second:
"zoo_fixtures_build.bank_branch_a02 is planned for archetype
'bank_branch_a02', which is not in this candidate's lot -- the planner
and the spec builder disagree about which buildings this mission places".
The guard was written for exactly this and did its job; the export then
shipped the greybox lot (export exit 0, 0 interventions, which is item
17's caveat again: the counter measures the tools, not the deliverable).
The miss was mine: `lot_for`'s docstring names three callers, a grep of
`packages` and `adapters` found one, and the other two live under
`apps/cli/commands`. LF 0.73.1: `building_library.lot_for_brief(model,
candidate, themed=)` reads library, count and archetype off one brief;
the planner and `_lot_for_compose` call it, `_write_site_spec`'s
`pick_lot` takes the same anchor, and `test_lot_for_brief` holds that the
three are one draw. Cold run 9009 is the third try on the brief. EARLIER
STATUS, KEPT VERBATIM: NARROWED 2026-09-12 -- FOUND BY COLD RUN 9007,
FIXED IN LEVEL FACTORY 0.73.0 THE SAME HOUR, NOT YET RUN*"""


def main() -> int:
    raw = io.open(P, "rb").read()
    if b"\r\n" in raw:
        print("roadmap has CRLF endings -- stop", file=sys.stderr)
        return 1
    text = raw.decode("utf-8")
    n = text.count(OLD)
    if n != 1:
        print(f"anchor matched {n} times; refusing", file=sys.stderr)
        return 1
    out = text.replace(OLD, NEW, 1).encode("utf-8")
    io.open(P, "wb").write(out)
    print(f"wrote {len(out)} bytes ({len(raw)} before); item 149 updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
