"""Roadmap 226 CLOSED by cold run 9223: the shop band is clear of the lamp.

Replaces 226's status block and adds the proof to its body. Each anchor must match exactly once;
nothing is written on a miss. The generated index is regenerated afterwards by
`tools/roadmap_status.py --write`, never by this script.

    python patches/patch_roadmap_226_9223.py
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

OLD_STATUS = (
    "*STATUS: NARROWED 2026-10-10 -- fixed in Lot 0.106.0, not yet run cold: a lamp or a tree "
    "keeps out of a shop band's span on the kerb it faces and steps to the nearer end of it. "
    "Replayed on cold run 9222's drawn site, one piece of 107 moves, Lamp_2 from station 30.00 "
    "to 25.05. Next: a cold run of restaurant_row_001, framed at the band.*\n"
)
NEW_STATUS = (
    "*STATUS: CLOSED 2026-10-10 -- proven in cold run 9223 (restaurant_row_001, 0 interventions, "
    "0 retries, findings 74 to 74): Lot said `LOT_BAND_KEPT_CLEAR: Lamp_2 would have stood at "
    "station 30.00, in front of a shop band; it stands at 25.05`, the replay's prediction, and "
    "the frame from 9222's station reads SCRAPPLE & SONS DELI whole with the lamp beside the "
    "band (`docs/cold_runs/cold_9223/band_evening.png`).*\n"
)
BODY_ANCHOR = "Owner: Lot.\n"
PROOF = (
    "\n**PROVEN, cold run 9223** (`docs/cold_runs/cold_9223/NOTES.md`), the first run under the "
    "reworked driver: Lot 0.106.0 moved the one lamp the replay said it would and nothing else "
    "(shell 0 of 52, art 0 of 74, findings 74 to 74). The facade right of the band is darker, "
    "its lamp now 5 m left; whether that stretch wants another light is a taste call.\n"
)


def main():
    raw = ROADMAP.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF; a CRLF means something changed it"
    text = raw.decode("utf-8")
    assert text.count(OLD_STATUS) == 1, text.count(OLD_STATUS)
    # "Owner: Lot." ends more than one item; take the one after 226's heading
    h = text.index("**226. ")
    b = text.index(BODY_ANCHOR, h)
    text = text[:b + len(BODY_ANCHOR)] + PROOF + text[b + len(BODY_ANCHOR):]
    text = text.replace(OLD_STATUS, NEW_STATUS)
    i = text.index(NEW_STATUS)
    assert text[i + len(NEW_STATUS):].startswith("\n**226. "), "226's status left its heading"
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 226: CLOSED by cold run 9223")


if __name__ == "__main__":
    main()
