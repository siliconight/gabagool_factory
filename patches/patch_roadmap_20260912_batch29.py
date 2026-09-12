"""Roadmap batch 29, 2026-09-12: cold run 9007 (item 17 REPLACE, old kept),
its lesson filed as item 149 (APPEND), and item 44's status told what 9007
could not show (REPLACE, old kept). Asserts every anchor once.
"""
import io
import sys

P = "PIPELINE_ROADMAP.md"

R = []

R.append(("""*STATUS: NARROWED 2026-09-11 -- COLD RUN 9006 SCORED ZERO ON THE SAME BRIEF
AS 9005 THROUGH FOUR TOOLS THAT MOVED THAT DAY, THE FOURTH ZERO IN THE
PROJECT AND THE FIRST WHOSE INPUT WAS A RE-RUN ON PURPOSE.""",
"""*STATUS: NARROWED 2026-09-12 -- COLD RUN 9007 SCORED ZERO ON THE BANK BRIEF
OF 8001 AND DELIVERED A BANK BLOCK WITH NO BANK IN IT, WHICH IS THE FIFTH ZERO
AND THE CLEAREST CASE YET THAT ZERO IS NOT THE NUMBER. `bank_block_001`,
archetype `urban_bank`, three buildings from the lot library, theme
`delco_1997`, crew 4, on DC 0.117.0 / Zoo 0.61.0 / LF 0.72.1 / Lux 0.33.0
/ Pixelcoat 0.28.0: 0 interventions, 0 retries, 0 unattributed changes,
every tool repo clean at --begin, all stages succeeded, export exit 0, 30
minutes (04:27 -> 04:57; the art layer took 64 s because every kit,
pack and fixture stage cache-hit from the library's earlier builds). The
lot was `arena_a03`, `clinic_a01`, `landmark_hall_a01`. `pick_lot` took a
seed and a count and nothing about the brief -- item 149, fixed the same
hour in LF 0.73.0. The run was meant to show item 44's species routing on
a bank's desks and could not, because there was no bank: its one hinted
volume was the clinic's 6 m reception, built as the box and said so. Zero
interventions with the wrong building is the failure `_preset_for` was
written against, one level up, and the counter did not see it: the hash
counts what changed in the tools, not whether the tools built the brief.
Log and journal: `docs/cold_runs/cold_9007/`; walk copy
`_runs/walk_export_bank_block_001`. Cold run 9008 re-runs the brief on
0.73.0. EARLIER STATUS, KEPT VERBATIM: NARROWED 2026-09-11 -- COLD RUN
9006 SCORED ZERO ON THE SAME BRIEF
AS 9005 THROUGH FOUR TOOLS THAT MOVED THAT DAY, THE FOURTH ZERO IN THE
PROJECT AND THE FIRST WHOSE INPUT WAS A RE-RUN ON PURPOSE."""))

R.append(("""*STATUS: NARROWED 2026-09-12 -- THE WIRE AND THE EXACT FIT SHIPPED (STEPS 1
AND 2 OF THE MEASURED PLAN), BUILT THROUGH BLENDER, NOT YET IN A PACKAGE.""",
"""*STATUS: NARROWED 2026-09-12 -- THE WIRE AND THE EXACT FIT SHIPPED (STEPS 1
AND 2 OF THE MEASURED PLAN), BUILT THROUGH BLENDER; THE FIRST PACKAGE RUN TO
SHOW IT (COLD 9007) HAD NO BANK IN ITS BANK BLOCK (ITEM 149), AND 9008 IS
THE RE-RUN. On 9007's three shells the routing did what it says: the
clinic's `reception_desk` (6.0 x 0.8 x 1.1, hinted `counter`) fell back to
the box with "width 6.00 outside 0.80..4.00" in the kit index; arena and
landmark hall carry no hinted volumes. `chair_row` (6.0 x 0.8 x 0.9) got
no hint at all because `chair` itself is not in the keyword table (seat,
bench, waiting are) -- one word, for the next DC change that rebuilds the
library. Dry-planned over the rebuilt library, 43 manifests with hinted
volumes: 193 hinted slots, 174 built as the box, 11 desk and 5 counter
modules become species; the bank shells (`bank_branch_a02`, `_a03`,
`bank_job`) each gain one real desk. Continued, unchanged:"""))

APPEND = """
*STATUS: NARROWED 2026-09-12 -- FOUND BY COLD RUN 9007, FIXED IN LEVEL
FACTORY 0.73.0 THE SAME HOUR, NOT YET RUN*

**149. The varied lot ignores the brief's archetype: a bank block had no
bank in it.** Cold run 9007 (item 17): `archetype: urban_bank`,
`building_count: 3`, `lot_library` set, and `building_library.pick_lot`
drew `arena_a03`, `clinic_a01`, `landmark_hall_a01` -- it takes a seed
and a count and nothing about the brief, and item 37's fix ("three
DISTINCT archetypes") was satisfied by three of the wrong ones. Every
stage passed and the deliverable was a bank block without a bank, which is
exactly the failure `adapters.deli_counter._preset_for` refuses for the
single-shell path ("a wrong-but-plausible building is the worst failure
this adapter can produce") reappearing on the lot path, where nothing
refused it. LF 0.73.0: `anchor_families(entries, archetype)` names the
library families that ARE the archetype by its parts (`bank`, `bank_*`,
`urban_bank` -> `bank_branch` / `bank_tower` / `bank_job`); `pick_lot` and
`lot_for` seat one of those first, drawn by the same stream so five
candidates still get five lots and a seed still means one thing, and draw
the rest as before; no anchor, or none in the library, is the old draw
byte for byte, and the planner prints which. On this library a
`county_hospital` brief still gets no anchor -- the library has no
hospital family; the transients are excluded by design (item 73) -- and
that is said rather than guessed. **WHAT WOULD CLOSE THIS:** cold run 9008
placing a bank first on the same brief; then the question item 105 already
holds about where the anchor stands on the site.
"""


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
    if "\n**149. " in text:
        print("item 149 already present", file=sys.stderr)
        return 1
    for old, new in R:
        text = text.replace(old, new, 1)
    text = text.rstrip("\n") + "\n" + APPEND.rstrip("\n") + "\n"
    out = text.encode("utf-8")
    io.open(P, "wb").write(out)
    print(f"wrote {len(out)} bytes ({len(raw)} before); 17, 44 replaced; 149 filed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
