# Roadmap delta — 2026-08-09

To be folded into `PIPELINE_ROADMAP.md`. Kept separate rather than edited in,
because that file is 194 KB and the surrounding numbering should be assigned by
whoever holds it. Evidence for every item is in `SESSION_0809_LADDER.md`.

---

## Closed

**Ladder into the solid roof** — the only known gameplay-blocking defect.
Cause: `deli_counter/themed_tscn.py` carried a hand copy of
`zoo_keeper.core.kit.PLATE_ROLES` that did not gain `"roof"`, so DC named a
module Zoo never built. Fixed in four repos' worth of one fact, and now
enforced by `test_mirror_agreement.py`. Verified with scene reference, `.glb`
on disk, and walk bot together.

---

## Roadmap 39 — NARROWED, NOT CLOSED

`packages/core/hashing.py` states it:

> STILL THE NARROW FIX. The general one is
> `BuildFingerprint.upstream_artifact_hashes`, which the scheduler reads from
> `job_spec["upstream_hashes"]` and which nothing populates, so every DAG edge
> carries this blindness.

Still true. `job_spec["upstream_hashes"]` is populated by nothing, and every
edge is therefore protected only by whatever `fingerprint_inputs` each adapter
remembered to hash by hand. Today's fix closed a *different* hole in the same
wall — the TOOL revision, not the upstream artifact — so 39 should not be
ticked. Each adapter hand-listing its inputs is the same shape as the mirrored
constant that caused the ladder: correct until someone adds an input and
forgets.

---

## New items

**A. Scene references must resolve.** *(propose: highest priority)*
A composed `.tscn` may not name an `ext_resource` that does not exist in the
package. Measured 2026-08-09: `site.tscn` referenced
`art/zoo/roof_rockay_01_w4000.glb`, produced by no job in the tree, and passed
compose, assemble, the sweep, a nav bake and `blockers open: 0, total findings:
54`. It loaded only because an orphan of that name from an older run was still
on disk; the orphan was a solid plate over a cut stairwell.
`themed_tscn._themed_available` already implements the check — its first branch
is `if not library_dir: return True  # trust the plan`. Make it a hard error at
the writer. Ten lines. This is the single change that would have turned a
two-day defect into a failed build.

**B. Cross-repo mirrored constants need an enforcing test.**
`deli_counter/themed_tscn.py` mirrors six names from `zoo_keeper.core.kit`
(`PLATE_ROLES`, `OPENING_ROLES`, `slot_typename`, `void_tag`, `opening_tag`,
`module_stem`), each labelled as a mirror in a comment and enforced by nothing.
`test_mirror_agreement.py` now covers them and auto-enrols new ones by reading
those comments. Remaining work: decide whether `_bridge_fresh/arch_v2.py` and
`_bridge/sw_0730a.py` are live — they hold pre-patch copies of `_SOLID` and
`PLATE_SPECIES` — and either enrol or delete them. Then audit for other
"Mirror of" comments across the toolchain.

**C. Adapters that drive another tool must probe that tool.**
`PresentationAdapter` drives Deli Counter's composer out of process and
reported `tool_version=self.adapter_version, repository_commit=None`, so no
edit to DC could change its fingerprint. Fixed. **Audit the other nine adapters
for the same shape** — any `probe()` that does not call
`_read_tool_version`/`_read_git_commit` against the repo whose code it actually
runs has the same blindness, and it is silent by construction.

**D. `art/zoo/` is never cleaned.**
The composed package accumulates modules from previous runs. Combined with A,
an orphan makes a dangling reference load successfully instead of erroring —
which is exactly how this defect hid. Fixing A makes this cosmetic; leaving A
open makes it dangerous.

**E. Instruments that cannot distinguish three states.**
`void %` reads 0.0% for a capped station, 52.66% for a correctly-open roof, and
**52.66% for no roof at all**. `walkbot.json` reports `climb: true,
top_exit: true` for both a fixed ladder and a ladder into open sky. Missing
geometry and extra geometry are opposite failure modes; one scalar cannot carry
both. Either add a presence term, or make the bot report what it *landed on* by
name. This misled the diagnosis twice in one session.

**G. ~~A stage must stage its scene's closure~~ — WITHDRAWN.**
This item was raised on a false diagnosis and is retracted in full; see
`LASERTAG_STAGES_A_STALE_SCENE.md`. `laser_tag_evaluate` had simply not run
since the lot changed (`started_at: null`, `command: []`), so its staging
directory held the previous execution's output — an absence of work, not a
defect. `stage_godot_project` copies siblings with `rmtree`-and-replace and is
correct. Laser Tag grades are not suspect.

