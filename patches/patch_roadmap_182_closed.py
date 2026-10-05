"""PIPELINE_ROADMAP.md: close item 182 on cold run 9165's price.

Replaces the item's status line (the whole line, which the generated index
also quotes only in part) and keeps the earlier one verbatim at the item's
end, as 180 did. The index is left to `tools/roadmap_status.py --write`.

    python patch_roadmap_182_closed.py
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

OLD_STATUS = ("*STATUS: OPEN 2026-10-05 -- MEASURED, NOT STARTED. Hiding all 25 Empties saves 816 draws / "
              "1.87 ms at the median view, up to 3,951 / 11.6 ms (9161, interleaved with cool-downs, control "
              "0.05 ms). A prototype merging each Empty's kit modules one mesh a side per material saves 686 / "
              "0.88 ms, up to 3,015 / 6.9 ms (9162, control 0.026 ms).*\n")
NEW_STATUS = ("*STATUS: CLOSED 2026-10-05 -- Level Factory 0.143.0 merges each Empty's kit modules one mesh a "
              "side per material in the export, after the occluder bake and before the light bake (colliders "
              "kept, materials duplicated, every merged mesh unwrapped). Cold run 9165, 0 interventions, "
              "against 9164 at 53 headings (control +0.058 ms, none unstable): draws median -643 / mean -875, "
              "up to -2,914; median frame -1.11 ms (59% of the hidden ceiling's -1.87), up to -7.10 ms. Light "
              "bake ok at 3,309 users; door collision and the street frame unchanged.*\n")

BODY_END = '''that thing, as one side of a building's covers was for 180. Merging across
houses stays wrong.
'''
BODY_NEW = '''that thing, as one side of a building's covers was for 180. Merging across
houses stays wrong.

**SHIPPED (0.143.0, cold run 9165).** `packages/exporting/merge_empties.py`
finds the scenes the site's `blocker_<n>` nodes instance, runs
`assets/godot/merge_empties.gd`, and believes its report, never its exit
code. 12 designs: 1,061 meshes of 1,660 surfaces became 236 merged meshes,
with 962 colliders kept.

**WHAT REMAINS, NOT THIS ITEM'S.**
  * **More merged meshes than the prototype made.** 14-22 a design, against
    the prototype's 12-13 on a walk copy already imported for its lightmap.
    The untested candidate is surface format (UV2 or not), which is part of
    the group key; the merge re-unwraps every mesh anyway.
  * **The Empties' module GLBs still ship and are re-imported.** Nothing
    instances them after the merge.
  * **The Empties' occluders are still one per wall module.** They were 1,002
    of 1,316 in 9162's package.

*Earlier status, kept verbatim:* ''' + OLD_STATUS


def main():
    s = ROADMAP.read_text(encoding="utf-8")
    assert "\r" not in s
    assert s.count(OLD_STATUS) == 1, "182's status line is not the one filed"
    assert s.count(BODY_END) == 1
    s = s.replace(OLD_STATUS, NEW_STATUS).replace(BODY_END, BODY_NEW)
    ROADMAP.write_text(s, encoding="utf-8", newline="\n")
    print("closed roadmap item 182")


if __name__ == "__main__":
    main()
