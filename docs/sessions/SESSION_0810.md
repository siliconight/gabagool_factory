# Session 0810 — legibility, lighting, and a Laser Tag investigation that ended somewhere else

Continues `SESSION_0809.md` and `SESSION_0809_LADDER.md`.

Six patches applied, one probe added, **six of my own claims retracted**. The
retractions are the most useful part of this file and they are listed first,
because every one of them was the same mistake and the next session will be
cheaper if that mistake is recognisable on sight.

---

## The pattern, stated once

Six wrong calls in one session. Five were one error:

> **An artefact was read as evidence about a process that did not produce it.**

- `site.tscn` has no lights → "the preview is unlit". The rig is in `walk.tscn`.
- 340 m open ground lanes → "the site needs blockers". `site_cover` already
  reported `still_open: 0` and `unbreakable: 0`.
- Score 45 on all 25 CSV rows → "the score is a constant". It is a map-level
  aggregate stamped on every run row.
- Enemy hooks from the greybox build vs footprints from the themed build →
  "enemy 0 is unfair". Two different sites.
- "the bot sight range is an unassignable `@export`" → half right, asserted from
  memory. `enemy_sight_range` is a plain field in a `.tres`; the *bot's* 45 m is
  the `@export` with nothing assigning it.

The sixth was different and worth its own note: a fix whose reasoning was sound
and whose measured outcome was not (`ENEMY_SIGHT_RANGE`, below).

**The guard that came out of it:** `probe_opening.guard_same_build` refuses a
scene and a gameplay json that describe different sites. It is the only thing
written today that attacks the pattern rather than an instance of it. More like
it, please.

---

## Applied and verified

| patch | file(s) | bytes | sidecar |
|---|---|---|---|
| `patch_lot_greybox_palette.py` | `lot/lot.py` | 96,061 → 98,385 | `.pre_lotpalette` |
| `patch_lf_preview_lighting.py` | `level_factory/packages/preview/walk_preview.py` | 12,167 → 13,810 | `.pre_previewlight` |
| `patch_lot_opening_walks.py` | `lot/site_spawns.py` | 39,596 → 43,801 | `.pre_openingwalk` |
| `patch_lot_real_occluders.py` | `lot/site_spawns.py`, `lot/lot.py` | 43,801 → 50,713; 98,385 → 98,891 | `.pre_realocclude` |
| `patch_lf_mission_scenario.py` | `models.py`, `commands/__init__.py`, `adapters/laser_tag/__init__.py` | 8,156 → 9,595; 103,136 → 104,344; 15,014 → 19,663 | `.pre_missionscenario` |

`probe_opening.py` added. `lot_demo_001`'s brief gains `crew_size: 4`. Twenty-
eight `.pre_*` sidecars in the tree, and they turn out to be a ledger rather
than clutter — see below.

### The palette

Lot emitted **no material at all** on 49 boxes per scene. `_box_node` and
`_yaw_box_node` have accepted `color=` since they were written; the only three
callers passing one — `road_*`, `sidewalk_*`, `blocker_*` — are exactly the
three a generated spec never emits. That was the whole of "flat grey".

Deli Counter's rule ("value separates function, ≥0.15 between co-read
surfaces") is **infeasible on a site**, and this was solved rather than
eyeballed: the largest gap satisfying every pair in the co-read graph is
**0.140**, and the assignment reaching it is degenerate. Value holds about seven
slots at 0.15; Lot and DC have seventeen surfaces.

So value now buys only *can I stand here*, and everything else is a
chroma-carried marker:

```
road 0.131 → ground 0.317 → path 0.478 → wall 0.710 → perimeter 0.879
gaps       0.186    0.161    0.232    0.169
```

`--palette` re-checks and refuses to write if it stops holding. It caught two
things I had wrong: courtyard's "cool hue names it apart" was a 0.01 saturation
gap (added a warmth metric), and `BLOCKER_COLOR` sat 0.03 in luminance from the
new plate (moved it, and said so).

Verified on the built scene: cover 11, ground 22, path 4, perimeter 4, **missing
0** on every one.

### The preview light rig

Not missing — **badly balanced**. Directionless ambient at 1.4 against a 0.6 sun
with shadows off: 0.43 : 1 in favour of the term that cannot shade form, because
ambient adds the same amount to every orientation. Now 0.30 / 1.70 with PSSM4
shadows at 260 m, and 40° of yaw so the four perimeter walls stop being lit in
identical pairs.

```
                     was    now
square to the sun    2.00   2.00
turned away          1.40   0.30
spread               0.60   1.70
```

The rig is written at `lf walk` time, so the preview must be **rebuilt**, not
just re-run.

---

## The Laser Tag investigation

Started as "make LT good enough and move on". It did not end there.

### The grade, decomposed

