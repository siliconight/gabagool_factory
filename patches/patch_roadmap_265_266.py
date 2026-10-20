"""Roadmap 265 (every floor hole has a cause, in progress) and 266 (interiors merge per room and material, from
the MultiMesh audit) appended after item 264.

Anchored: the roadmap must end on item 264's last line and carry no 265 or 266; nothing is written otherwise.
Every line LF. Then `python tools/roadmap_status.py --write` and `--check`.

    python patches/patch_roadmap_265_266.py
"""
import pathlib
import sys

ROADMAP = pathlib.Path(__file__).resolve().parents[1] / "PIPELINE_ROADMAP.md"
TAIL = "n the length of their voids, and the skylight could drop into the cage or onto the gaming floor. **What would close it:** each named wall clear of its hole by the factory's call, written down where the walker can reverse it; L27 silent on the library and on a fresh casino_tower; the shells rebuilt.\n"
ITEMS = '\n*STATUS: OPEN 2026-10-19 -- the walker\'s call; in progress (Zoo species drawn and previewed in a clone, nothing shipped).*\n\n**265. Every hole in a floor has a cause.** The walker, 2026-10-19, asking why the levels have holes in their floors -- Deli Counter\'s drop routes, cut square through a slab: 13 of the 159 built specs carry one (the six delis\' 2.2 m `vertical_attack_angle` from the apartment hideout into the kitchen; rowhouse_raid and apartment_walkup_a01 a bedroom over a kitchen, a counter partly under; both police stations an armory over the garage; warehouse_a02 a mezzanine; foundry_heist_vertical a catwalk over a press and a skylight room over an archive) -- and choosing to keep the routes: "go with 1, give them a reason to exist"; then "if we have holes it should be clear to the player that they are there, but also some reason other than a perfectly cut square (what is diegetic but a signal to the human playing the game)". **The design, the factory\'s calls, meant to be changed:** a cause per hole by room pair in a Deli Counter table (a link\'s own `cause` overrides) -- `cut` (a crew broke through: the delis, the foundry\'s skylight into the archive), `hatch` (a built floor hatch with a safety-yellow frame and its lid standing open: the police stations\' armories, the warehouse mezzanine) and `broken` (a floor that gave way: the rowhouse and the walk-up); the foundry\'s 5 x 3 m catwalk opening is undecided. Every hole\'s outline stops being a square: Zoo `hole_edge` stands round the cut -- the floor\'s underlayer torn back irregularly and jutting past the cut, the joist ends and the floor\'s dark cavity in the cut\'s walls, the ceiling broken back underneath with shards hanging -- all visual, the slab\'s rectangle staying the collider and the drop\'s route; `hole_spoil` lies on the floor below (what came down); `hole_kit` stands beside a `cut` hole (the crew\'s tarp, saw, bag, and a work light aimed into the opening, drawn not lit); `hatch` is `roof_hatch` in a new `floor` form. Measured so far, in a clone: each species builds to its slot\'s exact size at every form and variant tried, the edge 1,308 tris, the spoil 252-292, the kit 1,380; a cut hole is seven materials across its three modules (edge 2, spoil 3, kit 3 -- folded from twelve when the walker asked whether this was being done intelligently). **What would close it:** the species and the table shipped with tests that fail without them, the library rebuilt, a cold run per cause with frames from above and below, the hole\'s price in draws at its stations, and the walker\'s eye.\n\n*STATUS: OPEN 2026-10-19 -- measured, not started.*\n\n**266. Enterable buildings\' interiors merge per room and material.** The walker, 2026-10-19, with Godot 4.7\'s MultiMesh page: "Are we doing this intelligently?" -- "at a high level if we are using it for our total pipeline". Measured on cold run 9339\'s package (`docs/findings/multimesh_audit/`, `instancing_census.gd`): 3,587 separate mesh nodes in 1,958 distinct meshes, 3,798 surfaces in the draw pool; 63.3 % of them in meshes two or more nodes share and 25.0 % in meshes eight or more share, every one of those baked; MultiMesh already carries the two layers built for it -- the surface dressing, about 4,100 instances in 4 submissions, and the backdrop in 25. The buildings hold 2,576 of the 3,798 surfaces: wall panels 796 (one 12-triangle panel stands in 173 separate nodes), light fixtures 400, interior props 1,380. MultiMesh is not the lever for them -- they are baked, the 4.7 lightmap pages name MeshInstance3D and say nothing of MultiMesh, and a MultiMesh is one culling object -- MERGING is: per room and material, as the Empties already merge per side and the covers per side per material, so each merged mesh keeps its own lightmap and a room stays the unit that comes into view together. Interactive modules (doors, windows with states, hatches) stay separate. Also measured and left as a question: the dressing layer\'s MultiMeshes are one a species for the whole site, against CLAUDE.md\'s "never one for the level"; four submissions are cheap, and the always-on vertex work (about 4,100 instances every frame) is unmeasured on a low-end GPU. **What would close it:** a merge pass priced the way the cover merge was -- draws and frame time at stations inside the merged rooms, before and after, with two controls -- the bake unchanged in look (lightmap compared user by user), and the walker told what it cost and bought.\n'


def main():
    raw = ROADMAP.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("REFUSED: the roadmap has CRLF lines; nothing written")
    text = raw.decode("utf-8")
    if not text.endswith(TAIL):
        raise SystemExit("REFUSED: the roadmap does not end on item 264's last line; nothing written")
    if "**265. " in text or "**266. " in text:
        raise SystemExit("REFUSED: an item 265 or 266 is already there; nothing written")
    ROADMAP.write_bytes((text + ITEMS).encode("utf-8"))
    print("roadmap 265 and 266 opened; now tools/roadmap_status.py --write and --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
