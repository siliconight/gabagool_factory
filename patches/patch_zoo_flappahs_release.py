"""Zoo 1.75.0: VERSION and the CHANGELOG entry for `patch_zoo_flappahs.py` and
`patch_zoo_flappahs_notes.py`.

    python patch_zoo_flappahs_release.py
"""
import pathlib

ZOO = pathlib.Path(__file__).resolve().parent.parent / "zoo"

ENTRY = '''## [1.75.0] - the brand is FLAPPAHS, and a convenience store's door says so

**The walker, 2026-10-06:** "Flappahs store always Flappahs". The walker
writes the brand "flappahs".

**The spelling.**
- Pixelcoat's sign profile and mark spell it FLAPPAHS
  (`profiles/signs/delco.json`, `marks/flappahs_red.svg`).
- Zoo spelled it FLAPPHAS, in `price_pylon_forms.STORE`. That is the one
  constant every Flappahs surface reads: the pylon, the pumps, the coffee
  island, the slush machine and the door sign.
- So a station could wear FLAPPAHS on its fascia under a FLAPPHAS pylon.
- `STORE` is now FLAPPAHS, and every other occurrence outside this changelog
  is respelled: 11 Python files and 4 species' notes. No Zoo hash reads a
  species' notes.
- Both spellings are eight letters, so nothing sized from the string moves.
- Comments that cite an older run were respelled with the rest (cold run
  9122's hot spot, 9108's walk copy). The frames those runs took say
  FLAPPHAS.

**The door.**
- `storefront_names` reads a building's kind from whole words of its business
  string. The gas kind's words were gas, fuel, gs and stop.
- The Flappahs store is `convenience_store_a01` since Deli Counter 0.188.0,
  and a generated one reads `<level> convenience_store`. Neither carries any
  of those words, so its door showed a street number: 2814, for
  `convenience_store_a01`.
- `convenience` joins the gas kind's words.

**Tests** (`tests/test_storefront_names.py`):
- `test_the_brand_is_spelled_the_walkers_way` and
  `test_a_convenience_store_is_a_flappahs`. Both fail on 1.74.0's
  `price_pylon_forms.py` and `storefront_names.py`.
- **The suite:** 3,315 passed, 382 skipped, 1 xfailed.

'''


def main():
    version = ZOO / "VERSION"
    changelog = ZOO / "CHANGELOG.md"
    v = version.read_bytes()
    assert v == b"1.74.0", v
    c = changelog.read_bytes()
    assert b"\r\n" not in c
    assert c.startswith(b"## [1.74.0] - "), c[:60]
    version.write_bytes(b"1.75.0")
    changelog.write_bytes(ENTRY.encode("utf-8") + c)
    print("Zoo 1.75.0: VERSION and CHANGELOG")


if __name__ == "__main__":
    main()