`lot_demo_001` seed 5118, 25 runs, **45/100 FAIL** (WARN starts at 50):

| category | got | max | why |
|---|---|---|---|
| traversal | 0 | 25 | route completed 0% of runs, + 34 player-stuck |
| npc_pathing | 10 | 20 | 34 enemy-stuck events |
| sightlines | 10 | 20 | 37% of positions visible to 3+ enemy spawns |
| **cover** | **20** | **20** | **47% of shots blocked — full marks** |
| combat_pacing | 5 | 15 | crew under fire at 0.08 s |

**`site_cover` is the one part working perfectly.** Three separate
investigations independently confirmed it. Do not touch it.

### What was chased and what it cost

`probe_opening.py` attributed each enemy to a branch of
`opening_engagement_is_fair`: five fair by **distance** (55–129 m), one by
**occlusion** at 26.5 m, credited to `b0` — the crew's own spawn building —
covering 48% of the line.

Two hypotheses were tested and refused before that one was accepted:

- **Spawn permutation.** `use_random_spawn_permutations` shuffles only which
  enemy takes which enemy point. Six identical enemies over six fixed points is
  a geometric no-op.
- **A window too short.** `patch_lot_opening_walks.py` widened the fair-opening
  test from the spawn tile to the 4.5 m the crew walks. Verified on real data:
  **every enemy fair before, every enemy fair after.** It changed nothing, which
  is how we know the window was not the problem. The patch stays because the
  rule now asks the right question, and it will refuse a thin corner elsewhere.

`LT_EnemyBrain` fires only after a real raycast, inside 35 m. It fired at
0.08 s. So Lot's occlusion claim was false, and `lot.py` reads 959 real
colliders three lines above the `place_enemies` call and did not pass them.
That is the collider patch, and it stands on its own merits.

### The conservatism that did not survive contact

Shipped alongside it: refuse occlusion outright inside `ENEMY_SIGHT_RANGE`,
arguing that outside 35 m a wrong model costs nothing and inside it costs the
grade. Measured:

```
survival_min             6.73 → 19.60      the sub-7-second deaths stopped
enemy_stuck_events         34 → 75         and this is why
avg_enemy_deaths_per_run 0.72 → 0.24
route_completion_rate     0.0 → 0.0
total score                45 → 45
```

The crew survived longer because enemies pushed past 35 m landed on ground they
could not path off. `place_enemies` tests `outdoors()` — outside a building —
not whether the bake leaves a polygon underneath. **An opening bought by
stranding the opposition is not an opening.** Reverted; the constant stays as a
carried contract number.

### Where it actually ends

```
player_count   1     player_health   5
enemy_count    6     enemy_health    2
```

The crew must land **12 hits** to clear the map. It fires 15–17 shots and lands
6–9, and has never killed more than 2 of 6 in 50 recorded runs.
`team_wipe_count: 25` before and after.

**The scenario is unwinnable, and `route_completed` requires surviving the
route.** Traversal's 25 points cannot be earned by level geometry. Per
`OPENING_RANGE`'s own docstring — *one visible enemy is 0% route completion by
construction* — and with six enemies at 35 m sight on any real map, the crew
will see one.

The 45 ceiling is mostly a **scenario** fact, not a map fact. Level Factory ran
Laser Tag's stock `default_laser_tag_scenario.tres` on every mission it has ever
evaluated. That was the untouched lever, and it is no longer untouched — see the
next section.

---

## The mission-derived Laser Tag scenario

`patch_lf_mission_scenario.py` — `models.py` 8,156 → 9,595 (`0b9a40c73ef937d6`),
`commands/__init__.py` 103,136 → 104,344, `adapters/laser_tag/__init__.py`
15,014 → 19,663 (`a5dcac7401b9a2ae`). Sidecar `.pre_missionscenario`.

**The hook was already cut and nothing reached it:**

```python
scenario = str(job_spec.get(
    "scenario_res",
    "res://addons/laser_tag_tool/resources/default_laser_tag_scenario.tres"))
```

`scenario_res` has been readable since the adapter was written. Nothing ever set
it. **Every mission Level Factory has evaluated, ever, was graded against Laser
Tag's stock 1-versus-6** — a five-building night heist and a single-shell test
box against the same resource. Same shape as `PLATE_ROLES`, `site_lux.tscn`, and
`solids` not reaching `place_enemies`: fourth instance this session.

`MissionBrief` gains `crew_size`, `crew_health`, `enemy_count`, `enemy_health`,
defaulting to `1, 5, 6, 2` — exactly the stock numbers, so every existing brief
produces an identical scenario and no evaluated mission changes under its grade.
The job spec carries a `scenario` **dict**, not a path, because
`fingerprint_inputs` already hashes `job_spec["scenario"]`: values there mean
changing the encounter re-runs the evaluation. The adapter writes
`mission_scenario.tres` into the **staged** project — LF does not edit another
tool's checkout — with all 28 fields spelled out from one table so drift against
the stock resource is a diff rather than an excavation. No addon staged returns
`None` and falls back to stock; verified.

