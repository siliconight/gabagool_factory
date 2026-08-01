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

`gdcheck.py` at the factory root runs `gdparse` plus the traps a grammar cannot
see. Run it on every `.gd` before pushing to a machine that will load it:

    pip install gdtoolkit
    python gdcheck.py navmesh_solid_probe.gd

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
