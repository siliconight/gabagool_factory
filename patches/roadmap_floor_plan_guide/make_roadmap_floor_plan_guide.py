"""Write patches/patch_roadmap_floor_plan_guide.py: roadmap items 293, 294 and 295 appended after the last item
(asserted to be 292), from the walker's floor-plan guide of 2026-10-21 and its chase
(`docs/findings/guides_2026-10-21/floor_plan.md`). Copied from `roadmap_289_sight_contract/make_roadmap_289.py`'s
append half. Refuses if the name is taken.

    python patches/roadmap_floor_plan_guide/make_roadmap_floor_plan_guide.py
"""
import pathlib

F = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
dest = F / "patches" / "patch_roadmap_floor_plan_guide.py"
assert not dest.exists(), "name taken"
GUIDE = "`docs/reference/Floor_Plan_to_3D_Layout_and_Automap_Guide.md`"
CHASE = "`docs/findings/guides_2026-10-21/floor_plan.md`"
STATUS = ("*STATUS: OPEN 2026-10-21 -- the walker's floor-plan guide (" + GUIDE + "), chased in " + CHASE
          + "; not started.*\n\n")

ITEM293 = STATUS + (
    "**293. The floorplan tool draws each storey flat, and nothing shows how a building's storeys stack: an exploded "
    "axonometric view with architectural cutaways.** The walker, 2026-10-21, filing the guide: \"add this to the "
    "roadmap to make our floorplan tool better and acheive that Exploded axonometric view, with architectural "
    "cutaways\". `deli_counter/floorplan.py` renders one SVG a storey -- rooms, walls, typed openings, stairs with "
    "their destinations, ladders, open-to-below, furniture, markers, a scale and a legend -- offline, with no Blender "
    "and no generative model, so a designer judges the space rather than a table. Nothing draws a building in three "
    "dimensions as a diagram: no axonometric, isometric, exploded or cutaway view exists in any of the ten tool "
    "repositories (read again), and the only 3D presentations are `tools/look_shots.gd`'s perspective overview and "
    "straight-on orthographic elevations and `migrations/review_render.py`'s Cycles perspective shots. The guide's "
    "section 6 is the view the walker means: roofs and selected ceilings hidden, walls cut away where they hide the "
    "interiors, each floor raised by a display offset and kept aligned with the rest, an angled orthographic camera, "
    "outlines, restrained shading, floor labels and callouts -- the offsets the drawing's alone, never the "
    "elevations, collision or navigation. A spec already states most of what it reads (`spec_types.py`: storey "
    "height, wall and floor thickness, roofs, openings with sill and height, stairwells with their storeys, slab "
    "holes, floor holes and hatches); a floor's elevation and a wall's height are derived in `deli_counter.py`; a "
    "ceiling height, an atrium through several storeys and a partition's own thickness are stated nowhere. The plan "
    "disagrees with what is built in two places a 3D view would inherit (read again): partitions drawn 0.15 m thick "
    "and built at `wall_thick` (`floorplan.py:37` against `deli_counter.py:1750-1757`), and the storey height "
    "labelled \"clg\" (`floorplan.py:604-605`) where it is floor to floor. It leaves out ramps, platforms, fire "
    "escapes, parapets, roofs and ceilings. Plans are made only by `validate.py`, which the commit gate runs, into "
    "the ignored `build/floorplans/` (2,052 SVGs, half of them sightline overlays); `build.py --all`, and so a cold "
    "run, makes none, and Level Factory's `packages/service/facade.py:350-352` looks for a `lot_out/floorplan.svg` "
    "that nothing writes. **What would close it:** an exploded axonometric of every building, drawn from its spec "
    "beside its plans and offline and deterministic like them -- each storey's slab at its true elevation plus a "
    "display offset, walls standing to a cutaway height so the rooms read from above, openings as gaps, stairs and "
    "ladders drawn between the storeys they join, slab holes and floor holes as voids, roofs and ceilings left off, "
    "markers riding their storey's offset, room labels and a storey key -- with the offset applied to the drawing "
    "alone; the plan's two disagreements fixed first, and ramps, platforms and fire escapes drawn where they stand; "
    "the guide's acceptance checks (its section 10) asked of a test building -- a doorway moved or widened, a stair "
    "moved, an atrium's opening kept, two markers one above the other, the floors separated with their markers, the "
    "elevations unchanged -- and of a library building in a frame for the walker; made where the plans are made, and "
    "shown where a reviewer looks (a walker-review page, a level's export), chosen with the walker.\n")

