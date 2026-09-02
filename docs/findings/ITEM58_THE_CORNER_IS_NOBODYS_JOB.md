# Item 58 — the corner is nobody's job, and it is nobody's job everywhere

Measured 2026-08-24 against the `lot_demo_001` walk preview
(`.level_factory/preview/lot_demo_001_walk`, composed `site.tscn` written
2026-08-24, i.e. the census-#8 rebuild) and against Deli Counter's own
`build/<id>.slots.json` for the same five buildings. Read-only: no Godot, no
Blender, no rebuild. Two parsers, two independent sides of the same wall.

---

## The headline

**Every exterior wall run terminates exactly on the perpendicular wall's
centreline — 0.000 m past it — and neither run owns the outer quadrant of the
corner. 40 of 40 corners, 5 buildings, every storey, one distinct value.**

That leaves a re-entrant vertical notch **0.150 m × 0.150 m, full storey
height, at every outside corner of every building**, open on two faces and
open to the sky.

    corners tested                          40   (5 buildings x every storey x 4)
    distinct "reach past centreline" values [0.0]
    distinct wall thicknesses               [0.3]
    distinct notch sizes                    [0.15] m
    corners with a notch                    40 of 40

Uniform to machine precision on both instruments. This is a **rule**, not
drift.

## Candidate mechanisms, adjudicated

The item listed three "in likely order". The measurement keeps the first and
kills the other two.

| # | mechanism | verdict |
|---|-----------|---------|
| 1 | the corner junction is nobody's job; `wallEnd` fills straight-run remainders and no corner family owns the turn | **CONFIRMED** — every run stops on the perpendicular centreline and nothing is placed beyond it |
| 2 | a themed module narrower than its greybox slot after the name-boundary strip | **REFUTED** — runs are internally contiguous to 1e-6 and land on exact integers (±17.000, ±26.000, ±18.000). Nothing was stripped, and the slot spec has the same corner |
| 3 | seg-boundary rounding between adjacent wall slots | **REFUTED** — rounding does not produce one distinct value 40 times. The reach past the centreline is `0.0` exactly, everywhere |

**And it is authored upstream, not introduced at assembly.** The slot spec
already places the N/S runs from `-17.000` to `+17.000` while the E/W walls'
centreline is `∓17.000`. The composed scene realizes what it was handed
faithfully. Zoo and Lot are acquitted; the corner is missing from the
*request*.

## The roof agrees, by the same rule

`mansion_a02`'s `roof_rockay_01_w3400_d2400` is centred at the origin, so it
spans `x ∈ [-17, 17]`, `z ∈ [-12, 12]` — the wall **centrelines**, not the
outer faces. `arena_a03`'s `roof_..._w5200_d3200` does the same at ±26 / ±16.
So the outer 0.15 m of the entire wall ring is uncapped, and the corner notch
is open to the sky above it as well as to the outside. Independent
corroboration of the same centreline convention from a different species.

## The instrumentation gap the item flagged, quantified

`ext_0_N_seg9` **exists in all five buildings**. The overlay's `bldg` line
resolves the nearest instanced ancestor, which for a themed module is the
module itself, so the name it printed selects nothing. Resolved by world
transform instead:

    b0  mansion_a02          world ( -75.000, 1.746,  65.300)   24.08 m from the walk position
    b1  pvp_station_ref      world (   4.000, 1.646,  54.000)   74.78 m
    b2  large_warehouse_a01  world (  48.000, 2.846,  87.000)  111.41 m
    b3  arena_a03            world (  41.000, 2.846,   2.375)  134.02 m
    b4  strip_club_a03       world (  65.000, 1.646, -60.000)  194.73 m

Only `mansion_a02` is a candidate. **Fix the overlay to print the building
while in there** — one line, and it is the difference between a finding that
can be reopened and one that cannot.

## What is NOT claimed

- **Not a through-breach into the interior.** The notch is an L-shaped pocket
  cut out of the corner: the inner quadrant is covered by *both* runs. A
  straight ray from outside still meets wall. The item's "sightline and light
  leak through a wall the gameplay layer treats as solid" is **not supported**
  by the plan geometry; "a gap wide enough that sky/backlight shines through
  the corner from outside" **is**. The tactical-cover consequence should be
  restated or dropped.
- **Not proven to be the photographed object.** The crosshair read 21.63 m
  from `(-63.4, 1.6, 86.4)`. That ray meets mansion's N run at local
  `x ≈ -1.2`, which is `ext_0_N_seg8`'s span, ~19 m from the nearest corner;
  `seg9` sits at 23.2–24.1 m. Either the overlay's two numbers disagree, or
  the walker moved between reading and shot. The corner defect is real and
  universal regardless, but **the founding sighting is still not tied to it.**
- **GLB bounds were never read.** The device bridge refuses paths 9 folders
  deep (limit 7), so `art/zoo/*.glb` could not be staged. Thickness 0.30 m
  comes from the slot spec's `fit.dims`, which is authoritative for what was
  *asked*; the built meshes were not independently measured.
- **The slot-side run-continuity count is not settled.** 30 residual gaps
  remain on E/W runs in slot space, all of them at openings. Given the two
  ruler failures below, these are far more likely the ruler than the wall —
  but they are unresolved and should not be quoted as findings.

## The ruler, twice — and what it costs the gate

Two wrong readings were produced and corrected on the way here. Both have the
same shape: **a dimension read by ROLE when it is stored by AXIS.**

1. The filename token `_w<cm>` is the module's **X extent**. On an N/S run
   that is the run width (`wall_rockay_03_w200` = 2.00 m). On an E/W run the
   same token is the **thickness** (`wall_rockay_01_w30` = 0.30 m) and the
   2.00 m length lives on Z, where no filename records it.
2. `fit.dims` in the slot spec is `[x, y, z]`, not
   `[width, thickness, height]` — so the run width is `dims[0]` on N/S and
   `dims[1]` on E/W.

Either mistake prints a comb of **1.700 m** gaps (= 2.000 − 0.300) on every
E/W run and nothing on N/S. The first pass reported **222 gaps** and every one
was that number or half of it. That signature — one value, repeated, equal to
pitch minus thickness — is the tell.

**This is the constraint on the gate item 58 asks for.** An
envelope-continuity check **cannot derive module width from the filename**,
because the name records an axis extent whose meaning depends on the run's
orientation. It must read the GLB bounds (`module_extents.py` already has the
tested reader, basis included) or the slot spec's dims *with the axis
resolved from the run*. A gate that parses stems would pass the corner and
fail 222 sound joints — the exact inversion this file's first pass produced.

## Who owns the fix — decided 2026-08-24

**Deli Counter owns the corner.** A corner is part of a building, so it is a
slot, and slots are Deli Counter's; Zoo may author a better-looking corner
afterwards, into the slot DC declares. What DC must own is the COLLISION
piece and the modular economy around it. (If a corner ever turns out not to
be part of a building, that is a reason to rethink the routing, not to move
this slot.)

**Tier one costs no new geometry.** `_record_wall_slot` in `deli_counter.py`
already carries the mechanism: a `wallEnd` "is authored as a UNIT box and the
size rides as a per-slot scale: one module fits every remainder", verified
in-engine as unit box × `fit.dims` reproducing the baked shell 1:1. A corner
post is that same unit box at scale `[t, t, storey_h]` — zero new GLBs, more
instances of a species every kit already carries. That is the VRAM argument
in one line: one mesh, N instances, not N meshes.

**The geometry.** Pull each run end back by half the wall thickness, from the
perpendicular centreline to its inner face, and seat a `t × t` post at the
intersection. No overlap, envelope closed, footprint unchanged. The `wallEnd`
remainder already absorbs an arbitrary end width, so only the span
computation moves.

**Tier two is Zoo's, and Zoo already built it.** `wallCorner` — recipe plus
full genome entry, `rockay` included, dated 2026-07-14 — is a complete
L-shaped corner whose docstring is written against this exact defect: *"the
corner drops onto the meeting point of two DC wall runs with no offset
math."* Nothing has ever asked for one. Filed as roadmap item 64, with three
measured preconditions: the genome's 2.0–4.5 m height range excludes 252 of
the 988 corners; `wallCorner` is exact-fit and in neither `PLATE_ROLES` nor
`VOLUME_ROLES`, so `wallCorner_rockay_01_w30` would have to be 14 distinct
solids; and `known_species` is never passed to `plan_kit`, so the report that
would have said any of this is unarmed.

**Why the tiers split where they do, geometrically.** Scaling an L's leg
length scales its thickness with it, so `wallCorner` is structurally
exact-fit — 18 modules per theme+style. A `t × t` post is a cube, and a
scaled cube is still a cube, which is the only reason tier one can be one
unit module for the entire library.

This is item 62's gap protocol rather than a bug fix:

1. **Name the gap:** the slot vocabulary has `wall`, `wallEnd`, `doorway`,
   `window`, `breach` and no **corner**. `wallEnd` is a scaled remainder
   filler for a straight run; nothing turns.
2. **Owner:** `deli_counter` for the slot (it must ask for a corner), `zoo`
   for the species (`Corner_90_Outside` / `Inside`, item 57's "corner module
   family").
3. **Grow it in the owner's grammar,** versioned and tested — not by nudging
   run ends 0.15 m outward in one workspace.
4. **Re-run,** and every building on every future site closes its corners.

The cheap alternative — extend each N/S run by half the wall thickness so it
laps the perpendicular wall's outer face — closes the notch with no new
species, but it makes the lap arbitrary (which run wins is then a coin flip)
and it does not give item 57 the corner vocabulary it is asking for. Worth
pricing, not worth choosing by default.

## Library census, 2026-08-24 -- run by the gate this item asked for

`tools/envelope_continuity.py --dir deli_counter/build`, over all 137 slot
manifests:

    124 buildings read, 0 with no finding
    ENV_CORNER_OPEN          988
    ENV_DIMS_AXIS_SWAP       349
    ENV_RUN_GAP                1
    ENV_PLACEMENT_DRIFT        0
    REFUSED                   13   (1-5 slots each, no `wall` field -- stubs,
                                    not buildings; refused, NOT counted clean)

The notch tracks the wall thickness and nothing else -- 0.150 m on the 0.30 m
walls (812 corners), 0.175 on the 0.35 walls (152), 0.125 on the 0.25 walls
(24). Half the thickness, every time, at three different thicknesses. A
tolerance or a rounding cannot produce that; a missing module family can.

`ENV_PLACEMENT_DRIFT 0` is measured with the composed scenes joined on
`slot_id == node name` for the five `lot_demo_001` buildings: every module
sits exactly where its slot asks. The scene realizes the request; the request
is what has no corner.

**The one real run gap in 124 buildings** is `auto_shop_a02`, storey 0 N,
0.050 m between `ext_0_N_open0` and `ext_0_N_seg3`. One authoring step wide,
and the only one in the library -- filed here rather than folded into the
corner finding, because a remainder that was not filled and a corner that was
never anybody's job are different defects that look alike from a screenshot.

**The 349 frame differences** became roadmap item 63 -- filed as "openings
are transposed" and REFRAMED the same day. Neither frame is wrong: wall
segments are written in building space and placed unrotated, openings are
written canonical-X and rotated onto their wall, and both land correctly.
Reading `zoo_keeper/core/kit.py` (which documents `fit.dims` as `[w, d, h]`
and reads it positionally) and then the composed scene's node bases refuted
the first reading in about ten minutes. The real defect is that nothing in a
slot declares which frame it is in -- and, underneath it, that `rot_y` is
honoured for 8 of 698 exterior modules and inert for the other 690.

## Fixed and verified, 2026-08-25

Deli Counter 0.102.0 + 0.102.1, rebuilt through Blender 5.1.1 across the whole
library and re-measured:

    124 buildings read, 4 with no finding
    ENV_CORNER_OPEN            0     (was 988)
    ENV_RUN_GAP                1     (pre-existing auto_shop_a02)
    ENV_DIMS_FRAME_CANONICAL 349     (item 63, untouched by this)
    ENV_PLACEMENT_DRIFT        0
    ENV_SHAPE_UNRECOGNISED     0
    REFUSED                   13

Every figure landed on the number predicted before the rebuild.

**The change, in two expressions and four slots.** `_emit_wall_run` gained
`inset` and `corners`, both defaulted off — it has two callers and only
`_exterior` asks for either, so interior partitions are untouched by
construction. The inset pulls solid spans back to the perpendicular wall's
inner face; openings do not move, because they are placed in `_exterior` as a
fraction of the full run and arrive already positioned. `corners=(axis == 0)`
gives the turn to N/S, so the two runs meeting there cannot both fill it.

**Zero new modules in any kit.** The post is `size_mod="end"` → `wallEnd` →
the unit box DC scales → Zoo's `exact = typ != "wallEnd"` gives it unit
treatment with no change in that repo. An exact-fit corner would have been 18
modules per theme per style.

## The gate caught the regression its own change introduced

This is the part worth keeping. The corner fix alone took `ENV_RUN_GAP` 1 → 2:
one new 0.050 m hole beside a window in `strip_retail_a01`. Instrumenting the
builder found `_wall_span` computing a span's remainder **twice**, by two
algebraically identical expressions that are not identical in floating point:

    ext_1_N_seg6  a=-9.85 b=2.2 L=12.05 M=2.0 n=6
                  L - n*M = 0.05000000000000071   -> too big to absorb
                  b - x   = 0.04999999999999982   -> too small to emit
                  hole    = 0.04999999999999982

    ext_1_N_seg9  a=3.8  b=9.85 L=6.05 n=3        (control, same run)
                  L - n*M = 0.04999999999999982   -> absorbed, no hole

A threshold asked of two spellings of one number has a blind window either
side of it. 0.102.1 computes it once.

**And the mechanism was refuted before it was confirmed.** It was hypothesised,
tested against a reconstruction built from the manifest, and discarded —
because the reconstruction assumed the span began after the previous module
(`a=0.15`) when it actually begins at the run's inset edge (`a=-9.85`) and
covers six modules. The manifest's four-decimal rounding could not have
settled it either way; only the builder knew its own inputs. The probe was
worth the round trip, and reasoning about floats from rounded artifacts was
not.

## What would close item 58

- [x] locate the joint in the composed scene → located, and it is not one joint but 40
- [x] measure the gap against the slots on both sides → 0.150 × 0.150 m, and the slots already carry it
- [x] give corners an owner → decided: Deli Counter, as a `wallEnd` unit post; Zoo's `wallCorner` is tier two (item 64)
- [x] the envelope-continuity gate → `tools/envelope_continuity.py`, dims by axis, `--selftest` fails on a name-parsing ruler
- [x] the corner defect itself → DC 0.102.0/0.102.1, 988 → 0 verified on rebuilt geometry
- [x] wire the gate into a job, and graduate it to blocking → `tools/check_all.py`, `envelope` check; `ENV_CORNER_OPEN` graduated WARN → FAIL on 2026-08-25 by item 59's rule (a code graduates when the library reads zero, never before)
- [ ] tie the founding sighting to this, or record that it was not tied
- [ ] cut a `factory-v` entry: DC moved 0.101.2 → 0.102.1 and the certified set has not been re-cut

## Reproducing

    workspaces/lot-demo-ws/.level_factory/preview/lot_demo_001_walk/site.tscn
    workspaces/lot-demo-ws/.level_factory/preview/lot_demo_001_walk/lot/*/site.tscn
    deli_counter/build/{mansion_a02,pvp_station_ref,large_warehouse_a01,arena_a03,strip_club_a03}.slots.json

Corner test: for each storey, take each run's span along its own axis and the
perpendicular run's centreline offset; the run reaches `|end| - |centreline|`
past it, and `thickness/2` minus that is the uncovered notch.
