"""Deli Counter 0.194.0: VERSION and CHANGELOG for the server room's door and L24.

    python patch_dc_0194_release.py <suite line>

The suite line is quoted into the entry as run, e.g. "1234 passed in 300s".
Anchored on VERSION and the CHANGELOG head as read 2026-10-06.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DC = ROOT / "deli_counter"

ENTRY = '''## [0.194.0] - deli_a01's server room gets a door, and L24 names every room only a breach reaches

**The measurement.** Cold run 9188's site bake (the walk-test scene of
seed_9104; `docs/findings/deli_a01_upper_storey_9188/` at the factory root)
made deli_a01's server room a navmesh island of its own: 186 m2 on story 1
whose only ways in were two soft-wall breaches, one from the upper hall and
one from the apartment. L12 passed it, because L12 counts a breach panel, a
vaultable window and a floor-hole drop as ways in. The walker's call,
2026-10-06: give it a door.

**The door.** `specs/deli_a01.json`, story 1's partition along x = -2:
- a 1.25 m door at pos 0.25 (y 7.0), tagged `hall_to_server_room`;
- it opens from the upper hall, where the up-stair arrives;
- the breach beside it stays, as a way in for whoever breaches.

**Refurnished, unchanged.** Refurnished through
`migrate_furnish_recipes.migrate`, and furnish laid every piece back where
it was: none stood within 1.5 m of the new doorway. The spec's diff is the
door's six lines. Rebuilt, `circulation.check_shell` reads 15 volumes, 151
of 151 props and 0 conflicts.

**Proven on the site before shipping.** 9188's walk-test staging was copied,
the new shell swapped in, reimported, and baked with the same instrument and
settings:
- the server room's island is gone;
- the upper storey's island grows from 592 to 779 m2;
- islands drop from 165 to 164.

**L24 (WARN).** `layout_lint.walk_unreachable` and `walk_reach_findings`.
- L12's search moves, unchanged, into `_reach_from_ext`, and runs a second
  time over doors, garages, vault doors, stairs, ladders and ramps only.
- A room the first search reaches and the second does not is reachable only
  by breaching, vaulting a window or dropping.
- `graph()` labels a vaultable window "vault", the same as a vault door, so
  the filter acts on the raw opening kind before `graph()` sees it.
- Measured over the library first: 16 rooms in 8 built shells (22 in 11
  counting Level Factory's lf_ specs).
- L12 reads 0 findings over the 128 lint specs before and after the move, and
  a sealed room still fails it (a positive control, run against the patched
  file).

**Frozen: 15 rooms in 8 shells** (`walk_reach_baseline.json`). Each is a
design call put to the walker:
- the deli family's server room: fortifiable in deli_a03; the OBJECTIVE in
  cr_deli, deli_a02 and night_deli, where breaching in may be the point;
- its basement utility room, role 'connector', in all six deli shells;
- apartment_walkup_a01's kitchen, bedroom and office;
- rowhouse_raid's kitchen and basement vault.

A new one fails `test_no_new_room_only_a_breach_reaches`. A room given a
door must leave the list (`test_walk_baseline_has_not_gone_stale`).

**Not fixed here, and found by the same bake.** deli_a01's upper storey,
779 m2 with the door, is still cut off from the street at its up-stair's
foot.
- Furnish placed two crate stacks in the stairwell, and they shut both ways
  round the up-stair: 0.79 m and 0.54 m passages where a bake that erodes
  0.4 m a side needs 0.8 m.
- 9187 was cut off the same way, so 0.192.0 did not do it.
- The fix belongs in furnish, and comes next.

**Tests:** `test_walk_reach.py`, 9.
- All 9 failed before the patches.
- The door test and the library test failed until the door went in.

**Suite:** SUITE_LINE.

'''


def main():
    suite = " ".join(sys.argv[1:]).strip()
    assert suite, "pass the suite line as run"
    v = DC / "VERSION"
    assert v.read_bytes() == b"Deli Counter 0.193.0", v.read_bytes()
    cl = DC / "CHANGELOG.md"
    data = cl.read_bytes()
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.startswith("## [0.193.0] - the root is the builder and its gates"), text[:60]
    cl.write_bytes((ENTRY.replace("SUITE_LINE", suite) + text).encode("utf-8"))
    v.write_bytes(b"Deli Counter 0.194.0")
    print("Deli Counter 0.194.0: VERSION and CHANGELOG")


if __name__ == "__main__":
    main()
