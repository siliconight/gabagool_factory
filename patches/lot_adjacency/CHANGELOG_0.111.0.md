## 0.111.0 - the guide's adjacency as audit findings

**Roadmap 230.** The walker's adjacency and layout guide says a plausible
town is a network of relationships, and "can A be next to B" is answered by
what kind of adjacency it is and why. Level Factory 0.176.0 draws a lot by
a cluster template when the brief asks; this reads the lot that WAS drawn.

- **`site_adjacency.py`,** pure: a building's category from its
  archetype's words (nine of the guide's), the relation from geometry
  (`shared_boundary` within 3 m edge to edge, `across_local_street` when a
  road lies between the centres, else `same_block`), the guide's 9 x 9
  affinity matrix, and the sixteen pair rules Lot can judge (P04, P06, P07,
  P08, P10 to P14, P17 to P21, P28, P30) with the guide's verdicts and what
  each requires.
- **`S_ADJACENCY` in the site audit,** report-only: MED where the guide
  says `condition` or worse, or the affinity is -2 (a hospital sharing a
  boundary with a strip club, P21; a mansion beside a foundry); INFO where
  it says `prefer` or `allow`, which is the reason a pair is good (a deli
  beside the station, P17), or the affinity is merely weak. A plain fit
  says nothing.
- A finding, not a gate, until the draw above makes the verdicts mostly
  `prefer`; the Empties' terrace is composed by Level Factory and is not
  judged here.

**Tests:** 8 in `tests/test_site_adjacency.py`. **Suite:** RESULT_SUITE.
