# Surface Dressing — the contract

Layer 3 of the environment detail stack: collisionless instanced geometry
scattered across an ASSEMBLED SITE to add relief, silhouette breakup, parallax
and contact, without changing how the level plays.

Source: `Surface_Dressing_Level_Depth_Guide`. Roadmap item 45. This file is the
part of that guide this pipeline can *enforce* — the guide is art direction,
and everything below is either a number, a schema, or a gate.

## 1. What this is NOT

**It is not the pass that runs today.** `patina_dressing` produces
`<building>.patina.dressing.json`, schema `patina-dressing/1`, and it is:

    source      arena_a03.patina.glb        ONE BUILDING, before assembly
    anchors     roofline, slot_id, trim_piece
    families    gutter_run 83, edge_strip 64, curb 56, base_course 52,
                conduit_run 5
    note        "non-collision cover build orders for Zoo"

That is **Layer 2 — mid-frequency dressing bolted onto a building Deli Counter
made**. It has no concept of a site. It is correct and it stays.

Surface Dressing is **Layer 3, post-lock, site-level**: it runs after Lot has
assembled the mission and the shell is trusted, and it dresses the *ground and
the seams of the whole place*, not the façades of one building.

## 2. Where it sits

```
Deli Counter graybox -> structural/nav validation -> Lot site assembly
  -> Laser Tag evaluation -> human selection -> FUNCTIONAL SHELL LOCK
  -> Pixelcoat surface treatment
  -> Zoo dressing kit build          (Layer 3 species — DO NOT EXIST YET)
  -> Patina Surface Dressing manifest + placement
  -> Presentation Compose -> Lux -> gameplay regression -> Dispatch
```

Post-lock is not a preference. Before the lock the shell can still move, and a
dressing pass planned against a shell that then moves is planned against
nothing.

## 3. THE HONESTY RULE, and it is a measured number

The guide says: *"No decorative asset creates a believable but false traversal
promise."* That is the rule everything here exists to keep, and it was a
judgement call until `lot/site_steps.py` supplied the number.

A capsule does not meet a low step the way a box does. Contact lands on the
bottom hemisphere, so for capsule radius R meeting a step of height h the
contact normal's vertical component is `(R − h) / R`, and the tallest step a
body can walk up with **no step-up assistance at all** is

    unassisted_step_max = R · (1 − cos(floor_max_angle))

For Godot's default 45° floor angle and this stack's 0.4 m player capsule that
is **0.117 m**. Above it the engine classifies the contact as a WALL and the
capsule stops dead.

`agent_contract.json` states `max_step_up_m: 0.5` as though the body were a
box. That is what a controller can *lift itself over*, not what it can walk
over, and it is the wrong number for this.

**The rule:**

> Collisionless dressing may stand in traversed space **only** where its height
> is at or below `unassisted_step_max`. Below that a body would step over the
> object in reality, so passing through it is not a visible lie. Above it a body
> would have to climb — and walking through instead is exactly the false promise.

Applied to the guide's own height bands:

```
band     height        in traversed space
micro    2–10 cm       intangible is HONEST — unconditionally allowed
low      10–30 cm      SPLITS at 0.117 m. Allowed below it, refused above.
medium   30–70 cm      refused. Give it collision (then it is Layer 2) or
                       place it where a body cannot go.
tall     70–150 cm     refused, same reasons, more visibly.
```

This is not a new principle. Patina 0.3.0 stopped emitting `--panel-fields`
and `--pilasters` for precisely this: boxes standing 1.2 cm and 5 cm proud of a
wall whose collider ends at the wall face, i.e. non-collision geometry in space
a body walks through. Its own note is worth keeping in front of us —
*"There is no aiming fix... Both sides of a wall are walkable."* The fix there
was to move articulation INTO the authored depth (`arch.relief_parts`). The
equivalent here is the height band.

## 4. Where dressing may not go

