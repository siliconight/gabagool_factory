"""Roadmap item 176 closes: the cause was 0.143.0 and 0.144.0 fixes it.

CLOSED requires the evidence in the status line, with figures -- so the hash
A/B and the sweep's two ends go in the status rather than only in the body.

The body keeps what the item was FOR: the refuted hypotheses, the refuted fix,
and the second-order finding about the nav gate's duty cycle, which this
release does not address and which is the more valuable half.

Anchored on the full multi-line status block. The one-line index row at the top
of the file contains the same opening words, so a short anchor would match
twice; the generated block is never edited by hand and `roadmap_status.py
--write` regenerates it after this.
"""
from pathlib import Path

TARGET = Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

OLD = """*STATUS: OPEN 2026-09-23 -- REGRESSION, WINDOW IDENTIFIED, COMMIT NOT YET
FOUND. `foundry_heist_vertical` passed the stair gate when
`navgate_baseline.json` was generated (2026-08-21, 135 shells, 3 stair
failures) and fails now. Its basement bakes as a disjoint island: 339 polygons
against 1,286 for ground-to-roof, with three separate connections crossing the
junction and none carrying. Two hypotheses refuted (below). Recorded in the
baseline as entry four, explicitly labelled a regression.*
"""

NEW = """*STATUS: CLOSED 2026-09-23 -- CAUSE Deli Counter 0.143.0, FIXED IN 0.144.0.
Attributed from the tracked `outputs_sha256_16` in `build/*.manifest.json`:
this shell's glb reads `c600f22e9178d52e` before 0.143.0 and
`8f2b4ae3a33c8567` at and since it, so that release moved the geometry and
nothing after it did -- confirmed by building with `stairwell.py` from HEAD~1
(old hash returns, both stairs `ok`) and at HEAD (`stair_0` `no_path`).
MECHANISM: 0.143.0 clipped the rail's opening to the plate beneath it, 0.2778
+ 0.8 = 1.0778 m, while the bake needs about 1.4 -- so the opening must be
WIDER than its floor and "opening <= floor" has no solution. Swept by forcing
`open_rail` and rebuilding: FAIL at 1.0778/1.2/1.25/1.3/1.35, PASS at
1.4/1.6/1.8/2.05, nine distinct glb hashes with the 2.05 control reproducing
the pre-0.143.0 file exactly. FIX: `stair_guards` lets the opening hang past
the plate by up to `agent_contract.body_radius()` (0.35), derived from the
capsule the rail holds back rather than chosen; opening 1.4278, shell gates
`navigable: yes` at glb `4914523fd9cf46ab`, removed from the baseline. TWO
REFUTATIONS KEPT BELOW, including a fix that looks obviously right and does
nothing. THE SECOND-ORDER FINDING IS NOT CLOSED and is restated below: this
sat five weeks because the sweep that catches it needs a built library.*
"""

TAIL_OLD = """**THE SECOND-ORDER FINDING, and it may matter more than the first.** Nothing
caught this for a month."""

TAIL_NEW = """**A THIRD FIX WAS TRIED AND REFUTED, and it is the useful one to keep**
because it is what anybody would reach for. Deepen the PLATE so the opening it
allows has floor under all of it -- raise `WALKOFF_CLEAR` from 0.8 to 1.25,
sized so `step_d + WALKOFF_CLEAR` clears 1.4 for the library's shallowest step
(0.1667 m, measured over all 133 specs and 149 flights). It does nothing. The
walk-off also sizes `flight_rect`'s reserved rectangle and the builder's hole,
and the opening is measured from that rectangle's edge, so `t_lo` moved out by
exactly as much as the opening grew and the rail landed in the same place.
Rebuilt and gated: `no_path`, glb `2a371e974f9f852d`. **The opening and the
plate are one quantity at any scale**, which is why the premise was
unsatisfiable rather than merely tight -- and that is the thing worth
remembering, not the number.

**1.4 IS NOT A LIBRARY-WIDE MINIMUM**, and asserting it as one was the last
wrong turn here -- caught by running the test that made the claim, which failed
against 130 shells. 130 of 149 railed flights leave an opening below 1.4 (a
typical `step_d` of 0.2350 gives 1.3850; the shallowest, 0.1667, gives 1.3167)
and every one of them gates `navigable: yes`. What made this landing different
is topological, not dimensional: it sits in a corner against the south wall, so
the rail's opening is its ONLY way off. Elsewhere a landing has floor on more
than one side and survives a narrow gap. A width threshold measured on one
shell is a property of that shell's topology, and generalising it would have
failed 130 working buildings.

**THE SECOND-ORDER FINDING, and it may matter more than the first.** Nothing
caught this for a month."""


def main() -> None:
    data = TARGET.read_bytes()
    if b"\r\n" in data:
        raise SystemExit("REFUSED: expected LF, found CRLF")
    text = data.decode("utf-8")
    before = len(data)
    for i, (old, new) in enumerate(((OLD, NEW), (TAIL_OLD, TAIL_NEW)), 1):
        hits = text.count(old)
        if hits != 1:
            raise SystemExit(f"REFUSED: anchor {i} matched {hits} times")
        text = text.replace(old, new)
    out = text.encode("utf-8")
    if b"\r\n" in out:
        raise SystemExit("REFUSED: would write CRLF")
    TARGET.write_bytes(out)
    print(f"{TARGET.name}: {before} -> {len(out)} bytes (+{len(out) - before})")


if __name__ == "__main__":
    main()
