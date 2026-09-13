"""Roadmap batch 60, 2026-09-13 (night): cold run 9043's zero and the
buildings' insides (17 REPLACE, old kept); the furnishing pass and the desk
that fills a deep slot (44 REPLACE, old kept). Asserts every anchor.
"""
import io
import sys

P = "PIPELINE_ROADMAP.md"

R = []

R.append(("""*STATUS: NARROWED 2026-09-13 (evening) -- 9042 IS THE THIRTIETH ZERO AND
ITS FRAMES CAUGHT THE SECOND DEFECT IN THE SAME THIRTY LINES.""",
"""*STATUS: NARROWED 2026-09-13 (night) -- 9043 IS THE THIRTY-FIRST ZERO AND
IT CARRIED THE ART DIRECTION'S FIRST FOUR TOOL CHANGES. 0 interventions, 0
unattributed, 0 retries, export exit 0, with buildings meeting the street at
2 m instead of 21.5, walls naming a kind the art pass can resolve, roofs
that are not the walls, and stone, siding and shingle in the vocabulary. The
signs' facing was verified against the scene's own bases rather than by eye:
three signs, three roads, each normal pointing at the road its planner
chose.

AND THE RUN AFTER IT IS THE ONE THAT MATTERS TO THIS ITEM'S SECOND HALF.
9044 is running with the rooms furnished -- 819 prop slots become 3,809
across the library, 328 naming a species become 3,214 -- which is the first
change in this sequence aimed at what a player sees INSIDE a building
rather than from the street. Previously: 9042 IS THE THIRTIETH ZERO AND
ITS FRAMES CAUGHT THE SECOND DEFECT IN THE SAME THIRTY LINES."""))

R.append(("""*STATUS: NARROWED 2026-09-12 (late) -- THE TELLER LINE IS IN A COLD
PACKAGE:""",
"""*STATUS: NARROWED 2026-09-13 (night) -- THE BUILDINGS ARE FURNISHED, AND
THE FIRST DIAGNOSIS OF WHY THEY WERE NOT WAS WRONG. The walker: great
progress outside the buildings, what about the props inside.

THE REFUTATION FIRST, because it cost an hour and is the shape of mistake
this repo has written down twice. The first measurement read
`zoo/zoo_keeper/genome/minted.json` as the species catalogue, found 24
entries, and concluded that ten of the eleven species the buildings ask for
by name did not exist. `minted.json` is a list of what the STREET work
minted. Zoo has 83 recipes and every named species is among them --
`shelving`, `counter`, `desk`, `chair`, `filing_cabinet`, `table`,
`teller_line`, `drop_safe`, `water_tank`, `hvac_unit`, all present, all
building. The second wrong turn came from the same habit: `shell.slots.json`
showed every prop at `prop_greybox_01`, which is the GREYBOX stage's
manifest, where that ref is set by construction. The themed kit's own output
is the artefact that answers the question, and it was building the props it
was asked for.

WHAT IS ACTUALLY TRUE, from the themed builds and the slot manifests. Two
separate things, and only the second is about species:

  1. THE BUILDINGS HAD ALMOST NOTHING IN THEM. 819 prop slots across 130
     shells, a MEDIAN OF FOUR per building, 29 buildings with none at all.
     On cold run 9043's own street: a bank tower whose whole interior is
     three teller lines, a garage of 24 structural columns and one desk, and
     a funeral home with zero. Nothing was failing to resolve; there was
     nothing to resolve.
  2. OF THE 328 SLOTS THAT DID NAME A SPECIES, 285 FIT ITS RANGES AND 43 DID
     NOT -- and 30 of the 43 were `desk`, in two shapes: 27 at 1.1 or 1.2 m
     tall (a reception desk) and 10 at 6.0 m deep (a cubicle block).

BOTH ARE FIXED AND BOTH WERE MEASURED. Zoo 0.76.0 gives `desk` a `row_max`
-- the depth-axis twin of the `bay_max` this item already built -- so a
cubicle block is rows of desks back to back, and a transaction ledge above
`DESK_TOP_MAX` so a 1.2 m slot keeps its work surface at sitting height.
314 of 328 fit now; the 14 that do not are a 7 m deep `chair` and a 3 m deep
`counter`, which are rooms' worth of furniture in one volume and belong in
Deli Counter. Deli Counter 0.122.0 adds `furnish`, a pass separate from
`seed_cover` because the two answer different questions -- cover is a
gameplay property with a deliberate over-cover thesis behind it, furniture
is an art one. One piece per 16 square metres, capped at ten, existing
volumes counting toward the target, every name routing to a species Zoo
builds:

    prop slots        819 -> 3809
    naming a species  328 -> 3214
    shells with none   29 -> 2
    median per shell    4 -> 26

FOUR THINGS THE GATES TAUGHT IT, each recorded in the changelog with the
draft it replaced: the invariant is about SHELTER and not cover (a desk is
0.75 m and a desk IS low cover); cover must run FIRST or a furnished room
has nowhere left to stand the one piece a body can fight from; idempotence
is by MARK and not by count; and furniture must stay off exterior walls,
because `_seed_clear` guards partitions and knows nothing about the openings
in an outside wall -- a shelf run stood across the door of `office`'s exec
suite and the nav gate caught it. After that fix the nav verdicts are
identical to before furnishing: the same 14 pre-existing shells report
unreachable markers, none added, none fixed.

AN INSTRUMENT DISAGREEMENT FOUND ON THE WAY, filed here rather than fixed.
`nav_gate` prints `navigable: NO` for 14 shells and then `nav-gate: 129
shell(s) passed`; run on one shell it prints `1 shell(s) passed` directly
under its own NO. The summary is counting something other than the verdict
above it. It behaved that way before this work and the 14 are the same 14,
so nothing here rests on it -- but a gate whose summary contradicts its own
findings is exactly the shape CLAUDE.md's third rule is about, and somebody
should decide which of the two lines is the verdict. Previously: THE TELLER
LINE IS IN A COLD PACKAGE:"""))


def main() -> int:
    raw = io.open(P, "rb").read()
    if b"\r\n" in raw:
        print("roadmap has CRLF endings -- stop", file=sys.stderr)
        return 1
    text = raw.decode("utf-8")
    for old, _new in R:
        if text.count(old) != 1:
            print(f"anchor matched {text.count(old)} times; refusing: "
                  f"{old[:60]!r}", file=sys.stderr)
            return 1
    for old, new in R:
        text = text.replace(old, new, 1)
    out = text.encode("utf-8")
    io.open(P, "wb").write(out)
    print(f"wrote {len(out)} bytes ({len(raw)} before); 17, 44 updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
