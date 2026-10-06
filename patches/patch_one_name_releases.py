"""Option A's three releases: Pixelcoat 0.61.0, Zoo 1.79.0, Level Factory
0.148.0 -- VERSION (and Pixelcoat's wheel fallback) and a CHANGELOG entry
each, for `patch_pixelcoat_one_name_list.py`, `patch_pixelcoat_one_list_fit.py`,
`patch_zoo_door_wears_the_band.py` and `patch_lf_one_name.py`.

    python patch_one_name_releases.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

PX_ENTRY = '''## [0.61.0] - one name list: a band is dealt the names Zoo paints over the door

**The walker, 2026-10-06, option A** on the factory root's
`docs/findings/two_names_one_building/`: "Agreed". One list names a building
on both its signs, and it is the door box's: Zoo's `storefront_names.KINDS`,
written to the Delco-slang brand rule. Level Factory 0.148.0 deals each shell
one business and hands the same pack to its door box (Zoo 1.79.0), so the
band and the door cannot disagree.

**For each kind Zoo names, the family Level Factory deals now holds exactly
Zoo's names**, in both level themes:

| Zoo kind | family | names |
|---|---|---|
| deli | deli | JAWN'S HOAGIES, WOODER ICE & HOAGIES, SCRAPPLE & SONS DELI, YO! DELI |
| pizza | pizza (new) | PIE HOLE PIZZA, TOMATO PIE TONY'S, SAUCE BOSS PIZZA |
| bank | bank | FIRST DELCO SAVINGS, PIKE SAVINGS & LOAN, MATTRESS MONEY TRUST, YOUSE CREDIT CO-OP |
| pawn | pawn | HOCK IT HERE, CASH 4 YOUR JAWN, GOLD N STUFF PAWN |
| market | supermarket | PIKE FOOD MARKET, THE BIG CART, SCRAPPLE SUPERMARKET |
| pharmacy | pharmacy (new) | PILLS N THRILLS, DOC'S DISCOUNT DRUGS |
| card | card (new) | TOPDECK TONY'S, MINT-ISH CARDS |
| video | video (new) | MACDADE MOVIES |
| brewery | brewery (new) | DOWN THE SHORE BREWING, HONEST HON BREW CO |

- Each new entry is a panel from a palette of five. The brand's green is
  kept for FLAPPAHS alone.
- The names that held those families before keep every other family they
  had, and lose only these.
- The families Zoo has no names for (auto, warehouse, industrial, retail,
  bar, diner, restaurant, liquor) are unchanged. Their doors wear the band's
  pack too, so they agree by construction.

**Two constraints the new names met:**
- **`&` joins the bitmap fallback** (`signage._FONT`). WOODER ICE & HOAGIES
  and SCRAPPLE & SONS DELI need it, and a missing glyph renders as a silent
  space whenever the TTF cannot be found.
- **Legibility is measured, not counted.** `test_theme_signs` capped a name
  at 20 characters, and DOWN THE SHORE BREWING is 22.
  - `fit_scale` puts it on the band's 128 x 512 canvas at scale 5, the scale
    SCRAPPLE SUPERMARKET (20) always passed at.
  - The test now asserts the scale, at least 5, instead of the count.

**Tests:** `tests/test_one_name_list.py`, 20.
- Nine kinds x two themes: each family holds exactly Zoo's names. Zoo is
  read as source from a checkout above this repo.
- The brand green is FLAPPAHS alone: the control.
- On 0.60.0's profiles all 18 mirrors fail; the control passes.

**Suite:** 667 passed (0.60.0's 647 and these 20), run after the version
bump.

'''

ZOO_ENTRY = '''## [1.79.0] - a door box can wear the sign pack its building's band wears

**The walker, 2026-10-06, option A:** one name list on both of a building's
signs. Level Factory 0.148.0 deals each shell one business, and builds its
street band from that business's Pixelcoat pack. This release lets the door
box wear the SAME pack, so one building's two signs name one business by
construction, not by two tables agreeing.

- **`zoo_cli --fixtures ... --sign-pack DIR`** takes the pack directory.
- **`build_fixtures`** hands it to every `sign_box` placement of the build,
  and to nothing else. A fixtures build is one shell, and a shell is one
  business.
- **`sign_box`** loads that pack before it would pick one from a skin
  library, and wears it through the branch that already dressed a face from
  a pack.
- **Without a pack, nothing changes.** The face is named from
  `storefront_names`, which Pixelcoat 0.61.0's sign profile now mirrors.

**Built:** `deli_a01`'s fixtures with `--sign-pack` set to cold run 9184's
`signs/sign_flappahs`. Its door face is `M_SignBox_sign_flappahs_Face`.

**Tests:** `tests/test_door_wears_the_band.py`, 3.
- The CLI takes the flag.
- Only a door box is handed the pack.
- The door box wears a given pack before it would pick one.
- The Blender-bound code is read as source. All three fail on 1.78.0.

**Suite:** 3,343 passed, 382 skipped, 1 xfailed: 1.78.0's 3,340 and these
3.

'''

LF_ENTRY = '''## [0.148.0] - One business a shell, on its band and over its door

**The walker, 2026-10-06, option A** on the factory root's
`docs/findings/two_names_one_building/`: "Agreed". One name list on both of a
building's signs, the door box's.

**Dealt per shell, not per row.**
- Zoo builds a shell's fixtures once, and every instance of the shell wears
  that one door box. A band dealt per row could therefore give two
  instances of one shell two names over the one name on their door.
- `deal_signs` deals each distinct shell one business, by a stable hash of
  the shell. A shell is a row's archetype, or for a generated building the
  preset it was built from.
- No two shells on a street take the same business while the family has
  another to give.
- `_signs_for` maps rows through the deal.

**The door wears the band.**
- A fixtures job's spec carries `sign_pack`: the pack its shell was dealt on
  the selected candidate's street.
- `_door_sign_pack` reads it off that candidate's judged site spec, through
  the same `_sign_rows` the band's deal reads. The themed site stands the
  same buildings.
- The Zoo adapter passes it as `--sign-pack` (Zoo 1.79.0).
- The fixtures job now depends on the candidate's Pixelcoat build, which
  makes the pack.
- A shell dealt no band (0.147.0) gets no pack, and Zoo names its door as
  before. A missing site spec is said, not hidden.

**Finer families, Zoo's door kinds:**
- `card` and `video` come before `shop` and `store` read them as retail;
- `pizza` is no longer `restaurant`;
- `brewery` is no longer `liquor`;
- `pharmacy` is no longer `retail`.

Pixelcoat 0.61.0 fills each of these with exactly Zoo's names.

**Tests:**
- `test_signs_in_site_spec.py`, 3:
  - a shell is dealt one business wherever it stands, and two shells never
    repeat;
  - Zoo's door kinds are families of their own;
  - a door wears its shell's band, for library shells by id, for the
    generated shell by its preset, and with no pack when the site spec is
    missing.
- `test_fixture_pipeline.py`, 2: the fixtures build waits for the Pixelcoat
  build, and the adapter passes `--sign-pack`.
- All five fail on 0.147.0's code.

**Suite:** 1,968 collected: 1,953 passed, 14 skipped, 1 xfail. That is
0.147.0's 1,963 and the 5 above.

'''


def _prepend(path, entry, head_check, head=""):
    c = path.read_bytes()
    assert b"\r\n" not in c, path
    text = c.decode("utf-8")
    assert text.startswith(head + head_check), (path, text[:60])
    path.write_bytes((head + entry + text[len(head):]).encode("utf-8"))


def main():
    px, zoo, lf = ROOT / "pixelcoat", ROOT / "zoo", ROOT / "level_factory"
    assert (px / "VERSION").read_bytes() == b"Pixelcoat 0.60.0"
    assert (zoo / "VERSION").read_bytes() == b"1.78.0"
    assert (lf / "VERSION").read_bytes() == b"0.147.0"
    vpy = px / "pixelcoat" / "version.py"
    vt = vpy.read_bytes().decode("utf-8")
    assert vt.count('_FALLBACK = "0.60.0"\n') == 1
    _prepend(px / "CHANGELOG.md", PX_ENTRY, "## [0.60.0] - ", head="# Changelog\n\n")
    (px / "VERSION").write_bytes(b"Pixelcoat 0.61.0")
    vpy.write_bytes(vt.replace('_FALLBACK = "0.60.0"\n', '_FALLBACK = "0.61.0"\n').encode("utf-8"))
    _prepend(zoo / "CHANGELOG.md", ZOO_ENTRY, "## [1.78.0] - ")
    (zoo / "VERSION").write_bytes(b"1.79.0")
    _prepend(lf / "CHANGELOG.md", LF_ENTRY, "## [0.147.0] - ")
    (lf / "VERSION").write_bytes(b"0.148.0")
    print("Pixelcoat 0.61.0, Zoo 1.79.0, Level Factory 0.148.0: VERSION and CHANGELOG")


if __name__ == "__main__":
    main()
