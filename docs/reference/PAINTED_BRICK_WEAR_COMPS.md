# Painted brick, worn by weather: the walker's comps, and what each layer is

The walker, 2026-10-11, with two photographs of a television showing a
shooter's storage-yard map, beside the second-pass texture accents guide
(`BLENDER_SECOND_PASS_TEXTURE_ACCENTS_GUIDE.md`, roadmap 237):

> these are a couple of "screenshots" from call of duty -- showing that
> layering technique to add depths and character to textures/assets

> White paint on bricks that fading through wear of time/erosion/rain/etc

The photographs were shown in chat and are not stored here; another studio's
level is a comp for its technique, never a source. What follows is what was
read off them, by layer and by cause, and which tool of this factory owns
each layer today.

## WHAT THE TWO FRAMES SHOW

One single-storey brick building, seen from two sides.

- **The base: red-brown brick** in regular courses, with a raised string
  course about a metre up and a corner pilaster standing proud of the wall.
- **The coat: whitewash** over everything above the string course. It is a
  different material response, not a tint: matte, light, and it FOLLOWS THE
  BRICK RELIEF -- the paint sits on the brick faces and is thinnest at the
  mortar joints, so where it wears the joints go first and the brick shows
  as a lattice before it shows as patches.
- **The wear, placed by cause.** On the first side the paint is largely
  gone along the corner and the left third (the exposed edge; weather hits
  a corner from two directions), and it thins toward the bottom of the
  painted area, above the string course (the splash band: rain off the
  ground, rising damp). On the second side the paint is mostly intact; the
  wear sits in the top course under the roof's coping (water off the roof
  edge), in a band just above the plinth again, and around the two wall
  boxes. Nothing is worn at random in the middle of a clean field.
- **The plinth: the brick below the string course is never painted** and
  is darker, greyed and stained toward the ground. The boundary is
  construction, not noise -- a different course, a projecting line -- which
  is the guide's rule that construction explains boundaries (its 7.9).
- **Runoff from fixtures.** A grey junction box high on the first wall and
  two on the second, each with a rust-brown streak down from its lower
  corners, narrow at the source and fading with length, exactly the guide's
  7.6: an anchor, a downward direction, a width, a maximum length.
- **A wire** draped between the boxes along the top course, and small
  lamps on a string along the first wall -- dressing, hung from the boxes.
- **A stencilled numeral** ("2") painted on the whitewash of the second
  wall, worn by the same mask as the paint around it: the graphic is under
  the weather, not on top of it (the guide's 7.8, a stencil keeping the
  relief beneath).
- **The coping:** a dark cap along the roof edge, and the wall end shows
  its thickness.
- **The ground:** broken concrete, weeds at the wall's foot, gravel.

Seventy to ninety percent of each painted field is intact whitewash. The
character is in where the paint is missing and why, not in how much.

## WHICH TOOL OWNS EACH LAYER TODAY (roadmap 237's tiers)

| layer in the comp | this factory | tier |
|---|---|---|
| whitewash over brick, paint following the courses, worn at the joints | a Pixelcoat pack for the `wall` kind: albedo and roughness carry the coat, the brick through it and the joint-first wear as tileable layers; `recipe.cavity_grime` is the seed | A |
| wear concentrated at the corner, under the coping, in the splash band | a per-module exposure in the part's vertex colour (`Wear`, read by the shared material on both paths): corner and top-course modules darker toward the brick, the field clean | B1 |
| the paint lattice opening to patches where exposure is high | vertex mask x the pack's breakup texture: the shader the export's worldskin installs once per GLB, priced the CRT `next_pass` way | B2 |
| the unpainted plinth below a string course | Zoo's `base_course` dressing cover exists (0.18 m proud strip, placed by Patina); a metre-tall band is open: a ground-storey pack with a storey-tall tile under the worldskin's world projection, or a cover grown to a band -- not decided here | A/B |
| rust streak from a wall box's lower corners | a flat floater (roadmap 234) under each wall-mounted box, placed by Patina where the box is, merged into the side's dressing mesh with the covers: a streak is dressing, not a decal | B |
| the wire between boxes, the lamp string | dressing species on the box's anchors | existing path |
| the stencilled numeral, worn with the paint | the poster path (Zoo makes the flat art, Deli Counter and Lot say where); a stencil is a poster with the wall's wear in its alpha | existing path + B |
| the coping, the pilaster, the string course | Deli Counter's parapet and Zoo's kit (`edge_strip`, `pilaster`) | existing |

## THE FIRST RECIPE

One wall family, measured against the pack it replaces: a `brick_whitewash`
pack for `wall` (tier A), its ground storey's plinth as whatever the open
question above settles to, a `streak` cover under every wall-mounted box
(tier B through the dressing merge, no new draw), and the per-module
exposure value in `Wear` (B1). Then frames at the fixed stations beside a
run without it, and the walker's eye. Nothing here adds a material a
placement or a decal; GL Compatibility has none.
