"""Deli Counter 0.188.0, the second half: the Flappahs store as a family and a
recipe of its own.

The walker, 2026-10-06: "yes, a03 as convenience store; Flappahs store always
Flappahs". `gas_station_a03` -- tagged "Wawa (Flappahs)" in
`pipeline/registries/building_configuration_registry.json` -- stands no
forecourt, canopy, pumps or pylon, yet sat in the `gas_station` family, so a
gas-station brief drew a store with no fuel on about half its candidates (cold
run 9177: 2 of 3). And `convenience_store` had no recipe: Level Factory
aliased it to `gas_station`, the forecourt station.

  * `gas_station(..., forecourt=True)`: `forecourt=False` drops the pad, the
    canopy and its columns, the pump islands and pumps, and the `forecourt`
    room -- filtered from the one layout, not spelled twice.
  * `convenience_store(...)`: the store without the fuel, `preset:
    convenience_store`, registered.
  * The library's a03 becomes `convenience_store_a01` (the spec file is moved
    with `git mv` before this runs; this rewrites its `name` and the quoted
    store lists that name it). History in comments keeps the old name.

    git mv specs/gas_station_a03.json specs/convenience_store_a01.json
    python patch_dc_convenience_store.py
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DC = ROOT / "deli_counter"
OLD, NEW = "gas_station_a03", "convenience_store_a01"

EDITS = {
    DC / "presets.py": [
        ("""def gas_station(name: str = "gas_station_preset",
                mode: str = "heist",
                floors: int = 1,
                scale_ref: bool = False,
                basement: bool = False) -> dict:
""",
         """def gas_station(name: str = "gas_station_preset",
                mode: str = "heist",
                floors: int = 1,
                scale_ref: bool = False,
                basement: bool = False,
                forecourt: bool = True) -> dict:
"""),
        ("""    spec["markers"] = markers
    # THE FROZEN DRINK STATION (0.151.0), placed by the rule 0.150.0 gave
""",
         """    spec["markers"] = markers
    # A STORE WITHOUT FUEL (0.188.0): `forecourt=False` is the layout without
    # its pump forecourt -- what `convenience_store` builds, and what the
    # library's Flappahs store, `convenience_store_a01`, stands. Filtered from
    # the one layout rather than spelled twice, and before the rules below
    # place anything, so nothing is placed against a canopy that is not there.
    if not forecourt:
        spec["volumes"] = [v for v in spec["volumes"]
                           if not str(v.get("name", "")).startswith(_FORECOURT_PARTS)]
        spec["rooms"] = [r for r in spec["rooms"] if r.get("id") != "forecourt"]
    # THE FROZEN DRINK STATION (0.151.0), placed by the rule 0.150.0 gave
"""),
        ("""# ---------------------------------------------------------------------------
# OFFICE  --  assault/heist: multi-story corporate tower, central core
""",
         """#: The forecourt's volumes, by the names `gas_station` gives them.
_FORECOURT_PARTS = ("forecourt_", "canopy_", "pump_island_", "pump_")


def convenience_store(name: str = "convenience_store_preset",
                      mode: str = "heist",
                      floors: int = 1,
                      scale_ref: bool = False,
                      basement: bool = False) -> dict:
    \"\"\"THE FLAPPAHS STORE (0.188.0): the gas station's shop -- glass front,
    counter, gondolas, coffee island, glowing cooler wall, slush machine,
    roller grill, the window's beer sign and sale posters, stockroom and the
    manager's office with its safe -- without the pump forecourt. The
    walker, 2026-10-06: "a03 as convenience store; Flappahs store always
    Flappahs". `preset` says `convenience_store`, so a generated store reads
    as one whatever Level Factory names the level.\"\"\"
    spec = gas_station(name=name, mode=mode, floors=floors,
                       scale_ref=scale_ref, basement=basement, forecourt=False)
    spec["preset"] = "convenience_store"
    return spec


# ---------------------------------------------------------------------------
# OFFICE  --  assault/heist: multi-story corporate tower, central core
"""),
        ("""    "gas_station": gas_station,
""",
         """    "gas_station": gas_station,
    "convenience_store": convenience_store,
"""),
    ],
}

TEST = '''"""The Flappahs store as a family and a recipe of its own (0.188.0).

