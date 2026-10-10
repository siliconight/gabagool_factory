"""Roadmap 229: Deli Counter 0.206.1 landed, the home rule keyed on the room's words.

Replaces one sentence of 229's status block and appends the landing record to its body. Each
anchor must match exactly once; nothing is written on a miss, and nothing is written while the
RESULT_ placeholder is unfilled. The generated index is regenerated afterwards by
`tools/roadmap_status.py --write`.

    python patches/patch_roadmap_229_home_room.py
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

RESULT_CENSUS = "reads 1,140 rows and 4,133 lamps where 0.206.0 read 1,156 and 4,217: ten more rooms take the home's one fixture, 124 single-fixture rows where 114 stood (`docs/findings/fixture_rows/row_census_0206_1.txt`)"

OLD_STATUS = (
    "A residence-like room inside a shop (the deli's apartment hideout) took an office ceiling: the "
    "home rule should key on the room's words too. "
)
NEW_STATUS = (
    "A residence-like room inside a shop (the deli's apartment hideout) took an office ceiling: Deli "
    "Counter 0.206.1 (`patches/patch_dc_home_room.py`) keys the home rule on the room's words too "
    "(`_HOME_WORDS`: apartment, hideout, bedroom, living, flat, bedsit), one fixture at the room's "
    "centre; the library rebuilt " + RESULT_CENSUS + "; cold run 9231 shows it. "
)
BODY_ANCHOR = (
    "The draws are the number to watch as the species grow: every fixture is hardware.\n"
)
BODY_ADDED = (
    "\n**THE HOME RULE KEYED ON THE ROOM, 2026-10-10.** Deli Counter 0.206.1 "
    "(`patches/patch_dc_home_room.py`): `_home_room(r, residence)` is true for a residence building "
    "or for a room whose role or id carries one of `_HOME_WORDS` (apartment, hideout, bedroom, "
    "living, flat, bedsit), and `derive_light_anchors` asks it for the work plane and the row rule, "
    "so the deli's `apartment_hideout` takes one fixture at its centre on the floor plane where "
    "0.206.0 hung three rows of four. The suite's `living_room` case moved to a `back_floor` room so "
    "it still tests the building rule, and one case covers the room rule. Suite 1,379 passed, 2 "
    "skipped; the library rebuilt " + RESULT_CENSUS + ".\n"
)


def main():
    raw = ROADMAP.read_bytes()
    assert raw.count(b"\r") == 0, "the roadmap is LF; a CR means something changed it"
    text = raw.decode("utf-8")
    assert not RESULT_CENSUS.startswith("RESULT_"), "fill RESULT_CENSUS before applying"
    assert text.count(OLD_STATUS) == 1, text.count(OLD_STATUS)
    assert text.count(BODY_ANCHOR) == 1, text.count(BODY_ANCHOR)
    assert "THE HOME RULE KEYED ON THE ROOM, 2026-10-10" not in text, "already applied"
    text = text.replace(BODY_ANCHOR, BODY_ANCHOR + BODY_ADDED).replace(OLD_STATUS, NEW_STATUS)
    i = text.index(NEW_STATUS)
    j = text.index("\n", i)
    assert text[j:].startswith("\n\n**229. "), "229's status left its heading"
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 229: Deli Counter 0.206.1 landed")


if __name__ == "__main__":
    main()
