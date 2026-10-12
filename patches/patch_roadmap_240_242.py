"""Roadmap 240 and a new 242: the pole line's first two builds proven in cold run 9262, and the
route grade they showed rolling dice on the picked lot. Replaces 240's status block (asserted
once), appends one paragraph to 240's body (before 241's status) and appends item 242 at the end.
The index is NOT touched here: run `python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_240_242.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUS_OLD = ("*STATUS: OPEN 2026-10-11 -- filed, not started. Three comps read and mapped by owner "
              "(`docs/reference/PHILLY_STREET_COMPS.md`); the first three builds named: the utility pole "
              "line and its overhead wires (absent), the rowhouse front (stoop, railings, a dish on the "
              "front), the silver roofs. Level creation, after Zoo 1.102.0's roof profiles land.*")
STATUS_NEW = (
    "*STATUS: NARROWED 2026-10-12 -- the pole line's first two builds shipped and proven in a level, "
    "the walker's four calls of 2026-10-12 built as asked (one side of every street, the full wire set "
    "without house drops, a can every third or fourth pole, a cobra-head on every pole; "
    "`docs/proposals/POLE_LINE_DESIGN.md`). Zoo 1.104.0's `utility_pole` (a 40 ft wood pole, crossarm "
    "and insulators, the cobra-head on a 6 ft arm, a `transformer` form; four draws a pole) and Lot "
    "0.118.0's line (one kerb of every street at 0.61 m from the kerb face, no more than 36 m between "
    "poles, every pole's light at its lens, the band roads' steel lamps gone): cold run 9262, 0 "
    "interventions, 11 poles and 4 cans on the picked lot, both forms built PASS, 13 street lights at "
    "their lenses and lamps (`docs/findings/pole_line/`). Its Laser Tag route read 0.64 where 9261's "
    "read 1.00, and `lt_pole_ab.py` puts that on the lot's furniture rolling two pre-existing snags, "
    "not on the poles (filed as 242). Left: the wires (build 3), frames beside the comps for the "
    "walker's eye, then the rowhouse front and the silver roofs.*")

BODY_240 = """

**THE POLE LINE, BUILDS 1 AND 2, 2026-10-12** (`docs/findings/pole_line/`, cold run 9262). The walker's calls, asked before a line was drawn: one side of every street (not residential only, not both sides), the full wire set without house drops, a transformer can every third or fourth pole, a cobra-head on every pole (not every other; the far kerb keeps no lamps). **Zoo 1.104.0** draws the pole in pure Python (`core/utility_pole_forms.py`) and builds it through `prim_mesh` in four materials: Blender 5.1.1's census 3 builds, 0 coincident pairs; both forms PASS through the kit path at 4 submissions each. It owns the numbers Lot mirrors -- each form's module dims, where the pole stands in its module (0.615 m behind the centre: the cobra-head reaches 2.45 m toward the road and the crossarm 1.22 m away), the lens point, each wire's attachment. **Lot 0.118.0** stands the line: the kerb with less to dodge, runs broken at road crossings so a corner pole stands each side of a junction's mouth, poles stepped off cuts, meters, bands and markers by plan boxes (a tree keeps its crown, a signal 5 m), 0.61 m from the kerb face so the crossarm clears the building line by 1.17 m; every pole's light at its lens, a streetlight anchor as before; a can on the pole the most buildings front. On the four stored site fixtures 18, 20, 15 and 16 steel lamps became 8, 9, 9 and 9 poles with 3 cans each -- the street lights about halve, as the walker's option said. Cold run 9262 stood it in a real drive with 0 interventions; whether the streets read too dark, and how the poles look, is for frames and the walker's eye."""

ITEM_242 = """
*STATUS: OPEN 2026-10-12 -- measured, not started. Cold run 9262's picked candidate (restaurant_row_001 seed_9104) read Laser Tag route completion 0.64 and 29 player-stuck events where 9261 read 1.00 and 9, and `docs/findings/pole_line/lt_pole_ab.py` (the job's own command on copies of both runs' staged projects, both controls identical to their jobs in every field) showed the pole line is not the snag: 9262 without its poles read 0.72, 9261 without its lamps 0.88. Every stuck event stands at one of two places 9261's bot stuck at too -- a kerb face at (-66, -5) and beside a parking meter between two parked cars at (35, -17) -- and none within 1.5 m of a pole.*

**242. Laser Tag's route on a lot swings with any change to its street furniture.** Found by the pole line's first cold run (roadmap 240). On restaurant_row_001's picked lot the route the crew bot completes moved from 1.00 to 0.64 when the street's lamps became poles, and moved nearly as far when the lamps were simply taken away; two arms with neither lamps nor poles read 0.72 and 0.88. The furniture reshapes the navmesh, the navmesh decides which way the bot walks, and two snags that were already on the lot decide how often it sticks. The picker reads route completion right after the majors, so a grade a lamp's removal can move is a grade the furniture rolls: the snags are the defect, not the furniture. **WHAT TO MEASURE FIRST.** What a body meets at each place: at (-66, -5) a kerb face where the navmesh crosses and a capsule may not climb (CLAUDE.md's known tension between the bake's climb and the walking step), and at (35, -17) the gap between a meter on the kerb edge and the car in the bay beside it. **WHAT WOULD CLOSE IT.** Both snags removed by generator rules, and the route on this lot reading the same with and without the furniture arms of `lt_pole_ab.py`.
"""


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "**242. " not in text and "THE POLE LINE, BUILDS 1 AND 2" not in text, "already applied"
    assert text.count(STATUS_OLD) == 1, "240's status not found once"
    text = text.replace(STATUS_OLD, STATUS_NEW)
    h = text.find("\n\n**240. ")
    assert h > 0 and text.count("\n\n**240. ") == 1
    assert text[h - len(STATUS_NEW):h] == STATUS_NEW, "240's status does not sit above its heading"
    nxt = text.find("\n\n*STATUS:", h + 10)
    assert nxt > h and text.find("\n\n**241. ", nxt) > nxt, "241 does not follow 240"
    text = text[:nxt] + BODY_240 + text[nxt:]
    assert text.endswith("\n")
    text = text + ITEM_242
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 240: status and a paragraph; 242 filed; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
