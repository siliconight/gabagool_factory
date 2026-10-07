"""Deli Counter 0.203.0's release: VERSION and the CHANGELOG entry.

    python patch_dc_0203_release.py

Anchored on VERSION (b'Deli Counter 0.202.0') and on CHANGELOG.md's head
(415,451 bytes, LF, as read 2026-10-07).
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DC = ROOT / "deli_counter"

HEAD = "## [0.202.0] - a wall piece needs a wall behind it, and furniture keeps off a hole in its own floor\n"
ENTRY = """## [0.203.0] - a slot owns its own greybox nodes, never a sibling slot's

**How it was seen.** Cold run 9195 (gas_block_001) stopped at the art leg on
one blocker, `PRESENTATION_PLACEMENT_MISMATCH`:

    gas_station_a02: 1 themed module(s) do not match the greybox footprint
    (visual off the collision); 166/167 aligned. Worst: cooler_run
    (prop_cooler_run_delco_1997_04_w328_d90_h220: placed [3.28, 2.2, 0.9]
    on greybox [25.442, 2.2, 0.9])

**The cooler run was never 25 m.** The slot is 3.28 m, at x 14.26, and the
module was built to it. The greybox carries two cooler runs, `cooler_run` (x
12.62..15.90) and `cooler_run_sales` (8.0 m, x -9.54..-1.54). Their union is
exactly 25.442 m.

**The cause.** The placement gate (`portable_building._slot_greybox_extent`)
and the composer's fit (`themed_tscn._slot_extent`) took a greybox node as
part of a slot when its name was the slot id or began `<slot_id>_`. That is
the rule for an opening's own parts (`_lintel`, `_sill`, `_pane`), and it was
written so `seg1` would not swallow `seg10`. But it also swallowed a SIBLING
slot whose id begins the same way: `cooler_run_sales` begins `cooler_run_`.

**How far it reached:**
- 9 of 145 library buildings carry a slot id that begins another's, 19
  pairs.
- In 5, the sibling has greybox nodes:
  - the three pawn shops (`cr_pawn`, `night_pawn`, `pawn_shop_a01`):
    `counter` swallows `counter_service_..._1`, read as 9.86 x 6.36 m against
    its own 4.0 x 0.7;
  - the two gas stations (`gas_station_a02`, `fuel_stop_heist`):
    `cooler_run` swallows `cooler_run_sales`.
- Every level placing one of the five stopped at its art leg.
- The composer orients each module by the same extent. The cooler run's
  orientation came out right only because 0 degrees fit better than 90.
- The banks' `floor_vault` and `ceiling_vault` collide in name but have no
  greybox nodes, so neither reader measured them.
- **Not new.** Cold run 9184's compose manifest for gas_station_a02 carries
  the identical mismatch. Level Factory 0.147.0 never read it: it read one
  placed building's package of many. Level Factory 0.149.0 reads them all.

**The rule now, one copy:** a node belongs to the LONGEST slot id that names
it.
- `themed_tscn.longer_siblings(slot_id, slot_ids)` lists the siblings that
  begin `<slot_id>_`.
- `themed_tscn.owns_node(slot_id, node, siblings)` answers for one node.
- Both extents take the building's slot ids, and both callers pass them.
- `verify_placement` lists its slots once, since it walks them twice.

**Measured after.**
- The gate, re-run on the real gas_station_a02 greybox with cold run 9195's
  own kit and the compose job's arguments (`--theme delco_1997 --style 1`),
  reads 167 checked, 167 matched, 0 mismatched. The job's manifest read 166
  and 1 on the same 167.
- `themed_tscn.py` is a geometry source, so `build.py --all` ran once
  (7 min). Its only tracked change is each of the 146 manifests'
  `built_utc`: no shell, slot or gameplay file moved.

**Tests:** `test_slot_extent_owner.py`, 7.
- On 0.202.0 all 7 fail: the extents take no slot ids, and the real
  greybox reads 25.442 m.
- Two are guards that the old guarantees survive: an opening's parts still
  measure as one, and `seg1` still does not own `seg10`.

**Suite:** 1354 passed, 2 skipped in 93 s (`python -m pytest -q`): 0.202.0's
1347 and this release's 7.

"""


def main():
    v = (DC / "VERSION").read_bytes()
    assert v == b"Deli Counter 0.202.0", repr(v)
    c = (DC / "CHANGELOG.md").read_bytes()
    assert len(c) == 415451 and b"\r\n" not in c, len(c)
    text = c.decode("utf-8")
    assert text.startswith(HEAD) and text.count(HEAD) == 1
    (DC / "VERSION").write_bytes(b"Deli Counter 0.203.0")
    (DC / "CHANGELOG.md").write_bytes((ENTRY + text).encode("utf-8"))
    print("Deli Counter 0.203.0: VERSION and CHANGELOG written")


if __name__ == "__main__":
    main()
