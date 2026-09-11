"""Roadmap batch 7, 2026-09-11: narrow 85.

STATUS replaces the block and keeps the old one verbatim inside the new
(batch 5's mechanism). Asserts its anchor and refuses on a miss.
"""
import io
import re
import sys

P = "PIPELINE_ROADMAP.md"

STATUS = {
    85: """*STATUS: NARROWED 2026-09-11 -- MEASURED ACROSS THE LIBRARY, THE CAUSE FOUND
AT THE SOURCE AND FIXED THERE, THE INSTRUMENT KEPT; THE GATE IS NOT WIRED.
`tools/anchor_wall_probe.py` (factory root) reads what Deli Counter already
writes -- every anchor in `<building>.lights.json` expanded to its lamp
points, every wall slot in `<building>.slots.json` as a rotated box -- and
reports each lamp's signed clearance to the nearest wall on its storey.
BEFORE, 125 shipped buildings: the ceiling rows the item suspected are clean,
2,422 fluorescent and pendant lamp points with NONE inside a wall and a
minimum clearance of 1.35 m -- so "one bad anchor or a systematic offset"
was neither, for that type. The wall packs were the systematic offset: 334
anchors at a median clearance of 0.000 to the nearest wall, min -0.025 in a
0.35 m wall, and the 91 signs at 0.050. An opening's (x, y) is its wall's
CENTRELINE (425 of 425 exterior doors at 0.000 from it) and
`lights._WALL_PACK_OUT` / `_SIGN_OUT` were added to that point while their
comments said "proud of the wall face". Zoo built to the comment: the pack's
0.22 m body is centred on the anchor with an arm reaching 0.15 m back to the
wall plane, the sign's 0.18 m cabinet hangs entirely behind its face plane.
Half of every pack and most of every cabinet sat inside the wall -- a hanging
light half-buried at a wall/ceiling junction is what a wall pack 0.25 m above
a door head looks like from inside. Deli Counter 0.113.0: `derive_light_anchors`
and `build_light_manifest` take `wall_thick` (required, the `cap_thick` rule)
and place both facade types half a wall further out; `write_light_manifest`
passes the spec's own thickness. AFTER, re-derived over the same 125
buildings: pack clearance 0.150, sign 0.200 -- the constants, exactly -- and
the ceiling rows unchanged. Four test files updated, two new tests, 658
passing. The item's diagnosis of the gate was right and stands: Lux checks
the fixture against its marker and nothing checks the marker against the
wall. WHAT REMAINS is that check as a GATE rather than a probe run by hand --
the geometry is pure and already in the probe, and the natural home is the
Deli Counter adapter's `normalize_validation`, which has every input in one
job's outputs. Until then a regression here is caught by re-running the probe,
which is one command and no Godot.*""",
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
