"""Roadmap 240, 2026-10-13: the stoops' and railings' graders' breadth, run after the fact
(`docs/findings/stoop_breadth/`). Replaces the "Left: the graders' breadth ..." clause of 240's status (asserted
once and still directly above its heading) and appends one paragraph to its body, after the railings' and
before 241's status. The index is NOT touched here: run `python tools/roadmap_status.py --write` then
`--check`.

    python patches/patch_roadmap_240_stoop_breadth.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

S240_OLD = ("Left: the graders' breadth with stoops in the lots (the proposal's step, never run: "
            "`engine_breadth.py`'s staged lots predate the stoops); the street lights' shadow cost")
S240_NEW = ("The graders' breadth the proposal asked for, run after the fact (`docs/findings/stoop_breadth/`): on "
            "the 8 of `engine_breadth.py`'s lots with rowhomes, the same Deli Counter with and without stoops, "
            "the controls held -- the walk test unchanged on all eight, no Laser Tag stuck event within 10.9 m of "
            "a stoop over 229, the fights moving both ways. Left: the street lights' shadow cost")

BODY_240 = """

**THE GRADERS' BREADTH, 2026-10-13** (`docs/findings/stoop_breadth/`). The proposal's pre-ship step, run after the stoops and railings shipped. **The lots:** the 8 of `engine_breadth.py`'s 16 with rowhome Empties in them -- restaurant_row_001 x3, warehouse_yard_001 x3, bank_block_001, club_block_014, 14 to 28 stoops each; deli_001's, gas_block_001's and crossroads_9600's carry none. **The arms:** each lot as staged but for its `buildings/gs_empty_rowhome_*.glb` -- `flat`, the twelve as Deli Counter 0.212.0 builds them with `stoop=0`; `flat2`, the same again, the control; `stoop`, the twelve as 0.212.0 built them (`build_flat.py`: 6 stoop and 8 railing nodes a shell, 8 more colliders). Laser Tag 0.29.0 at `--fixed-fps 60`, 25 runs from each job's seed, Godot Physics; the walk test through `walktest.py`'s own steps. **Both controls held on every lot, and every bake sees the stoops** (+115 to +297 navmesh polygons a lot). **The walk test is unchanged:** every walker ok and every target reached on all eight, no anchor stranded, barred or without standing room. **No stuck body at a stoop:** 229 Laser Tag stuck events over every arm, none within 1 m of a stoop's plan box, the nearest 10.93 m; no player pin, no timeout. **The fights move, both ways:** six grades unchanged, warehouse_yard_001 seed_9004 PASS_WITH_TUNING 89 -> PASS 90 and seed_9206 WARN 68 -> 67, each route move one team wipe in 25 runs (in `flat` on 9004, in `stoop` on 9206); enemy stuck 0 -> 3 on restaurant_row_001 seed_9104 and 1 -> 3 on club_block_014, all 10.9 m or more from a stoop. **Found on the way:** the seed_9104 three -- two enemies standing still at (-2.05, 0.02, 12.24) and (-2.75, 0.02, 12.24), 18 m from the nearest stoop -- are in cold runs 9271 to 9273's own jobs and not 9270's, where those runs' notes said "grades as in 9270", true of the grades only; the spot's cause is unmeasured. **Not measured:** whether any geometry change of that size moves the fights as much -- no null perturbation was run, so the fight moves are reported, not attributed. **RETRACTED, KEPT** (`stoop_breadth_walk_staged_director_RETRACTED.out.txt`): the first walk used each copy's staged director, and the first lot staged before Lot 0.117.0 failed in its `flat` arm on "navigation map is EMPTY at QA time"; the walk now gets today's director, as `walktest.py`'s `main()` gives every run."""


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "THE GRADERS' BREADTH, 2026-10-13" not in text, "already applied"
    assert text.count(S240_OLD) == 1, "240's status clause not found once"
    text = text.replace(S240_OLD, S240_NEW)
    h = text.find("\n\n**240. ")
    s = text.rfind("\n\n*STATUS:", 0, h)
    assert h > 0 and S240_NEW in text[s:h], "240's status does not sit directly above its heading"
    nxt = text.find("\n\n*STATUS:", h + 10)
    assert nxt > h and text.find("\n\n**241. ", nxt) > nxt \
        and not re.search(r"\n\n\*\*\d+\. ", text[h + 10:nxt]), "241 does not follow 240"
    assert text.rfind("**THE RAILINGS, 2026-10-13**", h, nxt) > h, "the railings' paragraph is not 240's last"
    text = text[:nxt] + BODY_240 + text[nxt:]
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 240: status and a paragraph; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    main()
