# The draw-call budget, and what 60 FPS costs

The walker's target, stated 2026-09-27: **60 FPS**, which is 16.7 ms for the
whole frame — gameplay, netcode, physics, audio and rendering together.

The source is *Godot 4.7 Draw Call Optimization Guide*, copied in at
`docs/reference/Godot_4_7_Draw_Call_Optimization_Guide.md` so the guide and
this assessment travel together. The guide is the design; this file is the
routing, the measurement, and the disagreements.

It sits under `docs/PERFORMANCE_CONTRACT.md` §2 (define the target) and §7
(design rules), and unlike that document it carries numbers measured on this
project's own output.

---

## The one thing the guide declines to give, and this project has

> "There is no dependable rule such as 'X draw calls for 60 FPS': the cost
> varies with hardware, renderer, materials, visibility, and GPU workload."

Correct in general, and the guide's own remedy is the right one — *"profile a
representative scene on target hardware, then set a project-specific
draw-call guardrail."* This project has now done that twice, on different
packages, and got the same shape both times.

**Cold run 9062's package, 2026-09-16**, camera walked through a generated
level:

| draws | frame ms | frames over 16.7 ms | primitives |
|---:|---:|---:|---:|
| 1,730 | 9.49 | 13% | ~1.4M |
| 6,376 | 25.59 | 99.6% | ~1.4M |

**Cold run 9088's walk copy, 2026-09-27**, read off the F4 overlay while the
walker moved through the level. Same package, same machine, one session:

| draws | triangles | frame ms | GPU ms | render-CPU ms |
|---:|---:|---:|---:|---:|
| 1,091 | 139,440 | 6.23 | 2.12 | 4.65 |
| 1,484 | 1,805,782 | 7.03 | 1.19 | 5.36 |
| 2,257 | 1,897,424 | 11.28 | 3.24 | 9.34 |
| 2,834 | 1,977,130 | 11.93 | 8.30 | 10.58 |
| 5,287 | 2,078,242 | 23.24 | 15.85 | 20.97 |
| 5,429 | 2,099,044 | 26.14 | 20.60 | 24.33 |
| 5,483 | 2,066,184 | 27.48 | 21.15 | 25.92 |
| 5,739 | 2,070,880 | 29.90 | 23.33 | 28.03 |

Two things to read off it, and one caution.

**Triangles again did nothing.** Across rows 2–8 the triangle count moves
1.81M → 2.07M, a 15% change, while frame time moves 7.03 → 29.90 ms, a factor
of 4.3. The 2026-09-16 finding reproduces on a different package and a
different camera path. Row 1 is a sky-heavy view with almost no geometry in
frame and is not comparable to the rest; it is kept because dropping the
inconvenient sample is how a curve gets invented.

**Render-CPU exceeds GPU at every station** — 4.65 vs 2.12, 9.34 vs 3.24,
20.97 vs 15.85, 28.03 vs 23.33. That is the guide's §3 test for "is CPU-side
submission actually the bottleneck" answered YES for this content. Draw-call
work is the right thing to attack here; the guide is explicit that this must
be established rather than assumed, and it is established.

**The 16.7 ms crossing sits at roughly 3,900 draws** by interpolation between
the 2,834 (11.93 ms) and 5,287 (23.24 ms) rows.

### Why the guardrail must be far below 3,900

The measurement above is not the shipping condition, and every difference
runs the same way:

- **Debug build, walk copy**, with the F3/F4 overlay running. The guide's §2
  says acceptance decisions need exported builds.
- **An RTX 2060 at 1152×648.** Packages ship on **GL Compatibility as the
  low-end target on purpose** (`CLAUDE.md`). This is not that machine.
- **Nothing else is running.** No enemies, no AI, no netcode, no other
  players, no audio, no UI. The 16.7 ms is shared with all of it, and this
  game is multiplayer online — the walker's standing rule is that a cost here
  is paid on every client in a session.
- **One camera path, one seed, one level.** §3 of the contract asks for nine
  scenarios; this is roughly scenario 3 and part of 4.

So: **a provisional guardrail of 2,000 draws in the worst sightline**, which
is about half the measured crossing, with the remainder reserved for the work
that was absent from the measurement. It is provisional in the precise sense
that it should be replaced the moment someone measures an exported build on
a low-end GL Compatibility machine with bots running — and that measurement,
not this number, is the deliverable.

