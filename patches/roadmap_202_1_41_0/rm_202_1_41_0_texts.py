"""Texts for patches/patch_roadmap_202_1_41_0.py: roadmap 202's status and a paragraph for factory 1.41.0's three
install tests, a head on item 266's status for the merge's regression, and items 270, 271 and 272."""

STATUS_202 = (
    "*STATUS: NARROWED 2026-10-20 -- the path a stranger follows is certified a sixth time, with no deviation from "
    "the page: install test 12, at the set factory 1.41.0 certifies (Deli Counter 0.241.0, Dispatch 0.5.3, Level "
    "Factory 0.227.0, Lot 0.126.0, Lux 0.79.0, Patina 0.32.0, Zoo 1.117.0, the other three as 1.40.0), @@INSTALL12@@ "
    "It took three tests, and the first two found what no cold run could: install test 10 stopped at the export on "
    "a parking garage's ramp cut (Deli Counter 0.241.0, `docs/findings/ramp_cut_241/`, cold run 9356), and install "
    "test 11 shipped that level and its walk found no ladder -- Level Factory 0.223.0's buildings' merge had removed "
    "every building's ladders and markers (Level Factory 0.227.0, `docs/findings/merge_ladders_227/`, cold run "
    "9357). @@RELEASE@@ The assistant's notes travel too: `docs/sessions/agent_memory/`, `tools/agent_memory.py` "
    "(the walker, 2026-10-20: a new PC loses no progress). Left: a Linux run -- the walker has no Linux machine "
    "(2026-10-11), so `factory.sh` and START_HERE.md's Linux lines are written and unproven -- item 256, and item "
    "272, the gate that would have caught the merge's loss before an install test did.*"
)

BODY_202_ANCHOR_END = "wrapt 2.5.0 -> 2.5.1 in two days (item 256)."

BODY_202 = (
    "\n\n**INSTALL TESTS 10, 11 AND 12, 2026-10-20: factory 1.41.0** (`docs/findings/stranger_install/`). The walker "
    "asked for a fresh release that afternoon, so that a new PC would lose no progress. Every repo was already "
    "pushed; what a new PC would still have lost was the assistant's notes, and they went into this repo first "
    "(`docs/sessions/agent_memory/`, 128 notes, a restore into an empty folder checked identical). Test 10 "
    "(17:25, Level Factory 0.226.1) stopped at the export: the first level's seed is left to the pick, the pick "
    "took seed 9205, whose lot stands a parking garage, and the garage's ramp cut ran half a run past the ramp's "
    "head -- 33 undeclared drops the gate refused, and every library ramp did the same. No cold run since the "
    "gate shipped had drawn a garage: they named seed 9003. Test 11 (18:41, Deli Counter 0.241.0) shipped that "
    "level and its walk printed \"walk bot: no ladder_area3d in scene\": the morning's merge removed every "
    "building's `Ladders` and `Markers`, and eight cold runs (9349 to 9356) passed every gate over it, because none "
    "counts a group and the cold drive's walk step builds the walk copy without the walk's self-check (item 272). "
    "@@TEST12@@ Each fix was counted before it was chosen and proven on the level that failed, at 0 interventions; "
    "neither loss reached a release."
)

HEAD_266 = (
    "NARROWED 2026-10-20 -- A REGRESSION IN IT, FOUND AND FIXED: from Level Factory 0.223.0 to 0.226.2 the merge "
    "removed every enterable building's `Ladders` (Deli Counter's Area3D climb volumes) and `Markers` (the grouped "
    "spawns, objectives and cover a game finds by group) with the slots it took apart, and eight cold runs (9349 to "
    "9356) passed every gate over it; install test 11's walk found it (\"no ladder_area3d in scene\"). Level Factory "
    "0.227.0 (2592e7a, `patches/patch_lf_merge_carries.py`) keeps a slot holding what the merge cannot carry whole "
    "-- outside a static body, a node neither a mesh nor a bare Node3D, or any node with a group of its own or "
    "metadata -- counted first on two levels' packages (`docs/findings/merge_ladders_227/`: 9 slots of 1,753 kept, "
    "2 surfaces); cold run 9357 (0 interventions) merged 864 slots where 9356 merged 868, every other count of the "
    "merge 9356's, and its package carries deli_a01's 2 ladders and the level's 29 markers. Item 272 is the check "
    "that would have caught it. Earlier status kept: "
)

