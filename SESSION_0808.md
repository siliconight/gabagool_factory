# 2026-08-08 — marker scope, themed selection, and the first honest walk

Handoff for the next session. Read this and `deli_counter/docs/NAV_GATE_FINDINGS.md`
(the 2026-08-08 section at the end) before touching anything. **Do not
re-derive** — most of what follows cost a measurement, and several of the
measurements refuted the obvious answer.

---

## How to work on this

Three instructions from B$ that governed the whole session and still stand.

**Point at the docs, don't re-derive.** A fresh session that re-investigates
burns an hour reaching the same place. Where a number appears below, the script
that produced it is named.

**Ask B$ to run anything you can't run yourself.** Every mistake in the previous
session was on a question that needed a Blender build or a Godot bake, where
guessing felt cheaper than asking. That held today too: the GDScript half of the
nav gate change was unverifiable here and B$ ran it.

**Assumptions are the enemy.** "No guessing, no shortcuts." Four separate times
today the obvious explanation was wrong and the measurement said so.

One more, learned today and worth keeping. **Stage the repository and run its
suite before shipping anything.** The reverted patch from the previous session
broke 17 tests on B$'s machine. Today the same class of break happened again —
13 tests — but in a sandbox, because `level_factory` had been staged locally and
`pytest tests/unit` could be run before delivery. That single habit is the
difference between the two sessions.

### Environment

```
Blender   $env:BLENDER="C:\blender\blender.exe"          (not on PATH)
Godot     C:\Godot\4.7\Godot_v4.7-stable_win64_console.exe
```

* Setting `DC_GODOT` makes `deli_counter`'s pre-commit hook run the nav gate.
  **Commit from a shell without it.**
* A fresh PowerShell opens in `System32` — `cd` first.
* `lf` is not on PATH: `python level_factory\apps\cli\main.py <cmd>`, run with
  cwd = `lot-demo-ws` (the CLI refuses if it cannot find a workspace above cwd).
* Test mission `lot_demo_001`, batch `lot_demo`, workspace `lot-demo-ws`.
* The device bridge refuses hardlinked files. Job outputs under
  `.level_factory/jobs/*/out/` are hardlinked to `1/out/`; the copies under
  `.level_factory/preview/` are not, so read those.

---

## What landed

All demonstrated failing first. Every changed file has a `.pre_*` sidecar beside
it for revert — this repo's own convention (`deli_counter.py.pre_cap`).

**Deli Counter — marker scope split.** `nav_gate.gd` now reports what it
measured (`markers.detail[]`: each marker's level-space x/y, snap distance,
reachability) and writes `navigable: null`. `nav_gate.py` owns the
classification in `scope_markers()` and rewrites the manifest. Legacy
`checked`/`reachable`/`unreachable` carried through untouched so
`library_census.py` and 135 existing manifests keep meaning what they meant.
13 tests in `test_marker_scope.py`. **514 passed, 2 skipped.**
Sidecars: `nav_gate.py.pre_scope`, `godot/addon/deli_counter/nav_gate.gd.pre_scope`.

**Level Factory — themed selection.** `building_library.scoped_verdict()` reads
`navigable` off the manifest and never recomputes it; `themed_fitness` requires
non-empty slot coverage *and* `navigable is True`. `lot_for(..., themed=True)`
raises `ThemedShellsUnavailable` rather than returning a short lot. All three
callers of `lot_for` pass it — compose spec, themed site spec, **and the art
fan-out in `planner.py`**, which was missed and caught by `_art_entry`'s own
guard. `test_themed_selection.py`, 16 tests. Sidecars: `.pre_themed` on
`building_library.py`, `apps/cli/commands/__init__.py`, `tests/unit/test_fanout.py`,
`planner.py`.

**Level Factory — `walk` opens the assembled site.** `walk_content_dir()` prefers
`themed_site_assemble/out` over `presentation_compose/out/presentation`, keyed on
the *scene* not the directory, and does not branch on lot size.
`test_walk_target.py`, 5 tests. Sidecar `.pre_walkfix`.