**H. ~~A mission destination must be placed on ground the crew can reach~~ —
WITHDRAWN.** `walktest_navqa` walks the real baked navmesh with no combat in
it: four walkers, 18/18 targets each, ~875 m, `stranded_anchors 0`,
`anchors_behind_a_barrier 0`, verdict PASS. `cr_garage`'s extraction IS
reachable. The premise came from a reader that reduces every collision mesh to
its bounding box and so cannot see a doorway; `patch_lf_seal_honesty` (item L
below) is the fix, and this item was the same false seal wearing a different
hat. Second item this session raised on inference and killed by an instrument.

**H-old. A mission destination must be placed on ground the crew can REACH.**
*(superseded — kept only because the reasoning below is still the right shape
if a genuinely unreachable destination ever turns up)* Lot resolves a hook off
a prop it stands **in** (`resolve_onto_floor` → `LOT_DESTINATION_RESOLVED`) and
down onto the floor it stands **above** (`LOT_DESTINATION_RESEATED`). Neither
asks whether the crew can walk to the result. Measured 2026-08-09: candidate
5017's extraction sat on clear interior floor 2.2 m inside `cr_garage`
(footprint 36.35 x 28.35 at rot 90, spanning x −114.2…−85.8; hook at x −88),
in a pocket the site's own collision seals off. Both guards passed it
correctly; the build was refused 155 m downstream by Level Factory's
pre-flight, which is the only thing in the toolchain that computes
reachability.

The repair is a strict generalisation of code Lot already has: change
`resolve_onto_floor`'s acceptance test from *"floor an agent can stand on"* to
*"floor an agent can stand on **and reach from the crew spawn**"*. Same
nearest-first push, same findings. `site_enterability.py` may already hold the
connectivity primitive.

**H2. The box reader drops rotated colliders.**
`ground_contact.Box` is axis-aligned, so a `BoxShape3D` carrying a yaw falls
out of the walkability model entirely and lands in the `opaque` list. Lot's
`paths` are exactly this — rotated boxes, because the row's stagger puts them
off-axis. They are 14 mm decals over a plate the reader models fine, so nothing
in `lot_demo_001` depends on them; but `_caveat` asserts opaque colliders
"widen the walkable area rather than narrow it, so they cannot turn a pass into
a failure", and `Box` is load-bearing as **floor** as well as wall. That claim
is unproven in the narrowing direction. Either reduce a yawed box to its
enclosing AABB, or stop asserting the asymmetry.

**I. A failing candidate should be rejected, not block the mission.**
One of three candidates failed and the whole mission blocked, while the other
two graded fine and were usable. `Candidate` already carries `status`,
`rejection_reason` and `selected`. N candidates exist so that some can be bad;
a pipeline that stops when one is defeats the mechanism it paid for.

**J. Greybox and themed select from different pools.**
`require_themed_shells` narrows 134 → 97 on the themed path only. Same seed,
four of five archetypes differ and all five positions differ. Laser Tag grades
the greybox; the themed site ships. The comment on the branch chose grade
STABILITY over grade VALIDITY and said so; nothing had measured which side it
landed on. Also unresolved: `planner.py` claims `lot_for` is the one selection
rule while `_write_site_spec` reimplements it inline.

**K. Events report the origin as their position.**
Every entry in `lasertag.report.json`'s `events` has `"position": [0.0,0.0,0.0]`
while the real value sits in `metadata.position` — `probe_y`'s silent
substitution in a different tool. *(The companion claim that findings carry no
code is WITHDRAWN: `code: None` is Laser Tag's raw report only; LF's
`_normalize` assigns real codes and `lf validate` prints them.)*

**M. Enemy standoff: two numbers for one rule, in one file.** *(propose: high)*
`place_enemies` enforces `MIN_STANDOFF = 8.0`. The grader punishes anything
inside `MIN_ENGAGEMENT_STANDOFF = 45.0`, and per `spawn_placement`'s own
docstring "the crew's bot stops walking the moment it can see an enemy".
Measured 2026-08-09: Enemy_0 at 32.0 m from the crew spawn, admitted by
`opening_engagement_is_fair` because a building occludes it — and every one of
25 runs still stalemated for its full 180 s with 0% route completion. Either
the occlusion test and the engine disagree, or occlusion is not enough when the
bot's halt condition is sight range rather than a clear line. This is the
likeliest single cause of the stalemate and it is in Lot.

