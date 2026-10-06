"""Level Factory 0.146.0, third part: a brief that calls for a gas station, a
convenience store or a strip club in the words a brief reaches for gets the
recipe, and a generated building's sign reads the recipe it was built from.

The walker, 2026-10-06: the detail "should be in the logic that is called
when a level calls for a Gas Station, Convient Store, or a strip club".
Measured on this checkout's `adapters.deli_counter._preset_for`, every one
of these was REFUSED (`UnknownArchetype`), so the level never reached the
recipe at all:

    gas, fuel_station, filling_station, service_station, petrol_station
    convenience, c_store, mini_mart, minimart
    gentlemens_club, go_go_bar, gogo_bar, topless_bar, strip_joint

Left refused, on purpose, each for a reason a test records:
  * `corner_store`: in Philadelphia that is as often the deli as the
    Flappahs store, and a wrong-but-plausible building is the failure the
    resolver's docstring says it exists to prevent;
  * `nightclub`, `night_club`: a dance club is not a strip club, and there is
    no dance-club recipe;
  * `truck_stop`: a diesel plaza, not the corner station.
(`deli`, `night_deli` and `stop_n_go` are refused too and outside the three
kinds; the detail audit of 2026-10-06 lists them as open.)

THE SIGN. `_sign_rows` (this release, `patch_lf_flappahs_store.py`) gave a
generated row the brief's RAW archetype. `sign_family` reads substrings, and
`station` is civic: a `service_station` would wear a civic name, a
`mini_mart` a default one, a `go_go_bar` a bar's. The building is built from
`_preset_for(archetype)` -- and Zoo's door sign already reads that preset
(Deli Counter 0.188.0 writes it into the spec) -- so the fascia reads it too.
One rule for "what is this building", as `_is_raining` is one rule for rain.

    python patch_lf_brief_words.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
LF = ROOT / "level_factory"

EDITS = {
    LF / "adapters/deli_counter/__init__.py": [
        ('''    "highway_stop": "gas_station",
''',
         '''    "highway_stop": "gas_station",
    # The walker's three kinds (0.146.0), in the words a brief reaches for.
    # Each was refused, so the level never reached the recipe. Left refused
    # on purpose: `corner_store` (in Philadelphia as often the deli as the
    # Flappahs store), `nightclub` (not a strip club, and no dance-club
    # recipe), `truck_stop` (a diesel plaza, not the corner station) --
    # `test_dc_preset_registry.py` records each.
    "gas": "gas_station", "fuel_station": "gas_station",
    "filling_station": "gas_station", "service_station": "gas_station",
    "petrol_station": "gas_station",
    "convenience": "convenience_store", "c_store": "convenience_store",
    "mini_mart": "convenience_store", "minimart": "convenience_store",
    "gentlemens_club": "strip_club", "go_go_bar": "strip_club",
    "gogo_bar": "strip_club", "topless_bar": "strip_club",
    "strip_joint": "strip_club",
'''),
    ],
    LF / "apps/cli/commands/__init__.py": [
        ('''def _sign_rows(buildings, archetype) -> list:
    """The rows `_signs_for` reads (0.146.0). A row that names no archetype is
    the brief's own generated building, so it reads as the brief's
    archetype; library and Empty rows name theirs and keep it. Until 0.146.0
    a generated row read as `b0` -- the `default` family -- so a generated
    Flappahs store or gas station wore a random default name. Only the sign
    lookup sees this: the site spec's rows are not touched."""
    return [b if b.get("archetype") else {**b, "archetype": archetype or ""}
            for b in buildings]
''',
         '''def _sign_rows(buildings, archetype) -> list:
    """The rows `_signs_for` reads (0.146.0). A row that names no archetype is
    the brief's own generated building, so it reads as the Deli Counter
    preset the brief's archetype builds; library and Empty rows name theirs
    and keep it. Until 0.146.0 a generated row read as `b0` -- the `default`
    family -- so a generated Flappahs store or gas station wore a random
    default name. Only the sign lookup sees this: the site spec's rows are
    not touched.

    THE PRESET, NOT THE WORD. `sign_family` reads substrings, and `station`
    is civic: read raw, a `service_station` wore a civic name and a
    `mini_mart` a default one. The building is built from the adapter's
    `_preset_for`, and Zoo's door sign reads that preset too (Deli Counter
    0.188.0 writes it into the spec), so one rule says what it is. A word no
    preset answers to is kept as it is: no generated building stands for it,
    because Deli Counter refused it first."""
    from adapters.deli_counter import UnknownArchetype, _preset_for as _dc_preset
    try:
        business = _dc_preset(archetype or "")
    except UnknownArchetype:
        business = archetype or ""
    return [b if b.get("archetype") else {**b, "archetype": business}
            for b in buildings]
