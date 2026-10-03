## [1.58.0] - the dumpster

The walker, 2026-10-03, with two photographs of front-load containers
beside a gas station and a farm lane: "we should have some trash dumpsters
next to buildings (sides or back where its not in the way of where
customers would naturally walk into the building)". Zoo had no such
species; Deli Counter's cover vocabulary has named one since its first
level design and got a box.

`dumpster`: a steel tub whose front leans out toward the top and sits
lower than its back, a rim bar under the lids' front edge, a fork pocket
down each side, two black ribbed plastic lids sloping from the hinges to
the front, four casters (`core/dumpster_forms.py`). 1.83 x 1.10 x 1.30 m at
the genome's default, a 3-yard container. The front is -Y: the low edge,
the sticker, the side a body walks up to; the hinges and the wall it backs
onto are +Y. Lot 0.90.0 stands one against a building's back or side wall.

ONE ATLAS, ONE MATERIAL, ONE DRAW, 92 triangles. Every face is a quad on
one painted image (`recipes/_card_atlas.build_art`, the ATM's route): the
fleet colour, rust run down from the rim, grime risen from the ground,
chips to bare metal, the lids' ribs and the sky's streak across them are
paint. `variant` picks one of four invented Delco haulers and with it the
fleet colour -- DELCO DISPOSAL (green, "WE TAKE YOUR CRAP"), JAWN HAULERS
(blue, "ONE MAN'S TRASH. PERIOD."), MACDADE REFUSE (maroon, "YOUS FILL IT.
WE DUMP IT."), TINICUM TRASH CO (orange, "SMELLS LIKE HOME") -- each with a
555 number on a white sticker in the maker's face and a yellow CAUTION /
KEEP OFF label in the notice face. A second hauler's dumpster is a second
image, never a second material on one mesh. The four paints are chosen to
stand off asphalt, brick and painted block: a prop a body walks into reads
against what is behind it.

`tests/test_dumpster.py`: the genome and the kit stem; the slot filled and
centred with no two faces on one plane at 27 sizes and four haulers; every
quad wound out of the thing it closes; the front leaning and lower than the
back; one atlas and every tile present; every line of every tile setting at
every size; the paints distinct and none a grey; the names invented (the
poster, card, club and beer denylists, real haulers, and the two on the
reference photographs) and every number on the fictional exchange; and,
with Blender, one object and one material in the GLB.

