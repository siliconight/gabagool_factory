"""Deli Counter 0.189.0: two fixed points the suite holds the library to.

1. **deli_a03 is re-furnished after its door widened.**
   `test_club_fixtures.py::test_the_library_carries_the_fixture_pass_and_is_still_a_fixed_point_of_furnish`
   re-runs `migrate_furnish_recipes.migrate` on every spec and requires the
   spec back unchanged. The 2.4 m `office_stair_door`
   (`patch_dc_deli_a03_stair_door.py`) moves one piece: the work table
   `table_work_r9a51d20f_5` in the deli counter room, y 2.91 -> 3.91. Run
   through Deli Counter's own function, and refused unless that table is the
   only change.
2. **`material_kind.SKIN_KINDS` carries `chain_link`.** It is a literal copy
   of Zoo's `KNOWN_KINDS`, and Zoo 1.77.0 added the chain-link fence's fabric
   kind. `test_material_kind.py::test_the_kinds_are_zoo_s_when_zoo_is_beside_this_repo`
   has failed on every Deli Counter checkout since, which would refuse any
   commit at the pre-commit hook. Deli Counter writes no `chain_link`
   material, so there is no KIND_BY_MATERIAL row to add.

    python patch_dc_0189_fixed_points.py
"""
import copy
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DC = ROOT / "deli_counter"
SPEC = DC / "specs" / "deli_a03.json"
MK = DC / "material_kind.py"

MK_OLD = '''    "brick_brown", "brick_orange",
)
'''
MK_NEW = '''    "brick_brown", "brick_orange",
    # THE CHAIN-LINK FENCE'S FABRIC (Zoo 1.77.0, Pixelcoat 0.59.0): Lot stands
    # the fence; no spec here writes it, so it has no KIND_BY_MATERIAL row
    "chain_link",
)
'''


def main():
    sys.path.insert(0, str(DC))
    import migrate_furnish_recipes as m

    data = SPEC.read_bytes()
    assert b"\r\n" not in data
    d = json.loads(data.decode("utf-8"))
    door = [o for p in d["partitions"] for o in p.get("openings", [])
            if o.get("tag") == "office_stair_door"]
    assert door == [{"kind": "door", "pos": -0.38, "width": 2.4,
                     "tag": "office_stair_door"}], door
    full = copy.deepcopy(d)
    m.migrate(full)
    before = {v["name"]: v for v in d["volumes"]}
    after = {v["name"]: v for v in full["volumes"]}
    moved = sorted(n for n in set(before) | set(after) if before.get(n) != after.get(n))
    assert moved == ["table_work_r9a51d20f_5"], moved
    assert (before[moved[0]]["x"], before[moved[0]]["y"]) == (-15.16, 2.91)
    assert (after[moved[0]]["x"], after[moved[0]]["y"]) == (-15.21, 3.91)
    assert [k for k in set(d) | set(full) if d.get(k) != full.get(k)] == ["volumes"]
    # the same writer migrate_furnish_recipes.main() uses
    SPEC.write_bytes((json.dumps(full, indent=1) + "\n").encode("utf-8"))
    print("re-furnished", SPEC.relative_to(ROOT), "-- moved:", moved[0])

    mk = MK.read_bytes()
    eol = "\r\n" if b"\r\n" in mk else "\n"
    text = mk.decode("utf-8")
    old, new = MK_OLD.replace("\n", eol), MK_NEW.replace("\n", eol)
    assert text.count(old) == 1, "SKIN_KINDS anchor"
    MK.write_bytes(text.replace(old, new).encode("utf-8"))
    print("patched", MK.relative_to(ROOT))


if __name__ == "__main__":
    main()
