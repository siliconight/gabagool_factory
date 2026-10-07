"""Deli Counter 0.195.0: VERSION and CHANGELOG for the seeder's corridor rule.

    python patch_dc_0195_release.py <suite line>

Anchored on VERSION and the CHANGELOG head as read 2026-10-06.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DC = ROOT / "deli_counter"

ENTRY = '''## [0.195.0] - a seeded piece leaves a body's width on every side, and deli_a01's upper storey reaches the street

**The measurement.** In cold runs 9187 and 9188, deli_a01's upper storey
(779 m2 once 0.194.0 gave its server room a door) was a navmesh island the
street could not reach. The stairwell's plan, drawn against the bake
(`docs/findings/deli_a01_upper_storey_9188/` at the factory root):
- the up-stair, with its side and back guards, runs from the stairwell's
  south wall to its foot, so the only ways from the stairwell's door to the
  stair's foot run north past it;
- two crate stacks `seed_cover` placed shut both of them, where a bake that
  erodes 0.4 m a side needs 0.8 m:
  - `crate_stack_stairwell_0` left 0.79 m and 0.54 m. It was stale: today's
    `_seed_clear` refuses where it stands, 0.01 m off the up-stair's foot
    landing;
  - `crate_stack_stairwell_1` left 0.40 m and 0.23 m, and passed today's rule.

**Why the rule let it.** Each of `_seed_clear`'s margins is a fraction of a
body:
- 0.3 m off a stair's reserve;
- 0.9 m off a volume;
- 1.0 m from a partition's LINE to the piece's centre;
- nothing at all off an exterior wall.

Across the library: 69 seeded pieces in 128 shells; 23 stale, 35 within
1.1 m of a wall, a stair reserve or a piece, 40 either.

**The rule.** `_seed_clear(..., corridor=True)`, asked by both of
`seed_cover`'s calls.
- A standing piece's square keeps `agent_contract.min_corridor_width()`
  clear (1.1 m: 2 x the bake radius + 0.3).
- What it keeps clear of (`_corridor_obstacles`, true box gaps by
  `_box_gap`):
  - every wall's box, exterior and partition alike, `wall_thick` thick as
    the builder stands them;
  - every stair reserve;
  - every standing volume.
- Opt-in: furnish's seven callers keep their own rules.
- `reseat_piece(..., corridor=True)` moves a seeded piece by it, and leaves
  furniture to furnish.

**The library** (`migrate_seed_corridor.py`). It asks before furnish, as the
seeder does, then refurnishes. Across 13 shells it moved 35 pieces and
dropped 7 where nothing within 12 m answered:
- both stairwell crate stacks in deli_a01, a02 and a03. Each stairwell holds
  two stairs and has nowhere a crate fits with a body round it;
- video_store_a01's stockroom shelf-run shelter. That room has less tall
  cover now.

**Checked after the migration.**
- Both migrations are fixed points.
- Every changed spec is a fixed point of furnish. That was measured
  directly: the furnish migration's own `--check` prints totals and cannot
  say.
- The 13 shells are rebuilt, and `circulation.check_shell` passes 13 of 13.

**Proven on the site before shipping.** 9188's walk-test staging was
copied, the new deli_a01 swapped in, reimported, and baked with the same
instrument:
- deli_a01's only island of its own is its roof (957 m2);
- the street's island now covers its basement (783 m2), its ground floor
  (672 m2) and its stair and upper storey (759 m2);
- islands went from 165 (shipped) to 164 (0.194.0's door) to 161.

**Not done here.**
- Furnish keeps only 0.9 m from a volume, so furniture can stand 0.9 to
  1.1 m from a seeded piece. The census, furniture included, finds 4 such
  pieces in 2 shells.
- The nav gate proves each stair's two ends join, never that an entrance
  reaches them. That is how this outlived every gate, and it is next.

**Tests:** `test_seed_corridor.py`, 10.
- All 10 failed before the change.
- The seeder test was rewritten before it counted. In a 20 x 14 m room the
  old seeder happened to land every piece a body off every wall, so the
  test passed without the rule. In a 6 m deep building it failed:
  `counter_island_hall_2` stood 0.36 m off a wall.

**Suite:** SUITE_LINE.

'''


def main():
    suite = " ".join(sys.argv[1:]).strip()
    assert suite, "pass the suite line as run"
    v = DC / "VERSION"
    assert v.read_bytes() == b"Deli Counter 0.194.0", v.read_bytes()
    cl = DC / "CHANGELOG.md"
    data = cl.read_bytes()
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.startswith("## [0.194.0] - deli_a01's server room gets a door"), text[:60]
    cl.write_bytes((ENTRY.replace("SUITE_LINE", suite) + text).encode("utf-8"))
    v.write_bytes(b"Deli Counter 0.195.0")
    print("Deli Counter 0.195.0: VERSION and CHANGELOG")


if __name__ == "__main__":
    main()
