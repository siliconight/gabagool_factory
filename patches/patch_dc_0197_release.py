"""Deli Counter 0.197.0: VERSION and CHANGELOG for open floor in L12 and L24.

    python patch_dc_0197_release.py <suite line>

Anchored on VERSION and the CHANGELOG head as read 2026-10-06.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DC = ROOT / "deli_counter"

ENTRY = '''## [0.197.0] - open floor is a way in: L24's utility rooms were never breach-only

**Refuted: 0.194.0's L24 census.** L24 asked L12's graph, which joins rooms
through openings, stairs and ladders only.
- deli_a01's basement partition along y = 1 stops at x 12, so its utility
  room's north edge from x 12 to 19 is open floor. Cold run 9189's bake
  walks across it on the street's island, and L24 named the room "reachable
  only by breaching".
- On that report the walker said to give the deli family's utility rooms
  doors. They are walked into already, so none was added.
- 11 of the 15 rooms 0.194.0 froze were open floor or downstream of it:
  - the deli family's six basement utility rooms;
  - apartment_walkup_a01's kitchen, and through its stair and a door, its
    bedroom and office;
  - rowhouse_raid's kitchen and basement vault.

**One rule.** `tactical.build_graph` has modelled open floor all along, as
a closure. It is lifted unchanged to `tactical.shared_open_edge`, and
`layout_lint._reach_from_ext` asks it for L12 and L24. `build_graph`'s
adjacency was recorded on all 128 room-bearing specs before the lift and
compared after: identical.

**L24 now: 4 rooms in 4 shells**, frozen in `walk_reach_baseline.json`:
- the server room where it is the OBJECTIVE, in cr_deli, deli_a02 and
  night_deli: breach-only by design, the walker's call (an objective you
  breach into);
- deli_a03's fortifiable server room, pending.

Lint warnings went from 420 to 409: the 11.

**Refuted on the way, kept.** A scratch census first kept
apartment_walkup_a01's bedroom and office. It added open-floor links on top
of the old walkable set without re-following stairs and doors from the
rooms they reached. The shipped search is one graph, and
`test_walk_baseline_has_not_gone_stale` named the two first.

**A weakness of the shared rule, not changed here.** It sums the uncovered
length of a shared edge across separate gaps.
- apartment_walkup_a01's storey-1 office-bedroom edge reads open from two
  1 m slivers at its ends, about 0.85 m clear each.
- Nothing L12 or L24 decides rests on it today: a door joins those rooms.
- Changing it changes `build_graph` for its seven callers.

**Tests:** `test_walk_reach.py` +3. All three failed before the change.

**Suite:** SUITE_LINE.

'''


def main():
    suite = " ".join(sys.argv[1:]).strip()
    assert suite, "pass the suite line as run"
    v = DC / "VERSION"
    assert v.read_bytes() == b"Deli Counter 0.196.0", v.read_bytes()
    cl = DC / "CHANGELOG.md"
    data = cl.read_bytes()
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.startswith("## [0.196.0] - the nav gate asks whether an entrance reaches each stair"), text[:60]
    cl.write_bytes((ENTRY.replace("SUITE_LINE", suite) + text).encode("utf-8"))
    v.write_bytes(b"Deli Counter 0.197.0")
    print("Deli Counter 0.197.0: VERSION and CHANGELOG")


if __name__ == "__main__":
    main()