ITEMS = """
*STATUS: OPEN 2026-10-20 -- measured (`docs/findings/ramp_cut_241/`), not started; Deli Counter 0.241.0 fixed what the drop-edge gate refused and left this.*

**270. A ramp's cut begins where a body still meets the slab, and furnish does not read a ramp.** Found fixing the cut install test 10 stopped on (Deli Counter 0.241.0, `docs/findings/ramp_cut_241/`). Every library ramp's slab cut begins at the ramp's middle, and there the clearance between the upper slab's underside and the ramp's top face is 1.04 to 1.55 m on all nine (`ramp_census.py`, `ramp_census_0240.out.txt`) -- under a body's 1.8 m and the agent contract's `min_headroom_m` of 2.0. A body walking up a library ramp meets the slab's edge, so no ramp carries anyone between storeys; the stairs do. The contract's rule would open each cut 1.4 to 3.2 m further down its ramp, but `level_design`'s furnish keeps pieces off authored `slab_holes` and never reads a ramp's cut, so the longer cut would stand under furniture: foundry_heist_vertical's forklift (authored) and pallets, cbp_town_finale's chairs, each found on a rail's line by the 0.241.0 build. A ramp's own sides below its cut are open too: on the garage cold run 9356 shipped, one edge remains round the ramp, its west side 2 m up from its foot, 0.75 m to the floor beside it (`garage_rows_cold_9356.out.txt`; on 0.240.0 the sides by the overshoot dropped 2.4 to 2.7 m, and 0.241.0's rails guard the cut's length) -- Level Factory's gate reports it, a ramp not being floor-like, and does not refuse it. **What would close it:** furnish keeps a piece off a ramp's cut as it does off an authored hole, then the cut begins where `min_headroom_m` says, the six ramp specs refurnished and rebuilt, a walk test showing a body climbing a library ramp from one floor to the next, and the walker's call on a ramp's sides -- walls as a stair's flight has, rails, or open.

*STATUS: OPEN 2026-10-20 -- measured on cold run 9355's price (`docs/cold_runs/cold_9355/NOTES.md`, "The price"), not attributed.*

**271. The price drifts between sessions on identical bytes.** Pricing cold run 9355 against 9351's runs of four hours earlier read 184 fewer draws, 0.67 to 0.99 ms a heading more at p95 and 14 MiB less video memory, for a change that only adds texture. Priced again in one session, on bytes that had not changed: the morning package of 14:08 read the same draws and +0.61 ms a heading (its floor 0.10); 9351's own bytes, rebuilt from the walk copy, read 92 fewer draws at two evening headings than they did at 12:37; and buffer memory, 61.6 MB on 9351's and the morning package's runs before 14:15, read 44.6 to 48.8 MB after -- and it moves between runs of one package in a session too: the noon package's two runs at 14:10 and 14:14 read 57.4 and 59.5. Texture memory never moved on the same bytes, and day draws held. Until this is attributed, a price compares arms run in one session, in turn, alone, and reads `texture_mem_bytes` for a package's memory -- 9355 rebuilt its control in-session for that reason (`docs/cold_runs/cold_9355/make_hybrid.py`). **What would close it:** the harness writes into every report what could move it -- the window's real size, the display's resolution and scale, the GPU's clocks and power state, what else is running -- and a drift run on identical bytes, across a session boundary, attributes the 92 draws, the frame time and the buffers to one of them.

*STATUS: OPEN 2026-10-20 -- found by install test 11 (`docs/findings/merge_ladders_227/`); Level Factory 0.227.0 fixed the loss and left the check that would have found it.*

**272. Nothing checks that a package carries the gameplay its composition had.** From Level Factory 0.223.0 to 0.226.2 the buildings' merge removed every enterable building's `Ladders` (Area3D climb volumes, group `ladder_area3d`) and `Markers` (58 grouped spawns, objectives and cover on the two levels counted) from the package, and eight cold runs (9349 to 9356) passed every gate at 0 interventions over it: no gate counts a group, and the cold drive's walk step (`tools/walk_export.py`) builds the walk copy without the walk's self-check, which is where "walk bot: no ladder_area3d in scene" prints. Install test 11's walk found it the same day, before any release carried it. **What would close it:** the export counts each gameplay group's nodes (`ladder_area3d`, `dc_marker`, Lux's `LuxEmit_*` markers) in the composed scenes and in the package and refuses a loss it cannot attribute -- the drop-edge gate's shape, a census of what the package is for -- or the cold drive runs the walk's self-check, at about 4.6 minutes a run (install test 11's walk).
"""
