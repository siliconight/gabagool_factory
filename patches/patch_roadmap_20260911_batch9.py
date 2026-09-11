"""Roadmap batch 9, 2026-09-11: 63 superseded by 119.

STATUS replaces the block and keeps the old one verbatim inside the new
(batch 5's mechanism). Asserts its anchor and refuses on a miss.
"""
import io
import re
import sys

P = "PIPELINE_ROADMAP.md"

STATUS = {
    63: """*STATUS: SUPERSEDED 2026-09-11 -- BY ITEM 119, WHICH IS THIS ITEM FILED A
SECOND TIME AND CLOSED IN DELI COUNTER 0.109.0 (2026-09-07, "fit.dims means
one thing now"). The remedy taken was the second of the two this item offered:
unify rather than declare. `_record_wall_slot` writes MODULE-LOCAL dims, the
frame `_record_opening_slot` always wrote and both consumers (`plan_kit`,
`circulation.doorway_volume`) always read, and every shell was rebuilt.
MEASURED TODAY over the shipped library: 20,154 wall and opening slots in 128
manifests, and the only 401 with the thickness ahead of the length are `end`
remainders whose run is genuinely shorter than the wall is thick (0.10-0.28 m
against 0.30) -- length-first still, so zero slots in the world frame. The
August measurement in this item (266 building-space against 15 canonical on
one site) described a writer that no longer exists; cold-run shells built by
DC 0.103.0 still carry it and are the last that will. NOT RE-MEASURED, and
said so: the `rot_y` table -- honoured on 8 of 698 exterior modules in the
COMPOSED scene -- was taken on pre-0.109.0 slots, and no composed scene from
a post-0.109.0 build exists on disk yet to repeat it against; 0.109.0's own
note that "a unit box scaled by LOCAL dims and then turned by rot_y lands
correctly" is the writer's claim, not the composer's measurement. If the next
cold run's composed site still ignores `rot_y` on E/W segments, that is a new
item about the composer, not this one. `docs/ASSET_SWAP_CONTRACT.md` does not
yet spell the frame out in words.*""",
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
