"""Roadmap 244, 2026-10-13: read at source (`docs/reference/CURB_RAMPS.md`), and the item's premise corrected --
a 1997 Philadelphia street could meet its marked crosswalks with full kerbs. Replaces 244's status (asserted
once, still directly above its heading) and appends one paragraph to its body, at the end of the file. The
index is NOT touched here: run `python tools/roadmap_status.py --write` then `--check`.

    python patches/patch_roadmap_244_grounded.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

S244_OLD = ("*STATUS: OPEN 2026-10-12 -- found, not started. On cold run 9262's lot (seed_9104) 25 % of the "
            "crosswalks' kerb ends are dropped (11.80 of 48.00 m); the rest of each walk meets a full kerb.*")
S244_NEW = ("*STATUS: OPEN 2026-10-13 -- grounded, and now a walker's call. On cold run 9262's lot (seed_9104) 25 % "
            "of the crosswalks' kerb ends are dropped (11.80 of 48.00 m). Read at source "
            "(`docs/reference/CURB_RAMPS.md`): today's rule ramps every crosswalk, marked or not, but a 1997 "
            "Philadelphia street not resurfaced since 1992 could meet its crosswalks with full kerbs (Kinney v. "
            "Yerusalim, 3d Cir. 1993). Ramps at every crosswalk, at none, or by street (resurfaced or not) is the "
            "walker's; the ramp's numbers are written down for whichever.*")

BODY_244 = """

**READ AT SOURCE, 2026-10-13** (`docs/reference/CURB_RAMPS.md`). **RETRACTED, KEPT as this item's wording above:** "a marked crosswalk that ends at a full kerb face is not a street anybody built" -- true of a street built under today's rule, not of the game's. Kinney v. Yerusalim (9 F.3d 1067, 3d Cir. 1993) found that Philadelphia had put curb ramps on a sidewalk only where work touched its kerb or the street was rebuilt whole, and held that resurfacing a street is an alteration. So the city had to ramp the intersections of every street resurfaced since January 26, 1992. In 1997, then, a street not resurfaced since 1992 could meet its marked crosswalks with full kerbs, while one that had been would be ramped at its corners -- a mix by cause, still litigated in 2019. **Today's rule** (PROWAG, 2023): a curb ramp or blended transition at every crosswalk, marked or not; running slope at most 1:12 (8.3 %), cross slope 1:48, at least 48 in wide, a 48 x 48 in clear area at the bottom within the crosswalk and out of the travel lanes, a 4 x 4 ft turning space at the top. **The walker's call:** ramps at every crosswalk, at none (the level as it is, but for its road mouths), or by street, a street's resurfacing being a cause a level can carry. No source gives 1997's share of ramped corners, and none is written down here. Whichever is chosen, Lot's kerb model cuts where a crosswalk lands, and the graded lots carry the kerbs: price the change on the graders first (242)."""


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "READ AT SOURCE, 2026-10-13" not in text, "already applied"
    assert text.count(S244_OLD) == 1, "244's status not found once"
    text = text.replace(S244_OLD, S244_NEW)
    h = text.find("\n\n**244. ")
    s = text.rfind("\n\n*STATUS:", 0, h)
    assert h > 0 and text[s + 2:h] == S244_NEW, "244's status does not sit directly above its heading"
    assert text.find("\n\n*STATUS:", h) < 0, "244 is not the last item"
    text = text.rstrip("\n") + BODY_244 + "\n"
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 244: grounded, the premise corrected; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    main()
