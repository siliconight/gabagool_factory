# Session state — 2 Aug, the themed site, and what walking it found

Written as a handoff. Everything below is measured unless it says otherwise.

The short version: the export went from a bare ground plate to a four-building
themed site you can walk, and then a human walked it and found six defects in
twenty minutes that four instruments and 497 tests had all passed.

## What shipped, and the numbers that say so

| change | repo | evidence |
|---|---|---|
| `themed_site_assemble` DAG node | level_factory | overview eye_y 21.97 → 115.68 against greybox 122.39 |
| export ships `site.tscn` again | level_factory | `EXPORT_CLOSURE_BROKEN` cleared |
| entry instances one scene, not two | level_factory | `write_entry_scene`, + graybox control test |
| scene-declared colliders read | lot | 329 pass, 6 new tests |
| site spec emits paths + perimeter | level_factory | Lot's "isolated buildings" finding gone |
| Sun Link `node_paths` fix | factory tools | 1 directional light, was 2 |

Five instruments were built and are in `tools/`:

| tool | answers |
|---|---|
| `glb_uv_census.py` | which UV channels a GLB carries |
| `stage_census.py` | what each stage hands the next, and refuses cross-run compares |
| `insert_overhang.py` | how far an insert deviates from its slot |
| `walk_themed.py` | assembles a walkable project from the themed site |
| `look_shots.py` / `.gd` | exposure through cameras derived from the mission spine |

## The state of a level, measured

```
lot_assemble          137 nodes   greybox site, 4 buildings, ~150 m
presentation_compose  353 nodes   ONE themed building (named site.tscn)
themed_site_assemble  119 nodes   the site: 1 ext_resource, 4 instances
lux_apply             120 nodes   +1 LuxRoot, +2 refs
export                120 nodes   ~142 m, four buildings in frame
```

Walk test, seed 5320: **4 walkers, 16/16 targets, 816–821 m, 4 vertical legs by
ladder.** 27 of 31 path proofs pass. The 4 failures share one signature to two
decimals — path stops 7.79 m short, ends at y = 4.3, target stands at y = 0.2,
at proxies 1, 5, 9 and 13 of 16. **The same slot in each of four buildings**: one
defect replicated, an upper floor with no route down.

## What the walk found — the ranked list

Full detail in `PIPELINE_ROADMAP.md` items 36 and 37.

1. **All 28 fluorescent anchors are inside floor slabs.** Every level: the anchor
   sits 0.10 m below the floor above while the room's ceiling is 0.30 m lower,
   so the light is buried 0.20 m inside a 0.30 m slab. One wrong reference plane
   — measured from the slab above instead of the ceiling below. Windows, wall
   packs, signs and streetlights are all placed correctly; it is the
   ceiling-mounted type alone, and all of them.
2. **The z-fight gate is being served from cache as green.**
   `compose.summary.json` reads `ok: false`, 8 buried pairs at both storey
   ceilings, while the job reported `cache`.
   `run_presentation_compose.py` returns 3 on that condition.
3. **`Dressing` is unpoliced and mis-placed.** 2255 props spanning y −4.37 ..
   12.61 around a building of −4.00 .. 8.00. The rods are `Cover_pilaster`
   (×299) standing free in open floor; the parapet stubs are `Cover_edge_strip`
   (×64) a metre above the roof; the slabs above the roofline are
   `Cover_panel_field` and `Cover_gutter_run` reaching 12.6 m — gutters 4.6 m
   above the roof they drain. 114 nodes sit under the basement floor. All
   collision-less by contract, so a player walks through them. `Dressing`
   answers no slot, so the placement gate's 318 never include it, and the
   circulation gate covers doors, ladders and stairs but not open floor.
4. **Every building on the site is the same building.** `_write_site_spec` hands
   all N buildings one `shell.glb`; only `at` and `rot` differ. Deli Counter has
   **41 archetypes across 103 GLBs** going unused.
5. **Windows shade as moiré.** The modules ship `glass_wavy_normal.png` and the
   geometry carries no UV channel at all.
6. **Openings stack in one wall column** — a door with a door above it, a wall
   crossing a window. Same family as (2).