Cold run 9088's own worst observed view was **5,739 draws at 29.90 ms**, so
today's output is roughly **2.9× over** that guardrail at its worst and about
1.4× over at a typical traversal station.

---

## Where the factory already does what the guide asks

| The guide asks for | Who already does it |
|---|---|
| MultiMesh for large repeated populations | Lot's surface dressing: 6,566 instances in **4 draw calls** on cold run 9088 |
| Merge compatible geometry | Zoo 1.1.0's per-module merge by material: 118 meshes to 4, triangles identical, interiors 59–63% faster |
| Occlusion culling where rooms hide the level | Level Factory: `bake_occluders.gd`, 401 occluders shipped in 9088 with `use_occlusion_culling=true` |
| Don't express variation as new materials | `CLAUDE.md`'s cheapest rule, and LF 0.118.0's `material_census.py` measures violations — 908 entries, 242 names, 183 in 11 tint families on cold 9080 |
| Frame time in ms, not FPS; median and worst | `PERFORMANCE_CONTRACT.md` §3, and the F4 overlay reports ms, worst frame, and hitch counts |
| Change one factor at a time, same camera | How the merge, the CRT pass and the tint merge were all priced |
| A control that proves the instrument can see | `CLAUDE.md`'s hard rule, learned from a render probe that reported "pixel-identical" from frames that were 99.7% black |

The guide arriving independently at the MultiMesh-partitioning rule is worth
noting: this repo derived it from cold run 9062's measurement, the guide from
Godot's documentation. Two routes, same rule.

---

## Where the factory does NOT do what the guide asks

These are the gaps, in the order the measurement says to take them.

### 1. The dressing MultiMesh is one batch for the whole level

The guide's second named mistake is *"making one MultiMesh for the whole
level"*, and `CLAUDE.md` states the same rule in this repo's own words: *"one
MultiMesh per room, block or wall run — never one for the level, because a
MultiMesh is a single object to the culler."*

Measured on cold run 9088's shipped package
(`club_block_014_dressing.tscn`):

    MM_litter_scrap   instance_count = 1665
    MM_pebble         instance_count = 1709
    MM_rubble_frag    instance_count = 1571
    MM_weed_tuft      instance_count = 1621
                      4 MultiMeshes, 6,566 instances

and the level's geometry bounds are **230.3 × 11.3 × 115.3 m**. So each of
the four batches spans the entire site: stand anywhere and all 6,566
instances are submitted, because any part of the bound being visible makes
the whole batch visible.

**The repo is breaking its own rule in shipped output.** The 4-draw-call
figure that gets quoted as a success is the same fact as the culling failure
— the batch is cheap to submit precisely because it is one object, and it is
one object precisely because it cannot be culled.

Unknown, and worth measuring before acting: whether partitioning helps here
at all. 4 draw calls is already negligible against 5,739, so the win would be
**GPU-side** — not submitting ~6,500 instances' geometry when the camera sees
a corner. The guide is clear that this is a different bottleneck and must be
measured separately. Partitioning into, say, 6×3 cells would take 4 draws to
72 and remove most of the instance geometry; whether that trade is positive
is a measurement, not a deduction.

### 2. No MultiMesh sets `custom_aabb`

`grep -rn custom_aabb` across `lot`, `zoo`, `level_factory` and `lux` returns
**nothing**, and the shipped dressing scene has zero occurrences. The guide:
*"For procedurally placed instances, compute or assign a `custom_aabb` that
enclosed the full possible instance extent... An undersized bound can make
the batch disappear or clip unexpectedly; a needlessly huge bound weakens
culling."*

Godot computes a bound from the instance transforms when none is given, so
this is not currently a correctness bug. It becomes one the moment anything
partitions or repopulates a batch, which is exactly item 1. Fix them
together.

### 3. Mesh LOD and visibility ranges are unused

No `visibility_range`, no `lod_bias`, no HLOD anywhere in the tool repos. The
walker's standing constraint applies and is not in dispute — *"what I don't
want is for us to reduce poly count 'just cause' it's more than Halo"* — and
the silhouette-reading work (`docs/proposals/SILHOUETTE_READING.md`)
deliberately keeps LOD out.

