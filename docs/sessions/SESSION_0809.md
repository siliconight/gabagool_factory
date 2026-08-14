# Session 2026-08-09 — the ladder, closed; two cache/mirror defects fixed

Deep dives: **`SESSION_0809_LADDER.md`** (the ladder, five refuted hypotheses)
and **`LASERTAG_STAGES_A_STALE_SCENE.md`** — which is now a **retraction**. Its
original claim (that Laser Tag grades stale scenes) was false; it is kept
because the way it went wrong is instructive. This file is the state of the
tree and the handoff.

**Use the CLI before reading directories.** `lf validate <mission>` prints every
finding with code, severity and suggested fix. `lf diagnostics <job>` says in
nine lines whether a job ran at all. An hour went into inferring from file
listings what those two verbs state directly.

---

## State of the tree

Four changes landed and are verified. Two patches remain built and held.
`SESSION_0808.md`'s state-of-the-tree note is superseded by this section.

### Applied and verified

| patch | file | bytes | evidence |
|---|---|---|---|
| `patch_dc_roof_voids.py` | `deli_counter/roofs.py`, `deli_counter.py` | 2,823→5,200 / 125,456→127,164 | `test_roofs.py` 11 `[ok]`; rebuilt shell's roof slot carries 2 voids |
| `patch_zoo_roof_plate.py` | `zoo/.../arch.py`, `kit.py`, `recipes/_arch.py` | 18,394→19,505 / 15,721→15,729 / 5,360→5,865 | zoo suite 276 passed 2 skipped |
| `patch_dc_plate_roles.py` | `deli_counter/themed_tscn.py` | 20,557→20,565 | `test_mirror_agreement.py` green; sha `e7bd2ede…eea98`; sidecar `.pre_plateroles` |
| `patch_lf_presentation_probe.py` | `level_factory/adapters/presentation/__init__.py` | 20,618→21,886 | `pytest tests/unit` 572 passed; sha `2cbb30de…94cc7c`; sidecar `.pre_dcprobe` |
| `patch_lf_source_library.py` | 10 files (item 7) | `building_library.py` 18,467→24,641 | **594 passed**; index 134→123; `test_source_library.py` created |
| `patch_lf_seal_honesty.py` | `ground_contact.py`, `spawn_placement.py` | 19,766→21,006 / 25,236→30,044 | **601 passed**; `test_seal_honesty.py` 7 cases; sidecar `.pre_sealhonesty` |
| `patch_lot_crew_spawn_clearance.py` | `lot/site_spawns.py`, `lot/lot.py` | 35,391→39,596 / 95,481→96,061 | `--verify` passes; sidecar `.pre_crewclear` |
| `patch_lf_lasertag_timeout.py` | `level_factory/adapters/laser_tag/__init__.py` | 13,306→15,014 | 8→600 s, 25→1620 s, 50→3120 s; sidecar `.pre_lttimeout` |
| `patch_lf_site_shapes.py` | `site_variation.py`, `commands/__init__.py` | 17,038→23,530 / +118 | **601 passed**; `--verify` 4 checks; sidecar `.pre_siteshapes` |
| `patch_dc_greybox_palette.py` | `deli_counter/deli_counter.py` | 127,164→132,991 | 9 materials, **0 visual unpainted**; sidecar `.pre_gbpalette` |

New instrument: **`test_mirror_agreement.py`** (13,252 bytes) — spans
`deli_counter` and `zoo`, discovers mirrors from `themed_tscn.py`'s own
`#: Mirror of …` comments, compares signatures before values, and has no skip
path. Run it from the factory root.

**Item 7's detail.** Ten files patched,
`building_library.py` 18,467 → 24,641, `test_source_library.py` created,
**594 passed** with zero failures. The live index went 134 → 123 and the run
now names what it dropped:

```
[site] 11 entr(y/ies) ... are not source archetypes and were not offered to the
       lot: gs_facade_rowhome, gs_facade_storefront, lf_art_probe_001_5017,
       lf_category5_baie_dore_001_5017, lf_category5_baie_dore_001_5118
```

