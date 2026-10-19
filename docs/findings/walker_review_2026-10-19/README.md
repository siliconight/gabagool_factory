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

## The walker's answers, 2026-10-19

68 of the 69 questions were answered on the page between 20:57 and 21:27 UTC; `verdicts_2026-10-19.json` is the
page's store as read back that evening, one document per question. Each answer, with the walker's note where there is
one, now leads its roadmap item's status (`patches/patch_roadmap_look_review_2026_10_19.py`).

| item | question | answer | the walker's note |
|---|---|---|---|
| 170 | the hatch and its lid | Needs work | "the hole of the ladder opening doesn't match the lid...they should match" |
| 170 | the lid's default | Open by default | (the default already shipped) |
| 179 | inlets and covers | Needs work | the kerb's "cutout/indent" -- a ramp for wheels? It is the inlet's throat; curb ramps are separate |
| 228 | the edge | Needs work | "needs to ensure its thought of for runtime performance" |
| 238 | walls after the texture cut | Too soft or noisy | "you can tell where one texture stops and ends...needs 3d UV Tri stuff?" |
| 240 | the Philly street | Looks right | |
| 240 | street lights' shadows | Keep as is | "moving bodies shouldn't be dark, they will be important to see in the game" |
| 241 | the mid-rise block | Needs work | the shops' glow and windows want more detail; the trees too uniform |
| 241 | the shops' glow | Right | |
| 44 | the parked cars | Looks right | some want patina, wear, rust, bumper stickers |
| 45 | ground scatter | Natural | "maybe a little heavy if anything" |
| 148 | rooms as places | Too sparse | "computer screens should be on...bring life to this dead world" |
| 210 | phones face the sidewalk | Always | the booths' graffiti too uniform |
| 210 | the lit booth | Looks right | |
| 210 | which themes get phones | (note only) | "you decide...we should have city, rural, special" |
| 217 | clear-night moonlight | Right | |
| 217 | the rainy night | Needs work | |
| 217 | sun on a rainy day | A weak sun | |
| 217 | morning and noon presets | Build both | |
| 253 | walk done | Not yet | answered before the flag boxes shipped |

**The 49 open floors (255).** 48 answered, every one "Wall it"; corner_deli_heist_01's customer_floor|deli_counter
unanswered. Those answers came while the walker was unsure -- networked doors are the gameplay layer's, and they did
not want rooms walled shut -- and before it was explained that a wall here carries its own openings and that every door
opening already ships as a door socket. Afterwards, in chat: "go ahead with the 255 table, your defaults are good". The
defaults keep 16 pairs open and wall 33; that is what is built, as roadmap 260, and one row of the table flips a pair
back.
