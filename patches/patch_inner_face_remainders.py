"""Zoo 1.38.1 + Deli Counter 0.166.1: the remainders get the room face too.

Cold run 9123 showed the room face on every full segment and opening of the
gas station's stone walls, and stone still showing inside at the remainders:
a strip at the stockroom's frame, beside the sales floor's window, at the
walk-in cooler's corner. A remainder is a `wallEnd`, ONE unit box Deli
Counter scales per slot, and 0.166.0 left it out on the guess that a scaled
unit box might not keep its room side. It does, by the same measurement:
`tscn_export.godot_basis` is Ry(-t) x Scale_LOCAL, so a positive per-slot
scale is applied in the module's own frame before the turn, and the unit
box's -Y face (y = -0.5) is the room side at every facing as a segment's is;
and `_fit_rotation` fits WITH the scale and tries the slot's rotation first.
gas_station_a02 has 9 remainders, the widest 1.65 m.

  * Zoo `kit.INNER_FACE_ROLES` and `_arch.build_slab`'s room-face roles gain
    `wallEnd`; the unit module's stem gains `_i<kind>` like any other.
  * Deli Counter `_material_in` stops excluding `size_mod == "end"`, and
    `themed_tscn.INNER_FACE_ROLES` gains `wallEnd`.
  * Both repos' tests gain the remainder.

Every edit asserts its anchor once and refuses to write on a miss.
"""
from __future__ import annotations

import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _edit(path, pairs):
    raw = path.read_bytes()
    assert b"\r\n" not in raw, f"{path}: CRLF in an LF file"
    s = raw.decode("utf-8")
    for old, new in pairs:
        n = s.count(old)
        assert n == 1, f"{path.name}: anchor found {n} times: {old[:60]!r}"
        s = s.replace(old, new)
    path.write_bytes(s.encode("utf-8"))
    print("patched", path.relative_to(ROOT))


ZOO_KIT = [('''#: The roles whose module can carry a ROOM FACE (1.38.0): a full wall segment
#: and the openings in one. Deli Counter's `themed_tscn.INNER_FACE_ROLES` is
#: the mirror.
INNER_FACE_ROLES = ("wall", "window", "doorway", "breach")''',
            '''#: The roles whose module can carry a ROOM FACE (1.38.0): a full wall segment
#: and the openings in one -- and since 1.38.1 a remainder, the unit
#: `wallEnd` Deli Counter scales per slot (its scale is applied in the
#: module's own frame, so its -Y face is the room side too). Deli Counter's
#: `themed_tscn.INNER_FACE_ROLES` is the mirror.
INNER_FACE_ROLES = ("wall", "window", "doorway", "breach", "wallEnd")''')]

ZOO_ARCH = [('''    if inner and species in ("wall", "window", "doorway", "breach") and not plan.get("storefront"):''',
             '''    if inner and species in ("wall", "window", "doorway", "breach", "wallEnd") \\
            and not plan.get("storefront"):''')]

ZOO_TEST = [('''@pytest.mark.parametrize("role,openings", [("wall", []),
                                           ("window", [{"kind": "window", "width": 1.2,
                                                        "height": 1.2, "sill": 0.9}])])''',
             '''def test_a_remainder_is_its_own_build_too():
    """1.38.1: the unit `wallEnd` takes the room face (cold run 9123 showed
    stone at the gas station's remainders)."""
    end = _slot(slot_id="r", size_mod="end", fit={"dims": [0.6, 0.3, 3.9], "pivot": "center"})
    plan = kit.plan_kit({"building_id": "t", "slots": [end, dict(end, slot_id="r2", material_in=None)]},
                        theme="delco_1997", style=1)
    stems = sorted(m["stem"] for m in plan["modules"])
    assert stems == ["wallEnd_delco_1997_01_mstone", "wallEnd_delco_1997_01_mstone_idrywall"]


@pytest.mark.parametrize("role,openings", [("wall", []),
                                           ("window", [{"kind": "window", "width": 1.2,
                                                        "height": 1.2, "sill": 0.9}]),
                                           ("end", [])])'''),
            ('''    slot = _slot(role=role)
    slot["fit"]["openings"] = openings''',
             '''    slot = _slot(role="wall", size_mod="end") if role == "end" else _slot(role=role)
    slot["fit"]["openings"] = openings'''),
            ('''            elif abs(poly.normal.y) < 0.1:
                jamb += 1
                assert "drywall" not in mat, (o.name, mat)
    assert room and wall and jamb''',
             '''            elif abs(poly.normal.y) < 0.1:
                jamb += 1
                assert "drywall" not in mat, (o.name, mat)
    assert room and wall and jamb''')]