'''),
    ],
    LF / "tests/unit/test_signs_in_site_spec.py": [
        ('''def test_a_station_and_a_store_wear_flappahs_never_the_price_board():
''',
         '''def test_a_generated_building_reads_as_the_preset_it_was_built_from():
    """0.146.0: read raw, `station` is civic -- a generated `service_station`
    wore a civic name, a `mini_mart` a default one, a `go_go_bar` a bar's."""
    for word, family in (("service_station", "gas_station"),
                         ("mini_mart", "convenience"),
                         ("go_go_bar", "club"),
                         ("county_hospital", "civic")):
        (row,) = cmds._sign_rows([{"id": "b0"}], word)
        assert cmds.sign_family(row["archetype"]) == family, (word, row)
    # a word no preset answers to is kept: nothing was generated for it
    (row,) = cmds._sign_rows([{"id": "b0"}], "mixed_block")
    assert row["archetype"] == "mixed_block"


def test_a_station_and_a_store_wear_flappahs_never_the_price_board():
'''),
    ],
    LF / "tests/unit/test_dc_preset_registry.py": [
        ('''def test_this_check_can_actually_find_deli_counter():
''',
         '''def test_the_convenience_store_preset_resolves():
    """Deli Counter 0.188.0's `convenience_store`: the Flappahs store, the
    station's shop without the forecourt. Until 0.146.0 this adapter aliased
    the name to the forecourt `gas_station`, so a convenience-store brief
    stood pumps and a canopy. The walker, 2026-10-06: "a03 as convenience
    store; Flappahs store always Flappahs"."""
    assert _preset_for("convenience_store") == "convenience_store"
    for alias in ("convenience", "c_store", "mini_mart", "minimart"):
        assert _preset_for(alias) == "convenience_store", alias
    assert _preset_for("highway_stop") == "gas_station"


def test_the_walkers_three_kinds_resolve_from_a_briefs_words():
    """0.146.0. The walker, 2026-10-06: the detail belongs "in the logic that
    is called when a level calls for a Gas Station, Convient Store, or a
    strip club". Each of these was refused, so the level never got there."""
    for alias in ("gas", "fuel_station", "filling_station", "service_station",
                  "petrol_station"):
        assert _preset_for(alias) == "gas_station", alias
    for alias in ("gentlemens_club", "go_go_bar", "gogo_bar", "topless_bar",
                  "strip_joint"):
        assert _preset_for(alias) == "strip_club", alias


def test_the_words_left_refused_stay_refused():
    """A wrong-but-plausible building is worse than a refusal. `corner_store`
    is as often the deli as the Flappahs store in Philadelphia; a nightclub
    is not a strip club and has no recipe; a truck stop is not the corner
    station."""
    for word in ("corner_store", "nightclub", "night_club", "truck_stop"):
        with pytest.raises(UnknownArchetype):
            _preset_for(word)


def test_this_check_can_actually_find_deli_counter():
'''),
        ('''from adapters.deli_counter import _preset_for, _VALID_PRESETS
''',
         '''from adapters.deli_counter import UnknownArchetype, _preset_for, _VALID_PRESETS
'''),
    ],
}


def main():
    staged = {}
    for path, pairs in EDITS.items():
        data = path.read_bytes()
        crlf = data.count(b"\r\n")
        assert crlf in (0, data.count(b"\n")), f"{path}: mixed line endings"
        eol = "\r\n" if crlf else "\n"
        text = data.decode("utf-8")
        for old, new in pairs:
            old, new = old.replace("\n", eol), new.replace("\n", eol)
            n = text.count(old)
            assert n == 1, f"{path}: anchor matched {n} times: {old[:70]!r}"
            text = text.replace(old, new)
        staged[path] = text
    for path, text in staged.items():
        path.write_bytes(text.encode("utf-8"))
        print("patched", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