**Level Factory — debug overlay.** `assets/godot/debug_overlay.gd`, copied into
the preview with the bots, F3 toggles, on by default. Shows position, the
instanced package under the crosshair (read from the node's own
`scene_file_path`), and the collider name and distance. Sidecar
`walk_preview.py.pre_overlay`.

**551 passed, 1 skipped** in `level_factory/tests/unit`.

---

## What landed 2026-08-09

**`module_extents.py` — three fixes to the ruler.** It read `nums[10]` and
dropped the instance basis, which is what produced the `wallEnd` finding; it
now takes all eight corners through the full transform. `--kit <dir> --slots
<file>` compares a built kit against the slots it was built from, importing
Zoo's real `plan_kit` rather than restating the naming law. `--sweep <lot>
--builds <dir>` runs that over every building, one line each. `--selftest`
covers all three readers and **asserts the clean case as well as the failing
one** — the axis bug survived a fixture that only checked that a bad kit was
flagged. Sidecar `module_extents.py.pre_basis` reverts all of it.

**Level Factory — the Zoo kit fans out per building.** `zoo_kit_build` was
planned once per mission and fed `shell.slots.json`, and its output dir was
handed to every building's compose. It now takes `archetype=aid`, reads that
building's own slots from the library row, and reaches compose through the
same per-archetype map dressing and fixtures already use. `compose()` takes
`modules` as a PARAMETER — the comment above it already said why, and
`--modules` was the last argument still read from the closed-over spec.
4 tests in `test_fanout.py`, all demonstrated failing first.
**555 passed, 1 skipped.** Sidecars: `.pre_kitfanout` on `planner.py`,
`apps/cli/commands/__init__.py`, `adapters/presentation/__init__.py`,
`packages/core/models.py`, `tests/unit/test_fanout.py`,
`tests/test_presentation_lot.py`.

**The belief was written in five places** and all five now say what was
measured: the planner's comment, `_dep`'s docstring, `Job.archetype_id`'s
docstring, `test_placement_stages_fan_out_and_libraries_do_not`, and a test
named `test_every_archetype_gets_the_same_theme_and_kit` which passed
*because* one kit went to all of them. A belief that survives in a test is a
belief with a guard on it.

**Level Factory — a build directory is not a cache.** `work_dir` is
`<job>/<attempt>/out` and attempt 1 is attempt 1 on every run, so it was reused
indefinitely — and `collect_outputs` rglobs it, so a leftover was ADOPTED as an
output of this run: published, hashed, cached, read downstream. Cleared per
attempt now, and `_publish_stable` prunes what this run did not produce.
3 tests. Sidecar `scheduler.py.pre_cleanwork`. The repo had already paid for
this from the other end — `_without_provenance` exists because the same rglob
swept up the previous run's provenance sidecars until a path passed MAX_PATH
and killed a run. That fix filtered the symptom; this one removes the cause.

**PROVED on hardware**: two planted probes (one in `out/`, one in the attempt
dir) and the real five-day-old orphan all gone after one run.

**Level Factory — `lf cache forget <job_id>`.** A cache entry records the
outputs a build produced; when the build produced the WRONG outputs the entry
is not stale, it is POISONED, and re-running cannot notice because the
fingerprint covers the inputs and the inputs did not change. Clearing the work
dir stops new adoptions and does nothing for an entry already written — a cache
hit materializes the leftover straight back. `forget` reads the digest from the
job's own `fingerprint.last.json` receipt (written for exactly this question),
drops the manifest, leaves blobs for `prune`. 4 tests. Sidecars `.pre_forget`
on `cache.py`, `apps/cli/main.py`, `apps/cli/commands/__init__.py`.

**`marker_scope_census.py --selftest`.** `_outside` IS the 2026-08-08 finding —
it replaced snap distance and moved the library from 6 themeable families to
37 — and nothing had ever put it wrong on purpose. Proved before every census.
The fixture is depot's 46x26 footprint, not a square, because a square hides an
axis swap. Sidecar `.pre_selftest`.

**RETRACTED the same day: mtime is not a staleness signal here.** `--sweep`
briefly tagged an unplanned module "5 days older than the rest of this kit;
probably left behind". The next run refuted the rule — the cache is
content-addressed, so a byte-identical module is never re-copied, is
hard-linked, and `copy2` preserves its mtime the rest of the way.
`wallEnd_rockay_01.glb` is a unit box whose content never changes, so it reads
five days old while being current and correct. The sweep now reports
`MATCHES NO PLANNED MODULE` and does not guess why; the cause is decidable at
the kit, where the index is. **A cheap observable standing in for an expensive
truth — the exact defect `CLAUDE.md` opens its Instruments rule with.**

**Level Factory — the kit is measured against its own index, by the job that
built it.** `packages/validation/kit_dims.py`, called from `ZooAdapter.
normalize_validation` when it sees a `*_kit.built.json`. Zoo's index already
states the `dims` the planner asked for and the `fit` that says how to read
them; the `.glb` beside it is what was built, and nothing compared the two.
Both are inside one job's outputs, so the check needs no slots path, no Zoo
import and no knowledge of the naming law — it cannot drift from what it
checks. `ZOO_KIT_DIMS_MISMATCH` is a **blocker**; an unmeasurable module gets
its own non-blocking finding rather than passing in silence. 9 tests.
Sidecar `adapters/zoo/__init__.py.pre_kitgate`. **564 passed, 1 skipped.**

Compares the whole (w, d, h): the wall defect was a height but the plate
collision before it was a depth, and a check that only looks at the axis of
the last bug finds the last bug. The axis mapping is `(x, z, y)` — a `.glb` is
Y-up — and the test fixture is authored Y-up on purpose, because the version of
this that read z had a Z-up fixture that agreed with it and passed. Mutating
the mapping now fails **six** tests, the clean-kit case among them.

**VERIFIED ON HARDWARE 2026-08-09.** `run lot_demo_001 --art` planned FIVE
`zoo_kit_build` jobs, one per placed building, all succeeded, and no
un-suffixed kit job exists any more. `blockers open: 0` — the new gate stayed
quiet, which is its first real statement: all five kits measured correct
against their own indexes, on Blender output rather than fixtures. Then
`--sweep`: **7 of 8 buildings disagreeing became 3 of 8**, and every rebuilt
building reads `ok`. `bank_branch_a04` walls, breaches, doorways and windows
all measure **3.900** — what its slots have asked for all along. The 0.300 m
gap under every wall in it, and the 0.700 in `rail_station_a02`, are gone.

The three still disagreeing are `depot_a01`, `pharmacy_a02` (not placed in this
lot, so their packages still hold the old shared art — 6 and 9 GLBs against 23
planned, versus 32-of-33 for the rebuilt ones) and `bank_branch_a04`, on one
prop that turned out not to be a dimension fault at all — see below.

**A leftover in a package is not a badly built module, and the sweep said it
was.** `bank_branch_a04` reported `prop_rockay_01_w160` as a mismatch. That
file is dated 08-04; every other `.glb` in the package is from the 08-09 run,
and the kit job never produced it — it built `prop_rockay_01_w90`,
`prop_rockay_04_w160`, `prop_rockay_05_w1000`. It is a five-day-old orphan that
the packaging step re-skinned and re-imported as though current. The gate was
RIGHT to stay quiet: it checks what the job built. The sweep's detection was
right and its diagnosis was wrong, and a wrong diagnosis is worse than a miss
because it sends the reader to Zoo for a bug that is not there. Now reported as
`MATCHES NO PLANNED MODULE`, with the file's age against the rest of its kit
printed beside it. Selftest case added; removing the age check fails it.

**Open, and new:** the composed package accumulates modules across runs instead
of being rebuilt clean. One orphan is cosmetic; the mechanism is not, and it is
the same family as the `_bundle_asset` name-collision handling in
`exporting/localize.py`.

**STATE OF THE TREE.** Six changes landed 2026-08-09. Only the kit fan-out
has been through a full run and a sweep. The gate, the scheduler fix and
`cache forget` are each covered by tests and the first two were exercised by
the 08-09 runs; `cache forget` has not been run on hardware at all. Do not
stack more onto this before the next full run — that is why item 8 below waits.

**STILL UNVERIFIED:** the walk itself. The bot found a real defect on
this run — `Ladder_ladder_0: climb, top_exit — no opening at all at rel_y 3.90,
the slab is solid over the ladder` — a ladder rising one full storey into a
solid slab, same family as item 3. Nobody has walked the corrected site by eye.
(The exterior shot bot reports `void 99.48%`, exactly the figure item 5 below
predicts for a CORRECT site, so that calibration holds.)

**Pre-existing and unrelated, found while running the suites:**
`tests/test_presentation_fingerprint.py` fails to import —
`cannot import name '_COMPOSER_SOURCES' from 'adapters.presentation'` — on the
pre-patch tree as well. `tests/service/test_facade.py` has failures needing
real tools, identical before and after.

---

### Tools at the factory root

| script | what it answers |
|---|---|
| `marker_scope_census.py` | which unreachable markers are real, by footprint geometry |
| `library_themed_fit.py` | how many families can carry a theme (imports the real rule) |
| `module_extents.py` | do the modules in a band share a top and bottom line; `--kit`/`--sweep`: does a built kit have the dims its slots asked for (self-tests all three readers) |
| `library_census.py`, `library_clean.py` | what the library already knows about itself |
| `unpatch_lf_themed_selection.py` | reverses a patch by importing it, rather than restating it |

---

## The finding that reframed the week

**An extraction point stands on the street, and Lot lays the street.** A
per-building navmesh cannot contain it, so asking a building-scope bake whether
it is reachable puts the question at a scope where its subject does not exist.
Measured over all 135 shells: 99 have an extraction marker outside their own
footprint and unreachable. None of those 99 answers is about the building.

`docs/NAV_GATE_FINDINGS.md` said this on 2026-08-05 and it was not read before a
Level Factory selection rule was keyed on the uncorrected number. That rule kept
**6 of 134** shells, and not one of the six was kept for being a better building
— two had no extraction marker or one placed indoors, four had theirs close
enough to the wall that the snap landed on connected navmesh.

**The discriminator is footprint geometry, not snap distance.** The two
classifiers disagree ten times in this library, six of them dropping a real
interior defect as benign (`cr_deli objective_SAFE`, snap 2.6 m, inside the
footprint). `gameplay.json` carries `footprint` and every marker's x/y, so it is
arithmetic, not inference.

Corrected: **103 shells navigable, 15 with a genuinely unreachable interior
marker, 17 unjudged.** Themed-fit went from 6 families to **37**. `final_stand`
— the shell walked with a stair into a wall — is still refused on both
conditions; `pharmacy_a02` is still admitted.

The 15 are the signal that was buried under the 99: `office`, `deli_a02`,
`gas_station_a01`, `strip_retail_a01`, `primos_pizza` and others each have an
objective or loot marker on a disconnected island, and every one of them
currently reports `passed`.

---

## Open, in priority order

**1. Every wall in the library is 3.300 m tall whatever height was asked for.
Zoo, or the naming law. (Superseded 2026-08-09 — see the correction below.)**

~~`wallEnd` is the wrong height~~ — `wallEnd` was the only module in the library
that was RIGHT. The 1.000 m figure was an artefact of `module_extents.py`, which
read `nums[10]` (origin.y) out of each `Transform3D` and discarded the other
nine numbers. `wallEnd` is the one species Deli Counter SCALES — Zoo says so in
`genome/species/wallEnd.json`, `core/kit.py` line 13 and its
`exact = typ != "wallEnd"`, and the comment in `recipes/_arch.py`, and the
export naming agrees, because every other species bakes its width into its
filename (`wall_rockay_01_w200.glb`) and `wallEnd_rockay_01.glb` carries no
width token. Measured over all nine buildings: `wallEnd` is the only species
with a non-unit basis anywhere, so the one species the tool mis-measured was
the only species it COULD mis-measure. `module_extents.py` now applies the full
basis and self-tests the `.tscn` reader; sidecar `module_extents.py.pre_basis`.

**With the basis applied, the real defect is the opposite one.** Deli Counter's
`<id>.slots.json` declares a wall height per building, and every module that
bakes its height at build time ignores it:

```
building                slot h   wallEnd   wall built    error   per edge
depot_a01                  5.2       5.2        3.300   -1.900   0.950 GAP
rail_station_a02           4.7       4.7        3.300   -1.400   0.700 GAP
supermarket_a01            4.2       4.2        3.300   -0.900   0.450 GAP
bank_branch_a04            3.9       3.9        3.300   -0.600   0.300 GAP
construction_site_a03      3.3       3.3        3.300   +0.000   flush
funeral_home_a03           3.1       3.1        3.300   +0.200   0.100 OVERLAP
pharmacy_a02               3.1       3.1        3.300   +0.200   0.100 OVERLAP
```

`wall`, `breach`, `doorway` and `window` are **3.300 m in every building**. The
two that look clean are the two whose storey happens to be 3.3. `wallEnd`
matches the requested height in all seven, because its height lives in the
`.tscn` basis written at assembly and everything else bakes its height into the
`.glb` at build — so the one module carrying its height in the scene is the one
that could not lose it.

**0.950 m under every wall in `depot_a01` is the gap B$ walked.** The vertical
seams are the same defect at the other five.

**The premise is written down and it is false.** `core/kit.py`, `module_stem`:
*"a wall varies on one axis — its width — while its thickness and the storey
height are fixed, so `_w<cm>` is a complete key."* The storey height runs
3.1–5.2 across this library, so `wall_rockay_01_w200` is the stem for a 3.1 m
wall, a 3.9 m wall and a 5.2 m wall alike. `plan_kit`'s bucket key DOES include
full dims and correctly makes them separate modules — and then hands them all
the same filename. That is the plate collision the `_d<cm>` suffix already
fixed, one axis over, narrated in the same docstring two paragraphs above.

**Answered 2026-08-09. ONE kit is built per MISSION and handed to every
building in the lot.** `blender --background --python tools/zoo_cli.py --
--build-kit deli_counter/build/depot_a01.slots.json --out <tmp> --theme rockay`,
measured with `module_extents.py --kit <tmp> --slots ...`:

```
depot_a01  9 species built, 23 planned
  breach   x4  ok  h=[5.2]      floor    x3  ok  h=[0.02]
  ceiling  x3  ok  h=[0.02]     prop     x2  ok  h=[1.4, 1.8]
  doorway  x4  ok  h=[5.2]      roof     x1  ok  h=[0.3]
  wall     x3  ok  h=[5.2]      window   x1  ok  h=[5.2]
  wallEnd  UNIT x2 ok (1x1x1, scaled at placement)
