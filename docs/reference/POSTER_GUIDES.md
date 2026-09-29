# Poster guides -- what they are for here

Three guides the walker supplied on 2026-09-29, kept verbatim beside this file.
The walker asked that posters fill walls in four places -- strip club
interiors, bar interiors, exterior alley walls and utility poles, and store
windows and walls -- and that these guides raise poster quality across the
board. The card shop keeps its collector promos. The guides fill blanks; they
do not override a look the walker already likes.

| Guide | What it owns here |
|---|---|
| `Making_Strong_2D_Poster_Art_With_Procedural_Tools.md` | The art: hierarchy, three-value blocking, silhouette, directional composition, limited inks, one purposeful imperfection -- and the three tests below |
| `Procedural_Poster_Art_Guide_Blender_Godot_4_7.md` | The system: families with fixed layout rules, a seed that picks only among approved options, viewing bands, atlases, review at play distance |
| `Lewd_Poster_Art_Direction_Guide.md` | The copy and tone by location: club (brash faux glamour), bar (cheap photocopied gig bills), alley (layered, torn handbills); setup, double meaning, deflating turn |

## The three tests, which are the useful part

From the art guide, section 1. Each is mechanical, so each can be an
instrument that runs on every generated poster rather than a reviewer's habit
-- the "good, not just works" gate roadmap item 18 says does not exist:

- **Thumbnail:** shrunk to 120-160 px on its long edge, the focal image and the
  title are still findable.
- **Grayscale:** with colour removed, subject, background and title separate
  by value.
- **Blur:** blurred hard, the major masses make a deliberate pattern, not an
  even field.

An instrument built from these reports what it measured (a value separation,
a mass count) and stops; it does not declare a poster good.

## How the factory makes a poster, which is not how the guides do

The guides assume Blender authoring: Grease Pencil layers, Text objects,
Geometry Nodes, a compositor print pass, a PNG out. Zoo paints poster art in
pure Python instead -- `zoo_keeper/core/flat_art.py` `poster_plate()` onto
`card_art`'s `Canvas` at `card_art.TEXEL` (256 px/m), text in Zoo's
`pixel_type` faces, material `make_painted_material` (paint, not light;
nearest filter). Every guide technique has to be translated into Canvas
operations: a layer is a draw order, a colour ramp is a palette remap, a
registration offset is one ink pass drawn shifted by whole pixels. The Blender
recipes are the intent, not the implementation.

## What the guides say that this factory cannot take as written

- **Godot Decals.** Not supported by GL Compatibility, which is what packages
  ship on. Posters stay thin planes a few millimetres off the wall -- which the
  guides call the default anyway.
- **One texture per poster.** Every unique poster is a texture bind and a draw
  call; `CLAUDE.md`'s draw-call rule says variation belongs in instance data or
  an atlas. The guides' own answer for a wall of many posters is an atlas, so
  the shared per-building poster atlas that Zoo 0.98.0 named and did not build
  comes first, before posters reach more walls.
- **Mipmaps.** The guides assume mipmapped, filtered paper. Zoo's painted
  material is nearest-filtered by design (the pixel look). Whether its import
  carries mipmaps, and whether a halftone survives them, is unmeasured -- check
  it before choosing a dot size.

## Content limits

From the lewd guide and the walker's standing rules together: suggestive,
never explicit; adults only, and never in a youth-coded place (the card shop);
no real protected group as the punchline; every name an invented Delco one,
PG-13 crass, held against a denylist of real marks like
`card_brands.DENY_WORDS` and `club_names.BEER_DENYLIST`. Copy is written into a
reviewed table, never generated at build time.

## The baseline, measured 2026-09-29

`poster_baseline_2026-09-29.png`: the four poster images shipped in the card
shop (walk `_runs/walk_export_card_block_002`), and its play-area wall at 5 m
and 3 m. Against the guides' checks:

| Check | Card shop posters | |
|---|---|---|
| One dominant image | one centred figure | pass |
| Controlled palette | three colours per game | pass |
| Distinct families, not one template | one composition for all twelve games -- sky gradient, battlement skyline, a cloaked figure holding a small one, serif title, maker's mark; the sports league is a cloaked creature too | fail |
| Neighbours do not repeat | identical pairs side by side: art is chosen per size and variant (`flat_forms.plan_poster`), not per placement | fail |
| Title reads at play distance | about 6 cm capitals; unreadable at 5 m | fail |
| Print character with a cause | flat fills; no paper, ink offset, halftone or wear | fail |
| Cheap to repeat | one texture and one art material per poster, each atlas padded to 256 px wide | fail |
