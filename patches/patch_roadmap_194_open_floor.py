"""Roadmap item 194: the L24 rooms, settled by Deli Counter 0.197.0 and the walker.

    python patch_roadmap_194_open_floor.py

Anchored on item 194's first open item as `patch_roadmap_194_closed.py` wrote
it; must match exactly once. Touches neither the generated index nor the
counts line: run `tools/roadmap_status.py --write` and `--check` after.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
RM = ROOT / "PIPELINE_ROADMAP.md"

OLD = ("1. The 15 frozen L24 rooms are the walker's call: the deli family's server rooms "
       "(the objective in cr_deli, deli_a02 and night_deli) and basement utility rooms, three "
       "apartment_walkup_a01 rooms, rowhouse_raid's kitchen and vault.\n")
NEW = ("1. ~~The 15 frozen L24 rooms are the walker's call.~~ **Settled 2026-10-06.** 11 of "
       "the 15 were never breach-only: L24 asked L12's graph, which has no open floor, and "
       "deli_a01's basement utility room is walked into across the 7 m of its north edge its "
       "partition does not cover (cold run 9189's bake). The walker had asked, on that wrong "
       "report, for the utility rooms to get doors; none was needed. Deli Counter 0.197.0 makes "
       "L12 and L24 ask `tactical.shared_open_edge` -- the open-floor rule tactical's graph "
       "always had, lifted unchanged, `build_graph` identical on 128 specs -- and L24 now names "
       "4: the objective server rooms of cr_deli, deli_a02 and night_deli, breach-only by the "
       "walker's call, and deli_a03's fortifiable server room, still the walker's to decide. "
       "Open: the shared rule sums an edge's uncovered length across separate gaps.\n")


def main():
    data = RM.read_bytes()
    assert b"\r\n" not in data, "CRLF in the roadmap; refusing"
    text = data.decode("utf-8")
    assert text.count(OLD) == 1, "item 194's first open item not found once; refusing"
    RM.write_bytes(text.replace(OLD, NEW).encode("utf-8"))
    print("PIPELINE_ROADMAP.md: item 194's L24 rooms settled")


if __name__ == "__main__":
    main()
