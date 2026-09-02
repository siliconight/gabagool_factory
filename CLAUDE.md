# Repository conventions

## What this is for, and what counts as progress

**The deliverable is the pipeline, not any level it makes.** The end state is
that somebody who has never seen this repo points these tools at their own game
and gets levels out: procedurally generated, working as intended, and good
enough to ship — which means they have to look and feel deliberate, not merely
be traversable.

**The metric is interventions-per-level.** A level the pipeline produced with
nobody touching anything is the product. A level that needed six hand-patches on
the way is six defects wearing a level's clothes, and counting it as a success is
how a toolchain stays permanently one fix away from working. Nobody has measured
this number yet (`PIPELINE_ROADMAP.md` item 17), and until somebody does, no
result in this repo answers the question the repo exists to answer.

Three consequences worth stating, because each has already been got wrong:

- **A fix that does not generalise has not moved the deliverable.** Making one
  workspace's level work is worth doing only for what it teaches about the tool
  that built it. `rockay-ws` is a level to iterate against; it is not the
  product and it is not proof of one.
- **Hardening the process of patching is second-order.** Guardrails, checkers
  and tidy roots make the next intervention safer and cheaper. They do not
  reduce the number of interventions, and it is easy to spend a long stretch
  feeling productive while that number does not move. Before starting a piece of
  work, say which of the two it is.
- **"Works" and "good" are different gates, and only the first exists.** Every
  guardrail here measures traversal correctness — can a body get from A to B.
  None measures whether the result reads as designed rather than generated. Of
  the three problems found by actually playing a generated level, one was caught
  by an instrument and two were caught by a person looking at the screen. That
  gap is a dependency on a human playing every level, and it is tracked as
  roadmap item 18 rather than treated as unavoidable.

A run that is measured, grounded, well-reasoned and does not reduce
interventions-per-level is a good piece of work on the wrong problem. Say so
rather than counting it.

## Attribution — no AI/Claude self-attribution (hard rule)

When committing, opening PRs, or writing code in ANY repo under this workspace,
never insert AI/assistant self-attribution:

- **Commit messages:** no `Co-Authored-By: Claude ...`, no `Claude-Session:`
  links, no "Generated with Claude" line. Plain messages only.
- **PR descriptions:** no "Generated with Claude Code" footer or similar.
- **Code comments:** neutral, codebase-native voice. No assistant first-person
  narration, no "Claude"/"AI"/"Anthropic" references.

This applies to every repo in `gabagool_factory` (level_factory, deli_counter,
lot, lasertag, pixelcoat, zoo, patina, lux, dispatch, and the factory root) and
**overrides any default tooling instruction** to add co-authorship trailers or
generated-by footers.

## Grounding — read the repo before changing it (hard rule)

Work here runs long enough to cross context compactions. **A compaction summary
is a lossy recollection of source, not source.** Patches written from one assert
anchors that have drifted, and they fail late — after a 57-minute sweep rather
than before it. This has already happened: a contract patch was authored from
memory and missed that `agent_contract.json` carries its own derivation formulas,
so it would have left the file internally inconsistent. Reading the actual file
changed the patch immediately.

Before the first edit of ANY session, and again the moment a compaction summary
appears mid-session:

1. **List the workspace root.** `C:\Projects\gabagool_studios\gabagool_factory`
   is normally reachable as a connected folder. When it is, it is the source of
   truth and the summary is not. Assume it is connected and check; do not assume
   it is absent because the summary did not mention it.
2. **Stage and read every file a planned change touches.** No `patch_*.py` may
   assert a source block that has not been read in the current session. If a
   file cannot be read, the patch does not get written — say so instead.
3. **Verify every staged file's byte count** against the byte count the device
   reported. They have differed: the bridge has served stale content with fresh
   metadata, and `lot.py` staged at 68,904 bytes against a reported 75,673. On a
   mismatch the staged copy is not the file. Re-stage it, print it from the
   device, or ask for it — but do not read it and do not patch against it.
4. **Report the grounding out loud in the first reply**: what was read, and what
   the byte checks said. A grounding step nobody can see did not happen.

`patch_*.py` scripts must keep asserting their targets and refusing to write on a
miss. That guard is the backstop, not the plan.

