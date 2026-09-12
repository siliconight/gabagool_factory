"""Roadmap batch 38, 2026-09-12: cold runs 9013 and 9014 (17 REPLACE, old
kept) and the retraction inside the retraction on 18 (REPLACE, old kept):
DC 0.120.0's basis rewrite was wrong, the engine said so, 0.120.1 is the
package. Asserts every anchor.
"""
import io
import sys

P = "PIPELINE_ROADMAP.md"

R = []

R.append(("""*STATUS: NARROWED 2026-09-12 (late) -- COLD RUN 9012 SCORED ZERO ON THE
BANK BRIEF AND SHIPPED THE TELLER LINE AS A GLASS BARRIER WITH SIX
STATIONS, THE WALKER'S FEEDBACK ANSWERED IN A PACKAGE THE SAME DAY.""",
"""*STATUS: NARROWED 2026-09-12 (night) -- COLD RUNS 9013 AND 9014 SCORED
ZERO ON THE BANK BRIEF; 9013 IS THE PACKAGE THAT PROVED DC 0.120.0 WRONG
AND 9014 IS THE ONE WITH THE REMAINDERS ALONG THEIR WALLS BY THE ENGINE'S
READING AND NO OUTDOOR CLUTTER ON ANY FLOOR. Both the same brief as
9007-9012. 9013, on DC 0.120.0 / Lot 0.56.0 / LF 0.74.0: 0 interventions,
0 retries, 0 unattributed changes, all stages succeeded, export exit 0,
11 minutes (09:45 -> 09:56); lot `bank_tower_a01` / freight_terminal_a01
/ funeral_home_a03; the placement gate OK 165/165, the dressing 2,995
pieces with 0 inside any footprint (601 refused as `inside building`);
and `module_pose_census` OFF THE ENGINE: 6 wall remainders `across` on
the bank -- the writer's rotation was the transpose of the engine's, so
0.120.0 had turned the pieces across the other way, while the gate,
summing extents the same wrong way, agreed with the wrong scene (item
18). DC 0.120.1 within the hour. 9014, on DC 0.120.1: 0 interventions, 0
retries, 0 unattributed changes, every tool repo clean at --begin, all
stages succeeded, export exit 0, 12 minutes (10:05 -> 10:17); lot
`bank_branch_a02` / strip_retail_a02 / large_warehouse_a01 -- the sibling
of 9012's shell, with the same `int_0_1_seg1` beside the same doorway;
placement gate OK 130/130; census off the engine on the bank: 231
standing, 0 across (strip_retail_a02: 65 standing, 0 across, 1 spun, a
pre-existing row to look at); dressing 2,708 pieces, 0 inside a footprint,
489 refused as inside a building; `look_shots` at the walker's spot from
both rooms: the wall beside the doorway is flush, and the lobby carpet
carries nothing. The tenth and eleventh zeros; 9013's package is not one
to walk. Logs and journals: `docs/cold_runs/cold_9013/`, `cold_9014/`;
walk copy `_runs/walk_export_bank_block_001` is 9014's. Previously: COLD
RUN 9012 SCORED ZERO ON THE
BANK BRIEF AND SHIPPED THE TELLER LINE AS A GLASS BARRIER WITH SIX
STATIONS, THE WALKER'S FEEDBACK ANSWERED IN A PACKAGE THE SAME DAY."""))

R.append(("""*STATUS: NARROWED 2026-09-12 (late) -- THE WALKER WAS RIGHT ABOUT THE
ROTATED PIECES, THE CENSUS WAS BLIND TO THEM, AND A GATE HAD BEEN SAYING SO
IN EVERY COLD PACKAGE SINCE 9001.""",
"""*STATUS: NARROWED 2026-09-12 (night) -- THE FIX BELOW WAS HALF WRONG AND
THE ENGINE CAUGHT IT IN THE NEXT COLD RUN; THE HALF THAT STANDS IS THE
FIT. DC 0.120.0 (the status below) rewrote `godot_basis` on the reading
that its nine numbers were the placed axes and the old product was "scale
in world axes after the rotation". They are Godot's ROWS (`basis.rows[i]
[j]` is what the text format writes), and read as rows the 0.81.0 numbers
had been `Ry(-t) x Scale_local` all along: the code right, the docstring
wrong, and the fins had ONE cause -- the fit that tied on the unscaled
unit cube and answered 0. 0.120.0 transposed the product and cold run
9013 shipped the remainders across their walls the other way. What caught
it: `module_pose_census` reads world AABBs OFF THE ENGINE and reported 6
`across` on bank_tower_a01, while `verify_placement` -- writer and checker
sharing one convention, and summing extents by columns where the engine
sums by rows -- said 165 of 165 sat. Two instruments disagreed; the engine
is the one that is right by definition, and the recomposed 9013 bank read
195 standing / 0 across under 0.120.1 before 9014 was run. DC 0.120.1:
the numbers restored and named for what they are, `placed_extent()`
summing by rows in the fit and the gate, the fit given the scale kept.
THE LESSON FOR THIS ITEM'S INSTRUMENT SCORE: a checker that shares the
writer's convention measures the writer, not the level. The census counts
because it asks the engine. Cold run 9014, the walker's spot, both rooms:
flush (item 17). Previously: THE WALKER WAS RIGHT ABOUT THE
ROTATED PIECES, THE CENSUS WAS BLIND TO THEM, AND A GATE HAD BEEN SAYING SO
IN EVERY COLD PACKAGE SINCE 9001."""))


def main() -> int:
    raw = io.open(P, "rb").read()
    if b"\r\n" in raw:
        print("roadmap has CRLF endings -- stop", file=sys.stderr)
        return 1
    text = raw.decode("utf-8")
    for old, new in R:
        if text.count(old) != 1:
            print(f"anchor matched {text.count(old)} times; refusing: {old[:60]!r}", file=sys.stderr)
            return 1
    for old, new in R:
        text = text.replace(old, new, 1)
    out = text.encode("utf-8")
    io.open(P, "wb").write(out)
    print(f"wrote {len(out)} bytes ({len(raw)} before); 17, 18 updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
