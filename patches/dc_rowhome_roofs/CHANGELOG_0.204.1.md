## [0.204.1] - a quarter of the rowhome roofs carry an antenna or a dish

**The walker, 2026-10-09,** walking club_block_014 (roadmap 219, note 3):
"far too many Sattelite/Attena that makes the rowhomes look a little too
uniform and computer generated. perhaps 30% as many?"

**What was there.** The roof fixtures come from `presets.EMPTY_ROWHOMES`
(0.185.0): an antenna on eight of the twelve houses, "as a 1990s
Philadelphia street has -- cable came late to the city", and a dish on two.
That is 10 fixtures on 9 houses, and every copy of an archetype repeats its
roof.

**Now 3, 30% of 10,** on 3 houses:
- antennas on a and g;
- the dish on k.

A street of the twelve shows a quarter of its roofs dressed. The presets
lose six rows' fixtures (b, d, e, i, j and l). The six specs follow, as the
presets generate them, and the six shells were rebuilt.

*First attempt, refused by the suite and kept here.* The six specs were
edited by hand, and two tests failed, because the presets still asked for
fixtures the built roofs no longer carried:
- `test_roof_fixtures`'s built-roof test;
- `test_empties`'s preset-output test.

The presets are the source.

**Tests.** `test_the_family_has_antennas_on_two_and_a_dish_on_one`
(renamed from `..._on_eight_and_dishes_on_two`) fails on 0.204.0.
