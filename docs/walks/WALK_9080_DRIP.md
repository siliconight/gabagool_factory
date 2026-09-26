# Walk: cold run 9080's package, with the drip staged

`_runs/walk_9080_drip` — `LF_club_block_014.portable-godot` from
`workspaces/cold-9080-ws`, plus `walk_export.py --drip`. Walked 2026-09-26.

**None of these were found by an instrument.** That package's validation record
carries 56 findings and not one of them is below. Every item here was found by
a person looking at the screen, which is roadmap item 18 stated as evidence
rather than as a worry.

Coordinates are the debug overlay's `pos`, which is why the overlay exists.

---

## 1. Puddles read as generated — identical, evenly spaced

`pos x 23.4 y 1.7 z 37.4`, street outside the club.

Walker: "too many puddles and they all look like identical circles placed all
equally away from each other so it looks computer generated, and less natural".

Suspected mine, 2026-09-26: `pixelcoat.core.weathering.pooling_mask` bakes a
pooling pattern into the ground skin's TEXTURE, and Lot tiles that texture at
the pack's `meters_per_tile`. A per-tile pattern repeated on a grid is
identical circles at a fixed pitch by construction. Not yet confirmed — the
pitch has to be measured against `meters_per_tile` before this is stated.

## 2. Windows missing from the exterior

Same frame as 1. The building reads as a flat dark box.

Counted, not confirmed as a regression: 9078's package carries 8 `window_*.glb`
and 10 distinct window node names; 9080's carries **10 and 12**. The modules
did not disappear between the two runs, so if they are missing on screen the
cause is placement, lighting or the wet skin, not a missing kit. Open.

## 3. Unexpected hole in the floor

`pos x -13.1 y 4.9 z -1.1`, `bldg GreyboxBase deli_a01`, crosshair on
`slab_col_1` at 3.76 m, `y 3.02`.

Standing on the greybox base, looking down into a tiled room with a table in
it. A body can fall in.

## 4. Desks inside the stairs' clearance

`pos x 8.4 y 4.9 z 10.0`, `bldg ext_0_N_seg4 zoo`.

Two dressing props at the head of a flight: a large counter/desk squarely in
the path, and a second box apparently hanging over the stair void. A third prop
is visible floating clear of any floor at the left of frame.

## 5. A counter on the ceiling

`pos x 6.5 y 1.6 z 16.8`, `bldg counter_island_upper_hall_2 zoo`, crosshair on
`Counter` at 2.33 m, `y 3.30`.

Standing on the ground floor, looking up: a counter belonging to the UPPER hall
sits at y 3.30 — above the ground storey's ceiling line and below the upper
floor the player stands on at y 4.9 in finding 4.

---

## What the measurements said

### The unifying hypothesis was wrong, and here is what killed it

"A storey's floor slab is missing" predicted a room with a ceiling and no
floor. Read off `lot/deli_a01/site.tscn`: **every one of the 14 rooms has both**,
at four storey levels (-3.29 / 0.01 / 3.31 and ceilings at -0.31 / 2.99 / 6.29).
The four storey-1 slabs tile the footprint exactly -- `manager_office`
x[-19,-2] z[-2,14], `apartment_hideout` x[-2,19] z[-2,14], `server_room`
x[-2,19] z[-14,-2], `upper_hall` x[-19,-2] z[-14,-2] -- covering x[-19,19]
z[-14,14] with no gap. Withdrawn.

### And the first measurement was taken in the wrong frame

The overlay's `pos` was read as a position in the building's own coordinates.
It is not, twice over:

* **It is the EYE, not the feet.** `_walk.tscn` puts the camera at +1.6 on the
  player. Every `y` the walker quotes is 1.6 above the floor they are standing
  on -- `y 4.9` is the storey-1 floor at 3.31, not a fifth storey.
* **It is WORLD space, and the buildings are rotated.** `site.tscn` instances
  `deli_a01` as `b1` with a 180-degree Y rotation at origin (-5, 0, 5), so
  `local_x = -(world_x + 5)` and `local_z = 5 - world_z`. A first pass measured
  prop clearances against a ladder using world coordinates read straight into
  the building's scene and found nothing, which was a true answer to a question
  nobody asked.

Both are the shape this repo keeps paying for -- state the frame and the units
-- and both were caught before anything was patched, which is the only part
worth anything.

## 1, measured: the puddles repeat every 3.00 m because the mask is in a tile

`site.tscn`'s ground materials carry `uv1_scale = Vector3(0.333333, ...)` with
world triplanar on, so the ground skin repeats at **3.00 m**. The package ships
`skins/asphalt_delco_wet_albedo.png` and its wet roughness, so the wet chain is
live and the pooling is coming from the baked mask.

**A puddle baked into a 3 m tile is a grid of identical puddles by
construction.** No tuning of coverage, feather or span fixes that: the feature
being drawn is larger than the period it is drawn in. `pooling_mask` was built
at tile scale, and a puddle is a site-scale feature -- it belongs where
something knows the site's low points, not in a texture that repeats twice per
car length. This is a design error in the 2026-09-26 pooling work, not a
parameter.

Three ways out, and the cheap one is not obviously the worst:

* drop pooling from the tiled skin and keep only sub-tile dampness variation
  with no recognisable blob, then place real puddles as site-scale geometry
  where Lot already knows the grade;
* the same, but with the puddles as a second non-repeating mask over the site's
  extent -- one more texture fetch on the ground, which is the largest surface
  in any street frame and therefore the most expensive place to add one. It
  would have to be priced before it ships;
* leave it, and accept a 3 m grid.

## 3, 4 and 5, measured: dressing stands over the stairwell void

