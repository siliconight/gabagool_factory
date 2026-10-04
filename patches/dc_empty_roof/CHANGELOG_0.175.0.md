## [0.175.0] - An Empty is exterior plus roof

Roadmap 106. Cold run 9146 -- the first level to stand 0.174.0's rowhome
Empties across a street -- was refused at export by Level Factory's
greybox-skin gate (`GREYBOX_SLAB_IN_A_THEMED_PACKAGE`): 588 slab surfaces
still in `gb_floor`. Every one was an Empty's: 26 placed, 24 slab tiles on a
three-storey house and 18 on the two-storey, 48 + 96 + 120 + 108 + 48 + 168
= 588 exactly; the three real buildings' 193 were skinned. An Empty has no
rooms, so it recorded no floor and no roof slot, Zoo built it no `floor_` or
`roof_` module, and the worldskin's slab pass had nothing to dress a slab
with.

THE FACADE BRANCH NOW DOES WHAT ITS COMMENT SAID. `build` has documented a
facade as "exterior + roof + theme only. No interior" since it was written,
and called `_slabs()`, which emits every storey's slab:
- **No slab inside it.** An Empty keeps only its roof slab, visual and
  collision. The ground slab and the floors between storeys sat inside a
  sealed box behind opaque glass -- unseen, unreachable, and 18 of every 24
  visual slabs on a three-storey house. The roof keeps its visual, so a
  greybox level (no art pass) still has a top on every Empty, and its
  collision, so the box stays sealed against a throw.
- **A roof slot.** `_record_roof_slots` now runs for a facade when the build
  is modular, as it does for a building, so Zoo dresses the roof. No hole
  can land on an Empty's roof (it has no ladder or stair), so calling it
  without `_slab_holes_cut` first loses nothing.

A ROWHOUSE ROOF IS NOT BRICK. `empty_rowhome` names `roof_material:
"concrete"`: the flat roof of a 1990s Philadelphia rowhouse is tar,
silver-coated, and without the field the roof slot's style follows the
walls (`roofs.roof_slots`), so a brick house would have been handed a brick
roof. The six `gs_empty_rowhome_*` specs are rewritten from the preset.

The other half is Level Factory 0.138.0: the worldskin's slab reveal falls
back from `floor_` to `roof_`, the family of the surface an Empty's one
slab actually meets.

`test_empty_roof.py`:
- an Empty keeps only its roof slab, against the same house made enterable
  (control: all four levels);
- an Empty records one roof slot in concrete, over the full plan;
- the facade branch of `build` asks for its roof slot.

The six `gs_empty_rowhome_*` join `navgate_baseline.json`'s unjudged list
on the same reason as `gs_facade_rowhome`: facade-only, no interior for a
spawn marker to stand in. 0.174.0 should have been refused for this and was
not, because `check.py` runs its unit suites -- this test among them --
BEFORE `nav_gate.py --all` writes the `.navgate.json` it reads. A shell's
first commit therefore always passes `test_no_new_unjudged_shell`; the
Empties' results were first written during this commit's own hook (11:00,
2026-10-04). Recorded, not fixed here.
