"""Roadmap 228: step F landed (Zoo 1.97.0's tree, Lot 0.110.0's clustered belt), the tallies fixed.

Replaces 228's status block and adds the landing to its body. Each anchor must match exactly
once; nothing is written on a miss. The generated index is regenerated afterwards by
`tools/roadmap_status.py --write`.

    python patches/patch_roadmap_228_step_f.py
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

OLD_STATUS_TAIL = (
    "night shows plainer still. STEP F IS DRAFTED, not landed: Zoo 1.97.0 "
    "(`patches/patch_zoo_backdrop_3.py`, a forking trunk under seven lobes in three forms by the "
    "slot's proportions, 27 pure tests) and Lot 0.110.0 (`patches/patch_lot_tree_belt.py`, six "
    "dims two a form, clusters of 4 to 9 with 5 to 18 m of daylight between, the belt 6 m off "
    "the fence); the renders and the next parkland run judge them.*\n"
)
NEW_STATUS_TAIL = (
    "night shows plainer still. STEP F IS LANDED, not yet seen in a level: Zoo 1.97.0 "
    "(`patches/patch_zoo_backdrop_3.py`), a trunk that flares and forks into three limbs under "
    "ten overlapping lobes, the form by the slot's proportions (a low oak, a round maple, a narrow "
    "elm), 548 triangles, census clean, rendered in `docs/findings/backdrop_kit/tree_forms_1_97_0.png`; "
    "Lot 0.110.0 (`patches/patch_lot_tree_belt.py`), six dims two a form, the belt in clusters of "
    "4 to 9 with 5 to 18 m of daylight between, 6 m off the fence. The two tally lines are fixed "
    "(Lot 0.109.1, Level Factory 0.175.1). A parkland re-run (county_hospital_001 from 9227) "
    "shows the walker the trees and prices them; the borough's seven modules are priced by 9229.*\n"
)
BODY_ANCHOR = (
    "each priced within its controls' spread, the draws a heading +14 to +43. What stands past "
    "the edge now differs by level, as the walker asked; what the trees look like is step F.\n"
)
ADDED = (
    "\n**STEP F LANDED, 2026-10-10.** Zoo 1.97.0 (`backdrop_forms.tree_plan`, `tree_form`): a trunk "
    "cone that flares at the foot and forks into three limb cones, under ten lobes -- one over "
    "each limb's tip pulled a tenth toward the axis, a top lobe whose top is the slot's top, three "
    "fillers at the limbs' height and a lower ring under them whose foot keeps daylight above the "
    "fork -- each lobe a seven-by-four ellipsoid displaced by a sixth of its radius; the form by "
    "h / w (under 1.25 an oak on wide limbs, over 1.6 an elm with steep limbs and tall lobes, "
    "between a maple); the sum fitted to the slot. **The first draft was refuted by its render:** "
    "four lobes at the limb tips and three low fillers read as balloons on sticks; the second "
    "reads as a crown (`docs/findings/backdrop_kit/README.md`). 548 triangles of 800 (1.96.0: "
    "132), census clean, 6 pure tests, suite 4,147. Lot 0.110.0: `TREES` is six dims, two a "
    "form, drawn at random a tree; the near belt in clusters (`TREE_CLUSTER` 4 to 9 at 1.5 to "
    "3 m, `TREE_CLUSTER_GAP` 5 to 18 m), the far belt its one sparse run; `TREE_BELT` from 6 m "
    "(2.5), the roadside's from 4 m; on the 196 x 100 m test plate 265 trees in six modules "
    "where 1.96.0 laid about 600 in three. Lot 0.109.1 and Level Factory 0.175.1 count the "
    "backdrop's pieces by species and by side. **Price before look:** six tree modules a belt "
    "are about twelve more MultiMeshes than three; the parkland re-run measures it against "
    "9227's +14 draws.\n"
)


def main():
    raw = ROADMAP.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF; a CRLF means something changed it"
    text = raw.decode("utf-8")
    assert text.count(OLD_STATUS_TAIL) == 1, text.count(OLD_STATUS_TAIL)
    assert text.count(BODY_ANCHOR) == 1, text.count(BODY_ANCHOR)
    text = text.replace(BODY_ANCHOR, BODY_ANCHOR + ADDED).replace(OLD_STATUS_TAIL, NEW_STATUS_TAIL)
    i = text.index(NEW_STATUS_TAIL)
    assert text[i + len(NEW_STATUS_TAIL):].startswith("\n**228. "), "228's status left its heading"
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 228: step F landed")


if __name__ == "__main__":
    main()
