"""Item 172 closes on cold run 9077; item 177 opens on the z-fight gate.

172 is the ladder off-mesh link. CLOSED requires the evidence in the status
line, and this one earned a long line: the claim was made and falsified TWICE
before it held, so what closes it is a full pipeline run rather than a fixture.

177 is the finding 9076 and 9077 both surfaced and neither was about: a gate
that has printed FAIL on every cold run reported as clean. It is ANALYSIS
rather than OPEN in spirit but it is a task -- somebody has to decide whether
the gate blocks, warns, or goes -- so it is OPEN.

Anchored on the full multi-line status block and the file tail. The one-line
index rows at the top share their opening words, so short anchors would match
twice; `roadmap_status.py --write` regenerates that block afterwards.
"""
from pathlib import Path

TARGET = Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

OLD = """*STATUS: OPEN 2026-09-23 -- MEASURED ON A PACKAGE THAT HAS LADDERS. The link is
generated per ladder and reaches the shell's `gameplay.json`; ZERO files in the
shipped package carry it. The climb marker ships, so a player can climb and an
AI cannot path.*
"""

NEW = """*STATUS: CLOSED 2026-09-23 by cold run 9077 -- `links: 1`,
`lot:07_ladder_0_navlink`, [67.0, 3.6, -23.0] to [67.0, 7.2, -23.0], a 3.6 m
climb, bidirectional, cost 3.0, `required_capability: climb`, agent_types
player and ai_humanoid. 0 interventions, export exit 0. IT TOOK FOUR FIXES
BECAUSE THE CHAIN IS FOUR HOPS, and the claim was made and falsified twice on
the way: Dispatch 0.5.0 taught the Deli Counter importer to read ladders and
9075 read LINKS 0 because a site mission runs the LOT importer; Lot 0.76.0 and
Dispatch 0.5.1 fixed that and 9076 read LINKS 0 again because Level Factory's
`stage_dispatch_inputs` projects Lot's file through a key whitelist that
dropped `ladders` (LF 0.108.1). Both falsifications came from the same
falsifier, written into each brief BEFORE the run: "a package whose buildings
carry ladders and whose links[] is empty". THE VACUITY CHECK IS PART OF THE
RESULT: 9077's best-graded candidate (seed_9279, PASS_WITH_TUNING) carried NO
ladder, so selecting on grade as 9076 did would have read links 0 correctly
and proved nothing; seed_9077 was selected for the falsifier instead, at a
stated cost of a WARN grade.*
"""

TAIL_ANCHOR = """look before the rule is written as unconditional.
"""

TAIL_NEW = """look before the rule is written as unconditional.

*STATUS: OPEN 2026-09-23 -- THE GATE HAS FAILED ON EVERY COLD RUN REPORTED AS
CLEAN. `presentation_compose` exits 3 with "z-fight gate [FAIL]" and the word
ERROR on 9072 (107 coplanar pairs / 363 solids), 9073 (72/283), 9075 (44/300),
9076 (130/594) and 9077 (79/525). All five were reported as zero-intervention
runs. Nothing blocks, nothing is read, and no item tracked it until now.*

**177. A gate has printed FAIL on five consecutive cold runs and nobody read
it.** Found while attributing 9076's nonzero exit, which is the only reason it
surfaced -- the number was not being looked for.

**WHAT IT SAYS**, from `presentation_compose`'s own job log:

    [compose] ERROR: coplanar surfaces detected -- the package would flicker.
    [compose] z-fight gate [FAIL]: 130 coplanar pair(s) across 594 solids

**THE SERIES**, normalised because the absolute count tracks site size:

    run    pairs  solids  per solid   reported as
    9072     107     363      0.295   genuine zero
    9073      72     283      0.254   genuine zero
    9075      44     300      0.147   genuine zero
    9076     130     594      0.219   genuine zero
    9077      79     525      0.150   genuine zero

**WHY IT MATTERS MORE THAN THE NUMBER.** Coplanar surfaces are exactly the
class of defect the traversal gates cannot see and a person looking at the
screen notices immediately, as flicker. CLAUDE.md's own framing: "Works" and
"good" are different gates, and only the first exists -- of the three problems
found by actually playing a generated level, two were caught by a person
looking at the screen. Here is an instrument already pointed at one of those,
firing every time, wired to nothing.

**THE SHAPE IS THE POINT, and it is the second instance found in one day.**
`test_navgate_population` fires only when somebody happens to rebuild the shell
library, which is how a stair regression sat five weeks (item 176). This one
fires every run and is ignored. A gate with an unknown duty cycle and a gate
nobody reads fail the same way: they make a red light that changes no
behaviour, and a run gets called clean with the word ERROR in its log.

**WHAT IS NOT KNOWN, and must be established before it is made to block.**
Whether 79-130 coplanar pairs is a shipping defect or a threshold problem.
Nobody has looked at one of these pairs in the engine to see whether it
flickers at gameplay distances, whether the pairs are duplicate surfaces or
merely near-coincident ones, or whether the count is dominated by one
generator. Making it block today would stop every export on a number nobody
has interpreted -- which is the opposite mistake, not the fix.

**THE DECISION OWED**: block, warn, or delete. A gate that stays as it is
teaches every future reader that FAIL means nothing here, which is worse than
not having it.
"""


def main() -> None:
    data = TARGET.read_bytes()
    if b"\r\n" in data:
        raise SystemExit("REFUSED: expected LF, found CRLF")
    text = data.decode("utf-8")
    before = len(data)
    if "**177." in text:
        raise SystemExit("REFUSED: item 177 already present")
    for i, (old, new) in enumerate(((OLD, NEW), (TAIL_ANCHOR, TAIL_NEW)), 1):
        hits = text.count(old)
        if hits != 1:
            raise SystemExit(f"REFUSED: anchor {i} matched {hits} times")
        text = text.replace(old, new)
    out = text.encode("utf-8")
    if b"\r\n" in out:
        raise SystemExit("REFUSED: would write CRLF")
    TARGET.write_bytes(out)
    print(f"{TARGET.name}: {before} -> {len(out)} bytes (+{len(out) - before})")


if __name__ == "__main__":
    main()
