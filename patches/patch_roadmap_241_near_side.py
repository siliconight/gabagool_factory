"""Roadmap 241, 2026-10-13: the near side's cut -- Lot 0.121.0, Level Factory 0.201.0, Deli Counter 0.217.0, cold runs
9288 and 9289. The status stays NARROWED; its Left clause is re-written, and one body paragraph is added after the
first cut's. The index is NOT touched here: run `python tools/roadmap_status.py --write` then `--check`.

    python patches/patch_roadmap_241_near_side.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

LEFT_OLD = ("Left: the walker's eye on 9287's frames (`ab_sheet.png`); the NEAR side -- the mission's buildings "
            "among mid-rise Empties, no plate between them, which meets what Lot lays after the roads; heights by "
            "cause;")
LEFT_NEW = ("The NEAR side's cut built too: Lot 0.121.0 keeps its planners clear of every Empty (10 replayed jobs, "
            "0 files moved), Level Factory 0.201.0 fills the near frontage between the mission's buildings with a "
            "4 m passage beside each, Deli Counter 0.217.0 adds three narrow mid-rises (12.3, 10.3, 6.6 m) for the "
            "6.7-12.7 m rooms cold run 9288 measured; cold run 9289 (0 interventions) stood one or two a candidate "
            "and picked seed_9104 at PASS 100 (`docs/findings/urban_street/ab_9289/`: -38.5 draws a heading, p95 "
            "-0.26 ms, video memory +38.0 MiB against the strip). Left: the walker's eye on 9287's and 9289's frames "
            "(`ab_9287/ab_sheet.png`, `ab_9289/ab_sheet.png`); one candidate's enemy spawns starved by the near "
            "block and the far wall together (`LOT_ENEMY_SPAWN_UNPLACEABLE`, by elimination, the mechanism not "
            "traced); a fresh deal when a room's only fitting block is spent; heights by cause;")

BODY_ANCHOR = ("pads and dumpsters, so it is its own cut), heights by cause, the 2.0 m frontage, tree pits, the corner "
               "shop, the haze.\n\n")
BODY_NEW = (
    BODY_ANCHOR +
    "**THE NEAR SIDE, THE SECOND CUT, 2026-10-13** (`docs/findings/urban_street/`; `patches/patch_lot_blockers_stand.py`, "
    "`patch_lf_urban_near_side.py`, `patch_dc_midrise_narrow.py`; `docs/cold_runs/cold_9288/`, `cold_9289/`). The walker, "
    "asked why the roadmap had stopped: keep going. **Lot 0.121.0** hands every Empty to the planners that keep clear of what "
    "stands (fields, pylons, dumpsters, pads, cover) as an obstacle -- before it they read the mission's buildings only, "
    "harmless while every Empty stood across the road; `lot_replay.py` replayed the picked `lot_assemble` jobs of cold runs "
    "9278-9287 from their own `job.log`, 10 jobs, 0 files moved (the control, two replays, 0). **Level Factory 0.201.0**: "
    "`empties.infill` stands Empties along the near building line between the mission's own buildings, a 4 m passage "
    "(`site_variation.CLEARANCE`) kept beside each, side streets and the service lane never built over. **Cold run 9288 stood "
    "none**: `near_room.py` measured the rooms left -- 12.67, 11.35, 7.33, 6.70 m -- against the narrowest mid-rise's 15.3. "
    "**Deli Counter 0.217.0** grows the capability where it belongs: three narrow mid-rises, 12.30, 10.30 and 6.60 m as "
    "built, every other shell byte-identical. **Cold run 9289** (0 interventions): one or two narrow blocks stand on the near "
    "side a candidate, seed_9104 picked at PASS 100. Priced against the strip over the 52 headings that stood in the same "
    "place (`price_matched.py`; the geometry-derived `longest_sightline` station moved, which `price_glow.py` rightly "
    "refuses): draws -38.5 a heading, p95 -0.26 ms against a 0.12 ms floor, buffers 47.9 -> 83.0 MiB. **Found:** "
    "seed_9205's six enemy spawns found no ground (`LOT_ENEMY_SPAWN_UNPLACEABLE`) and Laser Tag refused the map; by "
    "elimination on its own site spec, the one near-side block and the far wall together -- the search's mechanism not "
    "traced; enemy placement is provisional. And a 6.70 m room stayed open because the deal had spent its one narrow "
    "block.\n\n")


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "THE NEAR SIDE, THE SECOND CUT" not in text, "already applied"
    for old in (LEFT_OLD, BODY_ANCHOR):
        assert text.count(old) == 1, ("anchor not found once", text.count(old), old[:60])
    h = text.find("\n\n**241. ")
    s = text.rfind("\n\n*STATUS:", 0, h)
    assert s < text.find(LEFT_OLD) < h, "the Left clause is not 241's status"
    text = text.replace(LEFT_OLD, LEFT_NEW).replace(BODY_ANCHOR, BODY_NEW)
    h = text.find("\n\n**241. ")
    s = text.rfind("\n\n*STATUS:", 0, h)
    assert text[s + 2:].startswith("*STATUS: NARROWED 2026-10-13 -- steps 2 and 3's first cut"), "241's status moved"
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 241: the near side's cut; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    main()