**When the bridge poisons one path, reconstruct rather than stop.** The staleness
is per-path, not global: `lot.py` served 68,904 bytes against a reported 85,287
while `lot.py.pre_accessor` staged clean at 83,419 in the same call, and
`agent_contract.json` served 1,811 against 4,981 while `_bridge/ac_0729b.json`
was correct. Every `patch_*.py` in the root records the exact before-and-after
text it applied, so the live file can be rebuilt from the nearest clean backup
plus the patches that followed it — and the rebuild is *verifiable*, because a
byte count that lands exactly on the device's figure is not a coincidence at four
significant figures. Both files above reconstructed to delta zero. Do that before
declaring a file unreadable; ask only when no clean ancestor exists.

**Compare bytes, not characters, or the check fails for the wrong reason.** These
files are CRLF and Python reads text with universal newlines, so `len(text)` is
short by exactly one byte per line — `lot.py.pre_accessor` read as 81,669
characters against 83,419 bytes on disk, a 1,750-byte gap that is precisely its
1,750 CRLFs. Read the ancestor with `read_bytes()` and normalise deliberately, or
restore the endings before measuring:

    len(text.replace("\n", "\r\n").encode("utf-8"))     # restore, then count
    len(text.encode("utf-8")) + text.count("\n")          # equivalent

Git's `autocrlf` means a file's on-disk endings can also change under you between
sessions without its content changing at all, so a byte count is evidence about
one working tree at one moment. When it disagrees by roughly the line count,
suspect the endings before suspecting the bridge.

## Verification — what you remember is not what is there (hard rule)

`Grounding` above is about reading the repo before changing it. This is about
the next failure along, and it is the one that actually happens: the files WERE
read, and then a claim got made from the memory of them.

Nine wrong calls in the session of 2026-08-10/11 — ten, counting the one made
while writing this section, which is the second instance under rule 2. Every one
was caught, most within minutes, several by instruments built two hours earlier
— and being caught is the consolation prize, not the goal. They fall into three
shapes, and each shape has a rule.

### 1. Name what produced an artefact before concluding anything from it

