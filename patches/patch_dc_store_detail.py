"""Deli Counter 0.188.0: a store generated from the preset dresses its window,
and says what it is, the way the library's stores do.

The walker, 2026-10-06: "the care and detail we put into the strip club and
flappahs convient store [should not] just get lost to the next phase of level
creation. That level of detail should be in the logic that is called when a
level calls for a Gas Station, Convient Store, or a strip club."

The audit that followed (2026-10-06), checked against the files:

  * THE WINDOW BEER SIGN AND THE SALE POSTERS existed only in the library's
    migrated specs. Every library store carries one `window_sign` and one
    `window_poster`; 0 of the 6 store specs generated from `presets.gas_station`
    in cold runs 9080-9282 / 9011-9213 carry either, and no preset emits them.
    The slush machine and the roller grill were given to the preset by the
    migrations' own rules (0.151.0, 0.152.0); the window was not.
  * THE BUSINESS. `level_design.club_building_id` reads a building's kind from
    its name and, on a generated spec, its `preset`. `presets.strip_club`
    writes `preset`; `presets.gas_station` did not, so a generated store's door
    sign read its kind off the MISSION id -- `lf_gas_block_001_9080` contains
    "gas" by luck; `lf_restaurant_row_001_...` does not.

    python patch_dc_store_detail.py [<deli_counter copy>]
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DC = ROOT / "deli_counter"

EDITS = {
    DC / "presets.py": [
        ("""import level_design
import migrate_roller_grill
import migrate_slush_machine
""",
         """import level_design
import migrate_roller_grill
import migrate_slush_machine
import migrate_window_poster
import migrate_window_sign
"""),
        ("""    fx, fy = 32.0, 22.0
    sh = 4.2
    half_x, half_y = fx / 2, fy / 2

    spec = {
        "$schema": "../schema/level.schema.json",
        "name": name, "mode": mode, "seed": 1999, "grid": 0.5,
""",
         """    fx, fy = 32.0, 22.0
    sh = 4.2
    half_x, half_y = fx / 2, fy / 2

    spec = {
        "$schema": "../schema/level.schema.json",
        # `preset` (0.188.0), as `strip_club` writes it: the recipe says what
        # the building is when Level Factory's `lf_<mission>_<seed>` name
        # does not, and `level_design.club_building_id` -- the door sign's
        # business -- reads both.
        "name": name, "mode": mode, "preset": "gas_station", "seed": 1999, "grid": 0.5,
"""),
        ("""    grill, _why = migrate_roller_grill.plan_grill(spec)
    if grill is not None:
        spec["volumes"].append(grill)
    return spec
""",
         """    grill, _why = migrate_roller_grill.plan_grill(spec)
    if grill is not None:
        spec["volumes"].append(grill)
    # THE WINDOW (0.188.0): the beer sign and the pair of sale posters, by
    # the rules the library's stores were given them with
    # (`migrate_window_sign.migrate`, `migrate_window_poster.migrate`), so
    # a store generated for a level dresses its glass as a drawn one does.
    # Until now only the migrated specs had them: 0 of 6 generated store
    # specs did. The sign first -- the posters keep clear of it. A refusal
    # leaves the spec without one; `test_store_window` holds that this
    # preset is not refused, in both modes.
    migrate_window_sign.migrate(spec)
    migrate_window_poster.migrate(spec)
    return spec
"""),
    ],
}

TEST = '''"""A store generated from the preset dresses its window and says what it is
(0.188.0).

The walker, 2026-10-06: the detail put into the Flappahs store must live in
the logic a level runs when it calls for a gas station or a convenience store,
not only in the library's specs. Every library store carried the window beer
sign and the sale posters (migrated in); 0 of 6 store specs generated from
`presets.gas_station` did. And the preset wrote no `preset`, so a generated
store's door sign read its kind off the mission id.

Run:  python -m pytest test_store_window.py -q
"""
import pytest

import level_design
import migrate_window_poster
import migrate_window_sign


@pytest.mark.parametrize("mode", ["heist", "assault"])
def test_a_generated_store_hangs_its_beer_sign_and_tapes_its_posters(mode):
    import presets
    spec = presets.gas_station(mode=mode)
    names = [v.get("name") for v in spec["volumes"]]
    assert names.count(migrate_window_sign.NAME) == 1
    assert names.count(migrate_window_poster.NAME) == 1


@pytest.mark.parametrize("mode", ["heist", "assault"])
def test_the_window_is_where_the_library_rule_puts_it(mode):
    """The preset calls the migrations' own rule, so running the migration
    over its spec changes nothing."""
    import presets
    spec = presets.gas_station(mode=mode)
    assert migrate_window_sign.migrate(spec) == (False, None)
    assert migrate_window_poster.migrate(spec) == (False, None)


@pytest.mark.parametrize("mode", ["heist", "assault"])
def test_a_generated_store_says_what_it_is_whatever_the_level_is_called(mode):
    import presets
    spec = presets.gas_station(name="lf_restaurant_row_001_9104", mode=mode)
    assert spec["preset"] == "gas_station"
    assert "gas_station" in level_design.club_building_id(spec)
'''

NEW_FILES = {DC / "test_store_window.py": TEST}


def main(root=None):
    base = pathlib.Path(root) if root else DC
    staged = {}
    for path, pairs in EDITS.items():
        path = base / path.relative_to(DC)
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
    for path, text in NEW_FILES.items():
        path = base / path.relative_to(DC)
        assert not path.exists(), f"{path} already exists"
        staged[path] = text
    for path, text in staged.items():
        path.write_bytes(text.encode("utf-8"))
        print("patched", path)


if __name__ == "__main__":
    import sys
    main(sys.argv[1] if len(sys.argv) > 1 else None)
