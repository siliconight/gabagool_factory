# Zoo's stale club golden digests -- in progress, paused 2026-10-14

**The task:** re-baseline or retire `zoo/tests/test_club_bpy.py`'s `MAIN_DIGESTS`, which hold five pinned digests of
what "main built":
- `crt_tv` at two sizes;
- `booth_seat` as a sofa;
- `pool_table`;
- the bar `table`.

`test_bpy_what_shipped_before_is_what_main_built` checks them inside Blender only. They fail on Zoo 1.108.0 as on
1.109.0, which was found and filed apart while tracing roadmap 247 (`docs/findings/roofprops_bytes/`).

**Why not just re-pin:** a digest that moved for a reason nobody read is the defect the pin exists to catch. Each
change is attributed to the version that made it before the pins move or go.

## Done

- **`digests_at.py`:** inside Blender, builds the five keys with a given Zoo, using the current test's `_build` and
  `_digest`, and prints each digest beside its pin. One instrument for every version.
- **`bisect.py`:** walks Zoo's first-parent commits from a start to `--to` and splits the line wherever any key's
  digest differs, down to neighbouring commits.
- **The first run** (`bisect.out.txt`) measured nothing. At 0.86.0 (5b15338), the start the pins' comment names,
  loading the current test module asks for the species `club_stage`, and 0.86.0 has no genome for it.

## Next, after the walker's demo of 2026-10-14

1. Start the line at 0.87.0 (c69ab57), the first Zoo with `club_stage`. `bisect.py` has no `--from` yet; it needs one.
2. Attribute each digest change to its version's CHANGELOG entry.
3. Then decide, key by key: re-pin where the change is understood and wanted, or retire the pin.
   - Its species already have other Blender coverage (`test_interior_bpy.py`, `test_crt_screens.py`).
   - The digest reads vertex order, which Zoo has moved on purpose since: 1.103.0 sorts by corners, and 1.109.0
     restarts each bevelled face at its lowest vertex.

**Deferred:** the bisect runs Blender once a measured commit, and it waits until the walker's demo is over so it
cannot compete with the walk for the machine.
