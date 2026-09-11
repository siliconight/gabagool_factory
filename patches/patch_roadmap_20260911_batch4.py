"""Roadmap batch 4, 2026-09-11: give the sentence-classified items a status line.

`roadmap_status.py --unclassified` lists 21 items "resting on a sentence rather
than a status line". Nine of them it infers CLOSED or RETRACTED from a phrase in
the body -- the phrase is the evidence, and this writes it into the status
block the index reads, verbatim, with nothing added. The rest it infers OPEN
from silence, and an OPEN line with no new evidence would be padding; those are
left alone except where a later item closed them (4).

INSERT mode: these items have no `*STATUS:` block above the heading, so one is
inserted -- the heading must match exactly once, and if a status block already
sits above it the script refuses rather than stacking two.
"""
import io
import re
import sys

P = "PIPELINE_ROADMAP.md"

#: Inferred by the index from these sentences in the body. Verbatim.
FORMALISE = {
    1: "*STATUS: CLOSED 2026-07-27 -- as the body records: \"Closed 2026-07-27\". "
       "Cover is exonerated; the trap is somewhere else. Written into a status "
       "line 2026-09-11 so the index reads it rather than infers it.*",
    2: "*STATUS: CLOSED 2026-07-27 -- as the body records: \"Closed 2026-07-27 as "
       "Lot 0.x\", `walktest.py` into the DAG. Written into a status line "
       "2026-09-11 so the index reads it rather than infers it.*",
    5: "*STATUS: CLOSED 2026-07-27 -- as the body records: \"Closed 2026-07-27 as "
       "Level Factory 0.14.0\", the resume pre-skip that replayed nothing. "
       "Written into a status line 2026-09-11 so the index reads it rather than "
       "infers it.*",
    7: "*STATUS: CLOSED 2026-07-27 -- as the body records: \"Closed 2026-07-27 as "
       "factory 1.6.0\", five stale pins re-pinned. Written into a status line "
       "2026-09-11 so the index reads it rather than infers it.*",
    11: "*STATUS: RETRACTED 2026-07-28 -- as the body records: \"Retracted "
        "2026-07-28\". Written into a status line 2026-09-11 so the index reads "
        "it rather than infers it.*",
    13: "*STATUS: RETRACTED 2026-07-28 -- as the body records: seed 5320's vault "
        "was never broken; its walktest never ran. Written into a status line "
        "2026-09-11 so the index reads it rather than infers it.*",
    15: "*STATUS: CLOSED 2026-07-28 -- as the body records: \"Closed 2026-07-28 as "
        "Level Factory 0.x\", fail-fast made candidate-scoped. Written into a "
        "status line 2026-09-11 so the index reads it rather than infers it.*",
    23: "*STATUS: CLOSED 2026-08-01 -- as the body records: \"Closed for Lux on "
        "2026-08-01; the general form is\" what follows in the item. Written into "
        "a status line 2026-09-11 so the index reads it rather than infers it.*",
    39: "*STATUS: RETRACTED 2026-08-xx -- as the body records: \"RETRACTED: "
        "`--force` is not broken\". Overtaken since: roadmap 93 found `--force` "
        "was a documented no-op and Level Factory 0.65.0 made it forget the "
        "plan's cache. Written into a status line 2026-09-11 so the index reads "
        "it rather than infers it.*",
}

#: Closed on new evidence, also inserted (no block exists).
CLOSE = {
    4: "*STATUS: CLOSED 2026-09-11 -- FIXED WHERE THE PATH IS WRITTEN, AND MEASURED "
       "ACROSS EVERY SCENE ON DISK. Level Factory's site-spec writer records why in "
       "its own comment: Lot writes each ext_resource as os.path.join(glb_dir, src) "
       "with glb_dir=\".\", so an absolute src passes straight through -- therefore "
       "the spec names \"lot/<id>/site.tscn\" and a staging step run before Lot puts "
       "the package there. Every `lot_assemble` `site.tscn` in every workspace on "
       "disk was grepped on 2026-09-11 for a drive-letter path: 41 of 42 carry none, "
       "and the one that does -- `lot-demo-ws` `art_probe_001` seed 5017, dated "
       "2026-08-05 -- predates the fix, which landed 2026-08-12 (`0e80f34`). Cold "
       "run 9005's ships `path=\"buildings/shell.glb\"`. The two downstream "
       "repairs the item objected to relying on are still there as guards -- the "
       "export closure scan reports `absolute_path_count` 0 on every recent package "
       "-- but the guarantee no longer rests on them.*",
}


def insert_status(lines, num, block):
    heading = re.compile(r"^\*\*%d\. " % num)
    hits = [i for i, l in enumerate(lines) if heading.match(l)]
    if len(hits) != 1:
        raise SystemExit(f"item {num}: heading matched {len(hits)} times")
    h = hits[0]
    # refuse to stack: nothing that looks like a status block within 3 lines
    for i in range(max(0, h - 3), h):
        if lines[i].startswith("*STATUS:"):
            raise SystemExit(f"item {num}: a status block already sits above it")
    # The line before the heading is blank for every item but 39, whose
    # heading runs straight on from item 38's last line. A status block has
    # to be preceded by a blank to parse as its own paragraph, so one is
    # supplied there -- which also fixes the slip.
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
    # highest item first, so earlier insertions do not shift later headings
    for num in sorted(list(FORMALISE) + list(CLOSE), reverse=True):
        insert_status(lines, num, FORMALISE.get(num) or CLOSE[num])
    out = "\n".join(lines).encode("utf-8")
    io.open(P, "wb").write(out)
    print(f"wrote {len(out)} bytes ({len(raw)} before); "
          f"{len(FORMALISE)} formalised, {len(CLOSE)} closed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
