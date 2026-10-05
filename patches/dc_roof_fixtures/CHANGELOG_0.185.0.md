## [0.185.0] - an Empty's TV antenna and satellite dish

The comps' rowhome has "a TV antenna on the roof", and the street has "the
odd early satellite dish". From across the road an Empty's roofline was a
flat parapet edge against the sky.

- **Authored per house**, as the door is: `roof_antenna` and `roof_dish` on
  the spec (`spec_types`, `schema/level.schema.json`), and
  `empty_rowhome(antenna=, dish=)`.
  - The family: an antenna on eight of the twelve, as a 1990s Philadelphia
    street has, since cable came late to the city.
  - A dish on two: the comps' "odd" one, on `b` beside its antenna and on
    `k` alone.
  - `c`, `f` and `h` have neither.
- **`roofs.roof_fixtures`** puts them on the roof slot as `antenna` / `dish`,
  with `front`, the facing of the exterior wall holding the `front_door`
  opening. The front is that wall, not a fixed side. Patina (>= 0.29.0)
  sets them back from it, and Zoo (>= 1.74.0) builds them.
  - Only on a facade. An Empty's roof is never reached, and an antenna a
    body walked through on a real rooftop would lie about it.
  - Asked for on a spec that is not a facade, or one with no front door, it
    raises rather than leaving the fixture out without a word.
  - Every other building's roof slot is unchanged.

The twelve rowhome specs are rewritten from the preset. The roof's geometry
is unchanged; the slot gains three fields. `presets.py` and `roofs.py` are
geometry sources, so every shell is rebuilt.
