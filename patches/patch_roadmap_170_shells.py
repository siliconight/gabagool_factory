"""Roadmap 170: a correction to the lid's status, 2026-10-15 -- the generated mission shells do not ship.

The NARROWED status written an hour earlier said nine of the sixteen roof-reaching stairs were "the mission
buildings Level Factory writes today, so every level made this week has a stair head open to the sky". Read
against cold run 9316's package: the generated shell (`deli_generate`, `lf_<mission>_<seed>`) is built, composed
and gated every run -- it is the first `presentation_compose` arm, "0/0 modules" -- and reaches no package; the
site stands the library's buildings (`building_library.lot_for_brief`, anchored on the brief's archetype), and
no file in the package carries the generated shell's hatch (`roof_hatch_13_-9`). So the stair heads that SHIP
are the library's: cr_deli and night_deli (the five other library specs with a roof-reaching stair -- bank,
corner_deli_heist_01, foundry_heist_vertical, harbor_score, rowhouse_raid -- are prop-only kitbash specs with
no walls and no roof slot). Replaces the status block (asserted once). The index is NOT touched here: run
`python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_170_shells.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

HEADING = ("\n\n**170. Every roof opening in the library is an open hole, and a building does\nnot have an open "
           "hole in its roof.**")
OLD = ("Left: the bulkhead over the 16 stair heads (step 2), "
       "the walker's eye on the frames and on the open default, and 3 of the 43 authored hatches whose specs are not "
       "built. Earlier status kept: the split (16 stairs reaching the roof, 43 hatch links under 69 roof ladders, "
       "26 ladders cutting nothing) and 2026-09-23's MEASURED, NOT STARTED -- 58 of 58 `roof_access` ladders cut "
       "the slab, 74 `hatch` links do, nothing in any tool emits a lid.*")
NEW = ("Left: the bulkhead over the stair heads (step 2) -- sized 2026-10-15 (`stair_heads.py`: holes 3.6-4.4 m "
       "wide, 5.1-7.5 m long, 1.0-2.25 m of roof left to the edge, storeys 3.2-5.0 m) -- whose SHIPPED population "
       "is two library buildings, cr_deli and night_deli: the nine `lf_*` shells are the mission's own, built, "
       "composed and gated every run (the first compose arm, 0/0 modules) and placed in no package since lots draw "
       "from the library, and the five other library specs with such a stair are prop-only kitbash specs with no "
       "walls and no roof; the earlier sentence that every level made this week has a stair head open to the sky "
       "was read off the specs, not a package, and is RETRACTED (cold run 9316's package carries no file with the "
       "generated shell's hatch). Also left: the walker's eye on the frames and the open default, 3 of the 43 "
       "authored hatches whose specs are not built, and the question of what the generated shell is for. Earlier "
       "status kept: the split (16 stairs reaching the roof, 43 hatch links under 69 roof ladders, 26 ladders "
       "cutting nothing) and 2026-09-23's MEASURED, NOT STARTED -- 58 of 58 `roof_access` ladders cut the slab, 74 "
       "`hatch` links do, nothing in any tool emits a lid.*")


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert text.count(OLD) == 1, "170's status tail not found once"
    i = text.find(OLD)
    assert text[i + len(OLD):].startswith(HEADING), "the tail does not adjoin 170's heading"
    text = text.replace(OLD, NEW)
    assert text.count("*STATUS: NARROWED 2026-10-15 -- the lid shipped, the bulkhead is left") == 1
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 170's status corrected; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