The greybox pool shrank by eleven; the themeable count stayed at 97, so the
themed pool was unchanged and its per-archetype art jobs all cache-hit — the
prediction held.

**Test baseline is 594, not 593.** Both `run_0809.ps1` and
`patch_lf_source_library.py`'s own banner say `593 passed, 1 skipped`. That
count predates today. Correct them rather than re-deriving the discrepancy.

### New instruments

**`probe_reach.py`** (11.4 KB, factory root). Draws the walkability field the
`JOB_PREFLIGHT_REFUSED` blocker is computed on — `spawn_placement.heightfield`
and `walk_distances`, the gate's own functions on the gate's own boxes, so it
cannot disagree about geometry. Lists the opaque colliders by name, gives a
verdict and walking distance per mission point, and prints a plan view:

```
+ reachable   o standable but SEALED   # solid   ~ other storey   . nothing
S crew        O objective              D reachable dest           E stranded
```

`--selftest` walls a yard and then cuts a 12 m doorway in it; it fails unless
the first seals and the second walks. `--cell N` for resolution.

This is what turned "something seals Route_2" into "the extraction is 2.2 m
inside `cr_garage`" in one run, after four wrong guesses from file listings.

**`probe_sightlines.py`** (14 KB, factory root). Measures the longest run of
open ground across a site, from the site spec alone — no engine, no bake,
milliseconds. Sweeps lines at 12 directions and computes open runs by exact
interval arithmetic against each footprint. Calibrated in both directions:
a plate under a shell reads 0 m, an empty 200 m corridor reads 200, the same
corridor with one shell across it reads 80, and a flush row reads 304 m against
an L's 192 m from the identical five shells.

`--selftest` must pass before any number it prints is worth reading.

**Baseline for `lot_demo_001`, three candidates, all `site_shape street_row`:**

| candidate | longest lane | direction |
|---|---|---|
| seed_5017 | 287.0 m | 0.0 deg |
| seed_5118 | 299.0 m | 0.0 deg |
| seed_5219 | 247.0 m | 0.0 deg |

**Every longest lane on every candidate is at 0 degrees** — straight down the
row, past every front door, 5.5x to 6.6x the 45 m at which the crew's bot opens
fire. Yaw, nudge and stagger move the length and never the direction, because
the row *is* the lane. The selftest's L cut the same five shells from 304 m to
192 m and moved the direction to 45 degrees.

`longest` is the comparable number. The count and total metres scale with plate
area, and `ground_size` sizes the plate from the placement.

### Built and HELD — unapplied

* **`patch_map_derived.py`** (30,203 bytes). `PIPELINE_MAP.md` drift is
  measured and unfixed: `walktest_navqa` and `themed_site_assemble` absent,
  `lux_apply` documented `← presentation_compose` but actually
  `← themed_site_assemble`, `patina_apply` outputs wrong, and "runs once on the
  selected candidate only" false for six stages.

---

## The verification rule this session produced

**Three artefacts or it is not verified.** For any change that should reach the
level:

```powershell
python $LF run lot_demo_001 --art      # the pipeline
python $LF walk lot_demo_001 --play    # REBUILDS the preview -- nothing else does
Select-String -Path "$SITE\site.tscn" -Pattern "art/zoo/<module>"
Get-ChildItem $ART -Filter "<module>*" | Select-Object Name, Length
Get-Content "$PREVIEW\walkbot.json"
```

Two traps, both hit today:

* **`run --art` does not write the preview.** `walk_preview.build_preview`
  `rmtree`s and rebuilds `preview/<mission>_walk` from scratch, and only `walk`
  calls it. Reading that tree after a run reads the *previous* walk.
* **`walkbot.json` cannot distinguish a fixed roof from an absent one.** Both
  report `climb: true, top_exit: true` and `void 52.66%`. Check the scene
  reference and the `.glb` beside it, every time.

---

## What's next, in the order I'd take it

