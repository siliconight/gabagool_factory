# Does an asset read? The gate that does not exist

PROPOSED, not started. The walker supplied *Original Xbox Era Asset Fidelity
Target* on 2026-09-26 and, after the triangle comparison below, said the
reading standard was "really the only thing of value from that read". This is
that standard turned into two instruments, and the evidence that they would
find something.

CLAUDE.md already names the hole:

> **"Works" and "good" are different gates, and only the first exists.** Every
> guardrail here measures traversal correctness — can a body get from A to B.
> None measures whether the result reads as designed rather than generated.

Roadmap item 18. This is a proposal for its first instrument.

## The triangle comparison, which is the wrong end of the doc

Measured 2026-09-26 against the doc's bands.

    106 Zoo species carry a triangle budget
      min 140   median 900   max 24,000

      <=500     small reusable prop          36 species
      501-1500  medium prop                  35 species
      1501-3000 prominent set-piece          16 species
      >3000     above every band in the doc  19 species

Two thirds sit inside the bands and the median species is squarely "medium
prop". The tail does not: `neon_sign` 5,000, `counter` 7,000, `desk` 8,000,
`back_bar` 8,500, `vault_door` 9,000, `cubicle_bank` 24,000 -- eight times the
doc's largest band, twelve times a Master Chief.

And per frame, against the ~130k polys per view the doc cites from Chris
Butcher (30k environment + 100k model):

    street/forecourt wide   2,120,644 tris   16.3x
    gas station front       2,098,294 tris   16.1x
    club street at night    2,061,034 tris   15.9x
    under a streetlight       939,416 tris    7.2x
    deli interior             870,044 tris    6.7x

**None of which matters much here, and that is the point.** This repo measured
on 2026-09-16 that frame time tracks draw-call submissions and barely notices
geometry: 1,730 draws read 9.49 ms and 6,376 read 25.59 ms while the primitive
count sat flat at ~1.4M throughout. The rows above say it again -- the deli
interior renders 870k triangles in 119 draws at 6.09 ms, while the club street
renders a SMALLER 2.06M in 4,078 draws at 13.45 ms. Cutting `cubicle_bank`
from 24,000 to 3,000 would change frame time by approximately nothing.

So the triangle bands are the wrong end of the document. Adopting them as a
performance budget would be measuring the cheap thing carefully.

## The right end

> Assets should read clearly at normal gameplay distance through strong
> silhouettes, purposeful shape changes, and surface detail carried mostly by
> texture, lighting, and color.
>
> **Art test:** If removing a row of polygons does not change the silhouette,
> shape read, or lighting, it probably does not need to be geometry.

That is a LOOK standard, and this toolchain has no instrument for any look
standard at all.

## It would find something on the first run

12.8% of every authored visible volume in the library already ships as a
featureless box -- 2,876 of 22,432 across 405 specs. Measured by asking
`deli_counter/prop_species.species_for_name` what each one resolves to:

    crate_stack_security_room                503
    shelf_run_vault_room                     393
    safe_floor_vault_room                    297
    cabinet_locker_vault_room                291
    VAULT                                    153
    crate_stack_tall_security_room_shelter   141
    col                                       96

These are not obscure corners. They are the props a player stares at in a
vault or a security room, and the routing table says `None` for them out loud
-- so they are box, box, box in a room where a crate, a locker and a safe
should each read as itself.

This matters because an instrument that finds nothing on a real library is
indistinguishable from an instrument that cannot see. This one has ~2,900
findings waiting, and they are known-true before it is written.

## What it is FOR, which decides its shape

The walker, 2026-09-26: "really all it should do is to push Zoo to make assets
that read well at various distances."

That is not a gate on a package. It is a development instrument for ONE repo,
and two things follow from it.

**It reports a worklist, not a verdict.** Nothing here should block a Level
Factory run or become a finding in a validation record. A species that reads
badly is Zoo's to improve, and the output wants to be a ranked list of species
worth an hour of modelling, most-broken first. The coplanar census is the
working precedent: it runs 106 species through Blender, prints a table, and
gates nothing.

**"At various distances" is the measurement, not a parameter of it.** A single
gameplay distance was the wrong design. An asset does not read or fail to read
-- it reads *up to* a distance and then stops, and the useful number per
species is where that happens.

