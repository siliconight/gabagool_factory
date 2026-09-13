# Set dressing and hard-surface references, read before the tools draw

The walker, 2026-09-12: "simple google searches of the zoo species can inform
the design before we hit blender." This is that step for the dressing layers
(roadmap 44, 45, 148, 152): eight references the walker handed over, what each
actually says, and what it means for the tool that owns the layer. Read here
by a person; applied in Zoo recipes, Patina placement rules and Pixelcoat
grammars. Rules the references do NOT give are said so, because a page that
was read and found thin is cheaper to record than to re-read.

## What the references say

**80.lv, "Learning hard-surface modeling and rendering"** — the one with
rules. Block out "the silhouette and big shapes first", then work "from big to
small": medium details on the asset, "finally adding small details that convey
a sense of scale". Materials at roughly a 70/30 ratio, one main material over
about seventy percent of the surface, the rest in contrasting colour or a
different material altogether; choose the split from "real-world construction
logic" — what moves, what is handled, what is bolted. Wear where things move:
accents and grime "in smaller areas where pieces would move around". Shiny
parts read in motion; use gloss as a hierarchy, not decoration.

**80.lv, "Studying the set dressing of Bloodborne with UE4"** — the one about
ground and large surfaces. The cobblestone look is "mixing tileables with
simple inserts (floating meshes made to match the underlying tiling
textures)": the ground texture and the pieces on it share a vocabulary, so a
pebble on cobbles is a cobble. Vertex paint plus inserts fills cracks with
grout, puddles, grass. For a huge asset, decide "how am I going to break it
up" before texturing. Grime is cheap and structural: "just multiply down your
underlying base color a little bit" with noise-driven splotches. Detail goes
where the camera is; the far field runs at a quarter of the density, under
fog and shadow.

**Pluralsight, "The importance of set dressing"** — the purpose statement.
Dressing is "filling shelves and generally making it look real and
lived-in". Know the set's purpose and who lives there before choosing; the
inhabitants decide the objects. Place "objects slightly off kilter", because
"objects in the real world are rarely perfectly aligned".

**RetroStyle Games, "Hard surface modeling from basics to pro"** — general:
clean bevels, sharp edges, "trims and decals" to add detail "without
increasing geometry complexity", and "when to sharpen, when to polish, and
when to leave it alone". No scale or hierarchy rules.

**Shapelab, "Beginner's guide to hard surface modeling"** — a definition and
four techniques (box, polygonal, kitbash, sculpt). No rules to apply.

**Forged of Blood, "Environment design and set dressing"** — a dev diary:
dressing follows the level's grid; a map "is a continuously evolving
process"; keep buffer time for changes. No placement rules.

**Art Bully, "Level art / map set dressing"** — a studio scope page: concept,
props, materials, lighting, engine integration, "closely collaborating with
level designers". No rules.

**Reddit r/gamedev, "Where do you draw the line between level design and set
dressing"** — pasted in by the walker after the fetch was refused. The
poster's definitions: level design is "how the player gets from A to B",
dressing is "giving an environment life ... figuring out who inhabits a space,
and how they've shaped what it's become". The thread's answers: the line is
"somewhat fuzzy" and "the narrative is the sticking point" — why is this
here, what story is the level telling; the split into phases exists because
"very few level designers have the ability to deliver artist quality visual
work", and the real workflow "is not a linear ... but an iterative one where
the work loops between artist and designer". The Guerrilla example, from a
Killzone level designer: a block-out places "a huge block to the left of the
player coming out of a spawn point", the artist replaces it with a wall with
a window — "a window blocks firing but it doesn't block sight"; and at small
scale, "if an env artist puts a plant down in place of a cube, it cuts the
corners off. Even if you extended the collision to be the same size as the
original block, a potted plant doesn't 'afford' cover the way that a stone
plinth would". The only consistent industry answer: "whatever works, works",
provided "your sizes are consistent and the player experience is smooth" —
standardised unit sizes so art knows what to build to. Best practice for the
back-and-forth: "put notes directly in the map rather than in an abstract
document". And the cost of skipping the hand-off: "expensive iteration and
needless feedback rounds because design couldn't be arsed to sign off on
block-ins".

**Thiago Klafke, "Modular environments"** — the one about kits, added by
the walker after the first eight. Work on a power-of-two "home grid spacing"
and keep every piece proportional to one base unit; pick the unit from how
close the player gets — "smaller units" up close, "bigger modules" far away.
Put a module's pivot "in one of the 'plane' extremities", not its centre,
and keep contact faces square so pieces combine any way round. Texture
"first when creating modular sets": a wall unit is "a 4-directionally tiling
texture + a trim texture", and the trim carries the edges, the base and the
cap. Hide repetition with vertex colour ("works like Photoshop multiply"),
trims, and "unique modeling" mixed into the modular base. Where a gap
cannot be closed, "add an artificial seam to your piece (such as the
extremity of a panel)" so the join reads as designed. Bake tiling textures
from high-poly planes; bake occlusion separately. "Export your pieces to the
editor early" and refine on what tiles badly in the engine, not in the
modeler.

