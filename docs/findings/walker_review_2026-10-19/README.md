# The walker's look review, 2026-10-19

**What it is.** One page that puts every look question waiting on the walker beside frames of it, with an answer to
tap and a note for each: https://claude.ai/artifact/4mvvW5CeXifC8wQUVX9Nh9 (private to the walker). It holds 69
questions: 20 across roadmap items 170, 179, 228, 238, 240, 241, 44, 45, 148, 210, 217 and 253, and 49 open floors
from item 255, one per room pair. Answers save to the page's own store, collection `verdicts`, one document per
question (`{choice, note, at}`), and are read back with the Artifact tool's data reads.

**Where the frames came from.** Every frame was shot on 2026-10-19 with `tools/look_shots.py`, from walk copies
(`tools/walk_export.py`) of four levels built that day, except where a caption names an earlier run:

| level | light | cold run |
|---|---|---|
| restaurant_row_001 | evening, clear | 9335 |
| urban_row_001 | evening, clear | 9336 |
| county_hospital_001 | night, rain | 9334 |
| gas_block_001 | night, clear | 9337 |

Cameras were aimed at real objects: `find_nodes.gd` asks the engine where every drain, payphone, car, fence, roof
hatch, fire escape and awning stands. Rooms are shot from a corner across to the far corner, from the specs' own room
bounds and each building's placement. Frames marked INSPECT use `look_shots.py --inspect studio`, a work light that
shows form and says nothing about the level's lighting. Roadmap 170's frames are cold run 9316's, because no level
built today has a roof hatch.

**Seen while shooting, put to the walker on the page:**

- **A payphone faces the storefront.** On restaurant_row_001 the phone stands at the building side of the sidewalk,
  and its face points at the storefront about a metre behind it, so from the street you see its plain back. At the
  hospital the phone stands at the kerb and its face points at the sidewalk.
- **A clear night is nearly black away from the street lamps.** The forecourt and its sign read; the ground between
  lamps does not.
- **Rooms are lit and sparse.** Big floors with a few shelves, cartons and desks.

**The open floors** (item 255) are drawn by `open_floor_plans.py`: each storey's plan from Deli Counter's
`floorplan.py`, with every baselined open edge that `layout_lint.open_floors` finds drawn in red and labelled by its
two rooms. All 49 baselined pairs were found and drawn, on 33 storey plans.

**Asset flags** (item 253) wait on a walk. Four walk copies stand in the factory's `_scratch/review/`: `walk_9336`,
`walk_9335`, `walk_9337` and `walk_9334`. G flags what the crosshair rests on as looking good, and P as needing love,
into `asset_flags.jsonl` beside each copy; `tools/asset_flags.py` gathers them.

**How to rebuild the page:** `collect_frames.py` (the frames as JPEGs), `open_floor_plans.py` (the plans), then
`build_page.py` (the page), each into one page folder, then publish it with its `img/` and `plans/` files.
