"""Deli Counter 0.190.0: `navgate_baseline.json` after the rebuild with the
ramp-head trim and the stair-width rule.

The swept gate over the rebuilt library (144 shells, every stair traversing):
- **twin_a01 connects at every origin.** Its flights are 1.2 m now, not
  0.9. `test_grid_baseline_has_not_gone_stale` failed on it until it left the
  list.
- **primos_pizza** gains `patrol_point_PAT_CLUB` among its fragile markers.
  Under 0.189.0 that marker was unreachable at the base bake, so it could not
  read as fragile. Under the trimmed ramps the base origin reaches it, and,
  like the safe, it connects at 6 of 8, exactly where `primos_pizza_stair_0`
  does.
- The other five entries are unchanged.

The file round-trips exactly through `json.dumps(indent=2)` and a newline, so
it is edited as data and written the same way.

    python patch_dc_grid_baseline_0190.py
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = ROOT / "deli_counter" / "navgate_baseline.json"

PRIMOS_MARKERS = ["objective_COUNT_SAFE (6/8 grid origins)",
                  "loot_STASH (6/8 grid origins)",
                  "patrol_point_PAT_CLUB (6/8 grid origins)"]
PRIMOS_ADD = (" Since 0.190.0's ramp-head trim the base origin also reaches "
              "patrol_point_PAT_CLUB, unreachable there under 0.189.0, and it too "
              "connects at 6 of 8, where the stair does.")


def main():
    raw = BASE.read_bytes().decode("utf-8")
    d = json.loads(raw)
    assert json.dumps(d, indent=2) + "\n" == raw, "the baseline no longer round-trips"
    gf = d["grid_fragile"]
    names = [e["shell"] for e in gf]
    assert names.count("twin_a01") == 1 and names.count("primos_pizza") == 1, names
    d["grid_fragile"] = [e for e in gf if e["shell"] != "twin_a01"]
    for e in d["grid_fragile"]:
        if e["shell"] == "primos_pizza":
            assert e["markers"] == PRIMOS_MARKERS[:2], e["markers"]
            e["markers"] = PRIMOS_MARKERS
            e["reason"] = e["reason"] + PRIMOS_ADD
    assert d["counts"]["grid_fragile"] == 7
    d["counts"]["grid_fragile"] = len(d["grid_fragile"])
    BASE.write_bytes((json.dumps(d, indent=2) + "\n").encode("utf-8"))
    print("navgate_baseline.json: twin_a01 out, primos_pizza's markers measured again;",
          "grid_fragile", d["counts"]["grid_fragile"])


if __name__ == "__main__":
    main()
