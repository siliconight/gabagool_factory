"""Deli Counter 0.187.0: VERSION and the CHANGELOG entry for
`patch_dc_demo_flag.py`.

    python patch_dc_demo_flag_release.py
"""
import pathlib

DC = pathlib.Path(__file__).resolve().parent.parent / "deli_counter"

ENTRY = '''## [0.187.0] - a spec can say it is a demo, and its validation manifest carries it

Roadmap 185. **The breadth sweep drew `setback_demo` and `pvp_station_ref`
into card_block_001's lots** (Level Factory cold runs 9170 and 9174).
- Level Factory draws any complete shell this repo does not call a facade,
  and reads this repo's word for what a shell is, never its name.
- Nothing said these were not buildings.
- The walker, 2026-10-06: keep demo and reference shells out of levels.

**`demo`, beside `facade`.**
- **Declared:** `LevelSpec.demo` (`spec_types.py`) and the schema property
  (`schema/level.schema.json`, which is closed to unknown keys).
- **Written:** `evidence.collect` writes it into the report that
  `write_reports` saves as `<id>.validation.json`.
- **Judges nothing:** a demo builds and validates like any other spec. The
  flag only says where it belongs.

**Marked: the five specs that exist to demonstrate or test a capability.**
- `setback_demo`: stepped setbacks. `office_stepped` is the building that
  uses them.
- `kitbash_demo`: kitbash assets.
- `rarity_demo`: rarity tiers.
- `survival_demo`: a survival layout.
- `pvp_station_ref`: a PvP station reference.

**Rebuilt.**
- **The five first:** each `validation.json` reads `demo: true`.
- **Then `build.py --all`:** `spec_types.py` is a geometry source, and
  `build_freshness.py` held 141 of 146 shells older than it, which `check.py`
  rightly failed on.
- **What changed:** the manifests' `built_utc`, nothing else tracked. The
  validation manifests are gitignored, and now carry `demo` on all 146.

**Tests** (`test_demo_flag.py`, 4, all failing on 0.186.0): the five specs
say so, a building does not, the schema declares it, and the report carries
it.

'''


def main():
    version = DC / "VERSION"
    changelog = DC / "CHANGELOG.md"
    v = version.read_bytes()
    assert v == b"Deli Counter 0.186.0", v
    c = changelog.read_bytes()
    assert b"\r\n" not in c
    assert c.startswith(b"## [0.186.0] - "), c[:60]
    version.write_bytes(b"Deli Counter 0.187.0")
    changelog.write_bytes(ENTRY.encode("utf-8") + c)
    print("Deli Counter 0.187.0: VERSION and CHANGELOG")


if __name__ == "__main__":
    main()
