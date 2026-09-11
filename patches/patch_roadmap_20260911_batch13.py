"""Roadmap batch 13, 2026-09-11: close 129, narrow 64.

STATUS replaces the block and keeps the old one verbatim inside the new
(batch 5's mechanism). Asserts its anchor and refuses on a miss.
"""
import io
import re
import sys

P = "PIPELINE_ROADMAP.md"

STATUS = {
    129: """*STATUS: CLOSED 2026-09-11 -- THE DEFAULT IS 4, DECIDED. Level Factory
0.69.0 sets `crew_size = 4` in `MissionBrief` and in the two CLI fallbacks that
repeated the 1; a test pins the model's default and refuses any fallback that
still says 1. The objection that held it at 1 -- raising the default changes
every historical comparison -- was weighed and overruled on the facts this item
already carried: 1 against the stock six guards was never a choice anyone
made (26 of 27 briefs never set the field because the schema did not mention
it), it wiped 75 of 75 runs on `warehouse_yard_001` and every run on two other
maps, and the 23 briefs still without a crew are all workspace copies and
cold-run records. Scenario values are in the Laser Tag fingerprint, so those
briefs re-run at 4 on their next evaluation rather than replaying a grade
taken at 1; the grades already stored stand as what they were. The four
shipped example briefs keep declaring the field, because a brief that says how
many people arrive beats one that inherits it. The unrun experiment this item
named -- crew 4 against route completion with 128's truncation removed -- was
run under 121 on 2026-09-11: `county_hospital_001` at 6 enemies, deaths
17 -> 0, survival 41.6 -> 180.1 s, progress 1.00 both arms.*""",

    64: """*STATUS: NARROWED 2026-09-11 -- THE THREE PRECONDITIONS ARE PAID; THE
PROMOTION WAITS FOR ART, AS THE ITEM SAID IT SHOULD. Zoo 0.60.0: (1) the
genome's height range is 2.0-6.5 m (was 4.5, which excluded 252 of 988
corners) and width/depth reach 0.25 -- re-measured over the rebuilt library
today, 950 corner posts across 17 (thickness, height) pairs, 0.25/0.30/0.35 m
by 2.7-6.2 m, the ranges and their measurement written into the genome; (2)
`kit.plan_kit` keys `wallCorner` on width, depth and height (`CORNER_ROLES`,
the prop's treatment), so `_w30` no longer names fourteen solids -- Deli
Counter 0.114.0 mirrors it in `themed_tscn.resolve_themed_stem` and the same
literal (`wallCorner_delco_01_w30_d30_h330`) is pinned in both suites; (3)
the gap report was armed under item 62 (Zoo 0.58.0). WHAT REMAINS is the
step the item priced and deferred: Deli Counter promoting its corner slots
from the `wallEnd` unit post (0.102.0's answer to item 58, zero new modules)
to `wallCorner`. Priced today: one exact module per (thickness, height) per
building, 17 across the library per theme and style, one more Blender
module per building per storey height in every kit job -- and at the slot's
own dims of [t, t, h] the L-recipe degenerates to the same post, so it buys
nothing a person can see until the corner has art a post does not (item 57's
vocabulary). Everything upstream of that art is now in place, which is what
this item was for.*""",
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
