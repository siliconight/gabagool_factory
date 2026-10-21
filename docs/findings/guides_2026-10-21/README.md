# Three documents, chased: the retopology TDD, lived-in levels, and floor plan to 3D layout

**A third, the same afternoon** (the walker: "add this to the roadmap to make our floorplan tool better and acheive
that Exploded axonometric view, with architectural cutaways"): *Floor Plan to 3D Layout and Automap Guide*, filed at
`docs/reference/Floor_Plan_to_3D_Layout_and_Automap_Guide.md`, unchanged. Its chase is `floor_plan.md` -- what the
floorplan tool (`deli_counter/floorplan.py`) draws, what a 3D view would read, and what exists of the guide's
exploded view, automap and connectivity graph -- the claims roadmaps 293 to 295 rest on read again first and marked.

The walker, 2026-10-21, shared two documents in the morning:

| document | filed at | the walker's words |
|---|---|---|
| BRPE-TDD-001 v3.0, a Blender retopology planner and executor with a Godot 4.7 runtime and MultiMesh half | `docs/proposals/Blender_Retopology_Planner_Executor_TDD_v3.0_Godot47_Runtime_MultiMesh.md` | "this should be used for zoo and deli counter big time" |
| *Lived-In Levels, Clear Navigation, Good Gunfights*, a design standard for a 1-4 player co-op PvE shooter in 1999 Pennsylvania | `docs/reference/Lived_In_Levels_Clear_Navigation_4P_PVE_1999_PA.md` | "this should directly address the last topic, around finding the balance of lived in levels that look real and not barren, but prioritize navigation and fun" |

The second answers the walker's two directions of the same morning: rooms neither crowded nor barren, and above all
"a lived in world that feels real when you are in it, but still is a video game, that prioritizes the fun and the
game of free nagivation and fun gun fights".

Each was checked against the repositories by a read-only research pass, kept here as given -- the lived-in report's
first person put in the repository's voice, nothing else changed -- with the instruments it wrote beside it:

| document | the pass's report | its instruments |
|---|---|---|
| the TDD | `retopo_tdd.md` | `retopo_tdd/` (run from the scratchpad they were written in; each takes its paths as arguments or reads the cold-9370 package named in its docstring) |
| the lived-in guide | `lived_in.md` | `lived_in/widths.py` (argv[1]: `deli_counter/agent_contract.json`) |

The reports' claims are theirs, each marked as read or inferred. A step taken on one re-reads its source first
(CLAUDE.md, Verification).

## Read again before anything was filed

Neither pass's word was taken for these; each was read or measured again in the session that filed them:

- **Every material double-sided.** 134 GLBs in cold run 9370's package, 410 materials, all `doubleSided: true`, 376
  opaque. Zoo sets `use_backface_culling` only to False, on cards (`zoo_keeper/bpylayer/materials.py:831`, `:849`).
- **The package names the wrong tools.** `LF_MANIFEST.json`'s `tools` block reads Deli Counter 0.241.0, Zoo 1.117.0
  and Level Factory 0.227.0; `_runs/cold/cold_9370/before.json` `versions` reads 0.248.0, 1.120.1 and 0.228.0.
- **Furnish's 0.9 m margin** is `_seed_clear`'s per-axis box test (`deli_counter/level_design.py:794-795` at 0.249.0),
  under the bake's 1.00 m door floor and the contract's 1.10 m corridor.
- **No instrument compares a route with and without furniture** (grep over Deli Counter, Level Factory and Lot: the
  only hits are a stair's AI cost multiplier and a box-inflation comment).
- **Two sightline crossings.** Level Factory's advisory sights from 1.4 m (`packages/validation/sightlines.py`) and
  crosses at 1.2; Laser Tag sights from 1.6 for both sides (`LT_TestScenario.gd:38`, `:58`), Lot carries 1.6 and 1.3
  (`lot/site_cover.py:63`, `:70`), and the contract crosses at 1.3 -- its note that "Lot still carries 1.2" is stale.
- **A shot into a teammate is a hit.** `LT_MetricsCollector.gd`'s match counts `FRIENDLY_HIT` in `shots_hit` through
  its default branch.

## What they come to

- **Neither moves interventions-per-level**, which the cold runs hold at 0. The TDD is frame cost on hardware nobody
  here has measured. The guide is the "good" gate (roadmap 18) on the walker's own first priority, the fight and
  free movement, where nearly every instrument the factory has is single-body and asks reachability alone.
- **The TDD's retopology core has nothing to act on in what Zoo and Deli Counter ship.** Zoo builds from primitives
  -- a 2 m wall module is 12 triangles -- and Deli Counter's boolean-cut walls never draw; every primitive arrives as a
  triangle list. Its one customer would be Zoo's ingest path, which no level uses. What the walker asked of it --
  Zoo and Deli Counter, "big time" -- lands on its runtime material contract instead: back-face culling (roadmap 285)
  and a shadow class per asset (286), both every-asset changes in those two repositories.
- **The guide's first-ranked gap was measured the same day**: what furnishing costs a route, with and without what
  furnish and the shelter pass stand (`docs/findings/furnish_route_cost/`, roadmap 288). Its first reading was on
  this morning's own change, Deli Counter 0.247.0's corner-store rows.

## Filed

| item | from | what |
|---|---|---|
| 285 | TDD | back-face culling off on every surface (Zoo, Deli Counter; Level Factory's merge key read first) |
| 286 | TDD | nothing decides which meshes cast shadows |
| 287 | TDD's surprise 2 | the package manifest names the release pins, not the tools that built it |
| 288 | guide, rank 1 | what furnishing costs a route -- measured |
| 289 | guide, smaller | Level Factory's sightline advisory crosses at 1.2 |
| 290 | guide, ranks 2-3 | Laser Tag: a teammate hit counted as a hit; shots a teammate denied and simultaneous attackers uncounted |
| 291 | guide, rank 4 | a second route can end under the shooter holding the first |

**On record already, not filed again:** the dressing as four site-wide MultiMeshes (roadmap 266's question,
`docs/DRAW_CALL_BUDGET.md` gap 1); a four-player congestion check, static first (roadmap 245's LEFT); the guide's
rank 5, density as a band per room kind read beside its cost, is roadmap 148's residue with 288's measure beside it.

## Questions only the walker can answer

From the TDD's pass: which mesh classes may stop casting live shadows; whether small props may pop out at distance
(visibility ranges), LOD having been left out on 2026-09-26; which machine is the low-end GL Compatibility target;
whether the retopology planner should be built at all, given its one customer.

From the guide and the census: whether a corner store's selling floor stays single file between its rows -- the
contract's 1.25 m aisle, the walker's "lanes open" floor -- or keeps one cross-aisle two abreast, the guide's market
("a broad cross-aisle and at least two tested ways around the central fixtures"); 288 has the numbers either way.
