# Glossary

The words this repo uses constantly and defines nowhere central. Structural
terms — workspace, job id, DAG, seed derivation, what each repo owns — are in
`PIPELINE_MAP.md` and are not repeated here.

**Where a term has an owner's own definition, this points at it rather than
restating it.** A second copy is the drift this toolchain keeps paying for, and
a glossary that disagrees with the code is worse than no glossary.

---

## People and process

**The walker** — the person these tools are built for, who plays the generated
levels and whose taste is the final word on whether one reads as designed. "The
walker's standing call" in `CLAUDE.md` means a decision they made that outranks
a measurement.

**Cold run** — the measurement the repo exists to answer: hand the tools a spec
they have never seen, run one command, and see whether a walkable gated package
comes out with nobody touching anything. Numbered (`cold_9078`). Procedure in
`docs/COLD_RUN.md`, instrument in `tools/cold_run.py`, rationale in roadmap 17.

**Intervention** — any reach into the machine that changes what the pipeline
would do next time: an edit to a tool repo, a spec, a brief, a theme or a
genome; a hand-authored file dropped into a workspace; a re-run with *different*
arguments. **Interventions-per-level is the metric.** Deliberately NOT
interventions: an identical re-run after a transient (`--retry`), reading
anything (`--observe`), the pipeline writing into a tool repo, and the three
human approval gates. `tools/cold_run.py`'s docstring is the authority.

**Gate vs advisory** — a gate refuses; an advisory reports and lets the build
continue. The split is authority, not subject: a refusal says the tool cannot
produce information from these inputs, an advisory says it will run fine and
mark the result down (`packages/adapters/sdk.py`, `advise_configuration`). Laser
Tag is soft by contract and never refuses a map; Lux's fixture gate blocks.

**Instrument vs product** — a runtime-shaped tool here exists to discover what a
good level must satisfy, so the builder can own that as an offline check. Laser
Tag going quiet is the goal. Nothing in an instrument ships in the package.

---

## What a level is made of

**Brief** — the authored description of one mission: archetype, building count,
`candidate_count`, theme, weather, time of day, objective hypotheses.

**Batch** — a `batch.json` naming a `batch_id`, a `seed_base`, a theme family
and a list of missions. For a cold run both live under
`docs/cold_runs/<id>/`, with the brief in `briefs/<mission_id>.json` — outside
the ten hashed tool repos on purpose, and version-controlled so the measurement
can be reproduced.

**Candidate** — one of N sites planned from a brief, at a derived seed
(`seed_base + i * 101`). They are built and graded, then a human selects one.

**Archetype** — the kind of place a mission is (`strip_club`, `urban_bank`,
`walkup_siege`). Drives which building recipes and site shape are used.

**Shell** — a building as Deli Counter emits it: the greybox GLB plus its
`gameplay` / `slots` / `manifest` / `lights` sidecars. Collision truth.

**Slot** — a declared swap point on a shell, with dims and a transform, listed
in `<name>.slots.json`. Zoo builds a kit module to each slot's exact dims. A
tight palette of slot sizes is what makes wall meshes instance.

**Site** — what Lot assembles: buildings placed on ground, with roads,
sidewalks, cover, paths and spawns, emitted as a walkable Godot scene.

**Greybox vs themed build** — the same mission has both. The greybox base always
runs; Art and Gameplay are optional additive layers. **Two different builds can
stand different scenes with the same filename** — five files are called
`site.tscn` — so name which build produced an artefact before concluding
anything from it (`CLAUDE.md`, verification rule 1).

**Walk copy** — a playable export staged for a person to walk, under `_runs/`.
Evidence: read it, do not edit it.

---

## Art

**Theme** — a named curation, one grammar per material kind
(`pixelcoat/profiles/themes/<theme>.json`, e.g. `delco_1997`). The vocabulary a
building wears is entirely the theme profile.

**Kind** — the slot a material fills, and a contract about light rather than a
style: `glass` is glazed see-through by consumers, `glass_facade` is not. A
grammar whose kind disagrees with what it promises is refused
(`material_grammar.see_through_fault`).

**Grammar** — a procedural material description
(`pixelcoat/profiles/materials/<id>.json`): base colours, frequency bands,
generators, roughness response, weathering, and now `wet`. Synthesised into
maps; never a photo.

**Pack** — what Pixelcoat writes per material: the PNG maps plus a
`<asset_id>.pack.json` manifest naming them, their `meters_per_tile`, import
hints, and (since 0.47.0) `map_sha256`. Schema `pixelcoat-pack/2`, additive over
`/1`.

**Skin library** — one `<kind>_<theme>/` pack per curated material, which Zoo
resolves against via `--skins <dir> --theme <theme>`.

**Genome, DNA, species, specimen, keeper, habitat, exhibit** — Zoo's own terms,
defined in `zoo/README.md`'s glossary. Note its warning there: a species count
written into prose goes stale, so read it from `genome.list_species()`.

**Triangle budgets in Zoo's genomes are REGRESSION DETECTORS, not frame costs.**
A species that silently doubles trips one. Frame time tracks draw calls, not
triangles (`CLAUDE.md`, measured 2026-09-16).

**`next_pass`** — a second material hung off a `BaseMaterial3D`, re-rasterising
the same triangles. Used for the CRT screen roll. It costs a submission per
material that takes it — measured 2.27–4.29 µs per added draw call — which is
why a baked material *variant* is the cheap way to express a static look and a
`next_pass` is the way to express a moving one.

---

## Measurement

**Draw call / submission** — the unit frame time actually tracks here. 1,730
draws read 9.49 ms; 6,376 read 25.59 ms with the primitive count flat at ~1.4M
throughout. Price a change in draw calls AND frame time, at fixed stations,
with a control that proves the instrument can see a difference at all.

**Station** — a fixed camera position and aim a probe measures from. A figure
quoted from a single station, or from one where the view is nearly empty, is
not a frame cost.

**Control** — the thing that proves the instrument can move. A render probe once
reported "pixel-identical" from frames that were 99.7% black. A number that
cannot move is not evidence.

**Attributed vs unattributed** — in a cold run's diff, a changed file the
pipeline is known to write (matched against `GENERATED`, with a reason printed
beside it) versus one nobody has accounted for. Every entry in that table is a
claim that a human never writes there, and a wrong claim hides a real edit.
