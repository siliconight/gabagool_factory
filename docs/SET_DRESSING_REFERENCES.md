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

## What it means for this pipeline, by layer and owner

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

## What the references do not settle

None of them give a number for density, cluster size or contact darkening.
Those come from measurement on a package, frame by frame, the way every other
number in `PIPELINE_ROADMAP.md` did — the references say what to look for,
and the walk says whether it is there.
