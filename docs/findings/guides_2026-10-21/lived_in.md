# The "Lived-In Levels" guide against the factory: where it already holds, where it does not, and the first measurement for each gap

Survey of `docs/reference/Lived_In_Levels_Clear_Navigation_4P_PVE_1999_PA.md` (read at `docs/proposals/`, where it was first filed) (the guide) against the tool repos, 2026-10-21. It is read-only: no repository file was changed. The guide's numbers are its own unvalidated proposals (guide line 26). This report treats them as data to compare against, not as targets.

Every claim carries a tag:

- **[READ]**: seen in the file and line cited.
- **[INFERRED]**: reasoned from read code or values, not observed in a run.

Every number names the tool that produced it. Section numbers (§N) are the guide's.

---

## 0. Grounding

**Tool versions read:**

- Deli Counter 0.248.0 (`deli_counter/VERSION`)
- Level Factory 0.228.0
- Lot 0.126.0
- Laser Tag 0.32.0

**Byte checks.** Each file was measured with `read_bytes()` and compared it with the size `ls -la` reported for the same file. Every pair agreed, and the files are all LF.

| File | Bytes |
|---|---|
| guide | 49,005 |
| `agent_contract.json` | 15,276 |
| `agent_contract.py` | 15,509 |
| `level_design.py` | 300,264 |
| `combat_audit.py` | 46,107 |
| `nav_gate.py` | 22,557 |
| `circulation.py` | 20,153 |
| `sightlines.py` | 16,364 |
| `tactical.py` | 41,761 |
| `layout_lint.py` | 82,542 |
| `navigability.py` | 5,050 |

**What was read, by repo:**

- **Deli Counter (DC):**
  - in full: `agent_contract.json` and `.py`, `combat_audit.py`, `nav_gate.py`, `circulation.py`, `sightlines.py`, `navigability.py`;
  - `level_design.py`, these line ranges: 1-1404, 1404-2560, 2895-3030, 3132-3651, 3698-3807, 3851-4010, 4302-4395 and 5065-5658;
  - `tactical.py`: 1-80 and 357-903;
  - `layout_lint.py`: 1-140, 336-357, 1007-1137 and 1531-1680;
  - parts of `nav_gate.gd`, `ticket_queue.py`, `ladder.py`, `test_furnish.py`, `test_corner_store_rows.py`, `test_seed_corridor.py`, `spec_types.py`, `presets.py` and `migrate_furnish_recipes.py`;
  - one library spec, `specs/deli_a03.json`.
- **Laser Tag (LT):**
  - in full: `LT_MetricsCollector.gd`;
  - `LT_MapSampler.gd`: lines 1-309;
  - parts of `LT_MapEvalHarness.gd`, `LT_TestScenario.gd`, `LT_BotPlayerController.gd`, `LT_Shooter.gd`, `LT_LineOfSightTester.gd`, `LT_Const.gd` and `test_body_collision_rules.gd`.
- **Lot:**
  - `site_tactical.py`: lines 1-389;
  - parts of `site_cover.py`, `site_targets.py`, `site_responders.py`, `site_audit.py`, `site_layout_lint.py` and `godot/addons/heist_nav_qa/nav_qa_director.gd`.
- **Level Factory (LF):** parts of `packages/validation/sightlines.py`, `tactical.py` and `spawn_placement.py`, `packages/core/models.py`, `apps/cli/commands/__init__.py`, `packages/staging/dispatch_inputs.py` and `assets/scripts/run_presentation_compose.py`.
- **Factory docs:**
  - `docs/LEVEL_STANDARD.md`: lines 1-240, 340-740 and 920-1000;
  - `docs/LAYOUT_RULES.md`, `docs/AGENT_CONTRACT.md`, `docs/AUTHORSHIP_GUIDE_APPLIED.md`, `docs/proposals/INTERIOR_FURNISHING.md`, `INTERIOR_EXTERIOR_BALANCE.md` and `ROW_ARRANGEMENT.md`;
  - `docs/findings/denser_rooms_148/README.md` and its `furnish_census*`;
  - `PIPELINE_ROADMAP.md` items 102, 129, 197, 211, 245, 282 and 283, plus the 124 status line.

**Numbers computed, all read-only:**

- **Clear-width table in (a):** `widths.py`, a script written for this pass (`lived_in/widths.py`). It reads `agent_contract.json`.
- **Floor-share census in (k):** an inline script calling DC's own `level_design.room_floor_share`. It ran over `deli_counter/specs/*.json`, excluding `lf_*` specs and facades, and only rooms of 9 m² or more.
- **Stair-width and ladder census in (f):** an inline script over the same specs.
- **deli_a03 volume naming in (d):** an inline script over that one spec.

`widths.py` is the one file besides this report that the pass created.

---

## 1. Summary

The factory already guards traversal well. It holds the contract's body sizes, the bake, reachability of markers and stairs, door apertures, and shelter height. It has almost nothing on four of the guide's central ideas:

1. **Widths after furnishing, along a route.** Only aisles and seeded pieces get a contract width. Everything else keeps 0.9 m from what stood before it.
2. **Four bodies at once.** Every crew instrument makes the four bodies ghosts to each other, by design.
3. **Simultaneous threat.** Nothing counts enemies per player.
4. **Reserving circulation before placement.** Furnish reserves only local approaches. Nothing reserves a route through a room.

Density is a per-m² count. By DC's own floor-share instrument, 652 of 701 library rooms sit below the walker's 12 % band.

| Q | The guide asks | The factory | Status |
|---|---|---|---|
| a | 0.70 m body; two players need 1.90 m, four need 3.70 m | Body diameter 0.70 exactly. The bake is for 0.80. The widest generated aisle (1.25) holds one body by the guide's formula. | Body: same. Multi-body widths: absent. |
| b | §5 widths measured after furnishing | Door 1.25 and the 1.5 m door approach. Aisle 1.25 against what stood before. Corridor 1.1 for seeded pieces, before furnish. 0.9 m for everything else. | Partial, mostly before furnishing or at placement only |
| c | Reserve routes, interactions and views first | Local keep-outs only: doors, stairs, ladders, vault swing, queue lanes, staff aisles, the objective (1.2 m from its centre). No route or view reservation. | Gap |
| d | Traversal cost of dressing (> 10 % warns); narrowest width | Reachability only (nav gate, walk test, LT). Path lengths are recorded but never compared with and without furniture. | Gap |
| e | Simultaneous attackers, directions, arrivals against four views | LT: shots, first contact, stuck and blocked events. A static sampler counts spawns with LOS. Nothing per player per moment. | Gap |
| f | Enter, retreat, revive, cross fire, carry, split, fewer players | Crew bodies do not collide with each other (LT and walk test, by design). No revive or carry. Teammate-blocked shots are unrecorded. | Gap |
| g | An alternate route avoids the same blocker or firing line | Cycle counts and node-disjoint room routes. One Lot angular-spread check at site scale. No firing-line test. | Partial |
| h | Low 0.9-1.2, tall 1.8-2.2; concealment is not cover | Crossing 1.3, shelter 1.6, nothing crouches. Gondola 1.40-1.45. No concealment or ballistic material on props. | Different model; gap on concealment |
| i | A nameable landmark per area | A `landmark` marker at the centroid of rooms with 7 roles. The brief's `landmark` field is read by nothing. | Gap |
| j | Eight reject/flag rules; keep room purpose | One enforced at library and level scale (rule 4), four partly (1, 2, 5, 7), two absent (3, 6), one not applicable (8). No room is ever rejected for losing its defining fixture. | Partial |
| k | Furnish by activity; vary density | Recipes per room kind. Target is one piece per 16 m², then 40 m², whatever the kind. Rows only on corner stores. | Partial |

