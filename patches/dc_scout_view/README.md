# The scout view: Deli Counter 0.258.0 (roadmap 296)

The walker, on the drawings review page (2026-10-22): deli_a03 and office "Needs work" -- "we need to find a way to be
simple and not noisy visually" -- and players should see something "simpler but carry all of the signals needed".

**How it was reached.** `edit_axo_scout_first.py` made the first `scout=` on a clone: furniture, room fills and names,
markers and every dashed line left out. Its first frames lost two signals -- which storey a flight reaches, and what
a floor hole opens onto -- so the clone was then changed by hand: one solid leader a flight, head to landing, with its
arrow; one line from each hole's centre to the floor below; door thresholds 3.4 wide against 2.2. The clone's diff is
the patch (`gen_dc_scout_view.py`); `edit_dc_scout.py` added the package's `scout.svg`, the tests and VERSION.

**Frames** (`render_frames.py`, Edge headless at the SVG's own size): `deli_a03_full.png` against
`deli_a03_scout.png`; `office_full.png` against `office_scout.png`; `pharmacy_a01_scout.png`. Elements drawn: deli_a03
1,422 -> 595, office 1,003 -> 520, pharmacy_a01 310 -> 135.

**Proofs**: `prove.out.txt` -- the full drawing the same bytes on all 458 specs of the working checkout, and all six
new or changed tests failing on 0.257.0, on the new name; `suite.out.txt` -- 1,791 passed (1,787 at 0.257.0);
`dry_run_*.out.txt` -- a fresh clone patched to the proven clone's every byte, a second run refused. Proven in a
package by cold run 9379 (`docs/cold_runs/cold_9379/`). Level Factory's half: `patches/lf_scout_view/`.

**Left**: whether these are the right signals is the walker's (proposed: each storey's walls, doors and windows,
stairs, ladders and holes); a view a player can rotate is roadmap 295's map mesh.
