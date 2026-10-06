"""Deli Counter 0.188.0: VERSION and the CHANGELOG entry for
`patch_dc_store_detail.py` and `patch_dc_convenience_store.py`.

    python patch_dc_flappahs_release.py
"""
import pathlib

DC = pathlib.Path(__file__).resolve().parent.parent / "deli_counter"

ENTRY = '''## [0.188.0] - the Flappahs store, generated or drawn, with everything it was given

**The walker, 2026-10-06:**
- "the care and detail we put into the strip club and flappahs convient store
  [should not] just get lost to the next phase of level creation. That level
  of detail should be in the logic that is called when a level calls for a
  Gas Station, Convient Store, or a strip club."
- Then: "a03 as convenience store; Flappahs store always Flappahs".

**What the audit found, checked against the files.** Most of the store's
detail was already in the recipe: counter, gondolas, cooler wall, slush
machine, roller grill, ATM, video poker, posters, glass front and lights.
Three things were not.

**1. The window beer sign and sale posters lived only in migrated specs.**
- Every library store carries one `window_sign` and one `window_poster`.
- 0 of the 6 stores generated from `presets.gas_station` carried either, and
  no preset emitted them. Counted in each shell's `slots.json`: candidate
  seeds 9080, 9181 and 9282 of `gas_block_001` (the A/B workspaces) and 9011,
  9112 and 9213 of `gas_stop_001` (cold run 9177).
- `gas_station` now ends as the slush machine (0.151.0) and roller grill
  (0.152.0) taught it to: by the migrations' own rules,
  `migrate_window_sign.migrate`, then `migrate_window_poster.migrate`.
- A generated store's glass is dressed as a drawn one's.

**2. A generated store's business was read off the mission id.**
`level_design.club_building_id` reads a building's kind from its name and its
`preset`.
- `presets.strip_club` wrote `preset` and `presets.gas_station` did not.
- So a generated store's door sign read "gas" in `lf_gas_block_001_9080` by
  luck, and would not in `lf_restaurant_row_001_...`.
- `gas_station` writes `preset: gas_station`. `club_building_id` is the only
  reader of a building spec's `preset` (checked across Deli Counter, Zoo,
  Lot, Lux, Patina, Pixelcoat and Level Factory; Level Factory's Lux adapter
  reads a job's `preset`, which names a Lux preset, not this).

**3. The Flappahs store sat in the gas-station family, and had no recipe.**
- `gas_station_a03`, tagged "Wawa (Flappahs)" in the factory's building
  registry, stands no forecourt, canopy, pumps or pylon.
- A gas-station brief drew it on about half its candidates (Level Factory
  cold run 9177: 2 of 3).
- `convenience_store` had no recipe, and Level Factory built it as the
  forecourt station.

The fix:
- **`gas_station(..., forecourt=True)`.** `forecourt=False` filters the pad,
  canopy and columns, pump islands, pumps and the `forecourt` room out of
  the one layout, before the fixture rules place anything.
- **`convenience_store(...)`** is that shop with `preset: convenience_store`,
  registered.
- **The library's a03 is now `convenience_store_a01`.**
  - Moved with `git mv`, and its `name` and the quoted store lists in seven
    files rewritten. History in comments keeps the old name.
  - Its family is its id less its variant, so it is the convenience store.
- **Re-derived on the rename.** The window sign and posters derive their
  variant from the building's name. The migrations were run again, so the
  renamed spec is their fixed point; it changed 6 lines.
- **Rebuilt.** a03's old build outputs were moved out of `build/`, so no
  library index draws a gas-station a03.

**Rebuilt again.** `presets.py` is a geometry source, and `build_freshness`
held 143 of 146 shells older than it. `build.py --all` followed, and the
tracked manifests changed only `built_utc`.

**The engine import gate** (`godot_gate.py`, which `check.py` does not run)
was run on the renamed shell, so it tracks the five files a03 did: PASS, 4 of
4 checks, 7 markers.

**Tests.**
- `test_store_window.py` (6): the generated store's sign and posters, placed
  by the library rule, and its `preset`. All fail on 0.187.0.
- `test_convenience_store.py` (6): the shop without the fuel, the station
  keeping all six pumps, the registry and `make`, and the renamed library
  spec.
  - Measured with 0.187.0's `presets.py`: the recipe's three tests fail.
  - The station keeping its pumps is the control, and passes on both.
  - The renamed-spec test fails on 0.187.0 by construction: there is no
    `convenience_store_a01.json` there.
- **`check.py`:** all checks passed. 1,211 unit tests, nav gate 144 shells.

'''


def main():
    version = DC / "VERSION"
    changelog = DC / "CHANGELOG.md"
    v = version.read_bytes()
    assert v == b"Deli Counter 0.187.0", v
    c = changelog.read_bytes()
    assert b"\r\n" not in c
    assert c.startswith(b"## [0.187.0] - "), c[:60]
    version.write_bytes(b"Deli Counter 0.188.0")
    changelog.write_bytes(ENTRY.encode("utf-8") + c)
    print("Deli Counter 0.188.0: VERSION and CHANGELOG")


if __name__ == "__main__":
    main()