That decision is about **authored polygon budgets**, and it should hold.
Runtime LOD is a different question, and the measurement above is the reason
to reopen it narrowly: at 2.07M triangles and CPU-bound submission, LOD's
value here would be in **collapsing distant objects into fewer submissions**
(visibility-range HLOD), not in thinning near geometry. That is the shape
worth a proposal; per-mesh decimation is not.

### 4. The per-object light cap interacts with all of this

Measured on cold run 9088: **34 of 4,625 meshes are reached by more than 8
lights**, the cap on GL Compatibility — worst a 47 m roof reached by 47
lights, and interior floors and ceilings at 19–21. The guide flags the same
hazard for MultiMesh specifically: *"the resource is treated as one object
for the maximum-lights-per-object restriction."*

So merging and instancing both trade draw calls for lighting fidelity, and
this project has already paid that price without noticing: Zoo's
merge-by-module made interiors 59–63% faster and made this worse. Any
partitioning work in item 1 should report the light-per-object histogram
before and after, because it moves both numbers at once.

### 5. Nothing measured any of this per run — BUILT, LF 0.122.0

`tools/cold_run.py` counts interventions. `tools/wet_ab.gd`,
`tools/occlusion_ab.gd` and `tools/tint_merge_ab.gd` measure frames at fixed
stations on one package, by hand, when someone remembers. There was no
per-run draw-call report, no worst-sightline station set, and no gate — every
number in the table above was transcribed from a screenshot of a person
walking the level.

**`level_factory/tools/perf_stations_run.py` is that harness.** Stations come
from the package's own `gameplay_anchors.json`; each takes four headings and
reports the worst, because facing matters more than standing. It reports
draws, primitives, objects, frame-time median/p95/worst, a GPU/CPU split and
the lights-per-object histogram in one place.

    python level_factory/tools/perf_stations_run.py <exported package>

First run on cold run 9088's own package, 12 stations warm:

| station | p95 ms | draws |
|---|---:|---:|
| extraction_10 | 13.55 | 3,507 |
| player_start_28 | 13.35 | 3,710 |
| attacker_spawn_16 | 12.77 | 3,403 |
| camera_socket_1 | 11.12 | 3,124 |
| crew_spawn_2 | 9.37 | 2,755 |
| objective_4 | 4.64 | 2,289 |

**12 of 12 stations over the 2,000-draw guardrail; 5 over 11 ms.** And it
agrees with the walk overlay independently — 11.85 ms at 2,287 draws from the
harness against 11.28 ms at 2,257 draws read off F4 during the walk. Two
instruments, two runs, one curve.

Exit codes match `tools/check_all.py`: 0 clean, 1 findings, 2 COULD NOT
MEASURE.

**Three measurement traps it fell into first, recorded because each produced
a confident wrong answer and the third is the interesting one:**

* **An unimported package measures as a fast one.** A portable package ships
  sidecars and no `.godot`; without importing it once no GLB loads, only the
  four dressing MultiMeshes draw, and the first run reported **4 draw calls at
  all 29 stations** as "every station inside budget".
* **A truncated run reported a pass.** The watchdog fired, the probe wrote
  what it had, and the caller read it as finished.
* **The instrument cost 13x the frame it was measuring.**
  `RenderingServer.viewport_set_measure_render_time` inserts GPU timestamp
  queries every frame: with them on, `defender_spawn_25` read **109.26 ms**
  p95 at 3,025 draws; with them off, **8.35 ms**. `debug_overlay.gd` had
  already found this and enables them only while its panel is visible. Frame
  time is now measured with the timers off; the GPU/CPU split comes from a
  separate short pass with them on and is labelled as not comparable.

The remaining gap is the one §2 names: every number here is still a debug
build on an RTX 2060. The harness makes an exported-build run on a low-end GL
Compatibility machine a command rather than an afternoon.

---

## What this changes about how a change gets priced

Unchanged, and restated because the guide agrees with all of it:

- Price a look **on/off, at several fixed stations, with a no-change
  control**, on the target renderer.
- Report **draw calls AND frame time**, split CPU and GPU. A draw-call number
  alone is diagnostic, not a verdict — the guide's first named mistake and
  this repo's own experience both say so.
