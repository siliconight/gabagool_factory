"""Deli Counter 0.192.0: apartment_walkup_a01's dining set joins the frozen
`stale_pieces_baseline.json`, with why.

`patch_dc_stale_pieces_tests.py` froze 44 pieces and moved 20, apartment's
three among the 20. Moving them broke `test_club_fixtures`' fixed point of
furnish: they are FURNISH pieces, and today's furnish puts them back.
- They stand over an AUTHORED slab hole (storey 1, 2 x 2 m at (4, -3)).
- `furnish` clears the stairs (`_stair_reserved_rects`) and cannot see an
  authored opening, so a refurnish lays the same table over it again.
- That is a generator fix, not a move: furnish and seed_cover should keep
  off authored openings too. Until then they are frozen.

    python patch_dc_stale_pieces_baseline_apartment.py
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = ROOT / "deli_counter" / "stale_pieces_baseline.json"

ADD = ["chair_set_re6154351_10_1", "table_dining_re6154351_10", "table_dining_re6154351_7"]
WHY = (" apartment_walkup_a01's dining set stands over an AUTHORED slab hole, "
       "and today's furnish puts it back there: furnish clears the stairs, "
       "not authored openings, so its fix is in the generator, not a move.")


def main():
    raw = BASE.read_bytes().decode("utf-8")
    d = json.loads(raw)
    assert json.dumps(d, indent=2) + "\n" == raw, "the baseline no longer round-trips"
    sp = d["stale_pieces"]
    assert "apartment_walkup_a01" not in sp, sp.keys()
    assert d["counts"] == {"pieces": 44, "shells": 7}, d["counts"]
    sp["apartment_walkup_a01"] = sorted(ADD)
    d["stale_pieces"] = dict(sorted(sp.items()))
    d["reason"] += WHY
    d["counts"] = {"pieces": sum(len(v) for v in sp.values()), "shells": len(sp)}
    BASE.write_bytes((json.dumps(d, indent=2) + "\n").encode("utf-8"))
    print("stale_pieces_baseline.json:", d["counts"])


if __name__ == "__main__":
    main()
