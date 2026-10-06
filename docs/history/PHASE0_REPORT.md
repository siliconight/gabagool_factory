# Phase 0 — CLOSED (2026-07-18)

**The engine leg is green.** All four Godot gates now PASS on the user's
hardware (Godot 4.7 stable, Windows), closing Production Package §19 Phase 0
in full:

| Engine gate | Result | Evidence |
|---|---|---|
| Godot import / round-trip engine leg | **PASS** | `deli_counter/build/pvp_station_ref.godot_import.json` |
| Navmesh gate (bake + stair + markers) | **PASS** (207 polys, stair connected, 2/2 markers) | `deli_counter/build/pvp_station_ref.navgate.json` |
| Runtime walktest (reference pvp site) | **PASS** — 15/15 path proofs (2 classified vertical/ladder), 4 players 8/8 targets (~326 m each), 12/12 bots | `_runs/ref_pvp_proj/ref_pvp_site_navqa.walktest.json` |
| Multiplayer smoke (4 players) | **PASS** — 3/3 clients connected, moved 5.4–24.3 m, clean teardown | `_runs/ref_pvp_proj/ref_pvp_site.mp_smoke.json` |

The 24-round shakedown produced one **shipped-defect discovery** (every
single-story cut_slabs stair discharged into a walk-off void — fixed in the
generator, `deli_counter` 0.79.0), the **agent contract** (single source of
truth for character metrics and derived clearances, `AGENT_CONTRACT.md`),
and a hardened QA harness whose failure modes are now documented in the two
repos' changelogs. Certified set: **factory 1.1.0** (deli_counter 0.79.0,
lot 0.19.0, pipeline 0.1.1). Reference registry records stamped `pass` on
all engine-gate fields; registries coherent.

---

# Phase 0 — Validation Foundation: Delivery Report

**Date:** 2026-07-17 · **Scope:** Production Package §19 Phase 0, sandbox-runnable items (0.1–0.9, 0.11). Engine-leg items (0.10) are specified and stubbed but require a Godot 4 binary — see "What still needs your machine."

## Test state at delivery

| Suite | Result |
|---|---|
| Deli Counter (`pytest`) | **298 passed**, 2 opt-in bpy tests skipped by default (`DC_BPY_TESTS=1` runs them; both pass) |
| Lot (`pytest tests/`) | **48 passed** |
| Zoo (`pytest tests/`) | **199 passed** |
| pipeline registrar (`pytest tests/`) | **16 passed** |
| `validate.py --all` (31 specs) | all pass |
| `roundtrip.py --all` (12 built GLBs) | **12/12 PASS** |
| `evidence.py --all` | 30 spec evidence packages written |
| `registry.py check` | registries coherent |

## What was built, per repo

### deli_counter (new/changed)
- **`pvp_heist.py`** — the gating PvP profile. Named gates with stable codes:
  PVP-SPAWN-A/D (spawn presence), PVP-SPAWN-BOUNDS, PVP-OBJ, **PVP-ROUTES**
  (≥2 interior-disjoint attacker routes via true Menger max-flow on the room
  graph), PVP-EXTRACT (objective→extraction/exit), **PVP-SPAWN-LOS**
  (opposing-spawn clear-ray check reusing sightlines geometry), **PVP-ROTATE**
  (protected defender rotation avoiding attacker entry rooms), PVP-FLANK,
  PVP-BREACH (breach must connect two resolvable spaces). Wired into
  `validate.py` as a blocking gate when `mode: "pvp_heist"`; added to the
  schema enum; combat_audit's heist+cqb packs auto-apply to pvp_heist.
- **`evidence.py`** — persists proof: `<name>.validation.json` (every gate,
  pass/fail + errors), `<name>.combat_audit.json` (full findings; HIGH
  findings **block** under pvp_heist, stay advisory in legacy modes),
  `<name>.navigation.json` (room graph, entries, objective rooms). Runs the
  same analyzer modules as validate.py — reports can't drift from the CLI.
  Auto-runs after every successful `build.py` build.
- **`roundtrip.py`** — the coordinate round-trip test (Blender leg).
  Expectations (visual bounds, origin, floor elevations, marker positions)
  are recorded **at build time** into the manifest's new `expected` block;
  roundtrip re-imports the exported GLB into a clean scene and enforces the
  ratified tolerance table (RT-SCALE / RT-BOUNDS / RT-ORIGIN / RT-MARKERS /
  RT-FLOORS). Writes `<name>.roundtrip.json`.
- **Applied-scale export fix** — the round-trip test immediately caught a real
  contract violation: boxes exported as unit cubes with node scale
  (34×26×0.3 slabs). `_apply_scales()` now bakes any non-unit scale into mesh
  data at export (multi-user module meshes made single-user first), so every
  production node ships at scale 1,1,1 per §14.
- **`review_render.py`** — the §16 standard review package: front/rear/left/
  right/roof/entrance/objective/gameplay-height/collision views + contact
  sheet + review.json, under a fixed neutral rig (identical FOV, exposure,
  sun+world, camera-riding interior lamp, 1.8 m character reference at the
  primary entrance). Cycles CPU, headless.
- **`specs_failing/`** — 10 known-bad fixtures + `FIXTURES.json` manifest;
  `test_failing_fixtures.py` proves each fails **for its documented reason**
  (sealed box, unreachable room, broken stair, orphan ladder, bad mode, and
  five pvp fixtures), plus bad-GLB coordinate fixtures (non-unit scale,
  drifted bounds) generated on the fly against roundtrip.
- **`slots.json` always-on for production** — pvp_heist builds force the
  modular emitter (`DC_MODULAR=1`) so the Zoo art-pass contract is always
  emitted (256 slots for the reference station).
