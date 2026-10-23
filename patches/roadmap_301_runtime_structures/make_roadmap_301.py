"""Write patches/patch_roadmap_301_runtime_structures.py: roadmap 301 appended after the last item (asserted to be 300)
-- the walker's ask for an item on runtime data structures. Copied from
`roadmap_299_300_walk_deli/make_roadmap_299_300.py`; it replaces no status. Refuses if the name is taken.

    python patches/roadmap_301_runtime_structures/make_roadmap_301.py
"""
import pathlib

F = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
dest = F / "patches" / "patch_roadmap_301_runtime_structures.py"
assert not dest.exists(), "name taken"
t = (F / "PIPELINE_ROADMAP.md").read_bytes().decode("utf-8")
assert "\r\n" not in t

ITEM301 = (
    "*STATUS: OPEN 2026-10-23 -- the walker's ask, filed with a first census of what runs every frame; not "
    "started.*\n\n"
    "**301. Nothing checks that what a level runs every frame uses the engine's data structures rather than "
    "working against them.** The walker, 2026-10-23, with a short piece on game data structures (arrays laid out "
    "contiguously for the cache, quad-trees, octrees and bounding volume hierarchies for culling, raycasts and "
    "collision, ring buffers for event and input logs, graphs and A* for pathfinding, spatial hash maps for neighbour "
    "lookups): \"Godot might be doing all of this already for us. but for our levels to think about\". **Godot does "
    "most of it, and the question is where our levels undo it.** The engine already keeps a dynamic BVH for frustum "
    "culling and for the physics broadphase, culls by occlusion (on in our packages: every look_shots frame reports "
    "`occlusion_culling: true`), paths with A* over the NavigationServer's polygon graph, and stores a MultiMesh's "
    "instances and a packed array's elements contiguously. **What our code and our scenes decide** -- each "
    "a place the cost grows with the level's content or its player count, which `CLAUDE.md` names as already "
    "refused: (1) PER-FRAME SCRIPTS. Measured 2026-10-23, 29 shipped runtime `.gd` files define `_process` or "
    "`_physics_process`: Lux 10 of 42, Laser Tag 13 of 38, Level Factory's package assets 5 of 18, Deli Counter's "
    "template 1 of 9, Zoo, Patina and Pixelcoat none. Lux already turns a rig's processing off unless it flickers or "
    "cycles (`lux_fluorescent_rig.gd`, `set_process` at its line 74), so a steady or baked lamp costs nothing a "
    "frame; whether every per-frame script does the same is not checked. The heaviest by queries and scans are Laser "
    "Tag's bot controller and its map-evaluation harness (a harness, not a game) -- bounded by the walker's rule "
    "for Laser Tag. (2) WHAT THE CULLER IS GIVEN. A MultiMesh is one object to the culler, so its partition decides "
    "what culls (Lot's dressing one per room, block or wall run; the backdrop one a module a side); a piece whose "
    "bounds span the level is in every frame's cull result -- the backdrop ground (432 x 332 m, one draw), Lux's "
    "horizon glow (760 m) -- cheap at one draw each, and the shape to recognise. (3) LOOKUPS IN GAMEPLAY. Sight and "
    "neighbour checks that walk every enemy against every player grow with both counts; a spatial hash or the "
    "physics server's own shape queries answer them without the scan. **What would close it:** a census tool beside "
    "`tools/light_check.py` that lists every per-frame script in a package with what each frame's work iterates "
    "(group lookups, child walks, loops over props, lights or players) and whether it can switch itself off; a "
    "per-frame CPU figure for a package at fixed stations, scripts on and off, with a control, priced the way "
    "`CLAUDE.md` asks; each scan that grows with content or players either moved onto an engine structure "
    "(groups cached, `VisibleOnScreenNotifier3D`, physics shape queries, a spatial hash) or shown cheap by "
    "measurement; nothing changed on reasoning alone.\n")
status, body = ITEM301.split("\n\n")
assert "\n" not in status and status.endswith("*") and body.startswith("**301. ") and body.count("\n") == 1

PATCH = '''"""Roadmap 301 (OPEN) filed: the walker's ask for runtime data structures -- what a level runs every frame,
and whether it uses the engine's structures or works against them. Copied from
`patch_roadmap_299_300_walk_deli.py`; it replaces no status. The index is NOT touched here: run
`python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_301_runtime_structures.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

NEW_ITEMS = %r


def main():
    raw = RM.read_bytes()
    if b"\\r\\n" in raw:
        raise SystemExit("REFUSED: the roadmap is LF and CRLF was found; nothing written")
    text = raw.decode("utf-8")
    if "\\n**301. " in text:
        raise SystemExit("REFUSED: already applied; nothing written")
    heads = [int(m.group(1)) for m in re.finditer(r"(?m)^\\*\\*(\\d+)\\. ", text)]
    if max(heads) != 300 or heads[-1] != 300:
        raise SystemExit("REFUSED: the last item is not 300; nothing written")
    if not text.endswith("\\n") or text.endswith("\\n\\n"):
        raise SystemExit("REFUSED: the roadmap does not end on one newline; nothing written")
    for item in NEW_ITEMS:
        text = text + "\\n" + item
    if len(re.findall(r"(?m)^\\*STATUS: [^\\n]*\\*\\n\\n\\*\\*301\\. ", text)) != 1:
        raise SystemExit("REFUSED: item 301's status does not adjoin its heading; nothing written")
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 301 OPEN filed; now roadmap_status.py --write / --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
''' % ([ITEM301],)
compile(PATCH, str(dest), "exec")
dest.write_text(PATCH, encoding="utf-8", newline="\n")
print("wrote", dest, len(PATCH), "chars")
