# The backdrop world generator

PROPOSED, and not started. The walker supplied a TDD on 2026-09-26 —
*Backdrop World Generator, Draft 1* — with "I think we need to make this tool
eventually for level factory". This is the read of it against what the factory
already has, so that when it is started nobody rebuilds four things that exist
and nobody skips the one that does not.

The TDD itself is the design. This file is only the routing and the
disagreements.

## What it asks for

A compiler that takes a playable level's geometry plus a regional profile and
emits a non-playable surrounding world: roads continuing past the map edge,
facade shells, midground blocks, distant silhouettes, sky and haze — so a small
heist site reads as part of a larger place from streets, windows and roofs. It
generates nothing traversable: no interiors, no AI, no navigation, no loot, no
ordinary collision.

Its own example names `level_id: flappahs_01`, which is this project's gas
station, so it was written with this factory in mind rather than in general.

## The half that already exists, under other names

Four of its implementation sections describe machinery the factory ships. A
backdrop generator should CALL these, not reimplement them.

| The TDD asks for | Who already does it |
|---|---|
| `OccluderInstance3D` for large reliable blockers, "after measuring CPU and GPU impact" | Level Factory: `assets/godot/bake_occluders.gd` and `count_occluders.gd`, and every package ships `occluders.tscn` with `occlusion_culling/use_occlusion_culling=true` in its `project.godot` |
| `MultiMeshInstance3D` "partitioned into modest spatial sectors ... one giant city-wide MultiMesh can waste GPU time" | Lot's surface dressing — 4,107 instances in 4 draw calls — and CLAUDE.md already states the rule as "one MultiMesh per room, block or wall run, never one for the level, because a MultiMesh is a single object to the culler" |
| "Share the playable level's `WorldEnvironment` and directional lighting ... avoid a second conflicting sky or light rig" | Lux owns the environment and the rigs; a second one is not currently possible |
| Deterministic output, manifest with input hashes and an output hash, "byte-identical for equal inputs" | Level Factory's whole contract: `portable_resource_manifest.json` carries a sha256 and a size per file, every job writes a `.provenance.json`, and the 133-shell rebuild of 2026-09-26 came back byte-identical |
| A validation report with actionable errors | LF's validation record and its finding codes; a backdrop's checks want to be findings there, not a separate `report.json` nobody reads — see `ZOO_CAPABILITY_GAP` below |

The TDD arriving independently at the MultiMesh-sector rule is worth noting: it
was derived here from a measurement (cold run 9062, 1,730 draws at 9.49 ms
against 6,376 at 25.59 ms) and there from Godot's documentation. Two routes,
same rule.

## The half that is genuinely new

Nothing in this factory does any of this, and none of it is a rename of
something that does:

* **Visibility analysis.** Sample reachable viewpoints, cast coverage rays into
  angular bins, union the visible intervals into an envelope, and generate only
  where a player can actually see. This is "prefer not submitting to submitting
  cheaply" applied to a skyline, and it is the part worth building first.
* **Edge continuation.** Roads, sidewalks, utility runs and grades crossing the
  playable boundary with matched width, heading and material. Lot builds a site
  and stops at its edge.
* **Midground and far vista.** Grouped low-detail blocks, regional silhouettes
  at plausible bearings, and the `north_yaw_degrees` discipline that keeps a
  water tower in the same direction from every vantage point.
* **A region catalog** of constraints and weighted assets, separate from
  environmental lighting, so one region can have several times of day.

## Where it disagrees with what this repo has measured

Three places, and each needs settling with a number rather than a preference.

**1. "Draw calls are diagnostic, not the sole pass/fail criterion."** On this
toolchain they are very close to the criterion. Measured 2026-09-16 on cold run
9062's package: 1,730 draw calls read 9.49 ms with 13% of frames over 16.7 ms,
6,376 read 25.59 ms with 99.6% over, while the primitive count sat at about
1.4M the entire time and never moved. Render-CPU was roughly twice GPU. A
backdrop budget that watches GPU time and treats draw calls as advisory is
watching the wrong number on this renderer.

**2. The provisional budget is stated GPU-first**: "≤0.5 ms p95 GPU and ≤0.2 ms
p95 CPU". Given the above, the CPU line is the binding one here and 0.2 ms is
tight — the drip fragment measured +1.85 ms worst-station for 19 wall
materials. Calibrate against a real slice before either number is treated as a
gate, which the TDD does say.

**3. The target renderer.** The TDD benchmarks "the desktop 60 FPS preset".
Packages here ship on **GL Compatibility**, on purpose, as the low-end target —
with `max_lights_per_object` at 8 and, as of 2026-09-26, a known history of
lighting that silently under-delivered on it. A backdrop validated only on a
desktop preset would be validated on a renderer this project does not ship.

## The one line in it this repo has just paid to learn

> Ray-based analysis is an optimization hint, not a visibility guarantee: test
> actual camera sweeps after assembly.

Cold runs 9081 through 9083 are that sentence in three acts. The manifest said
the canopy anchors were there; the package had no canopy. The properties said
125 lights were dynamic, positioned and in range; the pixels said they moved
the frame by 0.5%. Both were found by rendering a frame and measuring it, after
the artefacts had all agreed with each other. Any backdrop visibility envelope
needs the same treatment: a camera sweep that reads pixels, not a ray count
that reads intent.

## What to build first, if it is started

Not the generator. **The visibility analysis, alone, as an instrument** — sample
the reachable positions of an existing package, cast the rays, and produce the
heatmap and the envelope with nothing generated from it.

Three reasons. It is the genuinely new part, so it is where the learning is. It
is independently useful the moment it exists: it answers "which directions does
this level actually expose?", which nothing currently answers and which bears on
occluder placement and LOD today. And it can be checked against a thing that
already exists — run it on a shipped package, then walk that package and see
whether the sectors it called visible are the ones you can see. An envelope
that disagrees with a walk is a bug found before a single facade is generated.

Roadmap item, unfiled. The TDD is in the walker's Downloads; when this is
started, copy it in beside this file so the design and its assessment travel
together.