**N. The crew's sight range is not settable.** `LT_ENGAGEMENT_NOT_CONFIGURABLE`
already reports it: 45 m is an `@export` default on `LT_BotPlayerController`
that the harness never assigns, so the scenario field that looks like it sets
engagement range does not. It is also larger than the `enemy_sight_range`
(35 m) the resource does expose. Laser Tag's repo. Nothing improves a grade
until this or M lands.

**O. `run_count` is declared twice.** `25` in
`default_laser_tag_scenario.tres` and `25` again as the default in
`job_spec.get("run_count", 25)`. LF passes `--runs` so its value wins and the
scenario's is decorative — but they agree today by coincidence, not by
construction. Same shape as `PLATE_ROLES`.

**P. A job timeout must scale with the work it plans.** *(FIXED —
`patch_lf_lasertag_timeout.py`)* `plan_commands` read `run_count` from the job
spec and then planned a flat `timeout_seconds=900`, sized when the default was
8. At 25 runs Godot was killed 19 runs in, no report was written, and the
mission blocked on `JOB_TIMEOUT` for a level `walktest_navqa` walks clean. Now
`bake_wall_budget_seconds + runs * run_wall_budget_seconds`, both named with
their measurements. Note the budget is WALL clock and the scenario's
`max_run_time_seconds = 180.0` is SIMULATED — 19 runs of 180 simulated seconds
cost 900 s of wall time. Multiplying the two units together would have reserved
4,500 s for 1,200 s of work.

**Q. A site can be a shape other than a line.** *(APPLIED —
`patch_lf_site_shapes.py`)* `row` delegates to `row_offsets` so the line a
thousand graded candidates stand on has one implementation; `L` and
`courtyard` walk the same per-step gap rule and widen until no two shells can
touch under any nudge. Opt-in via `site_shape`, which reached the spec and was
read by nothing. Remaining: more shapes (`cross` is the one roads want, since
an intersection is where a street network gets a junction), and deciding
whether `courtyards` in the spec should finally get a derivable position now
that a layout can leave an open middle.

**R. The greybox exported no materials at all.** *(APPLIED —
`patch_dc_greybox_palette.py`)* Not the wrong material — none, anywhere in
Deli Counter. Eleven roles now carry a shared material each, keyed off the
`surface_roles` map DC already wrote and nothing consumed for looking. Stairs
and ladders alone are two thirds of the visual primitives on a shell.

The rule worth keeping: **value separates function, hue names it**, and the
pairs are only checked where they SHARE A VIEW. `--palette` measures relative
luminance and fails under 0.15; it caught the first draft putting stairs 0.042
from the floor, which is hue doing work value should do.

Next: bind pixelcoat packs to those material names (`gb_stair` tread banding
first), then the same table in Lot for `perim_*` / `Ground_*` / path decals —
Lot's surfaces carry no roles at all and need names inventing before they can
be painted.

**L. `lf validate` and `lf diagnostics` are underused.**
Not a defect — a discoverability note worth a line in `CLAUDE.md`. `validate`
prints every normalized finding with code, severity, scope and suggested fix;
`diagnostics` states in nine lines whether a job ran, what refused it and why.
An hour of this session went into inferring both from directory listings.
Anything that reconstructs pipeline behaviour from files on disk should check
these first — a directory that is only written when a job runs looks
arbitrarily old when the job stops running, and that is the absence of work
rather than evidence of a bug.

**F. Preview freshness is invisible.**
`run --art` does not write `preview/<mission>_walk`; only `walk` does, via a
full `rmtree` and rebuild. Nothing in the preview records which run it came
from, so reading it after a pipeline change silently reads the previous walk.
Cost about an hour and five refuted hypotheses. Cheapest fix: stamp the source
job's fingerprint digest into the preview directory and have `walk` print it.

---

## Instrument notes carried forward

Unchanged from `LADDER_INTO_SOLID_ROOF.md`, none of them fixed:

* The walk bot **names a cause** in its reason string
  (`"the slab is solid over the ladder"` — it was not a slab, and its own
  `blocker` field said `Roof` one key away). `CLAUDE.md`: a probe prints what it
  measured and stops.
* `probe_y` **silently substitutes** `rel.y + 1.0` when neither overhead ray
  hits, with a byte-identical reason string. A reader cannot tell a measurement
  from a fallback.
* The aperture sweep **varies `z` only**, at hardcoded local `x = 0`, while its
  own docstring names both axes. A hole offset across the ladder reports
  `aperture_z: []` — identical to a solid roof.
