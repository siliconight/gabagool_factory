"""Roadmap 241, 2026-10-14: heights by cause built and proven -- Level Factory 0.204.0 and cold run 9292. The status
stays NARROWED; its Left clause loses "heights by cause" and gains 9292's frames, and one body paragraph is added
after the near side's residues. The index is NOT touched here: run `python tools/roadmap_status.py --write` then
`--check`.

    python patches/patch_roadmap_241_heights.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

LEFT_OLD = ("Left: the walker's eye on 9287's and 9289's frames (`ab_9287/ab_sheet.png`, `ab_9289/ab_sheet.png`); heights "
            "by cause; the frontage;")
LEFT_NEW = ("Heights by cause built: Level Factory 0.204.0 (065ab60) stands the urban wall's lowest blocks across from the "
            "action's centre and its tallest toward the plate's farther end, and cold run 9292 (0 interventions, seed_9104 "
            "named against 9291's) read the rank correlation of distance with height at +0.91 to +0.93 against 9291's "
            "+0.40, -0.05 and +0.03, priced at -7.6 draws a heading and a p95 within its 0.04 ms floor "
            "(`docs/findings/urban_street/ab_9292/skyline_sheet.png`). Left: the walker's eye on 9287's, 9289's and "
            "9292's frames (`ab_9287/ab_sheet.png`, `ab_9289/ab_sheet.png`, `ab_9292/skyline_sheet.png`); the frontage;")
BODY_ANCHOR = ("70 m room between b1 and b2; every near-side room on the three candidates holds a block, each left with "
               "less than 6.6 m.\n\n")
BODY_NEW = BODY_ANCHOR + (
    "**HEIGHTS BY CAUSE, 2026-10-14** (`docs/findings/urban_street/wall_heights.py`; `patches/patch_lf_heights_by_cause.py`, "
    "`lf_heights_by_cause/measure_rho.py`; `docs/cold_runs/cold_9292/`). The comps: \"the tallest stand furthest away\". "
    "Until Level Factory 0.204.0 the wall's heights fell where the deal put them -- 9291's seed_9104 stood 16.5, 22.7, "
    "16.5, 32.5, 26.2, 19.6, 13.2, 38.7, 19.8 and 26.2 m west to east. 0.204.0 takes, of the blocks on the bag, the one "
    "whose height is nearest a target that is the shortest design's across from the action's centre (the middle of the "
    "span the spawn, objective and extraction buildings cover) and rises with distance to the tallest's at the plate's "
    "farther end; the heights are read off the shells' collider hulls (`street_line.shell_top`, 13.2 m at four storeys "
    "to 38.7 m at twelve), and every design is still dealt once a bag. On the test street's 120 walls the rank "
    "correlation of distance with height reads a median of +0.03 dealt and +0.82 by cause, measured on a preview of the "
    "code before it was applied. Cold run 9292 (0 interventions; seed_9104 named, since a pick follows the grade -- "
    "roadmap 245): +0.93, +0.92 and +0.91 on its candidates; grades and findings as 9291's. The standard A/B sheet's "
    "elevations crop the wall, so the skyline was shot from behind the near side and from the street tilted up "
    "(`ab_9292/skyline_sheet.png`): low across from the action, rising to both ends. Priced against 9291 at 53 "
    "headings: draws -7.6 a heading on the mean, p95 +0.04 ms against a 0.04 ms floor, memory identical -- the same "
    "ten blocks, reordered.\n\n")


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "HEIGHTS BY CAUSE, 2026-10-14" not in text, "already applied"
    for old in (LEFT_OLD, BODY_ANCHOR):
        assert text.count(old) == 1, ("anchor not found once", text.count(old), old[:60])
    h = text.find("\n\n**241. ")
    s = text.rfind("\n\n*STATUS:", 0, h)
    assert s < text.find(LEFT_OLD) < h, "the Left clause is not 241's status"
    for line in BODY_NEW.splitlines():
        assert not re.match(r"\*\*\d+\.", line), ("a body line would parse as an item", line[:40])
    text = text.replace(LEFT_OLD, LEFT_NEW).replace(BODY_ANCHOR, BODY_NEW)
    h = text.find("\n\n**241. ")
    s = text.rfind("\n\n*STATUS:", 0, h)
    assert text[s + 2:].startswith("*STATUS: NARROWED 2026-10-13 -- steps 2 and 3's first cut"), "241's status moved"
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 241: heights by cause; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    main()
