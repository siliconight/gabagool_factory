"""Roadmap 242: the snag found -- not a kerb face but a body pinned at the deli register counter's
corner by Godot Physics -- and the swing mostly the engine's (docs/findings/route_snag/). Replaces 242's
status (asserted once, still above its heading) and appends one paragraph to 242's body, which is the
file's last item but 243. The index is NOT touched here: run `python tools/roadmap_status.py --write`
then `--check`.

    python patches/patch_roadmap_242_snag.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

OLD = ("*STATUS: OPEN 2026-10-12 -- measured, not started. Cold run 9262's picked candidate "
       "(restaurant_row_001 seed_9104) read Laser Tag route completion 0.64 and 29 player-stuck events "
       "where 9261 read 1.00 and 9, and `docs/findings/pole_line/lt_pole_ab.py` (the job's own command on "
       "copies of both runs' staged projects, both controls identical to their jobs in every field) showed "
       "the pole line is not the snag: 9262 without its poles read 0.72, 9261 without its lamps 0.88. Every "
       "stuck event stands at one of two places 9261's bot stuck at too -- a kerb face at (-66, -5) and "
       "beside a parking meter between two parked cars at (35, -17) -- and none within 1.5 m of a pole.*")
NEW = ("*STATUS: NARROWED 2026-10-12 -- the snag found, and it is the physics engine's "
       "(`docs/findings/route_snag/`). Not a kerb face: 64 of 9263's 72 stuck events stand at one point to "
       "fifteen digits inside the deli, at its front register counter's south-west corner, where the bot "
       "-- cutting the corner by its 0.44 m arrival radius -- touches the counter and Godot Physics' "
       "`move_and_slide` takes the floor as every slide's collision and never turns along it; the counter's "
       "collision disabled, it walks off the next tick. The job's command on 9261's, 9262's and 9263's lots "
       "under Godot Physics (each reproducing its job) and under Jolt: player-stuck 9/29/72 against "
       "1/7/7, none at the counter, route 1.00/0.64/0.72 against 1.00/0.76/0.84 -- what is left tracks the "
       "fights. Left: which engine the game, and so the grader, runs (the walker's call); the second place, "
       "beside a meter at (35, -17), unattributed.*")

BODY = """

**THE SNAG, FOUND, 2026-10-12** (`docs/findings/route_snag/`). **The kerb face was a guess, REFUTED and kept above.** The point the bot stuck at is identical to fifteen digits in every run -- a body that never moves, not one wedged anew -- and it stands inside the deli, one body radius west of the front register counter's west end, level with its south face. `snag_trace.py` instruments a copy of the Laser Tag job's staged project (its control: the copy reproduces the job's first stuck event to the float): the crew member, back up from the basement objective and heading for the van, sets full speed toward a path point 0.48 m off, and `move_and_slide` returns six slide collisions a frame, all the deli's floor slab with an upward normal and zero travel. Swapping the slab's trimesh for a box changed nothing; disabling the counter's collision freed it the next tick; the run under Jolt slid along the counter and walked on. Two causes stack: the bot turns toward its next point within its 0.44 m arrival radius (body, a tick at the 4x step, half a cell) where the navmesh's 0.4 m erosion leaves the 0.35 m body 5 cm, so it clips corners; and Godot Physics, given a corner and the floor at once, slides on the floor's normal. `engine_ab.py`, the job's full command on the three runs' lots, under each engine: player-stuck 9/29/72 under Godot Physics, 1/7/7 under Jolt, none at the counter; route 1.00/0.64/0.72 against 1.00/0.76/0.84, the rest following the deaths (26/38/29 under Jolt). **WHAT WOULD CLOSE IT NOW.** The walker's call on the engine the game ships (a package names none; the game's project does), the grader running the same; the place beside the meter at (35, -17) attributed; and the three lots' routes reading within their fights' spread. The first closing condition above, snags removed by generator rules, rested on the refuted guess."""


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "THE SNAG, FOUND, 2026-10-12" not in text, "already applied"
    assert text.count(OLD) == 1, "242's status not found once"
    text = text.replace(OLD, NEW)
    h = text.find("\n\n**242. ")
    assert h > 0 and text.count("\n\n**242. ") == 1
    assert text[h - len(NEW):h] == NEW, "242's status does not sit above its heading"
    nxt = text.find("\n\n*STATUS:", h + 10)
    assert nxt > h and text.find("\n\n**243. ", nxt) > nxt, "243 does not follow 242"
    text = text[:nxt] + BODY + text[nxt:]
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 242: status and a paragraph; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    main()
