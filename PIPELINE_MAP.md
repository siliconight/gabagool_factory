# Pipeline map — the repos, how they chain, and what each run should leave behind

Orientation for anyone (human or agent) picking up work in `gabagool_factory`
without having lived through the last month of it. `PIPELINE_ROADMAP.md` is the
*current* state of a specific investigation; this file is the *standing* shape
of the system. Read this first, then the roadmap.

Sources: `factory.manifest.json`, `README.md`, `AGENT_CONTRACT.md`,
`ENGINE_GATES.md`, `level_factory/packages/pipeline/planner.py` (the DAG is
defined there and nowhere else), `level_factory/packages/adapters/registry.py`,
and the live `rockay-ws` workspace.

## The shape in one paragraph

Nine standalone tool repos build levels for someone else's game. Level Factory
is not a tenth tool — it is the orchestrator that plans a DAG of jobs, hands
each to a thin adapter, and records what came back. A mission brief fans out
into N candidate sites; each candidate is built by Deli Counter (buildings),
assembled by Lot (site), and graded by Laser Tag (map quality). One candidate
is then selected and locked, and only then do the optional layers run: Art
(Pixelcoat, Zoo, Patina, Lux) and Gameplay (Dispatch). The graybox base always
runs; the layers are independent and additive.

## What the stack is for, and what it is not allowed to decide

**The deliverable is a level shell for somebody else's Godot project.** It has to
open in that project and work as intended while depending on none of these
tools: no `level_factory`, no `lot`, no `deli_counter`, no Laser Tag addon, no
script from any repo here. Everything the shell needs is baked into the package.
If it only works because one of our tools is on disk, it is not a deliverable,
it is an instrument that escaped.

**These tools are not the authority on gameplay or networking.** Replication,
tick model, player controllers, weapons, AI, netcode, difficulty, time-to-kill —
all of it belongs to the consuming game, and none of it may be decided here.
`ENGINE_GATES.md` states the boundary and the DAG has to be read through it:
what we certify is the *asset* — geometry, collision, navigability,
reachability, closure — never the game played on it. Dispatch even emits the
boundary machine-readably as `runtime_ownership_requirements.json`: the things
the consumer owns, listed, rather than assumed.

The practical consequence is that our runtime-shaped tools are **instruments,
not products**:

* Laser Tag is a firefight simulator whose purpose is to *discover what a good
  level must satisfy* so Deli Counter and Lot can own that as a check. Its bots
  are not the consumer's AI and its combat model ships to nobody. A finding of
  its is a request for a guardrail upstream, not a verdict to enforce
  downstream. Its addon is staged into a throwaway project and never enters the
  package.
* `nav_qa_director.gd` and `mp_smoke.gd` are disposable QA harnesses, and
  `ENGINE_GATES.md` is explicit that neither may grow into a player controller.
* `site_walk.tscn` is an evaluation scene — it references `lot_site_walk.gd` and
  `lot_player.gd`, which is exactly why it is not what ships.

So the rule of thumb when reading the stage table below: a guardrail belongs in
the tool that *builds* the thing, checked offline before the scene is written,
and the runtime legs exist to prove the guardrail was the right one. Laser Tag
going quiet is the goal; Laser Tag's score going up is not.

### What "standalone" is enforced by, today

`presentation_compose` publishes the whole composed package rather than a
filtered set, because a folder without `project.godot` and an entry scene is not
a Godot project — an earlier suffix filter dropped it and the export opened the
Project Manager instead of the level. `PRESENTATION_UNRESOLVED_REF` is a
**blocker** on dangling or absolute `res://` references, and staging's
`_resolve_absolute_refs` copies absolutely-referenced files into the project and
rewrites the path. That last one exists because Lot bakes building GLBs by
absolute path, producing `res://C:/Projects/.../shell.glb` — a reference to one
developer's disk, which is the plainest possible violation of this rule and is
still carried as unfixed at source.