- **A number that cannot move is not evidence.** If a control that should
  change the measurement does not, the instrument is blind and the table is
  worthless.

Added by the 60 FPS target:

- **16.7 ms is the whole frame, on somebody else's machine, with other
  players in the session.** A station reading 11.93 ms in an empty debug walk
  is not passing; it is using 71% of the budget before the game is in it.
- **Report the worst station, not the average.** Cold run 9088's walk ranged
  6.23 → 29.90 ms across one level. The average of that is a number nobody
  experiences.

---

## Where the draw calls actually come from — ATTRIBUTED, 2026-09-27

`level_factory/tools/draw_attrib.gd`. The harness said twelve of twelve
stations were over budget; this says what is submitting. It counts the
passes of every drawable whose world AABB survives the camera frustum,
groups them by the GLB they came from, and — the part that makes it an
attribution rather than a story — **checks the model against the engine's
own draw-call counter at every station**.

    camera_socket_0   actual 4,008 draws
      visible surfaces (colour pass)   1,771    44%
      sun shadow pass                  1,712    43%
      local light shadows (12)           522    13%
                                       -----
                                       4,005    vs 4,008 measured

    camera_socket_1   actual 5,071 draws
      colour 2,329 (46%) + sun 2,217 (44%) + local 525 (10%) = 5,071  exact

With both shadow passes switched off, draws divided by frustum-visible
surfaces is **1.00 and 1.00**. The model is not approximating.

### The headline: about 44% of the frame is the moon's shadow map

One `DirectionalLight3D` resubmits every caster in the level. It is the
single largest line in the budget at every station measured, larger than all
the geometry a player can see, and larger than the twelve local
shadow-casting lights by a factor of three.

This is a LIGHTING dial, not a geometry problem, and the levers are ordered:

* `directional_shadow_max_distance` — the sun's shadow frustum currently
  reaches far enough to include most of a 230 x 115 m site. Cutting it
  reduces the caster set directly and costs shadow detail only at range.
