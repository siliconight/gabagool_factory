# Cold run 9319 -- urban_row_001 on Deli Counter 0.226.0 + Lot 0.125.0 + Dispatch 0.5.3 (2026-10-16): VOID

Staged from 9318 as the package proof that a declared drop's nav link reaches `navigation_hints.json` (roadmap
173, step 3). It got as far as the pick -- three candidates, seed 9104 again, PASS 100 -- and DIED AT THE ART
STAGE (`drive exit 2`) because the disk was full: C: at 100 %, 0 bytes free, while the export's light bake and
package copy needed space. Not a toolchain failure and not an intervention; nothing in the run's output is
evidence about the tools, and the run is re-staged as 9320 once the disk is measured and freed.

What the disk held is in `docs/findings/disk_full_2026_10_16/` if a record was worth keeping, else in the
root's CHANGELOG line for the day.
