## [1.59.0] - a car's paint rides its vertices

Cold run 9141 priced the parking fields (Lot 0.94.0) on and off on one
package: 17 cars cost +33 draws a heading and +0.15 ms of median frame,
about 11 draws a visible car (`docs/cold_runs/cold_9141/NOTES.md`). A built
car was 10-12 meshes on 9-11 materials, and six to eight of those
materials were ONE pack, `metal_painted`, in as many colours -- the body's
paint, the brightwork, the head, tail and corner lamps, the plate, the
cladding, the grey bumper -- because a tintable pack makes one material per
colour (`materials.make_material`), and `merge.pack_by_material` packs
parts into one mesh per material, never across. That is the colour-only
variation `CLAUDE.md`'s draw-call rule names first, and 1.8.0's
`geometry.tint_wear` is the path that rule asks for.

`car_forms.paint_tints(form, body_kind)` names every painted part and its
colour: the body's paint (when the genome's body kind is `metal_painted`;
a `plastic` body is another pack and keeps its material), the cladding,
and `FIXED_PAINT` -- the brightwork, lamp, plate and bumper colours the
recipe used to pass `make_material`, moved here so a test holds them. The
recipe gives every one of those parts ONE material, `M_Car_painted` at
`car_forms.PAINTED` (white), and multiplies each part's colour into its
`Wear` attribute. A part whose `Wear` layer is missing is refused rather
than shipped white. Level Factory's import (`zoo_worldskin.
_vertex_colour_albedo`) already draws COLOR_0 as albedo on any material
some surface of which is not white, and glTF's base colour is
factor x texture x COLOR_0, so the product is the one the material's own
factor made.

MEASURED on the eight distinct cars of cold run 9141's site, built from its
own slots, skins and seed by 1.58.0 and by this
(`patches/zoo_car_paint/colour_check.py`):

    materials a car     9-11 -> 4  (paint, interior canvas, rubber, glass)
    meshes a car       10-12 -> 5
    triangles          identical, car by car
    base colour        every painted corner, matched by position (0 of
                       852-980 positions unmatched a car): worst
                       |delta| 0.0036, under one 8-bit step -- the tint
                       key's hex rounding
    control            the same cars read as if the tint never landed:
                       worst |delta| 0.9819

The first control written for this check whitened only VEC4 colours, the
exporter writes COLOR_0 as VEC3, and it read the same 0.0036 -- a check
that could not fail. Kept in the tool's comments above the one that
replaced it.

Paid, and said: a lamp lens now shares the paint's material, so a lamp
renamed to light at night (the recipe's note on `_Lens` suffixes) has to
leave it again; wear and tint now share COLOR_0 and cannot be told apart.
The price in a level is the next cold run's.

`tests/test_car_forms.py`: every painted part keeps the colour its own
material carried (literals); a plastic body keeps its own; the recipe
paints with one material, tints the wear, refuses a part with no `Wear`
layer, and every group a tint names is a group it builds.
