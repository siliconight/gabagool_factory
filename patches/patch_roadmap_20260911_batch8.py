"""Roadmap batch 8, 2026-09-11: close 25, narrow 26.

Both items rest on a sentence rather than a status block (the index infers
OPEN from silence). INSERT mode, batch 4's mechanism: the heading must match
exactly once, a status block already above it refuses, a missing blank line
before the heading is supplied.
"""
import io
import re
import sys

P = "PIPELINE_ROADMAP.md"

INSERT = {
    25: """*STATUS: CLOSED 2026-09-11 -- EVERYTHING AUTOMATED IMPORTS FIRST, AND THE
LINE A PERSON READS NOW SAYS SO. The item asked two things. The pipeline half:
every stage that launches a generated project runs `godot --headless --path
<project> --import` before anything else -- Level Factory's staging
(`staging/godot_project.py:231`), export (`exporting/export.py:338`) and
portability check (`portability.py:92`), the Lux adapter's first command
(`adapters/lux:208`), Lot's `package.py:284` and `walktest.py:122`, and the
factory's `walk_export.py`, `walk_greybox.py` and `walk_themed.py`; `godot_probe`
already did, which is why the light census was ever measuring a populated
scene. The human half: `cater`'s "SERVED -> open <site>_walk.tscn in Godot, F6"
is followed since Lot 0.55.1 by the import command and why -- an unopened
project has no import artifacts and every building reads as vanished. The
behaviour itself is Godot's and is not a defect; what closed was the trap
being unannounced.*""",

    26: """*STATUS: NARROWED 2026-09-11 -- THE INSTRUMENT SHIPPED AND GREW; THE GATE
WAITS ON A NUMBER NOBODY HAS CHOSEN, WHICH THE ITEM SAYS IS THE RIGHT ORDER.
`tools/look_shots.py` exists (2026-08-03, then orthographic elevations and
`shot_diff`'s null floor on 09-02, `--interiors N` on 09-06): cameras derived
from the mission spine and the site AABB, a Rec.709 luminance histogram per
frame, and its first honest result a retraction of its own hand-run figures
(28.6% clipped -> 0.00% at 255, the real effect 18.62% within three codes of
white against 1.13% under Lux). It is not gated on anything, and the item is
explicit that it should not be until somebody decides what a level has to
beat. WHAT REMAINS is that decision, and the display dependency -- `--headless`
disables rendering, so a machine without one measures under llvmpipe, which
may be A/B'd against itself and not quoted beside a Forward+ figure. This does
not close item 18 and never claimed to.*""",
}


def insert_status(lines, num, block):
    heading = re.compile(r"^\*\*%d\. " % num)
    hits = [i for i, l in enumerate(lines) if heading.match(l)]
    if len(hits) != 1:
        raise SystemExit(f"item {num}: heading matched {len(hits)} times")
    h = hits[0]
    for i in range(max(0, h - 3), h):
        if lines[i].startswith("*STATUS:"):
            raise SystemExit(f"item {num}: a status block already sits above it")
    if h == 0:
        raise SystemExit(f"item {num}: heading at line 0")
    lead = [] if lines[h - 1].strip() == "" else [""]
    lines[h:h] = lead + block.split("\n") + [""]


def main() -> int:
    raw = io.open(P, "rb").read()
    if b"\r\n" in raw:
        print("roadmap has CRLF endings -- stop", file=sys.stderr)
        return 1
    lines = raw.decode("utf-8").split("\n")
    for num in sorted(INSERT, reverse=True):
        insert_status(lines, num, INSERT[num])
    out = "\n".join(lines).encode("utf-8")
    io.open(P, "wb").write(out)
    print(f"wrote {len(out)} bytes ({len(raw)} before); {len(INSERT)} inserted")
    return 0


if __name__ == "__main__":
    sys.exit(main())