`exports/<mission>.portable-godot/` is the standalone artifact, and
`dispatch_handoff` produces the handoff package proper: `mission.tscn`,
`mission_manifest.json`, `gameplay_anchors.json`,
`runtime_ownership_requirements.json`, `proposed_beat_graph.json`,
`navigation_hints.json`, `build.lock.json` and `HANDOFF.md`. Note the shape of
those names — anchors, hints, *proposed* beats, ownership *requirements*. The
package tells the consumer where things are and what it must decide. It does not
decide for them.

## Two-layer versioning

Each tool is its own git repo with its own semver, VERSION file, CHANGELOG and
tags. **Code changes always land in a tool repo, never at the factory level.**
The factory root versions the *combination*: `factory.manifest.json` pins the
tool versions certified together, and `factory_version` bumps when that set
changes. Every tool directory is gitignored at the root.

Lockstep check (the checking code lives in Level Factory, because code stays in
tools):

```powershell
level-factory verify-manifest --factory C:\Projects\gabagool_studios\gabagool_factory
```

`OK` = pin matches. `DRIFT` = same major, re-certify and bump. `INCOMPATIBLE` =
major bump, adapters likely broken. `UNKNOWN` = no VERSION source, which is the
known state for patina, pixelcoat and lasertag — see the notes in the manifest.

## Running it

The CLI's real home is `apps/cli/main.py`; `pyproject.toml` exposes it as a
`level-factory` console script for installed copies. For a source checkout with
no install, `level_factory/__main__.py` exists so `python -m level_factory`
works — but that directory has no `__init__.py`, so it resolves as a namespace
package **only when the factory root is the working directory**.

```powershell
cd C:\Projects\gabagool_studios\gabagool_factory
python -m level_factory -C <workspace> run <mission_id> --art
```

Running it from inside `level_factory` puts the wrong directory on `sys.path`
and fails with a bare `No module named level_factory`. That failure looks like
a broken install and is not one.

`--art` selects the Art layer. Legacy `--target` values map onto layer sets:
`functional-lock` = graybox only, `dispatch-handoff` = graybox + gameplay,
`presentation` = the full stack.

## The workspace

A workspace (e.g. `rockay-ws`) has two halves, and the distinction matters:

**Authored input** — `batches/<batch_id>/` holds `batch.json` (batch id,
mission list, `seed_base`, theme family) and
`missions/<mission_id>/brief/brief.json` (archetype, building count,
`candidate_count`, `target_minutes`, theme, objective hypotheses, notes).
Alongside it, `factory.project.json` carries project defaults. Note that
project defaults and a brief can disagree — `rockay-ws` defaults to
`target_minutes [25, 35]` while the Category 5 brief asks for `[12, 20]`.

**Machine state** — `.level_factory/` holds everything a run produces:

| Directory | Holds |
|---|---|
| `jobs/<job_id>/out/` | Each job's declared artifacts, plus provenance sidecars |
| `staging/<job_id>/` | Throwaway Godot projects assembled for headless addon runs |
| `exports/<mission>.portable-godot/` | Portable exported project |
| `cache/`, `temp/`, `locks/` | Scratch and concurrency control |
| `approvals/`, `validation/`, `preview/` | Gate and review state |
| `index.sqlite` | The run index — its mtime is a good proxy for "when did a run last finish" |

Job ids are `<mission>.<stage>.candidate.seed_<seed>` for per-candidate jobs and
`<mission>.<stage>` for singletons. Candidate seeds are derived deterministically
as `seed_base + i * 101`, so the same brief always plans the same candidates —
`rockay_category5` at `seed_base 5017` with `candidate_count 5` gives 5017, 5118,
5219, 5320, 5421.

## The DAG

Defined in `packages/pipeline/planner.py::plan_mission`. Graybox runs per
candidate; everything below the gate runs once, on the selected candidate only.

