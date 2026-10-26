# Civic rooms furnished as what they are (roadmap 308)

A chapel, a courtroom and a gallery all go to Deli Counter's `hall` recipe -- a dining hall: a service counter, waiting
chairs, vending, dining tables (`level_design.py`, the `("hall", ("gallery", "galleries", "exhibit", "chapel",
"assembly", "courtroom", ...))` row of the room-kind table; the recipe at `"hall": {"anchors": ("counter_service",)`).

## What the furnishing pass can do today (read 2026-10-25, Deli Counter 0.269.0)

- **Rows** (`furnish`'s `_rows`, 0.247.0): islands of one piece laid in rows DOWN THE ROOM'S LONG AXIS, whole rows
  from the middle out, until the room's floor share (`room_floor_share`) reaches the recipe's `rows_share`; each
  island's facing drawn at random from the two along its row (`rng.choice(fronts)`). Right for a store's back-to-back
  gondolas; wrong for pews, which all face one front with an aisle down the middle.
- **Anchors, wall runs, floor sets, clusters, fixtures**: as every recipe.
- **Zoo species that serve**: `bench` (a pew, until a pew species), `chair`, `desk`, `counter`, `display_case`, `table`.
  Missing: a pew, a lectern, a plinth.

## The design, not built

- **A front.** The wall opposite the room's main door (its widest doorway; a room with doors on two walls takes the
  wall facing the one off the building's entrance), so a chapel's altar and a court's bench stand where a person
  walking in looks.
- **Facing rows** (a new layer beside `_rows`): benches ACROSS the room, every one facing the front, a centre aisle at
  least a corridor wide (`agent_contract.min_corridor_width`) and side aisles where the room allows, the first row
  back from the front by the anchor's depth and a step, rows stopping a door's clearance short of the back wall.
- **The recipes**:
  - `chapel`: the front's anchor an altar table (`table`, later a species), a lectern beside it (`desk`, small),
    facing rows of pews (`bench`);
  - `courtroom`: the front's anchor the judge's bench (`counter`, raised later), a witness stand beside it (`desk`),
    two counsel tables facing the bench (`table`), a rail across the room, and facing rows (`bench`) behind it;
  - `gallery` / `exhibit` / `artifact` / `viewing`: display cases along the walls (`display_case`), plinths in a loose
    grid on the floor (a box until a plinth species), one bench (`bench`) to look from, the floor left open;
  - `assembly`: facing rows of chairs (`chair`) toward a front with a lectern.
- **Measured before and after**: the pieces each kind stands, the floor share against the walker's 12-25 % band
  (`rooms-not-crowded-not-barren`), and the route census (`route_cost.py`), since a pew row is a wall a fight runs
  between. A refurnish of the library's rooms of these kinds, and the fixed-point-of-furnish tests, as every recipe
  change has needed (Deli Counter 0.267.0's three refuted drafts).
