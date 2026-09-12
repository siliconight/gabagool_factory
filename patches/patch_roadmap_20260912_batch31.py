"""Roadmap batch 31, 2026-09-12: cold run 9009 -- item 17 REPLACE (old
kept), item 149 CLOSED (REPLACE, old kept), item 44 REPLACE (old kept).
Asserts every anchor once.
"""
import io
import sys

P = "PIPELINE_ROADMAP.md"

R = []

R.append(("""*STATUS: NARROWED 2026-09-12 -- COLD RUN 9007 SCORED ZERO ON THE BANK BRIEF
OF 8001 AND DELIVERED A BANK BLOCK WITH NO BANK IN IT, WHICH IS THE FIFTH ZERO
AND THE CLEAREST CASE YET THAT ZERO IS NOT THE NUMBER.""",
"""*STATUS: NARROWED 2026-09-12 -- COLD RUN 9009 SCORED ZERO ON THE BANK BRIEF,
THIRD TRY, WITH A BANK IN EVERY CANDIDATE'S LOT AND THE FIRST DIEGETIC PROP
IN A SHIPPED PACKAGE. Same `bank_block_001` brief as 9007 and 9008, on LF
0.73.1: 0 interventions, 0 retries, 0 unattributed changes, every tool
repo clean at --begin, all stages succeeded, export exit 0, 16 minutes
(05:23 -> 05:40). The anchored lot held in all three draws --
`bank_tower_a03` / auto_shop_a02 / warehouse_a01 (seed 9009, shipped),
`bank_branch_a03` / casino_a01 / strip_club_a01 (9110), `bank_tower_a02`
/ deli_a03 / parking_garage (9211) -- and the planner's guard stayed
silent. Item 44 in the package: `auto_shop_a02`'s `office_desk` (1.8 x
0.9 x 0.8) is `prop_desk_delco_1997_02_w180_d90_h80`, a desk, PASS, and a
`look_shots --station` at it in the walk copy shows a wooden pedestal desk
with drawers on the upper floor of the shop. The bank tower itself carried
one unhinted 2.6 x 0.6 x 1.0 prop and no desk that fits; the warehouse's
three racks and the shop's parts rack fell back to the box as runs, said
in the index. The sequence 9007 -> 9008 -> 9009 is the item's own thesis
in three runs: zero interventions each time, and only the third built
the brief. Log and journal: `docs/cold_runs/cold_9009/`; walk copy
`_runs/walk_export_bank_block_001` (this overwrites 9007's). EARLIER
STATUS, KEPT VERBATIM: NARROWED 2026-09-12 -- COLD RUN 9007 SCORED ZERO
ON THE BANK BRIEF
OF 8001 AND DELIVERED A BANK BLOCK WITH NO BANK IN IT, WHICH IS THE FIFTH ZERO
AND THE CLEAREST CASE YET THAT ZERO IS NOT THE NUMBER."""))

R.append(("""*STATUS: NARROWED 2026-09-12 -- 0.73.0 ANCHORED ONE OF THREE DRAWS AND COLD
RUN 9008 CAUGHT IT; 0.73.1 MAKES THE LOT ONE RULE READ OFF THE BRIEF; 9009
RUNNING.""",
"""*STATUS: CLOSED 2026-09-12 -- COLD RUN 9009 PLACED A BANK FIRST IN ALL
THREE CANDIDATES' LOTS ON THE SAME BRIEF THAT GOT NONE IN 9007:
`bank_tower_a03`, `bank_branch_a03`, `bank_tower_a02` lead the three draws,
the other two places vary by seed as before (auto_shop / warehouse, casino
/ strip_club, deli / parking_garage), the planner's disagreement guard
stayed silent, the art layer ran to completion and the export is clean
(LF 0.73.1, `lot_for_brief`). What remains is item 105's question, not
this one's: where the anchor stands on the site. EARLIER STATUS, KEPT
VERBATIM: NARROWED 2026-09-12 -- 0.73.0 ANCHORED ONE OF THREE DRAWS AND
COLD RUN 9008 CAUGHT IT; 0.73.1 MAKES THE LOT ONE RULE READ OFF THE BRIEF;
9009 RUNNING."""))

R.append(("""*STATUS: NARROWED 2026-09-12 -- THE WIRE AND THE EXACT FIT SHIPPED (STEPS 1
AND 2 OF THE MEASURED PLAN), BUILT THROUGH BLENDER; THE FIRST PACKAGE RUN TO
SHOW IT (COLD 9007) HAD NO BANK IN ITS BANK BLOCK (ITEM 149), AND 9008 IS
THE RE-RUN.""",
"""*STATUS: NARROWED 2026-09-12 -- STEPS 1 AND 2 SHIPPED AND NOW IN A COLD
PACKAGE: cold run 9009's `auto_shop_a02` carries `office_desk` as
`prop_desk_delco_1997_02_w180_d90_h80`, a desk, and the walk copy's frame
shows it. The same package says the rest of the item's number out loud:
`parts_rack` (1.0 x 5.0 x 1.8) and the warehouse's `rack_a/b/c` fell back
from `shelving` as runs, and `tool_bench` (3.0 x 1.0 x 1.0) was hinted
`chair` because "bench" is a chair keyword -- two words for the keyword
table (`chair` itself, and `bench` only when not `work`/`tool`), with the
next Deli Counter change that rebuilds the library. Step 3, the bays
mode, is unchanged. Previously: THE WIRE AND THE EXACT FIT SHIPPED (STEPS
1 AND 2 OF THE MEASURED PLAN), BUILT THROUGH BLENDER; THE FIRST PACKAGE
RUN TO SHOW IT (COLD 9007) HAD NO BANK IN ITS BANK BLOCK (ITEM 149), AND
9008 IS THE RE-RUN."""))


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
    print(f"wrote {len(out)} bytes ({len(raw)} before); 17, 149, 44 updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