**0. The blocker on `lot_demo_001` — RESOLVED, and it was a FALSE REFUSAL.**

`walktest_navqa` walks the route on the real baked navmesh with no combat in
it, and it passes:

```
walker player_0: ok (18/18 targets, 874.8 m)      verdict: PASS
walker player_1..3: ok (18/18 targets, ~875 m)    stranded_anchors 0
walker bot_0..bot_11: ok (1/1 targets)            anchors_behind_a_barrier 0
```

**The level is sound.** `cr_garage`'s extraction is reachable; every anchor has
standing room; nothing is behind a barrier. So `JOB_PREFLIGHT_REFUSED` would
have refused a build on a working level, and `patch_lf_seal_honesty` was
correct — the seal existed only in a reader that reduces every collision mesh
to its bounding box and therefore cannot see a doorway. Independent instrument,
same answer.

`LT_ROUTE_NEVER_COMPLETED`'s own text said to read this first. It took six
hours to do so.

**What actually fails now** is Laser Tag's bot, not the level. Every run
stalemates for its full 180 s: nobody arrives, nobody dies. The mechanism is in
the pipeline's own advisories and has been all along —

```
LT_OPENING_STANDOFF   1 enemy spawn within 45 m of the player spawn (Enemy_0 at
                      32.0 m) — the crew's bot stops walking the moment it can
                      see an enemy, so this also costs the run its route completion
LT_ENGAGEMENT_NOT_CONFIGURABLE   the crew's sight range (45 m) is an @export
                      default on LT_BotPlayerController the harness never assigns
```

— and `patch_lf_lasertag_timeout` turns the resulting `JOB_TIMEOUT` blocker
into a graded FAIL, which is a design finding rather than a build failure. The
grade stays 47/100 until the bot or the standoff changes.

<details>
<summary>The original diagnosis, kept for the trail</summary>

```
[BLOCKER] JOB_PREFLIGHT_REFUSED (configuration)  candidate.seed_5017
  1 of 3 mission destination(s) cannot be walked to from the player spawn:
  Route_2 is sealed off from the crew spawn
  fix: Fix the input the pre-flight named, then re-run the stage.
```

Item 7 changed 5017's lot; the new lot places the extraction where the crew
cannot reach it; the pre-flight refused the job before spending 900 seconds.
**That is the system working.** `laser_tag_evaluate.candidate.seed_5017` has
never executed against this lot — `diagnostics` shows `started_at: null`,
`command: []`, `exit_code: null`. It is deterministic from the seed, so
re-running will never clear it. 5118 and 5219 are unaffected.

**Measured, with `probe_reach.py`:**

```
spawn      b3  strip_retail_a01   site ( 67,  0)   0.0 m      [ok]
objective  b2  supermarket_a01    site (-10,-27)   93.7 m     [ok]
Route_2    b0  cr_garage          site (-88, -4)   SEALED
924 boxes, cell 0.5 m, not coarsened, 69,897 reachable cells
```

`cr_garage` footprint **36.35 x 28.35** at rot 90, so it spans x −114.2…−85.8.
`Route_2` sits at x −88 — **2.2 m inside its east wall**, on clear interior
floor, in a pocket the flood fill never reaches. `Route_2` is the third element
of Lot's `[spawn, objective, extraction]` route: the extraction.

**Why nothing caught it.** Lot has two destination guards and both correctly
pass this point:

| guard | fires when | here |
|---|---|---|
| `LOT_DESTINATION_RESEATED` | hook is **above** the floor | it isn't |
| `LOT_DESTINATION_RESOLVED` | hook is **inside a prop** (`resolve_onto_floor`, `outcome.needed`) | it isn't |

The hook is on clear floor, inside a building whose interior the crew cannot
enter. **Nothing in Lot checks whether a destination is reachable from the crew
spawn** — Level Factory's pre-flight is the only thing that computes it, and it
does so after the fact, as a blocker.

