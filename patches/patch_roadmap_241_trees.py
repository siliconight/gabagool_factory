"""Roadmap 241, 2026-10-14: street trees built and proven -- Lot 0.123.0, Level Factory 0.205.0 and cold run 9294.
The status stays NARROWED; its Left clause loses "tree pits" and gains 9294's frames, and one body paragraph is
added after heights by cause. The index is NOT touched here: run `python tools/roadmap_status.py --write` then
`--check`.

    python patches/patch_roadmap_241_trees.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

LEFT_OLD = ("Left: the walker's eye on 9287's, 9289's and 9292's frames (`ab_9287/ab_sheet.png`, `ab_9289/ab_sheet.png`, "
            "`ab_9292/skyline_sheet.png`); the frontage; tree pits; the penthouse,")
LEFT_NEW = ("Street trees built: Lot 0.123.0 (4e4859f) plants an urban street's sidewalks every 30 ft, each block's row "
            "centred between corners kept 30 ft clear -- Philadelphia's own siting guidelines, read at source "
            "(`docs/reference/STREET_TREES.md`) -- and Level Factory 0.205.0 (e13306a) writes `streetscape` into the "
            "site spec so Lot knows; cold run 9294 (0 interventions, seed_9104 named against 9292's) stood 46 trees "
            "where 9292 stood 19, the pick held at PASS 100 and every fight moved with the furniture while no spawn "
            "did, priced at +28.6 draws a heading and a p95 within its 0.10 ms floor "
            "(`docs/findings/urban_street/ab_9294/`). Left: the walker's eye on 9287's, 9289's, 9292's and 9294's frames "
            "(`ab_9287/ab_sheet.png`, `ab_9289/ab_sheet.png`, `ab_9292/skyline_sheet.png`, `ab_9294/ab_sheet.png`); "
            "the frontage; the penthouse,")
BODY_ANCHOR = "memory identical -- the same ten blocks, reordered.\n\n"
BODY_NEW = BODY_ANCHOR + (
    "**STREET TREES, 2026-10-14** (`docs/reference/STREET_TREES.md`; `docs/findings/urban_street/street_counts.py`, "
    "`fight_fields.py`; `patches/patch_lot_urban_street_trees.py`, `patch_lf_streetscape_in_spec.py`; "
    "`docs/cold_runs/cold_9294/`). The comps show street trees in pits along both sidewalks; Lot planted them halfway "
    "between lamps 25 m apart, a Delco strip's spacing. Philadelphia's siting guidelines (PHS / TreeVitalize, 2010) "
    "say 15 to 30 ft between trees and 30 ft from a corner. Lot 0.123.0 plants an urban street every 30 ft, each "
    "block's row centred between its corners; a strip plants as before (the picked jobs of 9278 to 9287 replayed, "
    "0 of 420 files moved). Level Factory 0.205.0 writes `streetscape: \"urban\"` into the site spec, where the "
    "compose stage had kept its decision to itself. Cold run 9294 (0 interventions; seed_9104 named against 9292's): "
    "trees 19 -> 46, the through road's kerbs 5 -> 14 and 6 -> 18 at 9.14 m but across a side street's corners; "
    "the bus stop's kit and 4 of the 12 utility poles stepped round the new grates and crowns. Every enemy and crew "
    "spawn stood at 9292's transform and every fight moved: shots blocked rose on all three candidates (202 -> 267, "
    "409 -> 501, 211 -> 347), and seed_9003's crew lost nobody, held below PASS by TRIVIAL_ENCOUNTER (90 -> 89), a "
    "verdict the pick shows and does not count; seed_9104 held at PASS 100. Laser Tag 0.32.0's one change logged "
    "nothing in 9294's 75 runs. Priced against 9292 at 53 headings: draws +28.6 a heading on the mean (39 up, 9 "
    "down), p95 +0.02 ms against a 0.10 ms floor, memory identical. Corrected while writing it up: Lot 0.123.0's "
    "changelog and its `urban_tree_stations` docstring say a tree steps clear of a cut; one whose station is within "
    "0.8 m of a cut is dropped, not stepped (`site_furniture._nudged`) -- queued for the next Lot change.\n\n")


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "STREET TREES, 2026-10-14" not in text, "already applied"
    for old in (LEFT_OLD, BODY_ANCHOR):
        assert text.count(old) == 1, ("anchor not found once", text.count(old), old[:60])
    h = text.find("\n\n**241. ")
    s = text.rfind("\n\n*STATUS:", 0, h)
    assert s < text.find(LEFT_OLD) < h, "the Left clause is not 241's status"
    e = text.find("\n\n*STATUS:", h)
    assert h < text.find(BODY_ANCHOR) < e, "the body anchor is not 241's"
    for line in BODY_NEW.splitlines():
        assert not re.match(r"\*\*\d+\.", line), ("a body line would parse as an item", line[:40])
    text = text.replace(LEFT_OLD, LEFT_NEW).replace(BODY_ANCHOR, BODY_NEW)
    h = text.find("\n\n**241. ")
    s = text.rfind("\n\n*STATUS:", 0, h)
    assert text[s + 2:].startswith("*STATUS: NARROWED 2026-10-13 -- steps 2 and 3's first cut"), "241's status moved"
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 241: street trees; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    main()
