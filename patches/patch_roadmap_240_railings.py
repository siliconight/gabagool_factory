"""Roadmap 240, 2026-10-13: the stoops' iron railings built and proven (Zoo 1.105.0, Deli Counter 0.212.0,
Level Factory 0.197.0; cold run 9273; the walker's calls "3 risers, concrete, railings both sides").
Replaces the end of 240's status (asserted once and still directly above its heading) and appends one
paragraph to its body, after the stoops' and before 241's status. The index is NOT touched here: run
`python tools/roadmap_status.py --write` then `--check`.

    python patches/patch_roadmap_240_railings.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

S240_OLD = ("Left: the street lights' shadow cost, the walker's call with that seen; the frames beside the comps "
            "for the walker's eye; the front's iron railings, its dishes and parged fronts; then the roofscape's "
            "rear ells, and the coating when a 1990s source says how common it was.*")
S240_NEW = ("Their iron railings are built, one each side as the walker called them (\"3 risers, concrete, "
            "railings both sides\"): Zoo 1.105.0's `stoop_railing`, Deli Counter 0.212.0, Level Factory 0.197.0; "
            "cold run 9273, 0 interventions, its 117 findings 9272's issue for issue; a body driven sideways off "
            "the landing or the flight stops at a railing where 9272's walks off; +8.0 draws a heading on the "
            "mean, p95 at the 0.12 ms floor in two prices. Left: the graders' breadth with stoops in the lots "
            "(the proposal's step, never run: `engine_breadth.py`'s staged lots predate the stoops); the street "
            "lights' shadow cost, the walker's call with that seen; the frames beside the comps for the walker's "
            "eye; the front's dishes and parged fronts; then the roofscape's rear ells, and the coating when a "
            "1990s source says how common it was.*")

BODY_240 = """

**THE RAILINGS, 2026-10-13** (`docs/cold_runs/cold_9273/`). **The walker's calls:** "3 risers, concrete, railings both sides -- build the railings" -- the proposal's three open calls answered as 0.211.0 had built two of them, and the third an order. **Zoo 1.105.0** (`patches/patch_zoo_stoop_railing.py`): `stoop_railing`, black painted iron in two forms drawn from a slot's box alone -- `level` (a post at each end, the top rail, a bottom rail, 5/8 in pickets at 4 in clear) and `flight` (a post at its low end, the rail from 36 in over the post's foot to the box's top, the pickets sheared to the pitch); one material and one part, no collision, and no face on another's (Blender's census 0 pairs over three corners; `prims.coincident_pairs` none over 60 sizes). The code's numbers where it speaks (IRC R311.7.8.1, 34 to 38 in), though by that code a three-riser stoop needs neither a handrail nor a guard. **Deli Counter 0.212.0** (`patches/patch_dc_stoop_railings.py`): one railing a side in two slots, the flight's rail 34.75 in over the nosing line at its post and 36 at the landing's edge, the way up between them 1.32 m. **5 cm inside the stoop's side, not flush:** flush, a flight's box shared the middle tread's side plane facing the same way over 0.0497 m2, which the composer's z-fight gate -- reading a module as its box -- skips under its 0.05 m2 floor, one deeper tread from a flag. `rot_y` 270, so each flight rises to the house: `godot_basis` (Ry(-t)) turns the module's high end to Godot -Z, and 90 would point it at the street. The colliders are Deli Counter's, in the greybox the graders walk: a box along the landing and a slab under each flight's rail. **Level Factory 0.197.0** (`patches/patch_lf_stoop_railings.py`): the terrace reads `stoop_rail_` as the stoop's -- read with the house, each flight's slab was its street edge, 1.4088 m in front of the facade on all twelve built shells (`patches/lf_stoop_railings/rail_hulls_0196.log`), and the row would have stood that much further back. **Cold run 9273** (0 interventions): findings 117, the same issue ids as 9272's; the composed scenes turn each railing as written; the z-fight gate reads four solids more a rowhome and 0 pairs; the merge took 48 modules into 12 more merged meshes and the bake 23 more users, one iron mesh an Empty. **The walk** (`rail_walk.gd`): on 9272's package a body driven sideways off the landing or the flight walks off and drops to grade; on 9273's it stops 0.312 m on, at the railing, and the climb to the door reads 9272's to the millimetre. **The frames** (`cold_9273/railings.png`): both railings on every stoop in view, each flight rising to its landing. **The price**, against 9272, twice: +8.0 draws a heading on the mean (at most +31); p95 +0.12 and -0.02 ms at the median against a 0.12 ms floor. **RETRACTED, KEPT in the run's notes:** the first price's +2.61 ms at its worst heading -- two headings whose subject passes disagreed by 2.8 and 4.5 ms read +0.02 and +0.01 ms measured again with the same draws. **Not done:** the graders' breadth the proposal asked for before shipping, for the stoops or for the railings; `engine_breadth.py`'s staged lots predate both, so it needs fresh lots of the other families. **For the walker's eye:** `cold_9273/railings.png`."""


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "THE RAILINGS, 2026-10-13" not in text, "already applied"
    assert text.count(S240_OLD) == 1, "240's status end not found once"
    text = text.replace(S240_OLD, S240_NEW)
    h = text.find("\n\n**240. ")
    s = text.rfind("\n\n*STATUS:", 0, h)
    assert h > 0 and text[s:h].endswith(S240_NEW), "240's status does not sit directly above its heading"
    nxt = text.find("\n\n*STATUS:", h + 10)
    assert nxt > h and text.find("\n\n**241. ", nxt) > nxt \
        and not re.search(r"\n\n\*\*\d+\. ", text[h + 10:nxt]), "241 does not follow 240"
    assert text.rfind("**THE STOOPS, 2026-10-13**", h, nxt) > h, "the stoops' paragraph is not 240's last"
    text = text[:nxt] + BODY_240 + text[nxt:]
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 240: status and a paragraph; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    main()
