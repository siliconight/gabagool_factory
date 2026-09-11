"""Roadmap batch 6, 2026-09-11: narrow 62, close 67, file 136.

STATUS replaces a block and keeps the old one verbatim inside the new (batch
5's mechanism); APPEND adds a new item at the end of the file, status block
first, as every item is laid out. Each asserts its anchor and refuses on a
miss.
"""
import io
import re
import sys

P = "PIPELINE_ROADMAP.md"

STATUS = {
    62: """*STATUS: NARROWED 2026-09-11 -- ZOO SAYS IT, LEVEL FACTORY COUNTS IT, AND
THE CLAIM THIS ITEM RESTED ON WAS WRONG IN A USEFUL WAY. The 2026-08-24 status
recorded `zoo_cli.py:370` as `plan_kit`'s ONLY caller and the argument never
passed. `build.build_kit` -- the path the pipeline's `zoo_kit_build` stage
actually runs -- has passed `known_species=genome.list_species()` since Zoo
0.32.0 (2026-07-17, commit a944ccd), written `missing_modules` into every
index and printed a WARNING. The CLI dry plan, which Level Factory runs as the
pre-build gate, was the only UNARMED caller. MEASURED 2026-09-11 before wiring
anything: 37 shipped kit indexes across 13 workspaces, 0 missing modules; 82
fixture indexes, 430 skipped anchors, every one `window` daylight -- the
`pendant` silence that raised this item is gone and nothing else is being
dropped. SHIPPED: Zoo 0.58.0 arms `--kit` and prints one `CAPABILITY_GAP`
line per missing module from both paths through one helper
(`kit.capability_gaps`: asked, nearest species by `difflib`, owner, the two
files to add); `missing_modules` entries carry `nearest` and `owner`. Level
Factory 0.67.0 files `ZOO_CAPABILITY_GAP` (moderate, `art_coverage`,
non-blocking) from a kit index's `missing_modules` and from a fixture index's
skips whose reason is `no fixture species`, so the count reaches the run
summary; six tests each side. FOUND ON THE WAY, AND FIXED: Level Factory's
`ZOO_PARTIAL_BUILD` read `n_fail` off the kit index and Zoo only ever
RETURNED it in-process -- 98 modules with status `fail` across those 37
indexes (90 in `lot-demo-ws`, 8 in `unlit-3b-ws`, zero in any cold run), zero
findings, and its own test green because the fixture was written to the
reader's guessed schema rather than the producer's. Derived from the
per-module `status` now, so it is live on every index Zoo has ever written,
and 0.58.0 writes the key. WHAT REMAINS is the "uniformly" in the title: Lux's
spawner still returns skips as a list rather than a tagged line, Pixelcoat's
missing-profile refusal and Deli Counter's lint have no `CAPABILITY_GAP`
spelling, and no run summary yet prints a gap COUNT as a number -- the
findings appear, the tally does not.*""",

    67: """*STATUS: CLOSED 2026-09-11 -- ARCHIVED, THE SECOND OF THE TWO ANSWERS THE
ITEM ALLOWED. `scripts/promote_factory.ps1` is removed from the tree (history
keeps it at a240533 and every commit before) and a local copy sits in
`_archive/scripts/`, which is gitignored; `docs/CERTIFY.md` Step 5 is the only
promotion procedure and was already the correct one. Parameterising was the
other answer and would have been padding: the certified set has been promoted
by hand since 1.3.0 and the manifest today pins tools eight to twenty minor
versions behind their checkouts, so the operation is not repeatable often
enough to want a script. `tidy_tools.ps1` and `tidy_migrations.ps1` still
name the file in their lists; those are records of the August move and are
left as written.*""",
}

APPEND = """
*STATUS: OPEN 2026-09-11 -- FOUND, PRICED, NOT DONE, BECAUSE THE FIX IS A
DECISION ABOUT DETERMINISM RATHER THAN A STRING*

**136. Zoo stamps every index with a version from July, and the same literal
seeds every asset.** Found 2026-09-11 while wiring roadmap 62.
`zoo_keeper/__init__.py` carries `TOOL_VERSION = "0.31.0"`; `VERSION` says
0.58.0. Every `<building>_kit.built.json`, `_fixtures.built.json` and
`_dressing.built.json` on disk therefore reads `zoo.tool_version: 0.31.0`,
37 kit indexes across 13 workspaces included, and a reader comparing an
artifact to the tool that made it is told a version that is 27 releases
stale.

**WHY IT IS NOT A ONE-LINE FIX.** The literal is also an input to every
seeding root key: `tools/zoo_cli.py:164,170,208,216,227,318` and
`tools/wear_probe.py:221` pass `TOOL_VERSION` into `seeding.root_key`, and
`dna.resolve_plan` / `resolve_module_plan` take it as a parameter. Correcting
the string re-rolls every asset Zoo builds -- the same brief, the same seed,
different geometry -- which invalidates every cached Zoo job and every
comparison history that rests on today's output.

**TWO ANSWERS, AND THE SECOND IS THE ONE TO TAKE.** (1) Read `VERSION` into
`TOOL_VERSION` and accept a one-time re-roll, re-certifying the set after.
(2) Split the two meanings the one name carries: a `SEED_EPOCH` frozen at
`"0.31.0"` for the root keys, so no vertex moves, and `TOOL_VERSION` read
from `VERSION` for the stamps, so the index tells the truth. The second
costs one constant and a grep; the first costs a re-certification and a
comparison history. Whichever is taken, a test should pin that the stamped
version equals `VERSION`, because this drifted for 27 releases without a
single check noticing.
"""


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
    # APPEND: the file ends with item 135's body and no footer.
    if any(l.startswith("**136. ") for l in lines):
        print("item 136 already present", file=sys.stderr)
        return 1
    if not any(l.startswith("**135. ") for l in lines):
        print("item 135 not found; refusing to append after it", file=sys.stderr)
        return 1
    while lines and lines[-1].strip() == "":
        lines.pop()
    lines += [""] + APPEND.strip("\n").split("\n") + [""]
    out = "\n".join(lines).encode("utf-8")
    io.open(P, "wb").write(out)
    print(f"wrote {len(out)} bytes ({len(raw)} before); {len(STATUS)} replaced, "
          f"1 appended")
    return 0


if __name__ == "__main__":
    sys.exit(main())
