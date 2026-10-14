"""Roadmap 241, 2026-10-13: steps 2 and 3's first cut built, proven and priced -- Level Factory 0.200.0 (65cf5e7),
cold run 9287, `docs/findings/urban_street/`; and the walker's word on step 1's frames. The status stays
NARROWED and gains the cut's evidence ahead of what it had, with its Left re-written; one body paragraph is
added at the item's end. The index is NOT touched here: run `python tools/roadmap_status.py --write` then
`--check`.

    python patches/patch_roadmap_241_urban_street.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUS_OLD = "*STATUS: NARROWED 2026-10-13 -- step 1's first cut built:"
STATUS_NEW = (
    "*STATUS: NARROWED 2026-10-13 -- steps 2 and 3's first cut built, proven and priced: Level Factory 0.200.0 "
    "(65cf5e7) reads `streetscape: \"urban\"` off the brief and stands the far side as a continuous wall of the "
    "mid-rise Empties, every other brief byte for byte the strip; cold run 9287 (urban_row_001, "
    "restaurant_row_001's brief plus the field, 0 interventions) stood 8 or 9 mid-rises a candidate, themed, "
    "seed_9104 picked at PASS 90 as 9285; priced against 9285's package at 53 headings, draws -71.6 a heading "
    "on the mean, p95 -0.15 ms at the median (floor 0.03), video memory +19.0 MiB, all of it buffers "
    "(`docs/findings/urban_street/`). The walker on step 1's frames: \"general scale looks fine for that "
    "specific building type\". Step 1's first cut built:")

LEFT_OLD = ("Left: the walker's eye on the frames; the penthouse, corner-shop and bay-window variants, each a "
            "capability Deli Counter lacks; Lot's urban layout; Level Factory's brief field; Lux's dusk haze; "
            "the price.*")
LEFT_NEW = ("Left: the walker's eye on 9287's frames (`ab_sheet.png`); the NEAR side -- the mission's buildings "
            "among mid-rise Empties, no plate between them, which meets what Lot lays after the roads; heights by "
            "cause; the frontage; tree pits; the penthouse, corner-shop and bay-window variants, each a capability "
            "Deli Counter lacks; Lux's dusk haze; the window rhythm and the detail the walker left open.*")

BODY_ANCHOR = ("the plain parapet, the 5-12 storey range against the comps' 12-15 far blocks.\n\n"
               "*STATUS: NARROWED 2026-10-12 -- the pin fixed in Laser Tag")
BODY_NEW = (
    "the plain parapet, the 5-12 storey range against the comps' 12-15 far blocks.\n\n"
    "**STEPS 2 AND 3, THE FIRST CUT, 2026-10-13** (`docs/findings/urban_street/`; "
    "`patches/patch_lf_streetscape_urban.py`; `docs/cold_runs/cold_9287/`). The walker, after step 1's frames: "
    "\"general scale looks fine for that specific building type\" -- the heights and widths stand; the window "
    "rhythm, the look and the detail stay open -- and then \"go ahead with the census, then 241\". **Level "
    "Factory 0.200.0:** `MissionBrief.streetscape`, whose `\"urban\"` a brief GETS only where a terrace stands "
    "(`streetscape_effective`, the functional signature keyed only then, so no strip brief's lock moves); "
    "`building_library.empties_for_brief` draws an urban brief's Empties from `gs_midrise_*`; "
    "`empties.terrace(continuous=True)` drops the alley every five to eight houses, a road across the far side "
    "the only break; an urban brief over a library without mid-rises says `URBAN_WITHOUT_MIDRISES`. Found on the "
    "way: the adapter's preset list had not learned Deli Counter 0.213.0's `empty_midrise`, and "
    "`test_dc_preset_registry` had been red since, unseen, because nothing ran the suite after that release. "
    "**Cold run 9287** (0 interventions): restaurant_row_001's brief plus the field, the near side's lots 9285's "
    "buildings exactly, 8 or 9 mid-rises across the street a candidate, themed; seed_9104 PASS 90 as before; "
    "findings 117 -> 118, the one more Laser Tag's `LT_MAP_BLIND_MAP` on the third candidate (52-63% of "
    "positions never seen from an enemy spawn, a taller gapless wall the obvious reading, not measured). "
    "**Priced against 9285's package** (`ab_record.sh`: same seed, same near side; 53 headings): draws 807 -> "
    "736 a heading on the mean, p95 -0.15 ms at the median against a 0.03 ms floor, textures 76.0 -> 74.4 MiB, "
    "buffers 47.9 -> 68.6 MiB, video 123.9 -> 142.9 MiB -- the wall draws cheaper than the two dozen rowhomes "
    "it replaced, merged per side, and holds about 19 MiB more, all of it the facades' geometry. **Not this "
    "cut:** the near side (the mission's buildings among mid-rises, no plate between -- it meets Lot's parking, "
    "pads and dumpsters, so it is its own cut), heights by cause, the 2.0 m frontage, tree pits, the corner "
    "shop, the haze.\n\n"
    "*STATUS: NARROWED 2026-10-12 -- the pin fixed in Laser Tag")


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "Level Factory 0.200.0 (65cf5e7)" not in text, "already applied"
    for old in (STATUS_OLD, LEFT_OLD, BODY_ANCHOR):
        assert text.count(old) == 1, ("anchor not found once", text.count(old), old[:60])
    h = text.find("\n\n**241. ")
    s = text.rfind("\n\n*STATUS:", 0, h)
    assert text[s + 2:].startswith(STATUS_OLD), "241's status does not sit directly above its heading"
    assert s < text.find(LEFT_OLD) < h, "the Left clause is not 241's status"
    text = text.replace(STATUS_OLD, STATUS_NEW).replace(LEFT_OLD, LEFT_NEW).replace(BODY_ANCHOR, BODY_NEW)
    h = text.find("\n\n**241. ")
    s = text.rfind("\n\n*STATUS:", 0, h)
    assert text[s + 2:].startswith(STATUS_NEW), "241's status no longer adjoins its heading"
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 241: steps 2-3's first cut; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    main()
