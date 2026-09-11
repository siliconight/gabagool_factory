"""Roadmap batch 12, 2026-09-11: close 136.

STATUS replaces the block and keeps the old one verbatim inside the new
(batch 5's mechanism). Asserts its anchor and refuses on a miss.
"""
import io
import re
import sys

P = "PIPELINE_ROADMAP.md"

STATUS = {
    136: """*STATUS: CLOSED 2026-09-11 -- THE SECOND ANSWER, TAKEN, AND THE PROOF THAT
NO VERTEX MOVED IS THE MORNING'S OWN BUILD. Zoo 0.59.0 splits the one name
into its two meanings: `TOOL_VERSION` is read from `VERSION` at import and
stamps every index and meta.json (0.59.0 today, not 0.31.0); `SEED_EPOCH` is
frozen at "0.31.0" and is what `seeding.root_key`, `habitat.habitat_id` and
`variants.family_id` fold in -- seven call sites in `bpylayer/build.py`, five
in `zoo_cli.py`, one in `wear_probe.py`, all moved. DETERMINISM CHECKED
AGAINST ARTIFACTS, not asserted: the clutter Zoo built for cold run 9005 at
09:0x this morning under the old code (`pebble_bb64e4.glb`,
`habitat_a49078.habitat.json`, theme `delco_1997`, seed 9005) reproduces
exactly under `SEED_EPOCH`, and `tests/test_version_stamp.py` pins those two
ids, pins the stamp to the VERSION file, and refuses statically any seed call
in the tree that reads the stamp -- the guard the dynamic tests cannot be,
since the two strings would agree again the day the epoch is bumped to the
tool version. 601 passing. What the item asked for beyond the fix -- "a test
that the stamped version equals VERSION" -- is the first of those tests.*""",
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
