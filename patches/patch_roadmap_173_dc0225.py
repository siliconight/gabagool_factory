"""Roadmap 173, 2026-10-15 evening: the two office stair gaps were rules, fixed in Deli Counter 0.225.0; the status
stays NARROWED and its 'Left, in order' list loses its first item. Anchored on the sentence written earlier the
same evening (asserted once). The index is NOT touched here: run `python tools/roadmap_status.py --write` then
`--check` after it.

    python patches/patch_roadmap_173_dc0225.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

OLD = ("Left, in order: the two office gaps against Deli Counter's `stairwell.py` guard rules "
       "(which sides of a switchback it guards, and its top landing -- rails without colliders or no rails), and a "
       "fix there if real; the declared set read off the package's records")
NEW = ("The two office gaps were rules, fixed the same evening in Deli Counter 0.225.0 "
       "(`patches/patch_dc_switchback_top_run.py`): `rail` left the arrival end open across the whole reserved "
       "rectangle, two runs wide, while the arriving flight is one; `side` stood only on the rectangle's outer "
       "edges, so nothing guarded the seam between the runs; and the top leg's cut spanned both runs when only its "
       "own reaches that storey. Now the top leg cuts and reserves its own run (the slab covers the pit), a thin "
       "seam wall runs to the turn landing with its underside a body's height above the floor -- the nav gate's "
       "measurement on one shell of 157, where a floor-level wall over the lower run cut that flight and a stepped "
       "underside did not help (`patches/dc_switchback_top_run/nav_gate_bisect.md`) -- and the rail rule stands a "
       "rail at the seam. The re-measure on a fresh package is cold run 9318, staged. Left, in order: the declared "
       "set read off the package's records")


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert text.count(OLD) == 1, f"anchor found {text.count(OLD)} times"
    text = text.replace(OLD, NEW)
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 173: the office gaps fixed in DC 0.225.0; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