- **`specs/pvp_station_ref.json`** — the passing reference pvp building
  (police station layout + extraction marker), passes every offline gate with
  stored evidence and renders.
- **`docs/COORDINATE_CONTRACT.md`** — the ratified shared contract (also
  copied into lot/ and zoo/). Key ratified decision: **spec/manifest space
  stays Blender-native Z-up meters**; Godot-import Y-up conversion is a
  tested boundary (round-trip), not a rewrite. Tolerances live in
  `roundtrip.py::TOLERANCES`.

### lot (new/changed)
- **`pvp_heist` site mode** in `site_tactical.py`: pre-merge gates (spawn/
  objective/extraction designations; routes spawn→objective→extraction; ≥2
  distinct approaches; attacker staging site-marker required) + post-merge
  `gate_merged()` (defender spawns must exist in the merged site; opposing-
  spawn separation ≥ 25 m default, per-site tunable via `pvp.min_spawn_
  separation`; protected defender hold — defenders in the objective building
  or with a rotation avoiding the attacker staging building). Merged
  `site.gameplay.json` now carries a `pvp_heist` report block.
- **`specs_failing/`** — 4 site-level failing fixtures + manifest + test.
- **`specs/ref_pvp/`** — the reference pvp mission site: 3 building
  placements (bank_job ×2 reused at different transforms + the reference
  station), road/courtyard/cover/perimeter, staging + extraction site
  markers. Assembles clean: pvp gates pass, 2 objective approaches,
  walkable + nav-QA scenes emitted.
- 12 new tests (`tests/test_pvp_site.py`, `tests/test_failing_fixtures.py`).

### zoo (new/changed)
- **Missing-module gap report** — `plan_kit(known_species=…)` routes slot
  roles the genome library can't build into `missing_modules` (with reasons)
  instead of crashing at build time; `build_kit` reports `n_missing` and
  persists the list in the kit index.
- **Kit index enrichment** — `*_kit.built.json` module entries now carry the
  full §2 contract: `category` (taxonomy), `dims`, `pivot`, `forward`
  (`+Y` authoring convention; the DC slot transform owns final facing),
  `supported_slot_types`, `material_set`, `collision`, `lod`, `status`.
- **Slot-fit authority fix** — genome prop-era dimension ranges demote to
  warnings when an exact slot fit target exists (the `fit_*` checks still
  gate hard). Found via the real integration run: DC legitimately requests a
  0.3 m-wide wall return the prop ranges never anticipated.
- **End-to-end proof** — the reference station's real 256-slot `slots.json`
  through `build_kit`: **14 modules built, 0 failures, 0 missing**.
- 3 new planner tests.

### pipeline (new)
- **`registry.py`** — the registrar. Enforces §20/§21: ID grammar
  (`BLD_<FAMILY>_<letter><nn>` embedding the family, `MSN_<NAME>_<nn>`),
  §6/§7 dimension vocabularies, **sibling distinction ≥2 tactical AND ≥2
  visual dimensions**, approved-requires-proof (gates = "pass", proof files
  exist on disk, visual score ≥4, no blocking/high issues, ≤5 mediums, no
  medium touching navigation/collision/coordinates, owner+date), mission
  rules (building counts by classification, no orphan config refs, no
  duplicate full combos, hero needs ≥2 reviewers averaging ≥4.5, family
  overuse >4 missions needs approval), automatic config↔mission back-link
  sync, deterministic byte-identical writes, and `check --portfolio` for the
  Phase 4 acceptance targets. Reference registries under `registries/` hold
  the two candidate configs + reference mission, coherent.

## What still needs your machine (the engine leg — Phase 0 item 0.10)
The sandbox cannot install Godot (binary downloads are outside its network
allowlist), so four gates are specified but not runnable here:
1. **Godot import gate + round-trip engine leg** — import each GLB, compare
   against the same manifest `expected` block roundtrip.py uses, then place
   via Lot with a known transform and compare world positions.
2. **nav_gate** — DC's existing headless navmesh proof (`nav_gate.py --all`).
3. **Automated walktest bot** — the `heist_nav_qa` addon Lot's `--navqa`
   scene feeds is not in any repo and must be built; Lot already emits the
   anchor groups it consumes.
4. **Multiplayer smoke test** — greenfield minimal harness (host + N clients:
   spawn, traverse, objective, extract).

The two registry gate fields for these ( `runtime_walktest`,
`godot_import`, `multiplayer_smoke_test`) are recorded as
`pending_engine_leg` on the reference records — the registrar will refuse
approval until they read `pass`, which is exactly the intended behavior.

## Phase 0 done-criteria status (§19)
| Criterion | Status |
|---|---|
| pvp_heist selectable in Deli Counter | ✅ |
| pvp_heist selectable in Lot | ✅ |
| Shared coordinate contract | ✅ ratified, documented in all three repos |
| Building + mission registry schemas | ✅ + enforcing registrar |
| Structural validator | ✅ (existing chain + persistence) |
| Navigation validator | ✅ offline; engine navmesh leg pending Godot |
| Coordinate round-trip test | ✅ Blender leg (12/12 GLBs); engine leg pending |
| Visual review renderer | ✅ |
| Known failing fixtures, failing for documented reasons | ✅ 14 DC + 4 Lot |
| Validation tools run from CLI | ✅ all |
| One reference building passes all gates | ✅ pvp_station_ref (offline gates) |
| One reference Lot site passes all gates | ✅ ref_pvp_site |
| Evidence stored with outputs | ✅ validation/combat/nav/roundtrip/review JSONs+PNGs |

Phase 0 is complete for everything this environment can execute; the four
engine-leg items are the remaining gap and the first order of business for
Phase 1 (they block the "runtime walktest" acceptance criteria, not the
vertical-slice authoring work).
