"""Roadmap 197 NARROWED (cold run 9246 and Laser Tag 0.26.0) and 239 filed (the graders' share of a
cold run, Level Factory 0.179.1's cap, the refused clock). 197: its status block replaced (asserted
whole by its first and last text, and asserted to adjoin its heading) and a paragraph appended to
its body. 239 appended after 238, the roadmap asserted to end with 238's body. Nothing written on a
miss. Run `python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_197_239.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"
HEAD_197 = "\n\n**197. A generated deli's enemies jam at its rear door.**"
S197_START = "*STATUS: OPEN 2026-10-07 -- narrowed to one spot, not explained: in cold run 9191 every generated-deli candidate"
S197_END = "stand 1 m outside the recipe's 1.1 m rear staff door.*"
S197_NEW = (
    "*STATUS: NARROWED 2026-10-11 -- re-measured on today's tools and half explained. Cold run 9246 "
    "(9191's brief and seeds, 0 interventions): no candidate is out any more, enemy-stuck 49 / 0 / 19 "
    "where 9191 read 177 / 192, and none at the 1.1 m rear door. Laser Tag 0.26.0 fixed the grader's "
    "half: every enemy had kept the pill scene's 0.40 capsule (the bake's radius, which the contract "
    "says is not a body radius) and its 0.8 m arrival radius, the value 0.18.0 measured jamming the "
    "crew at corners; on 9246's seed_9191, in copies of its own staged evaluation, stuck 49 -> 28 and "
    "WARN 68 -> PASS_WITH_TUNING 76, three unpatched runs identical in every field. Left: the 28, "
    "enemies queued on the crew's route along the deli's west wall among a kitchen grill and a shelf "
    "run, touching no static geometry -- each enemy's destination when it stalls is the next "
    "instrument; and the recipe's three floor doors under the contract's 1.25 m, flagged by a "
    "warning nothing reads.*")
TAIL_197 = ("**NEXT.** Bake 9191's walk-copy site and read the navmesh through the rear door, before any "
            "change to the recipe.")
ADD_197 = """

**RE-MEASURED, 2026-10-11** (`docs/cold_runs/cold_9246/NOTES.md`, `docs/findings/grader_speed/`). The NEXT above was overtaken: cold run 9246 ran 9191's never-changed brief on today's tools, and the rear door is no longer where enemies stop -- 42 of seed_9191's 49 stand just inside the west wall, 0.8 m short of the `alley_entry` door, and 7 at the loading bay's partition neck (an interior partition meets the north wall 0.1 m inside the bay's opening: roadmap 189's "door running past the end of its wall", seen from the other side). **The grader's half, fixed: Laser Tag 0.26.0.** `_configure_enemy` never applied `_apply_body`, so every enemy kept `LT_EnemyPill.tscn`'s capsule of radius 0.40 -- `nav_bake.agent_radius_m`, which the contract says "is NOT a body radius and nothing should be built from it" -- and the scene's `path_desired_distance` 0.8, which Laser Tag 0.18.0 measured cutting corners and jamming the crew and replaced for the crew only, its note saying the enemy's copy was used by nothing. Drafted onto a copy of seed_9191's staged evaluation: enemy-stuck 49 -> 28, grade WARN 68 -> PASS_WITH_TUNING 76, `INSTANT_CONTACT` cleared, route completion, enemy and player deaths unchanged -- and the job's own report and two quiet reruns identical in every field, so the difference is the patch's alone. **What is left.** Placed by their two-decimal positions, the 28 (and 0.25.0's 42) touch no static geometry: they stand along the inside of the west wall, where a kitchen grill 0.9 m deep and a 1.2 m shelf run alternate with 1.35 and 1.2 m gaps before the alley door, and each quarter-metre cell holds events from five or six enemies. The crew enters by that door and walks that wall to the objective; the six enemies spawn in a row behind the north wall and chase them in. So the remainder is enemies queued among the pieces and each other (enemies collide with enemies) or holding on targets they cannot reach -- a trace of each enemy's destination when it stalls is the instrument that would say which. And the 1.1 m rear door that started this item stands under the contract's `min_door_width_m` 1.25, with the recipe's 1.2 m front door and 1.1 m counter door, all flagged by Deli Counter's `navigability` as a warning nothing reads."""

TAIL_238 = ("**WHAT WOULD CLOSE IT.** The engine's monitor read under 100 MiB on a package at the fixed "
            "stations with the walker's eye on the frames, the probe run in every cold run's record "
            "beside the price so the number cannot drift back unseen.\n")
STATUS_239 = (
    "*STATUS: NARROWED 2026-10-11 -- the graders now run three at a time (Level Factory 0.179.1, the "
    "walker's call): verdicts unchanged at three and six in every trial, a few recorded positions one "
    "0.01 m rounding step apart from three up; the faster Laser Tag clock measured and refused. Open: "
    "that noise's cause, one import of a package instead of several, and how far Laser Tag's 4x clock "
    "(a 66.7 ms physics step) reads from the game's 60 Hz.*")
ITEM_239 = """

