## [0.138.0] - An Empty's roof slab takes the roof family

Roadmap 106. Cold run 9146, the first level with 0.137.0's Empties across
the street, was refused at export by this repo's own greybox-skin gate:
`GREYBOX_SLAB_IN_A_THEMED_PACKAGE`, 588 slab surfaces in `gb_floor`. All
588 were the Empties' (26 placed; attributed per archetype off the shipped
`site_base.glb`s, 48 + 96 + 120 + 108 + 48 + 168); the three real buildings'
193 were skinned. The worldskin's slab pass dresses a slab from a `floor_`
module beside the base, and an Empty's kit had none -- it has no rooms to
record a floor slot from.

Deli Counter 0.175.0 leaves an Empty only its roof slab and gives it a roof
slot, so Zoo builds it a `roof_` module. Here `SLAB_REVEAL_FAMILY` becomes
`["floor_", "roof_"]`. That follows the rule written on the constant -- a
reveal takes the family of the surface it meets, and an Empty's one slab
meets its roof. Families are tried in order, so a building, which always
carries a `floor_` module, takes exactly the material it took before.

The gate is unchanged and still refuses a slab with no family to take.

`tests/unit/test_worldskin_slabs.py` (real Godot import):
- a roof slab beside only a `roof_` module is skinned from it;
- the control: a base with both a `floor_` and a `roof_` module still takes
  `floor_`;
- the source shape names both families.

Also: `test_lux_rain.py` expected `night` to choose Blue Hour; it has chosen
`Delco Night` by design since 0.121.0, and the full suite failed on that
row on an untouched tree. The row now says so.