The stairwell occupies `floor_stairwell` at local x[-19,-8] z[-14,-6]. **Five
storey-1 dressing props stand inside that footprint**, at the storey-1 floor
plane:

    counter_island_upper_hall_0   (-10.42, 3.83,  -6.58)  2.20 x 0.80 x 1.05
    counter_island_upper_hall_2   (-11.65, 3.83, -11.21)  2.20 x 0.80 x 1.05
    planter_box_upper_hall_1      (-14.71, 3.75, -12.13)  0.70 x 1.40 x 0.90
    chair_waiting_rb0f5945e_2     (-18.52, 3.75,  -8.30)  1.80 x 0.60 x 0.90
    vending_rb0f5945e_3           (-18.44, 4.21, -11.74)  0.85 x 0.75 x 1.83

`counter_island_upper_hall_2` is the one in finding 5: its base sits at y 3.305
and the walker, standing in the stairwell on the ground floor at local
(-11.50, -11.80), photographed it at 2.33 m with the crosshair reading
`y 3.30`. The floor SLAB rect covers that area, so the opening the walker is
looking through is cut into the slab mesh rather than absent from the scene --
which is why the rect arithmetic above says "floor present" and the screen says
"hole". **The placer is subtracting the stair opening from neither the floor it
places on nor the clearance around it.**

Finding 4's walker position maps to local (-13.40, -5.00) on the storey-1
floor, one metre north of the stairwell edge at z = -6 -- the head of the
flight, with `stair_guard_back_12` and `stair_guard_side_5` 2.3-2.8 m away.
That is the same defect seen from above rather than below.

Finding 3 is NOT this. Local (8.10, 6.10) is in `apartment_hideout`, nowhere
near the stairwell, and its neighbours are ordinary ground-floor props. It
needs the floor mesh itself read -- an opening cut into a slab does not show up
in the slab's bounding rect, which is exactly the limitation this section just
ran into. Open.

## 2, narrowed: the window kit is present

9078 ships 8 `window_*.glb` and 10 distinct window node names; 9080 ships 10
and 12. Nothing was lost between the runs, so a window missing on screen is
placement, lighting or the wet skin -- not an absent kit. Open, and the cheapest
next step is a shot from the walker's own position rather than more counting.

## The hypothesis worth testing first


3, 4 and 5 may be one defect rather than three: **dressing placed against a
storey height that is not where that storey's floor slab is.** A prop half a
metre below its floor pokes through the ceiling of the room beneath (5); a prop
placed over a stair void has no floor under it at all (4); and a floor opening
nothing accounted for is a hole to fall into (3).

That is a guess. It is written down so the measurement that refutes it stays
attached to it — and per this repo's own rule, every item in the list above
gets attributed before any patch is written, because fixing the obvious one and
leaving two behind is how a sweep looks like it did not work.


---

## 2, CLOSED: the windows are there, they are just very dark

`pos x 6.3 y 4.9 z -7.2`, crosshair on `ext_col_1_S_open0_pane` at 1.80 m.

The kit was never missing and neither was the placement. The panes are dark
enough that at street distance the facade reads as an unbroken box, which is
what "the windows are gone" was describing. That is a lighting and glass
decision, not a defect in the build. Closed as reported; whether the glass
should read lighter is the walker's call.

## 6. It is raining indoors

`pos x 8.8 y 1.6 z 18.4` -> deli local (-13.80, -13.40), inside
`floor_stairwell` -- `crate_stack_stairwell_0`, a brick crate under a roof,
carrying drips.

MINE, 2026-09-26, and it is the defect `RAIN_WETNESS.md` item 4 names:
"interiors stay dry ... NOT measured by item 2's probe, and the probe cannot
answer it".

**The cause is the attachment being per MATERIAL.** `rain_drip.gd` walks the
scene and attaches to every material whose name matches a wall family.
`M_Skin_brick_delco_1997` is worn by the exterior walls AND by that crate AND
by the window reveals, and it is ONE resource shared by all of them -- 19 of
them across the package, one per imported GLB, which is the same fact that made
the +1.85 ms figure a figure about brick. A shared material cannot be wet on
one instance and dry on another.

The obvious fix is the wrong one. Attaching per instance means a
`surface_material_override` per mesh, which is one material per instance --
exactly the defect measured on this package the same morning (284 colour-only
materials, `PRESENTATION_TINT_MATERIALS`). Trading a weather bug for a
draw-call bug is not a fix.

The place this resolves is BUILD time, where `ext_*` and `int_*` are already
different meshes: the exterior families get one wet variant material each --
one extra material per family, not per instance -- and interiors keep the dry
one. That is the attachment the drip work has been deferring, and this finding
is the reason it cannot be deferred further.

## 7. Drips on the window reveal and sill

Same frame as 2. The sill and the inner reveal of the opening carry drips,
and both are sheltered by the head above them.

Same root cause as 6 -- they are brick, and brick is one material. The shader's
up-vector term keeps rain off a face that points down; nothing in it knows
whether there is a roof, a soffit or a window head ABOVE a face that points
out. A per-fragment test cannot answer that; a build-time one can, because the
builder knows which module is a reveal.

## 8. The drips are hard to see at all

Walker: "found some drops, they are really hard to find. need the right
lighting".

Correct, and expected from the fragment: `ALBEDO` is black, `ALPHA` is
`wet * 0.30`, and the visible part is a normal-map perturbation plus a
roughness cut. That needs a specular highlight to disturb, so in an unlit
interior or under overcast there is nothing for it to modulate.

**Tuning this costs nothing to run.** `NORMAL_MAP_DEPTH`, `ALPHA`, `drip_scale`
and `drip_speed` are uniforms and constants in the same instruction stream --
changing them does not change the +1.85 ms, so the look can be pushed without
re-pricing. What WOULD need re-pricing is any change that adds a texture fetch,
a branch with real work in it, or a screen read.
