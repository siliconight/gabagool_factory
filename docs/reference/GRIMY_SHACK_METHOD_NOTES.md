# A hand-built shack, and what the factory can take from it

Notes on a short video the walker brought on 2026-10-03 (an artist, JoeyToro,
building a derelict shack in Blender for Godot; 1,799 frames, read as six
contact sheets). The video is a hand workflow for one building; this repo
builds buildings by rule. What transfers is the RULES, not the hands.

## The method, in his order

1. **A real place first.** Google Street View of a county road, a mood board
   of three or four photographs, a two-minute sketch. The building has an
   address before it has a polygon.
2. **The silhouette, against a capsule.** A blockout at human scale, then
   sections extruded into a frame, doors and windows cut from it. "Getting
   that silhouette" is the stated goal of the blockout; the roof has a
   lower addition, so the outline is two shapes, not one.
3. **The inside painted dark before any texture.** Interior faces get a dark
   vertex colour so the building reads as unlit through its openings
   ("totally dark inside"). This is done at the blockout, as structure.
4. **Exposed structure with jank.** Thin board supports, then planks laid one
   at a time, each rotated a few degrees off (the move panel showed 14.7 and
   -5.5 degrees) and overlapping. The irregularity is per board, by hand.
5. **One small photo, crunched.** A photograph of his own fence, tiled,
   offset, cropped to 256 x 256, the contrast crushed. One texture for the
   whole shack.
6. **Vertex colour for every shadow.** "This is to simulate a little bit of
   ambient occlusion" -- and then all of the shadows, and the hue shifts,
   painted into COLOR by hand. He adds geometry where the paint needs
   resolution ("if I were to leave the geometry very simple" it could not
   carry the gradient), and says so as the one place he spends triangles.
7. **A second texture for grime**, painted on by the same vertex mask where
   the building is dirtiest, "combining that vertex colour with the new
   texture". Then the material in Godot, tweaked back in Blender.

## What this repo already does

- Vertex colour as the carrier: `geometry.wear_colors` darkens concave
  vertices and adds seeded grime; `tint_wear` carries colour; Level
  Factory's `_vertex_colour_albedo` draws it. The channel exists.
- One small texture per surface kind: Pixelcoat's packs are procedural
  256-class tiles with a crunched, limited palette.
- Silhouette as the first thing built: Deli Counter's greybox IS the
  blockout, placed by Lot, walked before any art.
- Reference first: the authorship guide asks for a brief per prop with a
  real cause; the Delco 1997 art direction and the street rules are the
  references for the kit.

## What it does not do, and could (each priced before shipping)

1. **Contact darkening by geometry, not by noise.** His AO is where things
   MEET: the ground line, under the eave, inside a window reveal, the inside
   corner of an addition. Ours is a concavity term and a noise. A wall
   plate's few vertices cannot carry a gradient at its foot; the fix is a
   loop cut a hand's width above the ground and below the soffit, and a
   darkening computed from distance to those lines. Triangles, not draws.
   Owner: the kit modules (`wall`, `window`, `doorway`, `roof`) in Zoo.
   Measured as a frame pair at a store corner.
2. **A grime layer where the wear is.** A second small texture blended in by
   the vertex channel -- one more sample, no draw -- at the foot of walls,
   under sills, behind downspouts. Pixelcoat would mint the grime tile per
   theme; the skin material blends it by COLOR. Owner: Pixelcoat and the
   worldskin.
3. **Dark interiors for shells.** A building that has no lit interior (an
   upper storey, a backdrop shell) carries dark vertex colour on its inside
   faces, so an opening reads as depth and not as the greybox behind glass.
   This is also the backdrop guide's "windows suggest occupancy without a
   bright grid".
4. **A vocabulary of neglect, for the buildings the brief says are
   neglected.** Boarded windows with janky planks, a sagging awning, a plank
   patch over a hole: Zoo species, each board its own few degrees off,
   placed by the brief (the vacant storefront, the garage), never on the
   open store. The jank is the cause made visible; a tidy store stays tidy.
5. **Silhouette variety as a Deli Counter output.** His shack reads because
   its outline is two shapes. Additions, lean-tos, porch roofs and a
   stepped parapet are cheap in a greybox and expensive to fake later.

## What not to take

- Hand placement. Every board here was moved by a person; the factory
  moves nothing by hand ("where fixes land" in `CLAUDE.md`). The per-board
  jank becomes a rule with a seed, or it does not ship.
- Darkness as a look. The shack is lit by its own vertex paint and little
  else. Our stores are lit by Lux's fixtures and the walker's call is that
  a level reads; the contact darkening above is a shadow under a thing,
  not a mood.