| Stage | Adapter | Resource | Depends on | Expected outputs |
|---|---|---|---|---|
| `deli_generate` | deli_counter | blender | — | `shell.glb`, `shell.gameplay.json`, `shell.slots.json`, `shell.manifest.json`, `shell.lights.json` |
| `lot_assemble` | lot | python_cpu | deli | `site.tscn`, `site_walk.tscn`, `site.site.gameplay.json`, `site.site.lights.json` |
| `laser_tag_evaluate` | laser_tag | godot_headless | lot | `lasertag.report.json`, `lasertag.report.csv` |
| *candidate selected + functional shell locked* | | | | |
| `pixelcoat_build` | pixelcoat | python_cpu | lot | `<kind>_<theme>/` skin library (dynamic; adapter validates) |
| `zoo_kit_build` | zoo | blender | lot, pixelcoat | named by `building_id` at exec; adapter validates |
| `patina_apply` | patina | python_cpu | lot | `shell.patina.glb`, `shell.patina.json`, `shell.patina.gameplay.json` |
| `patina_dressing` | patina | python_cpu | patina_apply | the above plus `shell.patina.dressing.json` |
| `zoo_dressing_build` | zoo | blender | patina_dressing, zoo_kit | named by `building_id` at exec |
| `zoo_fixtures_build` | zoo | blender | deli (selected) | named by `scope_id` at exec |
| `presentation_compose` | presentation | python_cpu | deli, zoo_kit, zoo_dressing, zoo_fixtures | `presentation/site.tscn` |
| `lux_apply` | lux | godot_headless | presentation_compose | `lux.applied.tscn`, `lux.quality.json`, `lux.validation.json` |
| `lux_fixture_gate` | lux | godot_headless | zoo_fixtures | `fixture_gate.report.json` |
| `dispatch_handoff` | dispatch | python_cpu | lux (with Art) or lot (without) | `mission.tscn`, `mission_manifest.json`, `gameplay_anchors.json`, `runtime_ownership_requirements.json`, `proposed_beat_graph.json`, `navigation_hints.json`, `build.lock.json`, `HANDOFF.md` |

Two edges are easy to miss. `presentation_compose` is what makes `--art` mean
"themed level" rather than "grey level with a lighting pass" — it fits themed
Zoo modules onto the greybox slot footprints while keeping greybox floors and
collision as the walkable base. And `lux_apply` runs over that *composed* scene,
not over the raw Lot site.

## The repos

**level_factory** — orchestrator. `packages/` holds the engine (pipeline,
adapters SDK, staging, validation, reporting, exporting, approvals, review);
`adapters/` holds one thin module per tool; `apps/cli/main.py` is the CLI. Owns
the job graph, the workspace, provenance, and the manifest lockstep check. Note
`presentation` is a registered adapter but *not* a tool repo — it drives Deli
Counter's own bpy-free scene composer.

**deli_counter** — buildings. Blender-side generator producing the greybox shell
GLB plus its gameplay/slots/manifest/lights sidecars. It is the source of
collision truth, and it owns `agent_contract.json` (see below). Also carries the
`godot_gate.py` / `nav_gate.py` / `roundtrip.py` building-level gates.

**lot** — sites. Pure-Python assembler that places buildings, routes, cover,
crew and enemy spawns onto a site and emits the walkable Godot scene. Where the
engagement-fairness logic lives (`site_spawns.py`, `site_cover.py`,
`site_pacing.py`). Also carries the site-level gates `walktest.py` and
`mp_smoke.py`.

**lasertag** — map grader. Godot addon run headlessly against a staged project;
samples the walkable floor for sightlines, simulates runs, and reports
engagement metrics and findings. **Soft gate by contract**: it grades a map, it
never refuses one — `Scheduler._advise` forces every advisory non-blocking and
demotes a BLOCKER to MAJOR. Its findings are answered by changing what gets
built, not by blocking the build.