Nothing is derived from `building_count` or `target_minutes`. A crew size
inferred from plate area would be a number nobody chose wearing the clothes of a
decision.

`lot_demo_001`'s brief now carries `crew_size: 4`, with the measurement in its
notes. **`enemy_count` stays 6 deliberately:** Lot's `place_enemies` writes six
hooks regardless of the scenario, so asking for fewer spawns a subset over an
even spread and makes it uneven. A crew was what the brief was missing, not
fewer guards.

`functional_signature` is untouched. `enemy_count` does change the walk scene
and arguably belongs in the lock, but adding a key invalidates every lock on
disk and `rockay-ws` carries one. That is a migration.

---

## The sidecar ledger is intact — do not clean it up

Twenty-eight `.pre_*` files across the tree read as clutter. They are not: each
one is the byte-exact state of its file before one named patch, and **the chains
have no gaps.**

```
lot.py            80,916 gate → 83,086 visible → 83,419 accessor → 85,287 angle
                → 89,298 step → 90,465 source → 91,220 junction → 92,207 flat
                → 93,365 sink → 95,481 crewclear → 96,061 lotpalette
                → 98,385 realocclude → 98,891 current

site_spawns.py    35,391 crewclear → 39,596 openingwalk → 43,801 realocclude
                → 50,713 current

walk_preview.py   11,023 overlay → 12,167 previewlight → 13,810 current
```

Every arrow is a patch whose input size equals the previous patch's output size.
`crewclear` output 96,061 and `.pre_lotpalette` is 96,061; the palette output
98,385 and `.pre_realocclude` is 98,385; realocclude added 506 and the file is
98,891. **The ledger reconstructs the whole history and it reconciles.**

Deleting them removes every `--revert` in the tree. The backlog item should read
*verify the chains* rather than *clean up the sidecars*, and this is that
verification.

---

## Open, in the order I would take them

1. **Wire `enemy_count` through to Lot.** The brief can now ask for four
   enemies and `place_enemies` still writes six hooks, so the harness spawns a
   subset over an even spread. One wire — `_write_site_spec` and
   `write_walk_scene` — and it is what makes the new field mean what it says.
2. **`lux_apply` output never reaches the preview.** `walk_content_dir` returns
   `themed_site_assemble/out` and never looks at `lux_apply/out`;
   `_find_level_scene` prefers `site_lux.tscn` while lux writes
   `lux.applied.tscn`. `grep -rn "site_lux"` returns two lines, both inside the
   function that reads it. That branch has never fired. Not a rename — lux's
   `out/` holds the scene and two sidecars while the buildings it instances live
   upstream, so something has to decide where they are assembled.
3. **Enemy placement should test navigability, not just `outdoors()`.** Straight
   out of the reverted conservatism: 75 stuck events say a point outside a
   building is not the same as a point with a navmesh polygon under it.
4. **`sightlines` 10/20** — 37% of walkable positions visible to 3+ enemy
   spawns. Untouched; it is enemy spawn *distribution*, not cover.
5. **The scenario run's result.** `crew_size: 4` was applied but the grade has
   not been read. `route_completed` has been `false` 50 of 50 runs across two
   evaluations; if four crew make it true, traversal comes off the floor and 45
   becomes something in the 70s. If not, the next levers are `crew_health` and
   `enemy_count`, both now one line in a brief.
6. Backlog carried from 0809: `patch_map_derived.py` unapplied, nav-gate re-bake,
   `--sweep` summary miscount, `_bridge*` copies of plate constants, by-eye roof
   check. **The sidecar item is retired** — see the ledger section.

---

## Things now known that were not

- `site_cover.plan_cover` exists, works, and owns the "is this site too open"
  question. `probe_sightlines.py` measures open *ground lanes*, which nothing
  grades. Do not confuse them again.
- Enemy sight is **35 m** (scenario `.tres`, assignable). The bot's is **45 m**
  (`@export`, nothing assigns it). `OPENING_RANGE = 45` is deliberately the
  crew's number.
- The greybox build and the themed build of one mission stand **different
  shells**. `require_themed_shells` narrows the pool. Never compare artefacts
  across them.
- The content cache hardlinks outputs, so the device bridge refuses to read job
  outputs directly. `Copy-Item` first — it breaks the link.
- A mission's merged `site.site.gameplay.json` carries building `footprint`s;
  the plan-time spec in `temp/` does not. A probe run against the spec sees zero
  buildings and reports every line open.
