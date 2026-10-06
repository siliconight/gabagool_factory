"""Zoo 1.76.0: VERSION and the CHANGELOG entry for
`patch_zoo_strip_is_not_a_club.py`.

    python patch_zoo_strip_release.py
"""
import pathlib

ZOO = pathlib.Path(__file__).resolve().parent.parent / "zoo"

ENTRY = '''## [1.76.0] - a retail strip is not a strip club

**`strip_retail_a01` and `a02`, a retail strip, said THE WOODER HOLE over the
door.** Found while measuring the two names a building can carry
(`docs/findings/two_names_one_building/` at the factory root).
- `storefront_names` took the club kind from the WORD `strip`.
- Deli Counter decides a strip club by `level_design._strip_club_building`:
  `"strip_club"` in the id. It furnishes the club and gives it a neon by that
  rule only.
- The door now follows the same rule.
- Every club's neon and door still agree.
- A retail strip shows its street number under its retail band.

**Tests** (`tests/test_storefront_names.py`):
`test_a_retail_strip_is_not_a_strip_club`.
- Neither retail strip reads as a club.
- The library club and a generated one still do.
- It fails on 1.75.0's `storefront_names.py`.

**Suite:** 3,316 passed, 382 skipped, 1 xfailed.

'''


def main():
    for token in ("TESTS_LINE", "SUITE_LINE"):
        assert token not in ENTRY, f"fill in {token} before applying"
    version = ZOO / "VERSION"
    changelog = ZOO / "CHANGELOG.md"
    v = version.read_bytes()
    assert v == b"1.75.0", v
    c = changelog.read_bytes()
    assert b"\r\n" not in c
    assert c.startswith(b"## [1.75.0] - "), c[:60]
    version.write_bytes(b"1.76.0")
    changelog.write_bytes(ENTRY.encode("utf-8") + c)
    print("Zoo 1.76.0: VERSION and CHANGELOG")


if __name__ == "__main__":
    main()
