"""Roadmap 230: Level Factory 0.176.1 and Lot 0.112.0 landed; cold run 9232 runs the brief again.

Replaces two sentences of 230's status block. Each anchor must match exactly once; nothing is
written on a miss. The generated index is regenerated afterwards by `tools/roadmap_status.py
--write`.

    python patches/patch_roadmap_230_0176_1.py
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

OLD_A = (
    "*STATUS: NARROWED 2026-10-10 -- steps 1 and 2 are LANDED and step 4 (the targets in the audit) "
    "is DRAFTED as Lot 0.112.0 (`patches/patch_lot_targets.py`, proven on a clone). "
)
NEW_A = (
    "*STATUS: NARROWED 2026-10-10 -- steps 1, 2 and 4 are LANDED: Level Factory 0.176.0 and 0.176.1, "
    "Lot 0.111.0 and 0.112.0 (`patches/patch_lot_targets.py`, the targets in the audit, 774 passed on "
    "the repo). "
)
OLD_B = (
    "Level Factory 0.176.1 (`patches/patch_lf_cluster_site.py`) reads "
    "the template in one function for all four draws and refuses, by test, any `pick_lot` outside "
    "the library without it; cold run 9232 re-runs the brief on it. "
)
NEW_B = (
    "Level Factory 0.176.1 (`patches/patch_lf_cluster_site.py`, LANDED: `preferred_for_brief` read by "
    "all four draws, a bracket-balanced test over every `pick_lot` in `apps/` and `packages/`, Lot "
    "0.112.0's `S_TARGETS` reaching the report as info; 2,204 passed) fixes it, and cold run 9232 "
    "re-runs the brief on it with Deli Counter 0.207.0. "
)


def main():
    raw = ROADMAP.read_bytes()
    assert raw.count(b"\r") == 0, "the roadmap is LF; a CR means something changed it"
    text = raw.decode("utf-8")
    assert text.count(OLD_A) == 1, text.count(OLD_A)
    assert text.count(OLD_B) == 1, text.count(OLD_B)
    text = text.replace(OLD_A, NEW_A).replace(OLD_B, NEW_B)
    i = text.index(NEW_A)
    j = text.index("\n", i)
    assert text[j:].startswith("\n\n**230. "), "230's status left its heading"
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 230: 0.176.1 and Lot 0.112.0 landed")


if __name__ == "__main__":
    main()
