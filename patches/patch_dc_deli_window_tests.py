"""Deli Counter 0.201.0 tests: a deli dresses its front window.

    python patch_dc_deli_window_tests.py

Writes `deli_counter/test_deli_window.py`, NEW (refuses if it exists). Run
BEFORE `patch_dc_deli_window.py`: every test that asks for the deli's window
fails on 0.200.0, where the window rules qualify stores only; the store's own
placement is pinned so the change cannot move it.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEST = ROOT / "deli_counter" / "test_deli_window.py"

SRC = '''"""A deli dresses its front window (0.201.0).

A corner deli has no shop front of glass: its street face is brick, with the
customers' door and one punched window -- `presets.corner_deli`'s S wall,
door `front_customer_entry` at pos -0.28 and a 2.0 m window at pos 0.0, sill
0.85, into the market aisles. The store's window rules
(`migrate_window_sign`, `migrate_window_poster`) hang a sign BESIDE a door in
a wall of glass and qualify stores only, so not one of the six library delis
had a sign or a poster. A deli's neon hangs IN its window, and its sale
posters are taped low on the glass under it.
"""
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import agent_contract                # noqa: E402
import level_design                  # noqa: E402
import migrate_window_poster as POST  # noqa: E402
import migrate_window_sign as SIGN   # noqa: E402
import presets                       # noqa: E402

DELIS = ("deli_a01", "deli_a02", "deli_a03", "cr_deli", "night_deli", "corner_deli_heist_01")


def _spec(name):
    return json.load(open(os.path.join(HERE, "specs", name + ".json"), encoding="utf-8"))


def _bare(d):
    """The spec without its window dressing: what the rules start from."""
    d = copy.deepcopy(d)
    d["volumes"] = [v for v in d["volumes"] if v.get("name") not in (SIGN.NAME, POST.NAME)]
    return d


def _ends(v, axis):
    c, s = v[axis], v["size_" + axis]
    return c - s / 2.0, c + s / 2.0


def test_a_deli_is_a_deli_and_a_store_is_not():
    assert SIGN.is_deli(_spec("deli_a01"))
    assert not SIGN.is_deli(_spec("convenience_store_a01"))


def test_the_front_window_is_the_one_on_the_customers_door_wall():
    fw = SIGN.front_window(_spec("deli_a01"))
    assert fw["wall"] == "S" and abs(fw["u"]) < 1e-9, fw
    assert abs(fw["width"] - 2.0) < 1e-9 and abs(fw["sill"] - 0.85) < 1e-9
    assert abs(fw["head"] - (0.85 + 1.4)) < 1e-9          # `Opening.resolved`'s height
    assert abs(fw["door_u"] - -10.5) < 1e-9               # pos -0.28 of 38 m, snapped


def test_the_sign_hangs_in_the_window_its_top_at_the_head():
    d = _bare(_spec("deli_a01"))
    v, why = SIGN.plan_window(d)
    assert why is None, why
    fw = SIGN.front_window(d)
    x0, x1 = _ends(v, "x")
    assert fw["u"] - fw["width"] / 2.0 < x0 and x1 < fw["u"] + fw["width"] / 2.0, (x0, x1)
    assert abs((v["z"] + v["size_z"] / 2.0) - fw["head"]) < 1e-3, v
    assert v["form"] == "window" and v["collision"] == "none" and v["name"] == SIGN.NAME
    # inside the wall's inner face, against the pane
    face = -14.0 + float(d["wall_thick"]) / 2.0
    y0, _y1 = _ends(v, "y")
    assert y0 > face and y0 - face < 0.10, (y0, face)


def test_the_posters_are_taped_under_the_sign_toward_the_door():
    d = _bare(_spec("deli_a01"))
    sign, _ = SIGN.plan_window(d)
    d["volumes"].append(sign)
    p, why = POST.plan_window(d)
    assert why is None, why
    fw = SIGN.front_window(d)
    x0, x1 = _ends(p, "x")
    assert fw["u"] - fw["width"] / 2.0 < x0 and x1 < fw["u"] + fw["width"] / 2.0, (x0, x1)
    assert p["x"] < fw["u"]                                # the door is west, at -10.5
    top, foot = p["z"] + p["size_z"] / 2.0, p["z"] - p["size_z"] / 2.0
    assert top <= sign["z"] - sign["size_z"] / 2.0 - POST.WINDOW_GAP + 1e-9, (top, sign)
    assert foot >= fw["sill"] + POST.WINDOW_FOOT - 1e-9, (foot, fw)
    assert p["form"] == "store" and p["material"] == POST.MATERIAL["id"]


def test_a_window_too_small_for_both_hangs_the_sign_and_says_why_not_the_posters():
    d = _bare(_spec("deli_a01"))
    for w in d["ext_walls"]:
        if w["wall"] == "S" and int(w.get("story", 0)) == 0:
            for o in w["openings"]:
                if o["kind"] == "window":
                    o["height"] = 0.9
    sign, why = SIGN.plan_window(d)
    assert sign is not None, why
    d["volumes"].append(sign)
    p, why = POST.plan_window(d)
    assert p is None and why, why


def test_a_building_with_no_window_on_the_door_wall_is_refused_and_says_so():
    d = _bare(_spec("deli_a01"))
    for w in d["ext_walls"]:
        if w["wall"] == "S":
            w["openings"] = [o for o in w["openings"] if o["kind"] != "window"]
    v, why = SIGN.plan_window(d)
    assert v is None and why


def test_a_stores_sign_still_hangs_beside_its_door():
    """The store's rule is untouched: the library's stores keep their sign
    where they had it."""
    for name in ("convenience_store_a01", "stop_n_go", "gas_station_a02"):
        d = _spec(name)
        have = next(v for v in d["volumes"] if v.get("name") == SIGN.NAME)
        want, why = SIGN.plan(d)
        assert why is None and want == have, (name, want, have)


def test_a_window_sign_stands_on_no_floor():
    """Hung in its window, a deli's sign's foot is at 1.65 m, under the
    headroom line; counted, it would cost the room a piece of furniture.
    The sign is spelled out here, not planned, so this asks the count alone
    (its first draft read the library's delis, which had no sign, and passed
    on nothing)."""
    d = _bare(_spec("deli_a01"))
    room = next(r for r in d["rooms"] if r["id"] == "market_aisles")
    without = level_design._room_volume_count(d, room)
    sign = {"name": "window_sign", "x": 0.0, "y": -13.645, "z": 1.95, "size_x": 1.2,
            "size_y": 0.06, "size_z": 0.6, "collision": "none", "material": "metal_painted",
            "form": "window"}
    d["volumes"].append(sign)
    assert agent_contract.min_headroom() > sign["z"] - sign["size_z"] / 2.0
    assert level_design._room_volume_count(d, room) == without


def test_every_library_deli_carries_its_window_and_is_a_fixed_point():
    for name in DELIS:
        d = _spec(name)
        names = [v.get("name") for v in d["volumes"]]
        assert SIGN.NAME in names and POST.NAME in names, name
        before = copy.deepcopy(d)
        assert SIGN.migrate(d) == (False, None) and POST.migrate(d) == (False, None), name
        assert d == before, name


def test_the_corner_deli_recipe_dresses_its_window_in_both_modes():
    for mode in ("heist", "assault"):
        s = presets.make("corner_deli", name="corner_deli_t", mode=mode)
        names = [v.get("name") for v in s["volumes"]]
        assert SIGN.NAME in names and POST.NAME in names, (mode, names[-6:])


def test_the_library_delis_are_a_fixed_point_of_furnish():
    import migrate_furnish_recipes
    for name in DELIS:
        d = _spec(name)
        before = json.dumps(d, sort_keys=True)
        migrate_furnish_recipes.migrate(d)
        assert json.dumps(d, sort_keys=True) == before, name
'''


#: test_window_sign.py's control moves to the sign's WALL form. It proved the
#: headroom line still counts a low piece by lowering the window sign itself
#: to 1.3 m; from 0.201.0 a sign hung IN a window stands on no floor at any
#: height (a deli's foot is at 1.65 m), so that control would fail for the
#: change, not for the rule it guards. Found by running the window tests
#: against a scratch copy with this release applied: `assert 13 == 13 + 1`.
WINDOW_SIGN = ROOT / "deli_counter" / "test_window_sign.py"
OLD_CONTROL = '''    """`furnish` tops a room up to a target less what is already there; a
    sign hung over a body's head takes no floor, so it must not count --
    it did, and a refurnish placed one piece fewer (gas_station_a02's
    `shelf_run_3`). The control: the same volume at a wall-fixture height
    (a dartboard's, 1.3 m) still counts."""
'''
NEW_CONTROL = '''    """`furnish` tops a room up to a target less what is already there; a
    sign hung over a body's head takes no floor, so it must not count --
    it did, and a refurnish placed one piece fewer (gas_station_a02's
    `shelf_run_3`). The control: the same sign in its WALL form at a
    wall-fixture height (a dartboard's, 1.3 m) still counts. In its window
    form it does not, at any height (0.201.0): a sign hung in a window
    stands on no floor, and a deli's window puts its foot at 1.65 m."""
'''
OLD_LOW = '''    low["volumes"].append(dict(_sign(spec), z=1.3 + 0.3))
'''
NEW_LOW = '''    low["volumes"].append(dict(_sign(spec), z=1.3 + 0.3, form="wall"))
'''


def main():
    assert not TEST.exists(), "test_deli_window.py already exists; refusing"
    data = WINDOW_SIGN.read_bytes()
    assert len(data) == 7196, "test_window_sign.py is %d bytes, not the 7,196 read" % len(data)
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    for old in (OLD_CONTROL, OLD_LOW):
        assert text.count(old) == 1, "test_window_sign.py anchor found %d times" % text.count(old)
    TEST.write_bytes(SRC.encode("utf-8"))
    WINDOW_SIGN.write_bytes(text.replace(OLD_CONTROL, NEW_CONTROL).replace(OLD_LOW, NEW_LOW)
                            .encode("utf-8"))
    print("test_deli_window.py: %d tests; test_window_sign.py's control moved to the wall form"
          % SRC.count("\ndef test_"))


if __name__ == "__main__":
    main()