## What is NOT wrong, and it cost a day to establish

**Zoo's structural inserts are exact.** `insert_overhang.py` finds no module off
its slot in any axis — not oversize, not tipped — and Deli Counter's own
placement gate independently reads `318/318 matched`. The suspicion that inserts
were dodging the shape contract is refuted twice over.

Also not defects, though this file's predecessors said otherwise:

- **The `-1` group is the BASEMENT.** `-1: y −4.00..−0.30`, `0: y 0.00..3.70`,
  `1: y 4.00..7.70` — three storeys, one footprint.
  `COORDINATE_CONTRACT.md`: *"basement = story −1"*. Roadmap 33 and 34 recorded
  it as a sentinel index and a defect to chase. Do not chase it.
- **`lux_apply` drops nothing.** +1 node, +2 refs, measured on one run.
- **The closure judge is correct.** It caught a real regression on its first
  outing and was overruled from a directory listing.

## Interiors are dark for three independent reasons

Objective shot: frame mean 69.1, **centre 44.9**. The centre statistic separates
inside from outside now; three separate causes sit behind that number:

1. `gl_compatibility` is hardcoded in `_write_project_godot`, which forecloses
   SDFGI and VoxelGI, so Pixelcoat's emissive layer lights nothing.
2. Nothing calls the light loader (roadmap 30 — and note both spawners are
   `RefCounted` statics, so `_build_modules` was never the place). Zoo's
   `LuxEmit_*` markers DO exist — 38 of them in the fixtures layer, contrary to
   item 30's reading, which was taken on the shell glb.
3. Every fluorescent anchor is 0.20 m inside a slab.

**Order matters here.** Fixing (2) alone would spawn 28 lights inside solid
slabs: the census would report 28 lights present, the rooms would stay dark, and
the fix would read as having failed for another reason. Fix (3) first.

## The method lesson, because it cost more than any defect

Six hypotheses were refuted by measurement in one day: the `site.tscn` skip, the
closure judge, a dropped container subtree, node ownership, import sidecars, and
the `-1` sentinel. Each looked right until it was counted.

Three of them survived as long as they did for one reason: **a file on disk was
read as evidence about a run that did not write it.** A stale
`export_closure_scan.json` read three times, a `project.godot` the editor had
rewritten, a staging directory re-imported two days after its job. The rule was
already in the roadmap, about seed 5320, and was quoted twice before being
broken again. `stage_census.py` now refuses cross-run comparisons by default —
and the one finding committed as ESTABLISHED and later retracted in full was
written after overriding that refusal with `--allow-mixed`.

And the blunt one: four instruments and 497 tests passed a package that was a
photograph of an empty plate. **The first look at a rendered frame settled it in
a glance, and the tool that takes those frames had been in the repo all day.**

## Pick up here

In order:

1. **Light anchor heights** (roadmap 36). One reference plane, all 28
   fluorescents, and it unblocks item 30.
2. **The cached red gate** (roadmap 36). A gate that knows the answer and is not
   heard is worse than no gate.
3. **A rule for `Dressing`** before a fix: `allowed_inward_intrusion_m` in the
   slot manifest and a gate that reads it. Today there is nothing to violate.
4. **Building variety** (roadmap 37) — and the three-type model the session
   ended on: facades that cannot be entered, buildings that can, and mission
   buildings. That is a design decision, not a bug fix.
5. The four-fold missing descent from the walk test.
6. UVs (roadmap 31), which blocks windows, lightmaps and trim sheets together.

## Repo state at pause

All four repos clean and pushed: `gabagool_factory`, `level_factory`, `lot`,
`deli_counter`. `level_factory` at 497 passed / 11 skipped; `lot` at 329 passed.

Untracked at root and deliberately left alone: `patch_slab_inset.py`,
`patch_wall_cap.py`, `scripts/lux_dress.ps1`, `tools/check_coplanar.py`,
`migrations/2026-08/patch_roadmap_props.py`. `check_coplanar.py` looks like a
real instrument that wants tracking.

`factory.manifest.json` is still unpinned — deli_counter's traversal gate fails
7 of 103 shells on 10 `no_path` stairs, and pinning over that would certify a
combination nobody has read.
