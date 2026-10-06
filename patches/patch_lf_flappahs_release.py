"""Level Factory 0.146.0: VERSION and the CHANGELOG entry for
`patch_lf_flappahs_store.py`, `patch_lf_signs_names_only.py` and
`patch_lf_brief_words.py`.

    python patch_lf_flappahs_release.py
"""
import pathlib

LF = pathlib.Path(__file__).resolve().parent.parent / "level_factory"

ENTRY = '''## [0.146.0] - A level that calls for a gas station, a convenience store or a strip club gets the recipe, and the Flappahs store's name

**The walker, 2026-10-06:**
- The detail put into the strip club and the Flappahs store "should be in
  the logic that is called when a level calls for a Gas Station, Convient
  Store, or a strip club."
- Then: "a03 as convenience store; Flappahs store always Flappahs".

**1. `convenience_store` is a recipe of its own.**
- Deli Counter 0.188.0's `convenience_store` is the station's shop without
  the pump forecourt. It joins `_VALID_PRESETS`.
- The alias that built a convenience-store brief as the forecourt
  `gas_station`, with pumps and a canopy, is gone.

**2. The words a brief reaches for.** Each of these was refused
(`UnknownArchetype`), so the level never reached the recipe:
- `gas`, `fuel_station`, `filling_station`, `service_station`,
  `petrol_station` now build `gas_station`;
- `convenience`, `c_store`, `mini_mart`, `minimart` build
  `convenience_store`;
- `gentlemens_club`, `go_go_bar`, `gogo_bar`, `topless_bar`, `strip_joint`
  build `strip_club`.

Left refused on purpose, because a wrong-but-plausible building is worse than
a refusal:
- `corner_store`: in Philadelphia it is as often the deli as the Flappahs
  store;
- `nightclub`: not a strip club, and there is no dance-club recipe;
- `truck_stop`: a diesel plaza, not the corner station.

`deli`, `night_deli` and `stop_n_go` are refused too. They are outside the
three kinds, and the detail audit of 2026-10-06 lists them as open.

**3. The fascia says FLAPPAHS.**
- **`convenience` reads before `store`.** `SIGN_FAMILIES` read
  `convenience_store_a01` as retail. It now reads as the `convenience`
  family, whose only name is FLAPPAHS in both sign profiles since Pixelcoat
  0.58.0.
- **A generated building reads as its recipe.**
  - `_write_site_spec`'s rows for the brief's own generated building carry
    an id and geometry, and no archetype. So `sign_family` read `b0`, the
    `default` family, and a generated store or station wore a random
    default name.
  - `_sign_rows` gives such a row the preset its archetype builds, using the
    adapter's `_preset_for`, for the sign lookup only. The site spec's rows
    are not touched.
  - It uses the preset, not the brief's word, because `sign_family` reads
    substrings and `station` is civic. Read raw, a `service_station` wore a
    civic name, a `mini_mart` a default one and a `go_go_bar` a bar's.
  - Zoo's door sign already reads the same preset (Deli Counter 0.188.0
    writes it into the spec), so one rule says what the building is.
- **A fascia names a business.** `_signs_for` deals only entries with text.
  - Pixelcoat's fuel price board sits in the `gas_station` family because it
    suits a station, but it names nobody.
  - With that family down to FLAPPAHS and the board, this release's own
    dealing, before the rule, gave the board to a generated gas station
    standing alone, to `gas_station_a02` at row index 0 and 2, and to
    `gas_station_a01` at 1 and 3.
  - No recorded cold run dealt the board (every `shop sign(s)` line under
    `docs/cold_runs`), so no level that shipped changes.
  - In both profiles, the board is the only entry with no text.

**Unproven until it runs cold:** a one-building convenience-store brief, and
`gas_block_001`.

**Tests.**
- `tests/unit/test_signs_in_site_spec.py`, 4 new:
  - the store reads as the `convenience` family;
  - a generated row reads as the brief's archetype;
  - a generated row reads as its preset, not the raw word;
  - a station and a store wear FLAPPAHS and never the price board.
- `tests/unit/test_dc_preset_registry.py`, 3 new:
  - `convenience_store` and its words resolve to the store;
  - the three kinds resolve from a brief's words;
  - the words left refused stay refused.
- **What fails on 0.145.0's code:**
  - all of them except the last, which is a control;
  - and the existing `test_the_adapter_knows_every_preset_deli_counter_registers`,
    against Deli Counter 0.188.0.
- **Each later rule was also proven against the rule before it.** Before
  names-only dealing, a generated gas station drew `sign_fuel_price`.
  Before the preset rule, a `service_station` read `civic`.

**Suite:** 1,960 collected: 1,945 passed, 14 skipped, 1 xfail. That is
0.145.0's 1,939, plus the 7 above, plus 14 cases
`tests/test_archetype_resolution.py` draws from the preset set and the alias
table: one preset and 13 aliases more (14 new, 1 gone).

'''


def main():
    assert "SUITE_LINE" not in ENTRY, "fill in the suite before applying"
    version = LF / "VERSION"
    changelog = LF / "CHANGELOG.md"
    v = version.read_bytes()
    assert v == b"0.145.0", v
    c = changelog.read_bytes()
    assert b"\r\n" not in c
    assert c.startswith(b"## [0.145.0] - "), c[:60]
    version.write_bytes(b"0.146.0")
    changelog.write_bytes(ENTRY.encode("utf-8") + c)
    print("Level Factory 0.146.0: VERSION and CHANGELOG")


if __name__ == "__main__":
    main()