## What it means for this pipeline, by layer and owner

**The kit already keeps the grid; the trim is the missing half (Klafke; Zoo
+ Pixelcoat, items 76, 141).** Deli Counter's `module_size` 2.0 m is the
home unit and every wall module is authored to it; the composer fits by
footprint, so a centre pivot costs nothing here. What Zoo modules do not
carry is the trim: one tiling skin covers the whole face, and the base,
the cap and the jamb are the same texture as the field. Klafke's wall is
two textures; ours is one. A trim strip at the skirting and the cornice,
resolved by kind like everything else, is the cheapest depth a wall can
gain, and it is also where the "artificial seam" goes: a wall-end
remainder that meets a full module reads as designed when a trim runs
across the join.

**Texture first, then place, then look in the engine (Klafke; the whole
chain).** The order this pipeline runs is the order he prescribes — the
theme library builds before the kit, the kit before the compose — and the
last step is the one to keep honest: the census and the walk are "export
your pieces to the editor early", and every measurement in item 18 came
from doing it.


**Ground and its clutter share one vocabulary (Bloodborne's inserts; Zoo +
Pixelcoat, item 152).** A clutter species is an insert on the surface it sits
on: its base colour is taken from that surface's Pixelcoat grammar and
darkened, not a flat grey of its own. A pebble on `asphalt_delco` is asphalt-
dark; a scrap on carpet is not a pebble at all. The recipe reads the pack the
ground was skinned with. Today every piece is one flat colour with no
relation to the plate — the measured cause of "defects in the texture".