every species matches the slots it was built from
```

**Zoo is not the defect.** Every one of the 23 modules comes out at exactly the
dims asked for, on all three axes, walls at 5.200. `build_slab` honours
`dims["height"]`. So does the stem collision above — real, but not the cause.

**NOT STALENESS. That was proposed here and it is retracted.** `depot_a01`'s
art is timestamped 08-05 22:29 and its `slots.json` 08-05 21:17 — the art is an
hour NEWER than the slots it disagrees with. The "six modules where twenty-three
are planned" that the staleness story rested on is not a staleness signal at
all: `--sweep` shows EVERY building missing the same roles, including the one
that otherwise passes, because a preview package holds only the art its `.tscn`
actually references. A number was read and a cause was named for it.

**`--sweep` over the lot, and the shape is one constant:**

```
building                glb  planned  absent  wrong  verdict      slot wants
depot_a01                 6       23       6      3  WRONG DIMS      5.2
rail_station_a02          4       23       6      2  WRONG DIMS      4.7
supermarket_a01           7       23       6      4  WRONG DIMS      4.2
bank_branch_a04           7       23       6      4  WRONG DIMS      3.9
funeral_home_a03          7       23       5      5  WRONG DIMS      3.1
pharmacy_a02              8       23       4      6  WRONG DIMS      3.1
construction_site_a03     6       23       6      0  ok              3.3
```

Every module in the library is **3.300 m**. `construction_site_a03` is not
healthy; it is the building whose requirement happens to equal the constant.
`breach_rockay_01_w140_ob6fc1c.glb` is 3.300 in all eight buildings, spanning
five different required heights, and is byte-identical in all of them.

**The cause, in `planner.py`, stated as an assumption:**

```python
zoo_kit_jid = job_id(brief.mission_id, _STAGE_ZOO_KIT)      # NO archetype
```

`zoo_dressing_build` and `zoo_fixtures_build` take `archetype=aid`. The kit does
not — one kit job per MISSION, built from ONE building's `slots.json`, and
`apps/cli/commands/__init__.py` hands its output dir to the compose of every
building as `modules_dir`. The belief is written down beside the dressing job:

> *"the SHARED kit: the kit is a module library resolved per slot"*

A kit is not building-independent. An `exact`-fit module is built to one slot's
dims. The ONE species that genuinely is shared — `wallEnd`, the 1x1x1 unit box —
is the only species that survives being shared, and that is why it measured
correct in all seven buildings.

**The stem collision is the other half of the same bug.** Because `module_stem`
omits height, one building's modules RESOLVE against another's slots instead of
failing to. Fix the fan-out alone and each building gets correct modules, the
collision going latent. Fix the stem alone and the wrong-sized modules stop
resolving — greybox stays, a visible hole instead of silently wrong geometry.
Both are wanted: the fan-out for correctness, the stem so this cannot be silent
again.

`_dep`'s own docstring already records this defect one layer down — "hands one
building's props to all of them", measured 2026-08-06, one dressing box in five
shells. The kit was left out of that fix because of the belief quoted above.

Not evidence, and discarded at the time: the `.glb` byte sizes are identical
across buildings for a given stem. Textures dominate the bytes and a box has
the same vertex count at any size, so the number distinguished nothing on its
own — though the measured geometry later agreed with it.

**2. `int_col_*_seg*` architecture. Deli Counter. — READ 2026-08-09, and the
premise looks wrong. Do not spend a walk on this yet.**

The claim was that the odd wall proportions, free-standing panels and floating
lintels ARE collision segments, textured so they read as finished. Measured:

* `_col_box` appends `self.col_suffix[mode]`, which is **`-colonly`** or
  **`-convcolonly`** (`deli_counter.py` line 69-71, 304-310). Both are Godot's
  collision-ONLY suffixes: the mesh collides and is **not drawn**.
* `site_base.glb.import` has `nodes/use_name_suffixes=true` and does not set
  `generate/physics`, so the suffix convention is live and applies.
* So the exported node is `int_col_0_0_seg2-colonly` and is invisible. A
  collision segment cannot be a thing you see.

**What the overlay was reporting is the COLLIDER, by design** — it prints "the
collider name and distance", so `int_col_*_seg*` appears under the crosshair
for *any* interior wall you face, including a perfectly ordinary one. Reading
that as "the panel IS a collision segment" is the same trap as the four verdict
keys in the traps section below: an instrument reporting a narrower thing than
the reader assumed.

**The visible geometry is `int_*_seg*` — Deli Counter's greybox partition
runs**, built at the building's real storey height, standing beside Zoo modules
built at 3.300 m. Mismatched heights side by side is what "odd proportions" and
"floating lintels" look like. **Unconfirmed, but if it holds, item 2 is a
symptom of item 1** and the fix above removes it. Walk this only AFTER the
item 1 fix is verified on hardware; a walk before then measures the old defect.

`WALL_SEGMENTATION.md` has now been read. Two things from it worth keeping:
segment seams are the named hotspot for gaps, double-walls and collision holes
at door voids ("offline checks can't catch it; budget one walk when this
lands"), and `_record_surface(col_name, ...)` records the COLLISION run as a
surface, so Pixelcoat and Patina do texture invisible geometry. Harmless to
look at; worth knowing if anything downstream reads `surface_roles` to decide
what a wall is.

**3. Stair into a slab, `construction_site_a03` (b2).** The original complaint
from 2026-08-07, and the open question "desk or ceiling" is now answered:
**ceiling**. The headroom check built on 2026-08-07 reads *specs*, not built
shells, and is non-blocking (`HEADROOM_ENFORCED` False, 2 violations of 157), so
it was never going to stop this. The nav gate's agent is 1.8 m; a flight with
1.9 m of clearance proves a polygon path and still feels like this. Whether
that is what happened is a measurement, not an inference. Walk to b2 and the
overlay will name the collider and its height.

**4. The site-scope extraction check. Unpaid.** Every one of those 99 markers now
reads `deferred to site scope`, and **nothing at site scope judges them**. That
is a record with an owner and no work behind it — one step better than a silent
hole, one step short of a check. Logged as Q4 in `NAV_GATE_FINDINGS.md`.

**5. Interior void stations.** `shot_bot.gd` computes a void fraction and never
gates on it: `st["ok"] = jitter <= JITTER_FAIL_PCT`. From an interior station
void *is* a gap detector, by the file's own docstring. Do **not** gate the
exterior station — its camera sits at `0.8 × the longest horizontal dimension`,
and this site is a 309 m strip, so a correct site measures 99.48% void. Calibrate
the way `JITTER_FAIL_PCT` was: a measured known-good and a measured known-bad
with the signal clear of the noise.

**6. Lot should compose a place, not a line.** Buildings run from x −118 to
+127 in a straight row. Streets, sidewalks, setbacks, rotation. B$'s item,
explicitly not a now-priority.

**7. THE PIPELINE READS ITS OWN OUTPUT AS SOURCE. Not housekeeping — this
is a correctness bug in every count taken this week. START THE NEXT SESSION
HERE.**

`deli_counter/build/` is the source archetype library AND the directory Level
Factory writes composed buildings into. Eleven entries in it are not source
archetypes: `lf_art_probe_001_5017`, five `lf_category5_baie_dore_001_*`, three
`lf_lot_demo_001_*` (Level Factory's own composed outputs), and
`gs_facade_rowhome` / `gs_facade_storefront` (facades, not buildings).

That is a feedback loop, not clutter. `lf_lot_demo_001_5017` appeared in the
2026-08-09 `--sweep` **as a building**. Every denominator this week — "6 of
134", "97 of 134 can carry a theme", "103 navigable, 15 holed, 17 unjudged" —
was measured against a library containing the pipeline's own output. The
numbers were consistent with each other and wrong together, which is the
hardest kind to notice.

**Fix it at the source, not by deleting files.** Deleting them works until the
next run writes them back. `building_library.index` is the one place every
count enters from — `library_census.py`, `library_themed_fit.py`,
`marker_scope_census.py` and `lot_for` all pass through it. Make it refuse
entries that are not source archetypes, with a test naming the eleven and
saying WHY each is excluded (an `lf_`-prefixed composed output, a facade with
no interior). One place, cannot drift, and every count above corrects itself.

Recount everything afterwards. The corrected figures in this document were
taken against the polluted library and none of them have been restated.

**Also here, unrelated and smaller:** `_find_level_scene` prefers
`site_lux.tscn`, but `lux_apply` writes `lux.applied.tscn` into its own job dir
and nothing copies it into a content dir — that preference has never fired, so
the walk preview shows compose lighting rather than the Lux runtime look.

**8. Root hygiene. Second, and mechanical.** Real, but no correctness
consequence, so it goes after 7 and after the tree is verified.

* **Sidecars whose original is gone.** `check_all.py` does not exist; three
  `check_all.py.pre_*` do. Same for `check_freshness.py`, `check_stair_pitch.py`,
  `check_steps.py`, `library_walk.py`, `rebuild_buildings.py` — all
  `.pre_root` sidecars for deleted files. Reverting from one restores a file
  the repo no longer has.
* **`.pre_*` duplicates git.** There is a `.git` here. The convention earns its
  keep inside a session and becomes archaeology after it; 2026-08-09 alone
  added a dozen. Worth a rule: sidecars are session-scoped and cleaned when the
  change is committed.
* **Nine spent `patch_lf_*.py` at the root**, beside a `migrations/` directory
  that exists for exactly this.
* **Scratch at the root:** `_bridge`, `_bridge_fresh`, `_runs`,
  `_scratch_archive`, `_scratch_walkable`, `_scratch2`, five `shots_*`
  directories, `test_themed_selection.py.pending`. `.gitignore` them.

The connection to item 7 is not decorative: **when everything looks like it
might be current, nothing reads as stale.** `prop_rockay_01_w160.glb` survived
five days in plain sight because a directory of mixed-age files is the normal
condition here.

---

## Traps that cost time today

**Changing what a shared rule selects obliges you to find every caller.**
`grep lot_for` names all three in one command. Two were edited; the third
(`planner.py`) fanned out art jobs for an archetype the narrower pool did not
contain, and `_art_entry` raised *"the planner and the spec builder disagree
about which buildings this mission places"* — its own guard, firing exactly as
written. The suite could not see it, because `test_fanout.py`'s library is
uniformly themeable and the two pools agree by accident. It only shows on a
**mixed** library.

**A fixture is a claim about the world.** `test_fanout.py::_library()` wrote every
manifest as the literal string `{}` — no coverage, no navgate — which is a
faithful stand-in for a library of holed, never-judged buildings. Harmless while
nothing read them; the moment selection did, all eight shells were correctly
judged unfit and thirteen tests died on an exception telling the exact truth.

**`res://` is optional in the per-building packages.** They are written portable
(`lot.py --portable`) so a stranger can drop one into their own project; their
paths are scene-relative. A pattern demanding the prefix matches the composed
site and silently matches nothing in the building scenes. `module_extents.py`
shipped once with that bug and reported "0 distinct modules" for all five
buildings while looking like it ran. It now refuses instead.

