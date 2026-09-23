"""Roadmap items 173 and 174, both out of the Quake III Arena bot thesis
(van Waveren 2001) read on 2026-09-23.

Anchored on item 172's close, which must match exactly once.
"""
from pathlib import Path

TARGET = Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

ANCHOR = """is where that division is supposed to be written down rather than assumed.
"""

ITEMS = """
*STATUS: OPEN 2026-09-23 -- THE INSTRUMENT EXISTS AND CANNOT YET BE A GATE.
`tools/walkable_edge.gd` finds the class (121 unguarded cells at the stairwell
the walker stepped off, 2.90 m at floor level) and reports 5,897 drop edges on
a clean package, of which 1,024 are the deliberately open sides of staircases.
A declaration is what separates the two.*

**173. A drop is either guarded or declared, and today nothing declares one.**
From van Waveren's Quake III Arena bot thesis (2001), chapter 6, read
2026-09-23.

**What the paper supplies.** Its Area Awareness System classifies every
connection between two areas as one of about twelve REACHABILITIES, and one of
them is `walk off ledge`: an explicit, ONE-WAY link created wherever the drop
between two ground edges exceeds the step height. Its own words: "The player
will not be able to walk back up, the player will have to jump back up or may
not be able to get back up directly at all." The router therefore knows the
drop exists, knows it is deliberate, and knows it does not work in reverse.

**Why that is the missing piece here.** `tools/walkable_edge.gd` (built the
same day, roadmap 168's sibling) measures whether a body can walk off an edge
with nothing above step-over height between it and the fall. On cold run
9072's package it found the walker's stairwell independently, from physics:
121 unguarded cells, the floor-level ones reading a 2.90 m drop. It also found
5,897 unguarded edges in total. Splitting them by whether the sky is overhead
cut it to 2,419, and 1,024 of THOSE stand at mid-flight heights dropping 0.8 m
-- the open sides of staircases, which `agent_contract.json` already records as
ordinary architecture after lateral containment was proposed and REJECTED with
a measurement. So the instrument is correct and unusable as a gate: it cannot
tell a fall nobody meant from a drop somebody chose.

**The rule the paper implies, which has a real zero:**

    every drop edge is either GUARDED, or DECLARED as a one-way reachability

An edge that is neither is a defect -- a missing guard or a missing link -- and
that is a gate that can refuse. Declared drops stop reporting once, rather than
being re-triaged by hand on every run.

**Owners.** Deli Counter and Lot -- emit a `walk_off_ledge` link where the
geometry makes an intentional drop, which they already know because they cut
the opening or placed the kerb. Dispatch -- carry it in
`navigation_hints.json`'s `links[]`, which exists as of 0.5.0 and was built for
exactly this shape (ladders were the first type; this is the second). Level
Factory -- promote `walkable_edge` from a tool to an export gate once something
declares.

**What else the taxonomy is a checklist for**, against what this pipeline
actually builds -- teleporters, jump pads and rocket jumps are not this game:

    walk / crouch          the baked mesh; `crouch_height_m` 1.2 exists
    walk off ledge         every drop in every level, none declared
    barrier jump           `max_step_up_m` 0.5
    ladder                 SHIPPED, Dispatch 0.5.0, item 172
    elevator / bobbing     `gameplay.json` carries a `platforms` key

**Also worth keeping from that chapter, and deliberately NOT adopted:** its
per-reachability TRAVEL TIME is the same idea as the per-type `cost` this
pipeline already ships on a ladder link, which is a small independent
confirmation that the shape is right. Its clusters-and-portals routing is
already latent here too -- `navigation_hints.json` bridges Deli Counter
interiors to Lot exteriors within `bridge_radius` and flags them
`bridged: true`, which is a portal by another name -- but nothing has measured
a routing cost problem, so building the hierarchy now would be optimising
toward a number nobody has taken. The AAS ITSELF is not worth porting: its
brush expansion and area subdivision are what Godot's Recast bake already does.

*STATUS: OPEN 2026-09-23 -- SMALL, AND HELD FOR ONE ANSWER. The aperture is
derivable today (a `slot_ref` resolves to a node in `site.tscn` and the GLBs)
but not declared, so a consumer re-derives what this pipeline computed.*

**174. An opening's aperture is not declared, so the layer that adds the door
has to re-derive it.** Raised with the walker, 2026-09-23.

**WHAT THIS PIPELINE ACTUALLY SHIPS, corrected twice in the conversation that
produced this item and worth stating precisely because both corrections
mattered.** It does not ship doors. It ships OPENINGS where doors will be
added, outside Level Factory, by a networked gameplay layer. Measured on a
`doorway_delco_1997_01_w125` module: two parts, `Doorway-colonly` and
`Doorway_brick_delco_1997`, and the visible one fills 0.411 of its own
bounding box -- 1.528 m2 of frame around 2.192 m2 of hole, about 1.05 x 2.09 m.
A frame, no leaf. (The bounding box alone says 1.24 x 3.00 and would have
supported the opposite conclusion; measuring the mesh rather than its box is
the same correction roadmap 168's occluder work turned on.)

**So the baked navmesh from a package is the ALL-OPENINGS-PASSABLE state**, and
that is the right base: it is maximal connectivity, and a door layer only ever
subtracts from it. `interactives.json`'s `default: "closed"` describes the door
that will be added, not the geometry that shipped -- a reader could take it for
the latter.

**What is missing is one geometric fact.** An anchor carries a stable id, a
`slot_ref`, a transform, `states` and `transitions`. It does not carry the
aperture. `ext_0_S_open0` does resolve -- it names a node in `lot/<building>/
site.tscn` and in the GLBs, 9 files in the package mention it -- so a consumer
CAN get there by walking the scene and reading bounds. That is this pipeline
asking somebody to re-derive a number it already computed, which is the same
shape as item 172's dropped nav link.

**`breach_wall` is the case that matters most.** `intact -> breached`,
`reversible: false`, `breach_class: soft_wall`. Breaching ADDS a route the
baked mesh does not contain, so the gameplay layer has to tell navigation that
something new exists -- and the aperture is precisely what it needs to say it.
A door only ever subtracts; a breach adds.

**Owners.** Deli Counter -- put the aperture on the interactive record it
already derives (`interactives.derive_interactive` computes the stable id from
the authored opening and its wall, so the opening is in hand at that moment).
Dispatch -- carry it through `interactives.json`.

**HELD FOR ONE ANSWER before building:** whether the runtime blocks a closed
door with a `NavigationObstacle3D`, toggles a region, or re-bakes a tile. The
three want slightly different payloads, and guessing would ship a field nobody
uses. Nothing else in this item depends on that answer.

**Not in scope, and recorded so it is not re-litigated:** the door's behaviour,
its replication, and when navigation is updated are the gameplay layer's.
`source: "inferred"` on these anchors is worth a separate look -- the pipeline
inferred that an opening is door-shaped, and a networked implementation would
be built on that inference.
"""


def main() -> None:
    data = TARGET.read_bytes()
    if b"\r\n" in data:
        raise SystemExit("REFUSED: roadmap is LF; found CRLF")
    text = data.decode("utf-8")
    hits = text.count(ANCHOR)
    if hits != 1:
        raise SystemExit(f"REFUSED: anchor matched {hits} times")
    if not text.endswith(ANCHOR):
        raise SystemExit("REFUSED: anchor is not the end of the file")
    before = len(data)
    out = (text + ITEMS).encode("utf-8")
    if b"\r\n" in out:
        raise SystemExit("REFUSED: would write CRLF")
    TARGET.write_bytes(out)
    print(f"PIPELINE_ROADMAP.md: {before} -> {len(out)} bytes "
          f"(+{len(out) - before}), {out.count(10)} lines, LF")


if __name__ == "__main__":
    main()
