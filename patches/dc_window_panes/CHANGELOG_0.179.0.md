## [0.179.0] - An Empty's windows carry a painted state

Cold run 9150: at night the rowhome Empties were a black mass outside the
streetlight pools, every window one opaque pane. The walker's Bloodlines
comp asks for lights on to show life: mixed per building, most dark, some
lit, bars at street level, a vacant house boarded (the factory root's
`docs/reference/EMPTIES_COMPS.md`, "LIT WINDOWS AT NIGHT").

Zoo 1.64.0 paints eight states into one atlas. Here `empty_panes.choose`
gives each Empty window one, and `_record_opening_slot` writes it on the
slot as `pane`.
- **Seeded** by building, seed and slot, so a rebuild paints the same
  street.
- **Street level:** bars on half, 28 lit in 100.
- **Upstairs:** no bars, 38 lit in 100.
- **Vacancy is authored, not drawn.** A seeded one-in-seven left none of the
  six rowhomes vacant ((6/7)^6, about 40%), and the agreed family lists
  boarded as a variant. So the spec takes `vacant` (`spec_types`, schema),
  `empty_rowhome(vacant=)` writes it, and `gs_empty_rowhome_e`, the painted
  block house, is the family's vacant one, every window boarded.

`themed_tscn.resolve_themed_stem` names a painted window `_p<state>` by the
same test Zoo's `plan_kit` makes, so the composer finds the module Zoo
built. `empty_panes.py` joins the build-freshness sources.

**Per building, not per placement.** The state rides on the slot and so on
the module, and every placement of one archetype shares its modules. Seven
copies of one rowhome across a street show one pattern seven times. More
variety needs more archetypes or a per-instance pick, and is not here.

`test_empty_panes.py`:
- the states are Zoo's atlas, in its order;
- most windows are dark, and only the street has bars;
- a vacant house is boarded, and the family has exactly one;
- an Empty's window carries its state and an enterable one does not (fails
  on 0.178.0);
- the name is Zoo's name;
- every built Empty window has a state.
