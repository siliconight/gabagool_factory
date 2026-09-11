"""Roadmap batch 16, 2026-09-11: close 60.

STATUS replaces the block and keeps the old one verbatim inside the new
(batch 5's mechanism). Asserts its anchor and refuses on a miss.
"""
import io
import re
import sys

P = "PIPELINE_ROADMAP.md"

STATUS = {
    60: """*STATUS: CLOSED 2026-09-11 -- DECIDED, BUILT INTO THE TIERS, PRICED ON
HARDWARE, AND WALKED WITH NUMBERS; AND THE WALK SAYS THE RANGES DID THE WORK.
THE DECISION (lever a, quality-gated): shadows are a BUDGET the tier spends
on the lights whose through-wall wash is worth stopping first. Lux 0.32.0
adds `LuxLighting.apply_shadow_policy`: every registered rig light is ranked
and `shadow_enabled` is set on the first `max_shadow_casters`, off on the
rest, on every preset apply and after every rig registration; the rig's own
`shadows_enabled` is what it does with no LuxRoot in the scene. 0.32.1 ranks
by RANGE ACROSS AN ENVELOPE THE LIGHT IS OUTSIDE OF -- signs (8 m, the
sighting), wall packs (5.5), streetlights (14) first, then windows (3.2-4.0
since 0.31.0), bulbs, fluorescent rows -- after 0.32.0's first order spent
all 24 casters on 19 windows and 5 bulbs and none on the four exterior
lights, caught by the new `tools/shadow_census.py` reading the running
package. `LuxRoot.shadow_caster_budget` overrides the tier so a level can be
priced without moving post-fx. PRICED (RTX 2060, GL Compatibility, 1600x900,
cold run 9005's export, 58 lights, GPU ms from the engine's own timestamps
via `look_shots --station`'s new per-shot column): 0 casters 2.5-5.6 ms on
the elevations, 4 -> 4.1-6.7, 12 -> 6.3-10.5, 24 -> 8.2-11.6; about 0.3 ms
per shadowed omni. So "High shadows everything" is a slideshow, and the
tiers are High 12, Medium 8, Low and Compatibility 4 (were 0, which would
have switched the shipped window shadows off). THE WALK, AS NUMBERS: four
GIVEN stations 2.15 m inside the rooms behind the sign and the three wall
packs, facing the wall the light hangs outside of, rendered at 0/4/12/24
casters. The doorway spill stays (the door fills the frame either way); the
wall faces beside and above it move by 0.0-0.9 luma of 255 when their light
gains a shadow map (sign station walls 1.8 -> 1.0, packs 12.3 -> 12.0, 35.0
-> 35.0). THE WASH THE ITEM SAW IS NOT THERE TO STOP: the August sighting
was a sign at energy 3 with an 8 m sphere before 0.19.0's drop-derived
ranges and before 0.31.0 took windows from 6.4-9.6 m to 3.2-4.0 -- lever (b)
already removed most of what lever (a) was priced for, which is the honest
finding and the reason the budgets are modest rather than generous. The
policy stands as the guard for the day a light class regains its range, and
the census and the stations are how that day gets noticed. Lever (c), cull
masks, stays unbuilt for the reason the item gave.*""",
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
