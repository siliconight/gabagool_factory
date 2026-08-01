"""Items 17 and 18: the pipeline has never been run cold, and nothing measures feel.

WHY THESE ARE ITEMS AND NOT NOTES. Every open item in this file to date is a
defect: a gate that passed something broken, a measurement taken with the wrong
ruler, a route the collision geometry blocks. They are all of the form "this
thing is wrong". Items 17 and 18 are a different shape -- they say what the
toolchain has never been asked to do, and what it has never been able to see.
A file that only tracks known defects will report itself finished the day the
last one closes, which is a long way from the thing being good.

Item 17 exists because sixteen items of measured, closed defects still do not
answer "does this work without somebody standing over it". Item 18 exists
because the three problems reported from actually PLAYING a level -- stairs too
steep, kerbs zig-zagging, paths drawn across roads -- are two-thirds invisible
to every gate in this repo.

Also appends the gdcheck false-positive finding to Smaller/carried, with the
arithmetic, because a checker that is wrong on every file it flags is a checker
that gets switched off, and this file already argued that case once tonight
about the moderate threshold.

Asserts every target, refuses on a miss, idempotent.
"""
import pathlib
import shutil

ROOT = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
RM = ROOT / "PIPELINE_ROADMAP.md"

ANCHOR = "### Not to be worked on\n"

NEW_ITEMS = '''**17. The pipeline has never been run cold, so nobody knows what it costs to
make a level.** The item the other sixteen do not cover.

Everything in this file measures a defect and closes it. None of it answers the
question the toolchain exists to answer: hand the tools a spec they have never
seen, run one command, and does a walkable, gated package come out with no
human and no assistant touching anything on the way? Today that is unknown, and
the numbers that look like they answer it do not:

    library_walk    19 of 20 sites walk       every one of the twenty has been
                                              iterated on. This measures a
                                              library already fixed, not a
                                              pipeline that works first time.
    check_all       steps/freshness/stairs    the same twenty, same objection
                    clean
    walkup_siege    walks end to end          reached after a long sequence of
                                              patches, which is the thing being
                                              questioned

**The metric is patches-required-per-level, and it is currently unmeasured.**
The acceptance test: pick a spec that has never been through the pipeline, run
it untouched, and record every intervention it needed. A run needing zero is
the first real evidence. A run needing four is a list of four defects, which is
worth more than another guardrail. Repeat on several specs before believing
either result -- one cold run that happens to succeed proves less than it feels
like it does.

**WHAT ROCKAY-WS IS, since this file has been sloppy about it.** It is a level
to iterate against. It is not the deliverable and it is not evidence of a
finished product. The deliverable is the TOOLS: a pipeline someone else points
at their own game to generate levels. A fix that makes rockay-ws work and does
not generalise has not moved the deliverable, and this file should stop counting
those as progress. (The same care applies in the other direction: rockay-ws's
342 .gd files are vendored copies of the lux, patina, pixelcoat and zoo addons,
already checked at their own repos, which is why check_all skips them. They are
copies, not evidence -- the distinction matters because a finding in genuinely
GENERATED output would be a finding about the generator and the most actionable
kind there is.)

**18. Every gate measures whether a level WORKS. None measures whether it is
GOOD.** The three problems reported from playing a generated level:

    stairs too steep to climb        check_stair_pitch.py    measured
    kerbs placed in odd zig-zags     nothing                 invisible
    paths drawn across road          nothing                 invisible
    carriageways

Two of three were caught by a person looking at the screen, and there is no
instrument that would have caught them otherwise. Every guardrail in this repo
answers "can a body traverse this" -- traversal correctness -- and a level can
be perfectly traversable and still read as obviously machine-generated. So long
as that gap exists, shipping requires a human to play every level, which is the
same dependency item 17 is about wearing different clothes.

The measurable part of "good" is where to start, because it can be gated:
a path that crosses a road should yield to it (walkup_siege's path_0 covers
16.0 m of asphalt at 30 degrees, path_2 covers 8.7 m at 66 degrees, and the lip
is 0.0157 m so no traversal gate can see it); a kerb cut should run
perpendicular to its kerb, not diagonally; a flight of stairs should have a
consistent pitch across a building. The parts that are not measurable stay a
human's job, and saying which is which is itself work nobody has done.

'''

CARRIED_OLD = "Retired from this list because they are fixed:"

CARRIED_NEW = '''`gdcheck.py` flags four files and is wrong on all four, which makes it a
guardrail heading for the off switch. Two separate defects, both text
heuristics standing in for tokenising. **The bracket counter strips comments
before masking strings** (`ln.split("#")[0]` runs inside the `re.sub`, so it is
evaluated first), and a `#` inside a string literal then eats the rest of the
line: `Color.html(cosmetic.get("color", "#ffffff"))` truncates to
`return Color.html(cosmetic.get("` and scores +2, which is exactly the net
LT_Cosmetic.gd reports; `"%s (#%d)" % [...]` scores +1, exactly LT_GhostPlayer's.
Mask strings first, then strip comments. **The implicit-concatenation check
tests `prev.endswith('"')` without stripping trailing comments**, so a dict
whose values carry `# e.g. "res://..."` comments flags every following line
(deli_counter_postimport.gd 37-38), and it has no notion that a line legally
begins with a string -- a `match` on string patterns trips it on every arm
(LT_DebugLaser.gd 180, 182). gdparse accepted all four files, and gdcheck's own
docstring claims trap 1 is a syntax error gdparse sees; that contradiction was
the tell.

Retired from this list because they are fixed:'''


def main() -> int:
    if not RM.exists():
        raise SystemExit(f"missing {RM}. Nothing written.")
    src = RM.read_text(encoding="utf-8")
    before = len(src)
    if "**17. The pipeline has never been run cold" in src:
        print("PIPELINE_ROADMAP.md: items 17 and 18 already present")
        return 0
    if "**16. The navmesh contains routes" not in src:
        raise SystemExit("PIPELINE_ROADMAP.md has no item 16 -- this is not the "
                         "file this patch was written against. NOTHING WRITTEN.")
    done = []
    for old, new, label in (
        (ANCHOR, NEW_ITEMS + ANCHOR,
         "items 17 and 18, ahead of `Not to be worked on`"),
        (CARRIED_OLD, CARRIED_NEW,
         "gdcheck's four false positives, in Smaller/carried"),
    ):
        n = src.count(old)
        if n != 1:
            raise SystemExit(f"{label}: anchor appears {n} time(s), expected "
                             f"exactly 1. NOTHING WRITTEN.")
        src = src.replace(old, new)
        done.append(label)

    backup = RM.with_suffix(".md.pre_goal")
    if not backup.exists():
        shutil.copy2(RM, backup)
    RM.write_text(src, encoding="utf-8")
    print("applied:")
    for line in done:
        print(f"  {line}")
    print(f"  {before} -> {len(src)} characters; previous file kept at "
          f"{backup.name}")
    print("\n  Nothing in the toolchain changed. This records what is not known "
          "and what\n  is not measured, so the next session starts from the "
          "goal rather than from\n  the last defect.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