**A tool that reads part of a transform reports confidently on the part it
read.** (2026-08-09.) `module_extents.py` took `nums[10]` for the origin and
dropped the basis, so it measured every scaled instance at its unscaled size.
It produced a clean table, a plausible number, and the week's top priority
aimed at the one module in the library that was correct. Two parsers lived in
that file; the one that had been put wrong on purpose and tested was fine, and
the one read by index and never tested was the one that was wrong. Its
`--selftest` now covers both, and the new case fails on the old file. **Before
trusting an instrument's number, read the line that produces it and check it
consumes the whole input** — this is the `nav_gate`/`shot_bot` lesson below
moved from verdicts to measurements.

**A `.glb` is Y-UP even though Zoo authors Z-up.** (2026-08-09.) Blender's
glTF exporter converts on the way out, so a standing slab's height is its **y**
extent on disk and its thickness is z. `module_extents.py --kit` shipped once
reading z and reported `wall WANTED h=[5.2] BUILT h=[0.3]` for a kit that was
perfectly correct — a wall's height compared against its own thickness — in a
function whose docstring warned about exactly that. The synthetic fixture was
authored Z-up too, so it agreed with the wrong reader and passed. **Assert the
CLEAN case, not just the failing one:** "it flagged the bad kit" cannot tell you
it would not also flag a good one, and only the clean report has any value.

**Verdict keys measure narrower things than their names suggest.** `nav_gate`'s
`ok` counts stairs only. `validation.passed` ignores its own warnings.
`shot_bot`'s `ok` is jitter only. `walk_bot` returns `ok: true` with the note
"traversal vacuous". Four instruments, all reporting a number beside a verdict
that does not include it. Assume the next one does too until you have read the
line that computes it.

**Nearly repeated it.** After seeing `void 86.7%` printed beside `[OK]`, the
proposed fix was to gate on void. Measuring first showed the exterior camera
frames a 309 m strip from 350 m away, so a *correct* site measures 99.48% — the
threshold would have failed good sites on day one. Picking a threshold on a
number without measuring what correct looks like is the same mistake as the
selection rule, one layer along.
