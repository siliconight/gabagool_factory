# 2026-08-04 — the facade, four bugs deep

Every change landed in a tool repo. Nothing was fixed at level scope.

The day started at "the dressing is in places it shouldn't be" and ended with a
facade that reads. It took four fixes, and each one only became visible once the
one above it stopped hiding it.

---

## 1. Which side of the wall — `patina/slots.py`, `paneling.py`, `framing.py`

`framing._face` and `paneling.panel_orders` both took module-local **+Y** as
outward. `rot_y` rotates it: +Y swings to −X at 90° and +X at 270°, so every
east and west wall was dressed on its inside. `facing` cannot rescue it — DC
emits slots per ROOM, so for a perimeter wall `facing` points INTO the building.

Fixed by deriving outward from the building's bbox centre (`footprint_center`,
`outward_sign`). A midpoint, not a mean: a densely partitioned wing would drag a
mean into itself.

    inward covers   416 of 1331  ->  0

Limit stated in the docstring: exact for a convex footprint, can be wrong at an
L's inner corner. The honest fix for that is a footprint polygon DC does not
ship.

## 2. The authored aperture — `zoo/core/arch.py`, `kit.py`, `dna.py`, `deli_counter/themed_tscn.py`

`fit.openings` — the real aperture DC writes on every doorway/window/breach
slot — was read by nobody. `arch.void_for` derived the hole from genome
FRACTIONS of the module height instead:

    slot asks          Zoo cut            error
    1.20 x 2.20 @0.00  0.96 x 3.48 @0.00  +1.28 m tall
    1.50 x 2.20 @0.00  1.26 x 3.60 @0.00  +1.40 m tall   (breach)
    3.00 x 1.40 @0.80  2.76 x 1.67 @1.29  +0.27 m, +0.49 m up

A 1.2 m door was a slit running floor to ceiling. That is the "weird window
shapes". Measured on the shipped GLBs after the fix: Header y 0.350..1.850, hole
2.200 m; window 1.400 @ 0.800. Outer bbox unchanged at ±0.600 × ±1.850.

Width stays jamb-clamped at 12 cm a side ON PURPOSE — DC authors the module
exactly as wide as its aperture, and with no jamb nothing in `slab_parts` spans
the module's full height, so fit-to-exact-dims stops passing by construction.

**`_o<hash>` added to both `module_stem` mirrors.** `doorway_rockay_01_w140`
named two different holes; a 2.2 m door and a 2.4 m door resolved to one file.
Third time this collision has been paid for (`_d` for plate depth, `_v` for
stairwells) so it went in before it bit. Both test files pin the same literal
hashes — `97cfbf`, `ba672d`, `150910` — so neither repo can drift alone.

## 3. Relief instead of covers — `zoo/core/arch.py`, `recipes/_arch.py`, `level_factory/adapters/patina/__init__.py`

The rule is "no dressing in walkable space". It was being enforced by AIMING
proud covers, and it cannot be. A module's collider is built from the same slab
as its visual, so the collision volume ends exactly at the wall face, and a
cover standing 1.2 cm–5 cm proud is by construction geometry outside the
collider that a body walks through.

Pointing them in put 546 panel fields in rooms. Pointing them out put the same
546 into the gaps between buildings, which Lot makes into routes. **There is no
third direction.**

`arch.relief_parts` carves instead: plinth, piers and cap at full depth, fields
between them pulled back 5 cm ON BOTH FACES. Consequences, all deliberate:

* outer bbox still exactly `(w, d, h)` — the plinth alone guarantees it;
* collision comes from `slab_parts`, not the relief, so the collider is
  bit-identical to every previous build;
* symmetric because the module must not know which face is the street — it is
  instanced at slots of every orientation, and a one-sided carve is bug 1 baked
  into the mesh where no per-slot transform can flip it.

`wall` species only. A `wallEnd` is a unit box DC scales per slot; openings
already articulate themselves.

Adapter `0.2.0 -> 0.3.0`, dropping `--panel-fields` and `--pilasters`. The bump
is load-bearing: the flags an adapter passes are not otherwise in the
fingerprint. `--gutters` stays — a roofline object at 7.6 m clears the 1.8 m a
body occupies. `panel_orders`/`pilaster_orders` are kept in Patina for a greybox
build, like `--frames`.

