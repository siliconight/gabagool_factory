"""Roadmap batch 46, 2026-09-13: cold run 9026 refused by the preflight on
the wrong storey (17 REPLACE, old kept; LF 0.78.1), and the waiting places
in the tools (153 REPLACE, old kept; Zoo 0.68.1, Lot 0.64.0). Asserts every
anchor.
"""
import io
import sys

P = "PIPELINE_ROADMAP.md"

R = []

R.append(("""*STATUS: NARROWED 2026-09-13 (late) -- COLD RUN 9025 SCORED ZERO WITH
THE STREET PARKED IN.""",
"""*STATUS: NARROWED 2026-09-13 (night) -- COLD RUN 9026 WAS NOT A ZERO: THE
LASER TAG PREFLIGHT REFUSED THE FIRST SEED ON THE WRONG STOREY, AND THE
EXPORT GATE HELD. The bank brief on Zoo 0.67.3 / Lot 0.63.0 / LF 0.78.0:
0 interventions, 0 retries, 0 unattributed changes, but the first seed's
`laser_tag_evaluate` failed at pre-flight -- "LT_ObjectivePoint is inside
solid geometry" -- the driver selected that seed by rule, art ran on an
eliminated candidate, and `export` refused it (exit 2) with the blocker
named. THE INSTRUMENT WAS WRONG, NOT THE LEVEL: seed 9026 put the deli
(`deli_a01`) at b2 with its objective in the basement vault at y = -3.0;
`spawn_placement` builds ONE heightfield around the crew spawn's floor and
judged the marker by the ground-floor cell above it, which the stockroom's
shelving blocks; the walktest on the same candidate, which bakes every
storey, walked all twelve anchors including that one (proxy_10, snapped
1.0 m). Basement objectives had passed the same field on 9019, 9020, 9022
and 9024 only because the cell above happened to be open floor. LF 0.78.1:
a marker under the field's surface by more than a climb, or over it by
more than a body, is "on a storey this field does not see" -- reported as
`LT_STOREY_UNSEEN` with both heights, never refused; a marker on the held
storey inside a solid still refuses (tested both ways). What held: the
export gate (0.76.0) refused a package with an open blocker, as built.
The waiting places (item 153) landed in Zoo 0.68.1 and Lot 0.64.0 on a
local Blender kit build (5 modules, 0 failed, the tree `pass`); cold run
9027 measures them with the preflight fix. Log and journal:
`docs/cold_runs/cold_9026/`. Previously: COLD RUN 9025 SCORED ZERO WITH
THE STREET PARKED IN."""))

R.append(("""*STATUS: NARROWED 2026-09-13 (late) -- CARS ARE PARKED IN THE KERB LANES,
AND LOT READS THE KIT INDEX BEFORE IT STANDS A MODULE.""",
"""*STATUS: NARROWED 2026-09-13 (night) -- THE WAITING PLACES ARE IN THE
TOOLS: A TREE BETWEEN THE LAMPS, A BUS STOP PER ROAD. Zoo 0.68.0/0.68.1:
`bus_shelter` (four posts under a flat roof, glazed back and ends from a
knee-high sill, open along the kerb; posts and panes collide, the roof
does not), `bench` (three slats on two cast ends), `street_tree` (a
tapered trunk from a 1.2 m iron grate, a two-frustum crown in the
vegetation grammar filling the slot's width at its waist; ONLY THE TRUNK
collides). Lot 0.64.0: `site_furniture` plants a tree halfway between
every two lamp stations on the outer half of each band, and stands one bus
stop per road -- shelter open to the kerb, bench inside against its back,
a stop sign a metre before -- on the kerb the buildings face
(`_facing_kerb`), at the midpoint of the longest stretch between
crossings, nudged clear of what already stands (`_free`). A tree's SLOT is
its crown (4 x 4 x 6, what Zoo builds) and its FOOTPRINT is its grate
(1.2 x 1.2, what the greybox draws and the navmesh carves): the greybox
over-blocks the trunk by the grate's margin and never under-blocks it.
Measured on a local kit build: bench 220 tris and shelter 352 built as
`warn` against prop's 200-tri budget, which Lot 0.63.0 read as "not pass"
-- the species carry their own budgets now and Lot stands a `warn` row
(an advisory, not a failure). The tree is the honest first state of the
alpha-cutout foliage: a faceted volume, not cards. Cold run 9027 measures
all of it. WHAT REMAINS: the marking texture (drafted: a Pixelcoat
`road_paint` kind with a cutout alpha, Lot's quads wearing it as a
scissor decal tinted by the marking's colour); intersections (drafted: a
road that ends on another begins its slab at that road's band edge, a
crossing is a box with crosswalks at its ends, the leg that ends is the
one that stops); the cover planner's truck-in-the-road as the exception.
Previously: CARS ARE PARKED IN THE KERB LANES,
AND LOT READS THE KIT INDEX BEFORE IT STANDS A MODULE."""))


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
