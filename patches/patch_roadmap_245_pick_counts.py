"""Roadmap 245 and 246, 2026-10-13: which majors decide a pick (CLOSED, Level Factory 0.202.0), and Laser Tag
counting the end of a short path as arriving (OPEN, found by 245's census). Both appended after item 244, the
last. The index is NOT touched here: run `python tools/roadmap_status.py --write` then `--check`.

Level Factory's commit is read from its repository and must be the 0.202.0 release, so the status line names
the commit that shipped it rather than a hash typed from memory.

    python patches/patch_roadmap_245_pick_counts.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"
TAIL = "price the change on the graders first (242).\n"


def _lf_commit():
    out = subprocess.run(["git", "-C", str(ROOT / "level_factory"), "log", "-1", "--format=%h %s"],
                         capture_output=True, text=True, check=True).stdout.strip()
    sha, subject = out.split(" ", 1)
    assert subject.startswith("0.202.0:"), ("Level Factory's head is not the 0.202.0 release", out[:80])
    return sha


def _items(lf):
    return (
        "\n*STATUS: CLOSED 2026-10-13 -- the walker left the call to the factory (\"I think you can make that call "
        "for the moment\"), and a census over the 62 cold workspace missions on this disk (186 candidates) made it. "
        f"Level Factory 0.202.0 ({lf}) picks as before -- out on the walk test or a major route or pathing finding, "
        "then the fewest majors, the highest route completion -- then the higher Laser Tag score (the walker's "
        "\"ties should go to the higher grade\"), then the lowest seed; Laser Tag's five verdicts on the fight "
        "(TRIVIAL_ENCOUNTER, NO_REACTION_TIME, LT_NO_SURVIVABLE_OPENING, NO_ENGAGEMENT, NO_CONTACT) are shown and "
        "not counted, and LOT_DESTINATION_ABOVE_FLOOR is not counted where the walk test walked every leg. The cold "
        "driver's picker reads that rule rather than spelling its own. Replayed as the driver runs it: 62 missions, "
        "28 picks move -- the census's 28, each to the same seed -- 12 to a higher route completion or score, 16 "
        "to an equal one, none to a lower (`docs/findings/pick_majors/`).*\n"
        "\n"
        "**245. Which majors decide a pick.** The walker, 2026-10-13, sharing a QA proof-of-concept on navigation "
        "and combat: does it help make Laser Tag good enough to use in the factory? The first step out of it was "
        "a choice -- which finding types stop counting as majors when a candidate is picked -- and the walker left "
        "it to the factory \"for the moment\".\n"
        "\n"
        "**WHAT THE CENSUS FOUND** (`docs/findings/pick_majors/major_census.py`, `major_census.out.txt`; its copy "
        "of the old rule picks what the driver picked on all 62). One code chose the picks, and it is Lot's: "
        "LOT_DESTINATION_ABOVE_FLOOR, on 96 of the 186 candidates, every one an objective 3.3 to 4.0 m up -- a "
        "storey, which Lot cannot tell offline a stair reaches. Not counting it alone moves 28 of the 62 picks; "
        "LT_MAP_NO_REACTION_TIME alone moves one; nothing else moves any. The walk test walked every leg on 95 of "
        "the 96 -- every crew walker exactly \"ok\", no leg credited as a ladder, which its own `ok` would pass. "
        "On the 96th, cold run 9185's seed_9003, its proof to the objective stopped 60.99 m short on a disjoint "
        "navmesh island: the doubt was right there, and it still counts there. Counted, it took a lower route "
        "completion or score than the new rule on 12 picks -- cold runs 9263 to 9265 took restaurant_row_001's "
        "0.72 at PASS_WITH_TUNING 78 over 1.00 at PASS 90 -- and an equal one on 16. Laser Tag's five verdicts on "
        "the fight, taken together, move none of the 62. They bracket one fight -- cold run 9283 carried "
        "NO_REACTION_TIME on two candidates whose crews died in 6.44 and 7.80 s and TRIVIAL_ENCOUNTER on the one "
        "whose crew lost nobody -- so they are not counted as a set, or not at all; they still reach the pick "
        "through the score. TRAVERSAL stays counted: on both of its candidates the crew was wiped before walking "
        "half the route, a fight outcome, but a crew held by the geometry reads the same.\n"
        "\n"
        "**WHAT IT CHANGES.** On this disk the new rule picks another seed in 28 missions: restaurant_row_001 in 23 "
        "of its 42 runs (every run since 9263), urban_row_001 in all 3, club_block_014 in 2 of 4. Sixteen of the "
        "moves are ties that now go to the lower seed -- a different level, with no measured difference. An A/B "
        "against an earlier run names its seed (`cold_drive.sh N PREV mission 9104`, not `auto`): "
        "`docs/findings/urban_street/ab_record.sh` was sound because both runs had picked seed_9104.\n"
        "\n"
        "**LEFT:** Lot's finding's severity and message -- the consequence it states, TRAVERSAL at 0%, held on none "
        "of the 95 walked, but Lot raises it before the walk test exists (roadmap 52's question); the "
        "proof-of-concept's later steps -- planted-defect fixtures scored for precision and recall, findings "
        "attributed to the element that caused them, a four-player congestion check, static first; and 246.\n"
        "\n"
        "*STATUS: OPEN 2026-10-13 -- found by 245's census and not fixed; Laser Tag's to fix, bounded.*\n"
        "\n"
        "**246. Laser Tag counts the end of a short path as arriving.** Found by 245's census. Cold run 9185's "
        "restaurant_row_001 seed_9003 read route completion 1.00 in Laser Tag, every run, while the walk test's "
        "path to its objective -- b0's apartment_hideout, 3.3 m up -- stopped 60.99 m short on a disjoint navmesh "
        "island (`docs/findings/pick_majors/README.md`).\n"
        "\n"
        "**THE READING** (consistent with that measurement, not traced in a run). `LT_BotPlayerController` counts "
        "a route point arrived when `_nav_finished()` is true, and that is `NavigationAgent3D.is_navigation_finished()`: "
        "true at the end of the path the navigation server returned, which for a target the network does not "
        "reach is the closest point it does. Godot's question \"is the agent at the target\" is "
        "`is_target_reached()`, and Laser Tag does not ask it. So Laser Tag's route completion is not a proof that "
        "a route point can be stood at; the walk test's path proofs are, and the pick reads those (245).\n"
        "\n"
        "**THE FIX** is Laser Tag's: an arrival only within `LT_Const.arrival_radius` of the route point itself. "
        "Prove it on 9185's candidate, whose completion should fall, with the factory's lots replayed as the "
        "control. Bounded: the walker has said Laser Tag work should not become a rabbit hole.\n"
    )


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "**245. " not in text and "**246. " not in text, "already applied"
    assert text.count(TAIL) == 1 and text.endswith(TAIL), "item 244 is not the roadmap's end"
    lf = _lf_commit()
    body = _items(lf)
    for line in body.splitlines():
        stripped = line.lstrip("*")
        assert not (line.startswith("**") and stripped[:1].isdigit() and not line.startswith(("**245. ", "**246. "))), \
            ("a body line would parse as an item", line[:40])
    RM.write_bytes((text + body).encode("utf-8"))
    print(f"roadmap 245 (CLOSED, Level Factory 0.202.0 {lf}) and 246 (OPEN); now roadmap_status.py --write / --check")


if __name__ == "__main__":
    main()