Exclusions are keyed to what the gameplay layer **already declares**, not to a
new hand-maintained list. If it is not already declared by Deli Counter or Lot,
it is not an exclusion this pass can honour.

```
exclusion tag     declared by                     why
path              Lot routes / crew path          traversal readability
spawn             Lot spawns                      the first second of play
objective         Deli Counter objective anchors  the thing you came for
interactable      Deli Counter interactives       must stay findable
door              Zoo openings (keep_out already
                  counts 19 on arena_a03)         thresholds stay clean
cover_edge        Lot cover plan                  cover silhouette is language
readability       Laser Tag sightlines            the pre-art baseline
```

## 5. The manifest — `surface-dressing/1`

Machine-readable schema: `level_factory/schemas/surface_dressing.v1.json`.

**Coordinate space is declared, not assumed.** `patina-dressing/1` carries
`"space": "spec/Blender Z-up raw coords"` and this schema keeps that convention
verbatim. Height is therefore `pos[2]`, **not** `pos[1]`. A GLB on disk is
Y-up; a manifest is Z-up; `COORDINATE_CONTRACT.md` covers only the first half
and `glb_nodes.py`'s docstring says so directly: *"do not trust one sentence to
cover both."* A height rule that reads the wrong axis is wrong in a way that
looks right.

Document header carries the derivation so an artifact can be checked without
this file:

```json
"capsule": { "radius_m": 0.4, "floor_max_angle_deg": 45,
             "unassisted_step_max_m": 0.117,
             "source": "lot/site_steps.py" }
```

Each order carries `height_m` — the **measured height of the placed instance**,
after scale — and `in_traversed_space`, computed by the planner against Lot's
walkable surfaces. Those two fields exist so the gate is one expression rather
than a re-derivation:

```
in_traversed_space AND height_m > unassisted_step_max_m AND collision_policy == "none"
    -> SURFACE_DRESSING_FALSE_TRAVERSAL_PROMISE  (blocker)
```

## 6. Gates

| gate | fails on | already exists? |
|---|---|---|
| collision unchanged from the lock | any locked collision record moving | **yes** — functional lock, 1,171 records since level_factory 0.31.0 |
| dressing declares no collision | `collision != none` on a dressing asset | **yes** — `ZOO_DRESSING_HAS_COLLISION`, blocker |
| false traversal promise | the expression in §5 | no — this contract adds it |
| navigation regression | walktest_navqa against the locked shell | yes |
| play equivalence | Laser Tag vs its pre-art baseline | yes, baseline exists |
| budgets | instance count, draw calls, VRAM, worst-case views | no |
| determinism | same seed, same manifest, byte-identical | partial — seed exists in `patina-dressing/1` |

Three of seven already exist. That is the useful thing this contract found.

## 7. What this does NOT decide

- **Art direction.** Densities, clustering behaviour, which causes get which
  detail, what a dressed street should feel like. The guide has opinions;
  this file has none.
- **The asset list.** Zoo currently ships 50 species and **none** of them is a
  Layer 3 class — no grass, weeds, pebbles, rubble, litter, leaves, sticks or
  roots. Nothing can be placed until that kit exists. This contract is written
  so the kit has something to be built against, not the other way round.
- **Budgets.** The numbers in §6 are a category with no values. They should be
  measured on a worst-case view in the runtime, not guessed here — the same
  mistake the light caps made twice on 2026-08-18.

## 8. The test

From the guide, unchanged, because it is the right one:

> If the dressing layer is hidden, the level should still play correctly. If the
> dressing layer is visible, the same level should feel materially richer.

The first half is checkable by the gates above. **The second half is not, by
anything in this repository.** On 2026-08-18 every headless check was green —
closure `ok: true`, portability `PASS`, 866 tests — while the level blinked,
went dark in rooms and had a seam across a floor, all found by a human walking
it. Surface Dressing is a *presentation* layer, so that gap is wider here than
anywhere else in the pipeline, not narrower.
