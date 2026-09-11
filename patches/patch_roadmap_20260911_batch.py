"""Roadmap batch, 2026-09-11: close 97, 98, 102, 120, 93, 100, 77.

Replaces the `*STATUS: ...*` block directly above each heading and nothing
else -- never the generated index (that is `roadmap_status.py --write`).
Each heading must match exactly once, and its status block must sit within
forty lines above it, or the script refuses to write.

Run from the factory root, then:
    python tools\\roadmap_status.py --write
    python tools\\roadmap_status.py --check
"""
import io
import re
import sys

P = "PIPELINE_ROADMAP.md"

STATUS = {
    97: """*STATUS: CLOSED 2026-09-11 -- BUILT, NOT ALIASED, AND RUN COLD TWICE. Pixelcoat
0.27.0 ships `profiles/themes/delco_1997.json`, a real profile differing from
`delco` in five material slots; Zoo 0.57.0's `theme_style` resolves the decade
qualifier so all 56 species reach a style through Zoo's own rule. Cold runs 9004
and 9005 both ran `delco_1997` end to end -- the plan reports "pixelcoat profile
found, all 56 species resolve" and `pixelcoat_build`, the stage that refused
outright on 9003, succeeded on both. The item's open question -- does the design
want a `delco_1997` -- was answered by the steer to fix gaps rather than route
around them: an alias to `delco` was tried first and reverted the same day, for
the reason roadmap 118 gives about aliases keeping the confusion.*""",

    98: """*STATUS: CLOSED 2026-09-11 -- THE HOOK PASSES AND HAS BEEN COMMITTED THROUGH.
`check.py` exits 0 on 2026-09-11 with "All checks passed" across all six gates
(coherence, layout rails, stair sweep, build freshness, nav traversal, catalog).
Five Deli Counter releases landed through the pre-commit hook on 2026-09-10 --
0.111.0, 0.111.1, 0.111.2, 0.112.0 -- with the full suite and the preset
scorecards running inside it each time. The three disjoint-navmesh shells the
status named were fixed under items 113/114 (DC 0.105.0), and `build_freshness`
did not fire on any of the four. The candidate explanation for four uncommitted
releases is therefore no longer reproducible, and the hook is not the blocker.*""",

    102: """*STATUS: CLOSED 2026-09-11 -- MEASURED FIRST, THEN FIXED, EXACTLY AS THIS ITEM
ASKED. Roadmap 130 ran the instrument this item said did not exist: cover per
interior room across the 14 non-facade presets, judged against a threshold
DERIVED from the firefight's own sight geometry rather than chosen -- 100 of
177 qualifying solids below the height where cover works, and 39 of 91 combat
rooms furnished with nothing that breaks a sightline. Deli Counter 0.112.0 then
seeds ONE piece at `shelter_height()` into each such room and leaves its
furniture alone: 39 -> 0, no other audit finding moved, `layout_lint` identical
with the change and without it. The "how much is enough" question resolved as
one piece of shelter with the rest left as life, per the brief for these
levels; it was not closed on a screenshot.*""",

    120: """*STATUS: CLOSED 2026-09-11 -- BOTH REMAINING HALVES ANSWERED BY LATER ITEMS.
Completion is reachable with enemies alive: 1.00 on all three cold-run-9005
candidates, and 0.00 -> 1.00 at EVERY populated enemy count on item 128's own
sweep once Laser Tag 0.22.0 stopped ending a run the moment the last guard fell.
The grade-does-not-follow-severity half: grades are score bands by design, and
128, 132 and 135 made the FAIL findings move the score -- `ENEMY_PATHING_BROKEN`
can take the whole pathing category and `TRIVIAL_ENCOUNTER` caps below PASS.
The "is 1-versus-6 the right thing to grade against" half was item 129's and is
answered: every shipped brief declares `crew_size: 4`. The census in this item
(31 of 33 reports at 0.0) was true when taken and described an instrument that
could not read the thing it was named for.*""",

    93: """*STATUS: CLOSED 2026-09-11 -- THE MAIN HALF LANDED TWELVE DAYS BEFORE THIS
STATUS SAID SO, AND THE RESIDUE CLOSES WITH LEVEL FACTORY 0.65.0.
`fingerprint_inputs` has carried `driver_src_hash` for the compose driver since
2026-08-30, with `test_presentation_driver_in_fingerprint.py` mirroring the Lux
test the item named -- this status was stale, not the code. The residue: `--force`
was a documented no-op ("accepted and ignored") and the scheduler's docstring
agreed. It now forgets every planned job's cached digest before the run, read
from each job's own `fingerprint.last.json` receipt -- the `cache forget` this
item found by reading the CLI, applied to the whole plan -- and the help text
says so. A fresh workspace with no receipts is counted, not an error.*""",

    100: """*STATUS: CLOSED 2026-09-11 -- IT SAYS SO, AND THE SPELLINGS THE BRIEFS USE ARE
KNOWN. Level Factory 0.65.0. A census of every brief on disk found SEVENTEEN OF
TWENTY-SEVEN asking for a shape the table did not carry, every one silently a
row -- including both of the two most recent cold runs, `warehouse_yard_001`
("yard") and `county_hospital_001` ("campus"). `shape_known` now distinguishes a
spelling nobody added from one that means row; the site spec records
`site_shape_resolved` {asked, got, known} so the fallback is on disk; and the
writer announces an unknown spelling on stderr in the gap-protocol voice. The
four spellings the briefs use are added deliberately and once, each as a stated
reading of the word: street_block -> row (7 briefs), boardwalk_crescent -> L (4),
yard -> row (3), campus -> courtyard (2). `string` (1 brief) is left unknown on
purpose, as the proof the announcement fires. The fallback itself is kept -- the
original comment was right that refusing a build over a label is the wrong
trade.*""",

    77: """*STATUS: CLOSED 2026-09-11 -- `--begin` RECORDS WHAT WAS ALREADY DIRTY AND
`--end` READS IT BACK. `cold_run.dirty()` runs `git status --porcelain
--untracked-files=no` per tool repo; `--begin` stores the result in
`before.json` and prints it, and `--end` annotates any changed file that was
already modified at the start as "(was ALREADY modified at --begin)" so an edit
in flight is distinguishable from an intervention. Untracked files are excluded
on purpose -- `snapshot` already catches a new hand-authored file as an addition,
and a workspace or a report is not a source edit. None, not [], when git cannot
answer. Selftested on a real `git init` repo, and proved live the same hour: on
2026-09-11 it correctly reported the two Level Factory files being edited for
item 100 as already dirty. `cold_7003`'s ambiguous 1 stays ambiguous -- this
closes the mechanism, not the archaeology.*""",
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
            print(f"item {num}: heading matched {len(hits)} times -- refusing",
                  file=sys.stderr)
            return 1
        h = hits[0]
        # Walk BACKWARD from the heading: one blank line, then the block's
        # last line (ending in `*`), then up to the `*STATUS:` opener. Walking
        # forward from the opener and stopping at the first `*`-terminated
        # line broke on a block with an interior line ending in `*`.
        if h < 3 or lines[h - 1].strip() != "":
            print(f"item {num}: no blank line directly above heading {h}",
                  file=sys.stderr)
            return 1
        # Tolerate a run of blank lines (item 120 has two) and normalise to
        # one on the way out, which is the convention roadmap_status expects.
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
            print(f"item {num}: no *STATUS: within 40 lines above heading",
                  file=sys.stderr)
            return 1
        lines[s:e + 1 + blanks] = block.split("\n") + [""]

    out = "\n".join(lines).encode("utf-8")
    io.open(P, "wb").write(out)
    print(f"wrote {len(out)} bytes ({len(raw)} before); {len(STATUS)} statuses replaced")
    return 0


if __name__ == "__main__":
    sys.exit(main())
