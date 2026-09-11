"""Roadmap batch 15, 2026-09-11: close 137.

STATUS replaces the block and keeps the old one verbatim inside the new
(batch 5's mechanism). Asserts its anchor and refuses on a miss.
"""
import io
import re
import sys

P = "PIPELINE_ROADMAP.md"

STATUS = {
    137: """*STATUS: CLOSED 2026-09-11 -- DERIVED, NOT TUNED, AND MEASURED BACK TO ONE
OF THE BASELINE. Lux 0.31.0: `LuxAreaLightRig.omni_range` (0 = the old
`4 x panel` rule, kept for signs and hand-placed rigs), and the loader sets a
window's the way it derives every other type's -- twice the panel's longer
side, clamped to 3.0-4.0 m: the floor under a 1.6 m sill and a few metres of
room, capped where item 54 capped the fluorescent rows on the same tiles. 1.6
m windows -> 3.2, 2.4 -> 4.0 (were 6.4 and 9.6). Deliberately NOT
`rig.light_range`: that resource defaults to 12.0 and the rig had never read
it, so honouring it would have made every window a 12 m sphere the day it was
first consulted -- caught while writing the fix, before a run. SAME PACKAGE,
SAME CENSUS: meshes over the per-mesh budget of 8 went 12 -> 3 (worst 12 ->
10), against 2 with the daylight stripped; the window ranges now sit in the
3-4 m bins beside the fluorescents (3m:21, 4m:32, 5m:4). THE RESIDUE, NAMED:
the one plate beyond the baseline is `ceiling_ground_east_ward/Ceiling_Panel_
t1_0` (and its floor twin), which a 3.2 m window grazes by 0.18 m -- the
7.5 x 6.0 plate size item 54 split for the fluorescent density, one light
class later. Trimming a window under 3.0 to shed it would stop it reaching
its own floor; splitting the plate is 54's move, not this item's.*""",
}


def main() -> int:
    raw = io.open(P, "rb").read()
    if b"\r\n" in raw:
        print("roadmap has CRLF endings -- stop", file=sys.stderr)
        return 1
    lines = raw.decode("utf-8").split("\n")
    for num, block in STATUS.items():
        heading = re.compile(r"^\*\*%d\. " % num)
        hits = [i for i, l in enumerate(lines) if heading.match(l)]
        if len(hits) != 1:
            print(f"item {num}: heading matched {len(hits)} times", file=sys.stderr)
            return 1
        h = hits[0]
        if h < 3 or lines[h - 1].strip() != "":
            print(f"item {num}: no blank line above heading", file=sys.stderr)
            return 1
        e = h - 1
        while e > 0 and lines[e].strip() == "":
            e -= 1
        blanks = h - 1 - e
        if not lines[e].rstrip().endswith("*"):
            print(f"item {num}: line above the blank does not close a status "
                  f"block: {lines[e][:60]!r}", file=sys.stderr)
            return 1
        s = None
        for i in range(e, max(-1, e - 40), -1):
            if lines[i].startswith("*STATUS:"):
                s = i
                break
        if s is None:
            print(f"item {num}: no *STATUS: within 40 lines", file=sys.stderr)
            return 1
        old = "\n".join(lines[s:e + 1]).strip()
        if not (old.startswith("*STATUS: ") and old.endswith("*")):
            print(f"item {num}: old block is not a *STATUS: ...* block", file=sys.stderr)
            return 1
        old_body = old[len("*STATUS: "):-1].rstrip()
        merged = block[:-1] + "\nEARLIER STATUS, KEPT VERBATIM: " + old_body + "*"
        lines[s:e + 1 + blanks] = merged.split("\n") + [""]
    out = "\n".join(lines).encode("utf-8")
    io.open(P, "wb").write(out)
    print(f"wrote {len(out)} bytes ({len(raw)} before); {len(STATUS)} replaced")
    return 0


if __name__ == "__main__":
    sys.exit(main())
