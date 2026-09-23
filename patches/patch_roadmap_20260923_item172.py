"""Roadmap item 172: ladder off-mesh nav links are generated and then dropped
at the package boundary.

Anchored on the file's final paragraph (item 171's close), which must match
exactly once. Does NOT touch the generated index.
"""
from pathlib import Path

TARGET = Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

ANCHOR = """that terminates on a roof meets 170's missing hatch.
"""

ITEM = """
*STATUS: OPEN 2026-09-23 -- MEASURED ON A PACKAGE THAT HAS LADDERS. The link is
generated per ladder and reaches the shell's `gameplay.json`; ZERO files in the
shipped package carry it. The climb marker ships, so a player can climb and an
AI cannot path.*

**172. An AI cannot path up a ladder in a shipped package, because the off-mesh
link the pipeline generates never leaves Deli Counter.** Raised by the walker,
2026-09-23, asking whether the levels have navmesh off-mesh links at all.

**THE CAPABILITY EXISTS AND IS BETTER THAN THE QUESTION ASSUMED.**
`ladder._nav_link` (`ladder.py:434`) emits one per ladder, and its docstring
names the distinction exactly: "an explicit off-mesh nav-link (NOT a baked
walkable slope)". It carries more than a pair of endpoints:

    id, start_position, end_position, bidirectional
    cost                  per ladder_type (fixed_vertical, ship, caged, ...)
    agent_types           ["player", "ai_humanoid"]
    required_capability   "climb"
    access_state          locked_gate / locked_hatch -> "locked"
    reservation_state     occupancy, which a multiplayer game needs

`_traversal_component` beside it carries the mount and dismount triggers and
the animation profile, and `audit_specs.py` already REFUSES a ladder whose
nav_link is zero-length. The bake half is equally real: `agent_contract.json`
pins `agent_radius_m` 0.40, `agent_height_m` 1.80, `agent_max_climb_m` 0.15,
`cell_height_m` 0.15 and `agent_max_slope_deg` 55, each with a written
derivation -- the climb value is exactly one voxel because Godot floors it to
whole voxels and warns that it does. `nav_gate.py` bakes a navmesh per shell in
Godot and tests stair traversal, island connectivity and marker reachability;
that is the instrument that identified `foundry_heist_vertical`'s basement as a
disconnected island the same day.

**WHAT IS LOST, measured on `walk_export_club_block_009` (deli_a03, which
carries `night_deli_ladder_0`) rather than on a package with no ladders in it
-- the first attempt at this measurement used one and proved nothing:**

    nav_link in the shell's gameplay.json         yes
    nav_link anywhere in the shipped package      0 files
    LADDER_0 / LADDER_1 markers in site.tscn      yes
    ladder entries in interactives.json (35)      0
    navigation_hints.json                         "navmesh": "bake_required",
                                                  nodes + edges, NO links

So the climb MARKER ships and the LINK does not. A player can climb; an AI
baking a navmesh from this package has no edge to path along and will route
around the ladder or call the roof unreachable.

**Why this is a deliverable problem rather than a cosmetic one.** The package
is the product: somebody who has never seen this repo points their game at it.
They bake (`navmesh: bake_required` tells them to) and get a mesh with no
off-mesh links, so every vertical connection a ladder makes is invisible to
their AI. The data to prevent that is computed, validated, and then dropped one
step before it would be useful.

**Owners.** Level Factory -- carry `gameplay.json`'s `nav_link` entries through
the export into the package, either as rows in `navigation_hints.json` (whose
`dispatch.navigation_hints.v0.2` schema already has `nodes` and `edges`, so a
`links` list is the natural third) or as `NavigationLink3D` nodes in the scene,
which costs nothing at runtime until something queries them. Dispatch -- decide
which of the two, since it owns that schema and the runtime contract.

**What would falsify the framing:** a consumer who bakes their own links from
the `LADDER_` markers, making the shipped link redundant. That is possible --
the marker carries position, climb height, width, depth and facing -- but it
asks every consumer to re-derive cost, direction, capability and access state
that this pipeline has already computed, and `runtime_ownership_requirements`
is where that division is supposed to be written down rather than assumed.
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
    out = (text + ITEM).encode("utf-8")
    if b"\r\n" in out:
        raise SystemExit("REFUSED: would write CRLF")
    TARGET.write_bytes(out)
    print(f"PIPELINE_ROADMAP.md: {before} -> {len(out)} bytes "
          f"(+{len(out) - before}), {out.count(10)} lines, LF")


if __name__ == "__main__":
    main()
