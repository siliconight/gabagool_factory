"""Roadmap batch 54, 2026-09-13: cold run 9034 zero with the tree grown by
species in the package (17 REPLACE, old kept; 153 REPLACE, old kept).
Asserts every anchor.
"""
import io
import sys

P = "PIPELINE_ROADMAP.md"

R = []

R.append(("""*STATUS: NARROWED 2026-09-13 (late night) -- COLD RUN 9033 SCORED ZERO WITH
THE FACETED CROWN BACK.""",
"""*STATUS: NARROWED 2026-09-13 (late night) -- COLD RUN 9034 SCORED ZERO WITH
THE TREE GROWN BY SPECIES. The bank brief on Zoo 0.70.0: 0 interventions,
0 retries, 0 unattributed changes, every tool repo clean at --begin, all
stages succeeded, 0 blockers, export exit 0, 12 minutes (23:33 -> 23:45);
every site-kit module `pass` (8 of 8). The twenty-fourth zero. Frames
(`docs/cold_runs/cold_9034/frames/`): a red maple at the kerb -- trunk,
leader, branches, twigs, faceted clusters at the tips, in the street's
own low-poly style -- and the row of them along the parked cars.
Previously: COLD RUN 9033 SCORED ZERO WITH
THE FACETED CROWN BACK."""))

R.append(("""*STATUS: NARROWED 2026-09-13 (late night) -- THE WALKER JUDGED THE CARDS
NOT READY AND NAMED THE DETAILED PATH: BRANCHES, TWIGS, SPECIES.""",
"""*STATUS: NARROWED 2026-09-13 (late night) -- THE TREE IS GROWN BY SPECIES,
IN A COLD PACKAGE (9034). Zoo 0.70.0: `core.tree_forms` tables red maple
(default), pin oak, honey locust, London plane and callery pear; the
recipe grows trunk, leader, branches at the species' angles, twigs and a
faceted cluster at every tip, fits the skeleton to the slot and then
places the clusters (fitting the whole tree after pressed them into
plates on the first local build), and a cluster is a quarter taller than
wide with a middle band (as wide as tall read as flat gems from the
sidewalk on the second). Measured on 9034's frames from the kerb and
along the row: a tree with a trunk you can see through to branches, leaf
masses at the tips, the same style as the cars and the shelter. The
walker's guidance is in `docs/SET_DRESSING_REFERENCES.md`. WHAT REMAINS:
the four other species are a genome param away and unmeasured in a
package; a street could plant one species per road or per block rather
than red maples throughout; the cards stay behind `params.crown`; an X
crossing's slabs are handled but the spec makes only a T; parking lanes
and the kerb line stop at the plate's roads. Previously: THE WALKER
JUDGED THE CARDS
NOT READY AND NAMED THE DETAILED PATH: BRANCHES, TWIGS, SPECIES."""))


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