**239. A cold run spends 88 % of its job time in its graders.** The walker, 2026-10-11, during cold run 9246: "is there anything intelligent we can do to make our coldruns faster without losing any certainty of quality or introducing regressions? Im thinking this is the most time consuming part of our iteration process?" Measured the same hour from every job's own `duration=` (`docs/findings/grader_speed/`): cold run 9245 (restaurant_row_001, 16 buildings, 32 minutes) spent 31.6 job-minutes, 65 % in Laser Tag's evaluations (three candidates, 25 runs each) and 22 % in the walk tests, every Blender build together 3 %; the shell leg spanned 15.7 minutes, because `DEFAULT_CONCURRENCY` let two Godot jobs run at once on 8 cores, and its longest single evaluation was 10.25 of them. The rest of the run is the export (extraction, an import of the package, the bake, the manifest) and the walk copy, about 10 minutes.

**WHAT WAS TRIED, AND WHAT EACH COST.**
- **A faster simulation clock: REFUSED.** Laser Tag runs at `--time-scale` 4; 8 would halve an evaluation and 16 cut it to 30 %, but Godot scales the PHYSICS STEP with `Engine.time_scale`, and the reports changed from their first event (enemy-stuck 49 at 4x, 2 at 8x, 0 at 16x on one seed).
- **The graders side by side: ADOPTED at three** (Level Factory 0.179.1, `scheduler.godot_cap`: the smaller of half the logical CPUs, never below 2, and `GODOT_PROVEN_WIDTH` 3). Laser Tag's evaluation is deterministic alone and two at a time -- every report identical to its job's in every field across reruns -- and at three and six every verdict held in every trial while one to three recorded event positions in some reports moved by one rounding step, the same boundary values each time. The walker took that trade knowing it. No evaluation ran slower beside the others; a 16-building shell leg should fall from 15.7 minutes to about 10.5, the longest evaluation's length, which the next cold run on that lot measures.

**OPEN, IN ORDER.**
1. **One import of a package, not several.** The export imports its package to bake it, the walk copy imports it again from scratch, and each walk test imports its staged project first; Godot re-verifies a reused import cache against each source's hash, so reuse is safe by construction where the sources are the same files. Worth about 1.5 to 3 minutes a run; to be measured before built.
2. **Jams cost wall time.** A run that ends on a stuck body plays to its 180 s limit, 45 s of wall at 4x: fixing what jams (roadmap 197, Laser Tag 0.26.0's enemy) also shortens the evaluation.
3. **The noise's cause.** Async navigation iterations and the worker pool shared across processes are the suspects (`engine_settings_probe.gd`); pinning either would move every grader's results once and needs its own A/B.
4. **The 4x clock's fidelity.** If Godot steps physics at 66.7 ms under Laser Tag's default, its findings are a coarser simulation than the game's 60 Hz; `realtime_ab.sh` runs one evaluation at 1x beside 4x, with 0.25.0's enemy and 0.26.0's, to say how far apart they read."""


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "RE-MEASURED, 2026-10-11" not in text and "\n**239. " not in text, "already applied"
    assert text.count(HEAD_197) == 1, "197's heading not found once"
    assert text.endswith(TAIL_238), ("the roadmap does not end with 238's body", text[-160:])
    h = text.index(HEAD_197)
    s = text.rfind("\n\n*STATUS:", 0, h) + 2
    status = text[s:h]
    assert status.startswith(S197_START) and status.endswith(S197_END), ("197's status", status[:90], status[-90:])
    nxt = text.find("\n\n*STATUS:", h + 10)
    assert text[h:nxt].endswith(TAIL_197), ("197's body tail", text[h:nxt][-140:])
    # the end first, then later edits before earlier ones, so offsets stay right
    text = text.rstrip("\n") + "\n\n" + STATUS_239 + ITEM_239 + "\n"
    text = text[:nxt] + ADD_197 + text[nxt:]
    text = text[:s] + S197_NEW + text[h:]
    assert text.endswith("\n")
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap: 197 NARROWED with its paragraph, 239 appended; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
