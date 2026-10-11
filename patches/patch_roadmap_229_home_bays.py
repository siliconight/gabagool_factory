"""Roadmap 229: Deli Counter 0.207.1 landed -- a home's room takes a fixture a bay.

Inserts one sentence into 229's status block and appends the record to its body. Each anchor must
match exactly once; nothing is written on a miss, and nothing is written while the RESULT_
placeholder is unfilled. The generated index is regenerated afterwards by
`tools/roadmap_status.py --write`.

    python patches/patch_roadmap_229_home_bays.py
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

RESULT_CENSUS = ("reads 1,071 rows and 4,102 lamps where 0.207.0 read 1,048 and 3,933, the difference the home "
                 "rooms' bays (`docs/findings/fixture_rows/row_census_0207_1.txt`); suite 1,388 passed before "
                 "and after the rebuild")

STATUS_ANCHOR = ("(one per 30 to 40 m2) or bulbs (`docs/cold_runs/cold_9232/rooms_before_after.png`, 9229 "
                 "against 9232). ")
STATUS_ADDED = (
    "Deli Counter 0.207.1 (`patches/patch_dc_home_bays.py`) does it: a home's room takes a fixture a "
    "7 m bay (`_HOME_SPACING`, the guide's \"by room\": one ceiling fixture a room of ordinary size), "
    "one bay keeping its one fixture at its centre byte for byte, a bigger room a grid of bays at the "
    "bays' centres, never on the tile line; the hideout takes two rows of three; the library rebuilt "
    + RESULT_CENSUS + ". "
)
BODY_ANCHOR = "174. Not priced at stations; cheaper than 0.206.1 by count.\n"
BODY_ADDED = (
    "\n**THE HOME'S BAYS, 2026-10-11.** Deli Counter 0.207.1 (`patches/patch_dc_home_bays.py`): "
    "`_rows_for_room`'s home branch lays WOOD's row rule at `_HOME_SPACING` (7 m) instead of returning "
    "one fixture -- as many rows across as the width asks at that spacing, as many fixtures along as "
    "the length, the room's cap thinning as everywhere, the lines at the bays' centres rather than "
    "snapped to a pitch, because a home hangs its fixture from the middle of the room. A room within "
    "one bay is the one fixture at its centre it always was, so a 9 x 7 m living room and a 4 x 5 m "
    "bedroom do not move; the deli's 21 x 16 m hideout, dark at both ends under one troffer in "
    "9232's frames, takes two rows of three 7 m apart. Proven over the furnished library before the "
    "rebuild (`docs/findings/fixture_rows/home_bays_diff_0207_1_draft.txt`): 448 rooms identical, 39 "
    "changed, all in residence buildings and residence-like rooms (a 22 m garage bay keeps its one "
    "line and takes three fixtures along it); the library rebuilt " + RESULT_CENSUS + ". The fixture "
    "is still a troffer: a home's dome or pendant is the species step. Not seen in a level yet; a "
    "residence-heavy brief (apartment_walkup, twin) would show it.\n"
)


def main():
    raw = ROADMAP.read_bytes()
    assert raw.count(b"\r") == 0, "the roadmap is LF; a CR means something changed it"
    text = raw.decode("utf-8")
    assert not RESULT_CENSUS.startswith("RESULT_"), "fill RESULT_CENSUS before applying"
    assert text.count(STATUS_ANCHOR) == 1, text.count(STATUS_ANCHOR)
    assert text.count(BODY_ANCHOR) == 1, text.count(BODY_ANCHOR)
    assert "THE HOME'S BAYS, 2026-10-11" not in text, "already applied"
    text = (text.replace(BODY_ANCHOR, BODY_ANCHOR + BODY_ADDED)
                .replace(STATUS_ANCHOR, STATUS_ANCHOR + STATUS_ADDED))
    i = text.index(STATUS_ADDED)
    j = text.index("\n", i)
    assert text[j:].startswith("\n\n**229. "), "229's status left its heading"
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 229: Deli Counter 0.207.1 landed")


if __name__ == "__main__":
    main()
