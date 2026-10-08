"""Roadmap: 204 CLOSED -- Level Factory 0.158.0 names the score and each
anchor's building and drops the unplaced shell's anchors, proven by cold run
9203; the site-level half was 0.156.0 and 0.157.0 (cold runs 9201, 9202).

    python patch_roadmap_204_close.py

Anchored on PIPELINE_ROADMAP.md as patch_roadmap_204_212_package.py left it
once its index was regenerated (1,307,011 bytes, LF, as read 2026-10-08):
204's status line by its unique prefix, directly above its heading; the
"Still to read" sentence of its first NEXT bullet; its last three NEXT
bullets. Then run `tools/roadmap_status.py --write` and `--check`.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
RM = ROOT / "PIPELINE_ROADMAP.md"

S204_PREFIX = "*STATUS: NARROWED 2026-10-08 -- the site-level half is fixed."
S204_NEW = (
    "*STATUS: CLOSED 2026-10-08 -- the package says where the score is, whose each anchor is, and starts and "
    "ends the mission at the getaway van. Level Factory 0.156.0 stages Lot's site markers -- the van's start and "
    "exit tagged `mission_start` and `extraction`, the responder arrivals as `ai_spawn`s tagged `responder` -- "
    "and 0.157.0 ships how each arrival arrives (cold runs 9201, 9202). 0.158.0 tags the site's objective "
    "building's objective `score` and writes the flow spawn -> score -> extract, passes each anchor's building "
    "through as `source_building`, and stages the generated Deli Counter shell's anchors only when the site has "
    "none of its own -- on a library lot they were a building not in the level, on deli_001 85 duplicates 6 m "
    "off. Cold run 9203: 0 interventions; the shipped package's beats are spawn -> score -> extract with score at b0's vault, 33 anchors all Lot's, 28 naming their building, Dispatch at readiness 100 and its notes 10 -> 7.*\n")

OLD_STILL = (
    "Still to read: where it takes Deli Counter anchors from on a library lot, and in which frame.\n")
NEW_STILL = (
    "Still to read: where it takes Deli Counter anchors from on a library lot, and in which frame. *Answered "
    "2026-10-08: from the candidate's generated shell (`deli_generate.candidate.seed_N`), in the shell's own "
    "frame; Level Factory 0.158.0 no longer stages them when the site carries its buildings.*\n")

OLD_REMAINING = (
    "- Mark the score: the objective anchors of the site spec's `objective` building carry the objective, and "
    "the site spec's extraction is marked as such.\n"
    "- Name each anchor's building (`source_building`).\n"
    "- A test on a library-lot package: no anchor from a shell the lot does not place.\n")
NEW_REMAINING = (
    "- Mark the score: the objective anchors of the site spec's `objective` building carry the objective, and "
    "the site spec's extraction is marked as such. *Done, below.*\n"
    "- Name each anchor's building (`source_building`). *Done, below.*\n"
    "- A test on a library-lot package: no anchor from a shell the lot does not place. *Done, below.*\n"
    "\n"
    "**THE REST, DONE: LEVEL FACTORY 0.158.0 (2026-10-08)** (`patches/patch_lf_package_score.py`).\n"
    "- **No anchor from a building that is not there.** Lot's gameplay holds every placed building's markers "
    "in site space, the generated shell's among them when the lot places it. So the shell's own anchors, props, "
    "interactives and ladders are staged only when the site has no markers to stand in for them.\n"
    "  - On a library lot they were a building not in the level, listed first.\n"
    "  - On deli_001 (cold run 9191), where the shell is placed as b0 at (6, 0), all 85 duplicated Lot's b0 "
    "anchors by name, 6 m off.\n"
    "- **The score.** `stage_dispatch_inputs(lot_site=)` reads the Lot job's drawn site spec for its "
    "`objective` building, and that building's objective anchors are tagged `score`. `mission_flow` writes "
    "spawn -> score -> extract; the score beat is written only when something carries the tag, since a beat "
    "bound to nothing is a Dispatch blocker. The extraction was already the van's (0.156.0).\n"
    "- **Each anchor's building.** `markers_to_anchors` passes `building` through, and Dispatch writes it as "
    "`source_building`, which was \"\" on every anchor of every package.\n"
    "- **Before the cold run.** Measured on cold run 9202's own outputs, built by the real Dispatch: the "
    "beats became spawn -> score -> extract, with score bound to `lot:A_6`, b0's vault. Anchors went 68 -> 33 "
    "(the unplaced shell's 35 gone), and 28 of the 33 name their building -- the other 5 are the van's and the "
    "responders'. Dispatch's notes went 10 -> 7, at readiness 100 with 0 blockers.\n"
    "- **The tests** (`tests/unit/test_dispatch_score_and_buildings.py`, 6) include the library-lot test this "
    "item asked for.\n"
    "- **Cold run 9203** (0 interventions; `docs/cold_runs/cold_9203/NOTES.md`): the shipped package matches the measurement made before it to the anchor. `DISPATCH_FINDING` went 10 -> 7, the three that went being the shell's `crew_spawn` and `responder_spawn` notes and its one nav bridge to Lot.\n"
    "- **A consequence to know.** The perf harness and `tools/look_shots.py` both take their stations and "
    "cameras from `gameplay_anchors.json`, so their station sets change with 0.158.0. A frame-time comparison "
    "across it compares different stations.\n")


def _replace_status(text, prefix, new_line, heading):
    lines = text.split("\n")
    hits = [i for i, l in enumerate(lines) if l.startswith(prefix)]
    assert len(hits) == 1, "status prefix found %d times: %r" % (len(hits), prefix[:50])
    i = hits[0]
    assert lines[i + 1] == "" and lines[i + 2].startswith(heading), "status not above %r" % heading
    lines[i] = new_line.rstrip("\n")
    return "\n".join(lines)


def main():
    data = RM.read_bytes()
    assert len(data) == 1307011, "PIPELINE_ROADMAP.md is %d bytes, read at 1,307,011" % len(data)
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    pairs = ((OLD_STILL, NEW_STILL), (OLD_REMAINING, NEW_REMAINING))
    for old, _new in pairs:
        assert text.count(old) == 1, "anchor found %d times: %r" % (text.count(old), old[:60])
    for new in (S204_NEW, NEW_STILL, NEW_REMAINING):
        assert "RESULT_" not in new, "an unfilled result: %r" % new[new.index("RESULT_"):][:40]
    text = _replace_status(text, S204_PREFIX, S204_NEW, "**204. ")
    for old, new in pairs:
        text = text.replace(old, new)
    RM.write_bytes(text.encode("utf-8"))
    print("204 closed; %d bytes" % len(text.encode("utf-8")))


if __name__ == "__main__":
    main()
