"""Level Factory 0.146.0: a convenience store is the Flappahs store, generated
or drawn, and its fascia says so.

The walker, 2026-10-06: "yes, a03 as convenience store; Flappahs store always
Flappahs".

  * `convenience_store` is a Deli Counter preset of its own (0.188.0: the
    station's shop without the pump forecourt). It joins `_VALID_PRESETS`; the
    alias that built it as the forecourt `gas_station` goes.
  * `SIGN_FAMILIES` reads `convenience` before `store` makes it retail, so
    `convenience_store_a01` (gas_station_a03 until DC 0.188.0) and a generated
    convenience store wear the `convenience` family's sign -- FLAPPAHS alone
    in both sign profiles since Pixelcoat 0.58.0.
  * A GENERATED BUILDING'S ROW NAMES NO ARCHETYPE (the audit, 2026-10-06:
    `_write_site_spec`'s single-shell rows carry `id` and geometry only), so
    `sign_family` read `b0` -- the `default` family -- and a generated store
    or station wore a random default name. `_sign_rows` gives such a row the
    brief's archetype for the sign lookup only; the site spec is unchanged.

    python patch_lf_flappahs_store.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
LF = ROOT / "level_factory"

EDITS = {
    LF / "adapters/deli_counter/__init__.py": [
        ('''    "auto_shop", "bank", "card_shop", "casino_tower", "compound",
    "corner_deli", "empty_rowhome", "facade_industrial", "facade_rowhome",
''',
         '''    "auto_shop", "bank", "card_shop", "casino_tower", "compound",
    "convenience_store",
    "corner_deli", "empty_rowhome", "facade_industrial", "facade_rowhome",
'''),
        ('''    "convenience_store": "gas_station", "highway_stop": "gas_station",
''',
         '''    # `convenience_store` is a preset of its own since Deli Counter 0.188.0
    # (the Flappahs store, the station's shop without the forecourt); until
    # then it aliased here to the forecourt `gas_station`.
    "highway_stop": "gas_station",
'''),
    ],
    LF / "apps/cli/commands/__init__.py": [
        ('''    ("gas_station", "gas_station"), ("gas", "gas_station"),
''',
         '''    ("gas_station", "gas_station"), ("gas", "gas_station"),
    # the Flappahs store (0.146.0), before `store` reads it as retail
    ("convenience", "convenience"),
'''),
        ('''def _signs_for(ws, buildings, pixelcoat_out: Path, theme: str) -> dict[str, str]:
''',
         '''def _sign_rows(buildings, archetype) -> list:
    """The rows `_signs_for` reads (0.146.0). A row that names no archetype is
    the brief's own generated building, so it reads as the brief's
    archetype; library and Empty rows name theirs and keep it. Until 0.146.0
    a generated row read as `b0` -- the `default` family -- so a generated
    Flappahs store or gas station wore a random default name. Only the sign
    lookup sees this: the site spec's rows are not touched."""
    return [b if b.get("archetype") else {**b, "archetype": archetype or ""}
            for b in buildings]


def _signs_for(ws, buildings, pixelcoat_out: Path, theme: str) -> dict[str, str]:
'''),
        ('''        signs = _signs_for(ws, buildings, pixelcoat_out, model.theme)
''',
         '''        signs = _signs_for(ws, _sign_rows(buildings, model.archetype),
                           pixelcoat_out, model.theme)
'''),
    ],
    LF / "tests/unit/test_signs_in_site_spec.py": [
        ('''    assert cmds.sign_family("landmark_hall_a02") == "default"
    assert cmds.sign_family("") == "default"
''',
         '''    assert cmds.sign_family("landmark_hall_a02") == "default"
    assert cmds.sign_family("") == "default"


def test_the_flappahs_store_reads_as_a_convenience_store():
    """0.146.0: read before `store` makes it retail. The walker, 2026-10-06:
    the Flappahs store is always Flappahs."""
    assert cmds.sign_family("convenience_store_a01") == "convenience"
    assert cmds.sign_family("convenience_store") == "convenience"
    assert cmds.sign_family("gas_station") == "gas_station"


def test_a_generated_building_reads_as_the_briefs_archetype():
    """0.146.0: a generated row names no archetype and read as `default`."""
    rows = [{"id": "b0"}, {"id": "b1", "archetype": "deli_a01"}]
    out = cmds._sign_rows(rows, "convenience_store")
    assert [cmds.sign_family(r["archetype"]) for r in out] == ["convenience", "deli"]
    assert rows[0] == {"id": "b0"}          # the site spec's own rows are untouched
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
