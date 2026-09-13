"""Roadmap batch 52, 2026-09-13: cold run 9032 zero with the crown reading as
a canopy (17 REPLACE, old kept; 153 REPLACE, old kept). Asserts every
anchor.
"""
import io
import sys

P = "PIPELINE_ROADMAP.md"

R = []

R.append(("""*STATUS: NARROWED 2026-09-13 (night) -- COLD RUN 9031 SCORED ZERO WITH THE
CROWN AS CARDS, THE PAINT IN PATCHES AND THE CARS BEFORE THE COVER.""",
"""*STATUS: NARROWED 2026-09-13 (night) -- COLD RUN 9032 SCORED ZERO WITH THE
CROWN READING AS A CANOPY. The bank brief on Zoo 0.69.2 / Pixelcoat
0.32.1 / Lot 0.66.1: 0 interventions, 0 retries, 0 unattributed changes,
every tool repo clean at --begin, all stages succeeded, 0 blockers, export
exit 0, 15 minutes (19:45 -> 20:00); every site-kit module `pass`, 3
cover pieces with the cars parked first. The twenty-second zero. Frames
(`docs/cold_runs/cold_9032/frames/`): one foliage tile per card with the
elliptical cutout -- the crown's edge is now the clusters' edge, from the
kerb and from across the street. Residue seen on the frames: the cards
are 2 cm boxes, and their thin side faces are projected on other axes
where the cutout does not cut them, so hairlines poke above a crown; the
card should be a plane. Previously: COLD RUN 9031 SCORED ZERO WITH THE
CROWN AS CARDS, THE PAINT IN PATCHES AND THE CARS BEFORE THE COVER."""))

R.append(("""*STATUS: NARROWED 2026-09-13 (night) -- THE FOUR RESIDUES ARE IN A COLD
PACKAGE (9031).""",
"""*STATUS: NARROWED 2026-09-13 (night) -- THE CROWN READS AS A CANOPY (9032):
ONE FOLIAGE TILE PER CARD, THE CARD'S EDGE THE CANOPY'S. Pixelcoat 0.32.1
(a cutout may name an ellipse; `foliage_delco` at 4 m per tile) and Zoo
0.69.2 (four vertical cards, the diagonal pair root-two longer so every
card fits the slot, UVs about the crown's centre). Measured on 9032's
frames from the kerb and from across the street. Residue: the cards'
thin side faces show as hairlines above a crown (item 17); an X
crossing's slabs are handled but the spec makes only a T; parking lanes
and the kerb line stop at the plate's roads, not at the courtyards or
the paths. Previously: THE FOUR RESIDUES ARE IN A COLD
PACKAGE (9031)."""))


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
    print(f"wrote {len(out)} bytes ({len(raw)} before); 17, 153 updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
