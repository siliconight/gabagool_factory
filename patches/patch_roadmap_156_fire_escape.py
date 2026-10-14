"""Roadmaps 156, 241 and 248, 2026-10-14: the fire escape built, proven and priced -- Zoo 1.110.0 and Deli Counter
0.220.0, cold run 9303 -- and what attributing its package found.

- 156: OPEN -> NARROWED, a visual fire escape on the urban street's walk-ups; one body paragraph after WHAT WOULD
  CLOSE THIS.
- 241: a sentence in the status before its Left, the fire escape's sheet added to what the walker has to see; one
  body paragraph after WHAT A PACKAGE CARRIES.
- 248, new, at the end: Patina reads a prop standing proud of a wall as the wall.

The index is NOT touched here: run `python tools/roadmap_status.py --write` then `--check`.

    python patches/patch_roadmap_156_fire_escape.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

S156_OLD = ("*STATUS: OPEN 2026-09-13 (late night) -- FILED FROM THE WALKER'S PHOTO,\n"
            "WITH THE SURVEY OF WHAT EXISTS. Nothing built yet.*")
S156_NEW = (
    "*STATUS: NARROWED 2026-10-14 -- A FIRE ESCAPE STANDS ON THE URBAN STREET'S WALK-UPS, TO BE SEEN AND NOT YET "
    "CLIMBED. Zoo 1.110.0 (c173a8a) draws `fire_escape` a storey a slot -- a slatted landing with 36 in guards and a "
    "22 in flight that switches back, the top landing, the drop ladder -- in black painted steel with no collider; "
    "Deli Counter 0.220.0 (827038a4) stands one on the front of every mid-rise Empty of six storeys or fewer that is "
    "no corner block, on the end bay away from the door. Cold run 9303 (urban_row_001, 0 interventions): six "
    "walk-ups on the picked candidate stand one, 28 storeys from 16 GLBs, nothing the graders read moved, priced at "
    "+3.3 draws a heading and +26 at the worst with the frame time inside its floor (`docs/findings/fire_escape/`). "
    "The closing condition's other half stands too: 241's urban street stands blocks of four to twelve storeys "
    "sharing walls (`walkups_9303_sheet.png`). Left: the merge -- each storey draws on its own, Level Factory's "
    "per-side merge taking slots by name; Patina's front dressing read off the stack (248); what closes this, a fire "
    "escape a body can climb on an enterable walk-up; and the walker's calls: front or back, which buildings, the "
    "colour, how it reads at night.*")

B156_ANCHOR = ("**WHAT WOULD CLOSE THIS:** a cold package with a walk-up whose fire escape a\n"
               "body can climb from the drop ladder to the top landing, on a block where the\n"
               "walker can see two buildings of different heights share a wall.\n")
B156_NEW = B156_ANCHOR + (
    "\n**THE FIRST CUT, VISUAL, 2026-10-14** (`docs/proposals/FIRE_ESCAPE.md`; `docs/findings/fire_escape/`; "
    "`patches/patch_zoo_fire_escape.py` and `zoo_fire_escape/`, `patch_dc_fire_escape.py` and `dc_fire_escape/`; "
    "`docs/cold_runs/cold_9303/`). Roadmap 241's urban street stood the first generated brick walk-ups, so the fire "
    "escape came in on them, to be seen first. **Zoo 1.110.0** (c173a8a) draws `fire_escape` from a slot's box "
    "alone, a storey at a time: `flight_a` and `flight_b`, a landing -- a slatted deck in a frame, a hatch at one "
    "end of its 22 in stair band (2012 IEBC 405.4, as a code forum quotes it), 36 in guards on three sides -- and a "
    "flight rising behind its front guard, `b` reflected so a stack switches back; `top_a` and `top_b`; `drop`. "
    "Black painted steel, one material, no collision; the coplanar census reads it clean over 1,968 sizes. **Deli "
    "Counter 0.220.0** (827038a4) stands one on every mid-rise Empty of six storeys or fewer that is no corner block "
    "(`WALKUP_STOREYS`, CHOSEN: where a walk-up stops before a building takes a lift) -- `gs_midrise_a`, `_b`, `_g`, "
    "`_h` and `_i` -- on the front's end bay away from the door, 1.2 m out, a `prop` slot a storey with no "
    "collider, the drop's foot 2.2 m over the ground floor. **Cold run 9303** (0 interventions, seed_9104 named "
    "against 9302): six walk-ups stand one on the picked candidate, 28 storeys from 16 GLBs, the bake's lightmap "
    "users 3,147 -> 3,175, 0 of 32 summary fields moved on any candidate. Seen (`walkups_9303_sheet.png`): under a "
    "street lamp the stacks read -- landings, switchbacks, the drop -- and black on dark brick nearly disappears "
    "where none lights them. Priced against 9302 at 53 headings: +3.3 draws a heading on the mean, +26 at the "
    "worst, p95 -0.09 ms at the median inside a 0.38 ms floor. **Refuted, the proposal's \"the per-side merge "
    "carries it\":** `merge_empties.gd` takes slots by name and `fire_escape_*` gives no side, so each storey draws "
    "on its own, four to six a walk-up; Level Factory 0.196.0 met the same with the stoop. **Found there:** Patina "
    "moved each walk-up front's coping, base course and curbs onto the stack's greybox boxes, 1.34 m off the wall "
    "(roadmap 248). **Left of this item:** the merge; climbing it, which closes 156; the light well; the walker's "
    "calls.\n")

S241_OLD = ("cold run 9298 (0 interventions) carried 13 of 16, 11.4 MB and 95 baked imports fewer, and moved nothing the "
            "graders read. Left: the walker's eye on 9287's, 9289's, 9292's, 9294's, 9295's and 9297's frames "
            "(`ab_9287/ab_sheet.png`, `ab_9289/ab_sheet.png`, `ab_9292/skyline_sheet.png`, `ab_9294/ab_sheet.png`, "
            "`ab_9295/corner_sheet.png`, `ab_9297/awning_zoom.png`),")
S241_NEW = ("cold run 9298 (0 interventions) carried 13 of 16, 11.4 MB and 95 baked imports fewer, and moved nothing the "
            "graders read. A fire escape built on the walk-ups (roadmap 156): Zoo 1.110.0 (c173a8a) draws it a storey "
            "a slot and Deli Counter 0.220.0 (827038a4) stands one on every mid-rise Empty of six storeys or fewer "
            "that is no corner block; cold run 9303 (0 interventions) stood six on the picked candidate, moved nothing "
            "the graders read, +3.3 draws a heading. Found there (248): Patina has moved the corner blocks' front "
            "dressing onto the awning's greybox box since 9297. Left: the walker's eye on 9287's, 9289's, 9292's, "
            "9294's, 9295's, 9297's and 9303's frames (`ab_9287/ab_sheet.png`, `ab_9289/ab_sheet.png`, "
            "`ab_9292/skyline_sheet.png`, `ab_9294/ab_sheet.png`, `ab_9295/corner_sheet.png`, "
            "`ab_9297/awning_zoom.png`, `docs/findings/fire_escape/walkups_9303_sheet.png`),")

B241_ANCHOR = "Found there and recorded under 247: Lux's applied scene is not byte-stable either.\n"
B241_NEW = B241_ANCHOR + (
    "\n**THE FIRE ESCAPE, 2026-10-14** (roadmap 156 has it whole; `docs/findings/fire_escape/`; "
    "`docs/cold_runs/cold_9303/`). The walker's photo of a brick walk-up asked for one, and the urban street stood "
    "the first walk-ups. Zoo 1.110.0 (c173a8a) draws `fire_escape` a storey a slot in black painted steel; Deli "
    "Counter 0.220.0 (827038a4) stands one on the front of `gs_midrise_a`, `_b`, `_g`, `_h` and `_i` -- six storeys "
    "or fewer, no corner block -- with no collider. Cold run 9303 (0 interventions, seed_9104 named against 9302): "
    "six walk-ups stand one on the picked candidate, and nothing the graders read moved, 0 of 32 fields on any "
    "candidate. Priced at +3.3 draws a heading and +26 at the worst, unmerged, the frame time inside a 0.38 ms "
    "floor. Attributing the package found that Patina reads anything standing proud of a front as the front: the "
    "walk-ups' coping, base course and curbs moved onto the stack's box, and the corner blocks' onto the awning's "
    "since 9297 (roadmap 248).\n")

ITEM_248 = (
    "\n*STATUS: OPEN 2026-10-14 -- FOUND BY THE FIRE ESCAPE'S COLD RUN, 9303. Patina reads a prop Deli Counter "
    "stands proud of a wall as the building's front, and moves that front's coping, base course and curbs onto the "
    "prop's greybox box, 1.34 m off the wall: the fire escape (Deli Counter 0.220.0), the awning (0.219.0, since "
    "cold run 9297) and the rowhome's stoop (0.211.0, since 9271) each do it. The fix is Patina's: a `prop` slot is "
    "not structure.*\n"
    "\n**248. Patina reads a prop standing proud of a wall as the wall.** Found attributing cold run 9303's package "
    "against 9302's (`docs/findings/fire_escape/README.md`, \"Found\"). Patina 0.30.0's `surfaces.classify` calls a "
    "vertical face an exterior wall when its centroid stands within `_BOUNDARY_TOL` (0.25 m) of the visual AABB -- "
    "the box round every visual mesh in the shell GLB -- and the anchor pass stands its roofline, wall-base and "
    "ground-edge anchors on exterior-wall faces only. Deli Counter greyboxes every `prop` slot as a visual box in "
    "that GLB, named by its `slot_id`. **Measured:** gs_midrise_a's front anchors went roofline 12 -> 1, ground edge "
    "8 -> 1 and wall base 4 -> 1 between 9302 and 9303, the one of each at y -8.842, the stack's box face, where the "
    "wall stands at -7.5; Patina then ordered a coping strip at the top landing's top and a base course and a curb "
    "on the sidewalk, all 1.34 m off the wall, on all five walk-ups. The corner blocks' anchors reach -8.842, the "
    "awning's box, in 9302 as in 9303. `gs_empty_rowhome_a`'s front anchors stood at -6.15 in cold runs 9258, 9263 "
    "and 9270 -- ground edge 3, roofline 4, wall base 2 -- and from 9271 at -7.61, the stoop's bottom tread, one of "
    "each. `gs_midrise_c`, standing neither, reads +-7.65 in both runs. **THE FIX** is Patina's. It reads the "
    "shell's `slots.json` before it classifies (`cli.py`), its `_ROLE_MAP` already reads a `prop` slot as trim, and "
    "a mesh is named by its node, which Deli Counter names by the slot's id; `classify` never asks. A prop should "
    "stay out of the box and its faces read as trim. Leaving it out of the box alone would not do: the test accepts "
    "a face standing beyond the boundary, so the stack's face would still read as wall. **WHAT WOULD CLOSE IT:** a "
    "cold run whose walk-ups', corner blocks' and rowhomes' fronts carry their dressing on the wall again and none "
    "off it, every other shell's dressing unchanged or each change attributed.\n")


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
    assert "**248. " not in text, "already applied"
    for old in (S156_OLD, B156_ANCHOR, S241_OLD, B241_ANCHOR):
        assert text.count(old) == 1, ("anchor not found once", text.count(old), old[:60])
    s, h, e = _span(text, 156)
    assert text[s + 2:h] == S156_OLD, "156's status is not where it was read"
    assert h < text.find(B156_ANCHOR) < e, "156's body anchor is not in 156"
    s, h, e = _span(text, 241)
    assert s < text.find(S241_OLD) < h, "241's status is not where it was read"
    assert h < text.find(B241_ANCHOR) < e, "241's body anchor is not in 241"
    assert text.endswith("their hashes.\n"), "the roadmap does not end where it was read"
    for block in (S156_NEW, B156_NEW, S241_NEW, B241_NEW, ITEM_248):
        for line in block.splitlines():
            assert not re.match(r"\*\*\d+\.", line) or line.startswith("**248. "), \
                ("a body line would parse as an item", line[:40])
    text = (text.replace(S156_OLD, S156_NEW).replace(B156_ANCHOR, B156_NEW)
            .replace(S241_OLD, S241_NEW).replace(B241_ANCHOR, B241_NEW)) + ITEM_248
    for number, head in ((156, "*STATUS: NARROWED 2026-10-14 -- A FIRE ESCAPE STANDS"),
                         (241, "*STATUS: NARROWED 2026-10-13 -- steps 2 and 3's first cut"),
                         (248, "*STATUS: OPEN 2026-10-14 -- FOUND BY THE FIRE ESCAPE'S COLD RUN")):
        s, h, e = _span(text, number)
        assert text[s + 2:].startswith(head), (number, "status does not adjoin its heading", text[s + 2:s + 80])
        assert "\n\n" not in text[s + 2:h], (number, "a blank line inside the status")
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 156 NARROWED, 241 one sentence and one paragraph, 248 filed; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    main()
