"""Roadmap batch 36, 2026-09-12: cold run 9012 -- the teller line in a
package (17 REPLACE, old kept; 44 REPLACE, old kept). Asserts every anchor.
"""
import io
import sys

P = "PIPELINE_ROADMAP.md"

R = []

R.append(("""*STATUS: NARROWED 2026-09-12 (night) -- COLD RUN 9011 SCORED ZERO ON A GAS
STATION BRIEF NEVER RUN, THE ANCHOR HELD, AND THE PUMP DID NOT SHIP BECAUSE
THE VARIANT THE ANCHOR DREW HAS NO PUMPS.""",
"""*STATUS: NARROWED 2026-09-12 (late) -- COLD RUN 9012 SCORED ZERO ON THE
BANK BRIEF AND SHIPPED THE TELLER LINE AS A GLASS BARRIER WITH SIX
STATIONS, THE WALKER'S FEEDBACK ANSWERED IN A PACKAGE THE SAME DAY. Same
brief as 9007-9010, on DC 0.119.0 / Zoo 0.65.0 / LF 0.73.1: 0
interventions, 0 retries, 0 unattributed changes, every tool repo clean
at --begin, all stages succeeded, export exit 0, 19 minutes (08:50 ->
09:09). Lot `bank_branch_a03` / cr_garage / museum_a02. The bank's kit
index: `prop_teller_line_..._w1200_d80_h240` PASS beside its filing
cabinet, desk and rooftop unit; zero fallbacks, zero alternates.
`look_shots --station` from the customer side of the walk copy: a
wooden counter, a header, six glass stations with posts between and a
service opening at the counter in each, on the lobby's carpet under a
tile grid -- the four reference photographs' shape. The ninth zero. Log
and journal: `docs/cold_runs/cold_9012/`; walk copy
`_runs/walk_export_bank_block_001` (overwrites 9010's). Previously: COLD
RUN 9011 SCORED ZERO ON A GAS
STATION BRIEF NEVER RUN, THE ANCHOR HELD, AND THE PUMP DID NOT SHIP BECAUSE
THE VARIANT THE ANCHOR DREW HAS NO PUMPS."""))

R.append(("""*STATUS: NARROWED 2026-09-12 (late) -- THE TELLER LINE IS A GLASS BARRIER
WITH A WINDOW PER STATION, FROM THE WALKER'S REFERENCES; COLD RUN 9012 IS
THE PACKAGE.""",
"""*STATUS: NARROWED 2026-09-12 (late) -- THE TELLER LINE IS IN A COLD
PACKAGE: cold run 9012's bank branch carries it as
`prop_teller_line_..._w1200_d80_h240`, PASS, and the frame from the
customer side shows six stations of glass over a wooden counter with a
service opening in each -- the references' shape, zero interventions
(item 17). What remains of this item is the eye on the re-walk (do six
2 m stations read as a bank, does the tray opening read as one), the 52
region-shaped placements that stay boxes, and the drawing itself: every
species here is boxes at the right proportions, and the recipes are where
a person makes them furniture. Previously: THE TELLER LINE IS A GLASS BARRIER
WITH A WINDOW PER STATION, FROM THE WALKER'S REFERENCES; COLD RUN 9012 IS
THE PACKAGE."""))


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
    print(f"wrote {len(out)} bytes ({len(raw)} before); 17, 44 updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
