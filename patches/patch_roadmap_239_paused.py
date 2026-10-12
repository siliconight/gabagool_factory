"""Roadmap 239: paused at the walker's call, 2026-10-12 ("our optimization for time is good enough for
now"), and Level Factory 0.193.2's suite cut recorded. Replaces 239's status block (asserted once)
with one that leads with where the loop stopped and what is left, keeping the old status's text
whole after it; appends one body paragraph at the end of 239's body. The index is NOT touched here:
run `python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_239_paused.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUS_OLD_HEAD = "*STATUS: NARROWED 2026-10-11 -- the graders no longer wait on real seconds."
OLD_LEAD = "*STATUS: NARROWED 2026-10-11 -- "
NEW_LEAD = (
    "*STATUS: NARROWED 2026-10-12 -- PAUSED at the walker's call, 2026-10-12: \"our optimization for "
    "time is good enough for now\", back to the roadmap's other items. Where it stopped: a cold run's "
    "drive 30.4 -> 6.9 minutes (9245 -> 9259, 0 interventions throughout); a stranger's first `make` "
    "34.1 -> 7.9 minutes and `walk` 10.9 -> 5.6 (install test 8, factory 1.39.0, released); Level "
    "Factory's suite 443.1 -> 355.1 s (0.193.2); two exports of a workspace one lightmap byte for byte "
    "(0.192.0) and two cold runs one in all but 15 of 16,777,216 texels (Zoo 1.103.0); every cut "
    "against a control and none moving a finding -- on a stranger's level too, where the clock moves "
    "no field of Laser Tag's report for either enemy body "
    "(`docs/findings/grader_speed/body_or_clock_ab.sh`). Left, each measured and none started: the "
    "bake's editor's first frame of the level (~10 s, not the viewport), the sidecar step's serial "
    "model imports (32 s), the Lux job's staging import (26.5 s), the suite's worldskin imports "
    "(91.7 s; side by side needs pytest-xdist, a download) and integration tests (166.8 s), the "
    "residue between two cold runs (rowhome_k's merged covers' triangle order, Lux's applied scene "
    "ids); and the walker's call on the grader's step (4x against the game's 1/60 s). THE HISTORY, "
    "as the status stood: ")

BODY_ADD = """

**THE SUITE, 2026-10-12** (`docs/findings/lf_suite_time/`). With the drive at 6.9 minutes, Level Factory's suite was as long as the run it gates -- 443.1 s on 0.193.1, by its own JUnit -- and 53 of its 2,348 tests held 394.6 s of it. The largest, `tests/test_archetype_resolution.py` at 118.8 s, walked the whole factory three times (1,524,870 entries, 69 % under `workspaces/`) for 487 briefs, listing 384,372 entries under directories it then discarded. Level Factory 0.193.2 walks once a session and never into a discarded directory, the predicate unchanged -- the same 487 briefs in the same order in four alternated walks (`brief_walk_probe.py`) -- and the suite ran 355.1 s, the module 22.0. Its three tests fail on 0.193.1, and against the old walk given the new names two fail on its behaviour while the identity passes. **Not changed, a question:** 148 of the 487 briefs are under the gitignored `_scratch/`, so the corpus depends on what a checkout holds; the skip list's own rule ("scratch, not corpus") would exclude them, which narrows what the tests read and waits for a change of its own. **Then the walker paused the loop** ("good enough for now"); what is left is in the status."""


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "PAUSED at the walker's call, 2026-10-12" not in text, "already applied"
    i = text.find(STATUS_OLD_HEAD)
    assert i >= 0 and text.count(STATUS_OLD_HEAD) == 1, "239's status block not found once"
    j = text.find("\n", i)
    old_status = text[i:j]
    assert old_status.startswith(OLD_LEAD) and old_status.endswith("*"), old_status[-80:]
    assert old_status.count("*STATUS:") == 1, "the status line holds two statuses"
    new_status = NEW_LEAD + old_status[len(OLD_LEAD):]
    text = text[:i] + new_status + text[j:]
    h = text.find("\n\n**239. ")
    assert h > 0 and text.count("\n\n**239. ") == 1, "239's heading not found once"
    assert h == i + len(new_status), "239's status does not sit directly above its heading"
    nxt = text.find("\n\n*STATUS:", h + 10)
    assert nxt > h, "no status block after 239's body"
    text = text[:nxt] + BODY_ADD + text[nxt:]
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 239: paused, its status led and kept, one paragraph appended; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