**Big to small, and the small conveys scale (80.lv; Zoo recipes, item 44).**
Every prop species is boxes at the right proportions; the drawing order is
silhouette, then the medium parts that say what the object is (a counter's
kick and top, a cabinet's drawer fronts), then the small parts that give it
scale (handles, a lock, a label). A recipe that has only the box has done step
one of three, and the genome's `reference` line is where the other two are
described before anybody opens Blender.

**Seventy-thirty, from construction logic (80.lv; Zoo materials).** One
species, two materials: the body and the part that is handled, hinged or
bolted. The recipe names both; Pixelcoat resolves both by kind. Wear goes on
the thirty: drawer pulls, the tray of a teller window, a door's push plate —
not spread evenly.

**Know who lives here (Pluralsight; Patina placement, item 148).** Interior
dressing is keyed on the room's role and the building's archetype, which Deli
Counter already emits (`public_entry`, `utility`, `vault`): posters and a
clock in a lobby, a vent and a detector on every ceiling, litter in the
utility room, nothing on a vault wall but the vault. A placement rule that
does not read the room role is decoration; one that does is set dressing.

**Off kilter, by a rule (Pluralsight; Patina and Deli Counter).** Placed
objects get a small yaw and offset jitter derived from a seed and the
object's size — a chair a few degrees off, a poster a centimetre off level —
never a hand-placed nudge, and never on things that are aligned by nature
(wall modules, teller stations, shelving runs).

**Break the big surface up before texturing it (Bloodborne; Pixelcoat and
Patina, item 45).** A 30 m lobby carpet and a 150 m ground plate need a
large-scale variation layer under the tile period: the grammar's `macro`
band is that layer and must be visible at the surface's own scale, and
Patina's vertex banding does the wall-base darkening the reference calls
"multiply down your underlying base color". Decals sit on top of both.

**Detail where the walker is (Bloodborne; Patina surface dressing, item
152).** Density follows the route, not the plate edge. Today 84 percent of
the clutter is in the perimeter strips nobody reaches and the wall bases the
walker brushes past got thirty-five pieces. The density table turns round:
wall bases and path edges high, open ground medium, perimeter low.

**Trims and decals before geometry (RetroStyle; Patina decals, item 152).**
A stain, a scuff, a tyre streak, a paint chip is a decal, not a mesh. The
pass exists in Patina and ships nowhere; the export carries it as Godot
`Decal` nodes with the stamps beside them. That is the layer the walker
called "opacity/transparency as layers on the dominant floor, wall,
ceiling".

**The block-in is the contract, and art can break it without touching
collision (Reddit; Deli Counter, the placement gate, Laser Tag).** This
pipeline already has the sign-off the thread asks for: `functional_shell_
locked` is design signing the block-in, and every themed module is fitted to
the greybox slot it replaces (`verify_placement`, a blocker since LF
0.74.0). What that gate measures is footprint. The thread's two examples are
the two things it does not: a window module in a wall slot changes SIGHT
where the block did not, and a plant in a box's slot changes what the space
AFFORDS as cover even at identical collision. The first is already in the
spec's hands — Deli Counter authors every opening with a kind, so a wall
slot never becomes a window by art — and the second is not measured
anywhere: Patina's cover props and Zoo's species stand in prop volumes
Laser Tag evaluated as boxes. A prop whose silhouette leaves the box it was
judged in is an affordance change the walker will feel and no gate will
report. The census that would catch it compares a placed prop's visual
extent against its slot the way the wall gate does, and that is a Zoo/DC
instrument to build before item 44's recipes stop being boxes.

**Scale is the one thing everyone agrees on (Reddit; agent_contract.json).**
"Your sizes are consistent" is this repo's `agent_contract.json` and the
exact-fit contract — a module's extents equal its slot. Keep it the hard
rule it already is; every reference that says anything says this.

**Notes in the map (Reddit; the manifests).** The thread's best practice is
this pipeline's habit: a package carries its slots, its provenance and its
gate verdicts beside the scene, not in a document. The one gap is the
verdict nobody reads — see item 18's third shape.

## The walker on trees (2026-09-13, cold runs 9031-9033)

Two rulings from looking at frames, both of which generalise past trees.

**A consistent low-poly style beats a half-finished realistic technique.**
The faceted crown of Zoo 0.68 "looked nice in its own retro way"; the
alpha-cutout cards of 0.69.2, measured on cold run 9032, were "not fully
baked" -- hairlines from the cards' side faces, and a canopy in a different
art style from the cars and the shelter beside it. So the cards stay behind
a genome param and the faceted crown ships. Owner: Zoo; the rule for every
species: an experimental technique ships only when a frame says it reads as
finished, and the style of the street is the style of the piece.

**Detail is structure first, and the species decides the structure.**
"Trees usually have multiple branches that stem from the trunk and those
branches have twigs and depending on what species of tree determines how
that looks." Zoo 0.70.0 grows the tree that way -- trunk, leader, primary
branches at the species' angles from vertical, twigs off the outer half,
a faceted leaf cluster at every tip -- from `core.tree_forms`, a table of
the street trees a Delaware County street plants: red maple (branches
ascending 30-48 degrees, an oval crown), pin oak (a leader to the top,
lower limbs drooping past level, upper rising: a pyramid), honey locust
(open, few limbs, fine twigs, a flat thin crown), London plane (massive
limbs forking low, a broad crown), callery pear (every branch rising tight
from one point, a narrow oval). Numbers are what a photograph shows; the
slot sizes the tree. Owner: Zoo, and the same order for every species that
gets the detailed path -- the parts of the real thing in the house style
before any texture trick.

## The walker's Call of Duty frames (2026-09-13): what a forecourt carries

Two screenshots of a gas station in a Tavorsk-style district, sent as
"examples of set dressing". What they show, and who owns each:

**Signage is a BAND across the frontage, not a plaque.** The store's name
runs the full width of its storefront above the glazing, and the canopy
carries a second band along its fascia. A small cabinet centred on a wall
reads as a notice board; the band is what says "this is a shop". Owner:
Pixelcoat (the face, rendered wide) and Lot (the band, sized to the
facade it hangs on).

**A pylon sign at the road.** Tall, freestanding, at the kerb where a
driver reads it before the building -- the second half of a strip's
signage, and the one a player sees from three streets away. Owner: Zoo (a
species) plus Lot (at the frontage, facing the road). NOT BUILT.

**Numbers on things.** Each pump bay carries its number on the canopy
column. Small legible marks at eye height are most of what makes a place
feel run by somebody. Owner: Pixelcoat (a numeral decal), Deli Counter or
Lot (where they go). NOT BUILT.

**Clutter in CLUSTERS, and the clusters are cheap objects.** Blue potable
water drums in a group of four, stacked sandbags, pallets, concrete
jersey barriers dragged across a lane, red-and-white bollards at every
column base. None is a hero asset; each is one simple shape repeated with
variation, and the grouping is what sells it. This pipeline's cover
planner reaches for a box truck or a shipping container -- both correct
and both large. Owner: Zoo (barrel, jersey barrier, bollard, pallet
stack) and Lot (`site_cover` and the kerb line placing them in clusters).
NOT BUILT.

**Walls, fences and hoardings that are not buildings.** A brick garden
wall with coping, corrugated hoarding panels, chain link -- the things
that divide a lot from the street and break a sightline at knee-to-eye
height. Lot has a perimeter and blockers; neither reads as any of these.

Held against the frames, what this pipeline now has right is the street
itself (road, kerbs, paint, parking, trees, furniture, the junction) and
what it lacks is the FORECOURT: the clusters, the bollards, the numbers,
and signage at the size a shop actually wears.

## The walker's Delco main-street shots (2026-09-13)

Three photographs of the real thing: a wet main street of attached
storefronts, a close walk past a butcher's shop, and a trolley street in
the evening. What they have that a generated site does not:

**The buildings are ATTACHED and meet the sidewalk.** A continuous row of
party-wall storefronts with no setback -- the door opens onto the walk.
This pipeline lays freestanding shells with a plate between them and the
road, which is a strip-mall lot, not a main street. Owner: Level Factory's
`site_variation` (the row and its spacing) and Deli Counter (a party wall
has no windows). The single biggest difference between these photographs
and a cold package.

**An awning over every storefront.** Red, black, striped; a metre and a
half deep at the head of the glazing. Probably the cheapest object in this
list and among the loudest. Owner: Zoo (a species) and Lot (hung on the
same facade as the sign).

**Two kinds of sign, not one.** The fascia band along the top of the
storefront AND a projecting blade sign hung perpendicular over the walk,
readable down the street. Owner: Pixelcoat (both faces) and Lot (both
placements).

**Overhead wires, and the poles that carry them.** Utility poles with
crossarms down the kerb line and a web of wires crossing the street --
plus trolley span wire where there are tracks. Nothing in this pipeline
draws a line between two points in the air. Owner: Zoo (`utility_pole`)
and Lot (the catenary between poles).

**Trolley tracks in the road.** Two rails and their ties set into the
asphalt: a Delaware County street, specifically. Owner: Lot, as another
kind of marking -- the machinery that paints a centre line already draws
a long thin thing along a road.

**Pole banners, planters, benches, a wall-mounted mailbox by a door.**
Small, and all in the band between the kerb and the glazing that this
pipeline now populates with lamps and trees.

## The walker's fire escape photo (2026-09-13)

"This is something i'd like to see in our toolset, fireescape stairs brick,
uneven architecture." The photo (not kept on disk; described here) is a
walk-up block in red brick, windows with stone lintels, sills and cornices. A
steel fire escape is bolted to a RECESSED facade in a narrow light well
between two street-facing masses: one landing per floor with a slatted steel
deck and railings on three sides, a switchback flight between landings, and
a drop ladder below the lowest. The neighbouring masses are different heights:
a taller brick party wall and chimney stand above a shorter roof.

**What the pipeline has, measured the same day** (full survey in roadmap 156):

- **Deli Counter owns fire escapes, and they are rules more than geometry.**
  `FireEscape` and fifteen placement tests exist; `_fire_escapes` builds a
  0.12 m deck box, ONE rail on the outer edge with no collision, and a
  0.6 x 0.6 m visual-only column for a stair. Nothing is recorded as a slot,
  so no art ever reaches it. 2 of 132 library specs author one, both serving a
  single floor; 0 of 177 generated specs. No preset proposes one:
  `ladder_place.fire_escape_proposal` exists and nothing calls it.
- **Zoo has pieces, not a fire escape.** `ladder` and `stair_rail` exist; no
  landing, grating, open-tread steel flight or drop-ladder species, and no slot
  role routes to any of them.
- **Brick works end to end** (`brick_delco`, mapped in `delco_1997`). Stone
  lintels, sills and cornices do not: DC's lintel and sill are flush infill in
  the wall's own material, and Zoo's cornice is cut into the wall by design.
- **Uneven massing is rectangular setbacks only** (2 specs). No recessed bays or
  light wells, one parapet height per building, no chimneys. Level Factory's
  site rows always leave an 8 m street between buildings, so a generated block
  never has two buildings touching, let alone at two heights.

**Owners, smallest first slice first:** Deli Counter rebuilds `_fire_escapes`
as walkable landings, flights with collision and guarded edges, recorded as
slots, and proposes one by default where a profile allows (`rowhome`); Zoo
grows `fire_escape_landing` and `fire_escape_stair` species; Pixelcoat grows a
steel grating (its material grammar already cuts holes). Then the massing:
a recessed facade segment in DC, and a terrace site shape in Level Factory
with buildings touching at different heights.

## What the references do not settle

None of them give a number for density, cluster size or contact darkening.
Those come from measurement on a package, frame by frame, the way every other
number in `PIPELINE_ROADMAP.md` did — the references say what to look for,
and the walk says whether it is there.