* `shadow_casting_setting = OFF` on small clutter. The walker's supplied
  bible says the same in its §2 generator rule ("disable shadows on small
  clutter and distant characters"), and it is an authoring decision in Zoo
  and Lot rather than a Lux one.
* Fewer directional splits.

None of it touches the moonlight itself, which the walker likes and which is
`delco_night`'s tuned 0.75 at elevation 38. Shadow RANGE is not shadow
PRESENCE.

### What was refuted on the way, each by measurement

| Suspect | Verdict |
|---|---|
| Local light shadows | real, but **10–13%** |
| `next_pass` material chains | **3 extra passes in the entire level** |
| Multiple surfaces per mesh | every drawable has exactly **1** — Zoo's merge-by-material worked |
| Something in the visible geometry | after both shadow passes, the ratio is exactly 1.00 |

### The visible half, ranked

Consistent across stations, as a share of the colour pass:

    19-21%  lux.applied              site surfaces, roads, walls, in-scene
    10-13%  strip_club_a01_dressing
     9%     prop_simple              parked cars
     5-6%   prop_shelving, prop_club, site_base
     3-4%   prop_cocktail, prop_parking, prop_bar, wall_delco_1997_01

No single prop family dominates. Halving the *geometry* would save about a
quarter of the frame; halving the *sun's caster set* saves about a fifth on
its own and touches nothing a player sees standing still.

### Two probe bugs worth recording, because both produced confident nonsense

* **The frustum sign convention was backwards** and the first run reported
  "predicted 0 surfaces on 0 objects" at all eight stations while the engine
  drew four thousand. The probe now CALIBRATES the sign against a point that
  must be inside the frustum, and prints the calibration, rather than
  asserting a convention.
* **`current_scene = scene` before `add_child` is refused outright** by Godot
  4.7 ("Condition p_scene->get_parent() != root is true"), so the assignment
  silently did nothing. Several probes in this session drew conclusions from
  a scene whose `current_scene` was null — including the one that briefly
  "found" a Lux defect that did not exist. Use `change_scene_to_packed`.

## The shadow cut, end to end — cold run 9089

Lux 0.50.0 cut `delco_night`'s `sun_shadow_max_distance` from 60 m to 30.
Cold run 9089 is 9088 again with that one change, same mission, same seed,
same candidate, and it closed at **zero interventions** with the same 34 and
58 findings. The harness against both packages, worst heading per station:

| station | 9088 (60 m) | 9089 (30 m) | ms |
|---|---|---|---:|
| extraction_10 | 13.55 ms / 3,507 | 8.89 / 2,300 | -34% |
| player_start_28 | 13.35 / 3,710 | 8.84 / 2,773 | -34% |
| attacker_spawn_16 | 12.77 / 3,403 | 8.04 / 2,167 | -37% |
| attacker_spawn_11 | 11.85 / 2,287 | 7.45 / 1,692 | -37% |
| camera_socket_1 | 11.12 / 3,124 | 5.85 / 2,024 | -47% |
| crew_spawn_2 | 9.37 / 2,755 | 5.38 / 1,953 | -43% |
| extraction_3 | 8.84 / 2,903 | 5.64 / 2,027 | -36% |
| camera_socket_0 | 8.52 / 2,351 | 6.51 / 1,941 | -24% |
| defender_spawn_25 | 8.35 / 3,025 | 5.16 / 1,566 | -38% |
| patrol_point_5 | 7.00 / 2,216 | 4.71 / 1,824 | -33% |
| defender_spawn_24 | 5.46 / 2,056 | 2.71 / 793 | -50% |
| objective_4 | 4.64 / 2,289 | 2.14 / 1,278 | -54% |

**Stations over the 11 ms budget: 5 to 0.** The worst is 8.89 ms against a
16.7 ms frame, so the level now has better than 7 ms of headroom for the
gameplay, AI, netcode and other players that none of this measurement
contains.

**Stations over the 2,000-draw guardrail: 12 to 5**, and the five that remain
sit at 2,024-2,773 rather than 3,000-3,700.

Every station improved and none regressed, which is what a single global
dial should look like. It is also the cheapest change in this file by a wide
margin: one number in one preset, no geometry touched, no authoring work, and
`lux_preset.gd`'s own luma numbers say the night look is unaffected.

WHAT IT DOES NOT DO. It is a NIGHT preset change. The daytime presets keep
60 m, the same cut there is unmeasured, and a daylit level will still carry
the full sun-shadow pass -- which attribution put at 43-44% of submissions.
That measurement should be repeated on a daytime package before assuming the
saving transfers.

## Against the walker's performance bible

`docs/reference/Godot_4_7_Multiplayer_Procedural_Level_Performance_Bible.md`,
supplied 2026-09-27. Three places it bears directly on the numbers above.

**Its §2 budget is much stricter than this file's**: ≤800 visible opaque
submissions at 60 FPS against the 2,000 derived here, with measured stations
at 2,056–5,071. Both can be right — theirs is a starting point for the
*minimum supported device*, this file's is the measured 16.7 ms crossing on
an RTX 2060 in a debug build. The honest reading is that 2,000 is generous
and should move toward 800 once anyone measures on a low-end GL
Compatibility machine, which is already the open item in §2.

**Its §2 caps real-time shadow-casting lights at 1 sun + 2 local for 60
FPS.** This package ships 12 local. Measured, those 12 cost 10–13% of
submissions — so the cap looks conservative *for draw calls*, and if it is
right it is right about GPU time, which nobody here has measured.

**Its §8 "required generated report" is very nearly `perf_stations.gd`**, and
named two camera probes the harness did not have: the **longest sightline**
and the **highest vantage point**. Both are now derived from the package (LF
0.124.0), and the first run proved the bible's point in one line:

    highest_vantage   12.17 ms p95   2,649 draws   <- the worst station in the level

Worse than all twelve anchor stations, whose worst was 8.89 ms. The view that
blows the budget was the one that had never been measured. It puts cold run
9089 back to one station over the 11 ms frame budget.

**And then it did not hold still.** The second run read the same station at
22.89 ms p95 at a different worst heading, with fewer draws (2,429 against
2,649) and a GPU/CPU split of 8.25 / 12.03 that does not add up to it. One
sample each. That is run-to-run instability at a station that looks across
the whole level, not a measurement of it, and the harness does not yet repeat
a station to tell the two apart. Until it does, "the vantage is the worst
station" is the honest reading and "22.89 ms" is not.

The **longest sightline** landed a real view once misses stopped counting:
127.7 m from `extraction_10` at yaw 293, 10.02 ms and 2,139 draws. Its first
run had ranked a 500 m ray that hit nothing -- a 4.6 m eye from a camera
socket clears the perimeter wall -- and measured 260 draws of void. Rays that
leave the map are now counted apart: **37 of them on this package**, which is
a finding about the boundary height against a standing eye, not about the
frame. Stations currently come from gameplay
anchors, which covers spawn and combat centre. Those two are exactly where a
level blows its budget and they should be added.

Its §2 also caps unique materials in a visible area at 80; `material_census`
found 242 names on cold 9080, 183 of them in 11 tint families.

## The sky, priced — cold run 9090

Cold run 9090 is 9089 again with Lux 0.53.0: SkyMint 1.1 spawned by the
`delco_night` preset (cube-sampled `empty_space` at brightness 8, clouds
off) and nothing else changed. It closed at **zero interventions**, same
seed, same candidate, same 34 and 58 findings, 1,356 files, closure clean.

The harness read every station **higher than 9089 at identical draw
counts** — extraction_10 8.89 → 10.20 ms on 2,300 draws both times,
player_start_28 8.84 → 10.70 on 2,773. Draws are the budget in this file, so
a cost that moves with none of them is a different kind of cost, and it was
priced the way CLAUDE.md asks: the same package, copied, with the preset's
`sky_provider_script` blanked and nothing else touched, run through the same
harness back to back. Worst heading per station, sky on / sky off:

| station | sky ON p95 / gpu | sky OFF p95 / gpu | draws | Δ p95 | Δ gpu |
|---|---:|---:|---:|---:|---:|
| highest_vantage | 13.10 / 7.19 | 11.41 / 5.62 | 2,649 | +1.69 | +1.57 |
| player_start_28 | 10.70 / 5.30 | 10.45 / 3.65 | 2,773 | +0.25 | +1.65 |
| extraction_10 | 10.20 / 4.76 | 10.02 / 3.48 | 2,300 | +0.18 | +1.28 |
| attacker_spawn_16 | 9.82 / 4.34 | 8.56 / 2.73 | 2,167 | +1.26 | +1.61 |
| attacker_spawn_11 | 9.53 / 5.15 | 8.74 / 2.56 | 1,692 | +0.79 | +2.59 |
| longest_sightline | 9.22 / 4.76 | 8.02 / 3.08 | 2,139 | +1.20 | +1.68 |
| camera_socket_1 | 7.99 / 3.25 | 6.94 / 2.08 | 2,024 | +1.05 | +1.17 |
| extraction_3 | 7.40 / 2.66 | 6.81 / 2.05 | 2,027 | +0.59 | +0.61 |
| crew_spawn_2 | 6.88 / 3.04 | 6.65 / 1.64 | 1,953 | +0.23 | +1.40 |
| objective_4 | 3.36 / 1.58 | 2.82 / 1.10 | 1,278 | +0.54 | +0.48 |

(Four stations picked a different worst heading between the two runs and
are left out rather than compared across headings. Reports:
`docs/cold_runs/cold_9090/perf_stations.json` and
`perf_stations_nosky_control.json`.)

**The sky costs about 1.3 ms of GPU and 0.2–1.7 ms of p95 at every
station, on identical draw counts.** It is a per-pixel cost — a fullscreen
shader — so it scales with resolution and not with the level, which is the
one shape of cost this file's draw-call reasoning cannot see. **The harness
renders at a fixed 1280×720** (`perf_stations.gd` `W`/`H`), 0.92 megapixels,
so 1.3 ms there is about 2.9 ms at 1080p and 5.2 ms at 1440p on the same
card before any difference in the card. On an RTX 2060 at 720p that is
inside the 11 ms budget everywhere except the vantage, which was over
without it (11.41). On the GL Compatibility target it is unmeasured and will
be larger in proportion.

**And it is not the shader — ATTRIBUTED on cold run 9091's package, twelve
copies later.** The paragraph that stood here said the cost was the cloud
block and the cheap version was one `if`. Measured, that `if` recovered
nothing, and neither did anything else in the shader. Same package, one
change per copy, same harness, median GPU delta over the stations whose
worst heading matched (reports in `docs/cold_runs/cold_9091/`):

| copy | what changed | Δ gpu ms |
|---|---|---:|
| cloud branch | `if (cloud_density < 1.0)` around the cloud work | −0.00 |
| cloud branch, hard | the same, `false` at compile time | −0.05 |
| + TIME = 0 | every `TIME` a constant | −0.00 |
| + no equirect | the `SKY_COORDS` path deleted | −0.07 |
| + minimal tail | sun block only after the fetch | −0.05 |
| QUALITY | `process_mode` REALTIME → QUALITY | +0.03 |
| QUALITY + write-on-change | and no uniform written after frame 1 (counted: 0 in 120) | −0.06 |
| mipmaps | mip chains on the cube faces | −0.08 |
| **V1** | a valid sky of ONLY the two cube fetches and the grade | −0.07 |
| **V2** | a valid sky of a FLAT COLOUR, no fetch at all | −0.05 |
| **V5** | V2 with `radiance_size` 128 → 32 | **−0.67** |
| **V4** | V2 with ambient Flat Color and `reflected_light_source` DISABLED | **−1.23** |
| sky off (9090) | Lux's ProceduralSkyMaterial instead of SkyMint | −1.39 |

A flat colour through a custom sky shader costs what the whole of SkyMint
costs. **The cost is not in the sky pass; it is the sky's radiance map —
rendered and filtered from the custom shader every frame on GL
Compatibility, and read back by every lit surface as ambient and
reflection.** Shrinking the map halves it; taking away its readers removes
it. `delco_night` leaves `ambient_mode` at its default, Sky, with
`room_probes_replace_ambient` putting the sky's contribution at 1.0 — so
every exterior surface's ambient IS a sample of this map, and every
material's specular reflects it.

**A retraction inside the attribution.** Two earlier copies read −1.24 ms:
a "minimal shader" and "minimal + sun", each built with an early `return`
in `sky()`. The harness swallows engine stderr; a windowed capture
(`tools/sky_look.gd`) printed `SHADER ERROR: Using 'return' in the 'sky'
processor function is incorrect`. Those shaders never compiled, Godot drew
no sky, and −1.24 was the cost of no sky — which is also why it matched
"sky off" so neatly. Every conclusion drawn from them for the hour in
between was discarded, and V1/V2 were built valid and compile-checked in
a window before being measured. Name what produced the artefact.

**What this leaves the walker to choose**, because each has a look attached:

- **Radiance 32** (V5): −0.67 ms. Ambient and reflections come from a 32²
  map of a black sky with stars, instead of 128². At night that is a blur
  of a blur. Cheapest to ship — one enum in `skymint.gd`.
- **Flat ambient, no sky reflections** (V4): −1.23 ms, the whole cost.
  Exterior ambient becomes the preset's `ambient_color` (0.16, 0.19, 0.30)
  at 0.55 rather than a sample of the sky; no material reflects the sky.
  That is a visible change to the night, in either direction, and the
  walker judges it at runtime.
- **Leave it**: 1.3 ms at 720p, scaling with pixels, on a card that has
  the headroom — and an open item for the GL Compatibility target.

`process_mode` QUALITY did not help, with the uniform writes proven off.
Either Compatibility re-renders the radiance every frame whatever the mode,
or something not counted still dirties the sky; the two are not separated,
and it is the next question if V5 is chosen.

**The rest of 9089's 1 ms is the day.** The control run (sky off) still
read ~1.2 ms above 9089 at the same draws — extraction_10 10.02 against 8.89
— on the same machine a day apart, one sample each. The harness still does
not repeat a station, so drift of that size is the noise floor these tables
sit on until it does.

Stations over the 2,000-draw guardrail on 9090: **7 of 14** — the five
anchors 9089 had, plus the vantage and the sightline, both of which were
over on 9089 too and simply had not been stations then.

## Open questions this file does not answer

- Whether partitioning the dressing MultiMesh is a net win (item 1). It is a
  GPU-side measurement and nobody has taken it.
- What an exported build on a low-end GL Compatibility machine actually does.
  Every number here is a debug walk copy on an RTX 2060.
- Where the 5,739-draw views come from. The draw count roughly quintuples
  between the cheapest and dearest station in one level and nothing attributes
  it — that attribution is a prerequisite for reducing it, per `CLAUDE.md`'s
  rule about accounting for every item in a gate's output before patching it.
