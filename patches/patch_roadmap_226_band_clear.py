"""Roadmap 226, new: a street lamp stood in front of a shop band (cold run 9222); Lot 0.106.0.

Appends item 226 after item 225's last line. The anchor must match exactly once; nothing is written
on a miss. The generated index is regenerated afterwards by `tools/roadmap_status.py --write`,
never by this script.

    python patches/patch_roadmap_226_band_clear.py
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

END_OF_225 = (
    "- **What it gives up:** a fight between two surfaces within 64 of each other, which a "
    "person can barely see.\n"
)
ITEM = (
    "\n*STATUS: NARROWED 2026-10-10 -- fixed in Lot 0.106.0, not yet run cold: a lamp or a tree "
    "keeps out of a shop band's span on the kerb it faces and steps to the nearer end of it. "
    "Replayed on cold run 9222's drawn site, one piece of 107 moves, Lamp_2 from station 30.00 "
    "to 25.05. Next: a cold run of restaurant_row_001, framed at the band.*\n"
    "\n"
    "**226. A street lamp stood in front of a shop band.** `docs/cold_runs/cold_9222/` "
    "(`band_evening.png`). deli_a01's band read SCRAPPLE & SONS DELI, and a lamp's pole stood "
    "in front of it and hid the E.\n"
    "- **Measured** with Lot's own `sign_placement` and `sign_size` on 9222's drawn site: the "
    "band spans stations 26 to 35 of road 0's left kerb; Lamp_2 stands at 30, 2.46 m in front "
    "of the facade.\n"
    "- **Why:** `site_furniture.plan_furniture` stands a lamp every 25 m and steps it 2 or 4 m "
    "around a marker, and never knew a band was there; the band is hung later, from the spec. "
    "A lamp (6 m) or a tree's crown reaches a band (centre 3.6 m); a hydrant, a post, a meter "
    "or a shelter does not.\n"
    "\n"
    "**Fixed, Lot 0.106.0** (`patches/patch_lot_band_clear.py`): `lot.sign_bands` gives every "
    "dealt band's span from the scene writer's own placement, and the planner keeps lamps and "
    "trees out of each one on the kerb it faces, widened 0.5 m at each end, stepping a piece to "
    "the nearer end and saying `LOT_BAND_KEPT_CLEAR`. With no band it is unchanged piece for "
    "piece. 7 tests, all failing on 0.105.0.\n"
    "\n"
    "Owner: Lot.\n"
)


def main():
    raw = ROADMAP.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF; a CRLF means something changed it"
    text = raw.decode("utf-8")
    assert text.count(END_OF_225) == 1, ("anchor", text.count(END_OF_225))
    assert "**226. " not in text, "item 226 already exists"
    text = text.replace(END_OF_225, END_OF_225 + ITEM)
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 226: filed, NARROWED")


if __name__ == "__main__":
    main()