**The fix (in the `lot` repo, not here).** `site_collision.resolve_onto_floor`'s
acceptance test should be *"floor an agent can stand on **and reach from the
crew spawn**"* rather than just "stand on". Same nearest-first push, same
finding vocabulary, one stronger predicate. `site_enterability.py` (9.3 KB,
unread) may already hold the connectivity primitive. Read that and
`resolve_onto_floor` before writing anything.

**Cheaper alternative that also unblocks:** implement candidate rejection
(roadmap I). 5118 and 5219 graded fine; one bad candidate should not stop a
mission that has two good ones.

**Refuted along the way** — the four opaque colliders named in the finding
(`site.tscn:path_1/col`, `path_2/col`, `path_3/col`, `Player/col`) are **not**
the seal. The paths are rotated `BoxShape3D` decals, 0.014 m thick at y 0.005,
laid over a ground plate the reader models fine. They fall out of the field only
because `Box` is axis-aligned and they carry a yaw. Worth fixing for model
completeness; it would not change this verdict.

**Also refuted, from the same thread.** The crew spawn was NOT trapped in the
navmesh erosion band. Both stuck clusters sat exactly on the spawn — x 65 with
the spawn at 67.0, x 70 with the spawn at 67.5 — and the apparent two-metre
move into a building was **my own 5 m bucket boundary flipping**, nothing more.
The bot never moved at all, in either configuration.
`patch_lot_crew_spawn_clearance` closes a real gap that `WALL_MARGIN`'s comment
documents, and it did not cause or cure this.

</details>

**1. Layout — APPLIED and DORMANT. Turn it on.**
`patch_lf_site_shapes` landed: `layout_offsets(shape, footprints)` with `row`
**delegating** to `row_offsets` (one implementation, cannot drift), plus `L`
and `courtyard`. Verified over 250 seeds each, `overlapping()` and
`uncovered()` both empty — which matters because `_write_site_spec` RAISES on
them. Spans: `row 216 x 0`, `L 100 x 132`, `courtyard 100 x 70`.

**Nothing has changed yet.** Every spec still reads `site_shape street_row`,
and 400 seeds confirm an unset or `row` shape places byte-identically, so no
graded candidate re-rolled. To use it, set `site_shape` on the brief:

```powershell
Get-ChildItem "$WS\.level_factory" -Recurse -Include *.json |
    Select-String "site_shape" | Select-Object -First 10 Path, Line
```

Current row baseline for the post-item-7 lot, from `probe_sightlines`:
**271 / 351 / 309 m, every one at 0 degrees.** (Note 5118 reads 351 greybox
against 309 themed — roadmap J showing up inside the measurement; compare like
to like.) The x-span drops 216 → 100, so the longest lane should fall well
under 271 m and, more importantly, **stop being at 0 degrees**.

**1-r. Greybox readability — APPLIED.** `patch_dc_greybox_palette`. Deli
Counter assigned **no material to anything**: no `materials.new`, no
`data.materials.append`, no `diffuse_color` anywhere in the repo, so the shell
exported an empty glTF material list and every surface rendered as one flat
default. Not a theming gap — an absence.

`surface_roles` has labelled all 192 surfaces the whole time and nothing
consumed it for looking. Eleven roles now carry a shared material each,
assigned at the two sites that already write the role. On `bank_branch_a04`:

```
gb_stair 66   gb_wall 18   gb_ladder 16   gb_window 6   gb_floor 4
gb_breach 4   gb_prop 4    gb_threshold 3  gb_ceiling 1
unpainted: 47 collision (correct), 0 visual
```

**Stairs and ladders are 82 of the 122 painted primitives** — two thirds of
what you look at, and both are the affordances that say where you can go.

The palette is checkable, not asserted: `--palette` measures relative luminance
between the pairs that actually SHARE A VIEW (a stair against the floor it
rises from, a doorway against the wall it is cut into) and fails under 0.15.
The first draft put stairs at 0.564 against a 0.522 floor — a gap of 0.042,
which is amber and grey reading as one surface in greyscale, in low light, or
to a colourblind player, on the single case the palette exists for. Hue was
doing work value should have been doing.