---

## 2. (a) The contract's body against the guide's 0.70 m

**The contract's numbers.** All are in `deli_counter/agent_contract.json` and all are [READ]:

| Field | Value | Line | Note |
|---|---|---|---|
| `characters.player.radius_m` | 0.35 | :6 | body diameter **0.70**, the guide's assumed value |
| `height_m` | 1.8 | :7 | |
| `eye_height_m` | 1.6 | :8 | |
| `chest_height_m` | 1.0 | :9 | |
| `crouch_height_m` | 1.2 | :11 | no consumer: "Nothing in this toolchain crouches" (:54) |
| `max_step_up_m` | 0.5 | :12 | |
| `walk_speed_mps` | 4.0 | :13 | |
| `nav_bake.agent_radius_m` | 0.40 | :23 | the bake's agent; diameter 0.80 |
| `agent_max_climb_m` | 0.15 | :25 | |
| `agent_max_slope_deg` | 55 | :26 | |
| `cell_size_m` | 0.10 | :27 | |
| `min_door_width_m` | 1.25 | :34 | a design minimum |
| `min_corridor_width_m` | 1.10 | :35 | |
| `min_headroom_m` | 2.0 | :36 | |
| `unassisted_step_max_m` | 0.1025 | :42 | |
| `cover_break_height_m` | 1.3 | :50 | |

**Derived values in `agent_contract.py`** [READ]:

| Function | Value | Line | Rule |
|---|---|---|---|
| `door_approach()` | 1.0 m | :187-191 | 2r + 0.3 |
| `stair_flight_width()` | 1.2 m | :119-135 | corridor + one cell; also the landing depth |
| `shelter_height()` | 1.6 | :255-281 | |
| `cover_break_height()` | 1.3 | :284-327 | |

**Derived values in the contract's own text** [READ]:

- **Bake door floor** = 2·ceil(0.4/0.1)·0.1 + 2·0.1 = **1.00 m** (`agent_contract.json:37`).
- **Side margin at a door:** a 0.35 m body has **0.275 m** a side in a 1.25 m door (:37).
- **Aisles:** `island_aisle_width()` and `staff_aisle_width()` = max(1.10, 1.25) = **1.25 m** (`level_design.py:3239-3255`, `:4302-4329`).

**The guide's formula with these inputs.** The formula is `clear_width = n·d + 2·wall_margin + (n−1)·gap`. These figures come from `widths.py`, reading `agent_contract.json`. Each input set is stated in the row.

| Inputs | n = 1 | n = 2 | n = 4 |
|---|---|---|---|
| A. Guide's margins on the contract body: d = 2·0.35 = 0.70, wall margin 0.15, gap 0.20 | 1.00 | **1.90** | **3.70** |
| B. Bake diameter: d = 2·0.40 = 0.80, wall margin 0.15, gap 0.20 | 1.10 | 2.10 | 4.10 |
| C. The contract's door margin: d = 0.70, wall margin 0.275, gap 0.20 | 1.25 | 2.15 | 3.95 |
| D. No margins: d = 0.70, wall margin 0, gap 0 | 0.70 | 1.40 | 2.80 |

**What the formula shows about existing numbers:**

- **The contract's corridor is the formula at n = 1** [READ inputs, INFERRED reading]. The derivation reads "2·agent_radius + 0.3" (`agent_contract.json:37`), which is d = 0.80 with 0.15 a side: row B.
- **The bake's door floor (1.00)** is row A at n = 1.
- **The contract's door (1.25)** is row C at n = 1.
- **The contract is entirely single-body.** There is no field for a between-player gap or for n.

**Factory widths, counted as side-by-side bodies at the guide's margins (row A)** [`widths.py`]:

| Width | Where | Bodies side by side |
|---|---|---|
| 1.25 | island and staff aisle | 1 |
| 1.10 | corridor | 1 |
| 1.40 | combat_audit `WIDE_DOOR` | 1 |
| 1.20 | combat_audit carry opening | 1 |
| 1.00 | door approach | 1 |
| 2.20 | combat_audit `CRAMP_MIN_DIM` | 2 |
| 0.90 | furnish's margin between pieces | 0, and below the 1.00 bake floor |
| 0.80 | tactical `MIN_OPENING_WIDTH` | 0, and below the 1.00 bake floor |

**Tensions:**

- **Two agents at zero margin.** `combat_audit.WIDE_DOOR` = 4·r = 1.4 m, commented ">= passes two agents / a loot carry" (`combat_audit.py:53-55`) [READ]. That is row D at n = 2, i.e. no wall margin and no gap; by row A it is single file.
- **"Four capsules fit" in 2.2 m.** `CRAMP_MIN_DIM` = 2.2 "four capsules + enemies do not fit" (`combat_audit.py:24-26, 64`) is a room's narrowest dimension [READ]. Four bodies side by side need 3.70 (row A), so the 2.2 threshold holds two abreast [INFERRED].
- **Three body sizes across the instruments** [READ]:
  - LT's pill is 0.35, from the scenario's body (`LT_TestScenario.gd:31-39`);
  - the Lot walk test's walkers are `AGENT_RADIUS * 0.7` = 0.28 (`nav_qa_director.gd:818`);
  - the bake uses 0.40.
  Roadmap 208 already records that the walk test walks a different body.
- **Speed.** The guide's example uses 4.5 m/s. The contract's player walks 4.0 m/s (:13), and LT sets its bot to that from the scenario (`LT_MapEvalHarness.gd:533`, `LT_TestScenario.gd:39`) [READ]. Lot's route-sample spacing still reasons from "The crew moves at 4.5 m/s" (`lot/site_cover.py:702-706`) [READ]. A 15 m sample step is 3.75 s at 4.0, not 3 [INFERRED].
- **Crossing exposure at the contract's speed** [`widths.py`]:
  - the guide's 3-7 m crossing = 0.75-1.75 s;
  - its 6 m example = 1.50 s (1.33 at 4.5).

---

## 3. (b) Furnish's clearances against the §5 table

**The guide's rule.** §5 widths are "the narrowest **usable opening after furnishing**" (guide line 127).

**The factory's numbers by guide row:**

