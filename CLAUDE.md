# Repository conventions

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

## Where fixes land

Fixes land in the tool repos — `lot`, `level_factory`, `deli_counter`, and their
siblings — never in a mission workspace. `rockay-ws` is evidence: read it, do not
edit it. `deli_counter/agent_contract.json` is the single source of truth for
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