`gb_roof` is inert on this building: `bank_branch_a04` has no surface labelled
`roof`. Worth a glance at what its top slab IS labelled, given the morning.

Next slice: bind pixelcoat packs to these nine material names — `gb_stair`
with hard horizontal tread banding earns its cost first, because repeated
horizontal edges are what make a thing read as climbable at fifty metres. That
slice needed named material slots to bind to and there were none; now there
are. Then the same table in Lot for `perim_*` / `Ground_*` / path decals, which
carry no roles and need names inventing.

**Two metrics that work RIGHT NOW**, and neither depends on the bot completing
a run, so layout changes are measurable while the stalemate stands:

* `probe_sightlines` longest lane — 287 / 299 / 247 m, every one at 0 degrees;
* Laser Tag's own sampling — `LT_MAP_OVEREXPOSED_ZONE` at 48-50%, and
  `LOT_COVER_PLACED` compensating for a **140.3 m** open sightline.

**1a. Enemy standoff: two numbers for one rule, in one file.**
`place_enemies` enforces `MIN_STANDOFF = 8.0`; the grader punishes anything
inside `MIN_ENGAGEMENT_STANDOFF = 45.0`, and the crew's bot halts on sight at
45 m. `opening_engagement_is_fair` allows a close enemy when a building
occludes it — Enemy_0 at 32 m was admitted on exactly that grounds — so the
occlusion test and the engine disagree somewhere. This is the likeliest single
cause of every run stalemating and it is in Lot, where we can reach it. Pairs
naturally with the layout work: a staggered site both shortens the lanes and
changes where an enemy may legally stand.

**1b. The Laser Tag bot.** `LT_BotPlayerController` halts on sight and its 45 m
sight range is an `@export` default the harness never assigns. Laser Tag's own
repo, untouched this session. **Nothing improves the grade until this or 1a
lands.**

**1c. The layout evidence, in-engine and current.** From `lf validate`:

```
LOT_COVER_PLACED        12 piece(s) of 2 m cover placed to break sightlines the
                        site left open past 45 m (longest 140.3 m)   seed_5118
LT_OPEN_SIGHTLINE       Enemy_3 and Enemy_5 see each other across 46.5 m of open
                        ground, past the 45 m at which Laser Tag opens fire
LT_MAP_OVEREXPOSED_ZONE 21% of walkable positions visible to 3+ enemy spawns
LT_MAP_TRAVERSAL        Bot rarely completed the route (0% of runs)  5118 + 5219
```

Lot is already placing cover to compensate for what the layout leaves open —
140.3 m at the worst. This is the pipeline's own instruments agreeing with
`probe_sightlines`' spec-level numbers, on the real levels.

**1. The dangling `ext_resource` gate.** *(highest value / lowest cost)*
`site.tscn` named a `.glb` no job produced and it survived compose, assemble,
the sweep, a nav bake and `blockers open: 0, total findings: 54`. It was caught
by a bot walking into it two days later. `_themed_available` already does the
check and its first branch is `if not library_dir: return True  # trust the
plan`. Roughly ten lines at the stage that writes the scene turns this whole
class into a failed build. **Nothing else on this list prevents a recurrence;
this does.**

**1b. A failing candidate should be rejected, not block the mission.** 5017
failed; 5118 and 5219 graded fine and are sitting there usable. `Candidate`
already carries `status`, `rejection_reason` and `selected` — the vocabulary
for "this one is bad, use another" is in the model. N candidates exist so some
can be bad.

**1c. Greybox and themed are different levels.** Same seed 5118, four of five
archetypes differ and all five positions differ:

```
grey   b0 final_stand   b1 supermarket_a01  b2 pharmacy_a02          b3 depot_a01        b4 lf_lot_demo_001_5017
themed b0 rail_station  b1 supermarket_a01  b2 construction_site_a03 b3 bank_branch_a04  b4 funeral_home_a03
```

