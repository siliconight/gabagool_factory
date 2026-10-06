"""Level Factory 0.144.4: VERSION and the CHANGELOG entry for
`patch_lf_demo_exclusion.py`.

    python patch_lf_demo_exclusion_release.py
"""
import pathlib

LF = pathlib.Path(__file__).resolve().parent.parent / "level_factory"

ENTRY = '''## [0.144.4] - A shell Deli Counter calls a demo is never drawn into a lot

Roadmap 185. **The breadth sweep drew demo and reference shells into
card_block_001's lots** (cold runs 9170 and 9174): `setback_demo` on
seed_9061 and `pvp_station_ref` on seed_9162.
- They are complete builds, carrying every manifest a building does.
- `source_exclusion` kept out only two kinds of shell: this pipeline's own
  composed outputs (the `lf_` prefix) and facades (Deli Counter's `facade`
  flag). It refuses, deliberately, to judge anything by its name.
- The walker, 2026-10-06: keep demo and reference shells out of levels.

**Five such specs exist in Deli Counter.**
- Three were complete and drawable: `setback_demo`, `pvp_station_ref` and
  `survival_demo`.
- `kitbash_demo` and `rarity_demo` were held out only by incomplete builds,
  and would have joined the draw on the next complete one.

**The fix.** Deli Counter 0.187.0 writes `demo` into `<id>.validation.json`,
and `source_exclusion` (`packages/pipeline/building_library.py`) reads it
beside `facade`. It is a third kind, found by Deli Counter's word like the
second, never by the name.

**Measured on the real library after Deli Counter's rebuild:** 127 complete
shells. All five demo and reference shells are excluded with the reason, and
none is drawable.

**What it invalidates.** Every lot drawn from the library. Three shells
fewer in the pool re-deals every seed's draw, the way a new building family
does.

**Tests** (`tests/unit/test_source_library.py`): the rule reads the flag, not
the name, put wrong on purpose both ways, as the facade rule is. It fails on
0.144.3.

**Suite:** 1,932 collected: 1,917 passed, 14 skipped, 1 xfail.

'''


def main():
    version = LF / "VERSION"
    changelog = LF / "CHANGELOG.md"
    v = version.read_bytes()
    assert v == b"0.144.3", v
    c = changelog.read_bytes()
    assert b"\r\n" not in c
    assert c.startswith(b"## [0.144.3] - "), c[:60]
    version.write_bytes(b"0.144.4")
    changelog.write_bytes(ENTRY.encode("utf-8") + c)
    print("Level Factory 0.144.4: VERSION and CHANGELOG")


if __name__ == "__main__":
    main()