**pixelcoat** — materials. Builds the themed skin library (one `<kind>_<theme>/`
pack per curated material) that Zoo kits resolve against. Version lives in
`pixelcoat/version.py`, not a root VERSION file.

**zoo** — kit and props. Blender-side builder of structural kit modules from DC
slots (skinned by Pixelcoat), plus dressing props and light fixtures. Names
outputs by `building_id` / `scope_id` at execution time, which is why the
planner declares no fixed expected outputs for Zoo stages and the adapter
validates instead. Kit modules are center-pivot slabs built to each slot's
*exact* dims, edge-beveled per style, and they carry their own collision — see
the collision contract below, which is subtler than it looks.

**patina** — cohesion and dressing. Pure-Python passes that unify the look
across a shell and emit the dressing manifest Zoo builds from. Its repo VERSION
file is currently empty, so the manifest check reports UNKNOWN.

**lux** — lighting. Godot-headless PS2-era look pass over the composed
presentation scene, plus the light-fixture gate. Unlike Laser Tag, fixture-gate
findings are **blocking** — a floating light or a dark fixture is broken output,
not a style note.

**dispatch** — handoff. Assembles the mission-shell package the consuming game
takes: scene, manifest, anchors, beat graph, navigation hints, ownership
requirements, lock file and `HANDOFF.md`. Contract pinned in `tools.lock.json`
as `dispatch.mission.v0.2`. This is the stage that produces the actual
deliverable, and everything upstream of it is either baked into that package or
was an instrument used to prove the package is sound.

**pipeline** — registries. Config/family/mission/hero records and the registrar
that refuses `approved` until every gate field reads `pass`.

## The collision contract — who owns the walkable surface

Worth getting exactly right, because two files in the stack describe it in
opposite terms and both are correct about different modes.

**Zoo modules do carry collision.** `recipes/_arch.py::build_slab` returns
`collision_boxes`; `core/arch.py::collision_boxes` emits one box per *solid*
part and deliberately gives the passable void none, "so doorways / windows /
breaches are walk/shoot-through". The `wall`, `doorway`, `window` and `breach`
genomes all set `collision: true`, and `bpylayer/build.py::build_module` (the
kit path) calls `collision.collision_from_boxes`, which writes a `<Root>-colonly`
sibling — Godot's import convention for "become a static collision shape and
discard the visual mesh". So a Zoo doorway module describes a genuinely better
collision volume than a solid greybox slab does.

**But in the Level Factory `--art` path, that is not what makes the level
walkable.** `themed_tscn.py::write_themed_tscn` has two modes. Without
`base_res`, Zoo's own collision carries the scene — "the resulting scene is
walkable directly, no greybox overlay needed", which is the standalone
copy-into-your-game path the Zoo README describes. With `base_res`, a greybox
**floors + collision** GLB is instanced at identity as the functional shell —
"collision and nav live on the greybox" — and the themed modules ride on top,
oriented by fitting each footprint to the greybox slot's measured extent rather
than trusting the slot's raw `rot_y`, so that "the art conforms to the collision,
by construction."

The pipeline uses the second mode. `portable_building.build_package` builds the
base via `strip_greybox_base`, which drops a greybox *visual* only when its node
name carries a themed slot id, and whose collider rule is unconditional:
`"colonly" in name` → keep, commented `never touch collision/nav`. **Every
greybox collider survives the strip.** The presentation adapter's capabilities
are `collision_fit` and `greybox_base`, and it raises
`PRESENTATION_PLACEMENT_MISMATCH` when a themed module's footprint does not match
the greybox footprint — a gate whose whole purpose is catching visuals drifting
off collision they do not own.

So: Zoo geometry **substitutes for the greybox visual at swapped slots**, and
greybox collision **remains authoritative**. Zoo's collision is not thrown away
— the module GLBs still carry their `-colonly` siblings and the LF Zoo adapter
passes no `--no-collision` for kit builds — it is *additive on top of* the
retained greybox collider rather than a replacement for it.

