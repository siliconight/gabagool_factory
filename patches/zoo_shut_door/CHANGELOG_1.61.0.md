## [1.61.0] - an Empty's door is shut

Deli Counter 0.174.0 made an Empty's doors solid in collision. The doorway
module drew the frame and its trim and no leaf -- a leaf existed only for a
storefront door -- so every Empty showed an open doorway into a dark box,
and a player walked into it as an invisible wall. Cold runs 9146-9148's
`empties_one_front_*` frames show it.

Deli Counter 0.178.0 tags an Empty's doorway `glazing: "facade"`, the tag
its windows have carried since 0.80.0. `dna` already turns that tag into
`glazing_kind: "glass_facade"`, and `kit.plan_kit` keeps it in the module
key. `_arch.build_slab` now fills a doorway so tagged with `Doorway_Leaf`
(a part the doorway genome already names):
- **Look.** A painted panel door, `wood_panel` kind, navy -- one of the
  rowhouse comp's three door colours.
- **Placement.** Set back `FACADE_DOOR_SETBACK` 0.08 m from the street face,
  `FACADE_DOOR_THICK` 0.045 m thick.
- **No collision of its own.** The wall's box already holds.

An untagged doorway -- every enterable building's -- is unchanged.

**Cost.** One mesh and one material more per Empty doorway: two a house, 52
on cold run 9148's site, until the Empties are merged per material (roadmap
106, open). Per-house door colour is the next step, and it belongs in
instance data, not a material per colour.

`tests/test_shut_door.py`:
- a tagged doorway plans as a facade opening (runs anywhere);
- under Blender, a tagged doorway builds a `wood_panel` leaf and an untagged
  one builds none.

Proven through the pipeline's own path: `zoo_cli --build-kit` on
`gs_empty_rowhome_f`, before and after.