## 4. Which AXIS — `patina/slots.py::wall_frame`

The one that had been under all three. DC writes **two dims conventions** into
one manifest, and its own composer says so:

> each module is oriented by FITTING its footprint to the greybox slot's extent
> instead of trusting the slot's raw rot_y — walls (world-oriented by deli) fit
> at 0 deg, canonical openings at 90/270
> — `themed_tscn.write_themed_tscn`

    ext_1_N_seg0   rot   0   dims (2.00, 0.35, 3.70)    run, thickness
    ext_1_W_seg0   rot 270   dims (0.35, 2.00, 3.70)    thickness, run

Patina applied `rot_y` to everything, so every E/W wall was rotated twice — run
0.35 m, thickness 2.0 m. **124 of 299 wall slots.** What shipped was 35 cm
gutter stubs every 2 m, floating 1.0 m off the facade (`d/2` of a two-metre
"thickness").

    before   ext_1_W_seg0   pos [-23.000, -15.0, 7.62]   len 0.35
    after    ext_1_W_seg0   pos [-22.175, -15.0, 7.62]   len 2.00
             ext_1_W_seg7   pos [-22.175,  -1.4, 7.62]   len 1.20   (remainder)
             ext_1_N_seg0   pos [-21.000, 16.175, 7.62]  len 2.00   (unchanged)

The discriminator is derived, not tabled: a wall is long on one horizontal axis
and thin on the other, and the canonical order is (run, thickness), so dims
listing the thin axis first can only be dims already rotated. No greybox GLB
needed. `wall_frame` returns `(run, thickness, along, outward)` and placement is
one line — it replaced nine call sites that each did their own trigonometry.

74 gutters, 4 wall lines, abutting at every seam, 5 breaks = the 5 top-storey
openings.

---

## A zero that was never real

`openings._story_wall_depth` took a MAXIMUM of `dims[1]` over a storey. One
world-oriented east wall reported the building's walls as **2.0 m** thick, so
`room_boxes` inset every room by 1.0 m instead of 0.175 and could not have seen
a cover standing in one. The "0 room intrusions" quoted twice on 08-03 and twice
again today was measuring nothing. Now uses `slots.wall_thickness`.

**The lesson, again:** a check that reports clean because its inputs are wrong
is worse than no check. This is the same failure as the `parsed BOTH` navmesh
bake (carves around dressing, so the zero is circular) and `walk_themed` without
`--godot` (measures an empty scene).

## The bridge served stale files six times

Device says 124,765 bytes; two consecutive stagings returned 1,106,040 bytes of
an older build. The `CLAUDE.md` byte-count rule caught it every time and the
analysis was thrown away rather than published. `paneling.py`, `test_paneling.py`
and four Zoo files did the same earlier. **Check the count before reading.**

---

## Open

* `lux_apply` still cache-hits — the path-blindness `lot` had. The shipped lit
  scene is stale; `walk_themed` masks it by carrying the preset itself.
* Lot's walk scene ships an unbaked `NavigationMesh`, and Godot warns
  `cell_height 0.15` against a map at `0.25`. Any nav measurement in that
  project is on shaky ground.
* `zoo_kit_build` does not sweep its output — 33 opening GLBs on disk, 15 live.
* Relief variation is plumbed (`style_block["relief"]` -> `plan.params.relief`)
  and **not authored**. Every wall in every building uses one rhythm, which is
  the original complaint in a new shape.
* `upstream_artifact_hashes` populated nowhere (roadmap 39).
* `LuxFixtureSpawner` returns attempts, not results — belongs upstream in Lux.
* `wear_colors` clamps away the above-white half of the ambient tint.
* `gather_facts` never runs on the dressing path.
* `tools/dressing_in_nav.py`/`.gd` still uncommitted; `--backing` still not
  trusted. Its site-level premise was right and is now quoted in three
  docstrings.
* DC's 10 pre-existing test failures (confirmed unrelated by stashing).
* The `objective` shot measured 36.3 before and after fixture lights — nothing
  reaches it.

## Next, by the user's direction

The geometry lever is spent. What is left is content: posters, per-building
accoutrement, Pixelcoat value variation BETWEEN surfaces (not weird colours),
and authoring per-style relief so one building does not have one rhythm.
