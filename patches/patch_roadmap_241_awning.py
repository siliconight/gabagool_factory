"""Roadmap 241, 2026-10-14: the corner shop's awning built and proven -- Zoo 1.108.0, Deli Counter 0.219.0, cold run
9297. The status stays NARROWED; its status gains the awning and its Left clause the awning's look at night and
9297's sheet, losing the awning; one body paragraph follows the corner shop's. The index is NOT touched here: run
`python tools/roadmap_status.py --write` then `--check`.

    python patches/patch_roadmap_241_awning.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

LEFT_OLD = ("+4.2 MiB video memory (`docs/findings/urban_street/ab_9295/corner_sheet.png`). Left: the walker's eye on "
            "9287's, 9289's, 9292's, 9294's and 9295's frames (`ab_9287/ab_sheet.png`, `ab_9289/ab_sheet.png`, "
            "`ab_9292/skyline_sheet.png`, `ab_9294/ab_sheet.png`, `ab_9295/corner_sheet.png`), and on the shops' glow "
            "and the corners' heights; the corner shop's awning and sign band;")
LEFT_NEW = ("+4.2 MiB video memory (`docs/findings/urban_street/ab_9295/corner_sheet.png`). Its awning built: Zoo 1.108.0 "
            "(b028d3d) draws a canvas shed in four colours and Deli Counter 0.219.0 (42fe102a) hangs one over each "
            "corner's storefront; cold run 9297 (0 interventions) moved nothing the graders read, +0.7 draws a "
            "heading, its frame time unpriced on a busy machine. Left: the walker's eye on 9287's, 9289's, 9292's, "
            "9294's, 9295's and 9297's frames (`ab_9287/ab_sheet.png`, `ab_9289/ab_sheet.png`, "
            "`ab_9292/skyline_sheet.png`, `ab_9294/ab_sheet.png`, `ab_9295/corner_sheet.png`, "
            "`ab_9297/awning_zoom.png`), and on the shops' glow, the corners' heights and the awning at night, which "
            "unlit barely reads; the awning's price on a quiet machine; the corner shop's sign band;")
BODY_ANCHOR = "and the pharmacy's roof props are not byte-stable from run to run (247).\n\n"
BODY_NEW = BODY_ANCHOR + (
    "**THE AWNING, 2026-10-14** (`patches/patch_zoo_shop_awning.py` and `zoo_shop_awning/`, `patch_dc_shop_awning.py` "
    "and `dc_shop_awning/`; `docs/cold_runs/cold_9297/`). The comps' corner shop stands \"at grade (lit, awning)\", "
    "and the Empties comps list the awning as Zoo's to build. Zoo 1.108.0 draws `shop_awning` from its slot's box "
    "alone: a canvas slope from the wall to a 10 in valance, closed at each end, in four colours as the form, 40 "
    "tris, one mesh and one material, every part closed and none lying on another (the coplanar census reads it "
    "clean, the bollard the control). Deli Counter 0.219.0 hangs one over each corner block's storefront in its "
    "shop's colour -- a deli's red, a bar's black, a laundromat's navy, a grocery's green -- 1.2 m out, sunk 8 mm "
    "into the wall, its valance 0.1 m over the storefront's head, with no collider; its schema carried the new "
    "field from the start, 0.218.0's lesson, and its suite found canvas missing from `material_kind` after the "
    "first build. Cold run 9297 (0 interventions, seed_9104 named): both standing corners hang their awning, and "
    "nothing the graders read moved, 0 of 32 fields on any candidate. Seen from the near sidewalk "
    "(`ab_9297/corner_sheet.png`, `awning_zoom.png`), the awning is a band of dark canvas over the lit storefront "
    "that at night barely reads: the shop's glow is paint and lights nothing, where the comps' awning is lit from "
    "under it. Priced at +0.7 draws a heading in two runs; frame time and memory not priced, the controls "
    "disagreeing with themselves by 0.48 and 1.22 ms with StarCraft II running on the machine.\n\n")


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "**THE AWNING, 2026-10-14**" not in text, "already applied"
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
    print("roadmap 241: the awning; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    main()
