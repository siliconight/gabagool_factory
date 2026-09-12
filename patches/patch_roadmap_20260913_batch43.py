"""Roadmap batch 43, 2026-09-13: the street in a cold package -- 153 REPLACE
(old kept) and 17 REPLACE (old kept) for cold run 9022. Asserts every anchor.
"""
import io
import sys

P = "PIPELINE_ROADMAP.md"

R = []

R.append(("""*STATUS: OPEN 2026-09-13 -- FILED FROM THE WALKER'S QUESTION AFTER THE SPECIES
COVER LANDED; THE VOCABULARY AND ITS OWNERS ARE IN THE ITEM, NOTHING BUILT*""",
"""*STATUS: NARROWED 2026-09-13 -- STEP ZERO IS IN A COLD PACKAGE: THE
GENERATED SITE HAS A ROAD WITH SIDEWALKS, AND THE KERB IS CUT WHERE THE
CREW CROSSES AND A WALL EVERYWHERE ELSE. Level Factory 0.78.0's
`_street_for` puts one 10 m road with 3 m sidewalks along the plate's
south edge, the full plate width, in the band below the southernmost
footprint face -- deepening the plate (9022: 69 -> 99 m) rather than
squeezing the road -- and a 4 m spur from a metre clear of each
building's south face to the road's centre line. Lot's existing
`_kerb_crossings` did the rest: cold run 9022's package carries `road_0`,
two sidewalk bands and three kerb cuts, one per spur, on the sidewalk the
buildings face; Lot 0.60.0 skins the strip and the cuts with the `road`
pack and the bands with `sidewalk`. Zero interventions, no blocker, the
walktest and Laser Tag routed across it (item 17). The frames from the
sidewalk and at a crossing: the kerb is a kerb, the cut is a cut, and the
road reads by its kerbs alone -- the road and the lot wear one asphalt
grammar, so the markings are what will make it a street, which is the
next step of this item as filed. Previously: OPEN 2026-09-13 -- FILED
FROM THE WALKER'S QUESTION AFTER THE SPECIES
COVER LANDED; THE VOCABULARY AND ITS OWNERS ARE IN THE ITEM, NOTHING BUILT*"""))

R.append(("""*STATUS: NARROWED 2026-09-13 (small hours) -- FOUR RUNS FOR THE SPECIES
COVER: 9018 REFUSED AT EXPORT ON A SEALED SPAWN, 9019 A ZERO THAT LOST ITS
MODULES ONE STAGE ON, 9020 A ZERO WITH THE CLUTTER BUILD RED, 9021 THE
ZERO WITH A TRUCK AND A CONTAINER ON THE LOT.""",
"""*STATUS: NARROWED 2026-09-13 -- COLD RUN 9022 SCORED ZERO WITH A STREET
IN THE PACKAGE. The bank brief on Lot 0.60.0 / LF 0.78.0 / Zoo 0.66.2: 0
interventions, 0 retries, 0 unattributed changes, every tool repo clean
at --begin, all stages succeeded, 0 blockers, export exit 0, 20 minutes
(15:18 -> 15:38); the plate deepened from 69 to 99 m for the road band;
`road_0` with two sidewalks and three kerb cuts, one per building's spur;
the species cover and the ground skins as before; the walktest's stuck
counts (player 1, enemy 2) no worse than 9014's (3, 3) with the kerbs in
place. The fourteenth zero. Log and journal: `docs/cold_runs/cold_9022/`;
walk copy `_runs/walk_export_bank_block_001` is 9022's. Previously: FOUR
RUNS FOR THE SPECIES
COVER: 9018 REFUSED AT EXPORT ON A SEALED SPAWN, 9019 A ZERO THAT LOST ITS
MODULES ONE STAGE ON, 9020 A ZERO WITH THE CLUTTER BUILD RED, 9021 THE
ZERO WITH A TRUCK AND A CONTAINER ON THE LOT."""))


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
