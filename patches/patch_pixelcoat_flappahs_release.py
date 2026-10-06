"""Pixelcoat 0.58.0: VERSION and the CHANGELOG entry for
`patch_pixelcoat_flappahs_signs.py`.

    python patch_pixelcoat_flappahs_release.py
"""
import pathlib

PX = pathlib.Path(__file__).resolve().parent.parent / "pixelcoat"

HEAD = "# Changelog\n\n"
ENTRY = '''## [0.58.0] - a gas station and a convenience store are FLAPPAHS

**The walker, 2026-10-06:** "Flappahs store always Flappahs". Zoo builds
every station's pumps, pylon, coffee island and slush machine in the brand,
so one brand per site means the fascia says it too.

- **`delco_1997` had no FLAPPAHS.** It is the theme nearly every brief
  names, and its `gas_station` family was GOOSE MART, QUIK KORNER and
  LUBE-N-GO. Cold run 9165 dealt the Flappahs store, then `gas_station_a03`,
  LUBE-N-GO (`b0=lube_n_go` in its log).
- **The entry is copied from `delco`**, where the walker named it on
  2026-09-26. Its families are `convenience` and `gas_station`, not
  `default`, which would re-deal every unbranded building's fascia.
- **In both profiles the two families name FLAPPAHS alone.**
  - The fuel price board (0.34.0) stays in `gas_station`.
  - It is not a business name, and Level Factory 0.146.0 deals only names.
  - Without that, the pool would be FLAPPAHS and the board, picked by hash.
    Measured with Level Factory's own dealing before its fix: a generated
    gas station standing alone drew the board.
- **The names that left keep a home.** GOOSE MART keeps `default` and
  LUBE-N-GO keeps `auto`. QUIK KORNER's only families were these two, so it
  joins `retail`.
- **Cost: retail re-deals.** Retail's pool grows from 5 to 6 in both
  profiles, and Level Factory picks by a hash modulo the pool's size. Most
  retail buildings are dealt a different name than before. A retail fascia
  that differs across this version is a re-deal, not a change in the
  building.

**Tests.**
- `tests/test_flappahs_signs.py` (5): in each profile, the two families name
  only FLAPPAHS, and `delco_1997` has it.
- All 5 fail on 0.57.0's profiles.
- **The suite:** 645 passed.

'''


def main():
    version = PX / "VERSION"
    changelog = PX / "CHANGELOG.md"
    v = version.read_bytes()
    assert v == b"Pixelcoat 0.57.0", v
    c = changelog.read_bytes()
    assert b"\r\n" not in c
    text = c.decode("utf-8")
    assert text.startswith(HEAD + "## [0.57.0] - "), text[:60]
    version.write_bytes(b"Pixelcoat 0.58.0")
    changelog.write_bytes((HEAD + ENTRY + text[len(HEAD):]).encode("utf-8"))
    print("Pixelcoat 0.58.0: VERSION and CHANGELOG")


if __name__ == "__main__":
    main()
