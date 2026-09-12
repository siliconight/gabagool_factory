"""Roadmap batch 45, 2026-09-13: cars parked in the kerb lanes and the kit
index's verdict read (153 REPLACE, old kept; 17 REPLACE, old kept, cold
run 9025). Asserts every anchor.
"""
import io
import sys

P = "PIPELINE_ROADMAP.md"

R = []

R.append(("""*STATUS: NARROWED 2026-09-13 (evening) -- THE STREET IS A MODEL, THE PAINT
IS ON THE ROAD AND THE KERB LINE STANDS ON THE SIDEWALKS, ALL IN COLD
PACKAGES.""",
"""*STATUS: NARROWED 2026-09-13 (late) -- CARS ARE PARKED IN THE KERB LANES,
AND LOT READS THE KIT INDEX BEFORE IT STANDS A MODULE. Lot 0.63.0:
`site_streets` gains parking lanes -- 6 m bays in a 2.2 m lane along each
kerb of a road with sidewalks, none within 6 m of a crossing or over a
kerb cut, the edge lines moved to the driving lanes' edge and every bay
edge ticked -- and `site_parking` parks a `simple_car` in 60 percent of
the bays by a stable hash, along the road, clear of every marker and of
everything already standing by the cover planner's own rules. A parked
car is cover and the same prop-slot record. Cold run 9025 (item 17): 23
cars parked, 22 kerb-line pieces, the cover planner needing only one
truck and one container with the street full; 34 modules standing; from
the sidewalk, a row of cars along the kerb with the bay ticks between
them. THE VERDICT, READ: Lot stood a module by file, so 9024 shipped the
lamp at 6.18 m against a 6.00 m slot with its index row `fail`; 0.63.0
reads `site_kit.built.json` and a row that is not `pass` keeps its box
under `LOT_COVER_MODULE_FAILED`. Measured on 9025: 13 lamp boxes stood
where 13 lamps had, which is the honest picture of a recipe that does
not fit its slot -- the streetlight floats its head above the lamp point
it puts at +h/2 for the light-anchor pipeline. Zoo 0.67.3 gives the
recipe both placements: an exact-fit plan puts the head's top at +h/2 and
the lamp point under the lens; the fixtures pipeline is unchanged. WHAT
REMAINS: the bus stop and the tree; a marking texture in Pixelcoat so the
paint is a decal; intersections; and the cover planner's own pieces are
now mostly the parked cars' job, so its truck-in-the-road should become
the exception it was meant to be. Previously: THE STREET IS A MODEL, THE PAINT
IS ON THE ROAD AND THE KERB LINE STANDS ON THE SIDEWALKS, ALL IN COLD
PACKAGES."""))

R.append(("""*STATUS: NARROWED 2026-09-13 (evening) -- COLD RUNS 9023 AND 9024 SCORED
ZERO: THE PAINT, THEN THE KERB LINE.""",
"""*STATUS: NARROWED 2026-09-13 (late) -- COLD RUN 9025 SCORED ZERO WITH
THE STREET PARKED IN. The bank brief on Lot 0.63.0 / Zoo 0.67.2: 0
interventions, 0 retries, 0 unattributed changes, every tool repo clean
at --begin, all stages succeeded, 0 blockers, export exit 0, 20 minutes
(16:53 -> 17:13); 23 cars parked in the kerb lanes, 22 kerb-line pieces,
1 truck and 1 container from the cover planner, 34 modules standing, 13
lamp boxes kept by the index's `fail` verdict (item 153); the walktest's
stuck counts (player 2, enemy 2) unchanged with 57 more colliders on the
street. The seventeenth zero. Log and journal: `docs/cold_runs/cold_9025/`;
walk copy `_runs/walk_export_bank_block_001` is 9025's. Previously: COLD
RUNS 9023 AND 9024 SCORED
ZERO: THE PAINT, THEN THE KERB LINE."""))


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
    print(f"wrote {len(out)} bytes ({len(raw)} before); 153, 17 updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
