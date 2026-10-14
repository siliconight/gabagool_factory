"""Roadmaps 248 and 156, 2026-10-14: Patina 0.31.0, a prop is not the building -- replayed over every Deli Counter
shell and proven by cold runs 9305, 9306 and 9307.

- 248: OPEN -> CLOSED, the evidence in the status; one body paragraph after WHAT WOULD CLOSE IT, at the end.
- 156: its Left loses 248.

The index is NOT touched here: run `python tools/roadmap_status.py --write` then `--check`.

    python patches/patch_roadmap_248_closed.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

S156_OLD = "Left: Patina's front dressing read off the stack (248); what closes this,"
S156_NEW = ("Its front dressing, which Patina had read off the stack, back on the wall by Patina 0.31.0 (248, CLOSED). "
            "Left: what closes this,")

S248_OLD = (
    "*STATUS: OPEN 2026-10-14 -- FOUND BY THE FIRE ESCAPE'S COLD RUN, 9303. Patina reads a prop Deli Counter "
    "stands proud of a wall as the building's front, and moves that front's coping, base course and curbs onto the "
    "prop's greybox box, 1.34 m off the wall: the fire escape (Deli Counter 0.220.0), the awning (0.219.0, since "
    "cold run 9297) and the rowhome's stoop (0.211.0, since 9271) each do it. The fix is Patina's: a `prop` slot is "
    "not structure.*")
S248_NEW = (
    "*STATUS: CLOSED 2026-10-14 -- PATINA 0.31.0 (2279f04): A PROP IS NOT THE BUILDING. `surfaces.classify` leaves "
    "a slots.json's `prop` slots out of the building's bounds and never reads their faces as exterior wall or roof. "
    "Replayed over all 158 Deli Counter shells with the dressing job's own command, 0.30.0 twice the control and "
    "byte-identical: 118 unchanged; 29 moved their dressing back onto the building -- five walk-ups, four corner "
    "blocks, twelve rowhomes, seven gas stations and twin_a01; 11 moved only Patina's styled GLB, which no package "
    "carries, each attributed. Cold runs, 0 interventions each and nothing the graders read moved: 9305 "
    "(urban_row_001) ordered no dressing off any wall where 9304 had 3 a walk-up and 12 and 18 on the corner "
    "blocks, priced at +2.0 draws a heading with the p95 inside 0.06 ms; 9306 (restaurant_row_001) stood every "
    "rowhome's front dressing on its wall; 9307 (gas_block_001) moved all 180 of the gas station's coping strips, "
    "base courses and curbs off the canopy's and the pad's edges onto the building, its grades exactly 9281's "
    "(`docs/findings/patina_props/`).*")

B248_ANCHOR = ("**WHAT WOULD CLOSE IT:** a cold run whose walk-ups', corner blocks' and rowhomes' fronts carry their "
               "dressing on the wall again and none off it, every other shell's dressing unchanged or each change "
               "attributed.\n")
B248_NEW = B248_ANCHOR + (
    "\n**FIXED, 2026-10-14** (`docs/findings/patina_props/`: `replay.py`, `glb_only_roles.py`, "
    "`roofline_9304_9305.png`; `patches/patch_patina_props_not_walls.py` and `patina_props_not_walls/`; "
    "`docs/cold_runs/cold_9305/`, `cold_9306/`, `cold_9307/`). **Patina 0.31.0** (2279f04): `classify(..., props=)` "
    "leaves the named meshes out of the bounds and never lets their faces read as exterior wall or roof, their other "
    "roles kept and a hint still winning; `SlotManifest.prop_ids()` names a slots.json's props and the CLI hands "
    "them over. Not forced to trim, as `_ROLE_MAP` reads a prop for tinting: that would retint the library's 9,933 "
    "prop slots, nearly all indoors, for nothing this needs. Its test fails on 0.30.0 and, on three real shells, "
    "finds the anchors with the props named equal to the anchors with them taken away. **The replay** ran every "
    "Deli Counter shell through the dressing job's own command in three arms, 0.30.0 twice as the control: 474 runs, "
    "the control byte-identical, 118 shells unchanged, 29 moving their dressing -- the only output a package "
    "carries -- and 11 only Patina's styled GLB (a rooftop unit's or a garage column's top no longer roof, and "
    "harbor_score, all props, finding its roof). **Found by it:** the gas stations' forecourt -- pad, canopy, "
    "columns, pumps -- is prop slots, and stood as the building's face; when it became so is not traced. **The "
    "cold runs:** 9305 (urban_row_001, against 9304): no dressing order off any wall, where 9304 had 3 on each "
    "walk-up and 12 and 18 under the corner blocks' awnings; gs_midrise_a's coping 37 -> 48; +2.0 draws a heading, "
    "p95 inside 0.06 ms. 9306 (restaurant_row_001): all twelve rowhomes' anchors on their walls. 9307 "
    "(gas_block_001, against 9281 a day earlier): every one of the gas station's 180 coping strips, base courses "
    "and curbs had stood off the building and none now does, the building carrying its own for the first time; the "
    "grades exactly 9281's. **Seen:** the coping back along the walk-ups' front parapets; the corner blocks' and the "
    "forecourt's change does not show from across the street at night, so the orders are their evidence. **For the "
    "walker:** a roofline is 2.0 m strips every 2.5 m with gaps, not one coping -- how every face has always read.\n")


def _span(text, number):
    h = text.find("\n\n**%d. " % number)
    assert h > 0, ("no item", number)
    s = text.rfind("\n\n*STATUS:", 0, h)
    e = text.find("\n\n*STATUS:", h)
    return s, h, (e if e > 0 else len(text))


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "**FIXED, 2026-10-14** (`docs/findings/patina_props/`" not in text, "already applied"
    for old in (S156_OLD, S248_OLD, B248_ANCHOR):
        assert text.count(old) == 1, ("anchor not found once", text.count(old), old[:60])
    s, h, e = _span(text, 156)
    assert s < text.find(S156_OLD) < h, "156's status is not where it was read"
    s, h, e = _span(text, 248)
    assert text[s + 2:h] == S248_OLD, "248's status is not where it was read"
    assert h < text.find(B248_ANCHOR) < e, "248's body anchor is not in 248"
    for block in (S156_NEW, S248_NEW, B248_NEW):
        for line in block.splitlines():
            assert not re.match(r"\*\*\d+\.", line), ("a body line would parse as an item", line[:40])
    text = text.replace(S156_OLD, S156_NEW).replace(S248_OLD, S248_NEW).replace(B248_ANCHOR, B248_NEW)
    for number, head in ((156, "*STATUS: NARROWED 2026-10-14 -- A FIRE ESCAPE STANDS"),
                         (248, "*STATUS: CLOSED 2026-10-14 -- PATINA 0.31.0 (2279f04)"),
                         (249, "*STATUS: OPEN 2026-10-14 -- FOUND ATTRIBUTING COLD RUN 9304'S PACKAGE")):
        s, h, e = _span(text, number)
        assert text[s + 2:].startswith(head), (number, "status does not adjoin its heading", text[s + 2:s + 80])
        assert "\n\n" not in text[s + 2:h], (number, "a blank line inside the status")
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 248 CLOSED, 156's Left updated; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    main()