ITEM294 = STATUS + (
    "**294. A building's room graph is undirected and reads no door state, though every link's direction and lock "
    "are recorded.** The guide's section 9 keeps a connectivity graph beside the geometry -- rooms, corridors and "
    "landings as nodes; doors, stairs, ladders and drops as connections carrying direction and access state -- to "
    "answer whether players reach the exit from the objective, whether locking a door disconnects a required route, "
    "whether a drop is one-way. `deli_counter/tactical.build_graph` (157-286) is undirected: a floor hole joins both "
    "ways (279-285), and its stair rule joins every overlapping room pair on consecutive storeys across a stair's "
    "span rather than the rooms the stair serves (`_connect_stair_column`, 244-255; both read again). "
    "`combat_audit`'s `_width_graph` and `layout_lint`'s graph are symmetric too. Direction and access state exist "
    "only per link in `gameplay.json` -- a drop's link is one-way with `required_capability` \"drop\", a ladder's "
    "carries `bidirectional` and `access_state`, a stair door `default_state` and `allow_random_lock` (`ladder.py` "
    "`_nav_link` and `drop_nav_link`, read again) -- and no graph reads them. An opening has no stable id, only an "
    "optional `tag` (9 of `office`'s 16 openings and 12 of `deli_a03`'s 27 carry none, read again), and an "
    "interactive's id hashes the door's position, so a moved door is a new door. **What would close it:** one graph, "
    "directed and carrying access state, built from the links the build writes; the stair rule joining only the "
    "rooms a stair serves; an opening's stable id; the guide's questions answered for every building, and gated "
    "where an answer is wrong -- an objective whose only route out runs through a door the gameplay may lock; "
    "`_count_independent_routes` and the audits asking it rather than their own graphs.\n")

ITEM295 = STATUS + (
    "**295. Nothing makes a map of a level.** The guide's sections 7 and 8: a simplified automap mesh from the same "
    "layout -- room and corridor footprints, stairs, ramps, bridges, openings and landmarks kept; props, ceilings and "
    "tall walls left out; adjacent regions merged but never across a wall; holes and narrow passages kept; a shallow "
    "thickness and highlighted boundaries rather than a wireframe -- shown in a world of its own (`SubViewport`, "
    "`own_world_3d`) through an orthographic camera, with each marker placed by its storey and space and riding any "
    "display offset. Nothing in any repository makes a minimap, an automap or a map scene (read again). The "
    "interactive map is the game's -- the gameplay layer lives outside Level Factory -- but the mesh and the "
    "identities it needs are the factory's to make, from specs it already has. **What would close it:** a level's "
    "export carrying a map mesh per storey and the room and storey identity of every region, made from the specs, "
    "checked against roadmap 294's graph, and against the walk navmesh for traversal only (the guide: a navmesh's "
    "edges are an agent's centre, shrunk by its radius, not the building's); the guide's acceptance checks; the "
    "in-game map scene left to the game, with a reference scene to show the walker.\n")

PATCH = '''"""Roadmap 293, 294 and 295 filed from the walker's floor-plan guide of 2026-10-21
(`docs/reference/Floor_Plan_to_3D_Layout_and_Automap_Guide.md`): an exploded axonometric view with architectural
cutaways from the floorplan tool, a directed connectivity graph, and an automap mesh. Appends the three after the last
item (asserted to be 292). Copied from `patch_roadmap_289_sight_contract.py`'s append half. The index is NOT touched
here: run `python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_floor_plan_guide.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

ITEMS = %r


def main():
    raw = RM.read_bytes()
    if b"\\r\\n" in raw:
        raise SystemExit("REFUSED: the roadmap is LF and CRLF was found; nothing written")
    text = raw.decode("utf-8")
    if "\\n**293. " in text:
        raise SystemExit("REFUSED: already applied; nothing written")
    heads = [int(m.group(1)) for m in re.finditer(r"(?m)^\\*\\*(\\d+)\\. ", text)]
    if max(heads) != 292 or heads[-1] != 292:
        raise SystemExit("REFUSED: the last item is not 292; nothing written")
    if not text.endswith("\\n") or text.endswith("\\n\\n"):
        raise SystemExit("REFUSED: the roadmap does not end on one newline; nothing written")
    for item in ITEMS:
        text = text + "\\n" + item
    for n in (293, 294, 295):
        if len(re.findall(r"(?m)^\\*STATUS: [^\\n]*\\*\\n\\n\\*\\*%%d\\. " %% n, text)) != 1:
            raise SystemExit("REFUSED: item %%d's status does not adjoin its heading; nothing written" %% n)
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 293, 294, 295 appended; now roadmap_status.py --write / --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
''' % ([ITEM293, ITEM294, ITEM295],)
for item in (ITEM293, ITEM294, ITEM295):
    assert "\n" not in item[:-1].replace("*\n\n**", "*  **"), "an item spans more than its status and its line"
compile(PATCH, str(dest), "exec")
dest.write_text(PATCH, encoding="utf-8", newline="\n")
print("wrote", dest, len(PATCH), "chars")