`require_themed_shells` narrows the pool 134 → 97 on the themed path only, and
the comment says why: *"NOT applied to the greybox branch. That places levels
already built and graded, and re-selecting them would be different levels
wearing the same grades."* It bought grade stability at the cost of grade
validity — Laser Tag grades the greybox, the themed one ships. Fix: select from
the pool of buildings that can complete the whole pipeline, so both branches
agree by construction. Costs one re-roll.

Related and unresolved: `planner.py` says *"`lot_for` is the one selection rule
— the compose spec and the site spec call the same function"*, but
`_write_site_spec` calls `index` / `require_themed_shells` / `pick_lot` inline
rather than calling `lot_for`. Both statements cannot be true.

**2. Apply the remaining held patch.** `patch_map_derived.py`, with
`--check`/`--revert`.

**3. Nav-gate re-bake for `bank_branch_a04`.** Its `.navgate.json` describes
pre-rebuild geometry and themed selection *reads that verdict* rather than
recomputing it. Needs `DC_GODOT`; check `nav_gate.py --help` for a single-shell
form before running `--all`.

**4. The `--sweep` summary line.**
`bad = sum(1 for _, r in rows if r["error"] or r["mismatch"] or r["missing"])`
counts unreadable packages as "disagree with their slots", contradicting the
function's own docstring. Re-run the sweep afterwards — the 3-of-8 number has
not been re-measured since the roof landed.

**5. The other copies of the plate constants.** `_bridge_fresh/arch_v2.py:27,34`
and `_bridge/sw_0730a.py` hold pre-patch `_SOLID` / `PLATE_SPECIES`. Establish
whether anything imports them. If they are live, they belong in
`test_mirror_agreement.py`; if they are dead, they belong in the bin.

**6. Item 8 — sidecar cleanup.** Session-scoped `.pre_*` files are accumulating
at the factory root and in every repo. Also at root: `probe_roof.glb` (189,620
— the bridge-workaround copy of the orphan) and `walkbot.before.json`.

```powershell
Get-ChildItem $FACTORY -Recurse -Include *.pre_* | Select-Object FullName, Length
```

**7. By eye, still owed.** Stand on the roof of `bank_branch_a04` and look at
the deck around the hole. Every instrument in this session reports the same
value for a correct roof and for no roof.

---

## The lesson this session actually taught

Five hypotheses died on the ladder, three more on the blocker, and every one
was killed by a cheap measurement after expensive reasoning. The pattern was
identical each time: **a stale or partial artefact read as evidence about a
live process.**

* a directory only written by `walk` looked stale, and was read as a stale
  pipeline;
* a job that never ran left an old staging dir, and it was read as a gate
  grading leftovers;
* a reader that cannot see doorways reported a seal, and it was read as a
  sealed level;
* a 5 m histogram bucket moved when the spawn moved 0.5 m, and it was read as a
  bot walking into a wall.

The tools that settled each one in a single command: `lf validate`,
`lf diagnostics`, `walktest_navqa`'s report, and `probe_reach`. **Ask the tool
what happened before reconstructing it from its leavings** — and when a finding
says "read that first", read that first.

---

## Handoff notes

* `deli_counter/build/bank_branch_a04.slots.json` sha256
  `163AD68298EEA325051872A3EDAA161FB0E140EB413B681EA6C46248862CB5E3` — the
  file both `zoo_kit_build` and `presentation_compose` read. Confirmed
  identical for both; if they ever diverge, that is a new defect.
* The verified roof module is
  `roof_rockay_01_w4000_d3000_v72fc6e.glb`, **229,240 bytes**.
* `cache forget` has now run on hardware. Its first real use was covering for
  the fingerprint defect fixed in this session — worth remembering when judging
  how well tested it is.
* **Timestamps in `.level_factory/` are meaningless.** The cache hard-links
  byte-identical outputs, so a restored file carries the cache entry's mtime.
  Filenames and hashes are evidence; mtimes are not.