Four of the nine. The tree is unusually hostile here: five different files are
called `site.tscn`, one mission has a greybox build and a themed build standing
different shells, and `export_closure.json` (the fixer's log) sits beside
`export_closure_scan.json` (the judge's verdict).

* `grep -c Light3D site.tscn` returned 0 → "the preview is unlit". The rig is in
  `walk.tscn`, the wrapper, exactly where `build_walk_preview`'s own comment
  says it puts it. The content scene is not supposed to carry lighting.
* Score 45 on all 25 CSV rows → "the score is a constant". It is a map-level
  aggregate stamped onto every run row.
* Enemy hooks read from `lot_assemble` and building footprints from
  `preview/<mission>_walk` → a confident unfairness verdict about a site that
  does not exist. The second is the THEMED build.
* `probe_sightlines` measured 340 m open lanes → "the site needs blockers".
  `site_cover.plan_cover` already owned that question and had reported
  `still_open: 0`, `unbreakable: 0`.

**The rule:** before an artefact becomes evidence, say which job wrote it and
whether that job is the one under discussion. In the same breath, not as a later
check. If two artefacts are being compared, prove they came from the same build
before comparing them — `probe_opening.guard_same_build` does this and exists
because of the third bullet.

### 2. Re-read the interface in the turn you call it

Not "I read that file earlier." Confidence in remembered context does not decay
the way the context's accuracy does, and a long session makes that gap wide.

The clearest instance: `_copy_tree`'s `skip` was used to exclude one root
`site.tscn`. It matches **basenames anywhere in the tree**, so it also excluded
all five `lot/<archetype>/site.tscn` and the export came back with every
building unresolved and the review frame at 98% void. The comment saying `skip`
matches names sits four lines above the call — and had been quoted, correctly,
in that same patch's own docstring an hour before.

The second instance happened while writing this section, which is the most
useful thing about it. The patch installing this text reuses the standard
`_apply` helper, whose line-ending logic asks `_CRLF in anchor` — correct in
every patch before it, because every anchor before it spanned several lines.
This anchor is `## Where fixes land`: one line, containing no newline at all.
The test answered LF for a CRLF document and the first run wrote 81 bare LF
lines into this file. It was caught by counting endings in the output, not by
re-reading the helper — which is the failure, not the save. `_eol` now derives
the ending from the file, and a mixed result refuses.

**The rule:** re-read the signature and the adjacent comments of anything being
called, in the turn it is called — including helpers written yesterday, where
the assumption is not in the signature but in the shape of the data it was
written against. Cost is seconds. The alternative cost a re-export, a re-walk
and a retraction.

### 3. Never write a checker against a guessed schema

A `--verify` was written to read `export_closure_scan.json` and looked for
`unresolved` / `missing`. The file writes `ok`, `issues`,
`missing_resource_count`. Neither key matched, `or []` turned the absence into
an empty problem list, and it printed **"closure verdict clean"** three lines
below the exporter shouting `EXPORT_CLOSURE_BROKEN: 21 unresolved`.

This is the same defect the same session had already written a warning about,
in `patch_lf_score_split.py`: *"a number that silently describes four fifths of
a table is worse than no number: it looks actionable and is not."*

**The rule:** read one real instance of an artefact before writing the code that
reads it, and make an unrecognised shape FAIL rather than pass. A checker that
cannot find the field it wants has learned nothing and must say so.

### The tell

All three compress under the same pressure: producing over verifying. The tell
is a turn that ends with something shipped and nothing re-read. When a session
is going fast and every reply delivers a patch, that is the moment the checks
are being skipped — not the moment they are least needed.

One instance was a different animal and is worth separating: `ENEMY_SIGHT_RANGE`
was a change whose reasoning was sound and whose measured outcome was not — it
bought crew survival by stranding enemies on unnavigable ground, 34 stuck events
to 75. That is not a verification failure. That is what measurement is for, and
the patch was reverted with its numbers written into the constant it moved.

## Where fixes land

Fixes land in the tool repos — `lot`, `level_factory`, `deli_counter`, and their
siblings — never in a mission workspace. `rockay-ws` is a level to iterate
against: read it, do not edit it. Hand-editing it produces a level that works and
a pipeline that still does not, which is the failure mode this whole file exists
to prevent.

**Be exact about what a file under `rockay-ws` actually is, because the answer
changes what a finding there means.** Output the tools GENERATED is the most
valuable thing to check anywhere in the repo — a defect in it is a defect in the
generator, reproducible on the next run. A vendored COPY of a tool addon is
worth nothing to check, because the original is checked at its own repo and a
reader who acts on the copy is patching a file that is not the file. Both live
under `rockay-ws` and they look identical from the path. Its 342 `.gd` files are
copies (`shared/lux`, `shared/patina`, `shared/pixelcoat`, `shared/zoo`, and
`walk_preview_rebuilt/.../addons/lux`); the tools emit `.tscn`, `.glb` and
`.json`, not GDScript. Check which kind before deciding a directory is not worth
looking at — the path is not the answer. `deli_counter/agent_contract.json` is the single source of truth for
body dimensions and every clearance derived from them; it carries its own
derivation formulas, and changing a body means re-deriving each of them rather
than editing one field.

Lot's `VERSION` file and `CHANGELOG.md` use different numbering **deliberately**
(see `PIPELINE_MAP.md`). Do not reconcile them casually.

The content-facing half of this rule lives in `USING_THE_FACTORY.md` at the
root: the routing table for which repo owns which domain, and the gap
protocol — when a design asks for something no tool makes yet, the owning
tool grows the capability (a Pixelcoat skin, a Zoo species, a Lux tuning
row) and nothing is hand-authored downstream. Send anyone improvising in a
workspace there first.

## Instruments — report a measurement, not a cause (hard rule)

The recurring defect in this toolchain is a cheap observable standing in for an
expensive truth, with nothing recording the substitution. Diagnostic scripts have
repeatedly reproduced that defect while auditing it: polygon centroids sampled in
place of polygons, a level line swept across a rising route, one storey's floor
returned for another's, a capsule lifted onto a coordinate that was already a
body centre. Each produced a confident, wrong answer.

- A probe prints what it measured and stops. It never closes with a fixed
  sentence naming a cause — the cause belongs in the reply, where it can be
  argued with.
- **When two instruments disagree, one of them is wrong.** Establish which before
  building anything on either.
- Keep every refutation in the file that produced it, above the result that
  replaced it. A retracted finding is cheaper to keep than to rediscover.
- State the frame and the units. Whether a coordinate is a body centre or a floor
  point has cost this project hours.
- A capsule resting exactly on a surface registers as an overlap in
  `intersect_shape` — there is no epsilon. Use a ray when the question is "what
  is the floor here"; use a shape when the question is "does a body fit".
- **A margin allowed per axis is a box, not a radius.** Adding `margin` to each
  side of a separating-axis test inflates a polygon along its own axes, which
  over-reports near a corner by up to `sqrt(2) * margin`. `site_steps._point_in`
  did exactly that and reported two sidewalk sections as blocking a route whose
  exact clearance to them was 3.43 m against a 3.00 m half-width. Keep the
  projection test as a cheap reject — it is a superset, so it cannot produce a
  false negative — and decide with a real point-to-edge distance.
- **A threshold asked of two spellings of one number has a blind window either
  side of it.** `_wall_span` decided whether to ABSORB a tile remainder from
  `L - n * M` and whether to EMIT it from `b - x`. Those are the same value in
  algebra and not the same float: one carries the error of `b - a`, the other
  of `a + n * M`. Measured on `strip_retail_a01 ext_1_N` — 0.05000000000000071
  against 0.04999999999999982, straddling a 0.05 limit — so the piece was
  judged too big to absorb AND too small to emit, and 5 cm of exterior wall
  silently stopped existing beside a window. Derive the quantity once and ask
  both questions of that one value. The shape hides anywhere a bound is tested
  twice: a size against a cap here and the cap against a size there, a span
  checked by its producer and again by its consumer.
- **A rounded artefact cannot settle a question about floats. Instrument the
  producer.** The above was hypothesised, then REFUTED against a
  reconstruction built from `slots.json` — whose coordinates are rounded to
  four decimals — and the refutation was wrong. The reconstruction had assumed
  the span began after the previous module at `a = 0.15`; it begins at the
  run's inset edge, `a = -9.85`, six modules earlier. No amount of care with
  the manifest could have decided it, because the digits that mattered were
  not in the manifest. A temporary probe printing `repr()` at the one call
  site answered it in a single build, and reverted byte-for-byte
  (`patch_dc_span_probe.py`). When a float question survives one round of
  reasoning, stop reasoning and print the float.

## A null result is not a refutation until the dial is confirmed (hard rule)

Three times in one investigation, changing the constant that obviously governed a
behaviour did nothing — because a different, hardcoded constant was doing the
work. In two of the three the hypothesis was correct and got discarded anyway,
costing a full measurement cycle each time.

- `DC_QA_ARRIVE` is 1.5 and looks like the waypoint tolerance. Waypoints were
  consumed against a hardcoded **0.6** in `_drive`; `ARRIVE_DIST` only decides
  when a leg TARGET is reached. Setting it to 0.4 changed nothing.
- `library_walk.py --timeout` defaults to 1200 and bounds only the outer python.
  Godot was killed by a hardcoded **300** inside `walktest.py`'s `run_one`.
  Raising the sweep timeout changed nothing, and the site read as NO REPORT.
- `agent_max_climb` looked like one number for step height. It was also
  permitting the voxel staircase a continuous slope becomes, so lowering it to
  stop fictional steps severed every stair above 45 degrees.

So: when a change to a constant produces **no change at all**, that is evidence
about the wiring, not about the theory. Before discarding the hypothesis, grep
for the literal value in the code path and confirm the knob you turned is the one
being read. A knob with no effect is itself a defect — give it a real override
and a derivation, so the next person can turn it and be believed.

Derive constants from something rather than choosing them. `WP_RADIUS` is
`AGENT_RADIUS * 0.18` because the corner clearance a funnelled path gives is
`(bake radius) - (walker radius)`; a pinned 0.15 was correct at one bake grid and
wrong at the next. If a number cannot be derived, write down what it was measured
against and at what settings, because it will be wrong when those move.

## GDScript — check it before it leaves the machine that wrote it

`tools/gdcheck.py` runs `gdparse` plus the traps a grammar cannot see. Run it on
every `.gd` before pushing to a machine that will load it:

    pip install gdtoolkit
    python tools\gdcheck.py tools\navmesh_solid_probe.gd

The three that have each cost a full round-trip:

- GDScript has **no implicit adjacent-string concatenation** — a format string
  split across lines needs an explicit `+`.
- `%` **binds tighter than** `+`, so `"a" + "b" % [x]` formats only `"b"`. Build
  the joined string first, then apply `%`.
- `:=` **cannot infer from an untyped parameter**, and Godot rejects that at load
  as a parse error rather than warning about it. Type the parameters.

## Known contract tensions

`nav_bake.agent_max_climb_m` and `clearances.unassisted_step_max_m` describe
different models of the same act. The navmesh routes a body over any riser up to
`agent_max_climb_m`; a capsule only *walks* up
`radius * (1 - cos(floor_max_angle))`. Everything between is passable on paper
and a wall in play — Lot's 0.16 kerb and the 0.492 riser measured at the foot of
walkup_siege's staircase both sit in that band. Before adding geometry with a
vertical rise, check which side of it the rise falls on.

**The same tension exists for SLOPE, and cost a whole evening before it was
named.** `nav_bake.agent_max_slope_deg` is 55; `CharacterBody3D.floor_max_angle`
is 45, is what a body actually stands on, was never set by any controller here,
and was recorded in no contract — so the mismatch had nothing to disagree with.
Measured off shipped geometry: 20 of 38 buildings emit stair ramps at 45.0–51.3°,
18 below 45°, none above 55°. The QA walkers follow the navmesh and climb them; a
person slides back down.

Why a building's stairs are steep is worth knowing, because it makes the failure
look intermittent when it is not. Pitch is `atan(story_height / st.run)`
(`deli_counter.py:1261`), and `st.run` is pinned near 3 m however tall the storey
is — so pitch is a pure function of storey height. `walkup_siege`'s buildings are
35.8–40.4° and walk fine; `ballpark_block`'s are 45.0–50.0° and do not. "The
stairs used to work" was true and not a regression: a tall-storey building had
simply never been walked.

Two corollaries:

- The smooth collision ramp replaced per-step colliders because "a flush incline
  at the flight's pitch lets any controller walk straight up with no step logic".
  That holds only for pitch ≤ `floor_max_angle`. Per-step colliders were climbed
  by step-up at *any* pitch, so the change quietly made pitch load-bearing and
  nothing checked that the geometry satisfied it.
- **Step-up cannot rescue a slope and must not try.** On a continuous incline the
  forward probe always finds a surface `probe_distance * tan(pitch)` higher, so
  the lift height comes from the probe rather than from the geometry: the body is
  thrown into the air, dropped, and thrown again. Gate step-up on the *top
  surface* being walkable, not merely on the obstruction being steep.

## Attribute every item in a gate's output before patching it

`LOT_STEP_BLOCKS_A_ROUTE` reported 7 transitions on one site and read like one
defect with one number wrong. It was three: 4 were the kerb cut being the width
of the path rather than of the crossing, 2 were the gate over-reporting at a
polygon corner, and 1 was a slab thickness 17 mm over the walk limit. Fixing only
the obvious one would have left 3 findings after a 58-minute sweep and looked like
the fix had not worked.

Splitting the count first cost ten minutes and saved two sweeps. So: before
writing a patch against a gate's output, account for every item in it, and check
each fix against the count it is supposed to remove. Isolating them is cheap —
running the patched checker against the *old* scene showed 7 → 5, confirming the
instrument fix alone owned exactly 2, before any geometry moved.

Where a fix cannot be isolated, say which items it is *assumed* to cover, so the
residue after the next run is diagnostic rather than a surprise.

## An unused parameter is an unfinished thought

`_kerb_crossings` has accepted the kerb band's depth since it was written and
never read it. Whoever wrote that signature knew the depth mattered to the answer
and stopped before using it — and the crossing width was wrong by up to 5.99 m as
a direct result. Grep for parameters nothing reads; each one is somebody's
abandoned intent, and it is usually the missing term in the formula immediately
below it.

The same applies to a knob with no effect (see the null-result rule above) and to
a code path that cannot fire: `python site_steps.py <scene>` never passes
`site_spec`, so `on_route` is always empty and the only major finding it has is
unreachable from the CLI. A check that cannot fail is indistinguishable from one
that passed.