The walker, 2026-10-06: "a03 as convenience store; Flappahs store always
Flappahs". `gas_station_a03` stood no fuel and sat in the gas-station family,
so a gas-station brief drew a store without pumps on about half its candidates;
`convenience_store` had no recipe and was built as the forecourt station.

Run:  python -m pytest test_convenience_store.py -q
"""
import json
import os

import pytest

import migrate_slush_machine
import migrate_window_poster
import migrate_window_sign
import presets

HERE = os.path.dirname(os.path.abspath(__file__))
FORECOURT = ("forecourt_", "canopy_", "pump_island_", "pump_")


def _names(spec):
    return [str(v.get("name", "")) for v in spec["volumes"]]


@pytest.mark.parametrize("mode", ["heist", "assault"])
def test_a_convenience_store_is_the_shop_without_the_fuel(mode):
    spec = presets.convenience_store(mode=mode)
    names = _names(spec)
    assert not [n for n in names if n.startswith(FORECOURT)]
    assert "forecourt" not in {r["id"] for r in spec["rooms"]}
    assert migrate_slush_machine.is_store(spec)
    for want in ("cooler_run", "coffee_island", migrate_window_sign.NAME,
                 migrate_window_poster.NAME):
        assert want in names, want
    assert spec["preset"] == "convenience_store"


@pytest.mark.parametrize("mode", ["heist", "assault"])
def test_the_gas_station_keeps_its_forecourt(mode):
    names = _names(presets.gas_station(mode=mode))
    assert sum(1 for n in names if n.startswith("pump_") and not n.startswith("pump_island_")) == 6
    assert "canopy_roof" in names and "forecourt_pad" in names


def test_the_recipe_is_registered_and_builds_through_make():
    assert presets.REGISTRY["convenience_store"] is presets.convenience_store
    spec = presets.make("convenience_store")
    assert spec["preset"] == "convenience_store"
    assert not [n for n in _names(spec) if n.startswith(FORECOURT)]


def test_the_library_flappahs_store_is_its_own_family():
    """`gas_station_a03` until 0.188.0: the family is the id less its
    variant, so the name is the family."""
    path = os.path.join(HERE, "specs", "convenience_store_a01.json")
    with open(path, encoding="utf-8") as f:
        assert json.load(f)["name"] == "convenience_store_a01"
    assert not os.path.exists(os.path.join(HERE, "specs", "gas_station_a03.json"))
'''

RENAMES = ["test_counter_accent.py", "test_roller_grill.py", "test_sales_cooler.py",
           "test_slush_machine.py", "test_storefront_glazing.py", "test_window_sign.py",
           "phase2b_status.py"]


def _eol(data):
    crlf = data.count(b"\r\n")
    assert crlf in (0, data.count(b"\n")), "mixed line endings"
    return "\r\n" if crlf else "\n"


def main():
    staged = {}
    for path, pairs in EDITS.items():
        data = path.read_bytes()
        eol = _eol(data)
        text = data.decode("utf-8")
        for old, new in pairs:
            old, new = old.replace("\n", eol), new.replace("\n", eol)
            n = text.count(old)
            assert n == 1, f"{path}: anchor matched {n} times: {old[:70]!r}"
            text = text.replace(old, new)
        staged[path] = text
    # the quoted names in the store lists; prose history keeps the old name
    for rel in RENAMES:
        path = DC / rel
        text = path.read_bytes().decode("utf-8")
        n = text.count(f'"{OLD}"')
        assert n >= 1, f"{path}: no quoted {OLD}"
        staged[path] = text.replace(f'"{OLD}"', f'"{NEW}"')
    spec = DC / "specs" / (NEW + ".json")
    assert spec.exists() and not (DC / "specs" / (OLD + ".json")).exists(), \
        "git mv the spec first"
    text = spec.read_bytes().decode("utf-8")
    assert text.count(f'"name": "{OLD}"') == 1
    text = text.replace(f'"name": "{OLD}"', f'"name": "{NEW}"')
    json.loads(text)
    staged[spec] = text
    test = DC / "test_convenience_store.py"
    assert not test.exists()
    staged[test] = TEST
    for path, text in staged.items():
        path.write_bytes(text.encode("utf-8"))
        print("patched", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