**Open question, not yet answered anywhere I could find.** Nothing gates that
additive overlap. Dressing has such a gate — `ZOO_DRESSING_HAS_COLLISION` is a
**blocker**, because covers are visual-only by contract — but there is no
equivalent for kit modules, and by inspection the composed scene should contain
both the greybox collider at a swapped slot and the Zoo module's own `-colonly`
volume. For exact-fit slabs those volumes are near-coincident, which is wasteful
rather than wrong; the case worth actually checking is an opening, where Zoo's
void is deliberately passable and the greybox's collider decides whether it
really is. Verify against a composed scene before relying on either answer.

## The contracts

**`deli_counter/agent_contract.json`** owns every character dimension and every
clearance derived from it — capsule metrics, nav bake parameters, door and
corridor minimums, QA tolerances. Door width, agent radius and bake cell size
are one decision, not three: a 0.4 m agent at 0.25 m voxels silently erodes 1.0 m
from every doorway and fragments a legal building into disjoint navmesh islands.
Change a body there, re-derive by the rules in `AGENT_CONTRACT.md`, re-run the
gates. Every consumer carries a fallback equal to the ratified values, so a
missing file degrades rather than breaks.

**The handoff boundary** (`ENGINE_GATES.md`) — this stack certifies the *asset*,
never the game. Replication, tick model, player controllers, weapons and AI
belong to the consumer. `nav_qa_director.gd` is a disposable QA harness and must
never grow into a player controller; `mp_smoke.gd` is replication-free by
contract, not by omission. A gate that seems to need gameplay logic is a signal
it belongs in the consumer's test suite.

**Tool paths and binaries** live in `<workspace>/tools.local.json`
(Blender, Godot, and each repo path); version/contract requirements live in
`tools.lock.json`. Godot is pinned at 4.7, Python at >= 3.11.

## Traps worth knowing before they cost you a day

*Invocation.* `python -m level_factory` from the wrong directory fails as
`No module named level_factory`. Run from the factory root.

*Staging directories are reused across runs.* A staged Godot project is not
rebuilt from nothing each time. This produced a graded scene from a build nobody
had asked about, with every mtime on disk agreeing it was current. The staged
scene is now deleted before anything else is decided, and `staging.notes.json`
records `scene_source`, `scene_source_sha256` and `scene_staged` — check those
rather than trusting timestamps. Sibling *subdirectories* are still only copied
`if not dst.exists()`, so the same family of defect remains there.

*mtime is not provenance.* More than one component decides "is this current?" by
comparing timestamps. Filesystem timestamps come from a coarse clock — one timer
tick, ~1-4 ms on Linux and ~15.6 ms on Windows — so two operations microseconds
apart can carry the *same* stamp. `cater.needs_build` compares spec against glb
with a strict `>`, which means a spec edited inside the same tick as the build
finishing is judged fresh and never rebuilt. Prefer a content hash.

*Version constants disagree, deliberately.* Lot reports 0.24.0 / 0.17.2 / 0.18.0
/ 0.32.0 across `VERSION`, `lot.py`, `version.py` and CHANGELOG, and Level
Factory 0.13.4 vs 0.13.19. Fingerprints depend on these, so they are left alone.
Do not "fix" them casually.

*Provenance sidecars recurse.* Every artifact accumulates
`x.provenance.json.provenance.json...` nested about eleven deep in every job
directory. Cosmetic, noisy, and it makes directory listings hard to read.

*Absolute `res://` refs.* Lot bakes building GLBs by absolute path, producing
non-portable `res://C:/Projects/.../shell.glb`. Staging rewrites these into real
`res://` paths on the way in, and `PRESENTATION_UNRESOLVED_REF` blocks if any
survive — but the source still emits them, so the standalone guarantee is
currently held up by two downstream repairs rather than by Lot not breaking it.
That is the wrong end. A package that references one developer's disk is the
plainest violation of the contract at the top of this file, and the fix belongs
where the path is written.