| Guide row (§5) | Guide range | Factory's nearest number | Source | When it is measured |
|---|---|---|---|---|
| Single-person opening | 1.0-1.2 | Door 1.25 (design); bake floor 1.00. Named exceptions: primos_pizza's kitchen_stairs at 1.20 and stairs-first landing doors at 1.1. | `agent_contract.json:34,37,38` [READ] | Before furnishing (apertures) |
| Single-person opening, cont. | | Door approach: no piece within **1.5 m + half** of an opening's centre, both sides of the wall. Exterior wall runs keep half-width + **0.9** along the wall. | `level_design.py:916-942`, `:3017-3020, 3055` [READ] | At placement, for every furnish and seed piece |
| Single-person opening, cont. | | Circulation gate: no prop within the door aperture ±**0.6** m. LF compose exits 6 on a failure. | `circulation.py:61,126-159`; `run_presentation_compose.py:363-376` [READ] | After furnishing, on the built greybox |
| Main two-way opening | 1.8-2.2 | None. combat_audit flags an objective room whose widest opening is under **1.4** (`OBJ_NARROW`). | `combat_audit.py:55, 806-810` [READ] | Before furnishing |
| Two-way circulation aisle | 2.0-2.6 | None. The generated aisle is **1.25** (`island_aisle_width`). | `level_design.py:3239-3255` [READ] | At placement only (see rows below) |
| Two-way aisle, card-shop island | | Kept 1.25 from the room's **bounds**, a wall's centreline. Measured 1.12 m from a partition's face (roadmap 282, open). | `level_design.py:3306-3317`; `PIPELINE_ROADMAP.md:20852` [READ] | At placement |
| Two-way aisle, corner-store rows (DC 0.247.0) | | `_row_slots` and `_row_clear`: 1.25 from wall **faces**, partitions, stair reserves, and everything standing when the row is laid. | `level_design.py:3406-3567` [READ] | At placement |
| Two-way aisle, rows on the final spec | | The test asserts 1.25 between gondolas and to walls. It accepts **0.9** to "the pieces placed after the rows". | `test_corner_store_rows.py:139-157` [READ] | **After** furnishing |
| Primary combat circulation | 2.8-3.6 | None. combat_audit's `CRAMPED` uses room narrowest dimension < **2.2**. | `combat_audit.py:64, 842-846` [READ] | Before furnishing (room bounds) |
| Small team maneuver area | 4×5 to 6×8 m | None. `KILLBOX_AREA` 35 m² and `_SEED_MIN_AREA` 30 m² are "big enough to need cover". | `combat_audit.py:65`; `level_design.py:329` [READ] | Before furnishing |
| Interaction approach | pose + approach + exit | No piece centre within **1.2 m** of an objective or loot marker; the piece's half-extent is not added. | `level_design.py:784-786` [READ] | At placement |
| Interaction approach, derived cases | | `card_play_table_floor()` (table + chairs + bodies, `:2410-2422`); `dart_lane()` (oche + 2r, `:3869-3888`); the staff aisle 1.25 behind counters. | [READ] | At placement |
| Revive area | | None. No revive exists in LT (none of the scripts listed in §0 models one). | [READ: absence in the files read] | n/a |
| Cover heights and crossing | | See (h). | | |

**The corridor rule (`corridor=True`)** [READ]:

- **Who asks it.** Only `seed_cover` calls it (`level_design.py:1032-1033, 1056-1057`).
- **What it requires.** The piece's square keeps **1.10** m (`min_corridor_width`) from every wall box (thickness-aware), stair reserve and standing volume (`:681-696`, `:800-808`, `:613-647`).
- **When it holds.** Its own test asks it "BEFORE furnish ... what furnish then stands beside a piece is furnish's to keep clear, not the seeder's" (`test_seed_corridor.py:144-149`).

**Furnish's own margin** [READ]:

- **Between pieces.** Every furnish piece keeps **0.9** m from any standing volume's edge, as a per-axis box test (`level_design.py:752-754`). That includes the seeded shelter piece, which runs first (`enrich`, `:5629-5654`).
- **From walls.** Floor candidates and clusters stand **1.0** m inside the room's bounds (`:5174`, `:5564`). Bounds are wall centrelines, so with 0.3 m walls the gap to the wall face is 0.85 m [INFERRED from READ values].
- **Inside clusters.** Members are packed 0.3-0.8 m apart "so a cluster is one obstacle to the navmesh" (`:2518-2522`).

**Which widths are measured after furnishing, in the guide's sense:**

- **After** [READ]:
  - the circulation gate, on the built greybox;
  - the corner-store row test, on the final spec;
  - the nav gate, which bakes the built shell including furniture boxes and records a single-piece rebuild experiment proving it (`nav_gate.gd:91-125, 208-226`);
  - the walk test and LT, which play the site walk copy.
- **At placement, against what stood before** [READ]:
  - `_seed_clear` and its door, stair, ladder and objective radii;
  - `_island_aisle_clear`;
  - `_row_clear`;
  - the 1.1 m corridor rule.
- **Before furnishing (apertures and room bounds)** [READ]:
  - door widths (`navigability.py:50-65`, `test_door_width.py`);
  - `WIDE_DOOR` / `OBJ_NARROW`, `H_CARRY_PINCH` (≥ 1.2 openings to a ≥ 1.4 exit, `combat_audit.py:533-559`), `CRAMPED`;
  - tactical's `MIN_OPENING_WIDTH` 0.8 (`tactical.py:27, 605-611`).
- **What none of them gives.** No after-furnishing instrument reports a **width along a route**. The circulation gate checks fixed boxes: apertures, ladder volumes and stair columns. The nav gate checks connectivity [INFERRED from the READ code paths].

**Tensions:**

- **Three spellings of "the floor in front of a door"** [READ]:
  - 1.5 m + half, a radius from the opening's centre (`level_design.py:916-942`);
  - 1.0 m, `door_approach()` used by layout_lint, the vault and ticket queues (`agent_contract.py:187-191`, `layout_lint.py:336-349`);
  - 0.6 m each side of the aperture (`circulation.py:61`).
  They answer different questions: a keep-out radius, a landing depth and a compose box. None of them is the guide's "first player can move aside" envelope.
- **A gap closed to the navmesh but not to a body.** Furnish's 0.9 m inter-piece margin is below the bake's 1.00 floor and above the body's 0.70. Such a gap is closed to the navmesh while a body could physically pass it [INFERRED from READ values]. This is the guide's "apparent path" mismatch in the other direction.

---

## 4. (c) Is circulation reserved inside a room before furnishing?

**The guide.** §3 and §13 step 3: reserve circulation, interactions, combat movement and important sightlines before placing large fixtures.

**What the factory reserves before furnish runs** (`enrich` order, `level_design.py:5629-5657`) [READ]:

1. **Teller enclosures.** Staff side walled, door locked (`enclose_teller_lines`).
2. **Vault rooms and the vault leaf's swing.** `vault_room.keepout_rects`, honoured by `_seed_clear` with +0.3 m (`:791-799`).
3. **Queues.** `ticket_queue.lay_queues` stands stanchion lines with lanes of `stair_flight_width()` (1.2) and a `door_approach()` floor in front of the window. Each line keeps 1.1 m from everything (`ticket_queue.py:9-41`). Furnish then keeps 0.9 m from each run, so a 1.2 m lane cannot take a piece (`level_design.py:2988-2995`). **This is the one place the factory reserves circulation for a human reason (a customer queue), as guide §3 asks.**
4. **`seed_cover`, then `furnish`.** Both place on a shuffled jittered grid of candidates (`:1009-1015`, `:5168-5177`). A 2.2 m spread separates hosts (`:809-811`).

**Fixture-local reservations inside furnish** [READ]:

- Stair reserves (flight and landing rects, +0.3, `:428-454, 761-764`).
- Ladders (1.6 m + half, `:781-783`).
- Slab holes (+0.3, `:765-780`).
- Doors (1.5 m + half).
- Objective and loot markers (1.2 m from the centre).
- The staff aisle behind a counter. The counter is placed "at its FINAL depth" so its keep-out covers the staff band (`:1326-1352`).
- The dartboard's throwing lane (`:3869-3972`).
- Furnish also writes a `patrol_point` in each staff aisle "so the nav gate answers whether a bartender can be reached there" (`migrate_furnish_recipes.py:52-65`). This is a reserve-then-verify for one interaction.

