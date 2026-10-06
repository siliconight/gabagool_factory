"""Lot 0.97.0: VERSION and the CHANGELOG entry for `site_fences`
(branch `fence_edge`, cherry-picked). `lot.py` and `version.py` keep their
own `LOT_VERSION`, deliberately (PIPELINE_MAP.md).

    python patch_lot_fence_release.py
"""
import pathlib

LOT = pathlib.Path(__file__).resolve().parent.parent / "lot"

ENTRY = '''## 0.97.0 - the fence at the playable edge: an Empty row's gaps

**The walker, 2026-10-04:** "I like the idea of a fence between playable
areas and non playable areas, thats good feedback to the player". A fence
goes wherever playable ground meets an Empty's back, a vacant lot or the
backdrop. Zoo 1.77.0's `chain_link_fence` is the fence.

**Phase one: an Empty row's gaps** (`site_fences.plan_fences`).
- The Empties stand in rows across the street, doors shut, backs to the
  plate's edge.
- Every gap a body fits through between two of them is a way behind the row,
  onto ground nothing was built for. So is the ground from each end of a row
  to the plate's edge.
- A fence closes each, along the row's front line, flush with the facades.
  From the street the row reads as one frontage with its alleys gated.

**What a body fits through is the player's capsule:**
`characters.player.radius_m` twice, 0.7 m, read from the contract.
- The navmesh's own narrowest gap (`site_cover.min_passable_gap`) is wider.
- A gap between the two is one a player squeezes through and a QA walker
  cannot. That makes it exactly the gap the walk tests would never report.

**The front line** is the row's long edge nearer a road.

**Never across a way, and never around a marker.**
- A run out from a row's end stops at the first road (with its sidewalks),
  path, building or blocker it would cross.
- A gap between two houses that anything crosses is not fenced.
- A run that would stand on a mission marker is not placed.
- A row with a marker anywhere behind its front line is left open, because
  fencing it would strand the marker.
- Each is said (`LOT_FENCE_SKIPPED`), never forced.

**Assembled on cold run 9180's site** with this checkout, against its
`site.json`:
- `LOT_FENCE_PLACED` three times: the 3.0 m alley between the seventh and
  eighth houses, and 13.5 m and 22.0 m from the row's ends to the plate.
  The plate is the extended 134 m, not the declared 115.
- All three reach `site.slots.json` as `chain_link_fence` prop slots, for
  the Zoo kit build to make.

**`COVER_MATERIALS`:** `chain_link_fence` is `metal_bare`, galvanised. The
fabric is its own kind in Zoo.

**Tests** (`tests/test_site_fences.py`), 9:
- a gap a body fits through is fenced along the front line;
- a gap too narrow is left alone;
- a run out from the row stops at a road;
- a gap a path crosses is not fenced, and is said;
- a fence never stands on a marker;
- a row with a marker behind it is left open;
- a row facing x runs along y;
- cold run 9180's row: 3.0, 4.0 and 12.5 m on its declared plate;
- the body is the player's capsule, 0.7 m.

Choosing the wrong long edge as the front line fails four of them. The
file cannot be collected on 0.96.0.

**Suite:** 660 passed. That is 0.96.0's 651 (counted in a worktree at
`main`) and the 9 above.

'''


def main():
    for token in ("TESTS_LINE", "SUITE_LINE"):
        assert token not in ENTRY, f"fill in {token} before applying"
    version = LOT / "VERSION"
    changelog = LOT / "CHANGELOG.md"
    v = version.read_bytes()
    assert v == b"Lot 0.96.0", v
    c = changelog.read_bytes()
    assert b"\r\n" not in c
    assert c.startswith(b"## 0.96.0 - "), c[:60]
    version.write_bytes(b"Lot 0.97.0")
    changelog.write_bytes(ENTRY.encode("utf-8") + c)
    print("Lot 0.97.0: VERSION and CHANGELOG")


if __name__ == "__main__":
    main()
