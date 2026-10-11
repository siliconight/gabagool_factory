## Floaters (details laid on a surface, not cut into it)

*Filed 2026-10-11 from the walker's reference: a short Blender tutorial (its
node set-up credited to the YouTube channel Penfinity) and the polycount thread
"Low poly hard surface modelling - Floaters" (polycount.com/discussion/86536,
2011). Roadmap 234. The concept is written down first; the helper below is not
built yet.*

A **floater** is a piece of detail -- a knob, a bezel, a ring, a grille, a
label, a bolt -- made as its own small mesh and laid ON a host surface instead
of cut INTO the host's topology. The host stays simple and the detail carries
the complexity; floaters stack (a ring on a knob on a panel) to build up a part
nobody wants to model as one mesh; and a floater can be baked down into its
host's texture. The modelling recipe from the reference: the floater's origin at
its bottom, its normals out, snapped onto the host face with its rotation
aligned to the face's normal (Blender: snap to Face, Align Rotation to Target,
Project Individual Elements).

**Zoo already builds floaters; this names them.** `flat_forms.JOIN` buries a
part 4 mm into whatever it lands in and `flat_forms.ART_PROUD` stands an art
quad 5 mm proud of the plate behind it (`pack_wall_forms`' numbers);
`crt_forms.STAND_BURY` sinks the CRT's knobs 6 mm into its body, past the
coplanar probe's 2 mm window; `dartboard_forms.RING_PROUD` and
`counter_register.PROUD` stand rings and details 3 mm off their faces. Each
species chose its own number. The concept is one rule for all of them, and a
helper so the next species does not choose again.

**In Cycles a floater hovers and a shader hides it; in Godot nothing hides
it.** The reference keeps its floaters just above the surface and makes them
read as part of it with a Cycles node set-up -- back faces made transparent by
mixing the Geometry and Light Path nodes. Zoo ships to Godot's GL
Compatibility renderer, which has no such pass, and a real-time engine has two
failures a render does not:

- a hovering floater's gap shows at grazing angles and in its shadow;
- two near-parallel faces a few millimetres apart fight in the depth buffer
  from a distance. The census's own arithmetic (`tests/test_coincident_faces.py`,
  `fight_distance_m`) puts it at sqrt(gap x 838871) metres on Godot's default
  24-bit buffer, near 0.05 and far 4000: 41 m for a 2 mm gap, 50 m for 3 mm,
  58 m for 4 mm, 65 m for 5 mm.

The thread's posters name the costs on the other side. A floater pushed deep
into its host darkens under vertex lighting and wastes lightmap texels on faces
nobody sees (Mark Dygert, SpeCter); welded geometry makes cleaner lightmaps
(Xendance); and deleting a floater's back faces can put holes in its shadow
(Mark Dygert). Zoo's levels are lightmapped, so both directions cost something.
Hence two kinds of floater, and a number for each:

- **A solid floater RESTS.** A knob, a bezel, a ring with walls. Its bottom is
  open -- no face of it lies on the host -- and only a SKIRT goes below the
  host plane: `FLOATER_SKIRT`, past the coplanar probe's 2 mm window and as
  little more as covers the junction (Zoo's `JOIN`, 4 mm). Nothing hovers, so
  there is no gap and no shadow line; almost nothing is buried, so it wastes
  almost no texels. Wear is computed per part before the export merge, so a
  floater's buried vertices take no darkness from the host.
- **A flat floater HOVERS by a known amount.** An art quad, a label, a printed
  ring. It is one-sided, with no back face, and stands `FLOATER_PROUD` off its
  host: at least 3 mm, which fights only beyond 50 m, where a prop-sized
  detail is a pixel or two; Zoo's art already stands 5 mm (65 m). Detail that
  would have to sit flatter than that is texture -- Pixelcoat's skin -- not
  geometry.

**What a floater costs.** In its host's material it merges into the host's mesh
at export (`merge.pack_by_material`): no draw call, its triangles counted
against the species' budget. In a material of its own -- a black knob on a grey
case -- it is one more mesh per material per module, as any part is today.
Prefer the host's material shaded (`FORM_SHADE`) or tinted by vertex colour to a
new material: colour-only variation is never a new material. A floater on a
moving part rides with that part's pivot.

**The helper (to build, roadmap 234).**
`geometry.add_floater(bm, point, normal, build, spin=0.0, skirt=FLOATER_SKIRT)`:
`build(bm)` makes the floater in its own frame (Z up, its base at z = 0, open at
the bottom); the helper turns +Z onto the host's normal, spins it about that
normal, and lowers it into the host by the skirt.
`geometry.add_flat_floater(bm, point, normal, w, h, proud=FLOATER_PROUD)` lays
a one-sided quad. A recipe takes `point` and `normal` from its own construction
-- it knows where its faces are -- rather than by ray-casting, so placement
stays deterministic, and the coplanar census stays the judge of every result.

**Baking (later, priced first).** The reference's other use -- floaters baked
into the host's normal map, so the detail costs no geometry at all -- needs a
normal-map channel Zoo does not ship. It is the route for detail too flat to
model (panel seams, a speaker grille's holes) and for a distant LOD, and would
be priced before it is built: texture memory per module.