**What is not reserved** [READ: no such structure in `level_design.py`'s placement functions or in `enrich`]:

- door-to-door routes through a room;
- combat movement areas;
- interaction poses beyond the 1.2 m centre radius;
- revive space;
- protected views.

**A refuted reservation exists.** A "3.0 m furniture-free ring round every objective went into Deli Counter's furnish" and "came out again". The objective's failure had been misattributed: its marker snapped onto a desk top (`nav_gate.gd:109-116`) [READ].

**Tension with a walker call.** The walker's "keep lanes open: the contract's 1.25 m aisle at least" is honoured only for rows and islands. Every other furnish piece holds 0.9 m [READ, above].

---

## 5. (d) Does anything measure what furnishing costs navigation?

**The guide.** §14 asks for a "dressing traversal cost": flag a median noncombat route-time increase above 10 % from B to C. §5 asks for the narrowest usable width.

**What the factory measures:**

- **DC nav gate.** It bakes the built shell (with furniture) and proves:
  - each stair connects;
  - interior markers are reachable from spawn (types objective, extraction, loot, patrol_point, rescue: `nav_gate.py:181`);
  - entrances reach each stair;
  - connections hold across a grid sweep.

  It reports islands as poly count and height range only, "REPORTED, NOT GATED" (`nav_gate.gd:258-269, 747-768`). It records **no path length and no width** [READ: `nav_gate.py`, `nav_gate.gd` grep]. A furnished room holding no marker could become a separate island and be listed, not judged [INFERRED].
- **Lot walk test.** It proves home→anchor and spine legs and records each leg's navmesh `length_m` (`nav_qa_director.gd:786-791`). Four timed physical walkers report `travelled_m`, status and position on a stall (`:262-310`). These are the guide's raw ingredients (route length, route time), but they are taken **once, on the furnished level**; nothing runs a second arm without furniture [READ].
- **LF `spawn_placement`.** It has a walkability heightfield and Dijkstra `walk_distances` over the walk scene's boxes (`packages/validation/spawn_placement.py:68-71, 195-294`). Limits [READ]:
  - 0.5 m cells;
  - one storey band of ±3 m around the spawn;
  - no erosion by body radius, so it cannot see sub-metre slots.

  It is a site-scale distance tool that could be run twice by filtering boxes [INFERRED].
- **Laser Tag.** It records route progress, `PlayerStuck` (a 4.0 s window with under 0.5 m moved, `LT_BotPlayerController.gd:45-46, 422-441`) and event positions (`LT_MetricsCollector.gd:138-157`). The guide warns at a 1 s stall; the factory's stuck window is 4 s here and in the contract's `qa.stuck_seconds` (`agent_contract.json:58`).
- **Width checks.** `circulation.py` checks apertures, ladder volumes and stair columns, not route widths. `test_corner_store_rows` checks one room kind's gondola gaps [READ].

**The gap.** Nothing compares with and without furniture. Nothing reports the narrowest width along a route after furnishing. Roadmap 148's density change reported "0 interventions, findings 108 -> 108" and frames and a price (`docs/findings/denser_rooms_148/README.md`). It reported no navigation cost. The nav gate came in only as the library's reachability [READ].

**What makes a cheap instrument possible** [READ]:

- **Furnish's pieces are separable on disk.** Library specs carry them under `{stem}_r{crc32}_{seq}` names, and `migrate_furnish_recipes.furnished_by_this_pass(v, tags)` already separates them (`:40-49`). On `specs/deli_a03.json`, 129 of 147 volumes match that pattern (an inline count).
- **Seed_cover's pieces are separable** by `level_design._seeded_cover` (`:815-827`).
- **There is a raw arm for presets.** `presets.make(p, enrich=False)` gives the unfurnished preset (`combat_audit.py:1014-1016, 1035-1040`).

---

## 6. (e) Threat density

**The guide (§7) asks for:**

- enemies alive, approaching and actively attacking;
- attack directions per usable player position;
- ranged attackers with a clear shot;
- rushers arriving together;
- enemy queues at openings;
- arrivals checked against all four players' views.

**What Laser Tag records** [READ]:

- **Per run** (`LT_MetricsCollector.gd:19-54`):
  - shots fired, hit, missed and blocked, by side;
  - deaths, survival time, team wipe;
  - time to first contact and to each side's first shot;
  - mean engagement distance;
  - crew and enemy stuck events;
  - `enemy_blocked_events` ("a guard held by another bot's body ... reported, not scored", :36-37);
  - route progress.
- **Logged events with positions** (`:147-157`). `EnemyStuck` positions are how roadmap 197 found six guards jamming at a 1.1 m rear door (`PIPELINE_ROADMAP.md:19104-19112`). This is the closest existing measure of the guide's "enemy queues at openings".
- **The scenario:** 25 runs, crew 4, 6 enemies (`level_factory/apps/cli/commands/__init__.py:868-885`; `packages/core/models.py:207-214`).

**Laser Tag's static sampler** (`LT_MapSampler.gd:99-194`) [READ]. For each sampled position it records:

- `visible_to`: enemy **spawns** with LOS (overexposed at ≥ 3);
- peer exposure: the fraction of 96 viewpoints that can see it;
- open directions out of 8 within weapon range.

These are the nearest thing to "attack directions per usable player position". Three limits:

- They are spawn markers, not live attackers [READ].
- The spawn-relative figures are "SECONDARY, AND THAT IS DELIBERATE" (`:11-17`).
- **Samples are taken at the first surface hit by a ray cast down from above the level's bounds** (`:214-226, 232-239`). Floors under a collidable roof are therefore probably never sampled, and the exposure and cover fractions would describe streets and roofs, not rooms [INFERRED; unverified, see the ranked list].

**Lot, Level Factory and Deli Counter** [READ]:

- **Lot `site_cover`.** It plans cover against open lines from crew-route samples every 15 m to enemy hooks within range (`site_cover.py:706-766, 769-884`). It is outdoor and static.
- **Lot responders.**
  - Arrivals drive in along a lane from a road end, with `ENTRY_RUN` behind the stop and the stop at least 12 m (`CAMP_RADIUS`) from spawn and extraction (`site_responders.py:12-46`; `site_audit.py:54, 227-235`). That is §7's "believable arrival".
  - `S_RESPONDER_ARC` wants the arrivals spread, no gap over 150° (`site_audit.py:53, 219-226`), so "pressure changes direction between waves". That matches §7's "later, communicated yard arrival", not simultaneous pressure.
  - Nothing checks an arrival against the crew's views.
- **LF.** `LT_OPENING_STANDOFF`: an enemy nearer than the opening range by walking distance (`spawn_placement.py:83-94`).
- **DC.** `sightlines.py` "weak cover": cover markers in LOS of attacker spawns; intel only (`sightlines.py:223-231, 20-22`).

**The gap.** No instrument counts enemies with a simultaneous line on one crew member. None counts distinct attack bearings per crew member over time, rushers arriving together, or arrivals within any crew member's view.

**Tension with a walker call.** "Spawns are provisional ... a level-quality measure keys off geometry, not spawn placement" (`docs/LEVEL_STANDARD.md:546-548`; LT `MapSampler`'s own note). A per-player attacker count is spawn- and AI-dependent, so it can only be reported, never gated. The roadmap's standing rules already say this of Laser Tag: "Laser Tag is a soft gate" (`PIPELINE_ROADMAP.md:31-36`).

---

## 7. (f) Four-player checks (§4)

| Guide check | What the factory records | Gap |
|---|---|---|
| Entering together (the first player moves aside) | The 1.5 m + half door approach (`level_design.py:916-942`). `C_NO_PIE`: approach depth < 1.6 m, CQB pack only (`combat_audit.py:590-600`). `OBJ_NARROW` < 1.4 (`:806-810`). [READ] | No multi-body entry: LT "players do NOT collide with each other" (`test_body_collision_rules.gd:7-10`; settled "by design", roadmap 124, `PIPELINE_ROADMAP.md:14082-14086`). Walk-test walkers "collide with the WORLD only, never each other -- four capsules spawned in a line grid-lock instantly otherwise" (`nav_qa_director.gd:822-825`). [READ] |
| Retreating together | `H_CARRY_PINCH` (`combat_audit.py:533-559`); `DEAD_END`, `VERT_DEAD_END` (`:768-773, 822-835`). LT bot seeks a cover marker within 25 m after 2 hits (`LT_BotPlayerController.gd:19-36, 391-403`). Lot `S_NAKED_ANCHOR` wants a backstop at spawn and extraction (`site_audit.py:241-247`). [READ] | No retreat behaviour or measure. All four crew bots walk **one shared route** (`LT_MapEvalHarness.gd:585, 596-603`). The walk test's four walkers walk one spine, spawned 1.6 m apart (`nav_qa_director.gd:237-242`). [READ] |
| Helping a teammate (revive) | Nothing. | No revive in LT or the contract. |
| Crossing fire lanes | LT's LOS uses `LASER_HIT_MASK`, which includes `LAYER_PLAYER` (`LT_Const.gd:20`). `has_line_of_sight` returns `collider == target` (`LT_LineOfSightTester.gd:52-70`), so a teammate in the line silently denies the shot. A crew shot that meets a teammate is `FRIENDLY_HIT` (`LT_Shooter.gd:73-77`), which the collector's default branch counts as a **hit** (`LT_MetricsCollector.gd:108-109`). [READ] | Neither declined shots nor teammate-blocked shots are recorded. `shots_hit` includes friendly blocks [INFERRED from the branch]. |
| Carrying loot | `H_CARRY_PINCH` on aperture widths (before furnishing). | No carry speed or body; no route check after furnishing. |
| Splitting briefly | Articulation-room chokes, node-disjoint routes (`combat_audit.py:116-142`; `tactical.py:377-466`). [READ] | No reconnect distance. |
| Playing with fewer people | The brief's `crew_size` (default 4, `models.py:207`). Roadmap 129 measured crew 1-4 on restaurant_row_001 (`PIPELINE_ROADMAP.md:14597-14608`). [READ] | Not routine; one size per run. |
| Stall over 1 s | Stuck window 4.0 s (LT `:45-46`; contract `qa.stuck_seconds` :58; walk test `STUCK_SECS`, `nav_qa_director.gd:44`). [READ] | 4× coarser than the guide's warning. |

**Stairs and ladders against "a main escape should not become a single-player funnel at its first landing" (§6)** [READ]:

- **Generated flights** are drawn at `stair_flight_width()` = 1.2 m (`presets.py:39-57`).
- **Width-less library stairs** take `Stairwell.width = 1.6` (`spec_types.py:179`).
- **Library census (an inline script over 132 specs, 149 stairs):**
  - 131 stairs write no width, so they are 1.6 m;
  - the rest: 1.0 m ×2, 1.1 ×1, 1.2 ×6, 1.4 ×4, 1.8 ×3, 2.2 ×2.
- **By the guide's formula** (row A: two need 1.90), **only the two 2.2 m flights pass two abreast** [INFERRED].
- **Ladders.** All 78 library ladders carry the default `occupancy_limit` 1 (`ladder.py:522-526`; this pass's census). DC warns `LADDER_MULTIPLAYER_DEADLOCK_RISK` when the limit is over 1 (`:1056-1066`). Yet `combat_audit._vertical_links` counts a one-at-a-time ladder as a full second link (`combat_audit.py:298-313`), so `VERT_DEAD_END` treats it as relief [READ].

**Already named in the roadmap.** Roadmap 245, LEFT: "a four-player congestion check, static first" (`PIPELINE_ROADMAP.md:20609`; `docs/findings/pick_majors/README.md:162-165`) [READ].

**Tension with the guide.** The guide says teammates "can obstruct vision, movement, and shots" and asks for collision tests "only if the game supports" them (guide lines 28, 86). The evaluator's design call is no player-player collision, while teammates **do** block sight and shots in LT. So movement congestion cannot be observed, and sight congestion happens unrecorded.

---

## 8. (g) Loops that give a different option (§6)

**The guide.** An alternate route counts only if it avoids the same blocker or firing line. Two doors into one tiny vestibule, or two aisles converging under one shooter, may fail. Do not add loops merely for graph connectivity.

**What the factory checks** [READ]:

- **DC `combat_audit` LOOPS.** The cyclomatic number of the room graph, edges − nodes + components (`combat_audit.py:746-767`). HIGH `NO_LOOPS` when there is no cycle; MED `ONE_LOOP`. This is pure connectivity, exactly what the guide warns against counting alone.
- **DC routes to the objective.**
  - `H_ONE_ROUTE` needs two interior-node-disjoint routes from entries to each objective (`_disjoint_paths2`, `:470-511`, heist pack only).
  - `tactical._count_independent_routes` is a max-flow over the node-split graph, informational (`tactical.py:377-446, 567-581`).

  These do avoid a shared **blocker room**. They know nothing of firing lines, opening widths or furniture.
- **DC layout_lint L1.** Rooms deeper than 7 m want two openings; it runs on `pvp_heist` specs only (`layout_lint.py:1558-1570`).
- **Lot `site_tactical._distinct_routes_to`.** Distinct first hops in the building graph (`site_tactical.py:198-211`). `tools/approach_probe.py` measured that on street sites it equals buildings − 1 in 78 of 78 (`approach_probe.py:1-20`).
- **Lot S5.** Approaches should spread ≥ 90° "so one defender angle cannot hold every approach" (`site_layout_lint.py:17-18, 41, 138-153`). This is the only firing-angle reasoning about alternates in the toolchain. It is site scale and reads the same degenerate building-graph angles (per `approach_probe.py`).
- **Lot `site_targets`.** Counts road-graph loops as INFO (`site_targets.py:20, 97-130, 242-243`). Its own note: "NOT MEASURED HERE ... any route test that needs the navmesh" (`:35-37`).
- **Factory docs.** `LEVEL_STANDARD.md` §5.1: "a short loop near the score -- GAP ... loops are never counted"; "a longer bypass -- GAP"; "recovery when a route is unsafe -- GAP" (`docs/LEVEL_STANDARD.md:376-381`). The walkable-city brief asks for "a longer route that bypasses the most exposed area" (`docs/reference/DYNAMIC_WALKABLE_CITY_LEVEL_DESIGN_BRIEF.md:85-88`).

**The gap.** No check asks whether two routes share a firing position, a narrow funnel, or the same last door.

---

## 9. (h) Cover heights, roles, concealment

**The contract's model** [READ]:

- **Cover is decided by the mutual standing sightline.** Two lines (eye 1.6 to chest 1.0) cross at 1.3. "BELOW THIS HEIGHT A SOLID IS SCENERY, NOT COVER" (`agent_contract.json:50-51`).
- **Shelter (1.6) is the taller eye.** "Below it the workable interval shrinks to a point, at it the whole line is available" (`agent_contract.py:255-281`).
- **Crouch** (1.2, :11) has no consumer (:54).

**The guide's bands against it:**

| Guide | Contract and DC | Pieces in the band (`level_design._PIECES`, :1405-1964) [READ] |
|---|---|---|
| Low 0.9-1.2 | Below 1.3: `cover_low` markers, "life rather than shelter" | Mid-floor: tables 0.74-0.9, desk 0.75. Wall: counters 0.92-1.08, `display_case` 0.95-1.05, booth 1.15, safe 0.8-1.2. Clusters ≤ 1.5 (cartons 0.6-1.4, pallets 0.7-1.4). |
| Tall 1.8-2.2 | Shelter 1.6: the seed piece is built at exactly 1.6 (`level_design.py:1027-1046`). Lot's outdoor cover is 2.0 (`site_cover.py:77`). | Wall only: `shelf_run` 1.8-2.1, lockers 1.9, vending 1.83-1.9, tank 1.8-2.2, `back_bar` 2.4. Furnish's invariant: "NOTHING MID-FLOOR REACHES SHELTER HEIGHT" (`:1091-1097`), except the card shop's declared island (`test_furnish.py:120-155`). |
| Corner-store gondola | 1.40-1.45, "BELOW SHELTER, ABOVE COVER" (`level_design.py:1788-1798`; `test_corner_store_rows.py:99-103`) | Breaks a mutual standing line only from the middle part of it: t ∈ [0.33, 0.67] at 1.40 (`agent_contract.py:272-277`) and [0.25, 0.75] at 1.45 (computed the same way). |

**Tensions:**

- **The deli counter and the guide's low cover.** The deli counter, the guide's model "cover that belongs in the building" (§6), sits in the guide's low band. In the factory's model it is scenery, because nothing crouches.
- **Head exposure over a shelter piece.** A 1.6 m shelter piece shows a standing 1.8 m body's top 0.2 m. LT aims at the chest, so it never registers that exposure: the guide's "standing exposure" check is outside the model [INFERRED from READ values].
- **"Cover a body crouches behind."** The gondola's own comment says so (`:1792-1793`), while the contract says nothing crouches [READ, both].

**Roles** [READ]:

- **Two marker roles by height.** `cover_low` and `cover_high` split at 1.3 (`level_design.py:130-135, 257-258`).
- **Room-level checks.** `_room_has_cover` and `_room_has_shelter` (`:377-420`); combat_audit `KILLBOX` and `COVER_ALL_LOW` (`combat_audit.py:837-883`).
- **Caps against over-cover.** `_COVER_PER_ROOM_CAP` 5, `_SEED_MAX_PIECES` 4 (`:138, 330`).
- **Missing:** protected side, exposed sides, exit from cover, and one-player versus shared-defence roles (§6) [READ: absence in the functions above].

**Concealment and ballistics** [READ]:

- **Props.** A prop's material carries acoustics only: `(acoustic, absorption, damping)` (`level_design.py:2676-2702`; `material_kind.py:5-8`).
- **Ballistics exist only for openings:**
  - breakable windows (`spec_types.py:105-108`; `interactives.py:163-208`);
  - LT destructibles, where bullets break glass and breach walls are charge-only (`test_destructible.gd:217-253`).
- **Everything else with collision blocks LOS and shots in LT** (`LT_Const.gd:20`; the sampler masks World and Laser Blocker). A glass deli case such as deli_a03's `deli_case_cover` (material glass, convex collision, read from the spec) is therefore opaque, bullet-stopping cover to the evaluator [INFERRED].
- **No concept of concealment-not-cover exists.**

**Instrument defects already filed** [READ]:

- **Roadmap 283 (open).** `_room_has_cover`, `_room_has_shelter` and `combat_audit._cover_in_room` ask a piece's storey in ways that let floor-below pieces count. Asked by the foot, the audit "gain[s] seven COVER_ALL_LOW" (`PIPELINE_ROADMAP.md:20856`).
- **A stale crossing in Level Factory, not in Lot.**
  - LF's live advisory module `packages/validation/sightlines.py` still carries `EYE_HEIGHT = 1.4` and `MIN_COVER_HEIGHT` = 1.2 (`:48-59`). It is called by the Laser Tag adapter (`tactical.py:183-189`; `adapters/laser_tag/__init__.py:304`).
  - Lot now carries 1.6/1.3 (`lot/site_cover.py:63-70`).
  - The contract's note says "Lot still carries 1.2" (`agent_contract.json:51`), which is stale about Lot and silent about LF.

---

## 10. (i) Landmarks (§9)

**What exists** [READ]:

- **DC `add_landmarks`.** One `landmark` marker at the **centroid** of each room whose role is one of objective_room, public_entry, finale, loot_room, safe_room, vault_room or staging (`level_design.py:141-145, 273-314`). "The marker is just the anchor + a label -- the art team makes it visually distinct."
- **Dispatch staging** maps it to an "interaction" anchor (`level_factory/packages/staging/dispatch_inputs.py:31-35`).
- **The brief's `landmark` field** is in `UNBUILT_BRIEF_FIELDS`, "read only by `MissionBrief.functional_signature`" (`level_factory/apps/cli/commands/__init__.py:90-100`).
- **`LEVEL_STANDARD.md`:**
  - "landmark hierarchy ... BUILT as objects; GAP as a hierarchy (the field is read by nothing)";
  - hero props "GAP: nothing chooses a level's heroes";
  - "landmarks and affordances unreadable at player height -- EYE" (`:485, 492-497, 688`).
- **Lot `site_targets`:** "NOT MEASURED HERE ... landmarks" (`:35-36`).
- **Candidates nobody checks.** Recipe anchors (grill, service counter, furnace, desk, bar, stage) are placed first and are the nearest thing to a landmark fixture (`_RECIPES`, `:2187-2376`). They are the same species for every room of a kind; nothing checks they are distinct within a building or visible from its doors.

**The gap.** No instrument checks that a room has a distinct, nameable, visible landmark.

---

## 11. (j) The §13 reject-or-flag list

| §13 rule | Enforced? | By what [READ] |
|---|---|---|
| 1. Intersects a protected movement or interaction volume | **Partly** | `_seed_clear`: doors, stairs and reserves, slab holes, ladders, objective radius, vault swing (`level_design.py:650-812`). `circulation.check_shell`, compose exit 6 (`circulation.py:305-347`; `run_presentation_compose.py:363-376`). layout_lint L22 (vault leaf) and L23 (piece over a stair hole or walk). `dart_lane_blockers`. Queue keep-outs. **No route, combat-area, revive or view volumes exist to intersect.** |
| 2. Reduces an opening below the metric without a recorded exception | **Partly**, for apertures | Door 1.25 held by `test_door_width.py`, with two exceptions named in the contract (`agent_contract.json:38`). `navigability.py` warns (`:50-65`). combat_audit `audit_accept` records accepted findings (`combat_audit.py:954-972`). **Not for widths inside rooms after furnishing** (section 3). |
| 3. Hides an arrival, landmark, objective or route cue from test positions | **No** | Nearest: `_threshold_visibility`, the share of floor visible from a doorway, giving `C_BLIND_ROOM` / `C_NAKED_ROOM`; CQB pack, objective and fortifiable rooms only (`combat_audit.py:385-421, 602-624`). Hung pieces are checked for headroom only (`hung_headroom_ok`, `level_design.py:510-531`), never for what they hide. |
| 4. Creates an isolated navmesh island or an apparent path the controller cannot traverse | **Yes, at library and level scale; not per placement** | Nav gate (stairs gated; markers judged; islands listed), walk test physical walkers, LT `PlayerStuck`, LF seal findings, layout_lint L12. Seed pieces keep a 1.1 m corridor so "a seeded piece cannot cut a floor in two" (`level_design.py:681-696`). Furnish's own pieces are not asked, and a marker-less room's island is listed, not judged [INFERRED]. |
| 5. Depends on an unsupported vault, crouch, climb or door behaviour | **Partly** | L24: a room reachable only by breach, window or drop (`layout_lint.py:1123-1136`). Ladder deadlock and `scripted_direction` warnings (`ladder.py:1049-1066`). The contract: nothing crouches (:54). **Locked doors:** the teller staff door ships `locked` (`level_design.py:5694-5706`), and no reachability check reads lock state. `WALK_KINDS` counts every door (`layout_lint.py:967`). |
| 6. Creates an unreviewed firing slit, or a collider that blocks apparently clear shots | **No** | LT logs `ShotBlocked` with the collider's name and `shots_blocked_by_collision_percent` (`LT_MetricsCollector.gd:88-97, 232-233`): a measurement nobody turns into a placement rule. The ticket window is sealed because "a pane that shot out would be a firing line" (`ticket_queue.py:13-14`): a design call, not a check. |
| 7. Has no plausible support, owner, task or spatial relationship | **Partly** | Wall pieces need a built wall that holds their whole run (`_edge_backing` / `_held`, `level_design.py:3154-3163, 3229-3236`). Hosts bring seats. Stock follows room kind. **No owner or task.** `AUTHORSHIP_GUIDE_APPLIED.md:43-44`: "Rooms are not built round an activity." |
| 8. Exceeds the budget for active physics or other expensive behaviour | **n/a / partial** | Furnish places only static volumes. A triangle cap exists (`_CARD_SHOP_ROOM_TRIS`, a regression detector, `:1138-1178`), plus the per-mesh 8-light cap and the on-demand price. See the separate Blender/Godot runtime and MultiMesh TDD for §12. |

**Room purpose.** No room is ever rejected or revised for losing its defining fixture [READ]:

- Furnish's `short` loop hands a refused anchor's or wall piece's share to floor sets and clusters (`level_design.py:5582-5602`). A kitchen whose grill fits nowhere gets cartons.
- `seed_cover` keeps the finding when nothing fits (`:1047-1050`).
- The only purpose check is layout_lint L8, a family's signature rooms by **room-id tokens**, on `pvp_heist` specs only (`layout_lint.py:37-45, 1558-1559, 1653-1660`).
- A measured instance exists. On card_shop_a01 "the shop came back with no pack wall, no CRT and no shopkeeper", and nothing refused it (`level_design.py:1337-1346`). It was fixed by placement order, not by a guard.

---

## 12. (k) Furnish by activity, and density

**What matches §8** [READ]:

- **Rooms read as kinds.** Whole tokens of the room's id, then its role (`_ROOM_KINDS`, `:1980-2044`; `_room_kind`, `:2895-2928`). Building-aware overrides cover strip clubs, card shops, video stores, office floors and corner stores.
- **Each kind is a recipe:**
  - one or two **anchors** (large fixtures);
  - about half the target as a **wall run**;
  - **floor sets** that bring their own (a desk and its chair; a table and its chairs, some pulled out or turned);
  - **clusters** of 2-4 pieces packed 0.3-0.8 m apart (`_RECIPES`, `:2187-2376`; `_furnish_plan`, `:3698-3755`).
- **Fixtures carry their user's needs:** a poker cabinet brings its stool, a dartboard its throwing lane, a counter its staff aisle and back bar.
- **Surface stock follows the room**, for desks, bars, kitchens, vaults and storage.

That is the guide's "what belongs together" layer.

**What is missing from §8** [READ]:

- "who uses it" and "what changed recently" (`AUTHORSHIP_GUIDE_APPLIED.md:43-44`);
- environmental story clusters, marked GAP (`LEVEL_STANDARD.md:509, 962`).

**§13's opening line against the placement method** ("constrained placement ... not uniform random scatter") [READ]:

- Floor sets and clusters stand on a shuffled, jittered grid of 5-14 by 5-14 candidates, with a 2.2 m spread between hosts (`level_design.py:5168-5177, 809-811`). That is a near-uniform scatter for the floor's non-row pieces [INFERRED].
- Rows (corner stores) and islands are the constrained exceptions.

**The density target is area only** [READ]:

- `_furnish_target` gives one piece per 16 m² up to 10, then one per 40 m² up to 30 (`:3607-3620`).
- Overrides are few: strip club 24 m², card shop 20 m², corridor cap 2.
- Rows lay to a floor share of 0.25 on corner-store floors only (`:2350-2356, 5464-5515`).
- The roadmap-148 census (`docs/findings/denser_rooms_148/furnish_census_0245.out.txt`, DC 0.245.0) shows a **median target of about 10** for almost every kind. "EVERY room between 160 and 400 m2 wants ten" (README).
- Repetition is held per (piece, size) and per building: `_SAME_PIECE_MAX` 4 and `_PALETTE` 3 (`:2512-2517`). §9's rhythm (cluster, quiet surface, large fixture, clear opening) has no rule.

**Floor share against the walker's band.** An inline census, using DC's own `room_floor_share` over DC 0.248.0's library on disk (701 rooms of 9 m² or more, `lf_*` specs and facades excluded):

| | Below 12 % | In 12-25 % | Above 25 % |
|---|---|---|---|
| All rooms | 652 | 43 | 6 |
| Rooms with `combat_range` | 646 | 43 | 6 |

| Kind | Rooms | p10 | Median | p90 | In band |
|---|---|---|---|---|---|
| fallback | 106 | 0.019 | 0.027 | 0.062 | 1 % |
| office | 95 | 0.022 | 0.047 | 0.086 | 6 % |
| vault | 74 | 0.024 | 0.050 | 0.094 | 8 % |
| storage | 67 | 0.019 | 0.046 | 0.104 | 0 % |
| shop_floor | 57 | 0.022 | 0.089 | 0.202 | 30 % |
| hall | 55 | 0.026 | 0.039 | 0.078 | 2 % |
| lobby | 53 | 0.018 | 0.032 | 0.071 | 4 % |
| garage | 35 | 0.021 | 0.040 | 0.098 | 0 % |
| corridor | 35 | 0.002 | 0.004 | 0.025 | 0 % |
| kitchen | 23 | 0.049 | 0.084 | 0.119 | 9 % |
| club | 21 | 0.044 | 0.063 | 0.106 | 10 % |
| strip_club | 7 | 0.109 | 0.119 | 0.138 | 43 % |

How `room_floor_share` counts (`level_design.py:3372-3403`): the plan footprint of standing collision volumes whose foot is on the room's floor, unrotated. Its own docstring says a turned chair counts unturned. The README's review rooms (3.7-16.1 %) agree with this table.

**Tensions:**

- **The walker's band against the targets.** The band is "~12-25 %, primary furniture in rows, lanes open" (2026-10-21). The library's medians are 2-9 % by kind. Roadmap 148 refuted raising the count: "+63 %" pieces moved the market aisles only 5.7 → 6.8 % (`plateau_dry_run`, README). The factory's only proven lever for share is **rows of primary furniture**.
- **Rows and the 0.9 m margin.** Rows keep 1.25 m only against what stood before them (section 3). Any per-kind share target needs section 5's traversal measure beside it, or "lanes open" cannot be shown.

---

## 13. §12 runtime and MultiMesh

One line, by design: the guide's §12 MultiMesh, instancing and runtime-budget bullets are covered by the separate Blender retopology / Godot runtime / MultiMesh TDD survey. For roadmap 266 see `PIPELINE_ROADMAP.md:20782`.

---

## 14. Tensions in one place

1. **The contract is single-body throughout.** There is no gap term and no n. The factory's "wide" numbers are all row D (no margins) or n = 1 (sections 2 and 7).
2. **Crew-crew collision is off by design** (LT roadmap 124; walk test `:822-825`). Teammates still block sight and shots in LT. Congestion is invisible; sight bottlenecks happen unrecorded.
3. **Nothing crouches.** The guide's low-cover band and the deli counter are scenery to the evaluator. The gondola's comment says "crouches behind" (sections 9 and 2).
4. **Three door-approach numbers** (1.5 radius, 1.0, 0.6) and **three body radii** (0.35, 0.28, 0.40) are in use across instruments.
5. **Furnish keeps 0.9 m between pieces.** That is below the bake's 1.00 floor and the walker's 1.25 "at least". Only rows, islands and seeded pieces carry the contract widths, and seeded pieces only before furnish.
6. **Stale constants:**
   - LF's live sightline advisory still crosses at 1.2 (eye 1.4);
   - the contract's note blames Lot, which has moved;
   - Lot's route sampling reasons from a 4.5 m/s crew that now walks 4.0.
7. **Ladders.** Every library ladder is one-at-a-time, yet the vertical-link count treats a ladder as equal to a stair. And per `LEVEL_STANDARD.md` §7.2, players can climb only in the walk copy.
8. **Stuck threshold.** 4 s in every instrument against the guide's 1 s warning. It is the contract's `qa.stuck_seconds`, so changing it is a contract decision.
9. **The guide's §14 three builds (A/B/C) map only partly.** `enrich=False` presets give an A-like arm. Library specs carry furnish's pieces under separable names, so a B-to-C split is computable offline. No package build exists for B.

---

## 15. Ranked: the five highest-value gaps for a navigation-first, fights-first level

Ordered by the walker's reporting order (2026-10-21): the nav gate, then cover mix and sightlines, then the look. Each first step is a measurement from artefacts on disk, not a redesign.

**1. What furnishing costs a route, after furnishing.** Guide §5, §13 rules 1-2 and 4, §14 traversal cost; questions b, c, d. **Owner: Deli Counter.**

- **Why first.** The nav gate is the walker's first report line, and today it answers only "is the marker reachable" (section 5). Every density change (148, 281) shipped with no number for what it did to movement.
- **The instrument.** An offline census over `deli_counter/specs/*.json`, per room:
  - shortest paths between every pair of the room's openings, on a 0.10 m grid (the bake's cell);
  - inside the wall faces;
  - obstacles are standing collision volumes on that storey, dilated by 0.35 (body) and again by 0.40 (bake);
  - run twice: all volumes, then without `migrate_furnish_recipes.furnished_by_this_pass` and `level_design._seeded_cover` pieces.
- **Per room, report:**
  - path-length ratio;
  - opening pairs that disconnect;
  - the narrowest clearance along each path (a distance transform);
  - furnish pieces that intersect the unfurnished door-to-door corridor (the §3 reservation, measured before it is policy).
- **Flags.** Over 10 % (the guide's warning, retuned after the census), any disconnect, a narrowest clearance under 1.00.
- **Controls:**
  - a room with no generated pieces must read 0 % and identical clearance;
  - a planted 0.9 m slot must read closed at 0.40 and open at 0.35.

**2. Four bodies at one doorway.** Guide §4, §14 four-player crossing; question f. **Owner: Level Factory or Deli Counter for the static census; Laser Tag for the counter.**

- **The static census** is roadmap 245's queued "four-player congestion check, static first". For every `combat_range` room, list its ways in: doors, open edges (`tactical.OPEN_FLOOR_M`), stairs, and ladders with their `occupancy_limit`. For each, give the side-by-side body count n = floor((w − 0.30 + 0.20) / 0.90), using the contract's 0.70 body and the guide's margins.
- **It reports:**
  - rooms where **every** way in has n ≤ 1;
  - story pairs whose only second link is a one-at-a-time ladder.
- **The next cheapest step, in Laser Tag:** count LOS checks denied because the first collider was a teammate, and count `FRIENDLY_HIT` apart from `shots_hit`. Both are one counter each beside existing code (`LT_LineOfSightTester.gd:52-70`; `LT_MetricsCollector.gd:108-109`).

**3. How many enemies are shooting one player at once.** Guide §7; question e. **Owner: Laser Tag.**

- **The counter.** Per crew bot per physics second, count live enemies whose `has_line_of_sight` to that bot passes, and bin their bearings into 8 sectors.
- **Per run, report:**
  - the maximum and median concurrent attackers;
  - the share of crew-seconds with ≥ 3;
  - distinct sectors per crew-second.

  Reported, never scored: spawns are provisional.
- **Before relying on the static counterpart**, verify that `LT_MapSampler` samples interiors at all. In one existing report, count sampled positions inside building footprints at ground-storey height. Its downward first-hit sampling suggests it does not (section 6).

**4. A second route that is not a different option.** Guide §6; question g. **Owner: Deli Counter (`combat_audit`).**

- For each objective and fortifiable room, take the two node-disjoint routes `tactical._count_independent_routes` / `combat_audit._disjoint_paths2` already find.
- Using `sightlines.py`'s 2D occluders (`_occluders`, `_clear`), ask whether one standing position inside the room or its holdout neighbour sees the final doorway of **both** routes.
- Count the rooms where one shooter holds both. This is §6's "converge immediately under the same shooter", pure Python over the specs. Its results should be read beside item 2's width census.

**5. Density as a band, per kind, read beside its cost.** Walker direction 1; guide §8-9; question k. **Owner: Deli Counter.**

- Keep the floor-share-by-kind census in `docs/findings/` as the baseline any per-kind share target is set against: p10, median, p90 and in-band share. This pass's one-off reading: 652 / 43 / 6 below, in and above 12-25 % over 701 rooms.
- Add `docs/findings/denser_rooms_148/furnish_census.py`'s count beside it, and item 1's traversal cost.
- **The rule it encodes.** Share rises only through rows of primary furniture; 148 refuted raising counts. A share gain is not reported without its path-length and narrowest-width change.

**Also found, smaller, each worth a line in the roadmap:**

- **Interaction approach.** The objective and loot radius is 1.2 m from the piece's **centre** with no half-extent (`level_design.py:784-786`). The guide's interaction approach is pose + approach + exit.
- **Ladders counted as full links.** `VERT_DEAD_END` counts a one-at-a-time ladder as a full second link (`combat_audit.py:298-313`).
- **LF's stale crossing.** The sightline advisory crosses at 1.2 (`level_factory/packages/validation/sightlines.py:48-59`), and the contract's note about Lot is stale (`agent_contract.json:51`).
- **Locked doors.** Doors marked locked count as walkable in every reachability check.
- **No room-purpose guard.** A recipe whose anchor fails is silently topped up with cartons (`level_design.py:5582-5602`).
