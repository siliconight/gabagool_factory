## [0.174.0] - Empties with real fronts: the rowhome family

Roadmap 106. The walker, 2026-10-04, shown the two Empties this repo built --
`gs_facade_rowhome` and `gs_facade_storefront`, every slot a wall, no
opening -- standing in a row across a street: "that just looks like a
continuous concrete wall". The walker then sent comps (a Philadelphia
rowhouse street; four industrial lofts) and set the period, the 1990s, and
the families, in order: rowhome, porch-front row, main-street storefront,
corner store or taproom, brick factory, cinder-block garage. All read off in
the factory root's `docs/reference/EMPTIES_COMPS.md`. This is the first.

AN EMPTY'S DOOR IS SOLID. `_wall_collision` carves a walkable void for a
door; behind an Empty's door is no interior, no navmesh and nothing to
reach, so on an Empty no opening carves and the wall stays one box. A
window already kept its wall solid.

AN EMPTY CARRIES NO GAMEPLAY. `_record_openings` returns at once on an
Empty: no opening record, no socket marker, no interactive. Item 106's
note on giving an Empty windows asked for exactly this ("an Empty is meant
to carry no gameplay").

`presets.empty_rowhome(width, floors, wall, door_side, cornice, seed)`: the
comp's rowhouse. Two window bays; a door in one bay and a window in the other
at street level, two windows on every storey above, stacked on the same
bays; a back door and a window a storey behind; the side walls left
unlisted so `auto_exterior` seals them -- party walls. Windows are glazed
`facade` by the existing tag, so Zoo skins them opaque `glass_facade`; the
painted pane that will make them read as lit, dark, curtained or barred is
Pixelcoat's next step.

A TERRACE READS AS HOUSES BECAUSE EACH HOUSE DIFFERS, so the library gets a
table of six (`EMPTY_ROWHOMES`, `specs/gs_empty_rowhome_[a-f].json`):
widths 5.5, 6.0 and 6.5 m (the comp's 18-21 ft houses), two or three
storeys, brick (three), siding, Formstone (`stone_ext`) and painted block,
the door to either side, cornice heights 0.6-1.0 m.

`test_empties.py`: the rowhome has a door and a window at street level and
two windows a storey above, its party walls unlisted; an Empty's door does
not carve its wall (the control, the same spec enterable, does); an Empty
records no gameplay from its openings (the control does); the six differ in
width, storeys, wall, cornice and door side, each wall a mapped skin kind;
each spec is the preset's own output.
