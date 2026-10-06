"""Level Factory 0.147.0: a band names a shop.

`docs/findings/two_names_one_building/` (2026-10-06): of the 95 library shells
with a door box, the band's pool holds the door's name for 6. The pairings
that read worst all came from one of three rules in `SIGN_FAMILIES` and
`_signs_for`:

  * `civic` MEANT TWO THINGS. Pixelcoat's `civic` family is state-run
    commerce (the Pennsylvania state store, a savings bank); this table sent
    police, courthouse, station, library, clinic and hospital to it, so a
    police station was dealt STATE WINE + SPIRITS.
  * A BUILDING OF NO FAMILY TOOK A `default` SHOP: GOOSE MART, HOAGIE HUT,
    CORNER TAP ... on a museum, a stadium, a funeral home, a train yard, a
    mansion. Cold runs 9171 and 9173 shipped the county hospital as CORNER
    TAP.
  * `club` took the casino and the country club, and `strip` would take a
    strip club, so each wore CLUB VELVET or a retail name over its own neon.

THE RULE NOW. A band is the lit cabinet a SHOP hangs over its street, so a
building gets one only when it reads as a family of shop the theme names. A
building of no family, or of a family the theme names nothing for, stands
with no band -- its door box (Zoo `storefront_names`) or its neon names it,
in its own words. That is the walker's authorship rule applied to a sign: a
thing is there because something caused it (`authorship-guide`).

  * `default` deals nothing, and neither does `none`, the family for a
    building a later key would wrongly claim (`strip_club` before `strip`,
    `parking` before `garage`).
  * The `civic` rows go: police, courthouse, library, clinic, hospital and
    `station` now read `default`.
  * `club` and `casino` go; `strip_club` reads `none`.
  * The Flappahs stores by other names: `fuel` and `corner_station` read
    `gas_station` (`fuel_stop_heist`, `gs_corner_station`: pumps and canopy),
    `stop_n_go` reads `convenience` (no pumps; the store's rooms). Each door
    already says FLAPPAHS (Zoo `storefront_names`: gas, fuel, gs, stop).

Named shops -- bank, deli, market, pawn, brewery, pharmacy, pizza, card,
video -- keep a band whose name differs from their door's. That is option A
or B in the finding, and the walker's call.

    python patch_lf_a_band_names_a_shop.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
LF = ROOT / "level_factory"

EDITS = {
    LF / "apps/cli/commands/__init__.py": [
        ('''SIGN_FAMILIES = (
    ("bank", "bank"), ("credit_union", "bank"), ("pawn", "pawn"),
''',
         '''SIGN_FAMILIES = (
    # A band names a shop (0.147.0). `none` stops a building a later key
    # would wrongly claim: a strip club is not `strip` retail (its neon and
    # door name it), a parking garage is not an `auto` repair shop.
    ("strip_club", "none"), ("parking", "none"),
    ("bank", "bank"), ("credit_union", "bank"), ("pawn", "pawn"),
'''),
        ('''    ("brewery", "liquor"), ("distillery", "liquor"), ("bar", "bar"),
    ("club", "club"), ("casino", "club"),
''',
         '''    ("brewery", "liquor"), ("distillery", "liquor"), ("bar", "bar"),
'''),
        ('''    ("gas_station", "gas_station"), ("gas", "gas_station"),
    # the Flappahs store (0.146.0), before `store` reads it as retail
    ("convenience", "convenience"),
''',
         '''    ("gas_station", "gas_station"), ("gas", "gas_station"),
    # the stations by other names (0.147.0): `fuel_stop_heist` and
    # `gs_corner_station` stand pumps and a canopy, and their doors already
    # say FLAPPAHS
    ("fuel", "gas_station"), ("corner_station", "gas_station"),
    # the Flappahs store (0.146.0), before `store` reads it as retail;
    # `stop_n_go` is one too (0.147.0: no pumps, the store's rooms)
    ("convenience", "convenience"), ("stop_n_go", "convenience"),
'''),
        ('''    ("store", "retail"), ("pharmacy", "retail"), ("laundr", "retail"),
    ("courthouse", "civic"), ("police", "civic"), ("station", "civic"),
    ("library", "civic"), ("clinic", "civic"), ("hospital", "civic"),
)
''',
         '''    ("store", "retail"), ("pharmacy", "retail"), ("laundr", "retail"),
)
#: The families that deal no band (0.147.0): a building of no shop family,
#: and one stopped on purpose. Until 0.147.0 `default` dealt GOOSE MART,
#: HOAGIE HUT, CORNER TAP ... to whatever matched nothing -- a museum, a
#: stadium, the county hospital (cold runs 9171, 9173).
NO_BAND = frozenset(("default", "none"))
'''),
        ('''    THE PRESET, NOT THE WORD. `sign_family` reads substrings, and `station`
    is civic: read raw, a `service_station` wore a civic name and a
    `mini_mart` a default one.''',
         '''    THE PRESET, NOT THE WORD. `sign_family` reads substrings, and until
    0.147.0 `station` was civic: read raw, a `service_station` wore a civic
    name and a `mini_mart` a default one.'''),
        ('''    named = [s for s in profile if s.get("text")]
    for i, b in enumerate(buildings):
        family = sign_family(b.get("archetype") or b.get("id"))
        pool = [s for s in named if family in (s.get("families") or [])]
        if not pool:
            pool = [s for s in named if "default" in (s.get("families") or [])]
        if not pool:
            continue
''',
         '''    named = [s for s in profile if s.get("text")]
    for i, b in enumerate(buildings):
        family = sign_family(b.get("archetype") or b.get("id"))
        if family in NO_BAND:
            continue
        # A family the theme names no shop for stands with no band, rather
        # than borrowing a `default` shop's name (0.147.0).
        pool = [s for s in named if family in (s.get("families") or [])]
        if not pool:
            continue
'''),
    ],
    LF / "tests/unit/test_signs_in_site_spec.py": [
        ('''def test_a_station_and_a_store_wear_flappahs_never_the_price_board():
''',
         '''#: Every library family that is not a shop (0.147.0), from
#: `docs/findings/two_names_one_building/`: institutions, landmarks, the
#: businesses whose own sign names them, and homes.
_NOT_SHOPS = (
    "07_police_station", "courthouse_a01", "rail_station_a01", "train_yard_a01",
    "clinic_a01", "county_hospital", "airport_terminal_a01", "arena_a01",
    "stadium_a01", "museum_a01", "funeral_home_a01", "casino_a01",
    "country_club_a01", "strip_club_a01", "mansion_a01", "twin_a01",
    "apartment_walkup_a01", "office", "parking_garage_a01", "landmark_hall_a01",
    "marina_a01", "construction_site_a01",
)


def test_a_band_names_a_shop():
    """0.147.0. Until it, a police station was dealt STATE WINE + SPIRITS
    (`civic` meant state-run commerce in Pixelcoat), the county hospital
    CORNER TAP (cold runs 9171, 9173), a casino CLUB VELVET (9179)."""
    ws = _Workspace()
    for archetype in _NOT_SHOPS:
        rows = [{"id": "b", "archetype": archetype}]
        assert cmds._signs_for(ws, rows, Path("/px/out"), "delco_1997") == {}, archetype


def test_a_shop_still_takes_a_band_of_its_own_family():
    ws = _Workspace()
    for archetype, family in (("bank_branch_a02", "bank"), ("deli_a01", "deli"),
                              ("strip_retail_a01", "retail"),
                              ("self_storage_a01", "warehouse"),
                              ("auto_shop_a01", "auto")):
        signs = cmds._signs_for(ws, [{"id": "b", "archetype": archetype}],
                                Path("/px/out"), "delco_1997")
        slug = Path(signs["b"]).name[len("sign_"):]
        profile = {s["slug"]: s for s in cmds._sign_profile(ws, "delco_1997")}
        assert family in profile[slug]["families"], (archetype, slug)


def test_every_flappahs_door_wears_flappahs():
    """0.147.0: the stations and the store by other names. Each door already
    said FLAPPAHS (Zoo `storefront_names`); the band said a civic or default
    name."""
    ws = _Workspace()
    for archetype in ("gs_corner_station", "fuel_stop_heist", "stop_n_go",
                      "cr_gas", "gas_street", "gas_station_a01",
                      "convenience_store_a01"):
        signs = cmds._signs_for(ws, [{"id": "b", "archetype": archetype}],
                                Path("/px/out"), "delco_1997")
        assert Path(signs["b"]).name == "sign_flappahs", (archetype, signs)


def test_a_station_and_a_store_wear_flappahs_never_the_price_board():
'''),
        ('''                         ("go_go_bar", "club"),
                         ("county_hospital", "civic")):
''',
         '''                         # 0.147.0: a strip club's neon names it, and a
                         # hospital is no shop -- neither takes a band
                         ("go_go_bar", "none"),
                         ("county_hospital", "default")):
'''),
        ('''def test_an_archetype_reads_as_a_family_of_business():
    assert cmds.sign_family("bank_branch_a02") == "bank"
''',
         '''def test_an_archetype_reads_as_a_family_of_business():
    assert cmds.sign_family("strip_club_a01") == "none"      # not `strip` retail
    assert cmds.sign_family("parking_garage_a01") == "none"  # not an `auto` shop
    assert cmds.sign_family("bank_branch_a02") == "bank"
'''),
    ],
}


def main():
    staged = {}
    for path, pairs in EDITS.items():
        data = path.read_bytes()
        crlf = data.count(b"\r\n")
        assert crlf in (0, data.count(b"\n")), f"{path}: mixed line endings"
        eol = "\r\n" if crlf else "\n"
        text = data.decode("utf-8")
        for old, new in pairs:
            old, new = old.replace("\n", eol), new.replace("\n", eol)
            n = text.count(old)
            assert n == 1, f"{path}: anchor matched {n} times: {old[:70]!r}"
            text = text.replace(old, new)
        staged[path] = text
    for path, text in staged.items():
        path.write_bytes(text.encode("utf-8"))
        print("patched", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
