"""Roadmap batch 5, 2026-09-11: close 121 and 6, narrow 59, mark 40 analysis.

Three mechanisms: STATUS replaces a whole block (batches 1-3), INSERT adds one
where none exists (batch 4), HEAD rewords the opening sentence of a block whose
record is worth keeping. Each asserts its anchor and refuses on a miss.
"""
import io
import re
import sys

P = "PIPELINE_ROADMAP.md"

STATUS = {
    121: """*STATUS: CLOSED 2026-09-11 -- MEASURED, ON A TRIVIAL MAP AND ON ONE THAT
FIGHTS BACK, AND THE FLAG SHOWS. Every earlier A/B of `advance_while_engaging`
ran against a crew of one that died in seconds or a run that ended the moment
the last guard fell, so the flag had nowhere to show; 128 and 129 removed both.
Fourth measurement, 10 runs per arm, crew 4, the flag the only difference.
`restaurant_row_001` at 4 enemies: progress 1.00 both, deaths 0 both, kills 4.0
both, `player_stuck` 2 -> 0, survival 32.5 -> 31.0 s -- a small, real effect on
a map the crew was never threatened on. `county_hospital_001` at 6 enemies, the
map that put 47 crew members down on cold run 9005: progress 1.00 both,
**player_deaths 17 -> 0, survival 41.6 s -> 180.1 s (the full clock), kills 2.3
-> 0.8**, score 76 -> 73 (PASS_WITH_TUNING -> WARN). THAT IS TRAVERSAL UNDER
FIRE, READ OFF THE INSTRUMENT: a crew that keeps walking while it shoots gets
through six guards without losing anyone, and clears a third as many of them.
The score falling while the crew stops dying is the rubric doing its job --
`TRIVIAL_ENCOUNTER` and the pacing category read a disengaged crew correctly.
THE DEFAULT STAYS OFF, and that is a design call rather than a residue: stop-
and-fight is the original bot and the comparison history rests on it, which is
the same objection that has kept every behavioural flag opt-in. A brief that
wants the other bot sets it, and since Level Factory 0.60.0 it can.*""",
}


#: Items with NO status block of their own. Inserted above the heading.
#: Item 6 needs one urgently: batch 4 gave item 7 a status line, and the
#: index -- which treats everything up to the next heading as item 6's body
#: -- now reads item 7's line as item 6's sentence and infers 6 CLOSED on
#: 2026-07-27. It is closed, but on 2026-09-11 and for its own reason.
INSERT = {
    6: """*STATUS: CLOSED 2026-09-11 -- IT SAYS SO, AT INFO. Level Factory 0.66.1:
`advise_scene` files `LT_SCENE_NOT_READ` when the scene is absent or never
given -- the path and which, and the checks that therefore did not run
(sightline, standoff, floating-marker) -- so their silence reads as absence
rather than as a clean bill. Non-blocking and not a defect claim: the
pre-flight still owns "there is no scene here", and the original reasoning
against saying that twice is kept in the docstring. What the item asked for was
provenance, and that is what is filed. The existing test that pinned silence
now pins the notice.*""",

    40: """*STATUS: ANALYSIS 2026-09-11 -- A TRIAGE RECORD, NOT A TASK. The item says so
in its own first paragraph: the sweep "reports questions, not defects", and
this is the human half, naming four fifths of the output as correct by design
so nobody re-triages it. It was inferred OPEN by silence, which misfiles a
finding as work owed. Anything it surfaced that IS a defect has its own
number.*""",
}


#: Item 59's status block is sixty lines of record whose HEAD contradicts its
#: own tail: it opens "GENERATOR AVOIDANCE AND THE FOUNDING SIGHTING REMAIN"
#: and, forty lines later, reports the founding sighting probed at zero on
#: lot_demo_001 (45 apertures, no wall inside any) and L18 graduated WARN ->
#: FAIL. Replacing the block would throw the record away; only the head is
#: reworded, exact-once anchor, everything after it untouched.
HEAD = {
    59: (
        "*STATUS: OPEN 2026-08-24 -- LIBRARY SURGERY LANDED; GENERATOR AVOIDANCE\n"
        "AND THE FOUNDING SIGHTING REMAIN. DC 0.101.1 slid all 33 offending\n",
        "*STATUS: NARROWED 2026-09-11 -- TWO THIRDS DONE, AND THE HEAD OF THIS BLOCK\n"
        "WAS STALE AGAINST ITS OWN TAIL. The lint shipped (`layout_lint` L18, Deli\n"
        "Counter 0.101.0), the library was slid clean (0.101.1, 33 findings in 28\n"
        "specs), the founding sighting was probed at ZERO on the composed\n"
        "`lot_demo_001` (45 apertures, no wall inside any), and L18 graduated WARN ->\n"
        "FAIL (0.101.2) -- all recorded below, unchanged. WHAT REMAINS is the last\n"
        "third: the floorplan generator learning avoidance, for which the FAIL gate\n"
        "is the backstop rather than the fix. Reheaded 2026-09-11; the 2026-08-24\n"
        "record follows. LIBRARY SURGERY LANDED. DC 0.101.1 slid all 33 offending\n",
    ),
}


def rehead(text, num, old, new):
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"item {num}: head anchor matched {n} times")
    return text.replace(old, new)


def insert_status(lines, num, block):
    heading = re.compile(r"^\*\*%d\. " % num)
    hits = [i for i, l in enumerate(lines) if heading.match(l)]
    if len(hits) != 1:
        raise SystemExit(f"item {num}: heading matched {len(hits)} times")
    h = hits[0]
    for i in range(max(0, h - 3), h):
        if lines[i].startswith("*STATUS:"):
            raise SystemExit(f"item {num}: a status block already sits above it")
    lead = [] if lines[h - 1].strip() == "" else [""]
    lines[h:h] = lead + block.split("\n") + [""]


def main() -> int:
    raw = io.open(P, "rb").read()
    if b"\r\n" in raw:
        print("roadmap has CRLF endings -- stop", file=sys.stderr)
        return 1
    text = raw.decode("utf-8")
    for num, (old, new) in HEAD.items():
        text = rehead(text, num, old, new)
    lines = text.split("\n")
    for num in sorted(INSERT, reverse=True):
        insert_status(lines, num, INSERT[num])
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
        # The block being replaced is a record, not a placeholder -- 121's
        # carries the `route_completed` audit and the 0.60.0 scenario fix.
        # Keep it verbatim inside the new block rather than throwing it away.
        old = "\n".join(lines[s:e + 1]).strip()
        if not (old.startswith("*STATUS: ") and old.endswith("*")):
            print(f"item {num}: old block is not a *STATUS: ...* block", file=sys.stderr)
            return 1
        old_body = old[len("*STATUS: "):-1].rstrip()
        if not block.endswith("*"):
            print(f"item {num}: new block does not end with *", file=sys.stderr)
            return 1
        merged = (block[:-1] + "\nEARLIER STATUS, KEPT VERBATIM: " + old_body + "*")
        lines[s:e + 1 + blanks] = merged.split("\n") + [""]
    out = "\n".join(lines).encode("utf-8")
    io.open(P, "wb").write(out)
    print(f"wrote {len(out)} bytes ({len(raw)} before); {len(STATUS)} replaced, "
          f"{len(INSERT)} inserted, {len(HEAD)} reheaded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
