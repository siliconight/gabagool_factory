"""Level Factory 0.147.0: VERSION and the CHANGELOG entry for
`patch_lf_a_band_names_a_shop.py`.

    python patch_lf_band_release.py
"""
import pathlib

LF = pathlib.Path(__file__).resolve().parent.parent / "level_factory"

ENTRY = '''## [0.147.0] - A band names a shop

**What was measured** (`docs/findings/two_names_one_building/` at the factory
root, 2026-10-06). A building can carry two lit name signs:
- the band Lot hangs on its street face, dealt here from Pixelcoat's sign
  profile;
- the box over its door, which Zoo names from its own table.

Of the 95 library shells with a door box, the band's pool held the door's
name for 6. The pairings that read worst came from three rules here:

- **`civic` meant two things.**
  - Pixelcoat's `civic` family is state-run commerce: the Pennsylvania state
    store, and a savings bank.
  - `SIGN_FAMILIES` sent police, courthouse, station, library, clinic and
    hospital to it.
  - So a police station was dealt STATE WINE + SPIRITS.
- **A building of no family took a `default` shop.** GOOSE MART, HOAGIE
  HUT, CORNER TAP and the rest went on a museum, a stadium, a funeral home,
  a train yard or a mansion. Cold runs 9171 and 9173 shipped the county
  hospital as CORNER TAP.
- **`club` took the casino and the country club.** A casino's band said
  CLUB VELVET over a door naming the casino (9179, `casino_a02`).

**The rule now: a band is the lit cabinet a shop hangs over its street.** A
building gets one only when it reads as a family of shop the theme names.
Anything else stands with no band, and its door box or neon names it in its
own words. This is the walker's authorship rule applied to a sign: a thing is
there because something caused it.

- `default` deals nothing.
- `none` deals nothing either. It is the family for a building a later key
  would wrongly claim: `strip_club` before `strip`, `parking` before
  `garage`.
- The `civic` rows go.
- `club` and `casino` go.
- **The Flappahs stores by other names wear FLAPPAHS.**
  - `fuel` and `corner_station` read `gas_station`: `fuel_stop_heist` and
    `gs_corner_station` both stand pumps and a canopy.
  - `stop_n_go` reads `convenience`: no pumps, and the store's rooms.
  - Each door already said FLAPPAHS.

**Named shops still carry two names.** A bank, deli, market, pawn shop,
brewery, pharmacy, pizzeria, card shop or video store keeps a band whose name
differs from its door's. Making them agree is option A or B in the finding,
and the walker's call.

**Cost: fewer lit bands.** Each library shell was dealt alone on a
street, `delco_1997`, under both versions.
- Under 0.146.0 every one got a band: 148 of 148.
- Under 0.147.0, 68 do.
- **The 80 that lose a band:**
  - institutions and landmarks: the police station, courthouses,
    rail stations, clinics, airport terminals, arenas, stadiums,
    museums, train yards, landmark halls and marinas;
  - the businesses whose own sign names them: casinos, country
    clubs, strip clubs and funeral homes;
  - homes and offices: mansions, the twin, apartment walkups (their
    doors have no storefront box), offices, parking garages and
    construction sites;
  - the twelve Empty shells, five mission specs and the demo specs.
- **Five change their name to FLAPPAHS:** the three
  `fuel_stop_heist` specs, `gs_corner_station` and `stop_n_go`.
- Each band is a lit cabinet, so a night street now has fewer of
  them, and none that names the wrong business.

**Tests** (`tests/unit/test_signs_in_site_spec.py`):
- **3 new:**
  - `test_a_band_names_a_shop`: 22 non-shops are dealt nothing;
  - `test_a_shop_still_takes_a_band_of_its_own_family`: the
    control, which passes on 0.146.0 too;
  - `test_every_flappahs_door_wears_flappahs`: seven stations and
    stores by every name.
- **Two changed:** `strip_club` and `parking` read `none`; a
  generated `go_go_bar` reads `none` and `county_hospital` reads
  `default`.
- On 0.146.0's code, every one of these except the control fails.

**Suite:** 1,963 collected: 1,948 passed, 14 skipped, 1 xfail. That is
0.146.0's 1,960 and the 3 above.

'''


def main():
    for token in ("BANDS_LINE", "TESTS_LINE", "SUITE_LINE"):
        assert token not in ENTRY, f"fill in {token} before applying"
    version = LF / "VERSION"
    changelog = LF / "CHANGELOG.md"
    v = version.read_bytes()
    assert v == b"0.146.0", v
    c = changelog.read_bytes()
    assert b"\r\n" not in c
    assert c.startswith(b"## [0.146.0] - "), c[:60]
    version.write_bytes(b"0.147.0")
    changelog.write_bytes(ENTRY.encode("utf-8") + c)
    print("Level Factory 0.147.0: VERSION and CHANGELOG")


if __name__ == "__main__":
    main()