## Instrument 1: legibility range

**Question:** out to what distance does this species still read as itself?

For each species, render its flat mask at a ladder of camera distances and a
fixed set of yaws, and at each distance ask two things:

* **Is it still more than a box?** Compare its mask against a plain box of the
  same bounding volume. Every species starts distinguishable from its own
  bounding box and converges to it as the silhouette collapses into a
  rectangle at range. The distance where it stops being distinguishable is the
  number: "this crate reads as a crate to 8 m and as a box after that."
* **Is it still itself and not its neighbour?** Compare against every other
  species' mask at the same distance and report the nearest one. A safe and a
  shelf run colliding at 6 m is a different and worse finding than either
  collapsing to a box at 25 m.

The output is one row per species -- its box-range, its nearest neighbour, and
the range at which that neighbour becomes indistinguishable -- sorted by
box-range ascending, so the species that stop reading soonest are at the top.
That is the worklist.

A crate and a carton arguably should collide; a safe and a shelf run should
not. No verdict is printed on which.

**AND IT PAYS FOR ITSELF IN DRAW CALLS, WHICH IS THE PART TO NOT OVERSELL.**
The distance at which a species stops being distinguishable from its own
bounding box is also the distance past which its geometry is buying nothing
visible. That is exactly where an LOD swap, an impostor, or a MultiMesh
collapse belongs, and it is currently chosen by nobody. It would be the first
derived answer this repo has to "where does detail stop paying" -- but it is a
consequence of the instrument, not its purpose, and the purpose is that the
asset reads.

Design notes that follow from this repo's own history:

* **The distance ladder and yaw set are recorded in the output.** A silhouette
  is a function of where you stand; a number that does not state its camera is
  not a measurement.
* **The instrument must prove it can see.** A pair of known-distinct species
  and a pair of known-identical ones (any two of the 2,876 boxes) go through
  every run as controls. A descriptor that cannot separate a `streetlight`
  from a `sofa` has learned nothing about the rest.
* **No texture, no material, no lighting.** Silhouette only -- that is the
  doc's test and it is also what makes the result stable across themes.

## Instrument 2: silhouette efficiency

**Question:** how many of this asset's triangles change its outline at all?

The doc's art test, mechanised. Decimate the mesh progressively; at each step
re-render the mask and measure how much it moved. Report the triangle count at
which the outline starts to change, against the asset's actual count. The
ratio is "how much of this geometry is doing silhouette work".

That is the number that would settle `cubicle_bank`'s 24,000 -- not by
comparing it to a band from another game, but by saying how many of those
24,000 a player could see the absence of.

It also answers something the triangle budgets cannot. A Zoo budget is a
REGRESSION DETECTOR ("a species that silently doubles trips them", CLAUDE.md)
and was never a frame cost. Silhouette efficiency is the first thing that
would say whether a budget is set anywhere near the right place.

## What neither of them measures

Beauty, period-correctness, and whether an asset belongs in the room. A
silhouette can be perfectly distinct and perfectly ugly. Both instruments
measure DISTINGUISHABILITY and GEOMETRIC EFFICIENCY, which is the honest
subset of the doc's argument, and the walker's eye remains the only instrument
for the rest.

They also say nothing about frame cost, and should never be presented as if
they do. On this renderer triangles are nearly free.

## What to build first

Instrument 1, and only after its controls pass. It is the one with 2,876
findings already waiting, it needs no decimation machinery, and its output is
a ranked list a person can read in a minute.

The first thing to look at in that list is not the boxes. It is any species
with real geometry whose box-range is SHORT -- an asset somebody modelled that
stops reading at four metres is a worse finding than a placeholder that never
read at all, because the placeholder is honest about what it is.

Instrument 2 needs a decimator and a threshold, and a threshold is exactly the
kind of number this repo insists on measuring before choosing. Build it second,
with instrument 1's descriptor already proven.

## Where it would live

Zoo owns the species and already renders them headless for the coplanar census
(`tools/coplanar_census.py`, three builds per species at min/default/max). A
silhouette pass is the same shape of job: build the species, render, measure,
report. The census is the working precedent for how to run 106 species through
Blender and come back with a table -- including the discipline that a new
species must be RUN through it rather than counted into the total.
