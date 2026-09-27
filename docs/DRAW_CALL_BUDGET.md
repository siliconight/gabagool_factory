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

### 5. Nothing measures any of this per run

`tools/cold_run.py` counts interventions. `tools/wet_ab.gd`,
`tools/occlusion_ab.gd` and `tools/tint_merge_ab.gd` measure frames at fixed
stations on one package, by hand, when someone remembers. There is no
per-run draw-call report, no worst-sightline station set, and no gate.

`PERFORMANCE_CONTRACT.md` §10 calls for a permanent benchmark set and notes
it does not exist. **That is the item that makes every other item on this
list checkable**, and it is the one to build first — a fixed station set per
package reporting draws, triangles, frame ms, GPU ms, render-CPU ms and the
lights-per-object histogram, so a change can be priced without a human
walking the level.

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

## Open questions this file does not answer

- Whether partitioning the dressing MultiMesh is a net win (item 1). It is a
  GPU-side measurement and nobody has taken it.
- What an exported build on a low-end GL Compatibility machine actually does.
  Every number here is a debug walk copy on an RTX 2060.
- Where the 5,739-draw views come from. The draw count roughly quintuples
  between the cheapest and dearest station in one level and nothing attributes
  it — that attribution is a prerequisite for reducing it, per `CLAUDE.md`'s
  rule about accounting for every item in a gate's output before patching it.
