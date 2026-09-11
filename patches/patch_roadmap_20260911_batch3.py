"""Roadmap batch 3, 2026-09-11: close 101 and 65; narrow 121.

Same mechanics as the earlier batches: replace only the `*STATUS:` block
above each heading, walking backward from the heading and normalising the
blank run to one.
"""
import io
import re
import sys

P = "PIPELINE_ROADMAP.md"

STATUS = {
    101: """*STATUS: CLOSED 2026-09-11 -- THE THIRD SHAPE, DONE REVERSIBLY, AS LEVEL
FACTORY 0.66.0. `strip_dead_node_paths` runs as the export's last pass, once
every scene is in place: a `node` that names nothing in the shipped scenes is
renamed `node_dispatch`; position and stable id -- the pattern
`interactives.json` used and the reason it survived -- are untouched, nothing is
deleted, and the original address is one rename away for the day LF's entry
grows the tree that would make it true (the first shape). Resolution is by node
NAME anywhere in any shipped scene rather than by full path, because a
re-parent is exactly the failure being handled. Only the two Dispatch files are
touched, by name: `site.site.gameplay.json` carries 473 `node` fields on cold
9005 and every one resolves. Re-measured on a re-export of cold 8001's
`LF_bank_block_001`: `gameplay_anchors.json` 38 moved and 8 kept,
`runtime_ownership_requirements.json` 12 moved, recorded in the package as
`handoff_bindings.json`. Seven unit tests. THE FIRST SHAPE STAYS AVAILABLE and
is not chosen here: whether the portable entry should carry a
`Functional/GameplayAnchors` tree is a question for the gameplay layer that is
expected to leave this toolchain, and a package that asserts nothing false is
the right state to hand it.*""",

    65: """*STATUS: CLOSED 2026-09-11 -- THE GRADERS REFUSE A STALE SITE, WHICH IS THE
SECOND OF THE TWO REMEDIES THIS ITEM NAMED AND THE ONE WITH THE PRECEDENT.
`tools/library_walk.py` now runs `check_freshness.verify` over every building a
site walks before staging it, and REFUSES the site -- printing each stale stem,
its state and the rebuild command -- unless `--allow-stale` is passed. A refused
site prints in the summary table as `REFUSED STALE`, counts as a regression
when it carried a `pass` stamp, and exits non-zero, because a stamp this run
could not re-earn is not a pass. Proved live on 2026-09-11: `ballpark_block`
refused on three STALE-BUILDER buildings without launching Godot. THE DEBT THE
ITEM MEASURED IS STILL THERE AND NOW CANNOT BE GRADED PAST: `check_freshness`
reports 62 STALE-BUILDER across the library today ("78 files then, 79 now"),
so the library cannot be walked until `rebuild_buildings.py --blender` runs --
which is the point. The first remedy, propagation as a DAG job, is not needed
for Level Factory missions: they stage each building fresh from its own
`deli_generate` output and never read `lot/specs/<site>/buildings/` at all,
which is why no cold run was affected.*""",
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
        lines[s:e + 1 + blanks] = block.split("\n") + [""]
    out = "\n".join(lines).encode("utf-8")
    io.open(P, "wb").write(out)
    print(f"wrote {len(out)} bytes ({len(raw)} before); {len(STATUS)} statuses replaced")
    return 0


if __name__ == "__main__":
    sys.exit(main())
