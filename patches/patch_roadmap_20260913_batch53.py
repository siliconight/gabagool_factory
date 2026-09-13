"""Roadmap batch 53, 2026-09-13: cold run 9033 zero with the faceted crown
back (17 REPLACE, old kept); the walker's judgement of the cards and the
advice for the detailed path -- branches, twigs, species (153 REPLACE,
old kept). Asserts every anchor.
"""
import io
import sys

P = "PIPELINE_ROADMAP.md"

R = []

R.append(("""*STATUS: NARROWED 2026-09-13 (night) -- COLD RUN 9032 SCORED ZERO WITH THE
CROWN READING AS A CANOPY.""",
"""*STATUS: NARROWED 2026-09-13 (late night) -- COLD RUN 9033 SCORED ZERO WITH
THE FACETED CROWN BACK. The bank brief on Zoo 0.69.3: 0 interventions, 0
retries, 0 unattributed changes, every tool repo clean at --begin, all
stages succeeded, 0 blockers, export exit 0, 15 minutes (23:09 -> 23:25).
The twenty-third zero. Frames in `docs/cold_runs/cold_9033/frames/`.
Previously: COLD RUN 9032 SCORED ZERO WITH THE
CROWN READING AS A CANOPY."""))

R.append(("""*STATUS: NARROWED 2026-09-13 (night) -- THE CROWN READS AS A CANOPY (9032):
ONE FOLIAGE TILE PER CARD, THE CARD'S EDGE THE CANOPY'S.""",
"""*STATUS: NARROWED 2026-09-13 (late night) -- THE WALKER JUDGED THE CARDS
NOT READY AND NAMED THE DETAILED PATH: BRANCHES, TWIGS, SPECIES. On the
9032 frames: "we went from mario64 trees which looked nice in their own
retro way to something that isn't fully baked yet" -- the cards' thin
side faces show as hairlines and the canopy reads as a different art
style from the cars and the shelter beside it. Zoo 0.69.3 ships the
faceted crown again; the cards and the `foliage` kind stay behind
`params.crown` (measured on 9033, the faceted crown in a package). THE
ADVICE: "trees usually have multiple branches that stem from the trunk
and those branches have twigs and depending on what species of tree
determines how that looks." So the tree is GROWN, by species, in the
same faceted style: `core.tree_forms` tables the street trees a Delco
street plants -- red maple (the default), pin oak, honey locust, London
plane, callery pear -- each as where the first branch leaves the trunk,
how far the leader runs, how many primary branches, their angles from
vertical low/mid/high (a pin oak droops low and rises high, a pear rises
tight), twigs per branch, cluster size and crown envelope; the recipe
grows a tapered trunk and leader, branches spiralling up by the golden
angle, twigs off each branch's outer half, and a small faceted leaf
cluster at every tip, then fits the whole tree to the slot per axis so a
form shapes and the slot sizes. The genome names the species. Landing as
Zoo 0.70.0; cold run 9034 measures it. Previously: THE CROWN READS AS A
CANOPY (9032):
ONE FOLIAGE TILE PER CARD, THE CARD'S EDGE THE CANOPY'S."""))


def main() -> int:
    raw = io.open(P, "rb").read()
    if b"\r\n" in raw:
        print("roadmap has CRLF endings -- stop", file=sys.stderr)
        return 1
    text = raw.decode("utf-8")
    for old, new in R:
        if text.count(old) != 1:
            print(f"anchor matched {text.count(old)} times; refusing: {old[:60]!r}", file=sys.stderr)
            return 1
    for old, new in R:
        text = text.replace(old, new, 1)
    out = text.encode("utf-8")
    io.open(P, "wb").write(out)
    print(f"wrote {len(out)} bytes ({len(raw)} before); 17, 153 updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
