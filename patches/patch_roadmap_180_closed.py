"""Roadmap item 180 CLOSED: Zoo 1.68.0 merges a building's covers one side per
material, measured on cold run 9155 (`docs/cold_runs/cold_9155/NOTES.md`).

The status line keeps its evidence; the earlier OPEN line is kept verbatim in
the body, as the roadmap keeps every status it replaced. The generated index is
NOT touched -- `roadmap_status.py --write` regenerates it.

    python patch_roadmap_180_closed.py <roadmap path>
"""
import pathlib
import sys

OLD_STATUS = ("*STATUS: OPEN 2026-10-05 -- MEASURED on cold run 9154's package: hiding every "
              "cover takes the worst view from 8,690 draws / 27.33 ms p95 to 5,571 / 17.74 ms, "
              "and the median view 850 draws / 2.06 ms lighter; control 0 draws / +0.05 ms. "
              "Nothing merges them.*\n")
NEW_STATUS = ("*STATUS: CLOSED 2026-10-05 -- Zoo 1.68.0 merges a building's covers one SIDE per "
              "material (8 meshes a building, 3,370 cover instances -> 232). Cold run 9155, 0 "
              "interventions, against 9154 at 53 headings: draws median -673 / mean -901; median "
              "frame -1.86 ms (89% of the hidden ceiling's -2.09), p95 -2.32 ms (99%), on the 50 "
              "headings stable between two control runs; the worst view 8,690 -> 5,904 draws. "
              "No live light lost (at most 5 of 8 on a merged mesh); frames differ from 9154 on at "
              "most 0.33% of pixels by more than 16 levels.*\n")

TAIL = ("machine\"), and every Empty detail still queued -- window air conditioners,\n"
        "bars, lintels and sills -- adds covers to multiply by placements.\n")
OUTCOME = r"""
**OUTCOME (Zoo 1.68.0, cold run 9155).** Shipped as designed above, one
correction made on the way. Grouping by the cover normal's dominant axis
would have put every curb and every roof edge strip of a building -- they
face UP, 60 of a rowhome's 103 covers -- into one mesh the size of the
building. An up-facing cover takes the side it stands nearest instead,
measured against the footprint's half-size (`core.dressing.cover_side`).
  * **Shape.** Every dressing GLB in 9155 is 8 meshes, 4 sides x concrete and
    painted metal, `refused 0`. The bake's users went 8,263 -> 5,125, which is
    exactly minus 3,370 covers plus 232 merged meshes.
  * **Geometry.** Rebuilt from 9154's own manifests before shipping, every
    vertex is within 1.3 um of its unmerged counterpart, with the same normal
    and uv.
  * **Price.** Measured against the mean of two 9154 runs, over the 50
    headings where those two agree within 1 ms (3 hitched in one control run
    and are listed in the notes): see the status line. Over the provisional
    budget: 13 -> 12 of 14 stations, 11 with the covers hidden.
  * **Lights.** The harness's census rose 46 -> 61 meshes over the cap. It
    counts baked lights, which do not draw live on a lightmapped mesh. A
    census of live lights only finds none over 8 on any merged mesh.
  * **Look.** The bake re-packed, and the difference from 9154 lies on the
    merged gutters and downspouts, faintly on brick, and on one lit window
    whose module did not change -- cause not established.

**WHAT REMAINS IS NOT THIS ITEM'S.** 12 of 14 stations are still over the
provisional budget with every cover merged and 11 with every cover gone, so
the rest of the overrun lives in something other than Patina's dressing.

*Earlier status, kept verbatim:* *STATUS: OPEN 2026-10-05 -- MEASURED on
cold run 9154's package: hiding every cover takes the worst view from 8,690
draws / 27.33 ms p95 to 5,571 / 17.74 ms, and the median view 850 draws /
2.06 ms lighter; control 0 draws / +0.05 ms. Nothing merges them.*
"""


def main():
    p = pathlib.Path(sys.argv[1])
    d = p.read_bytes()
    assert b"\r\n" not in d, "the roadmap is LF; a CRLF means something changed"
    s = d.decode("utf-8")
    assert s.count(OLD_STATUS) == 1, "item 180's OPEN status not found exactly once"
    assert s.count(TAIL) == 1 and s.endswith(TAIL), "item 180 is no longer the last thing in the file"
    s = s.replace(OLD_STATUS, NEW_STATUS) + OUTCOME
    p.write_bytes(s.encode("utf-8"))
    print("closed item 180 in", p)


if __name__ == "__main__":
    main()