DC_MAIN = [('''                and slot.get("role") in ("wall", "window", "doorway", "breach")
                and slot.get("size_mod") != "end" and not slot.get("glazing")''',
            '''                and slot.get("role") in ("wall", "window", "doorway", "breach")
                and not slot.get("glazing")'''),
           ('''        kind and glazing), or None: only a full wall segment or an opening in
        an EXTERIOR wall (`ext_<story>_<N|E|S|W>`) in an outside-only finish
        has one. Not a remainder (`end`, a unit box scaled per slot) and not
        a storefront (glass)."""''',
            '''        kind and glazing), or None: only a wall segment -- a remainder too
        since 0.166.1 -- or an opening in an EXTERIOR wall
        (`ext_<story>_<N|E|S|W>`) in an outside-only finish has one. Not a
        storefront (glass)."""''')]

DC_TSCN = [('''#: The roles whose module can have a room face (Zoo 1.38.0,
#: `kit.INNER_FACE_ROLES`): full exterior wall segments and their openings.
INNER_FACE_ROLES = ("wall", "window", "doorway", "breach")''',
            '''#: The roles whose module can have a room face (Zoo 1.38.0,
#: `kit.INNER_FACE_ROLES`): exterior wall segments, remainders included since
#: 0.166.1 (`wallEnd`), and their openings.
INNER_FACE_ROLES = ("wall", "window", "doorway", "breach", "wallEnd")''')]

DC_TEST = [('''            want = (ext and s.get("material") in OUTSIDE_ONLY and s.get("size_mod") != "end"
                    and s.get("role") in ("wall", "window", "doorway", "breach"))''',
            '''            want = (ext and s.get("material") in OUTSIDE_ONLY and not s.get("glazing")
                    and s.get("role") in ("wall", "window", "doorway", "breach"))'''),
           ('''def test_the_gas_station_s_stone_walls_are_drywall_inside():
    d = json.load(open(os.path.join(HERE, "build", "gas_station_a02.slots.json"), encoding="utf-8"))
    stone = [s for s in d["slots"] if s.get("material") == "stone" and s.get("material_in")]
    assert stone and {s["material_in"] for s in stone} == {"drywall"}''',
            '''def test_the_gas_station_s_stone_walls_are_drywall_inside():
    """Every stone wall slot, the 9 remainders cold run 9123 showed stone at
    included (0.166.1)."""
    d = json.load(open(os.path.join(HERE, "build", "gas_station_a02.slots.json"), encoding="utf-8"))
    stone = [s for s in d["slots"] if s.get("material") == "stone" and s.get("role") != "roof"]
    assert stone and all(s.get("material_in") == "drywall" for s in stone), \\
        [s["slot_id"] for s in stone if not s.get("material_in")]
    assert sum(1 for s in stone if s.get("size_mod") == "end") == 9


def test_the_remainder_stem_mirror_writes_the_room_face():
    slot = {"slot_id": "ext_0_N_seg12", "role": "wall", "size_mod": "end", "style": 1,
            "material": "stone", "material_in": "drywall",
            "fit": {"dims": [0.175, 0.3, 3.9], "pivot": "center"}}
    stem, scaled = themed_tscn.resolve_themed_stem(slot, "delco_1997", 1, material="stone")
    assert scaled and stem == "wallEnd_delco_1997_01_mstone_idrywall"''')]


def main():
    _edit(ROOT / "zoo/zoo_keeper/core/kit.py", ZOO_KIT)
    _edit(ROOT / "zoo/zoo_keeper/recipes/_arch.py", ZOO_ARCH)
    _edit(ROOT / "zoo/tests/test_inner_face.py", ZOO_TEST)
    _edit(ROOT / "deli_counter/deli_counter.py", DC_MAIN)
    _edit(ROOT / "deli_counter/themed_tscn.py", DC_TSCN)
    _edit(ROOT / "deli_counter/test_inner_face.py", DC_TEST)


if __name__ == "__main__":
    main()
